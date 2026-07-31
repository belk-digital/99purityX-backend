from enum import Enum


class TerritoryStatus(str, Enum):
    """
    Lifecycle status of a Territory.
    """

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class TerritoryLevel(str, Enum):
    """
    Represents the hierarchy level of a territory.
    """

    COUNTRY = "COUNTRY"
    REGION = "REGION"
    STATE = "STATE"
    CITY = "CITY"
    ZONE = "ZONE"