from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import (
    get_db,
)
from app.modules.auth.api.dependencies import (
    get_current_user,
)
from app.modules.auth.models.user import User
from app.modules.organization_invitations.repositories.organization_invitation_repository import (
    OrganizationInvitationRepository,
)
from app.modules.organization_invitations.schemas.organization_invitation_schema import (
    OrganizationInvitationCreate,
    OrganizationInvitationResponse,
    OrganizationInvitationUpdate,
)
from app.modules.organization_invitations.services.organization_invitation_service import (
    OrganizationInvitationService,
)
from app.modules.organization_memberships.schemas.organization_membership_schema import (
    OrganizationMembershipResponse,
)
from app.modules.organizations.api.dependencies import (
    validate_admin_access,
)

router = APIRouter(
    prefix="/organization-invitations",
    tags=["Organization Invitations"],
)



@router.post(
    "",
    response_model=OrganizationInvitationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_invitation(
    payload: OrganizationInvitationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    service = OrganizationInvitationService()

    return await service.create_invitation(
        db=db,
        data=payload,
        invited_by=current_user.id,
    )


@router.get(
    "",
    response_model=list[OrganizationInvitationResponse],
)
async def get_invitations(
    organization_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    service = OrganizationInvitationService()

    return await service.list_invitations_by_organization(
        db=db,
        organization_id=organization_id,
    )


@router.get(
    "/{invitation_id}",
    response_model=OrganizationInvitationResponse,
)
async def get_invitation(
    invitation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    service = OrganizationInvitationService()

    return await service.get_invitation(
        db=db,
        invitation_id=invitation_id,
    )


@router.put(
    "/{invitation_id}",
    response_model=OrganizationInvitationResponse,
)
async def update_invitation(
    invitation_id: UUID,
    payload: OrganizationInvitationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    service = OrganizationInvitationService()

    invitation = await service.get_invitation(
        db=db,
        invitation_id=invitation_id,
    )

    return await service.update_invitation(
        db=db,
        invitation=invitation,
        data=payload,
        actor_user_id=current_user.id,
    )


@router.delete(
    "/{invitation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_invitation(
    invitation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    service = OrganizationInvitationService()

    invitation = await service.get_invitation(
        db=db,
        invitation_id=invitation_id,
    )

    await service.delete_invitation(
        db=db,
        invitation=invitation,
        actor_user_id=current_user.id,
    )

    return None


@router.post(
    "/{invitation_id}/resend",
    response_model=OrganizationInvitationResponse,
)
async def resend_invitation(
    invitation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    service = OrganizationInvitationService()

    return await service.resend_invitation(
        db=db,
        invitation_id=invitation_id,
        actor_user_id=current_user.id,
    )


@router.post(
    "/{invitation_id}/cancel",
    response_model=OrganizationInvitationResponse,
)
async def cancel_invitation(
    invitation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    service = OrganizationInvitationService()

    return await service.cancel_invitation(
        db=db,
        invitation_id=invitation_id,
        actor_user_id=current_user.id,
    )


@router.post(
    "/accept/{invitation_token}",
    response_model=OrganizationMembershipResponse,
)
async def accept_invitation(
    invitation_token: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    service = OrganizationInvitationService()

    return await service.accept_invitation(
        db=db,
        invitation_token=invitation_token,
        current_user=current_user,
    )


@router.post(
    "/decline/{invitation_token}",
    response_model=OrganizationInvitationResponse,
)
async def decline_invitation(
    invitation_token: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    service = OrganizationInvitationService()

    return await service.decline_invitation(
        db=db,
        invitation_token=invitation_token,
        actor_user_id=current_user.id,
    )