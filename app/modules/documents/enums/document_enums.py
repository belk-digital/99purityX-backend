from enum import Enum


class DocumentType(str, Enum):
    LAB_REPORT = "lab_report"
    PRESCRIPTION = "prescription"
    CONSULTATION_ATTACHMENT = "consultation_attachment"
    MEDICAL_RECORD = "medical_record"
    INSURANCE_DOCUMENT = "insurance_document"
    CONSENT_FORM = "consent_form"
    OPTIMIZATION_PROGRAM_DOCUMENT = "optimization_program_document"
    PROGRESS_REPORT = "progress_report"
    OTHER = "other"


class DocumentStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"
