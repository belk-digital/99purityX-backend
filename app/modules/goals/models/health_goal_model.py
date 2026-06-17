from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base
from app.infrastructure.database.mixins import TimestampMixin, UUIDMixin
from app.modules.goals.enums.goal_enums import (
    GoalCategory,
    HealthGoalStatus,
)

if TYPE_CHECKING:
    from app.modules.consultations.models.consultation_model import Consultation
    from app.modules.goals.models.goal_progress_model import GoalProgress
    from app.modules.optimization.models.optimization_program_model import (
        OptimizationProgram,
    )
    from app.modules.patients.models.patient_model import Patient
    from app.modules.providers.models.provider_model import Provider


class HealthGoal(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "health_goals"

    patient_id: Mapped[str] = mapped_column(
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    provider_id: Mapped[str] = mapped_column(
        ForeignKey("providers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    consultation_id: Mapped[str] = mapped_column(
        ForeignKey("consultations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    program_id: Mapped[str] = mapped_column(
        ForeignKey("optimization_programs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    category: Mapped[GoalCategory] = mapped_column(
        Enum(GoalCategory),
        nullable=False,
        index=True,
    )

    target_value: Mapped[Decimal] = mapped_column(
        Numeric(12, 4),
        nullable=False,
    )

    current_value: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 4),
        nullable=True,
    )

    unit: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    start_value: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 4),
        nullable=True,
    )

    target_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    status: Mapped[HealthGoalStatus] = mapped_column(
        Enum(HealthGoalStatus),
        default=HealthGoalStatus.ACTIVE,
        nullable=False,
        index=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    patient: Mapped["Patient"] = relationship(
        "Patient",
        back_populates="health_goals",
        lazy="selectin",
    )

    provider: Mapped["Provider"] = relationship(
        "Provider",
        back_populates="health_goals",
        lazy="selectin",
    )

    consultation: Mapped["Consultation"] = relationship(
        "Consultation",
        back_populates="health_goals",
        lazy="selectin",
    )

    program: Mapped["OptimizationProgram"] = relationship(
        "OptimizationProgram",
        back_populates="health_goals",
        lazy="selectin",
    )

    progress_records: Mapped[list["GoalProgress"]] = relationship(
        "GoalProgress",
        back_populates="goal",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
