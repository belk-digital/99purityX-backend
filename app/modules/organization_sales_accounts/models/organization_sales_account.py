from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
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

from app.modules.organization_sales_accounts.constants.organization_sales_account_status import (
    OrganizationSalesAccountStatus,
)
from app.modules.organization_sales_accounts.constants.organization_sales_account_type import (
    OrganizationSalesAccountType,
)

if TYPE_CHECKING:
    from app.modules.organizations.models.organization import Organization
    from app.modules.sales.models.sales_member import SalesMember
    from app.modules.sales.models.sales_organization import SalesOrganization


class OrganizationSalesAccount(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    """
    Represents the commercial relationship between a Healthcare Organization
    and the Sales domain.

    This entity owns commercial information only.

    It does NOT own:

    - Providers
    - Patients
    - Appointments
    - Memberships
    - Clinical workflows

    Future commercial modules such as Subscriptions, Contracts,
    Billing, Renewals and Customer Success will attach to this entity.
    """

    __tablename__ = "organization_sales_accounts"

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            name="uq_organization_sales_account",
        ),
    )

    # -------------------------------------------------------------------------
    # References
    # -------------------------------------------------------------------------

    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "organizations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    sales_organization_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "sales_organizations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    created_by_sales_member_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "sales_members.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    account_owner_sales_member_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "sales_members.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    # -------------------------------------------------------------------------
    # Commercial Information
    # -------------------------------------------------------------------------

    account_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
    )

    account_type: Mapped[OrganizationSalesAccountType] = mapped_column(
        Enum(
            OrganizationSalesAccountType,
            name="organization_sales_account_type",
        ),
        default=OrganizationSalesAccountType.DIRECT,
        nullable=False,
    )

    status: Mapped[OrganizationSalesAccountStatus] = mapped_column(
        Enum(
            OrganizationSalesAccountStatus,
            name="organization_sales_account_status",
        ),
        default=OrganizationSalesAccountStatus.ONBOARDING,
        nullable=False,
    )

    # -------------------------------------------------------------------------
    # Commercial Lifecycle
    # -------------------------------------------------------------------------

    customer_since: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    contract_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    contract_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    renewal_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # -------------------------------------------------------------------------
    # Additional Information
    # -------------------------------------------------------------------------

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # -------------------------------------------------------------------------
    # ORM Relationships
    # -------------------------------------------------------------------------

    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="sales_account",
    )

    sales_organization: Mapped["SalesOrganization"] = relationship(
        "SalesOrganization",
        back_populates="organization_sales_accounts",
    )

    created_by_sales_member: Mapped["SalesMember"] = relationship(
        "SalesMember",
        foreign_keys=[created_by_sales_member_id],
        back_populates="created_accounts",
    )

    account_owner_sales_member: Mapped["SalesMember"] = relationship(
        "SalesMember",
        foreign_keys=[account_owner_sales_member_id],
        back_populates="owned_accounts",
    )