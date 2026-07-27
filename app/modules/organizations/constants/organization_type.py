from enum import StrEnum


class OrganizationType(StrEnum):
    """
    Defines the business category of an organization.

    This is intentionally generic so the platform can support
    multiple healthcare business models without schema changes.
    """

    CLINIC = "clinic"
    HOSPITAL = "hospital"
    INDEPENDENT_PRACTICE = "independent_practice"
    WELLNESS_CENTER = "wellness_center"
    MEDICAL_SPA = "medical_spa"
    CORPORATE_HEALTHCARE = "corporate_healthcare"
    ENTERPRISE_NETWORK = "enterprise_network"