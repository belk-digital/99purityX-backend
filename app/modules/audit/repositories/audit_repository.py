from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.models.audit_log_model import AuditLog


class AuditRepository:

    @staticmethod
    async def create(
        db: AsyncSession,
        audit_log: AuditLog
    ) -> AuditLog:

        db.add(audit_log)

        await db.commit()
        await db.refresh(audit_log)

        return audit_log

    @staticmethod
    async def get_all(
        db: AsyncSession,
        limit: int = 100,
        offset: int = 0
    ):

        query = (
            select(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await db.execute(query)

        return result.scalars().all()