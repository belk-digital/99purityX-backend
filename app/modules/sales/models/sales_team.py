from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
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

from app.modules.sales.constants.sales_team_enums import (
    SalesTeamStatus,
)

if TYPE_CHECKING:
    from app.modules.sales.models.sales_organization import (
        SalesOrganization,
    )
    from app.modules.sales.models.sales_member import (
        SalesMember,
    )


class SalesTeam(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    """
    Represents a functional Sales Team within a Sales Organization.

    Examples:
    - Enterprise Sales
    - Clinic Sales
    - Hospital Sales
    - Wellness Sales
    - Customer Success
    """

    __tablename__ = "sales_teams"

    __table_args__ = (
        UniqueConstraint(
            "sales_organization_id",
            "team_code",
            name="uq_sales_team_code_per_organization",
        ),
        UniqueConstraint(
            "sales_organization_id",
            "name",
            name="uq_sales_team_name_per_organization",
        ),
    )

    # -------------------------------------------------------------------------
    # Relationships
    # -------------------------------------------------------------------------

    sales_organization_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "sales_organizations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # -------------------------------------------------------------------------
    # Team Information
    # -------------------------------------------------------------------------

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    team_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # -------------------------------------------------------------------------
    # Status
    # -------------------------------------------------------------------------

    status: Mapped[SalesTeamStatus] = mapped_column(
        Enum(
            SalesTeamStatus,
            name="sales_team_status",
        ),
        default=SalesTeamStatus.ACTIVE,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # -------------------------------------------------------------------------
    # ORM Relationships
    # -------------------------------------------------------------------------

    sales_organization: Mapped["SalesOrganization"] = relationship(
        "SalesOrganization",
        back_populates="sales_teams",
    )

    sales_members: Mapped[list["SalesMember"]] = relationship(
        "SalesMember",
        back_populates="sales_team",
        cascade="all, delete-orphan",
    )