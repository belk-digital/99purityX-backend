from enum import Enum


class SalesOrganizationStatus(str, Enum):
    """
    Lifecycle status of a Sales Organization.
    """

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    ARCHIVED = "ARCHIVED"


class SalesTeamStatus(str, Enum):
    """
    Lifecycle status of a Sales Team.
    """

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class TerritoryStatus(str, Enum):
    """
    Lifecycle status of a Territory.
    """

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class SalesMemberStatus(str, Enum):
    """
    Membership status of a Sales Member.
    """

    INVITED = "INVITED"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"


class SalesOrganizationRole(str, Enum):
    """
    Roles available inside a Sales Organization.
    """

    OWNER = "OWNER"

    ADMIN = "ADMIN"

    MANAGER = "MANAGER"

    ACCOUNT_MANAGER = "ACCOUNT_MANAGER"

    SALES_REPRESENTATIVE = "SALES_REPRESENTATIVE"

    CUSTOMER_SUCCESS = "CUSTOMER_SUCCESS"

    FINANCE = "FINANCE"

    SUPPORT = "SUPPORT"