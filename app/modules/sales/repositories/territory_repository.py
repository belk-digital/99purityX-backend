from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.sales.models.territory import (
    Territory,
)


class TerritoryRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create(
        self,
        territory: Territory,
    ) -> Territory:

        self.db.add(territory)

        await self.db.flush()

        await self.db.refresh(territory)

        return territory

    async def get_by_id(
        self,
        territory_id: UUID,
    ) -> Territory | None:

        query = (
            select(Territory)
            .where(
                Territory.id == territory_id,
            )
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_by_name(
        self,
        sales_organization_id: UUID,
        parent_territory_id: UUID | None,
        name: str,
    ) -> Territory | None:

        query = (
            select(Territory)
            .where(
                Territory.sales_organization_id == sales_organization_id,
                Territory.parent_territory_id == parent_territory_id,
                Territory.name == name,
            )
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_by_code(
        self,
        sales_organization_id: UUID,
        code: str,
    ) -> Territory | None:

        query = (
            select(Territory)
            .where(
                Territory.sales_organization_id == sales_organization_id,
                Territory.code == code,
            )
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_all(
        self,
    ) -> list[Territory]:

        query = (
            select(Territory)
            .order_by(
                Territory.name.asc(),
            )
        )

        result = await self.db.execute(query)

        return result.scalars().all()

    async def get_all_by_sales_organization(
        self,
        sales_organization_id: UUID,
    ) -> list[Territory]:

        query = (
            select(Territory)
            .where(
                Territory.sales_organization_id == sales_organization_id,
            )
            .order_by(
                Territory.name.asc(),
            )
        )

        result = await self.db.execute(query)

        return result.scalars().all()

    async def get_children(
        self,
        parent_territory_id: UUID,
    ) -> list[Territory]:

        query = (
            select(Territory)
            .where(
                Territory.parent_territory_id == parent_territory_id,
            )
            .order_by(
                Territory.name.asc(),
            )
        )

        result = await self.db.execute(query)

        return result.scalars().all()

    async def has_children(
        self,
        territory_id: UUID,
    ) -> bool:

        query = (
            select(Territory.id)
            .where(
                Territory.parent_territory_id == territory_id,
            )
            .limit(1)
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none() is not None

    async def delete(
        self,
        territory: Territory,
    ) -> None:

        await self.db.delete(
            territory,
        )

        await self.db.flush()