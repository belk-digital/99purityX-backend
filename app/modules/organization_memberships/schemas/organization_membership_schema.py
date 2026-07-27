from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.organization_memberships.constants.membership_enums import (
    MembershipStatus,
    OrganizationRole,
)


class OrganizationMembershipCreate(BaseModel):
    organization_id: UUID
    user_id: UUID

    role: OrganizationRole = OrganizationRole.PROVIDER

    membership_status: MembershipStatus = MembershipStatus.PENDING

    is_primary: bool = False
    is_default: bool = False
    is_active: bool = True

    notes: Optional[str] = Field(
        default=None,
        max_length=1000,
    )

class OrganizationMembershipUpdate(BaseModel):
    role: Optional[OrganizationRole] = None

    membership_status: Optional[MembershipStatus] = None

    is_primary: Optional[bool] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None

    notes: Optional[str] = Field(
        default=None,
        max_length=1000,
    )


class OrganizationMembershipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID

    organization_id: UUID
    user_id: UUID

    role: OrganizationRole

    membership_status: MembershipStatus

    is_primary: bool
    is_default: bool
    is_active: bool

    joined_at: Optional[datetime]

    notes: Optional[str]

    created_at: datetime
    updated_at: datetime

class OrganizationMembershipListResponse(BaseModel):
    items: list[OrganizationMembershipResponse]
    total: int