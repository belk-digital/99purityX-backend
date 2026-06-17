"""
Seeds demo patients, doctors, and admin for production demo.
Usage: python seed_demo_data.py
All accounts use password: Demo@1234
"""
import asyncio
from sqlalchemy import select
import app.infrastructure.database.models  # noqa: F401
from app.infrastructure.database.session import AsyncSessionLocal
from app.modules.auth.models.user import User
from app.modules.auth.models.role import Role
from app.modules.auth.models.user_profile import UserProfile
from app.modules.auth.services.password_service import PasswordService
from app.modules.patients.models.patient_model import Patient
from app.modules.providers.models.provider_model import Provider

PASSWORD = "Demo@1234"

PATIENTS = [
    {"email": "john.patient@demo.com", "first": "John", "last": "Smith"},
    {"email": "sarah.patient@demo.com", "first": "Sarah", "last": "Johnson"},
    {"email": "mike.patient@demo.com", "first": "Mike", "last": "Williams"},
    {"email": "emma.patient@demo.com", "first": "Emma", "last": "Brown"},
    {"email": "alex.patient@demo.com", "first": "Alex", "last": "Davis"},
]

DOCTORS = [
    {"email": "dr.wilson@demo.com", "first": "James", "last": "Wilson", "type": "Physician", "speciality": "General Medicine", "exp": 12, "fee": 150},
    {"email": "dr.chen@demo.com", "first": "Lisa", "last": "Chen", "type": "Specialist", "speciality": "Endocrinology", "exp": 8, "fee": 200},
    {"email": "dr.patel@demo.com", "first": "Raj", "last": "Patel", "type": "Specialist", "speciality": "Cardiology", "exp": 15, "fee": 250},
    {"email": "dr.martinez@demo.com", "first": "Maria", "last": "Martinez", "type": "Nutritionist", "speciality": "Sports Nutrition", "exp": 6, "fee": 120},
    {"email": "dr.thompson@demo.com", "first": "David", "last": "Thompson", "type": "Physician", "speciality": "Anti-Aging Medicine", "exp": 10, "fee": 180},
]

ADMIN_EMAIL = "admin@belkdigital.com"


async def create_user(db, email, first, last, role):
    existing = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if existing:
        print(f"  Already exists: {email}")
        return existing

    user = User(
        email=email,
        hashed_password=PasswordService.hash_password(PASSWORD),
        role_id=role.id,
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    await db.flush()

    profile = UserProfile(user_id=user.id, first_name=first, last_name=last)
    db.add(profile)

    return user


async def main():
    async with AsyncSessionLocal() as db:
        # Get roles
        patient_role = (await db.execute(select(Role).where(Role.name == "PATIENT"))).scalar_one_or_none()
        doctor_role = (await db.execute(select(Role).where(Role.name == "DOCTOR"))).scalar_one_or_none()
        admin_role = (await db.execute(select(Role).where(Role.name == "ADMIN"))).scalar_one_or_none()

        if not patient_role or not doctor_role:
            print("ERROR: Roles not seeded. Run seed.py first.")
            return

        # Create patients
        print("\n--- Creating Patients ---")
        for p in PATIENTS:
            user = await create_user(db, p["email"], p["first"], p["last"], patient_role)
            # Create patient profile if not exists
            existing_patient = (await db.execute(select(Patient).where(Patient.user_id == user.id))).scalar_one_or_none()
            if not existing_patient:
                db.add(Patient(user_id=user.id))
                print(f"  Created: {p['email']}")

        # Create doctors
        print("\n--- Creating Doctors ---")
        for d in DOCTORS:
            user = await create_user(db, d["email"], d["first"], d["last"], doctor_role)
            # Create patient profile (required by the system)
            existing_patient = (await db.execute(select(Patient).where(Patient.user_id == user.id))).scalar_one_or_none()
            if not existing_patient:
                db.add(Patient(user_id=user.id))
            # Create provider profile
            existing_provider = (await db.execute(select(Provider).where(Provider.user_id == user.id))).scalar_one_or_none()
            if not existing_provider:
                db.add(Provider(
                    user_id=user.id,
                    provider_type=d["type"],
                    speciality=d["speciality"],
                    years_experience=d["exp"],
                    consultation_fee=d["fee"],
                ))
                print(f"  Created: {d['email']} ({d['type']} - {d['speciality']})")

        # Promote admin
        if admin_role:
            print("\n--- Promoting Admin ---")
            admin_user = (await db.execute(select(User).where(User.email == ADMIN_EMAIL))).scalar_one_or_none()
            if admin_user:
                admin_user.role_id = admin_role.id
                print(f"  Promoted: {ADMIN_EMAIL}")
            else:
                print(f"  Not found: {ADMIN_EMAIL} (register first, then re-run)")

        await db.commit()

        print("\n=== Done! ===")
        print(f"Password for all demo accounts: {PASSWORD}")
        print(f"\nPatients ({len(PATIENTS)}):")
        for p in PATIENTS:
            print(f"  {p['email']}")
        print(f"\nDoctors ({len(DOCTORS)}):")
        for d in DOCTORS:
            print(f"  {d['email']} — {d['type']}, {d['speciality']}")
        print(f"\nAdmin: {ADMIN_EMAIL}")


asyncio.run(main())
