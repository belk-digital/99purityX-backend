from enum import Enum


class SalesOrganizationStatus(str, Enum):
    """
    Lifecycle status of a Sales Organization.
    """

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    ARCHIVED = "ARCHIVED"