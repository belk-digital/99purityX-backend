from enum import Enum


class OrganizationSalesAccountType(str, Enum):
    """
    Defines the commercial classification of a customer account.
    """

    DIRECT = "DIRECT"

    RESELLER = "RESELLER"

    ENTERPRISE = "ENTERPRISE"

    PARTNER = "PARTNER"

    INTERNAL = "INTERNAL"