from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.optimization.enums.program_enums import (
    HabitProtocolStatus,
)
from app.modules.optimization.models.habit_log_model import HabitLog
from app.modules.optimization.models.habit_protocol_model import HabitProtocol


class HabitProtocolRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        habit: HabitProtocol,
    ) -> HabitProtocol:
        self.db.add(habit)

        await self.db.flush()
        await self.db.refresh(habit)

        return habit

    async def update(
        self,
        habit: HabitProtocol,
    ) -> HabitProtocol:
        await self.db.flush()
        await self.db.refresh(habit)

        return habit

    async def get_by_id(
        self,
        habit_id: UUID,
    ) -> HabitProtocol | None:
        result = await self.db.execute(
            select(HabitProtocol)
            .options(
                selectinload(HabitProtocol.program),
                selectinload(HabitProtocol.patient),
                selectinload(HabitProtocol.provider),
            )
            .where(HabitProtocol.id == habit_id)
        )

        return result.scalar_one_or_none()

    async def get_all(
        self,
        limit: int = 20,
        offset: int = 0,
        status: HabitProtocolStatus | None = None,
    ) -> list[HabitProtocol]:
        query = select(HabitProtocol).options(
            selectinload(HabitProtocol.program),
            selectinload(HabitProtocol.patient),
            selectinload(HabitProtocol.provider),
        )

        if status:
            query = query.where(HabitProtocol.status == status)

        query = (
            query.order_by(desc(HabitProtocol.created_at))
            .offset(offset)
            .limit(limit)
        )

        result = await self.db.execute(query)

        return list(result.scalars().all())

    async def get_by_patient_id(
        self,
        patient_id: UUID,
        limit: int = 20,
        offset: int = 0,
        status: HabitProtocolStatus | None = None,
    ) -> list[HabitProtocol]:
        query = (
            select(HabitProtocol)
            .options(
                selectinload(HabitProtocol.program),
                selectinload(HabitProtocol.patient),
                selectinload(HabitProtocol.provider),
            )
            .where(HabitProtocol.patient_id == patient_id)
        )

        if status:
            query = query.where(HabitProtocol.status == status)

        query = (
            query.order_by(desc(HabitProtocol.created_at))
            .offset(offset)
            .limit(limit)
        )

        result = await self.db.execute(query)

        return list(result.scalars().all())

    async def get_by_provider_id(
        self,
        provider_id: UUID,
        limit: int = 20,
        offset: int = 0,
        status: HabitProtocolStatus | None = None,
    ) -> list[HabitProtocol]:
        query = (
            select(HabitProtocol)
            .options(
                selectinload(HabitProtocol.program),
                selectinload(HabitProtocol.patient),
                selectinload(HabitProtocol.provider),
            )
            .where(HabitProtocol.provider_id == provider_id)
        )

        if status:
            query = query.where(HabitProtocol.status == status)

        query = (
            query.order_by(desc(HabitProtocol.created_at))
            .offset(offset)
            .limit(limit)
        )

        result = await self.db.execute(query)

        return list(result.scalars().all())

    async def get_by_patient_and_provider_id(
        self,
        patient_id: UUID,
        provider_id: UUID,
        limit: int = 20,
        offset: int = 0,
        status: HabitProtocolStatus | None = None,
    ) -> list[HabitProtocol]:
        query = (
            select(HabitProtocol)
            .options(
                selectinload(HabitProtocol.program),
                selectinload(HabitProtocol.patient),
                selectinload(HabitProtocol.provider),
            )
            .where(
                HabitProtocol.patient_id == patient_id,
                HabitProtocol.provider_id == provider_id,
            )
        )

        if status:
            query = query.where(HabitProtocol.status == status)

        query = (
            query.order_by(desc(HabitProtocol.created_at))
            .offset(offset)
            .limit(limit)
        )

        result = await self.db.execute(query)

        return list(result.scalars().all())


class HabitLogRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        habit_log: HabitLog,
    ) -> HabitLog:
        self.db.add(habit_log)

        await self.db.flush()
        await self.db.refresh(habit_log)

        return habit_log

    async def get_by_id(
        self,
        log_id: UUID,
    ) -> HabitLog | None:
        result = await self.db.execute(
            select(HabitLog)
            .options(
                selectinload(HabitLog.habit_protocol)
                .selectinload(HabitProtocol.program),
                selectinload(HabitLog.habit_protocol)
                .selectinload(HabitProtocol.patient),
                selectinload(HabitLog.habit_protocol)
                .selectinload(HabitProtocol.provider),
                selectinload(HabitLog.patient),
            )
            .where(HabitLog.id == log_id)
        )

        return result.scalar_one_or_none()

    async def get_by_habit_and_date(
        self,
        habit_protocol_id: UUID,
        log_date,
    ) -> HabitLog | None:
        result = await self.db.execute(
            select(HabitLog).where(
                HabitLog.habit_protocol_id == habit_protocol_id,
                HabitLog.date == log_date,
            )
        )

        return result.scalar_one_or_none()

    async def get_all(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> list[HabitLog]:
        result = await self.db.execute(
            select(HabitLog)
            .options(
                selectinload(HabitLog.habit_protocol)
                .selectinload(HabitProtocol.program),
                selectinload(HabitLog.patient),
            )
            .order_by(desc(HabitLog.created_at))
            .offset(offset)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_by_patient_id(
        self,
        patient_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> list[HabitLog]:
        result = await self.db.execute(
            select(HabitLog)
            .options(
                selectinload(HabitLog.habit_protocol)
                .selectinload(HabitProtocol.program),
                selectinload(HabitLog.patient),
            )
            .where(HabitLog.patient_id == patient_id)
            .order_by(desc(HabitLog.created_at))
            .offset(offset)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_by_provider_id(
        self,
        provider_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> list[HabitLog]:
        result = await self.db.execute(
            select(HabitLog)
            .join(HabitProtocol)
            .options(
                selectinload(HabitLog.habit_protocol)
                .selectinload(HabitProtocol.program),
                selectinload(HabitLog.patient),
            )
            .where(HabitProtocol.provider_id == provider_id)
            .order_by(desc(HabitLog.created_at))
            .offset(offset)
            .limit(limit)
        )

        return list(result.scalars().all())
