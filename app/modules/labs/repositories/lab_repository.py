from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.labs.enums.lab_enums import LabOrderStatus
from app.modules.labs.models.lab_order_model import LabOrder
from app.modules.labs.models.lab_result_model import LabResult


class LabOrderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, lab_order: LabOrder) -> LabOrder:
        self.db.add(lab_order)

        await self.db.flush()
        await self.db.refresh(lab_order)

        return lab_order

    async def update(self, lab_order: LabOrder) -> LabOrder:
        await self.db.flush()
        await self.db.refresh(lab_order)

        return lab_order

    async def get_by_id(self, lab_order_id: UUID) -> LabOrder | None:
        result = await self.db.execute(
            select(LabOrder)
            .options(
                selectinload(LabOrder.patient),
                selectinload(LabOrder.provider),
                selectinload(LabOrder.consultation),
                selectinload(LabOrder.results),
            )
            .where(LabOrder.id == lab_order_id)
        )

        return result.scalar_one_or_none()

    async def get_all(
        self,
        limit: int = 20,
        offset: int = 0,
        status: LabOrderStatus | None = None,
    ) -> list[LabOrder]:
        query = select(LabOrder).options(
            selectinload(LabOrder.patient),
            selectinload(LabOrder.provider),
            selectinload(LabOrder.consultation),
        )

        if status:
            query = query.where(LabOrder.status == status)

        query = (
            query.order_by(desc(LabOrder.created_at))
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
        status: LabOrderStatus | None = None,
        include_results: bool = False,
    ) -> list[LabOrder]:
        options = [
            selectinload(LabOrder.patient),
            selectinload(LabOrder.provider),
            selectinload(LabOrder.consultation),
        ]

        if include_results:
            options.append(selectinload(LabOrder.results))

        query = (
            select(LabOrder)
            .options(*options)
            .where(LabOrder.patient_id == patient_id)
        )

        if status:
            query = query.where(LabOrder.status == status)

        query = (
            query.order_by(desc(LabOrder.created_at))
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
        status: LabOrderStatus | None = None,
    ) -> list[LabOrder]:
        query = (
            select(LabOrder)
            .options(
                selectinload(LabOrder.patient),
                selectinload(LabOrder.provider),
                selectinload(LabOrder.consultation),
            )
            .where(LabOrder.provider_id == provider_id)
        )

        if status:
            query = query.where(LabOrder.status == status)

        query = (
            query.order_by(desc(LabOrder.created_at))
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
        status: LabOrderStatus | None = None,
        include_results: bool = False,
    ) -> list[LabOrder]:
        options = [
            selectinload(LabOrder.patient),
            selectinload(LabOrder.provider),
            selectinload(LabOrder.consultation),
        ]

        if include_results:
            options.append(selectinload(LabOrder.results))

        query = (
            select(LabOrder)
            .options(*options)
            .where(
                LabOrder.patient_id == patient_id,
                LabOrder.provider_id == provider_id,
            )
        )

        if status:
            query = query.where(LabOrder.status == status)

        query = (
            query.order_by(desc(LabOrder.created_at))
            .offset(offset)
            .limit(limit)
        )

        result = await self.db.execute(query)

        return list(result.scalars().all())


class LabResultRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, lab_result: LabResult) -> LabResult:
        self.db.add(lab_result)

        await self.db.flush()
        await self.db.refresh(lab_result)

        return lab_result

    async def get_by_id(self, lab_result_id: UUID) -> LabResult | None:
        result = await self.db.execute(
            select(LabResult)
            .options(
                selectinload(LabResult.lab_order)
                .selectinload(LabOrder.patient),
                selectinload(LabResult.lab_order)
                .selectinload(LabOrder.provider),
                selectinload(LabResult.lab_order)
                .selectinload(LabOrder.consultation),
            )
            .where(LabResult.id == lab_result_id)
        )

        return result.scalar_one_or_none()
