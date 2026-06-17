from decimal import Decimal
from uuid import UUID
import uuid

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean

from app.infrastructure.database.base import Base
from app.infrastructure.database.mixins import TimestampMixin, UUIDMixin
from app.modules.consultations.models.consultation_model import (
    Consultation,
)
from app.modules.labs.models.lab_order_model import LabOrder
from app.modules.optimization.models.optimization_program_model import (
    OptimizationProgram,
)
from app.modules.optimization.models.habit_protocol_model import HabitProtocol
from app.modules.optimization.models.peptide_protocol_model import (
    PeptideProtocol,
)
from app.modules.goals.models.health_goal_model import HealthGoal
from app.modules.analytics.models.provider_analytics_model import (
    ProviderAnalytics,
)
from app.modules.documents.models.document_model import Document


class Provider(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "providers"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
    )

    provider_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    speciality: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
        index=True,
    )

    license_number: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
        unique=True,
    )

    years_experience: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    bio: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    consultation_fee: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="provider_profile",
        lazy="selectin",
    )
    
    appointments = relationship(
        "Appointment",
        back_populates="provider",
        cascade="all, delete-orphan",
    )
    
    consultations: Mapped[list["Consultation"]] = relationship(
        "Consultation",
        back_populates="provider",
        lazy="selectin",
    )

    lab_orders: Mapped[list["LabOrder"]] = relationship(
        "LabOrder",
        back_populates="provider",
        lazy="selectin",
    )

    optimization_programs: Mapped[list["OptimizationProgram"]] = relationship(
        "OptimizationProgram",
        back_populates="provider",
        lazy="selectin",
    )

    habit_protocols: Mapped[list["HabitProtocol"]] = relationship(
        "HabitProtocol",
        back_populates="provider",
        lazy="selectin",
    )

    peptide_protocols: Mapped[list["PeptideProtocol"]] = relationship(
        "PeptideProtocol",
        back_populates="provider",
        lazy="selectin",
    )

    health_goals: Mapped[list["HealthGoal"]] = relationship(
        "HealthGoal",
        back_populates="provider",
        lazy="selectin",
    )

    analytics_snapshots: Mapped[list["ProviderAnalytics"]] = relationship(
        "ProviderAnalytics",
        back_populates="provider",
        lazy="selectin",
    )

    documents: Mapped[list["Document"]] = relationship(
        "Document",
        back_populates="provider",
        lazy="selectin",
    )
