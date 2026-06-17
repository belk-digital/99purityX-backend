from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.appointments.repositories.appointment_repository import (
    AppointmentRepository,
)

from app.modules.audit.schemas.audit_schema import (
    AuditLogCreate,
)

from app.modules.audit.services.audit_service import (
    AuditService,
)

from app.modules.consultations.enums.consultation_enums import (
    ConsultationStatus,
)

from app.modules.consultations.models.consultation_model import (
    Consultation,
)

from app.modules.consultations.repositories.consultation_repository import (
    ConsultationRepository,
)

from app.modules.consultations.schemas.consultation_schema import (
    ConsultationCreate,
    ConsultationUpdate,
)
from app.modules.consultations.enums.consultation_enums import (
    ConsultationStatus,
)

class ConsultationService:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

        self.consultation_repo = (
            ConsultationRepository(db)
        )

        self.appointment_repo = (
            AppointmentRepository(db)
        )

    async def create_consultation(
        self,
        payload: ConsultationCreate,
        current_user,
    ) -> Consultation:

        provider = (
            current_user.provider_profile
        )

        if not provider:
            raise HTTPException(
                status_code=403,
                detail="Provider profile required",
            )

        if not provider.is_active:
            raise HTTPException(
                status_code=403,
                detail="Inactive providers cannot create consultations",
            )

        appointment = (
            await self.appointment_repo.get_by_id(
                payload.appointment_id
            )
        )

        if not appointment:
            raise HTTPException(
                status_code=404,
                detail="Appointment not found",
            )

        if (
            appointment.provider_id
            != provider.id
        ):
            raise HTTPException(
                status_code=403,
                detail="Unauthorized appointment access",
            )

        existing_consultation = (
            await self.consultation_repo.get_by_appointment_id(
                payload.appointment_id
            )
        )

        if existing_consultation:
            raise HTTPException(
                status_code=400,
                detail="Consultation already exists for this appointment",
            )

        consultation = Consultation(
            appointment_id=appointment.id,
            patient_id=appointment.patient_id,
            provider_id=appointment.provider_id,
            started_at=payload.started_at,
            chief_complaint=payload.chief_complaint,
            provider_notes=payload.provider_notes,
        )

        consultation = (
            await self.consultation_repo.create(
                consultation
            )
        )

        await AuditService.create_log(
            db=self.db,
            actor_user_id=current_user.id,
            payload=AuditLogCreate(
                action="consultation_created",
                resource="consultation",
                resource_id=str(
                    consultation.id
                ),
                description="Consultation created",
                audit_metadata={
                    "appointment_id": str(
                        appointment.id
                    ),
                },
            ),
        )

        return consultation

    async def get_my_consultations(
        self,
        current_user,
        limit: int = 20,
        offset: int = 0,
        status: ConsultationStatus | None = None,
    ):

        if current_user.provider_profile:

            return (
                await self.consultation_repo.get_provider_consultations(
                    current_user.provider_profile.id,
                    limit=limit,
                    offset=offset,
                    status=status,
                )
            )

        if current_user.patient:

            return (
                await self.consultation_repo.get_patient_consultations(
                    current_user.patient.id,
                    limit=limit,
                    offset=offset,
                    status=status,
                )
            )

        raise HTTPException(
            status_code=403,
            detail="Unauthorized access",
        )

    async def get_consultation_by_id(
        self,
        consultation_id,
        current_user,
    ):

        consultation = (
            await self.consultation_repo.get_by_id(
                consultation_id
            )
        )

        if not consultation:
            raise HTTPException(
                status_code=404,
                detail="Consultation not found",
            )

        if current_user.provider_profile:

            if (
                consultation.provider_id
                != current_user.provider_profile.id
            ):
                raise HTTPException(
                    status_code=403,
                    detail="Unauthorized consultation access",
                )

        elif current_user.patient:

            if (
                consultation.patient_id
                != current_user.patient.id
            ):
                raise HTTPException(
                    status_code=403,
                    detail="Unauthorized consultation access",
                )

        return consultation

    async def update_consultation(
        self,
        consultation_id,
        payload: ConsultationUpdate,
        current_user,
    ) -> Consultation:

        consultation = (
            await self.consultation_repo.get_by_id(
                consultation_id
            )
        )

        if not consultation:
            raise HTTPException(
                status_code=404,
                detail="Consultation not found",
            )

        if not current_user.provider_profile:
            raise HTTPException(
                status_code=403,
                detail="Provider access required",
            )

        if (
            consultation.provider_id
            != current_user.provider_profile.id
        ):
            raise HTTPException(
                status_code=403,
                detail="Unauthorized consultation update",
            )

        if (
            consultation.status
            == ConsultationStatus.COMPLETED
        ):
            raise HTTPException(
                status_code=400,
                detail="Completed consultations cannot be modified",
            )

        if (
            payload.ended_at
            and payload.ended_at
            < consultation.started_at
        ):
            raise HTTPException(
                status_code=400,
                detail="ended_at must be after started_at",
            )

        if payload.ended_at is not None:
            consultation.ended_at = (
                payload.ended_at
            )

        if payload.provider_notes is not None:
            consultation.provider_notes = (
                payload.provider_notes
            )

        if payload.summary is not None:
            consultation.summary = (
                payload.summary
            )

        if (
            payload.follow_up_required
            is not None
        ):
            consultation.follow_up_required = (
                payload.follow_up_required
            )

        if payload.status is not None:
            consultation.status = (
                payload.status
            )

        consultation = (
            await self.consultation_repo.update(
                consultation
            )
        )

        audit_action = (
            "consultation_updated"
        )

        if (
            consultation.status
            == ConsultationStatus.COMPLETED
        ):
            audit_action = (
                "consultation_completed"
            )

        if (
            consultation.status
            == ConsultationStatus.CANCELLED
        ):
            audit_action = (
                "consultation_cancelled"
            )

        await AuditService.create_log(
            db=self.db,
            actor_user_id=current_user.id,
            payload=AuditLogCreate(
                action=audit_action,
                resource="consultation",
                resource_id=str(
                    consultation.id
                ),
                description="Consultation updated",
                audit_metadata={
                    "status": consultation.status.value,
                },
            ),
        )

        return consultation