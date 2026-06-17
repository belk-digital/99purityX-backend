from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.schemas.audit_schema import AuditLogCreate
from app.modules.audit.services.audit_service import AuditService
from app.modules.consultations.repositories.consultation_repository import (
    ConsultationRepository,
)
from app.modules.labs.enums.lab_enums import LabOrderStatus
from app.modules.labs.models.lab_order_model import LabOrder
from app.modules.labs.models.lab_result_model import LabResult
from app.modules.labs.repositories.lab_repository import (
    LabOrderRepository,
    LabResultRepository,
)
from app.modules.labs.schemas.lab_schema import (
    LabOrderCreate,
    LabOrderUpdate,
    LabResultCreate,
)
from app.modules.patients.repositories.patient_repository import (
    PatientRepository,
)
from app.modules.providers.repositories.provider_repository import (
    ProviderRepository,
)


class LabService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.lab_order_repository = LabOrderRepository(db)
        self.lab_result_repository = LabResultRepository(db)
        self.patient_repository = PatientRepository(db)
        self.provider_repository = ProviderRepository(db)
        self.consultation_repository = ConsultationRepository(db)

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

    async def _validate_lab_order_access(
        self,
        lab_order: LabOrder,
        current_user,
    ) -> None:
        if self._is_admin(current_user):
            return

        provider_id = self._provider_id(current_user)

        if provider_id and lab_order.provider_id == provider_id:
            return

        patient_id = self._patient_id(current_user)

        if patient_id and lab_order.patient_id == patient_id:
            return

        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Unauthorized lab access",
        )

    async def _validate_provider_write_access(
        self,
        provider_id: UUID,
        current_user,
    ) -> None:
        if self._is_admin(current_user):
            return

        current_provider_id = self._provider_id(current_user)

        if (
            not current_provider_id
            or current_provider_id != provider_id
        ):
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="Assigned provider access required",
            )

    async def create_lab_order(
        self,
        payload: LabOrderCreate,
        current_user,
    ) -> LabOrder:
        patient = await self.patient_repository.get_by_id(
            payload.patient_id
        )

        if not patient:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Patient not found",
            )

        provider = await self.provider_repository.get_by_id(
            payload.provider_id
        )

        if not provider:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Provider not found",
            )

        if not provider.is_active:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Provider is inactive",
            )

        await self._validate_provider_write_access(
            provider.id,
            current_user,
        )

        consultation = await self.consultation_repository.get_by_id(
            payload.consultation_id
        )

        if not consultation:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Consultation not found",
            )

        if consultation.patient_id != patient.id:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Consultation patient does not match lab order patient",
            )

        if consultation.provider_id != provider.id:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Consultation provider does not match lab order provider",
            )

        lab_order = LabOrder(
            patient_id=patient.id,
            provider_id=provider.id,
            consultation_id=consultation.id,
            lab_name=payload.lab_name,
            notes=payload.notes,
            ordered_at=payload.ordered_at
            or datetime.now(timezone.utc),
        )

        lab_order = await self.lab_order_repository.create(
            lab_order
        )

        await AuditService.create_log(
            db=self.db,
            actor_user_id=current_user.id,
            payload=AuditLogCreate(
                action="lab_order_created",
                resource="lab_order",
                resource_id=str(lab_order.id),
                description="Lab order created",
                audit_metadata={
                    "patient_id": str(patient.id),
                    "provider_id": str(provider.id),
                    "consultation_id": str(consultation.id),
                },
            ),
        )

        await self.db.commit()
        await self.db.refresh(lab_order)

        return lab_order

    async def get_lab_orders(
        self,
        current_user,
        limit: int = 20,
        offset: int = 0,
        status: LabOrderStatus | None = None,
    ) -> list[LabOrder]:
        if self._is_admin(current_user):
            return await self.lab_order_repository.get_all(
                limit=limit,
                offset=offset,
                status=status,
            )

        provider_id = self._provider_id(current_user)

        if provider_id:
            return await self.lab_order_repository.get_by_provider_id(
                provider_id=provider_id,
                limit=limit,
                offset=offset,
                status=status,
            )

        patient_id = self._patient_id(current_user)

        if patient_id:
            return await self.lab_order_repository.get_by_patient_id(
                patient_id=patient_id,
                limit=limit,
                offset=offset,
                status=status,
            )

        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Unauthorized lab access",
        )

    async def get_lab_order_by_id(
        self,
        lab_order_id: UUID,
        current_user,
    ) -> LabOrder:
        lab_order = await self.lab_order_repository.get_by_id(
            lab_order_id
        )

        if not lab_order:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Lab order not found",
            )

        await self._validate_lab_order_access(
            lab_order,
            current_user,
        )

        return lab_order

    async def update_lab_order(
        self,
        lab_order_id: UUID,
        payload: LabOrderUpdate,
        current_user,
    ) -> LabOrder:
        lab_order = await self.lab_order_repository.get_by_id(
            lab_order_id
        )

        if not lab_order:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Lab order not found",
            )

        await self._validate_provider_write_access(
            lab_order.provider_id,
            current_user,
        )

        old_status = lab_order.status

        update_data = payload.model_dump(
            exclude_unset=True,
        )

        for field, value in update_data.items():
            setattr(lab_order, field, value)

        if (
            lab_order.status == LabOrderStatus.COMPLETED
            and lab_order.completed_at is None
        ):
            lab_order.completed_at = datetime.now(timezone.utc)

        if (
            lab_order.status != LabOrderStatus.COMPLETED
            and payload.completed_at is None
        ):
            lab_order.completed_at = None

        lab_order = await self.lab_order_repository.update(
            lab_order
        )

        audit_action = "lab_order_updated"

        if (
            old_status != lab_order.status
            and lab_order.status == LabOrderStatus.COMPLETED
        ):
            audit_action = "lab_order_completed"

        if (
            old_status != lab_order.status
            and lab_order.status == LabOrderStatus.CANCELLED
        ):
            audit_action = "lab_order_cancelled"

        await AuditService.create_log(
            db=self.db,
            actor_user_id=current_user.id,
            payload=AuditLogCreate(
                action=audit_action,
                resource="lab_order",
                resource_id=str(lab_order.id),
                description="Lab order updated",
                audit_metadata={
                    "old_status": old_status.value,
                    "new_status": lab_order.status.value,
                },
            ),
        )

        await self.db.commit()
        await self.db.refresh(lab_order)

        return lab_order

    async def create_lab_result(
        self,
        payload: LabResultCreate,
        current_user,
    ) -> LabResult:
        lab_order = await self.lab_order_repository.get_by_id(
            payload.lab_order_id
        )

        if not lab_order:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Lab order not found",
            )

        await self._validate_provider_write_access(
            lab_order.provider_id,
            current_user,
        )

        if (
            payload.reference_min is not None
            and payload.reference_max is not None
            and payload.reference_min > payload.reference_max
        ):
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="reference_min must be less than or equal to reference_max",
            )

        lab_result = LabResult(
            lab_order_id=lab_order.id,
            biomarker_name=payload.biomarker_name,
            value=payload.value,
            unit=payload.unit,
            reference_min=payload.reference_min,
            reference_max=payload.reference_max,
            notes=payload.notes,
            recorded_at=payload.recorded_at
            or datetime.now(timezone.utc),
        )

        lab_result = await self.lab_result_repository.create(
            lab_result
        )

        await AuditService.create_log(
            db=self.db,
            actor_user_id=current_user.id,
            payload=AuditLogCreate(
                action="lab_result_created",
                resource="lab_result",
                resource_id=str(lab_result.id),
                description="Lab result created",
                audit_metadata={
                    "lab_order_id": str(lab_order.id),
                    "patient_id": str(lab_order.patient_id),
                    "provider_id": str(lab_order.provider_id),
                    "biomarker_name": lab_result.biomarker_name,
                },
            ),
        )

        await self.db.commit()
        await self.db.refresh(lab_result)

        return lab_result

    async def get_lab_result_by_id(
        self,
        lab_result_id: UUID,
        current_user,
    ) -> LabResult:
        lab_result = await self.lab_result_repository.get_by_id(
            lab_result_id
        )

        if not lab_result:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Lab result not found",
            )

        await self._validate_lab_order_access(
            lab_result.lab_order,
            current_user,
        )

        return lab_result

    async def get_patient_labs(
        self,
        patient_id: UUID,
        current_user,
        limit: int = 20,
        offset: int = 0,
        status: LabOrderStatus | None = None,
    ) -> list[LabOrder]:
        patient = await self.patient_repository.get_by_id(
            patient_id
        )

        if not patient:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Patient not found",
            )

        if not self._is_admin(current_user):
            current_patient_id = self._patient_id(current_user)
            current_provider_id = self._provider_id(current_user)

            if current_patient_id:
                if current_patient_id != patient_id:
                    raise HTTPException(
                        status_code=http_status.HTTP_403_FORBIDDEN,
                        detail="Unauthorized patient lab access",
                    )

            elif current_provider_id:
                pass

            else:
                raise HTTPException(
                    status_code=http_status.HTTP_403_FORBIDDEN,
                    detail="Unauthorized patient lab access",
                )

        if (
            not self._is_admin(current_user)
            and self._provider_id(current_user)
        ):
            return await (
                self.lab_order_repository.get_by_patient_and_provider_id(
                    patient_id=patient_id,
                    provider_id=self._provider_id(current_user),
                    limit=limit,
                    offset=offset,
                    status=status,
                    include_results=True,
                )
            )

        return await self.lab_order_repository.get_by_patient_id(
            patient_id=patient_id,
            limit=limit,
            offset=offset,
            status=status,
            include_results=True,
        )
