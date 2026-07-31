from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.sales.models.sales_organization import (
    SalesOrganization,
)


class SalesOrganizationRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create(
        self,
        sales_organization: SalesOrganization,
    ) -> SalesOrganization:

        self.db.add(sales_organization)

        await self.db.flush()

        await self.db.refresh(sales_organization)

        return sales_organization

    async def get_by_id(
        self,
        sales_organization_id: UUID,
    ) -> SalesOrganization | None:

        query = (
            select(SalesOrganization)
            .where(
                SalesOrganization.id == sales_organization_id
            )
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_by_slug(
        self,
        slug: str,
    ) -> SalesOrganization | None:

        query = (
            select(SalesOrganization)
            .where(
                SalesOrganization.slug == slug
            )
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_by_name(
        self,
        name: str,
    ) -> SalesOrganization | None:

        query = (
            select(SalesOrganization)
            .where(
                SalesOrganization.name == name
            )
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_all(
        self,
    ) -> list[SalesOrganization]:

        query = (
            select(SalesOrganization)
            .order_by(
                SalesOrganization.name.asc()
            )
        )

        result = await self.db.execute(query)

        return result.scalars().all()

    async def delete(
        self,
        sales_organization: SalesOrganization,
    ) -> None:

        await self.db.delete(
            sales_organization,
        )

        await self.db.flush()