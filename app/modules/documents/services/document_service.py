from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, UploadFile, status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.modules.audit.schemas.audit_schema import AuditLogCreate
from app.modules.audit.services.audit_service import AuditService
from app.modules.documents.enums.document_enums import (
    DocumentStatus,
    DocumentType,
)
from app.modules.documents.models.document_model import Document
from app.modules.documents.repositories.document_repository import (
    DocumentRepository,
)
from app.modules.documents.schemas.document_schema import DocumentUpdate
from app.modules.documents.services.storage_service import StorageService


class DocumentService:
    def __init__(
        self,
        db: AsyncSession,
        storage_service: StorageService,
    ):
        self.db = db
        self.repository = DocumentRepository(db)
        self.storage_service = storage_service

    @staticmethod
    def _is_admin(current_user) -> bool:
        return bool(
            current_user.role
            and current_user.role.name == "ADMIN"
        )

    @staticmethod
    def _provider_id(current_user):
        if current_user.provider_profile:
            return current_user.provider_profile.id

        return None

    @staticmethod
    def _patient_id(current_user):
        if current_user.patient:
            return current_user.patient.id

        return None

    async def _validate_document_access(
        self,
        document: Document,
        current_user,
    ) -> None:
        if self._is_admin(current_user):
            return

        patient_id = self._patient_id(current_user)

        if patient_id and document.patient_id == patient_id:
            return

        provider_id = self._provider_id(current_user)

        if provider_id:
            has_access = await self.repository.provider_has_patient(
                provider_id=provider_id,
                patient_id=document.patient_id,
            )

            if has_access:
                return

        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Unauthorized document access",
        )

    async def _validate_upload_access(
        self,
        patient_id: UUID,
        provider_id: UUID | None,
        current_user,
    ) -> None:
        if self._is_admin(current_user):
            return

        current_patient_id = self._patient_id(current_user)

        if current_patient_id:
            if current_patient_id != patient_id:
                raise HTTPException(
                    status_code=http_status.HTTP_403_FORBIDDEN,
                    detail="Patients may only upload their own documents",
                )

            return

        current_provider_id = self._provider_id(current_user)

        if current_provider_id:
            if provider_id and provider_id != current_provider_id:
                raise HTTPException(
                    status_code=http_status.HTTP_403_FORBIDDEN,
                    detail="Provider mismatch",
                )

            has_access = await self.repository.provider_has_patient(
                provider_id=current_provider_id,
                patient_id=patient_id,
            )

            if has_access:
                return

        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Unauthorized document upload",
        )

    @staticmethod
    def _validate_file(
        file: UploadFile,
        content: bytes,
    ) -> None:
        mime_type = file.content_type or "application/octet-stream"

        if mime_type not in settings.ALLOWED_DOCUMENT_MIME_TYPES:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Unsupported document MIME type",
            )

        if len(content) <= 0:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty",
            )

        if len(content) > settings.MAX_DOCUMENT_UPLOAD_BYTES:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file exceeds maximum allowed size",
            )

    async def _document_download_url(
        self,
        document: Document,
    ) -> str:
        return await self.storage_service.generate_download_url(
            storage_key=document.storage_key,
            document_id=document.id,
        )

    async def attach_download_url(
        self,
        document: Document,
    ):
        setattr(
            document,
            "download_url",
            await self._document_download_url(document),
        )

        return document

    async def upload_document(
        self,
        file: UploadFile,
        patient_id: UUID,
        provider_id: UUID | None,
        document_type: DocumentType,
        title: str,
        description: str | None,
        consultation_id: UUID | None,
        lab_order_id: UUID | None,
        optimization_program_id: UUID | None,
        current_user,
    ) -> Document:
        if provider_id is None and self._provider_id(current_user):
            provider_id = self._provider_id(current_user)

        patient = await self.repository.get_patient_by_id(patient_id)

        if not patient:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Patient not found",
            )

        if provider_id:
            provider = await self.repository.get_provider_by_id(
                provider_id
            )

            if not provider:
                raise HTTPException(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    detail="Provider not found",
                )

        await self._validate_upload_access(
            patient_id=patient_id,
            provider_id=provider_id,
            current_user=current_user,
        )

        links_valid = await self.repository.optional_links_match_patient(
            patient_id=patient_id,
            consultation_id=consultation_id,
            lab_order_id=lab_order_id,
            optimization_program_id=optimization_program_id,
        )

        if not links_valid:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Linked record does not belong to patient",
            )

        content = await file.read()

        self._validate_file(file, content)

        original_file_name = file.filename or "document"
        mime_type = file.content_type or "application/octet-stream"

        file_name, storage_key = await self.storage_service.upload_file(
            original_file_name=original_file_name,
            content=content,
            mime_type=mime_type,
        )

        document = Document(
            patient_id=patient_id,
            provider_id=provider_id,
            uploaded_by_user_id=current_user.id,
            consultation_id=consultation_id,
            lab_order_id=lab_order_id,
            optimization_program_id=optimization_program_id,
            document_type=document_type,
            title=title,
            description=description,
            file_name=file_name,
            original_file_name=original_file_name,
            mime_type=mime_type,
            file_size=len(content),
            storage_key=storage_key,
            status=DocumentStatus.ACTIVE,
            uploaded_at=datetime.now(timezone.utc),
        )

        document = await self.repository.create(document)

        await AuditService.create_log(
            db=self.db,
            actor_user_id=current_user.id,
            payload=AuditLogCreate(
                action="document_uploaded",
                resource="document",
                resource_id=str(document.id),
                description="Document uploaded",
                audit_metadata={
                    "patient_id": str(patient_id),
                    "provider_id": str(provider_id)
                    if provider_id
                    else None,
                    "document_type": document.document_type.value,
                    "mime_type": document.mime_type,
                    "file_size": document.file_size,
                },
            ),
        )

        await self.db.commit()
        await self.db.refresh(document)

        return await self.attach_download_url(document)

    async def get_documents(
        self,
        current_user,
        limit: int = 20,
        offset: int = 0,
        document_type: DocumentType | None = None,
        patient_id: UUID | None = None,
        provider_id: UUID | None = None,
        status: DocumentStatus | None = None,
    ) -> list[Document]:
        effective_status = status or DocumentStatus.ACTIVE

        if self._is_admin(current_user):
            documents = await self.repository.get_all(
                limit=limit,
                offset=offset,
                document_type=document_type,
                patient_id=patient_id,
                provider_id=provider_id,
                status=effective_status,
            )
        elif self._patient_id(current_user):
            documents = await self.repository.get_all(
                limit=limit,
                offset=offset,
                document_type=document_type,
                patient_id=self._patient_id(current_user),
                status=effective_status,
            )
        elif self._provider_id(current_user):
            documents = await self.repository.get_all(
                limit=limit,
                offset=offset,
                document_type=document_type,
                patient_id=patient_id,
                provider_id=provider_id,
                status=effective_status,
            )
            documents = [
                document
                for document in documents
                if await self.repository.provider_has_patient(
                    self._provider_id(current_user),
                    document.patient_id,
                )
            ]
        else:
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="Unauthorized document access",
            )

        return [
            await self.attach_download_url(document)
            for document in documents
        ]

    async def get_document_by_id(
        self,
        document_id: UUID,
        current_user,
    ) -> Document:
        document = await self.repository.get_by_id(document_id)

        if not document:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        await self._validate_document_access(document, current_user)

        return await self.attach_download_url(document)

    async def get_download_url(
        self,
        document_id: UUID,
        current_user,
    ) -> str:
        document = await self.get_document_by_id(
            document_id,
            current_user,
        )

        if document.status == DocumentStatus.DELETED:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        download_url = await self._document_download_url(document)

        await AuditService.create_log(
            db=self.db,
            actor_user_id=current_user.id,
            payload=AuditLogCreate(
                action="document_downloaded",
                resource="document",
                resource_id=str(document.id),
                description="Document download URL generated",
                audit_metadata={
                    "patient_id": str(document.patient_id),
                    "document_type": document.document_type.value,
                },
            ),
        )

        await self.db.commit()

        return download_url

    async def update_document(
        self,
        document_id: UUID,
        payload: DocumentUpdate,
        current_user,
    ) -> Document:
        document = await self.get_document_by_id(
            document_id,
            current_user,
        )

        update_data = payload.model_dump(exclude_unset=True)
        old_status = document.status

        for field, value in update_data.items():
            setattr(document, field, value)

        document = await self.repository.update(document)

        audit_action = "document_updated"

        if old_status != document.status:
            if document.status == DocumentStatus.ARCHIVED:
                audit_action = "document_archived"
            elif document.status == DocumentStatus.DELETED:
                audit_action = "document_deleted"

        await AuditService.create_log(
            db=self.db,
            actor_user_id=current_user.id,
            payload=AuditLogCreate(
                action=audit_action,
                resource="document",
                resource_id=str(document.id),
                description="Document metadata updated",
                audit_metadata={
                    "old_status": old_status.value,
                    "new_status": document.status.value,
                },
            ),
        )

        await self.db.commit()
        await self.db.refresh(document)

        return await self.attach_download_url(document)

    async def delete_document(
        self,
        document_id: UUID,
        current_user,
    ) -> Document:
        document = await self.get_document_by_id(
            document_id,
            current_user,
        )

        document.status = DocumentStatus.DELETED

        document = await self.repository.update(document)

        await AuditService.create_log(
            db=self.db,
            actor_user_id=current_user.id,
            payload=AuditLogCreate(
                action="document_deleted",
                resource="document",
                resource_id=str(document.id),
                description="Document soft deleted",
                audit_metadata={
                    "patient_id": str(document.patient_id),
                    "document_type": document.document_type.value,
                },
            ),
        )

        await self.db.commit()
        await self.db.refresh(document)

        return await self.attach_download_url(document)

    async def get_patient_documents(
        self,
        patient_id: UUID,
        current_user,
        limit: int = 20,
        offset: int = 0,
        document_type: DocumentType | None = None,
        status: DocumentStatus | None = None,
    ) -> list[Document]:
        patient = await self.repository.get_patient_by_id(patient_id)

        if not patient:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Patient not found",
            )

        if not self._is_admin(current_user):
            current_patient_id = self._patient_id(current_user)

            if current_patient_id and current_patient_id != patient_id:
                raise HTTPException(
                    status_code=http_status.HTTP_403_FORBIDDEN,
                    detail="Unauthorized patient document access",
                )

            current_provider_id = self._provider_id(current_user)

            if current_provider_id:
                has_access = await self.repository.provider_has_patient(
                    current_provider_id,
                    patient_id,
                )

                if not has_access:
                    raise HTTPException(
                        status_code=http_status.HTTP_403_FORBIDDEN,
                        detail="Unauthorized patient document access",
                    )

        documents = await self.repository.get_by_patient_id(
            patient_id=patient_id,
            limit=limit,
            offset=offset,
            document_type=document_type,
            status=status or DocumentStatus.ACTIVE,
        )

        return [
            await self.attach_download_url(document)
            for document in documents
        ]
