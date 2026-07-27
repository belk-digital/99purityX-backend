from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
)

from app.modules.organization_invitations.constants.invitation_enums import (
    InvitationSource,
    InvitationSource,
    InvitationStatus,
)
from app.modules.organization_memberships.constants.membership_enums import (
    OrganizationRole,
)


class OrganizationInvitationCreate(BaseModel):

    organization_id: UUID
    email: EmailStr
    role: OrganizationRole
    message: str | None = None


class OrganizationInvitationUpdate(BaseModel):
    """
    Invitations follow a state-machine workflow.

    Role changes are intentionally not allowed through updates.
    To change a role, cancel the existing invitation and create a new one.
    This preserves a complete audit history.
    """

    message: str | None = None
    expires_at: datetime | None = None


class OrganizationInvitationResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID

    email: EmailStr

    role: OrganizationRole
    status: InvitationStatus
    invitation_source: InvitationSource

    expires_at: datetime
    accepted_at: datetime | None

    message: str | None

    invited_by: UUID

    created_at: datetime
    updated_at: datetime

class OrganizationInvitationListResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    items: list[OrganizationInvitationResponse]
    total: int