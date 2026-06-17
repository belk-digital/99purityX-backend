from datetime import (
    datetime,
    timedelta,
    timezone,
)

from uuid import UUID

from fastapi import (
    HTTPException,
    status,
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models.user import User

from app.modules.appointments.constants.appointment_constants import (
    MAX_APPOINTMENT_DURATION_HOURS,
    MIN_APPOINTMENT_DURATION_MINUTES,
)

from app.modules.appointments.enums.appointment_enums import (
    AppointmentStatus,
)

from app.modules.appointments.models.appointment_model import (
    Appointment,
)

from app.modules.appointments.repositories.appointment_repository import (
    AppointmentRepository,
)

from app.modules.appointments.schemas.appointment_schema import (
    AppointmentCreate,
    AppointmentUpdate,
)

from app.modules.audit.schemas.audit_schema import (
    AuditLogCreate,
)

from app.modules.audit.services.audit_service import (
    AuditService,
)

from app.modules.patients.repositories.patient_repository import (
    PatientRepository,
)

from app.modules.providers.repositories.provider_repository import (
    ProviderRepository,
)


class AppointmentService:

    @staticmethod
    async def validate_appointment_access(
        appointment: Appointment,
        current_user: User,
    ) -> None:

        # ADMIN ACCESS
        if current_user.role.name == "admin":
            return

        # PATIENT ACCESS
        if current_user.patient:
            if (
                appointment.patient_id
                != current_user.patient.id
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied",
                )

            return

        # PROVIDER ACCESS
        if current_user.provider_profile:
            if (
                appointment.provider_id
                != current_user.provider_profile.id
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied",
                )

            return

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    @staticmethod
    async def create_appointment(
        db: AsyncSession,
        patient_id: UUID,
        data: AppointmentCreate,
        actor_user_id: UUID,
    ) -> Appointment:

        appointment_repository = (
            AppointmentRepository(db)
        )

        patient_repository = (
            PatientRepository(db)
        )

        provider_repository = (
            ProviderRepository(db)
        )

        # PREVENT PAST APPOINTMENTS
        if data.scheduled_start < datetime.now(
            timezone.utc
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Appointments cannot be created "
                    "in the past"
                ),
            )

        # VALIDATE TIME RANGE
        if data.scheduled_end <= data.scheduled_start:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "scheduled_end must be after "
                    "scheduled_start"
                ),
            )

        # VALIDATE DURATION
        duration = (
            data.scheduled_end
            - data.scheduled_start
        )

        if duration < timedelta(
            minutes=MIN_APPOINTMENT_DURATION_MINUTES,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Appointment duration too short",
            )

        if duration > timedelta(
            hours=MAX_APPOINTMENT_DURATION_HOURS,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Appointment duration too long",
            )

        # VALIDATE PATIENT
        patient = await patient_repository.get_by_id(
            patient_id,
        )

        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found",
            )

        # VALIDATE PROVIDER
        provider = await provider_repository.get_by_id(
            data.provider_id,
        )

        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Provider not found",
            )

        # VALIDATE PROVIDER ACTIVE
        if not provider.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provider is inactive",
            )

        # DOUBLE BOOKING CHECK
        has_conflict = (
            await appointment_repository
            .provider_has_conflicting_appointment(
                provider_id=str(provider.id),
                scheduled_start=data.scheduled_start,
                scheduled_end=data.scheduled_end,
            )
        )

        if has_conflict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Provider already has an appointment "
                    "during this time"
                ),
            )

        # CREATE APPOINTMENT
        appointment = Appointment(
            patient_id=patient.id,
            provider_id=provider.id,
            scheduled_start=data.scheduled_start,
            scheduled_end=data.scheduled_end,
            reason=data.reason,
            notes=data.notes,
        )

        appointment = await appointment_repository.create(
            appointment,
        )

        # AUDIT LOG
        await AuditService.create_log(
            db=db,
            actor_user_id=actor_user_id,
            payload=AuditLogCreate(
                action="appointment_created",
                resource="appointment",
                resource_id=str(appointment.id),
                description="Appointment created",
                audit_metadata={
                    "patient_id": str(patient.id),
                    "provider_id": str(provider.id),
                },
            ),
        )

        await db.commit()

        await db.refresh(appointment)

        return appointment

    @staticmethod
    async def get_appointment(
        db: AsyncSession,
        appointment_id: UUID,
    ) -> Appointment:

        appointment_repository = (
            AppointmentRepository(db)
        )

        appointment = (
            await appointment_repository.get_by_id(
                appointment_id,
            )
        )

        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found",
            )

        return appointment

    @staticmethod
    async def update_appointment(
        db: AsyncSession,
        appointment: Appointment,
        data: AppointmentUpdate,
        actor_user_id: UUID,
    ) -> Appointment:

        # PREVENT MODIFICATION OF FINALIZED STATES
        if appointment.status == AppointmentStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Completed appointments cannot "
                    "be modified"
                ),
            )

        if appointment.status == AppointmentStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Cancelled appointments cannot "
                    "be modified"
                ),
            )

        old_status = appointment.status

        # VALIDATE TIME RANGE
        if (
            data.scheduled_start
            and data.scheduled_end
            and data.scheduled_end
            <= data.scheduled_start
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid schedule range",
            )

        # UPDATE FIELDS
        update_data = data.model_dump(
            exclude_unset=True,
        )

        for field, value in update_data.items():
            setattr(appointment, field, value)

        await db.flush()

        # AUDIT STATUS CHANGES
        if old_status != appointment.status:

            await AuditService.create_log(
                db=db,
                actor_user_id=actor_user_id,
                payload=AuditLogCreate(
                    action="appointment_status_changed",
                    resource="appointment",
                    resource_id=str(appointment.id),
                    description="Appointment status changed",
                    audit_metadata={
                        "old_status": old_status.value,
                        "new_status": appointment.status.value,
                    },
                ),
            )

        await db.commit()

        await db.refresh(appointment)

        return appointment