from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import get_db
from app.modules.auth.api.rbac import require_permissions
from app.modules.auth.constants.permissions import (
    DELETE_DOCUMENTS,
    UPDATE_DOCUMENTS,
    UPLOAD_DOCUMENTS,
    VIEW_DOCUMENTS,
)
from app.modules.auth.models.user import User
from app.modules.documents.enums.document_enums import (
    DocumentStatus,
    DocumentType,
)
from app.modules.documents.schemas.document_schema import (
    DocumentDownloadResponse,
    DocumentResponse,
    DocumentUpdate,
)
from app.modules.documents.services.document_service import DocumentService
from app.modules.documents.services.storage_service import get_storage_service

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


def get_document_service(
    db: AsyncSession = Depends(get_db),
) -> DocumentService:
    return DocumentService(
        db=db,
        storage_service=get_storage_service(),
    )


@router.post(
    "/upload",
    response_model=DocumentResponse,
)
async def upload_document(
    file: UploadFile = File(...),
    patient_id: UUID = Form(...),
    document_type: DocumentType = Form(...),
    title: str = Form(...),
    provider_id: UUID | None = Form(default=None),
    description: str | None = Form(default=None),
    consultation_id: UUID | None = Form(default=None),
    lab_order_id: UUID | None = Form(default=None),
    optimization_program_id: UUID | None = Form(default=None),
    current_user: User = Depends(require_permissions(UPLOAD_DOCUMENTS)),
    service: DocumentService = Depends(get_document_service),
):
    return await service.upload_document(
        file=file,
        patient_id=patient_id,
        provider_id=provider_id,
        document_type=document_type,
        title=title,
        description=description,
        consultation_id=consultation_id,
        lab_order_id=lab_order_id,
        optimization_program_id=optimization_program_id,
        current_user=current_user,
    )


@router.get(
    "",
    response_model=list[DocumentResponse],
)
async def get_documents(
    document_type: DocumentType | None = Query(default=None),
    patient_id: UUID | None = Query(default=None),
    provider_id: UUID | None = Query(default=None),
    status: DocumentStatus | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(require_permissions(VIEW_DOCUMENTS)),
    service: DocumentService = Depends(get_document_service),
):
    return await service.get_documents(
        current_user=current_user,
        limit=limit,
        offset=offset,
        document_type=document_type,
        patient_id=patient_id,
        provider_id=provider_id,
        status=status,
    )


@router.get(
    "/patient/{patient_id}",
    response_model=list[DocumentResponse],
)
async def get_patient_documents(
    patient_id: UUID,
    document_type: DocumentType | None = Query(default=None),
    status: DocumentStatus | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(require_permissions(VIEW_DOCUMENTS)),
    service: DocumentService = Depends(get_document_service),
):
    return await service.get_patient_documents(
        patient_id=patient_id,
        current_user=current_user,
        limit=limit,
        offset=offset,
        document_type=document_type,
        status=status,
    )


@router.get(
    "/{document_id}/download",
    response_model=DocumentDownloadResponse,
)
async def get_document_download_url(
    document_id: UUID,
    current_user: User = Depends(require_permissions(VIEW_DOCUMENTS)),
    service: DocumentService = Depends(get_document_service),
):
    download_url = await service.get_download_url(
        document_id=document_id,
        current_user=current_user,
    )

    return DocumentDownloadResponse(
        document_id=document_id,
        download_url=download_url,
        expires_in_seconds=300,
    )


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
)
async def get_document_by_id(
    document_id: UUID,
    current_user: User = Depends(require_permissions(VIEW_DOCUMENTS)),
    service: DocumentService = Depends(get_document_service),
):
    return await service.get_document_by_id(
        document_id=document_id,
        current_user=current_user,
    )


@router.put(
    "/{document_id}",
    response_model=DocumentResponse,
)
async def update_document(
    document_id: UUID,
    payload: DocumentUpdate,
    current_user: User = Depends(require_permissions(UPDATE_DOCUMENTS)),
    service: DocumentService = Depends(get_document_service),
):
    return await service.update_document(
        document_id=document_id,
        payload=payload,
        current_user=current_user,
    )


@router.delete(
    "/{document_id}",
    response_model=DocumentResponse,
)
async def delete_document(
    document_id: UUID,
    current_user: User = Depends(require_permissions(DELETE_DOCUMENTS)),
    service: DocumentService = Depends(get_document_service),
):
    return await service.delete_document(
        document_id=document_id,
        current_user=current_user,
    )
