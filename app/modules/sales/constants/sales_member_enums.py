from enum import Enum


class SalesMemberStatus(str, Enum):
    """
    Lifecycle status of a Sales Member.
    """

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"


class SalesMemberRole(str, Enum):
    """
    Business role of a Sales Member within a Sales Organization.
    """

    SALES_ADMINISTRATOR = "SALES_ADMINISTRATOR"

    REGIONAL_MANAGER = "REGIONAL_MANAGER"

    SALES_MANAGER = "SALES_MANAGER"

    ACCOUNT_MANAGER = "ACCOUNT_MANAGER"

    SALES_EXECUTIVE = "SALES_EXECUTIVE"

    CUSTOMER_SUCCESS_EXECUTIVE = "CUSTOMER_SUCCESS_EXECUTIVE"

    FINANCE_EXECUTIVE = "FINANCE_EXECUTIVE"