from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.modules.organization_sales_accounts.constants.organization_sales_account_status import (
    OrganizationSalesAccountStatus,
)
from app.modules.organization_sales_accounts.constants.organization_sales_account_type import (
    OrganizationSalesAccountType,
)


class OrganizationSalesAccountBaseSchema(BaseModel):
    """
    Base schema shared across create, update and response models.
    """

    account_type: OrganizationSalesAccountType = (
        OrganizationSalesAccountType.DIRECT
    )

    status: OrganizationSalesAccountStatus = (
        OrganizationSalesAccountStatus.ONBOARDING
    )

    customer_since: datetime

    contract_start: datetime | None = None

    contract_end: datetime | None = None

    renewal_date: datetime | None = None

    notes: str | None = None

    is_active: bool = True


class OrganizationSalesAccountCreateSchema(
    OrganizationSalesAccountBaseSchema,
):
    """
    Schema used when creating a commercial account.
    """

    organization_id: UUID

    sales_organization_id: UUID

    created_by_sales_member_id: UUID

    account_owner_sales_member_id: UUID


class OrganizationSalesAccountUpdateSchema(BaseModel):
    """
    Schema used for partial updates.
    """

    account_owner_sales_member_id: UUID | None = None

    account_type: OrganizationSalesAccountType | None = None

    status: OrganizationSalesAccountStatus | None = None

    contract_start: datetime | None = None

    contract_end: datetime | None = None

    renewal_date: datetime | None = None

    notes: str | None = None

    is_active: bool | None = None


class OrganizationSalesAccountResponseSchema(
    OrganizationSalesAccountBaseSchema,
):
    """
    Schema returned to API consumers.
    """

    id: UUID

    account_number: str

    organization_id: UUID

    sales_organization_id: UUID

    created_by_sales_member_id: UUID

    account_owner_sales_member_id: UUID

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )