from enum import Enum


class OrganizationRole(str, Enum):
    """
    Organization-specific roles.

    These define a user's role within an organization and are
    independent of platform-level roles (e.g., Super Admin).
    """

    OWNER = "OWNER"
    ADMINISTRATOR = "ADMINISTRATOR"
    PROVIDER = "PROVIDER"
    NURSE = "NURSE"
    RECEPTIONIST = "RECEPTIONIST"
    MEDICAL_ASSISTANT = "MEDICAL_ASSISTANT"
    BILLING = "BILLING"
    SUPPORT = "SUPPORT"
    VIEWER = "VIEWER"


class MembershipStatus(str, Enum):
    """
    Lifecycle state of the membership.
    """

    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    DISABLED = "DISABLED"
    REMOVED = "REMOVED"

