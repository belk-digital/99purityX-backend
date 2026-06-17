import asyncio
import app.infrastructure.database.models  # noqa: F401 — registers all SQLAlchemy models
from app.infrastructure.database.session import AsyncSessionLocal
from app.modules.auth.seed.seed_roles import seed_roles
from app.modules.auth.seed.seed_permissions import seed_permissions
from app.modules.auth.seed.seed_role_permissions import seed_role_permissions

async def main():
    async with AsyncSessionLocal() as db:
        print("Seeding roles...")
        await seed_roles(db)
        print("Seeding permissions...")
        await seed_permissions(db)
        print("Seeding role permissions...")
        await seed_role_permissions(db)
        print("Done.")

asyncio.run(main())