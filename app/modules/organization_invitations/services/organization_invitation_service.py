import secrets
from datetime import (
    datetime,
    timedelta,
    timezone,
)
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
from app.modules.auth.models.user import (
    User,
)
from app.modules.organization_invitations.constants.invitation_enums import (
    InvitationStatus,
)
from app.modules.organization_invitations.models.organization_invitation import (
    OrganizationInvitation,
)
from app.modules.organization_invitations.repositories.organization_invitation_repository import (
    OrganizationInvitationRepository,
)
from app.modules.organization_invitations.schemas.organization_invitation_schema import (
    OrganizationInvitationCreate,
    OrganizationInvitationUpdate,
)
from app.modules.organization_memberships.constants.membership_enums import (
    MembershipStatus,
)
from app.modules.organization_memberships.models.organization_membership import (
    OrganizationMembership,
)
from app.modules.organization_memberships.repositories.organization_membership_repository import (
    OrganizationMembershipRepository,
)
from app.modules.organization_memberships.schemas.organization_membership_schema import (
    OrganizationMembershipCreate,
)
from app.modules.organization_memberships.services.organization_membership_service import (
    OrganizationMembershipService,
)
from app.modules.organizations.repositories.organization_repository import (
    OrganizationRepository,
)

INVITATION_EXPIRY_DAYS = 7
INVITATION_TOKEN_BYTES = 32


class OrganizationInvitationService:

    @staticmethod
    async def create_invitation(
        db: AsyncSession,
        data: OrganizationInvitationCreate,
        invited_by: UUID,
    ) -> OrganizationInvitation:

        invitation_repository = OrganizationInvitationRepository(db)
        organization_repository = OrganizationRepository(db)
        membership_repository = OrganizationMembershipRepository(db)

        organization = await organization_repository.get_by_id(
            data.organization_id,
        )

        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found.",
            )

        if not organization.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization is not active.",
            )

        inviter_membership = await membership_repository.get_user_membership(
            organization_id=data.organization_id,
            user_id=invited_by,
        )

        if not inviter_membership or not inviter_membership.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inviter does not have an active membership in this organization.",
            )

        # Only DB-checked against PENDING invitations — accepted, declined,
        # expired, and cancelled invitations may legitimately exist for the
        # same organization + email, so this can't be a unique constraint.
        existing_invitation = await invitation_repository.get_pending_by_email(
            organization_id=data.organization_id,
            email=data.email.lower(),
        )

        if existing_invitation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A pending invitation already exists for this email.",
            )

        invitation = OrganizationInvitation(
            organization_id=data.organization_id,
            email=data.email.lower(),
            role=data.role,
            status=InvitationStatus.PENDING,
            invitation_token=OrganizationInvitationService._generate_token(),
            expires_at=OrganizationInvitationService._get_current_time()
            + timedelta(
                days=INVITATION_EXPIRY_DAYS,
            ),
            message=data.message,
            invited_by=invited_by,
        )

        invitation = await invitation_repository.create(
            invitation,
        )

        await AuditService.create_log(
            db=db,
            actor_user_id=invited_by,
            payload=AuditLogCreate(
                action=AuditAction.CREATE,
                resource=AuditResource.ORGANIZATION_INVITATION,
                resource_id=str(invitation.id),
                description="Organization invitation created",
                audit_metadata={
                    "organization_id": str(invitation.organization_id),
                    "email": invitation.email,
                    "role": invitation.role.value,
                },
            ),
        )

        await db.commit()

        await db.refresh(
            invitation,
        )

        return invitation

    @staticmethod
    async def get_invitation(
        db: AsyncSession,
        invitation_id: UUID,
    ) -> OrganizationInvitation:

        repository = OrganizationInvitationRepository(db)

        invitation = await repository.get_by_id(
            invitation_id,
        )

        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization invitation not found.",
            )

        return invitation

    @staticmethod
    async def get_invitation_by_token(
        db: AsyncSession,
        invitation_token: str,
    ) -> OrganizationInvitation:

        repository = OrganizationInvitationRepository(db)

        invitation = await repository.get_by_token(
            invitation_token,
        )

        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found.",
            )

        return invitation

    @staticmethod
    async def list_invitations_by_organization(
        db: AsyncSession,
        organization_id: UUID,
    ) -> list[OrganizationInvitation]:

        repository = OrganizationInvitationRepository(db)

        return await repository.get_by_organization(
            organization_id,
        )

    @staticmethod
    async def update_invitation(
        db: AsyncSession,
        invitation: OrganizationInvitation,
        data: OrganizationInvitationUpdate,
        actor_user_id: UUID,
    ) -> OrganizationInvitation:

        # Role is intentionally not part of OrganizationInvitationUpdate.
        # A role change is a cancel_invitation() + create_invitation(), so
        # the audit trail shows what happened instead of a mutated record.
        OrganizationInvitationService._validate_pending_status(
            invitation,
        )

        update_data = data.model_dump(
            exclude_unset=True,
        )

        for field, value in update_data.items():
            setattr(
                invitation,
                field,
                value,
            )

        await db.flush()

        await AuditService.create_log(
            db=db,
            actor_user_id=actor_user_id,
            payload=AuditLogCreate(
                action=AuditAction.UPDATE,
                resource=AuditResource.ORGANIZATION_INVITATION,
                resource_id=str(invitation.id),
                description="Organization invitation updated",
                audit_metadata={
                    "organization_id": str(invitation.organization_id),
                    "email": invitation.email,
                },
            ),
        )

        await db.commit()

        await db.refresh(
            invitation,
        )

        return invitation

    @staticmethod
    async def delete_invitation(
        db: AsyncSession,
        invitation: OrganizationInvitation,
        actor_user_id: UUID,
    ) -> None:

        repository = OrganizationInvitationRepository(db)

        await repository.delete(
            invitation,
        )

        await AuditService.create_log(
            db=db,
            actor_user_id=actor_user_id,
            payload=AuditLogCreate(
                action=AuditAction.DELETE,
                resource=AuditResource.ORGANIZATION_INVITATION,
                resource_id=str(invitation.id),
                description="Organization invitation deleted",
                audit_metadata={
                    "organization_id": str(invitation.organization_id),
                    "email": invitation.email,
                },
            ),
        )

        await db.commit()

    @staticmethod
    async def resend_invitation(
        db: AsyncSession,
        invitation_id: UUID,
        actor_user_id: UUID,
    ) -> OrganizationInvitation:

        invitation = await OrganizationInvitationService.get_invitation(
            db=db,
            invitation_id=invitation_id,
        )

        OrganizationInvitationService._validate_pending_status(
            invitation,
        )
        
        if OrganizationInvitationService._is_expired(
            invitation,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Invitation has expired. "
                    "Create a new invitation instead."
                ),
            )

        # Rotate the token so any previously shared invite link stops
        # working, and push expiry out another full window.
        invitation.invitation_token = OrganizationInvitationService._generate_token()
        invitation.expires_at = (
            OrganizationInvitationService._get_current_time()
            + timedelta(
                days=INVITATION_EXPIRY_DAYS,
            )
        )

        await db.flush()

        await AuditService.create_log(
            db=db,
            actor_user_id=actor_user_id,
            payload=AuditLogCreate(
                action=AuditAction.RESEND,
                resource=AuditResource.ORGANIZATION_INVITATION,
                resource_id=str(invitation.id),
                description="Organization invitation resent",
                audit_metadata={
                    "organization_id": str(invitation.organization_id),
                    "email": invitation.email,
                },
            ),
        )

        await db.commit()

        await db.refresh(
            invitation,
        )

        return invitation

    @staticmethod
    async def accept_invitation(
        db: AsyncSession,
        invitation_token: str,
        current_user: User,
    ) -> OrganizationMembership:
        """
        Assumes an already-authenticated user — either an existing user who
        logged in, or a new user who just registered with the invited
        email. This keeps the invitation module independent of the
        registration flow: it only checks that the authenticated account's
        email matches the invitation before handing off to
        OrganizationMembershipService, which stays the single source of
        truth for membership creation.
        """

        membership_repository = OrganizationMembershipRepository(db)

        invitation = await OrganizationInvitationService.get_invitation_by_token(
            db=db,
            invitation_token=invitation_token,
        )

        OrganizationInvitationService._validate_pending_status(
            invitation,
        )

        if OrganizationInvitationService._is_expired(invitation):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This invitation has expired.",
            )

        if current_user.email.lower() != invitation.email.lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This invitation was not issued to the current account.",
            )

        already_member = await membership_repository.membership_exists(
            organization_id=invitation.organization_id,
            user_id=current_user.id,
        )

        if already_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this organization.",
            )

        # Never construct OrganizationMembership manually here — all
        # membership business rules (primary/default flags, joined_at,
        # audit logging) already live in OrganizationMembershipService.
        membership = await OrganizationMembershipService.create_membership(
            db=db,
            data=OrganizationMembershipCreate(
                organization_id=invitation.organization_id,
                user_id=current_user.id,
                role=invitation.role,
                membership_status=MembershipStatus.ACTIVE,
                is_primary=False,
                is_default=False,
                is_active=True,
                notes=None,
            ),
            actor_user_id=current_user.id,
        )

        invitation.status = InvitationStatus.ACCEPTED
        invitation.accepted_at = OrganizationInvitationService._get_current_time()

        await db.flush()

        await AuditService.create_log(
            db=db,
            actor_user_id=current_user.id,
            payload=AuditLogCreate(
                action=AuditAction.ACCEPT,
                resource=AuditResource.ORGANIZATION_INVITATION,
                resource_id=str(invitation.id),
                description="Organization invitation accepted",
                audit_metadata={
                    "organization_id": str(invitation.organization_id),
                    "email": invitation.email,
                },
            ),
        )

        await db.commit()

        await db.refresh(
            invitation,
        )

        return membership

    @staticmethod
    async def decline_invitation(
        db: AsyncSession,
        invitation_token: str,
        actor_user_id: UUID | None = None,
    ) -> OrganizationInvitation:

        invitation = await OrganizationInvitationService.get_invitation_by_token(
            db=db,
            invitation_token=invitation_token,
        )

        OrganizationInvitationService._validate_pending_status(
            invitation,
        )

        invitation.status = InvitationStatus.DECLINED

        await db.flush()

        await AuditService.create_log(
            db=db,
            actor_user_id=actor_user_id,
            payload=AuditLogCreate(
                action=AuditAction.DECLINE,
                resource=AuditResource.ORGANIZATION_INVITATION,
                resource_id=str(invitation.id),
                description="Organization invitation declined",
                audit_metadata={
                    "organization_id": str(invitation.organization_id),
                    "email": invitation.email,
                },
            ),
        )

        await db.commit()

        await db.refresh(
            invitation,
        )

        return invitation

    @staticmethod
    async def cancel_invitation(
        db: AsyncSession,
        invitation_id: UUID,
        actor_user_id: UUID,
    ) -> OrganizationInvitation:

        invitation = await OrganizationInvitationService.get_invitation(
            db=db,
            invitation_id=invitation_id,
        )

        OrganizationInvitationService._validate_pending_status(
            invitation,
        )

        invitation.status = InvitationStatus.CANCELLED

        await db.flush()

        await AuditService.create_log(
            db=db,
            actor_user_id=actor_user_id,
            payload=AuditLogCreate(
                action=AuditAction.CANCEL,
                resource=AuditResource.ORGANIZATION_INVITATION,
                resource_id=str(invitation.id),
                description="Organization invitation cancelled",
                audit_metadata={
                    "organization_id": str(invitation.organization_id),
                    "email": invitation.email,
                },
            ),
        )

        await db.commit()

        await db.refresh(
            invitation,
        )

        return invitation

    @staticmethod
    def _generate_token() -> str:

        return secrets.token_urlsafe(
            INVITATION_TOKEN_BYTES,
        )

    @staticmethod
    def _get_current_time() -> datetime:

        return datetime.now(timezone.utc)

    @staticmethod
    def _validate_pending_status(
        invitation: OrganizationInvitation,
    ) -> None:

        if invitation.status != InvitationStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This invitation is no longer pending.",
            )

    @staticmethod
    def _is_expired(
        invitation: OrganizationInvitation,
    ) -> bool:

        return invitation.expires_at < OrganizationInvitationService._get_current_time()