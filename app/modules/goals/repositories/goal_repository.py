from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.goals.enums.goal_enums import HealthGoalStatus
from app.modules.goals.models.goal_progress_model import GoalProgress
from app.modules.goals.models.health_goal_model import HealthGoal


class HealthGoalRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, goal: HealthGoal) -> HealthGoal:
        self.db.add(goal)

        await self.db.flush()
        await self.db.refresh(goal)

        return goal

    async def update(self, goal: HealthGoal) -> HealthGoal:
        await self.db.flush()
        await self.db.refresh(goal)

        return goal

    async def get_by_id(self, goal_id: UUID) -> HealthGoal | None:
        result = await self.db.execute(
            select(HealthGoal)
            .options(
                selectinload(HealthGoal.patient),
                selectinload(HealthGoal.provider),
                selectinload(HealthGoal.consultation),
                selectinload(HealthGoal.program),
                selectinload(HealthGoal.progress_records),
            )
            .where(HealthGoal.id == goal_id)
        )

        return result.scalar_one_or_none()

    async def get_all(
        self,
        limit: int = 20,
        offset: int = 0,
        status: HealthGoalStatus | None = None,
    ) -> list[HealthGoal]:
        query = select(HealthGoal).options(
            selectinload(HealthGoal.patient),
            selectinload(HealthGoal.provider),
            selectinload(HealthGoal.consultation),
            selectinload(HealthGoal.program),
        )

        if status:
            query = query.where(HealthGoal.status == status)

        query = (
            query.order_by(desc(HealthGoal.created_at))
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
        status: HealthGoalStatus | None = None,
    ) -> list[HealthGoal]:
        query = (
            select(HealthGoal)
            .options(
                selectinload(HealthGoal.patient),
                selectinload(HealthGoal.provider),
                selectinload(HealthGoal.consultation),
                selectinload(HealthGoal.program),
            )
            .where(HealthGoal.patient_id == patient_id)
        )

        if status:
            query = query.where(HealthGoal.status == status)

        query = (
            query.order_by(desc(HealthGoal.created_at))
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
        status: HealthGoalStatus | None = None,
    ) -> list[HealthGoal]:
        query = (
            select(HealthGoal)
            .options(
                selectinload(HealthGoal.patient),
                selectinload(HealthGoal.provider),
                selectinload(HealthGoal.consultation),
                selectinload(HealthGoal.program),
            )
            .where(HealthGoal.provider_id == provider_id)
        )

        if status:
            query = query.where(HealthGoal.status == status)

        query = (
            query.order_by(desc(HealthGoal.created_at))
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
        status: HealthGoalStatus | None = None,
    ) -> list[HealthGoal]:
        query = (
            select(HealthGoal)
            .options(
                selectinload(HealthGoal.patient),
                selectinload(HealthGoal.provider),
                selectinload(HealthGoal.consultation),
                selectinload(HealthGoal.program),
            )
            .where(
                HealthGoal.patient_id == patient_id,
                HealthGoal.provider_id == provider_id,
            )
        )

        if status:
            query = query.where(HealthGoal.status == status)

        query = (
            query.order_by(desc(HealthGoal.created_at))
            .offset(offset)
            .limit(limit)
        )

        result = await self.db.execute(query)

        return list(result.scalars().all())


class GoalProgressRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, progress: GoalProgress) -> GoalProgress:
        self.db.add(progress)

        await self.db.flush()
        await self.db.refresh(progress)

        return progress

    async def get_by_id(self, progress_id: UUID) -> GoalProgress | None:
        result = await self.db.execute(
            select(GoalProgress)
            .options(
                selectinload(GoalProgress.goal)
                .selectinload(HealthGoal.patient),
                selectinload(GoalProgress.goal)
                .selectinload(HealthGoal.provider),
                selectinload(GoalProgress.goal)
                .selectinload(HealthGoal.program),
            )
            .where(GoalProgress.id == progress_id)
        )

        return result.scalar_one_or_none()
