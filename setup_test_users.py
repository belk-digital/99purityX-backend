"""
Run after registering test accounts to set up roles.

Usage:
  .venv\Scripts\python setup_test_users.py

Edit the emails below to match your registered accounts.
"""
import asyncio
from sqlalchemy import select, text

import app.infrastructure.database.models  # noqa: F401
from app.infrastructure.database.session import AsyncSessionLocal
from app.modules.auth.models.user import User
from app.modules.auth.models.role import Role
from app.modules.providers.models.provider_model import Provider


# ─── EDIT THESE ───────────────────────────────────────────────────────────────
ADMIN_EMAIL = "admin@belkdigital.com"
DOCTOR_EMAIL = "doctor@test.com"
# ──────────────────────────────────────────────────────────────────────────────


async def main():
    async with AsyncSessionLocal() as db:
        # 1. Promote admin
        admin_role = (await db.execute(
            select(Role).where(Role.name == "ADMIN")
        )).scalar_one_or_none()

        if admin_role:
            result = await db.execute(
                text("UPDATE users SET role_id = :rid WHERE email = :email"),
                {"rid": str(admin_role.id), "email": ADMIN_EMAIL},
            )
            print(f"Promoted {ADMIN_EMAIL} to ADMIN: {result.rowcount} row(s)")

        # 2. Give doctor the DOCTOR role
        doctor_role = (await db.execute(
            select(Role).where(Role.name == "DOCTOR")
        )).scalar_one_or_none()

        doctor_user = (await db.execute(
            select(User).where(User.email == DOCTOR_EMAIL)
        )).scalar_one_or_none()

        if doctor_role and doctor_user:
            await db.execute(
                text("UPDATE users SET role_id = :rid WHERE email = :email"),
                {"rid": str(doctor_role.id), "email": DOCTOR_EMAIL},
            )
            print(f"Set {DOCTOR_EMAIL} role to DOCTOR")

            # 3. Create provider profile if not exists
            existing = (await db.execute(
                select(Provider).where(Provider.user_id == doctor_user.id)
            )).scalar_one_or_none()

            if not existing:
                provider = Provider(
                    user_id=doctor_user.id,
                    provider_type="Physician",
                    speciality="General Medicine",
                    years_experience=5,
                    consultation_fee=150,
                )
                db.add(provider)
                print(f"Created provider profile for {DOCTOR_EMAIL}")
            else:
                print(f"Provider profile already exists for {DOCTOR_EMAIL}")

        await db.commit()
        print("Done!")


asyncio.run(main())
