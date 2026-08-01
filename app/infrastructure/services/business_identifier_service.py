from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.constants.business_identifier_prefixes import (
    BusinessIdentifierPrefix,
)
from app.infrastructure.models.business_identifier_sequence import (
    BusinessIdentifierSequence,
)
from app.infrastructure.repositories.business_identifier_repository import (
    BusinessIdentifierRepository,
)
from app.infrastructure.utils.business_identifier import (
    BusinessIdentifierGenerator,
)


class BusinessIdentifierService:
    """
    Generates sequential business identifiers.

    Examples:

        ACC-000001
        INV-000001
        SUB-000001
        CON-000001
    """

    @staticmethod
    async def generate_next(
        db: AsyncSession,
        prefix: BusinessIdentifierPrefix,
    ) -> str:

        repository = BusinessIdentifierRepository(db)

        await repository.get_by_prefix_for_update(
            prefix.value,
        )

        # ---------------------------------------------------------
        # First identifier for this prefix
        # ---------------------------------------------------------

        if sequence is None:

            sequence = BusinessIdentifierSequence(
                prefix=prefix.value,
                next_value=2,
            )

            await repository.create(sequence)

            return BusinessIdentifierGenerator.format(
                prefix=prefix,
                sequence=1,
            )

        # ---------------------------------------------------------
        # Existing prefix
        # ---------------------------------------------------------

        current_value = sequence.next_value

        sequence.next_value += 1

        await repository.update(sequence)

        return BusinessIdentifierGenerator.format(
            prefix=prefix,
            sequence=current_value,
        )