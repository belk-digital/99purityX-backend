from uuid import UUID

from sqlalchemy import desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.appointments.models.appointment_model import Appointment
from app.modules.consultations.models.consultation_model import Consultation
from app.modules.documents.enums.document_enums import (
    DocumentStatus,
    DocumentType,
)
from app.modules.documents.models.document_model import Document
from app.modules.labs.models.lab_order_model import LabOrder
from app.modules.optimization.models.optimization_program_model import (
    OptimizationProgram,
)
from app.modules.patients.models.patient_model import Patient
from app.modules.providers.models.provider_model import Provider


class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, document: Document) -> Document:
        self.db.add(document)

        await self.db.flush()
        await self.db.refresh(document)

        return document

    async def update(self, document: Document) -> Document:
        await self.db.flush()
        await self.db.refresh(document)

        return document

    async def get_by_id(self, document_id: UUID) -> Document | None:
        result = await self.db.execute(
            select(Document)
            .options(
                selectinload(Document.patient),
                selectinload(Document.provider),
                selectinload(Document.uploaded_by_user),
                selectinload(Document.consultation),
                selectinload(Document.lab_order),
                selectinload(Document.optimization_program),
            )
            .where(Document.id == document_id)
        )

        return result.scalar_one_or_none()

    async def get_all(
        self,
        limit: int = 20,
        offset: int = 0,
        document_type: DocumentType | None = None,
        patient_id: UUID | None = None,
        provider_id: UUID | None = None,
        status: DocumentStatus | None = None,
    ) -> list[Document]:
        query = select(Document).options(
            selectinload(Document.patient),
            selectinload(Document.provider),
            selectinload(Document.uploaded_by_user),
        )

        if document_type:
            query = query.where(Document.document_type == document_type)

        if patient_id:
            query = query.where(Document.patient_id == patient_id)

        if provider_id:
            query = query.where(Document.provider_id == provider_id)

        if status:
            query = query.where(Document.status == status)

        query = (
            query.order_by(desc(Document.uploaded_at))
            .offset(offset)
            .limit(limit)
        )

        result = await self.db.execute(query)

        return list(result.scalars().all())

    async def get_by_patient_id(
        self,
        patient_id: UUID,
        limit: int = 20,
        offset: int = 0,
        document_type: DocumentType | None = None,
        status: DocumentStatus | None = None,
    ) -> list[Document]:
        return await self.get_all(
            limit=limit,
            offset=offset,
            document_type=document_type,
            patient_id=patient_id,
            status=status,
        )

    async def get_patient_by_id(self, patient_id: UUID) -> Patient | None:
        result = await self.db.execute(
            select(Patient).where(Patient.id == patient_id)
        )

        return result.scalar_one_or_none()

    async def get_provider_by_id(self, provider_id: UUID) -> Provider | None:
        result = await self.db.execute(
            select(Provider).where(Provider.id == provider_id)
        )

        return result.scalar_one_or_none()

    async def provider_has_patient(
        self,
        provider_id: UUID,
        patient_id: UUID,
    ) -> bool:
        result = await self.db.execute(
            select(OptimizationProgram.id).where(
                OptimizationProgram.provider_id == provider_id,
                OptimizationProgram.patient_id == patient_id,
            )
        )

        if result.scalar_one_or_none() is not None:
            return True

        result = await self.db.execute(
            select(Consultation.id).where(
                Consultation.provider_id == provider_id,
                Consultation.patient_id == patient_id,
            )
        )

        if result.scalar_one_or_none() is not None:
            return True

        result = await self.db.execute(
            select(Appointment.id).where(
                Appointment.provider_id == provider_id,
                Appointment.patient_id == patient_id,
            )
        )

        return result.scalar_one_or_none() is not None

    async def optional_links_match_patient(
        self,
        patient_id: UUID,
        consultation_id: UUID | None = None,
        lab_order_id: UUID | None = None,
        optimization_program_id: UUID | None = None,
    ) -> bool:
        if consultation_id:
            result = await self.db.execute(
                select(Consultation.id).where(
                    Consultation.id == consultation_id,
                    Consultation.patient_id == patient_id,
                )
            )

            if result.scalar_one_or_none() is None:
                return False

        if lab_order_id:
            result = await self.db.execute(
                select(LabOrder.id).where(
                    LabOrder.id == lab_order_id,
                    LabOrder.patient_id == patient_id,
                )
            )

            if result.scalar_one_or_none() is None:
                return False

        if optimization_program_id:
            result = await self.db.execute(
                select(OptimizationProgram.id).where(
                    OptimizationProgram.id == optimization_program_id,
                    OptimizationProgram.patient_id == patient_id,
                )
            )

            if result.scalar_one_or_none() is None:
                return False

        return True
