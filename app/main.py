import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.database import models

from app.modules.auth.api.routes import (
    router as auth_router,
)

from app.modules.audit.api.audit_routes import (
    router as audit_router,
)

from app.modules.patients.api.patient_routes import (
    router as patient_router,
)

from app.modules.providers.api.provider_routes import router as provider_router
from app.modules.appointments.api.appointment_routes import (
    router as appointment_router,
)
from app.modules.consultations.api.consultation_routes import (
    router as consultation_router,
)
from app.modules.labs.api.lab_routes import router as lab_router
from app.modules.optimization.api.program_routes import (
    router as optimization_router,
)
from app.modules.optimization.api.habit_routes import (
    router as optimization_habit_router,
)
from app.modules.optimization.api.peptide_routes import (
    router as peptide_router,
)
from app.modules.goals.api.goal_routes import router as goal_router
from app.modules.analytics.api.analytics_routes import (
    router as analytics_router,
)
from app.modules.documents.api.document_routes import (
    router as document_router,
)

app = FastAPI()

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(audit_router)
app.include_router(patient_router)
app.include_router(provider_router)
app.include_router(appointment_router)
app.include_router(consultation_router)
app.include_router(lab_router)
app.include_router(optimization_router)
app.include_router(optimization_habit_router)
app.include_router(peptide_router)
app.include_router(goal_router)
app.include_router(analytics_router)
app.include_router(document_router)
