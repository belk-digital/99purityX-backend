import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.models.audit_log_model import AuditLog
from app.modules.audit.repositories.audit_repository import AuditRepository
from app.modules.audit.schemas.audit_schema import AuditLogCreate


class AuditService:

    @staticmethod
    async def create_log(
        db: AsyncSession,
        actor_user_id: Optional[uuid.UUID],
        payload: AuditLogCreate
    ) -> AuditLog:

        audit_log = AuditLog(
            actor_user_id=actor_user_id,
            action=payload.action,
            resource=payload.resource,
            resource_id=payload.resource_id,
            description=payload.description,
            audit_metadata=payload.audit_metadata,
            ip_address=payload.ip_address,
            user_agent=payload.user_agent,
        )

        return await AuditRepository.create(
            db=db,
            audit_log=audit_log
        )

    @staticmethod
    async def get_logs(
        db: AsyncSession,
        limit: int,
        offset: int
    ):

        return await AuditRepository.get_all(
            db=db,
            limit=limit,
            offset=offset
        )