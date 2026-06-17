from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.modules.providers.models.provider_model import Provider


class ProviderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_id(self, user_id: UUID) -> Provider | None:
        query = select(Provider).where(Provider.user_id == user_id)

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_by_id(self, provider_id: UUID) -> Provider | None:
        query = select(Provider).where(Provider.id == provider_id)

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_all(self) -> list[Provider]:
        query = select(Provider).order_by(Provider.created_at.desc())

        result = await self.db.execute(query)

        return list(result.scalars().all())

    async def create(self, provider: Provider) -> Provider:
        self.db.add(provider)

        await self.db.flush()
        await self.db.refresh(provider)

        return provider

    async def update(self, provider: Provider) -> Provider:
        await self.db.flush()
        await self.db.refresh(provider)

        return provider
    
    async def create(
        self,
        provider: Provider,
    ) -> Provider:

        self.db.add(provider)

        await self.db.flush()

        await self.db.refresh(provider)

        return provider