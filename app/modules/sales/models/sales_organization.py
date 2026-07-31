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

from app.modules.sales.constants.sales_organization_enums import (
    SalesOrganizationStatus,
)

if TYPE_CHECKING:
    from app.modules.sales.models.sales_team import (
        SalesTeam,
    )
    from app.modules.sales.models.territory import (
        Territory,
    )
    # from app.modules.sales.models.sales_member import (
    #     SalesMember,
    # )


class SalesOrganization(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    """
    Represents a commercial Sales Organization operating under
    the Telehealth platform.

    A Sales Organization is responsible for:

    - Customer acquisition
    - Sales operations
    - Team management
    - Territory management
    - Customer onboarding

    It does NOT contain any clinical data.

    Clinical data belongs exclusively to Healthcare Organizations.
    """

    __tablename__ = "sales_organizations"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    slug: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    status: Mapped[SalesOrganizationStatus] = mapped_column(
        Enum(
            SalesOrganizationStatus,
            name="sales_organization_status",
        ),
        default=SalesOrganizationStatus.ACTIVE,
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

    country: Mapped[str | None] = mapped_column(
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

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    
    # ------------------------------------------------------------------
    # Future Relationships
    # ------------------------------------------------------------------
    # These relationships will be enabled in later phases:
    #
    # Phase 4.2 -> SalesTeam
    # Phase 4.3 -> Territory
    # Phase 4.4 -> SalesMember
    #
    # Uncomment once the corresponding models are implemented.

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    sales_teams: Mapped[list["SalesTeam"]] = relationship(
        "SalesTeam",
        back_populates="sales_organization",
        cascade="all, delete-orphan",
    )

    territories: Mapped[list["Territory"]] = relationship(
        "Territory",
        back_populates="sales_organization",
        cascade="all, delete-orphan",
    )

    # sales_members: Mapped[list["SalesMember"]] = relationship(
    #     "SalesMember",
    #     back_populates="sales_organization",
    #     cascade="all, delete-orphan",
    # )