from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models.business_identifier_sequence import (
    BusinessIdentifierSequence,
)


class BusinessIdentifierRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    # -------------------------------------------------------------------------
    # Create
    # -------------------------------------------------------------------------

    async def create(
        self,
        sequence: BusinessIdentifierSequence,
    ) -> BusinessIdentifierSequence:

        self.db.add(sequence)

        await self.db.flush()

        await self.db.refresh(sequence)

        return sequence

    # -------------------------------------------------------------------------
    # Read
    # -------------------------------------------------------------------------

    async def get_by_prefix(
        self,
        prefix: str,
        *,
        for_update: bool = False,
    ) -> BusinessIdentifierSequence | None:
        """
        Retrieve a business identifier sequence.

        When for_update=True, acquires a row-level lock
        (SELECT ... FOR UPDATE) to safely generate identifiers
        under concurrent requests.
        """

        query = (
            select(
                BusinessIdentifierSequence,
            )
            .where(
                BusinessIdentifierSequence.prefix == prefix,
            )
        )

        if for_update:
            query = query.with_for_update()

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_all(
        self,
    ) -> list[BusinessIdentifierSequence]:

        query = (
            select(
                BusinessIdentifierSequence,
            )
            .order_by(
                BusinessIdentifierSequence.prefix.asc(),
            )
        )

        result = await self.db.execute(query)

        return result.scalars().all()

    # -------------------------------------------------------------------------
    # Update
    # -------------------------------------------------------------------------

    async def update(
        self,
        sequence: BusinessIdentifierSequence,
    ) -> BusinessIdentifierSequence:

        await self.db.flush()

        await self.db.refresh(sequence)

        return sequence

    # -------------------------------------------------------------------------
    # Delete
    # -------------------------------------------------------------------------

    async def delete(
        self,
        sequence: BusinessIdentifierSequence,
    ) -> None:

        await self.db.delete(sequence)

        await self.db.flush()