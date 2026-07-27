from enum import StrEnum


class OrganizationStatus(StrEnum):
    """
    Represents the lifecycle state of an organization.

    PENDING   : Organization has been created but is not yet operational.
    ACTIVE    : Organization is active and can access the platform.
    SUSPENDED : Organization has been temporarily disabled.
    ARCHIVED  : Organization has been permanently archived.
    """

    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"