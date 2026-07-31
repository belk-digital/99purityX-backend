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

from app.modules.sales.repositories.sales_team_repository import (
    SalesTeamRepository,
)
from app.modules.sales.schemas.sales_team_schema import (
    SalesTeamCreateSchema,
    SalesTeamResponseSchema,
    SalesTeamUpdateSchema,
)
from app.modules.sales.services.sales_team_service import (
    SalesTeamService,
)

router = APIRouter(
    prefix="/sales-teams",
    tags=["Sales Teams"],
)


@router.post(
    "",
    response_model=SalesTeamResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_sales_team(
    payload: SalesTeamCreateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    service = SalesTeamService()

    return await service.create_sales_team(
        db=db,
        data=payload,
        actor_user_id=current_user.id,
    )


@router.get(
    "",
    response_model=list[SalesTeamResponseSchema],
)
async def get_sales_teams(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    repository = SalesTeamRepository(db)

    return await repository.get_all()


@router.get(
    "/organization/{sales_organization_id}",
    response_model=list[SalesTeamResponseSchema],
)
async def get_sales_teams_by_organization(
    sales_organization_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    repository = SalesTeamRepository(db)

    return await repository.get_by_sales_organization(
        sales_organization_id,
    )


@router.get(
    "/{sales_team_id}",
    response_model=SalesTeamResponseSchema,
)
async def get_sales_team(
    sales_team_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    service = SalesTeamService()

    return await service.get_sales_team(
        db=db,
        sales_team_id=sales_team_id,
    )


@router.put(
    "/{sales_team_id}",
    response_model=SalesTeamResponseSchema,
)
async def update_sales_team(
    sales_team_id: UUID,
    payload: SalesTeamUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    service = SalesTeamService()

    sales_team = await service.get_sales_team(
        db=db,
        sales_team_id=sales_team_id,
    )

    updated_sales_team = (
        await service.update_sales_team(
            db=db,
            sales_team=sales_team,
            data=payload,
            actor_user_id=current_user.id,
        )
    )

    return updated_sales_team


@router.delete(
    "/{sales_team_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_sales_team(
    sales_team_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    service = SalesTeamService()

    sales_team = await service.get_sales_team(
        db=db,
        sales_team_id=sales_team_id,
    )

    await service.delete_sales_team(
        db=db,
        sales_team=sales_team,
        actor_user_id=current_user.id,
    )

    return None