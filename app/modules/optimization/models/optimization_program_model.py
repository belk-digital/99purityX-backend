from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base
from app.infrastructure.database.mixins import TimestampMixin, UUIDMixin
from app.modules.optimization.enums.program_enums import (
    OptimizationProgramStatus,
)

if TYPE_CHECKING:
    from app.modules.analytics.models.program_analytics_model import (
        ProgramAnalytics,
    )
    from app.modules.consultations.models.consultation_model import Consultation
    from app.modules.documents.models.document_model import Document
    from app.modules.goals.models.health_goal_model import HealthGoal
    from app.modules.optimization.models.habit_protocol_model import (
        HabitProtocol,
    )
    from app.modules.optimization.models.peptide_protocol_model import (
        PeptideProtocol,
    )
    from app.modules.patients.models.patient_model import Patient
    from app.modules.providers.models.provider_model import Provider


class OptimizationProgram(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "optimization_programs"

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

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    goal: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[OptimizationProgramStatus] = mapped_column(
        Enum(OptimizationProgramStatus),
        default=OptimizationProgramStatus.DRAFT,
        nullable=False,
        index=True,
    )

    start_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    end_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    patient: Mapped["Patient"] = relationship(
        "Patient",
        back_populates="optimization_programs",
        lazy="selectin",
    )

    provider: Mapped["Provider"] = relationship(
        "Provider",
        back_populates="optimization_programs",
        lazy="selectin",
    )

    consultation: Mapped["Consultation"] = relationship(
        "Consultation",
        back_populates="optimization_programs",
        lazy="selectin",
    )

    habit_protocols: Mapped[list["HabitProtocol"]] = relationship(
        "HabitProtocol",
        back_populates="program",
        lazy="selectin",
    )

    peptide_protocols: Mapped[list["PeptideProtocol"]] = relationship(
        "PeptideProtocol",
        back_populates="program",
        lazy="selectin",
    )

    health_goals: Mapped[list["HealthGoal"]] = relationship(
        "HealthGoal",
        back_populates="program",
        lazy="selectin",
    )

    analytics_snapshots: Mapped[list["ProgramAnalytics"]] = relationship(
        "ProgramAnalytics",
        back_populates="program",
        lazy="selectin",
    )

    documents: Mapped[list["Document"]] = relationship(
        "Document",
        back_populates="optimization_program",
        lazy="selectin",
    )
