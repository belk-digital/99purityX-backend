from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import get_db

from app.modules.auth.api.dependencies import (
    get_current_user,
)
from app.modules.auth.models.user import User

from app.modules.organization_sales_accounts.schemas.organization_sales_account_schema import (
    OrganizationSalesAccountCreateSchema,
    OrganizationSalesAccountUpdateSchema,
    OrganizationSalesAccountResponseSchema,
)
from app.modules.organization_sales_accounts.services.organization_sales_account_service import (
    OrganizationSalesAccountService,
)

router = APIRouter(
    prefix="/organization-sales-accounts",
    tags=["Organization Sales Accounts"],
)


# -----------------------------------------------------------------------------
# Create
# -----------------------------------------------------------------------------

@router.post(
    "",
    response_model=OrganizationSalesAccountResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_organization_sales_account(
    payload: OrganizationSalesAccountCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = OrganizationSalesAccountService(db)

    try:
        return await service.create_organization_sales_account(
            payload=payload,
            performed_by=current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


# -----------------------------------------------------------------------------
# Get All
# -----------------------------------------------------------------------------

@router.get(
    "",
    response_model=list[OrganizationSalesAccountResponseSchema],
)
async def get_organization_sales_accounts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = OrganizationSalesAccountService(db)

    return await service.get_all()


# -----------------------------------------------------------------------------
# Get By ID
# -----------------------------------------------------------------------------

@router.get(
    "/{account_id}",
    response_model=OrganizationSalesAccountResponseSchema,
)
async def get_organization_sales_account(
    account_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = OrganizationSalesAccountService(db)

    try:
        return await service.get_by_id(
            account_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


# -----------------------------------------------------------------------------
# Update
# -----------------------------------------------------------------------------

@router.put(
    "/{account_id}",
    response_model=OrganizationSalesAccountResponseSchema,
)
async def update_organization_sales_account(
    account_id: UUID,
    payload: OrganizationSalesAccountUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = OrganizationSalesAccountService(db)

    try:
        return await service.update_organization_sales_account(
            account_id=account_id,
            payload=payload,
            performed_by=current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


# -----------------------------------------------------------------------------
# Delete
# -----------------------------------------------------------------------------

@router.delete(
    "/{account_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_organization_sales_account(
    account_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = OrganizationSalesAccountService(db)

    try:
        await service.delete_organization_sales_account(
            account_id=account_id,
            performed_by=current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )