from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
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

from app.modules.sales.repositories.sales_organization_repository import (
    SalesOrganizationRepository,
)
from app.modules.sales.schemas.sales_organization_schema import (
    SalesOrganizationCreateSchema,
    SalesOrganizationResponseSchema,
    SalesOrganizationUpdateSchema,
)
from app.modules.sales.services.sales_organization_service import (
    SalesOrganizationService,
)

from app.modules.organizations.api.dependencies import (
    validate_admin_access,
)

router = APIRouter(
    prefix="/sales-organizations",
    tags=["Sales Organizations"],
)


@router.post(
    "",
    response_model=SalesOrganizationResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_sales_organization(
    payload: SalesOrganizationCreateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    service = SalesOrganizationService()

    return await service.create_sales_organization(
        db=db,
        data=payload,
        actor_user_id=current_user.id,
    )


@router.get(
    "",
    response_model=list[SalesOrganizationResponseSchema],
)
async def get_sales_organizations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    repository = SalesOrganizationRepository(db)

    return await repository.get_all()


@router.get(
    "/{sales_organization_id}",
    response_model=SalesOrganizationResponseSchema,
)
async def get_sales_organization(
    sales_organization_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    service = SalesOrganizationService()

    return await service.get_sales_organization(
        db=db,
        sales_organization_id=sales_organization_id,
    )


@router.put(
    "/{sales_organization_id}",
    response_model=SalesOrganizationResponseSchema,
)
async def update_sales_organization(
    sales_organization_id: UUID,
    payload: SalesOrganizationUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    service = SalesOrganizationService()

    sales_organization = await service.get_sales_organization(
        db=db,
        sales_organization_id=sales_organization_id,
    )

    updated_sales_organization = (
        await service.update_sales_organization(
            db=db,
            sales_organization=sales_organization,
            data=payload,
            actor_user_id=current_user.id,
        )
    )

    return updated_sales_organization


@router.delete(
    "/{sales_organization_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_sales_organization(
    sales_organization_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    service = SalesOrganizationService()

    sales_organization = await service.get_sales_organization(
        db=db,
        sales_organization_id=sales_organization_id,
    )

    await service.delete_sales_organization(
        db=db,
        sales_organization=sales_organization,
        actor_user_id=current_user.id,
    )

    return None