from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Enum,
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

from app.modules.organizations.constants.organization_status import (
    OrganizationStatus,
)
from app.modules.organizations.constants.organization_type import (
    OrganizationType,
)
from app.modules.organization_sales_accounts.models.organization_sales_account import (
    OrganizationSalesAccount,
)

if TYPE_CHECKING:
    from app.modules.organization_memberships.models.organization_membership import (
        OrganizationMembership,
    )
    from app.modules.organization_invitations.models.organization_invitation import (
        OrganizationInvitation,
    )


class Organization(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    """
    Represents a tenant within the Telehealth platform.

    An Organization can represent:

    - Clinic
    - Hospital
    - Independent Practice
    - Wellness Center
    - Medical Spa
    - Corporate Healthcare
    - Enterprise Healthcare Network

    Relationships to users, providers and patients will be introduced
    through OrganizationMembership in future phases.
    """

    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    slug: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    organization_type: Mapped[OrganizationType] = mapped_column(
        Enum(
            OrganizationType,
            name="organization_type",
        ),
        nullable=False,
    )

    status: Mapped[OrganizationStatus] = mapped_column(
        Enum(
            OrganizationStatus,
            name="organization_status",
        ),
        default=OrganizationStatus.PENDING,
        nullable=False,
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    website: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    timezone: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    logo_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    primary_color: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    secondary_color: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    tax_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    
    memberships: Mapped[list["OrganizationMembership"]] = relationship(
        "OrganizationMembership",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    
    organization_invitations: Mapped[list["OrganizationInvitation"]] = relationship(
        "OrganizationInvitation",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    
    sales_account: Mapped["OrganizationSalesAccount"] = relationship(
        "OrganizationSalesAccount",
        back_populates="organization",
        uselist=False,
        cascade="all, delete-orphan",
    )