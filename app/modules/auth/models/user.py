from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
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

if TYPE_CHECKING:
    from app.modules.documents.models.document_model import Document
    from app.modules.auth.models.role import Role
    from app.modules.auth.models.user_profile import UserProfile
    from app.modules.auth.models.session import UserSession
    from app.modules.patients.models.patient_model import Patient
    from app.modules.providers.models.provider_model import Provider


class User(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role_id = mapped_column(
        ForeignKey("roles.id"),
        nullable=False,
    )
    
    google_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    auth_provider: Mapped[str] = mapped_column(
        String(50),
        default="local",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    mfa_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    role: Mapped["Role"] = relationship(
        "Role",
        back_populates="users",
    )

    profile: Mapped["UserProfile"] = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
    )

    sessions: Mapped[list["UserSession"]] = relationship(
        "UserSession",
        back_populates="user",
    )

    patient: Mapped["Patient"] = relationship(
        "Patient",
        back_populates="user",
        uselist=False,
    )

    provider_profile: Mapped["Provider"] = relationship(
        "Provider",
        back_populates="user",
        uselist=False,
        lazy="selectin",
    )

    uploaded_documents: Mapped[list["Document"]] = relationship(
        "Document",
        back_populates="uploaded_by_user",
        lazy="selectin",
    )

    