from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base
from app.infrastructure.database.mixins import TimestampMixin, UUIDMixin
from app.modules.documents.enums.document_enums import (
    DocumentStatus,
    DocumentType,
)

if TYPE_CHECKING:
    from app.modules.auth.models.user import User
    from app.modules.consultations.models.consultation_model import Consultation
    from app.modules.labs.models.lab_order_model import LabOrder
    from app.modules.optimization.models.optimization_program_model import (
        OptimizationProgram,
    )
    from app.modules.patients.models.patient_model import Patient
    from app.modules.providers.models.provider_model import Provider


class Document(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "documents"

    patient_id: Mapped[str] = mapped_column(
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    provider_id: Mapped[str | None] = mapped_column(
        ForeignKey("providers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    uploaded_by_user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    consultation_id: Mapped[str | None] = mapped_column(
        ForeignKey("consultations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    lab_order_id: Mapped[str | None] = mapped_column(
        ForeignKey("lab_orders.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    optimization_program_id: Mapped[str | None] = mapped_column(
        ForeignKey("optimization_programs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    document_type: Mapped[DocumentType] = mapped_column(
        Enum(DocumentType),
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

    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    original_file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    mime_type: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    file_size: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    storage_key: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        unique=True,
    )

    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus),
        default=DocumentStatus.ACTIVE,
        nullable=False,
        index=True,
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    patient: Mapped["Patient"] = relationship(
        "Patient",
        back_populates="documents",
        lazy="selectin",
    )

    provider: Mapped["Provider | None"] = relationship(
        "Provider",
        back_populates="documents",
        lazy="selectin",
    )

    uploaded_by_user: Mapped["User"] = relationship(
        "User",
        back_populates="uploaded_documents",
        lazy="selectin",
    )

    consultation: Mapped["Consultation | None"] = relationship(
        "Consultation",
        back_populates="documents",
        lazy="selectin",
    )

    lab_order: Mapped["LabOrder | None"] = relationship(
        "LabOrder",
        back_populates="documents",
        lazy="selectin",
    )

    optimization_program: Mapped["OptimizationProgram | None"] = relationship(
        "OptimizationProgram",
        back_populates="documents",
        lazy="selectin",
    )
