from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.sales.models.sales_member import (
    SalesMember,
)


class SalesMemberRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create(
        self,
        sales_member: SalesMember,
    ) -> SalesMember:

        self.db.add(sales_member)

        await self.db.flush()

        await self.db.refresh(
            sales_member,
        )

        return sales_member

    async def get_by_id(
        self,
        sales_member_id: UUID,
    ) -> SalesMember | None:

        query = (
            select(SalesMember)
            .where(
                SalesMember.id == sales_member_id,
            )
        )

        result = await self.db.execute(
            query,
        )

        return result.scalar_one_or_none()

    async def get_by_user_and_sales_organization(
        self,
        user_id: UUID,
        sales_organization_id: UUID,
    ) -> SalesMember | None:

        query = (
            select(SalesMember)
            .where(
                SalesMember.user_id == user_id,
                SalesMember.sales_organization_id == sales_organization_id,
            )
        )

        result = await self.db.execute(
            query,
        )

        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        user_id: UUID,
    ) -> list[SalesMember]:

        query = (
            select(SalesMember)
            .where(
                SalesMember.user_id == user_id,
            )
            .order_by(
                SalesMember.created_at.desc(),
            )
        )

        result = await self.db.execute(
            query,
        )

        return result.scalars().all()

    async def get_all(
        self,
    ) -> list[SalesMember]:

        query = (
            select(SalesMember)
            .order_by(
                SalesMember.created_at.desc(),
            )
        )

        result = await self.db.execute(
            query,
        )

        return result.scalars().all()

    async def get_all_by_sales_organization(
        self,
        sales_organization_id: UUID,
    ) -> list[SalesMember]:

        query = (
            select(SalesMember)
            .where(
                SalesMember.sales_organization_id
                == sales_organization_id,
            )
            .order_by(
                SalesMember.created_at.desc(),
            )
        )

        result = await self.db.execute(
            query,
        )

        return result.scalars().all()

    async def get_all_by_sales_team(
        self,
        sales_team_id: UUID,
    ) -> list[SalesMember]:

        query = (
            select(SalesMember)
            .where(
                SalesMember.sales_team_id
                == sales_team_id,
            )
            .order_by(
                SalesMember.created_at.desc(),
            )
        )

        result = await self.db.execute(
            query,
        )

        return result.scalars().all()

    async def get_all_by_territory(
        self,
        territory_id: UUID,
    ) -> list[SalesMember]:

        query = (
            select(SalesMember)
            .where(
                SalesMember.territory_id
                == territory_id,
            )
            .order_by(
                SalesMember.created_at.desc(),
            )
        )

        result = await self.db.execute(
            query,
        )

        return result.scalars().all()

    async def delete(
        self,
        sales_member: SalesMember,
    ) -> None:

        await self.db.delete(
            sales_member,
        )

        await self.db.flush()