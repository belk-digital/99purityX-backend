from enum import Enum


class SalesTeamStatus(str, Enum):
    """
    Lifecycle status of a Sales Team.
    """

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"