from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.modules.sales.constants.sales_member_enums import (
    SalesMemberRole,
    SalesMemberStatus,
)


class SalesMemberBaseSchema(BaseModel):
    """
    Base schema shared across create, update and response models.
    """

    role: SalesMemberRole

    sales_team_id: UUID | None = None

    territory_id: UUID | None = None

    joined_at: datetime | None = None

    is_primary: bool = False

    is_active: bool = True


class SalesMemberCreateSchema(SalesMemberBaseSchema):
    """
    Schema used when creating a Sales Member.
    """

    user_id: UUID

    sales_organization_id: UUID


class SalesMemberUpdateSchema(BaseModel):
    """
    Schema used for partial updates.
    """

    role: SalesMemberRole | None = None

    sales_team_id: UUID

    territory_id: UUID
    
    joined_at: datetime | None = None

    status: SalesMemberStatus | None = None

    is_primary: bool | None = None

    is_active: bool | None = None


class SalesMemberResponseSchema(SalesMemberBaseSchema):
    """
    Schema returned to API consumers.
    """

    id: UUID

    user_id: UUID

    sales_organization_id: UUID

    status: SalesMemberStatus

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )