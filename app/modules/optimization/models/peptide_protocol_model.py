from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base
from app.infrastructure.database.mixins import TimestampMixin, UUIDMixin
from app.modules.optimization.enums.program_enums import (
    PeptideProtocolStatus,
    PeptideRoute,
)

if TYPE_CHECKING:
    from app.modules.optimization.models.optimization_program_model import (
        OptimizationProgram,
    )
    from app.modules.patients.models.patient_model import Patient
    from app.modules.providers.models.provider_model import Provider


class PeptideProtocol(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "peptide_protocols"

    program_id: Mapped[str] = mapped_column(
        ForeignKey("optimization_programs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

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

    peptide_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    purpose: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    dosage: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    frequency: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    route: Mapped[PeptideRoute] = mapped_column(
        Enum(PeptideRoute),
        nullable=False,
        index=True,
    )

    status: Mapped[PeptideProtocolStatus] = mapped_column(
        Enum(PeptideProtocolStatus),
        default=PeptideProtocolStatus.PLANNED,
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

    program: Mapped["OptimizationProgram"] = relationship(
        "OptimizationProgram",
        back_populates="peptide_protocols",
        lazy="selectin",
    )

    patient: Mapped["Patient"] = relationship(
        "Patient",
        back_populates="peptide_protocols",
        lazy="selectin",
    )

    provider: Mapped["Provider"] = relationship(
        "Provider",
        back_populates="peptide_protocols",
        lazy="selectin",
    )
