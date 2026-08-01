from app.infrastructure.constants.business_identifier_prefixes import (
    BusinessIdentifierPrefix,
)


class BusinessIdentifierGenerator:

    DEFAULT_PADDING = 6

    @classmethod
    def format(
        cls,
        prefix: BusinessIdentifierPrefix,
        sequence: int,
        padding: int | None = None,
    ) -> str:

        if padding is None:
            padding = cls.DEFAULT_PADDING

        return (
            f"{prefix.value}-"
            f"{str(sequence).zfill(padding)}"
        )