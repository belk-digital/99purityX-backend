import asyncio

from app.infrastructure.database import models

from app.infrastructure.database.session import (
    AsyncSessionLocal
)

from app.modules.auth.seed.seed_roles import (
    seed_roles
)

from app.modules.auth.seed.seed_permissions import (
    seed_permissions
)

from app.modules.auth.seed.seed_role_permissions import (
    seed_role_permissions
)




async def run():

    async with AsyncSessionLocal() as db:

        print("Seeding roles...")
        await seed_roles(db)

        print("Seeding permissions...")
        await seed_permissions(db)

        print("Seeding role permissions...")
        await seed_role_permissions(db)

        print("RBAC seeding completed.")


if __name__ == "__main__":
    asyncio.run(run())