from uuid import UUID

from fastapi import HTTPException, status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.schemas.audit_schema import AuditLogCreate
from app.modules.audit.services.audit_service import AuditService
from app.modules.consultations.repositories.consultation_repository import (
    ConsultationRepository,
)
from app.modules.optimization.enums.program_enums import (
    OptimizationProgramStatus,
)
from app.modules.optimization.models.optimization_program_model import (
    OptimizationProgram,
)
from app.modules.optimization.repositories.program_repository import (
    OptimizationProgramRepository,
)
from app.modules.optimization.schemas.program_schema import (
    OptimizationProgramCreate,
    OptimizationProgramUpdate,
)
from app.modules.patients.repositories.patient_repository import (
    PatientRepository,
)
from app.modules.providers.repositories.provider_repository import (
    ProviderRepository,
)


class OptimizationProgramService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.program_repository = OptimizationProgramRepository(db)
        self.patient_repository = PatientRepository(db)
        self.provider_repository = ProviderRepository(db)
        self.consultation_repository = ConsultationRepository(db)

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

    async def _validate_program_access(
        self,
        program: OptimizationProgram,
        current_user,
    ) -> None:
        if self._is_admin(current_user):
            return

        provider_id = self._provider_id(current_user)

        if provider_id and program.provider_id == provider_id:
            return

        patient_id = self._patient_id(current_user)

        if patient_id and program.patient_id == patient_id:
            return

        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Unauthorized optimization program access",
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
    def _validate_date_range(
        start_date,
        end_date,
    ) -> None:
        if start_date and end_date and end_date < start_date:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="end_date must be after or equal to start_date",
            )

    async def create_program(
        self,
        payload: OptimizationProgramCreate,
        current_user,
    ) -> OptimizationProgram:
        self._validate_date_range(
            payload.start_date,
            payload.end_date,
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

        consultation = await self.consultation_repository.get_by_id(
            payload.consultation_id
        )

        if not consultation:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Consultation not found",
            )

        if consultation.patient_id != patient.id:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Consultation patient does not match program patient",
            )

        if consultation.provider_id != provider.id:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Consultation provider does not match program provider",
            )

        program = OptimizationProgram(
            patient_id=patient.id,
            provider_id=provider.id,
            consultation_id=consultation.id,
            name=payload.name,
            goal=payload.goal,
            status=payload.status,
            start_date=payload.start_date,
            end_date=payload.end_date,
            notes=payload.notes,
        )

        program = await self.program_repository.create(program)

        await AuditService.create_log(
            db=self.db,
            actor_user_id=current_user.id,
            payload=AuditLogCreate(
                action="optimization_program_created",
                resource="optimization_program",
                resource_id=str(program.id),
                description="Optimization program created",
                audit_metadata={
                    "patient_id": str(patient.id),
                    "provider_id": str(provider.id),
                    "consultation_id": str(consultation.id),
                    "status": program.status.value,
                },
            ),
        )

        await self.db.commit()
        await self.db.refresh(program)

        return program

    async def get_programs(
        self,
        current_user,
        limit: int = 20,
        offset: int = 0,
        status: OptimizationProgramStatus | None = None,
    ) -> list[OptimizationProgram]:
        if self._is_admin(current_user):
            return await self.program_repository.get_all(
                limit=limit,
                offset=offset,
                status=status,
            )

        provider_id = self._provider_id(current_user)

        if provider_id:
            return await self.program_repository.get_by_provider_id(
                provider_id=provider_id,
                limit=limit,
                offset=offset,
                status=status,
            )

        patient_id = self._patient_id(current_user)

        if patient_id:
            return await self.program_repository.get_by_patient_id(
                patient_id=patient_id,
                limit=limit,
                offset=offset,
                status=status,
            )

        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Unauthorized optimization program access",
        )

    async def get_program_by_id(
        self,
        program_id: UUID,
        current_user,
    ) -> OptimizationProgram:
        program = await self.program_repository.get_by_id(
            program_id
        )

        if not program:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Optimization program not found",
            )

        await self._validate_program_access(
            program,
            current_user,
        )

        return program

    async def update_program(
        self,
        program_id: UUID,
        payload: OptimizationProgramUpdate,
        current_user,
    ) -> OptimizationProgram:
        program = await self.program_repository.get_by_id(
            program_id
        )

        if not program:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Optimization program not found",
            )

        await self._validate_provider_write_access(
            program.provider_id,
            current_user,
        )

        next_start_date = (
            payload.start_date
            if payload.start_date is not None
            else program.start_date
        )
        next_end_date = (
            payload.end_date
            if payload.end_date is not None
            else program.end_date
        )

        self._validate_date_range(
            next_start_date,
            next_end_date,
        )

        old_status = program.status

        update_data = payload.model_dump(
            exclude_unset=True,
        )

        for field, value in update_data.items():
            setattr(program, field, value)

        program = await self.program_repository.update(program)

        audit_action = "optimization_program_updated"

        if (
            old_status != program.status
            and program.status == OptimizationProgramStatus.COMPLETED
        ):
            audit_action = "optimization_program_completed"

        if (
            old_status != program.status
            and program.status == OptimizationProgramStatus.CANCELLED
        ):
            audit_action = "optimization_program_cancelled"

        await AuditService.create_log(
            db=self.db,
            actor_user_id=current_user.id,
            payload=AuditLogCreate(
                action=audit_action,
                resource="optimization_program",
                resource_id=str(program.id),
                description="Optimization program updated",
                audit_metadata={
                    "old_status": old_status.value,
                    "new_status": program.status.value,
                },
            ),
        )

        await self.db.commit()
        await self.db.refresh(program)

        return program
