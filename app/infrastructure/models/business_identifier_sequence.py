from sqlalchemy import (
    Integer,
    String,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.infrastructure.database.base import Base
from app.infrastructure.database.mixins import (
    TimestampMixin,
    UUIDMixin,
)


class BusinessIdentifierSequence(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    """
    Stores sequential counters for business identifiers.

    Examples:

        ACC -> 125
        INV -> 981
        SUB -> 42
    """

    __tablename__ = "business_identifier_sequences"

    prefix: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True,
        index=True,
    )

    next_value: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )