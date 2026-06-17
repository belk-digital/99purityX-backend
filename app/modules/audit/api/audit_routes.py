from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import get_db
from app.modules.audit.schemas.audit_schema import (
    AuditLogResponse
)
from app.modules.audit.services.audit_service import AuditService
from app.modules.auth.api.rbac import (
    require_permissions,
)
from app.modules.auth.models.user import User

router = APIRouter(
    prefix="/audit",
    tags=["Audit"]
)


@router.get(
    "/logs",
    response_model=list[AuditLogResponse]
)
async def get_audit_logs(
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_permissions(["view_audit_logs"])
    )
):

    return await AuditService.get_logs(
        db=db,
        limit=limit,
        offset=offset
    )