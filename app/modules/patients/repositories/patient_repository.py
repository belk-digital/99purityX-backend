from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.patients.models.patient_model import (
    Patient,
)


class PatientRepository:
    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create_patient(
        self,
        patient: Patient,
    ) -> Patient:
        self.db.add(patient)

        await self.db.commit()
        await self.db.refresh(patient)

        return patient

    async def get_by_user_id(
        self,
        user_id: UUID,
    ) -> Patient | None:

        result = await self.db.execute(
            select(Patient).where(
                Patient.user_id == user_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_id(
        self,
        patient_id: UUID,
    ) -> Patient | None:

        result = await self.db.execute(
            select(Patient).where(
                Patient.id == patient_id
            )
        )

        return result.scalar_one_or_none()

    async def update_patient(
        self,
        patient: Patient,
    ) -> Patient:

        await self.db.commit()
        await self.db.refresh(patient)

        return patient