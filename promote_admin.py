import asyncio
from sqlalchemy import select, text
import app.infrastructure.database.models
from app.infrastructure.database.session import AsyncSessionLocal
from app.modules.auth.models.role import Role

async def promote():
    async with AsyncSessionLocal() as db:
        role = (await db.execute(select(Role).where(Role.name == "ADMIN"))).scalar_one_or_none()
        if role:
            result = await db.execute(
                text("UPDATE users SET role_id = :rid WHERE email = :email"),
                {"rid": str(role.id), "email": "admin@belkdigital.com"},
            )
            await db.commit()
            print(f"Promoted {result.rowcount} user(s) to ADMIN")
        else:
            print("ADMIN role not found")

asyncio.run(promote())
