import uuid
from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel


class AuditLogCreate(BaseModel):
    action: str
    resource: str
    resource_id: Optional[str] = None
    description: Optional[str] = None
    audit_metadata: Optional[dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuditLogResponse(BaseModel):
    id: uuid.UUID
    actor_user_id: Optional[uuid.UUID]
    action: str
    resource: str
    resource_id: Optional[str]
    description: Optional[str]
    audit_metadata: Optional[dict]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True