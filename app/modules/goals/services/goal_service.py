from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.schemas.audit_schema import AuditLogCreate
from app.modules.audit.services.audit_service import AuditService
from app.modules.consultations.repositories.consultation_repository import (
    ConsultationRepository,
)
from app.modules.goals.enums.goal_enums import HealthGoalStatus
from app.modules.goals.models.goal_progress_model import GoalProgress
from app.modules.goals.models.health_goal_model import HealthGoal
from app.modules.goals.repositories.goal_repository import (
    GoalProgressRepository,
    HealthGoalRepository,
)
from app.modules.goals.schemas.goal_schema import (
    GoalProgressCreate,
    HealthGoalCreate,
    HealthGoalUpdate,
)
from app.modules.optimization.repositories.program_repository import (
    OptimizationProgramRepository,
)
from app.modules.patients.repositories.patient_repository import (
    PatientRepository,
)
from app.modules.providers.repositories.provider_repository import (
    ProviderRepository,
)


class HealthGoalService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.goal_repository = HealthGoalRepository(db)
        self.progress_repository = GoalProgressRepository(db)
        self.patient_repository = PatientRepository(db)
        self.provider_repository = ProviderRepository(db)
        self.consultation_repository = ConsultationRepository(db)
        self.program_repository = OptimizationProgramRepository(db)

    @staticmethod
    def _is_admin(current_user) -> bool:
        return bool(
            current_user.role
            and current_user.role.name == "ADMIN"
        )

    @staticmethod
    def _provider_id(current_user):
        if current_user.provider_profile:
            return current_user.provider_profile.id

        return None

    @staticmethod
    def _patient_id(current_user):
        if current_user.patient:
            return current_user.patient.id

        return None

    async def _validate_goal_access(
        self,
        goal: HealthGoal,
        current_user,
    ) -> None:
        if self._is_admin(current_user):
            return

        provider_id = self._provider_id(current_user)

        if provider_id and goal.provider_id == provider_id:
            return

        patient_id = self._patient_id(current_user)

        if patient_id and goal.patient_id == patient_id:
            return

        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Unauthorized goal access",
        )

    async def _validate_provider_write_access(
        self,
        provider_id: UUID,
        current_user,
    ) -> None:
        if self._is_admin(current_user):
            return

        current_provider_id = self._provider_id(current_user)

        if (
            not current_provider_id
            or current_provider_id != provider_id
        ):
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="Assigned provider access required",
            )

    @staticmethod
    def _audit_action_for_status_change(
        old_status: HealthGoalStatus,
        new_status: HealthGoalStatus,
    ) -> str:
        if old_status == new_status:
            return "goal_updated"

        if new_status == HealthGoalStatus.ACHIEVED:
            return "goal_achieved"

        if new_status == HealthGoalStatus.CANCELLED:
            return "goal_cancelled"

        return "goal_updated"

    async def create_goal(
        self,
        payload: HealthGoalCreate,
        current_user,
    ) -> HealthGoal:
        patient = await self.patient_repository.get_by_id(
            payload.patient_id
        )

        if not patient:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Patient not found",
            )

        provider = await self.provider_repository.get_by_id(
            payload.provider_id
        )

        if not provider:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Provider not found",
            )

        if not provider.is_active:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Provider is inactive",
            )

        await self._validate_provider_write_access(
            provider.id,
            current_user,
        )

        consultation = await self.consultation_repository.get_by_id(
            payload.consultation_id
        )

        if not consultation:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Consultation not found",
            )

        program = await self.program_repository.get_by_id(
            payload.program_id
        )

        if not program:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Optimization program not found",
            )

        if consultation.patient_id != patient.id:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Consultation patient does not match goal patient",
            )

        if consultation.provider_id != provider.id:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Consultation provider does not match goal provider",
            )

        if program.patient_id != patient.id:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Program patient does not match goal patient",
            )

        if program.provider_id != provider.id:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Program provider does not match goal provider",
            )

        goal = HealthGoal(
            patient_id=patient.id,
            provider_id=provider.id,
            consultation_id=consultation.id,
            program_id=program.id,
            title=payload.title,
            description=payload.description,
            category=payload.category,
            target_value=payload.target_value,
            current_value=payload.current_value,
            unit=payload.unit,
            start_value=payload.start_value,
            target_date=payload.target_date,
            status=payload.status,
            notes=payload.notes,
        )

        goal = await self.goal_repository.create(goal)

        await AuditService.create_log(
            db=self.db,
            actor_user_id=current_user.id,
            payload=AuditLogCreate(
                action="goal_created",
                resource="health_goal",
                resource_id=str(goal.id),
                description="Health goal created",
                audit_metadata={
                    "patient_id": str(patient.id),
                    "provider_id": str(provider.id),
                    "program_id": str(program.id),
                    "category": goal.category.value,
                    "status": goal.status.value,
                },
            ),
        )

        await self.db.commit()
        await self.db.refresh(goal)

        return goal

    async def get_goals(
        self,
        current_user,
        limit: int = 20,
        offset: int = 0,
        status: HealthGoalStatus | None = None,
    ) -> list[HealthGoal]:
        if self._is_admin(current_user):
            return await self.goal_repository.get_all(
                limit=limit,
                offset=offset,
                status=status,
            )

        provider_id = self._provider_id(current_user)

        if provider_id:
            return await self.goal_repository.get_by_provider_id(
                provider_id=provider_id,
                limit=limit,
                offset=offset,
                status=status,
            )

        patient_id = self._patient_id(current_user)

        if patient_id:
            return await self.goal_repository.get_by_patient_id(
                patient_id=patient_id,
                limit=limit,
                offset=offset,
                status=status,
            )

        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Unauthorized goal access",
        )

    async def get_goal_by_id(
        self,
        goal_id: UUID,
        current_user,
    ) -> HealthGoal:
        goal = await self.goal_repository.get_by_id(goal_id)

        if not goal:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Health goal not found",
            )

        await self._validate_goal_access(
            goal,
            current_user,
        )

        return goal

    async def update_goal(
        self,
        goal_id: UUID,
        payload: HealthGoalUpdate,
        current_user,
    ) -> HealthGoal:
        goal = await self.goal_repository.get_by_id(goal_id)

        if not goal:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Health goal not found",
            )

        await self._validate_provider_write_access(
            goal.provider_id,
            current_user,
        )

        old_status = goal.status

        update_data = payload.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(goal, field, value)

        goal = await self.goal_repository.update(goal)

        audit_action = self._audit_action_for_status_change(
            old_status=old_status,
            new_status=goal.status,
        )

        await AuditService.create_log(
            db=self.db,
            actor_user_id=current_user.id,
            payload=AuditLogCreate(
                action=audit_action,
                resource="health_goal",
                resource_id=str(goal.id),
                description="Health goal updated",
                audit_metadata={
                    "old_status": old_status.value,
                    "new_status": goal.status.value,
                },
            ),
        )

        await self.db.commit()
        await self.db.refresh(goal)

        return goal

    async def record_progress(
        self,
        payload: GoalProgressCreate,
        current_user,
    ) -> GoalProgress:
        goal = await self.goal_repository.get_by_id(payload.goal_id)

        if not goal:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Health goal not found",
            )

        await self._validate_provider_write_access(
            goal.provider_id,
            current_user,
        )

        progress = GoalProgress(
            goal_id=goal.id,
            value=payload.value,
            notes=payload.notes,
            recorded_at=payload.recorded_at
            or datetime.now(timezone.utc),
        )

        progress = await self.progress_repository.create(progress)

        goal.current_value = progress.value
        await self.goal_repository.update(goal)

        await AuditService.create_log(
            db=self.db,
            actor_user_id=current_user.id,
            payload=AuditLogCreate(
                action="goal_progress_recorded",
                resource="goal_progress",
                resource_id=str(progress.id),
                description="Goal progress recorded",
                audit_metadata={
                    "goal_id": str(goal.id),
                    "patient_id": str(goal.patient_id),
                    "provider_id": str(goal.provider_id),
                    "value": str(progress.value),
                    "recorded_at": progress.recorded_at.isoformat(),
                },
            ),
        )

        await self.db.commit()
        await self.db.refresh(progress)

        return progress

    async def get_progress_by_id(
        self,
        progress_id: UUID,
        current_user,
    ) -> GoalProgress:
        progress = await self.progress_repository.get_by_id(
            progress_id
        )

        if not progress:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Goal progress not found",
            )

        await self._validate_goal_access(
            progress.goal,
            current_user,
        )

        return progress

    async def get_patient_goals(
        self,
        patient_id: UUID,
        current_user,
        limit: int = 20,
        offset: int = 0,
        status: HealthGoalStatus | None = None,
    ) -> list[HealthGoal]:
        patient = await self.patient_repository.get_by_id(patient_id)

        if not patient:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Patient not found",
            )

        if self._is_admin(current_user):
            return await self.goal_repository.get_by_patient_id(
                patient_id=patient_id,
                limit=limit,
                offset=offset,
                status=status,
            )

        provider_id = self._provider_id(current_user)

        if provider_id:
            return await self.goal_repository.get_by_patient_and_provider_id(
                patient_id=patient_id,
                provider_id=provider_id,
                limit=limit,
                offset=offset,
                status=status,
            )

        current_patient_id = self._patient_id(current_user)

        if current_patient_id and current_patient_id == patient_id:
            return await self.goal_repository.get_by_patient_id(
                patient_id=patient_id,
                limit=limit,
                offset=offset,
                status=status,
            )

        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Unauthorized patient goal access",
        )
