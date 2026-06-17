from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models.permission import Permission

PERMISSIONS = [
    {
        "name": "manage_users",
        "description": "Manage users"
    },
    {
        "name": "manage_roles",
        "description": "Manage roles"
    },
    {
        "name": "manage_permissions",
        "description": "Manage permissions"
    },
    {
        "name": "view_patients",
        "description": "View patients"
    },

    # Providers
    {
        "name": "manage_provider_profile",
        "description": "Manage own provider profile"
    },
    {
        "name": "view_providers",
        "description": "View providers"
    },
    {
    "name": "manage_providers",
    "description": "Manage providers"
    },

    # Labs
    {
        "name": "view_labs",
        "description": "View lab orders and lab results"
    },
    {
        "name": "create_lab_orders",
        "description": "Create lab orders"
    },
    {
        "name": "update_lab_orders",
        "description": "Update lab orders"
    },
    {
        "name": "create_lab_results",
        "description": "Create lab results"
    },

    # Optimization Programs
    {
        "name": "view_optimization_programs",
        "description": "View optimization programs"
    },
    {
        "name": "create_optimization_programs",
        "description": "Create optimization programs"
    },
    {
        "name": "update_optimization_programs",
        "description": "Update optimization programs"
    },
    {
        "name": "view_optimization_habits",
        "description": "View optimization habit protocols"
    },
    {
        "name": "create_optimization_habits",
        "description": "Create optimization habit protocols"
    },
    {
        "name": "update_optimization_habits",
        "description": "Update optimization habit protocols"
    },
    {
        "name": "view_habit_logs",
        "description": "View optimization habit logs"
    },
    {
        "name": "create_habit_logs",
        "description": "Create optimization habit logs"
    },
    {
        "name": "view_peptide_protocols",
        "description": "View peptide protocols"
    },
    {
        "name": "create_peptide_protocols",
        "description": "Create peptide protocols"
    },
    {
        "name": "update_peptide_protocols",
        "description": "Update peptide protocols"
    },
    {
        "name": "view_goals",
        "description": "View health goals"
    },
    {
        "name": "create_goals",
        "description": "Create health goals"
    },
    {
        "name": "update_goals",
        "description": "Update health goals"
    },
    {
        "name": "view_goal_progress",
        "description": "View goal progress"
    },
    {
        "name": "record_goal_progress",
        "description": "Record goal progress"
    },
    {
        "name": "view_documents",
        "description": "View documents"
    },
    {
        "name": "upload_documents",
        "description": "Upload documents"
    },
    {
        "name": "update_documents",
        "description": "Update document metadata"
    },
    {
        "name": "delete_documents",
        "description": "Soft delete documents"
    },
]


async def seed_permissions(
    db: AsyncSession
):

    for item in PERMISSIONS:

        result = await db.execute(
            select(Permission).where(
                Permission.name == item["name"]
            )
        )

        exists = result.scalar_one_or_none()

        if exists:
            continue

        permission = Permission(
            name=item["name"],
            description=item["description"]
        )

        db.add(permission)

    await db.commit()
