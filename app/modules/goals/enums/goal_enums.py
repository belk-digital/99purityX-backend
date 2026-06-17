from enum import Enum


class GoalCategory(str, Enum):
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"
    METABOLIC_HEALTH = "metabolic_health"
    HORMONE_HEALTH = "hormone_health"
    SLEEP = "sleep"
    RECOVERY = "recovery"
    CARDIOVASCULAR = "cardiovascular"
    LONGEVITY = "longevity"
    BIOMARKER = "biomarker"
    CUSTOM = "custom"


class HealthGoalStatus(str, Enum):
    ACTIVE = "active"
    ACHIEVED = "achieved"
    PAUSED = "paused"
    CANCELLED = "cancelled"
