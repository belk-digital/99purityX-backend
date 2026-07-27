from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base
from app.infrastructure.database.mixins import (
    TimestampMixin,
    UUIDMixin,
)
from app.modules.organization_memberships.constants.membership_enums import (
    MembershipStatus,
    OrganizationRole,
)


class OrganizationMembership(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = "organization_memberships"

    # -------------------------------------------------------------------------
    # Relationships
    # -------------------------------------------------------------------------

    organization_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # -------------------------------------------------------------------------
    # Organization Role
    # -------------------------------------------------------------------------

    role: Mapped[OrganizationRole] = mapped_column(
        Enum(OrganizationRole),
        nullable=False,
    )

    # -------------------------------------------------------------------------
    # Membership State
    # -------------------------------------------------------------------------

    membership_status: Mapped[MembershipStatus] = mapped_column(
        Enum(MembershipStatus),
        default=MembershipStatus.PENDING,
        nullable=False,
    )

    # -------------------------------------------------------------------------
    # Membership Flags
    # -------------------------------------------------------------------------

    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # -------------------------------------------------------------------------
    # Membership Timeline
    # -------------------------------------------------------------------------

    joined_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


    # -------------------------------------------------------------------------
    # Additional Notes
    # -------------------------------------------------------------------------

    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # -------------------------------------------------------------------------
    # ORM Relationships
    # -------------------------------------------------------------------------

    organization = relationship(
        "Organization",
        back_populates="memberships",
    )

    user = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="organization_memberships",
    )
