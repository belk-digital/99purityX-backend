from enum import Enum


class InvitationStatus(str, Enum):
    """
    Current lifecycle state of an organization invitation.
    """

    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class InvitationType(str, Enum):
    """
    How the invitation was generated.

    This allows future onboarding flows without
    changing the database schema.
    """

    ORGANIZATION = "ORGANIZATION"
    PROVIDER = "PROVIDER"
    STAFF = "STAFF"


class InvitationSource(str, Enum):
    """
    Who initiated the invitation.
    Useful for audit logs, analytics and future workflows.
    """

    PLATFORM_ADMIN = "PLATFORM_ADMIN"
    ORGANIZATION_OWNER = "ORGANIZATION_OWNER"
    ORGANIZATION_ADMIN = "ORGANIZATION_ADMIN"
    SALES = "SALES"
    SYSTEM = "SYSTEM"