from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.enums.audit_enums import (
    AuditAction,
    AuditResource,
)

from app.modules.audit.schemas.audit_schema import (
    AuditLogCreate,
)

from app.modules.audit.services.audit_service import (
    AuditService,
)

from app.modules.patients.models.patient_model import (
    Patient,
)

from app.modules.patients.repositories.patient_repository import (
    PatientRepository,
)

from app.modules.patients.schemas.patient_schema import (
    PatientUpdateSchema,
)


class PatientService:
    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db
        self.repository = PatientRepository(db)

    async def create_patient_profile(
        self,
        user_id: UUID,
    ) -> Patient:

        patient = Patient(
            user_id=user_id,
        )

        return await self.repository.create_patient(
            patient
        )

    async def get_my_profile(
        self,
        user_id: UUID,
    ) -> Patient | None:

        return await self.repository.get_by_user_id(
            user_id
        )

    async def get_patient_by_id(
        self,
        patient_id: UUID,
    ) -> Patient | None:

        return await self.repository.get_by_id(
            patient_id
        )

    async def update_my_profile(
        self,
        current_user_id: UUID,
        data: PatientUpdateSchema,
    ) -> Patient:

        patient = (
            await self.repository.get_by_user_id(
                current_user_id
            )
        )

        if not patient:
            raise ValueError(
                "Patient profile not found"
            )

        update_data = (
            data.model_dump(
                exclude_unset=True
            )
        )

        for field, value in update_data.items():
            setattr(
                patient,
                field,
                value,
            )

        updated_patient = (
            await self.repository.update_patient(
                patient
            )
        )

        await AuditService.create_log(
            db=self.db,
            actor_user_id=current_user_id,
            payload=AuditLogCreate(
                action=AuditAction.UPDATE.value,
                resource=AuditResource.PATIENT.value,
                resource_id=str(patient.id),
                description="Patient profile updated",
            ),
        )

        return updated_patient