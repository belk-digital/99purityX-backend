from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base
from app.infrastructure.database.mixins import TimestampMixin, UUIDMixin
from app.modules.labs.enums.lab_enums import LabOrderStatus

if TYPE_CHECKING:
    from app.modules.consultations.models.consultation_model import Consultation
    from app.modules.documents.models.document_model import Document
    from app.modules.labs.models.lab_result_model import LabResult
    from app.modules.patients.models.patient_model import Patient
    from app.modules.providers.models.provider_model import Provider


class LabOrder(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "lab_orders"

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

    lab_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[LabOrderStatus] = mapped_column(
        Enum(LabOrderStatus),
        default=LabOrderStatus.ORDERED,
        nullable=False,
        index=True,
    )

    ordered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    patient: Mapped["Patient"] = relationship(
        "Patient",
        back_populates="lab_orders",
        lazy="selectin",
    )

    provider: Mapped["Provider"] = relationship(
        "Provider",
        back_populates="lab_orders",
        lazy="selectin",
    )

    consultation: Mapped["Consultation"] = relationship(
        "Consultation",
        back_populates="lab_orders",
        lazy="selectin",
    )

    results: Mapped[list["LabResult"]] = relationship(
        "LabResult",
        back_populates="lab_order",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    documents: Mapped[list["Document"]] = relationship(
        "Document",
        back_populates="lab_order",
        lazy="selectin",
    )
