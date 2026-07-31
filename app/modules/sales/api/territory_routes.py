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

from app.modules.organizations.api.dependencies import (
    validate_admin_access,
)

from app.modules.sales.repositories.territory_repository import (
    TerritoryRepository,
)
from app.modules.sales.schemas.territory_schema import (
    TerritoryCreateSchema,
    TerritoryResponseSchema,
    TerritoryUpdateSchema,
)
from app.modules.sales.services.territory_service import (
    TerritoryService,
)

router = APIRouter(
    prefix="/territories",
    tags=["Territories"],
)


@router.post(
    "",
    response_model=TerritoryResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_territory(
    payload: TerritoryCreateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    service = TerritoryService()

    return await service.create_territory(
        db=db,
        data=payload,
        actor_user_id=current_user.id,
    )


@router.get(
    "",
    response_model=list[TerritoryResponseSchema],
)
async def get_territories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    repository = TerritoryRepository(db)

    return await repository.get_all()


@router.get(
    "/sales-organization/{sales_organization_id}",
    response_model=list[TerritoryResponseSchema],
)
async def get_territories_by_sales_organization(
    sales_organization_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    repository = TerritoryRepository(db)

    return await repository.get_all_by_sales_organization(
        sales_organization_id,
    )


@router.get(
    "/{territory_id}",
    response_model=TerritoryResponseSchema,
)
async def get_territory(
    territory_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    service = TerritoryService()

    return await service.get_territory(
        db=db,
        territory_id=territory_id,
    )


@router.put(
    "/{territory_id}",
    response_model=TerritoryResponseSchema,
)
async def update_territory(
    territory_id: UUID,
    payload: TerritoryUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    service = TerritoryService()

    territory = await service.get_territory(
        db=db,
        territory_id=territory_id,
    )

    updated_territory = await service.update_territory(
        db=db,
        territory=territory,
        data=payload,
        actor_user_id=current_user.id,
    )

    return updated_territory


@router.delete(
    "/{territory_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_territory(
    territory_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    service = TerritoryService()

    territory = await service.get_territory(
        db=db,
        territory_id=territory_id,
    )

    await service.delete_territory(
        db=db,
        territory=territory,
        actor_user_id=current_user.id,
    )

    return None