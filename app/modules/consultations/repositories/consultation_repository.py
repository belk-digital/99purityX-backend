from sqlalchemy import (
    desc,
    select,
)

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.orm import selectinload

from app.modules.consultations.models.consultation_model import (
    Consultation,
)
from app.modules.consultations.enums.consultation_enums import (
    ConsultationStatus,
)


class ConsultationRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create(
        self,
        consultation: Consultation,
    ) -> Consultation:

        self.db.add(consultation)

        await self.db.commit()

        await self.db.refresh(
            consultation
        )

        return consultation

    async def get_by_id(
        self,
        consultation_id,
    ) -> Consultation | None:

        result = await self.db.execute(
            select(Consultation)
            .options(
                selectinload(
                    Consultation.patient
                ),
                selectinload(
                    Consultation.provider
                ),
                selectinload(
                    Consultation.appointment
                ),
            )
            .where(
                Consultation.id == consultation_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_appointment_id(
        self,
        appointment_id,
    ) -> Consultation | None:

        result = await self.db.execute(
            select(Consultation)
            .where(
                Consultation.appointment_id
                == appointment_id
            )
        )

        return result.scalar_one_or_none()

    async def update(
        self,
        consultation: Consultation,
    ) -> Consultation:

        await self.db.commit()

        await self.db.refresh(
            consultation
        )

        return consultation

    async def get_provider_consultations(
        self,
        provider_id,
        limit: int = 20,
        offset: int = 0,
        status: ConsultationStatus | None = None,
    ):

        query = (
            select(Consultation)
            .options(
                selectinload(
                    Consultation.patient
                ),
                selectinload(
                    Consultation.appointment
                ),
            )
            .where(
                Consultation.provider_id
                == provider_id
            )
        )

        if status:
            query = query.where(
                Consultation.status == status
            )

        query = (
            query.order_by(
                desc(
                    Consultation.created_at
                )
            )
            .offset(offset)
            .limit(limit)
        )

        result = await self.db.execute(
            query
        )

        return result.scalars().all()

    async def get_patient_consultations(
        self,
        patient_id,
        limit: int = 20,
        offset: int = 0,
        status: ConsultationStatus | None = None,
    ):

        query = (
            select(Consultation)
            .options(
                selectinload(
                    Consultation.provider
                ),
                selectinload(
                    Consultation.appointment
                ),
            )
            .where(
                Consultation.patient_id
                == patient_id
            )
        )

        if status:
            query = query.where(
                Consultation.status == status
            )

        query = (
            query.order_by(
                desc(
                    Consultation.created_at
                )
            )
            .offset(offset)
            .limit(limit)
        )

        result = await self.db.execute(
            query
        )

        return result.scalars().all()