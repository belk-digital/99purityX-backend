from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models.role import Role


ROLES = [
    {
        "name": "ADMIN",
        "description": "Platform administrator with full access"
    },
    {
        "name": "DOCTOR",
        "description": "Medical provider role"
    },
    {
        "name": "PATIENT",
        "description": "Patient role"
    },
    {
        "name": "NUTRITIONIST",
        "description": "Nutrition specialist role"
    },
    {
        "name": "CARE_COORDINATOR",
        "description": "Care coordination role"
    }
]


async def seed_roles(
    db: AsyncSession
) -> None:

    for role_data in ROLES:

        result = await db.execute(
            select(Role).where(
                Role.name == role_data["name"]
            )
        )

        existing_role = result.scalar_one_or_none()

        if existing_role:
            continue

        role = Role(
            name=role_data["name"],
            description=role_data["description"]
        )

        db.add(role)

    await db.commit()