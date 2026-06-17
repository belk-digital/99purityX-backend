from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.optimization.enums.program_enums import (
    OptimizationProgramStatus,
)
from app.modules.optimization.models.optimization_program_model import (
    OptimizationProgram,
)


class OptimizationProgramRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        program: OptimizationProgram,
    ) -> OptimizationProgram:
        self.db.add(program)

        await self.db.flush()
        await self.db.refresh(program)

        return program

    async def update(
        self,
        program: OptimizationProgram,
    ) -> OptimizationProgram:
        await self.db.flush()
        await self.db.refresh(program)

        return program

    async def get_by_id(
        self,
        program_id: UUID,
    ) -> OptimizationProgram | None:
        result = await self.db.execute(
            select(OptimizationProgram)
            .options(
                selectinload(OptimizationProgram.patient),
                selectinload(OptimizationProgram.provider),
                selectinload(OptimizationProgram.consultation),
            )
            .where(OptimizationProgram.id == program_id)
        )

        return result.scalar_one_or_none()

    async def get_all(
        self,
        limit: int = 20,
        offset: int = 0,
        status: OptimizationProgramStatus | None = None,
    ) -> list[OptimizationProgram]:
        query = select(OptimizationProgram).options(
            selectinload(OptimizationProgram.patient),
            selectinload(OptimizationProgram.provider),
            selectinload(OptimizationProgram.consultation),
        )

        if status:
            query = query.where(OptimizationProgram.status == status)

        query = (
            query.order_by(desc(OptimizationProgram.created_at))
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
        status: OptimizationProgramStatus | None = None,
    ) -> list[OptimizationProgram]:
        query = (
            select(OptimizationProgram)
            .options(
                selectinload(OptimizationProgram.patient),
                selectinload(OptimizationProgram.provider),
                selectinload(OptimizationProgram.consultation),
            )
            .where(OptimizationProgram.patient_id == patient_id)
        )

        if status:
            query = query.where(OptimizationProgram.status == status)

        query = (
            query.order_by(desc(OptimizationProgram.created_at))
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
        status: OptimizationProgramStatus | None = None,
    ) -> list[OptimizationProgram]:
        query = (
            select(OptimizationProgram)
            .options(
                selectinload(OptimizationProgram.patient),
                selectinload(OptimizationProgram.provider),
                selectinload(OptimizationProgram.consultation),
            )
            .where(OptimizationProgram.provider_id == provider_id)
        )

        if status:
            query = query.where(OptimizationProgram.status == status)

        query = (
            query.order_by(desc(OptimizationProgram.created_at))
            .offset(offset)
            .limit(limit)
        )

        result = await self.db.execute(query)

        return list(result.scalars().all())
