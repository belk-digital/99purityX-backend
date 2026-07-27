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
from app.modules.organization_memberships.repositories.organization_membership_repository import (
    OrganizationMembershipRepository,
)
from app.modules.organization_memberships.schemas.organization_membership_schema import (
    OrganizationMembershipCreate,
    OrganizationMembershipResponse,
    OrganizationMembershipUpdate,
)
from app.modules.organizations.api.dependencies import (
    validate_admin_access,
)
from app.modules.organization_memberships.services.organization_membership_service import (
    OrganizationMembershipService,
)

router = APIRouter(
    prefix="/organization-memberships",
    tags=["Organization Memberships"],
)


@router.post(
    "",
    response_model=OrganizationMembershipResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_membership(
    payload: OrganizationMembershipCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    service = OrganizationMembershipService()

    return await service.create_membership(
        db=db,
        data=payload,
        actor_user_id=current_user.id,
    )


@router.get(
    "",
    response_model=list[OrganizationMembershipResponse],
)
async def get_memberships(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    repository = OrganizationMembershipRepository(db)

    return await repository.get_all()


@router.get(
    "/{membership_id}",
    response_model=OrganizationMembershipResponse,
)
async def get_membership(
    membership_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    service = OrganizationMembershipService()

    return await service.get_membership(
        db=db,
        membership_id=membership_id,
    )


@router.put(
    "/{membership_id}",
    response_model=OrganizationMembershipResponse,
)
async def update_membership(
    membership_id: UUID,
    payload: OrganizationMembershipUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    service = OrganizationMembershipService()

    membership = await service.get_membership(
        db=db,
        membership_id=membership_id,
    )

    updated_membership = await service.update_membership(
        db=db,
        membership=membership,
        data=payload,
        actor_user_id=current_user.id,
    )

    return updated_membership


@router.delete(
    "/{membership_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_membership(
    membership_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    service = OrganizationMembershipService()

    membership = await service.get_membership(
        db=db,
        membership_id=membership_id,
    )

    await service.delete_membership(
        db=db,
        membership=membership,
        actor_user_id=current_user.id,
    )

    return None