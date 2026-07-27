from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func

from app.modules.organization_memberships.models.organization_membership import (
    OrganizationMembership,
)
from app.modules.organization_memberships.constants.membership_enums import (
    MembershipStatus,
    OrganizationRole,
)

from app.modules.organization_memberships.constants.membership_enums import (
    MembershipStatus,
    OrganizationRole,
)


class OrganizationMembershipRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create(
        self,
        membership: OrganizationMembership,
    ) -> OrganizationMembership:

        self.db.add(membership)

        await self.db.flush()

        await self.db.refresh(membership)

        return membership

    async def get_by_id(
        self,
        membership_id: UUID,
    ) -> OrganizationMembership | None:

        query = (
            select(OrganizationMembership)
            .where(
                OrganizationMembership.id == membership_id
            )
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        user_id: UUID,
    ) -> list[OrganizationMembership]:

        query = (
            select(OrganizationMembership)
            .where(
                OrganizationMembership.user_id == user_id
            )
            .order_by(
                OrganizationMembership.created_at.asc()
            )
        )

        result = await self.db.execute(query)

        return result.scalars().all()

    async def get_by_organization(
        self,
        organization_id: UUID,
    ) -> list[OrganizationMembership]:

        query = (
            select(OrganizationMembership)
            .where(
                OrganizationMembership.organization_id == organization_id
            )
            .order_by(
                OrganizationMembership.created_at.asc()
            )
        )

        result = await self.db.execute(query)

        return result.scalars().all()

    async def get_user_membership(
        self,
        organization_id: UUID,
        user_id: UUID,
    ) -> OrganizationMembership | None:

        query = (
            select(OrganizationMembership)
            .where(
                OrganizationMembership.organization_id == organization_id,
                OrganizationMembership.user_id == user_id,
            )
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def membership_exists(
        self,
        organization_id: UUID,
        user_id: UUID,
    ) -> bool:

        membership = await self.get_user_membership(
            organization_id=organization_id,
            user_id=user_id,
        )

        return membership is not None

    async def get_primary_membership(
        self,
        user_id: UUID,
    ) -> OrganizationMembership | None:

        query = (
            select(OrganizationMembership)
            .where(
                OrganizationMembership.user_id == user_id,
                OrganizationMembership.is_primary.is_(True),
            )
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_default_membership(
        self,
        user_id: UUID,
    ) -> OrganizationMembership | None:

        query = (
            select(OrganizationMembership)
            .where(
                OrganizationMembership.user_id == user_id,
                OrganizationMembership.is_default.is_(True),
            )
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def delete(
        self,
        membership: OrganizationMembership,
    ) -> None:

        await self.db.delete(membership)

        await self.db.flush()
        
    async def get_all(
        self,
    ) -> list[OrganizationMembership]:

        query = (
            select(OrganizationMembership)
            .order_by(
                OrganizationMembership.created_at.asc()
            )
        )

        result = await self.db.execute(query)

        return result.scalars().all()
    
    async def clear_primary_memberships(
        self,
        user_id: UUID,
    ) -> None:

        memberships = await self.get_by_user(
            user_id,
        )

        for membership in memberships:
            membership.is_primary = False

        await self.db.flush()
        
    async def clear_default_memberships(
        self,
        user_id: UUID,
    ) -> None:

        memberships = await self.get_by_user(
            user_id,
        )

        for membership in memberships:
            membership.is_default = False

        await self.db.flush()
        
    async def count_active_owners(
        self,
        organization_id: UUID,
    ) -> int:

       
        query = (
            select(
                func.count()
            )
            .select_from(
                OrganizationMembership
            )
            .where(
                OrganizationMembership.organization_id == organization_id,
                OrganizationMembership.role == OrganizationRole.OWNER,
                OrganizationMembership.membership_status == MembershipStatus.ACTIVE,
                OrganizationMembership.is_active.is_(True),
            )
        )

        result = await self.db.execute(query)

        return result.scalar_one()
    
    async def count_active_owners_excluding(
        self,
        organization_id: UUID,
        membership_id: UUID,
    ) -> int:


        query = (
            select(
                func.count()
            )
            .select_from(
                OrganizationMembership
            )
            .where(
                OrganizationMembership.organization_id == organization_id,
                OrganizationMembership.id != membership_id,
                OrganizationMembership.role == OrganizationRole.OWNER,
                OrganizationMembership.membership_status == MembershipStatus.ACTIVE,
                OrganizationMembership.is_active.is_(True),
            )
        )

        result = await self.db.execute(query)

        return result.scalar_one()