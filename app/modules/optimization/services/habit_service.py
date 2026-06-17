from uuid import UUID

from fastapi import HTTPException, status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.schemas.audit_schema import AuditLogCreate
from app.modules.audit.services.audit_service import AuditService
from app.modules.optimization.enums.program_enums import (
    HabitProtocolStatus,
    OptimizationProgramStatus,
)
from app.modules.optimization.models.habit_log_model import HabitLog
from app.modules.optimization.models.habit_protocol_model import HabitProtocol
from app.modules.optimization.repositories.habit_repository import (
    HabitLogRepository,
    HabitProtocolRepository,
)
from app.modules.optimization.repositories.program_repository import (
    OptimizationProgramRepository,
)
from app.modules.optimization.schemas.habit_schema import (
    HabitLogCreate,
    HabitProtocolCreate,
    HabitProtocolUpdate,
)
from app.modules.patients.repositories.patient_repository import (
    PatientRepository,
)
from app.modules.providers.repositories.provider_repository import (
    ProviderRepository,
)


class HabitService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.habit_repository = HabitProtocolRepository(db)
        self.habit_log_repository = HabitLogRepository(db)
        self.program_repository = OptimizationProgramRepository(db)
        self.patient_repository = PatientRepository(db)
        self.provider_repository = ProviderRepository(db)

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

    async def _validate_habit_access(
        self,
        habit: HabitProtocol,
        current_user,
    ) -> None:
        if self._is_admin(current_user):
            return

        provider_id = self._provider_id(current_user)

        if provider_id and habit.provider_id == provider_id:
            return

        patient_id = self._patient_id(current_user)

        if patient_id and habit.patient_id == patient_id:
            return

        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Unauthorized habit access",
        )

    async def _validate_habit_log_access(
        self,
        habit_log: HabitLog,
        current_user,
    ) -> None:
        if self._is_admin(current_user):
            return

        provider_id = self._provider_id(current_user)

        if (
            provider_id
            and habit_log.habit_protocol.provider_id == provider_id
        ):
            return

        patient_id = self._patient_id(current_user)

        if patient_id and habit_log.patient_id == patient_id:
            return

        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Unauthorized habit log access",
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

    async def create_habit(
        self,
        payload: HabitProtocolCreate,
        current_user,
    ) -> HabitProtocol:
        program = await self.program_repository.get_by_id(
            payload.program_id
        )

        if not program:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Optimization program not found",
            )

        if program.status != OptimizationProgramStatus.ACTIVE:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Habits can only be created for active programs",
            )

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

        if program.patient_id != patient.id:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Program patient does not match habit patient",
            )

        if program.provider_id != provider.id:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Program provider does not match habit provider",
            )

        habit = HabitProtocol(
            program_id=program.id,
            patient_id=patient.id,
            provider_id=provider.id,
            title=payload.title,
            description=payload.description,
            target_value=payload.target_value,
            target_unit=payload.target_unit,
            frequency=payload.frequency,
            status=payload.status,
            notes=payload.notes,
        )

        habit = await self.habit_repository.create(habit)

        await AuditService.create_log(
            db=self.db,
            actor_user_id=current_user.id,
            payload=AuditLogCreate(
                action="habit_created",
                resource="habit_protocol",
                resource_id=str(habit.id),
                description="Habit protocol created",
                audit_metadata={
                    "program_id": str(program.id),
                    "patient_id": str(patient.id),
                    "provider_id": str(provider.id),
                    "status": habit.status.value,
                },
            ),
        )

        await self.db.commit()
        await self.db.refresh(habit)

        return habit

    async def get_habits(
        self,
        current_user,
        limit: int = 20,
        offset: int = 0,
        status: HabitProtocolStatus | None = None,
    ) -> list[HabitProtocol]:
        if self._is_admin(current_user):
            return await self.habit_repository.get_all(
                limit=limit,
                offset=offset,
                status=status,
            )

        provider_id = self._provider_id(current_user)

        if provider_id:
            return await self.habit_repository.get_by_provider_id(
                provider_id=provider_id,
                limit=limit,
                offset=offset,
                status=status,
            )

        patient_id = self._patient_id(current_user)

        if patient_id:
            return await self.habit_repository.get_by_patient_id(
                patient_id=patient_id,
                limit=limit,
                offset=offset,
                status=status,
            )

        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Unauthorized habit access",
        )

    async def get_habit_by_id(
        self,
        habit_id: UUID,
        current_user,
    ) -> HabitProtocol:
        habit = await self.habit_repository.get_by_id(habit_id)

        if not habit:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Habit not found",
            )

        await self._validate_habit_access(
            habit,
            current_user,
        )

        return habit

    async def update_habit(
        self,
        habit_id: UUID,
        payload: HabitProtocolUpdate,
        current_user,
    ) -> HabitProtocol:
        habit = await self.habit_repository.get_by_id(habit_id)

        if not habit:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Habit not found",
            )

        await self._validate_provider_write_access(
            habit.provider_id,
            current_user,
        )

        old_status = habit.status

        update_data = payload.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(habit, field, value)

        habit = await self.habit_repository.update(habit)

        audit_action = "habit_updated"

        if (
            old_status != habit.status
            and habit.status == HabitProtocolStatus.COMPLETED
        ):
            audit_action = "habit_completed"

        if (
            old_status != habit.status
            and habit.status == HabitProtocolStatus.CANCELLED
        ):
            audit_action = "habit_cancelled"

        await AuditService.create_log(
            db=self.db,
            actor_user_id=current_user.id,
            payload=AuditLogCreate(
                action=audit_action,
                resource="habit_protocol",
                resource_id=str(habit.id),
                description="Habit protocol updated",
                audit_metadata={
                    "old_status": old_status.value,
                    "new_status": habit.status.value,
                },
            ),
        )

        await self.db.commit()
        await self.db.refresh(habit)

        return habit

    async def create_habit_log(
        self,
        payload: HabitLogCreate,
        current_user,
    ) -> HabitLog:
        habit = await self.habit_repository.get_by_id(
            payload.habit_protocol_id
        )

        if not habit:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Habit not found",
            )

        if habit.status != HabitProtocolStatus.ACTIVE:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Logs can only be created for active habits",
            )

        patient_id = self._patient_id(current_user)

        if not self._is_admin(current_user):
            if not patient_id or patient_id != habit.patient_id:
                raise HTTPException(
                    status_code=http_status.HTTP_403_FORBIDDEN,
                    detail="Patients may only log their own habits",
                )

        existing_log = await self.habit_log_repository.get_by_habit_and_date(
            habit_protocol_id=habit.id,
            log_date=payload.date,
        )

        if existing_log:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Habit log already exists for this date",
            )

        habit_log = HabitLog(
            habit_protocol_id=habit.id,
            patient_id=habit.patient_id,
            date=payload.date,
            actual_value=payload.actual_value,
            completed=payload.completed,
            notes=payload.notes,
        )

        habit_log = await self.habit_log_repository.create(habit_log)

        await AuditService.create_log(
            db=self.db,
            actor_user_id=current_user.id,
            payload=AuditLogCreate(
                action="habit_log_created",
                resource="habit_log",
                resource_id=str(habit_log.id),
                description="Habit log created",
                audit_metadata={
                    "habit_protocol_id": str(habit.id),
                    "patient_id": str(habit.patient_id),
                    "completed": habit_log.completed,
                    "date": habit_log.date.isoformat(),
                },
            ),
        )

        await self.db.commit()
        await self.db.refresh(habit_log)

        return habit_log

    async def get_habit_logs(
        self,
        current_user,
        limit: int = 20,
        offset: int = 0,
    ) -> list[HabitLog]:
        if self._is_admin(current_user):
            return await self.habit_log_repository.get_all(
                limit=limit,
                offset=offset,
            )

        provider_id = self._provider_id(current_user)

        if provider_id:
            return await self.habit_log_repository.get_by_provider_id(
                provider_id=provider_id,
                limit=limit,
                offset=offset,
            )

        patient_id = self._patient_id(current_user)

        if patient_id:
            return await self.habit_log_repository.get_by_patient_id(
                patient_id=patient_id,
                limit=limit,
                offset=offset,
            )

        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Unauthorized habit log access",
        )

    async def get_habit_log_by_id(
        self,
        log_id: UUID,
        current_user,
    ) -> HabitLog:
        habit_log = await self.habit_log_repository.get_by_id(log_id)

        if not habit_log:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Habit log not found",
            )

        await self._validate_habit_log_access(
            habit_log,
            current_user,
        )

        return habit_log

    async def get_patient_habits(
        self,
        patient_id: UUID,
        current_user,
        limit: int = 20,
        offset: int = 0,
        status: HabitProtocolStatus | None = None,
    ) -> list[HabitProtocol]:
        patient = await self.patient_repository.get_by_id(patient_id)

        if not patient:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Patient not found",
            )

        if self._is_admin(current_user):
            return await self.habit_repository.get_by_patient_id(
                patient_id=patient_id,
                limit=limit,
                offset=offset,
                status=status,
            )

        provider_id = self._provider_id(current_user)

        if provider_id:
            return await self.habit_repository.get_by_patient_and_provider_id(
                patient_id=patient_id,
                provider_id=provider_id,
                limit=limit,
                offset=offset,
                status=status,
            )

        current_patient_id = self._patient_id(current_user)

        if current_patient_id and current_patient_id == patient_id:
            return await self.habit_repository.get_by_patient_id(
                patient_id=patient_id,
                limit=limit,
                offset=offset,
                status=status,
            )

        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Unauthorized patient habit access",
        )
