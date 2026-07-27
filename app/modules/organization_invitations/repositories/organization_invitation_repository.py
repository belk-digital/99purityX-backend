from uuid import UUID

from sqlalchemy import (
    and_,
    select,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)
from sqlalchemy.orm import (
    selectinload,
)

from app.modules.organization_invitations.constants.invitation_enums import (
    InvitationStatus,
)
from app.modules.organization_invitations.models.organization_invitation import (
    OrganizationInvitation,
)


class OrganizationInvitationRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create(
        self,
        invitation: OrganizationInvitation,
    ) -> OrganizationInvitation:

        self.db.add(invitation)

        await self.db.flush()

        await self.db.refresh(invitation)

        return invitation

    async def get_by_id(
        self,
        invitation_id: UUID,
    ) -> OrganizationInvitation | None:

        query = (
            select(OrganizationInvitation)
            .where(
                OrganizationInvitation.id == invitation_id
            )
            .options(
                selectinload(
                    OrganizationInvitation.organization
                ),
                selectinload(
                    OrganizationInvitation.inviter
                ),
            )
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_by_token(
        self,
        invitation_token: str,
    ) -> OrganizationInvitation | None:

        query = (
            select(OrganizationInvitation)
            .where(
                OrganizationInvitation.invitation_token
                == invitation_token
            )
            .options(
                selectinload(
                    OrganizationInvitation.organization
                ),
                selectinload(
                    OrganizationInvitation.inviter
                ),
            )
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()
    
    
    async def get_pending_by_token(
        self,
        invitation_token: str,
    ) -> OrganizationInvitation | None:

        query = (
            select(OrganizationInvitation)
            .where(
                and_(
                    OrganizationInvitation.invitation_token
                    == invitation_token,
                    OrganizationInvitation.status
                    == InvitationStatus.PENDING,
                )
            )
            .options(
                selectinload(
                    OrganizationInvitation.organization
                ),
                selectinload(
                    OrganizationInvitation.inviter
                ),
            )
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_by_email(
        self,
        email: str,
    ) -> list[OrganizationInvitation]:

        query = (
            select(OrganizationInvitation)
            .where(
                OrganizationInvitation.email == email
            )
            .order_by(
                OrganizationInvitation.created_at.desc()
            )
        )

        result = await self.db.execute(query)

        return result.scalars().all()

    async def get_pending_by_email(
        self,
        organization_id: UUID,
        email: str,
    ) -> OrganizationInvitation | None:

        query = (
            select(OrganizationInvitation)
            .where(
                and_(
                    OrganizationInvitation.organization_id
                    == organization_id,
                    OrganizationInvitation.email == email,
                    OrganizationInvitation.status
                    == InvitationStatus.PENDING,
                )
            )
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_by_organization(
        self,
        organization_id: UUID,
    ) -> list[OrganizationInvitation]:

        query = (
            select(OrganizationInvitation)
            .where(
                OrganizationInvitation.organization_id
                == organization_id
            )
            .options(
                selectinload(
                    OrganizationInvitation.inviter
                )
            )
            .order_by(
                OrganizationInvitation.created_at.desc()
            )
        )

        result = await self.db.execute(query)

        return result.scalars().all()

    async def get_all(
        self,
    ) -> list[OrganizationInvitation]:

        query = (
            select(OrganizationInvitation)
            .options(
                selectinload(
                    OrganizationInvitation.organization
                ),
                selectinload(
                    OrganizationInvitation.inviter
                ),
            )
            .order_by(
                OrganizationInvitation.created_at.desc()
            )
        )

        result = await self.db.execute(query)

        return result.scalars().all()

    async def delete(
        self,
        invitation: OrganizationInvitation,
    ) -> None:

        await self.db.delete(
            invitation,
        )

        await self.db.flush()
        
    