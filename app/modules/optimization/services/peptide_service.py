from uuid import UUID

from fastapi import HTTPException, status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.schemas.audit_schema import AuditLogCreate
from app.modules.audit.services.audit_service import AuditService
from app.modules.optimization.enums.program_enums import (
    OptimizationProgramStatus,
    PeptideProtocolStatus,
)
from app.modules.optimization.models.peptide_protocol_model import (
    PeptideProtocol,
)
from app.modules.optimization.repositories.peptide_repository import (
    PeptideProtocolRepository,
)
from app.modules.optimization.repositories.program_repository import (
    OptimizationProgramRepository,
)
from app.modules.optimization.schemas.peptide_schema import (
    PeptideProtocolCreate,
    PeptideProtocolUpdate,
)
from app.modules.patients.repositories.patient_repository import (
    PatientRepository,
)
from app.modules.providers.repositories.provider_repository import (
    ProviderRepository,
)


class PeptideProtocolService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.peptide_repository = PeptideProtocolRepository(db)
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

    async def _validate_protocol_access(
        self,
        protocol: PeptideProtocol,
        current_user,
    ) -> None:
        if self._is_admin(current_user):
            return

        provider_id = self._provider_id(current_user)

        if provider_id and protocol.provider_id == provider_id:
            return

        patient_id = self._patient_id(current_user)

        if patient_id and protocol.patient_id == patient_id:
            return

        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Unauthorized peptide protocol access",
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

    @staticmethod
    def _audit_action_for_status_change(
        old_status: PeptideProtocolStatus,
        new_status: PeptideProtocolStatus,
    ) -> str:
        if old_status == new_status:
            return "peptide_protocol_updated"

        if new_status == PeptideProtocolStatus.ACTIVE:
            return "peptide_protocol_started"

        if new_status == PeptideProtocolStatus.PAUSED:
            return "peptide_protocol_paused"

        if new_status == PeptideProtocolStatus.COMPLETED:
            return "peptide_protocol_completed"

        if new_status == PeptideProtocolStatus.CANCELLED:
            return "peptide_protocol_cancelled"

        return "peptide_protocol_updated"

    async def create_protocol(
        self,
        payload: PeptideProtocolCreate,
        current_user,
    ) -> PeptideProtocol:
        self._validate_date_range(
            payload.start_date,
            payload.end_date,
        )

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
                detail="Peptide protocols can only be created for active programs",
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
                detail="Program patient does not match peptide protocol patient",
            )

        if program.provider_id != provider.id:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Program provider does not match peptide protocol provider",
            )

        protocol = PeptideProtocol(
            program_id=program.id,
            patient_id=patient.id,
            provider_id=provider.id,
            peptide_name=payload.peptide_name,
            purpose=payload.purpose,
            dosage=payload.dosage,
            frequency=payload.frequency,
            route=payload.route,
            status=payload.status,
            start_date=payload.start_date,
            end_date=payload.end_date,
            notes=payload.notes,
        )

        protocol = await self.peptide_repository.create(protocol)

        await AuditService.create_log(
            db=self.db,
            actor_user_id=current_user.id,
            payload=AuditLogCreate(
                action="peptide_protocol_created",
                resource="peptide_protocol",
                resource_id=str(protocol.id),
                description="Peptide protocol created",
                audit_metadata={
                    "program_id": str(program.id),
                    "patient_id": str(patient.id),
                    "provider_id": str(provider.id),
                    "peptide_name": protocol.peptide_name,
                    "status": protocol.status.value,
                },
            ),
        )

        await self.db.commit()
        await self.db.refresh(protocol)

        return protocol

    async def get_protocols(
        self,
        current_user,
        limit: int = 20,
        offset: int = 0,
        status: PeptideProtocolStatus | None = None,
    ) -> list[PeptideProtocol]:
        if self._is_admin(current_user):
            return await self.peptide_repository.get_all(
                limit=limit,
                offset=offset,
                status=status,
            )

        provider_id = self._provider_id(current_user)

        if provider_id:
            return await self.peptide_repository.get_by_provider_id(
                provider_id=provider_id,
                limit=limit,
                offset=offset,
                status=status,
            )

        patient_id = self._patient_id(current_user)

        if patient_id:
            return await self.peptide_repository.get_by_patient_id(
                patient_id=patient_id,
                limit=limit,
                offset=offset,
                status=status,
            )

        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Unauthorized peptide protocol access",
        )

    async def get_protocol_by_id(
        self,
        protocol_id: UUID,
        current_user,
    ) -> PeptideProtocol:
        protocol = await self.peptide_repository.get_by_id(
            protocol_id
        )

        if not protocol:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Peptide protocol not found",
            )

        await self._validate_protocol_access(
            protocol,
            current_user,
        )

        return protocol

    async def update_protocol(
        self,
        protocol_id: UUID,
        payload: PeptideProtocolUpdate,
        current_user,
    ) -> PeptideProtocol:
        protocol = await self.peptide_repository.get_by_id(
            protocol_id
        )

        if not protocol:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Peptide protocol not found",
            )

        await self._validate_provider_write_access(
            protocol.provider_id,
            current_user,
        )

        next_start_date = (
            payload.start_date
            if payload.start_date is not None
            else protocol.start_date
        )
        next_end_date = (
            payload.end_date
            if payload.end_date is not None
            else protocol.end_date
        )

        self._validate_date_range(
            next_start_date,
            next_end_date,
        )

        old_status = protocol.status

        update_data = payload.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(protocol, field, value)

        protocol = await self.peptide_repository.update(protocol)

        audit_action = self._audit_action_for_status_change(
            old_status=old_status,
            new_status=protocol.status,
        )

        await AuditService.create_log(
            db=self.db,
            actor_user_id=current_user.id,
            payload=AuditLogCreate(
                action=audit_action,
                resource="peptide_protocol",
                resource_id=str(protocol.id),
                description="Peptide protocol updated",
                audit_metadata={
                    "old_status": old_status.value,
                    "new_status": protocol.status.value,
                    "peptide_name": protocol.peptide_name,
                },
            ),
        )

        await self.db.commit()
        await self.db.refresh(protocol)

        return protocol

    async def get_patient_protocols(
        self,
        patient_id: UUID,
        current_user,
        limit: int = 20,
        offset: int = 0,
        status: PeptideProtocolStatus | None = None,
    ) -> list[PeptideProtocol]:
        patient = await self.patient_repository.get_by_id(patient_id)

        if not patient:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Patient not found",
            )

        if self._is_admin(current_user):
            return await self.peptide_repository.get_by_patient_id(
                patient_id=patient_id,
                limit=limit,
                offset=offset,
                status=status,
            )

        provider_id = self._provider_id(current_user)

        if provider_id:
            return await (
                self.peptide_repository.get_by_patient_and_provider_id(
                    patient_id=patient_id,
                    provider_id=provider_id,
                    limit=limit,
                    offset=offset,
                    status=status,
                )
            )

        current_patient_id = self._patient_id(current_user)

        if current_patient_id and current_patient_id == patient_id:
            return await self.peptide_repository.get_by_patient_id(
                patient_id=patient_id,
                limit=limit,
                offset=offset,
                status=status,
            )

        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Unauthorized patient peptide protocol access",
        )
