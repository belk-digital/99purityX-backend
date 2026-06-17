from enum import Enum


class LabOrderStatus(str, Enum):
    ORDERED = "ordered"
    SAMPLE_COLLECTED = "sample_collected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
