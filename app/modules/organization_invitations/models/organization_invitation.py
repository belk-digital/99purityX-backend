from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.infrastructure.database.base import Base
from app.infrastructure.database.mixins import (
    TimestampMixin,
    UUIDMixin,
)
from app.modules.organization_invitations.constants.invitation_enums import (
    InvitationSource,
    InvitationStatus,
)
from app.modules.organization_memberships.constants.membership_enums import (
    OrganizationRole,
)

if TYPE_CHECKING:
    from app.modules.auth.models.user import User
    from app.modules.organizations.models.organization import Organization


class OrganizationInvitation(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = "organization_invitations"

    organization_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    role: Mapped[OrganizationRole] = mapped_column(
        Enum(
            OrganizationRole,
        ),
        nullable=False,
    )

    status: Mapped[InvitationStatus] = mapped_column(
        Enum(
            InvitationStatus,
        ),
        default=InvitationStatus.PENDING,
        nullable=False,
    )

    invitation_source: Mapped[InvitationSource] = mapped_column(
        Enum(
            InvitationSource,
        ),
        nullable=False,
    )

    invitation_token: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    accepted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    invited_by: Mapped[str] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="organization_invitations",
    )

    inviter: Mapped["User"] = relationship(
        "User",
        foreign_keys=[invited_by],
    )