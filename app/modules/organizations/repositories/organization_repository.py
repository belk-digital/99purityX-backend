from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.organizations.models.organization import (
    Organization,
)


class OrganizationRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create(
        self,
        organization: Organization,
    ) -> Organization:

        self.db.add(organization)

        await self.db.flush()

        await self.db.refresh(organization)

        return organization

    async def get_by_id(
        self,
        organization_id: UUID,
    ) -> Organization | None:

        query = (
            select(Organization)
            .where(
                Organization.id == organization_id
            )
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_by_slug(
        self,
        slug: str,
    ) -> Organization | None:

        query = (
            select(Organization)
            .where(
                Organization.slug == slug
            )
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_by_name(
        self,
        name: str,
    ) -> Organization | None:

        query = (
            select(Organization)
            .where(
                Organization.name == name
            )
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_all(
        self,
    ) -> list[Organization]:

        query = (
            select(Organization)
            .order_by(
                Organization.name.asc()
            )
        )

        result = await self.db.execute(query)

        return result.scalars().all()

    async def delete(
        self,
        organization: Organization,
    ) -> None:

        await self.db.delete(organization)

        await self.db.flush()