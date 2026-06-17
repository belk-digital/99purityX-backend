from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    and_,
    select,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from sqlalchemy.orm import (
    selectinload,
)

from app.modules.appointments.enums.appointment_enums import (
    AppointmentStatus,
)

from app.modules.appointments.models.appointment_model import (
    Appointment,
)


class AppointmentRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create(
        self,
        appointment: Appointment,
    ) -> Appointment:

        self.db.add(appointment)

        await self.db.flush()

        await self.db.refresh(appointment)

        return appointment

    async def get_by_id(
        self,
        appointment_id: UUID,
    ) -> Appointment | None:

        query = (
            select(Appointment)
            .where(
                Appointment.id == appointment_id
            )
            .options(
                selectinload(Appointment.patient),
                selectinload(Appointment.provider),
            )
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_patient_appointments(
        self,
        patient_id: UUID,
    ):

        query = (
            select(Appointment)
            .where(
                Appointment.patient_id == patient_id
            )
            .options(
                selectinload(Appointment.provider),
                selectinload(Appointment.patient),
            )
            .order_by(
                Appointment.scheduled_start.desc()
            )
        )

        result = await self.db.execute(query)

        return result.scalars().all()

    async def get_provider_appointments(
        self,
        provider_id: UUID,
    ):

        query = (
            select(Appointment)
            .where(
                Appointment.provider_id == provider_id
            )
            .options(
                selectinload(Appointment.provider),
                selectinload(Appointment.patient),
            )
            .order_by(
                Appointment.scheduled_start.desc()
            )
        )

        result = await self.db.execute(query)

        return result.scalars().all()

    async def provider_has_conflicting_appointment(
        self,
        provider_id: str,
        scheduled_start: datetime,
        scheduled_end: datetime,
    ) -> bool:

        query = (
            select(Appointment)
            .where(
                and_(
                    Appointment.provider_id
                    == provider_id,

                    Appointment.status
                    != AppointmentStatus.CANCELLED,

                    Appointment.scheduled_start
                    < scheduled_end,

                    Appointment.scheduled_end
                    > scheduled_start,
                )
            )
        )

        result = await self.db.execute(query)

        appointment = result.scalar_one_or_none()

        return appointment is not None