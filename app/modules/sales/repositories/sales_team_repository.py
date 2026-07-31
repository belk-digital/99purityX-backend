from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.sales.models.sales_team import (
    SalesTeam,
)


class SalesTeamRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create(
        self,
        sales_team: SalesTeam,
    ) -> SalesTeam:

        self.db.add(sales_team)

        await self.db.flush()

        await self.db.refresh(sales_team)

        return sales_team

    async def get_by_id(
        self,
        sales_team_id: UUID,
    ) -> SalesTeam | None:

        query = (
            select(SalesTeam)
            .where(
                SalesTeam.id == sales_team_id
            )
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_by_name(
        self,
        sales_organization_id: UUID,
        name: str,
    ) -> SalesTeam | None:

        query = (
            select(SalesTeam)
            .where(
                SalesTeam.sales_organization_id == sales_organization_id,
                SalesTeam.name == name,
            )
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_by_team_code(
        self,
        sales_organization_id: UUID,
        team_code: str,
    ) -> SalesTeam | None:

        query = (
            select(SalesTeam)
            .where(
                SalesTeam.sales_organization_id == sales_organization_id,
                SalesTeam.team_code == team_code,
            )
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_all(
        self,
    ) -> list[SalesTeam]:

        query = (
            select(SalesTeam)
            .order_by(
                SalesTeam.name.asc()
            )
        )

        result = await self.db.execute(query)

        return result.scalars().all()

    async def get_by_sales_organization(
        self,
        sales_organization_id: UUID,
    ) -> list[SalesTeam]:

        query = (
            select(SalesTeam)
            .where(
                SalesTeam.sales_organization_id == sales_organization_id,
            )
            .order_by(
                SalesTeam.name.asc()
            )
        )

        result = await self.db.execute(query)

        return result.scalars().all()

    async def delete(
        self,
        sales_team: SalesTeam,
    ) -> None:

        await self.db.delete(
            sales_team,
        )

        await self.db.flush()