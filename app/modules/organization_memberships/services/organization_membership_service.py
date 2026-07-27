from datetime import datetime
from uuid import UUID

from fastapi import (
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.enums.audit_enums import (
    AuditAction,
    AuditResource,
)
from app.modules.audit.schemas.audit_schema import (
    AuditLogCreate,
)
from app.modules.audit.services.audit_service import (
    AuditService,
)
from app.modules.auth.repositories.user_repository import (
    UserRepository,
)
from app.modules.organization_memberships.constants.membership_enums import (
    MembershipStatus,
    OrganizationRole,
)
from app.modules.organization_memberships.models.organization_membership import (
    OrganizationMembership,
)
from app.modules.organization_memberships.repositories.organization_membership_repository import (
    OrganizationMembershipRepository,
)
from app.modules.organization_memberships.schemas.organization_membership_schema import (
    OrganizationMembershipCreate,
    OrganizationMembershipUpdate,
)
from app.modules.organizations.repositories.organization_repository import (
    OrganizationRepository,
)


class OrganizationMembershipService:

    @staticmethod
    async def create_membership(
        db: AsyncSession,
        data: OrganizationMembershipCreate,
        actor_user_id: UUID,
    ) -> OrganizationMembership:

        membership_repository = OrganizationMembershipRepository(db)
        organization_repository = OrganizationRepository(db)
        user_repository = UserRepository(db)

        organization = await organization_repository.get_by_id(
            data.organization_id,
        )

        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found.",
            )

        user = await user_repository.get_by_id(
            data.user_id,
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )

        exists = await membership_repository.membership_exists(
            organization_id=data.organization_id,
            user_id=data.user_id,
        )

        if exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this organization.",
            )

        if data.is_primary:
            await membership_repository.clear_primary_memberships(
                data.user_id,
            )

        if data.is_default:
            await membership_repository.clear_default_memberships(
                data.user_id,
            )

        membership = OrganizationMembership(
            organization_id=data.organization_id,
            user_id=data.user_id,
            role=data.role,
            membership_status=data.membership_status,
            is_primary=data.is_primary,
            is_default=data.is_default,
            is_active=data.is_active,
            notes=data.notes,
        )

        if (
            membership.membership_status
            == MembershipStatus.ACTIVE
            and membership.joined_at is None
        ):
            membership.joined_at = datetime.utcnow()

        membership = await membership_repository.create(
            membership,
        )

        await AuditService.create_log(
            db=db,
            actor_user_id=actor_user_id,
            payload=AuditLogCreate(
                action=AuditAction.CREATE,
                resource=AuditResource.ORGANIZATION_MEMBERSHIP,
                resource_id=str(membership.id),
                description="Organization membership created",
                audit_metadata={
                    "organization_id": str(membership.organization_id),
                    "user_id": str(membership.user_id),
                    "role": membership.role.value,
                },
            ),
        )

        await db.commit()

        await db.refresh(
            membership,
        )

        return membership

    @staticmethod
    async def get_membership(
        db: AsyncSession,
        membership_id: UUID,
    ) -> OrganizationMembership:

        repository = OrganizationMembershipRepository(db)

        membership = await repository.get_by_id(
            membership_id,
        )

        if not membership:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization membership not found.",
            )

        return membership

    @staticmethod
    async def update_membership(
        db: AsyncSession,
        membership: OrganizationMembership,
        data: OrganizationMembershipUpdate,
        actor_user_id: UUID,
    ) -> OrganizationMembership:

        membership_repository = OrganizationMembershipRepository(db)

        update_data = data.model_dump(
            exclude_unset=True,
        )

        if update_data.get("is_primary") is True:
            await membership_repository.clear_primary_memberships(
                membership.user_id,
            )

        if update_data.get("is_default") is True:
            await membership_repository.clear_default_memberships(
                membership.user_id,
            )

        for field, value in update_data.items():
            setattr(
                membership,
                field,
                value,
            )

        if (
            membership.membership_status
            == MembershipStatus.ACTIVE
            and membership.joined_at is None
        ):
            membership.joined_at = datetime.utcnow()

        await db.flush()

        await AuditService.create_log(
            db=db,
            actor_user_id=actor_user_id,
            payload=AuditLogCreate(
                action=AuditAction.UPDATE,
                resource=AuditResource.ORGANIZATION_MEMBERSHIP,
                resource_id=str(membership.id),
                description="Organization membership updated",
                audit_metadata={
                    "organization_id": str(membership.organization_id),
                    "user_id": str(membership.user_id),
                    "role": membership.role.value,
                },
            ),
        )

        await db.commit()

        await db.refresh(
            membership,
        )

        return membership

    @staticmethod
    async def delete_membership(
        db: AsyncSession,
        membership: OrganizationMembership,
        actor_user_id: UUID,
    ) -> None:

        repository = OrganizationMembershipRepository(db)

        if membership.role == OrganizationRole.OWNER:

            active_owners = await repository.count_active_owners_excluding(
                organization_id=membership.organization_id,
                membership_id=membership.id,
            )

            if active_owners == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot remove the last active owner of an organization.",
                )

        await repository.delete(
            membership,
        )

        await AuditService.create_log(
            db=db,
            actor_user_id=actor_user_id,
            payload=AuditLogCreate(
                action=AuditAction.DELETE,
                resource=AuditResource.ORGANIZATION_MEMBERSHIP,
                resource_id=str(membership.id),
                description="Organization membership deleted",
                audit_metadata={
                    "organization_id": str(membership.organization_id),
                    "user_id": str(membership.user_id),
                },
            ),
        )

        await db.commit()