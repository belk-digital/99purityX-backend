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
from app.modules.organizations.repositories.organization_repository import (
    OrganizationRepository,
)
from app.modules.organizations.schemas.organization_schema import (
    OrganizationCreateSchema,
    OrganizationResponseSchema,
    OrganizationUpdateSchema,
)
from app.modules.organizations.services.organization_service import (
    OrganizationService,
)
from app.modules.organizations.api.dependencies import (
    validate_admin_access,
)

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)


@router.post(
    "",
    response_model=OrganizationResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_organization(
    payload: OrganizationCreateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    service = OrganizationService()

    return await service.create_organization(
        db=db,
        data=payload,
        actor_user_id=current_user.id,
    )


@router.get(
    "",
    response_model=list[OrganizationResponseSchema],
)
async def get_organizations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    repository = OrganizationRepository(db)

    return await repository.get_all()


@router.get(
    "/{organization_id}",
    response_model=OrganizationResponseSchema,
)
async def get_organization(
    organization_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    service = OrganizationService()

    return await service.get_organization(
        db=db,
        organization_id=organization_id,
    )


@router.put(
    "/{organization_id}",
    response_model=OrganizationResponseSchema,
)
async def update_organization(
    organization_id: UUID,
    payload: OrganizationUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    service = OrganizationService()

    organization = await service.get_organization(
        db=db,
        organization_id=organization_id,
    )

    updated_organization = (
        await service.update_organization(
            db=db,
            organization=organization,
            data=payload,
            actor_user_id=current_user.id,
        )
    )

    return updated_organization


@router.delete(
    "/{organization_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_organization(
    organization_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    service = OrganizationService()

    organization = await service.get_organization(
        db=db,
        organization_id=organization_id,
    )

    await service.delete_organization(
        db=db,
        organization=organization,
        actor_user_id=current_user.id,
    )

    return None