from enum import Enum


class RoleEnum(str, Enum):
    ADMIN = "ADMIN"
    PROVIDER = "PROVIDER"
    PATIENT = "PATIENT"
    STAFF = "STAFF"