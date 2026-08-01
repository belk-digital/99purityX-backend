from enum import Enum


class BusinessIdentifierPrefix(str, Enum):
    """
    Prefixes used when generating business-facing identifiers.
    """

    ACCOUNT = "ACC"

    SUBSCRIPTION = "SUB"

    INVOICE = "INV"

    CONTRACT = "CON"

    PAYMENT = "PAY"

    TICKET = "TKT"

    APPOINTMENT = "APT"

    PRESCRIPTION = "RX"

    LAB_ORDER = "LAB"

    ORDER = "ORD"