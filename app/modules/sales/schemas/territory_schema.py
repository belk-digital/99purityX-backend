from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.modules.sales.constants.territory_enums import (
    TerritoryLevel,
    TerritoryStatus,
)


class TerritoryBaseSchema(BaseModel):
    """
    Base schema shared across create, update and response models.
    """

    name: str

    code: str

    level: TerritoryLevel

    country: str | None = None

    state: str | None = None

    city: str | None = None

    description: str | None = None

    is_active: bool = True


class TerritoryCreateSchema(TerritoryBaseSchema):
    """
    Schema used when creating a Territory.
    """

    sales_organization_id: UUID

    parent_territory_id: UUID | None = None


class TerritoryUpdateSchema(BaseModel):
    """
    Schema used for partial updates.
    """

    name: str | None = None

    code: str | None = None

    level: TerritoryLevel | None = None

    country: str | None = None

    state: str | None = None

    city: str | None = None

    description: str | None = None

    parent_territory_id: UUID | None = None

    status: TerritoryStatus | None = None

    is_active: bool | None = None


class TerritoryResponseSchema(TerritoryBaseSchema):
    """
    Schema returned to API consumers.
    """

    id: UUID

    sales_organization_id: UUID

    parent_territory_id: UUID | None

    status: TerritoryStatus

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )