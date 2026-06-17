from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.optimization.enums.program_enums import (
    PeptideProtocolStatus,
)
from app.modules.optimization.models.peptide_protocol_model import (
    PeptideProtocol,
)


class PeptideProtocolRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        peptide_protocol: PeptideProtocol,
    ) -> PeptideProtocol:
        self.db.add(peptide_protocol)

        await self.db.flush()
        await self.db.refresh(peptide_protocol)

        return peptide_protocol

    async def update(
        self,
        peptide_protocol: PeptideProtocol,
    ) -> PeptideProtocol:
        await self.db.flush()
        await self.db.refresh(peptide_protocol)

        return peptide_protocol

    async def get_by_id(
        self,
        peptide_protocol_id: UUID,
    ) -> PeptideProtocol | None:
        result = await self.db.execute(
            select(PeptideProtocol)
            .options(
                selectinload(PeptideProtocol.program),
                selectinload(PeptideProtocol.patient),
                selectinload(PeptideProtocol.provider),
            )
            .where(PeptideProtocol.id == peptide_protocol_id)
        )

        return result.scalar_one_or_none()

    async def get_all(
        self,
        limit: int = 20,
        offset: int = 0,
        status: PeptideProtocolStatus | None = None,
    ) -> list[PeptideProtocol]:
        query = select(PeptideProtocol).options(
            selectinload(PeptideProtocol.program),
            selectinload(PeptideProtocol.patient),
            selectinload(PeptideProtocol.provider),
        )

        if status:
            query = query.where(PeptideProtocol.status == status)

        query = (
            query.order_by(desc(PeptideProtocol.created_at))
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
        status: PeptideProtocolStatus | None = None,
    ) -> list[PeptideProtocol]:
        query = (
            select(PeptideProtocol)
            .options(
                selectinload(PeptideProtocol.program),
                selectinload(PeptideProtocol.patient),
                selectinload(PeptideProtocol.provider),
            )
            .where(PeptideProtocol.patient_id == patient_id)
        )

        if status:
            query = query.where(PeptideProtocol.status == status)

        query = (
            query.order_by(desc(PeptideProtocol.created_at))
            .offset(offset)
            .limit(limit)
        )

        result = await self.db.execute(query)

        return list(result.scalars().all())

    async def get_by_provider_id(
        self,
        provider_id: UUID,
        limit: int = 20,
        offset: int = 0,
        status: PeptideProtocolStatus | None = None,
    ) -> list[PeptideProtocol]:
        query = (
            select(PeptideProtocol)
            .options(
                selectinload(PeptideProtocol.program),
                selectinload(PeptideProtocol.patient),
                selectinload(PeptideProtocol.provider),
            )
            .where(PeptideProtocol.provider_id == provider_id)
        )

        if status:
            query = query.where(PeptideProtocol.status == status)

        query = (
            query.order_by(desc(PeptideProtocol.created_at))
            .offset(offset)
            .limit(limit)
        )

        result = await self.db.execute(query)

        return list(result.scalars().all())

    async def get_by_patient_and_provider_id(
        self,
        patient_id: UUID,
        provider_id: UUID,
        limit: int = 20,
        offset: int = 0,
        status: PeptideProtocolStatus | None = None,
    ) -> list[PeptideProtocol]:
        query = (
            select(PeptideProtocol)
            .options(
                selectinload(PeptideProtocol.program),
                selectinload(PeptideProtocol.patient),
                selectinload(PeptideProtocol.provider),
            )
            .where(
                PeptideProtocol.patient_id == patient_id,
                PeptideProtocol.provider_id == provider_id,
            )
        )

        if status:
            query = query.where(PeptideProtocol.status == status)

        query = (
            query.order_by(desc(PeptideProtocol.created_at))
            .offset(offset)
            .limit(limit)
        )

        result = await self.db.execute(query)

        return list(result.scalars().all())
