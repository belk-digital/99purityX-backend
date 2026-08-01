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

from app.modules.sales.repositories.sales_member_repository import (
    SalesMemberRepository,
)
from app.modules.sales.schemas.sales_member_schema import (
    SalesMemberCreateSchema,
    SalesMemberResponseSchema,
    SalesMemberUpdateSchema,
)
from app.modules.sales.services.sales_member_service import (
    SalesMemberService,
)

router = APIRouter(
    prefix="/sales-members",
    tags=["Sales Members"],
)


@router.post(
    "",
    response_model=SalesMemberResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_sales_member(
    payload: SalesMemberCreateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    service = SalesMemberService()

    return await service.create_sales_member(
        db=db,
        data=payload,
        actor_user_id=current_user.id,
    )


@router.get(
    "",
    response_model=list[SalesMemberResponseSchema],
)
async def get_sales_members(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    repository = SalesMemberRepository(db)

    return await repository.get_all()


@router.get(
    "/sales-organization/{sales_organization_id}",
    response_model=list[SalesMemberResponseSchema],
)
async def get_sales_members_by_sales_organization(
    sales_organization_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    repository = SalesMemberRepository(db)

    return await repository.get_all_by_sales_organization(
        sales_organization_id,
    )


@router.get(
    "/{sales_member_id}",
    response_model=SalesMemberResponseSchema,
)
async def get_sales_member(
    sales_member_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    service = SalesMemberService()

    return await service.get_sales_member(
        db=db,
        sales_member_id=sales_member_id,
    )


@router.put(
    "/{sales_member_id}",
    response_model=SalesMemberResponseSchema,
)
async def update_sales_member(
    sales_member_id: UUID,
    payload: SalesMemberUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    service = SalesMemberService()

    sales_member = await service.get_sales_member(
        db=db,
        sales_member_id=sales_member_id,
    )

    updated_sales_member = await service.update_sales_member(
        db=db,
        sales_member=sales_member,
        data=payload,
        actor_user_id=current_user.id,
    )

    return updated_sales_member


@router.delete(
    "/{sales_member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_sales_member(
    sales_member_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    validate_admin_access(current_user)

    service = SalesMemberService()

    sales_member = await service.get_sales_member(
        db=db,
        sales_member_id=sales_member_id,
    )

    await service.delete_sales_member(
        db=db,
        sales_member=sales_member,
        actor_user_id=current_user.id,
    )

    return None