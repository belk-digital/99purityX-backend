from enum import Enum


class OrganizationSalesAccountStatus(str, Enum):
    """
    Represents the commercial lifecycle of a healthcare organization.
    """

    PROSPECT = "PROSPECT"

    ONBOARDING = "ONBOARDING"

    ACTIVE = "ACTIVE"

    SUSPENDED = "SUSPENDED"

    CHURNED = "CHURNED"