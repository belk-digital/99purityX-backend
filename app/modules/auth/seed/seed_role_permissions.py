from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models.role import Role
from app.modules.auth.models.permission import Permission
from app.modules.auth.models.role_permission import RolePermission


ROLE_PERMISSIONS = {
    "ADMIN": [
        "manage_users",
        "manage_roles",
        "manage_permissions",
        "view_patients",
        "create_consultation",
        "update_consultation",
        "manage_protocols",
        "manage_payments",
        "view_analytics",

        "manage_provider_profile",
        "view_providers",
        "manage_providers",

        "view_labs",
        "create_lab_orders",
        "update_lab_orders",
        "create_lab_results",

        "view_optimization_programs",
        "create_optimization_programs",
        "update_optimization_programs",

        "view_optimization_habits",
        "create_optimization_habits",
        "update_optimization_habits",
        "view_habit_logs",
        "create_habit_logs",

        "view_peptide_protocols",
        "create_peptide_protocols",
        "update_peptide_protocols",

        "view_goals",
        "create_goals",
        "update_goals",
        "view_goal_progress",
        "record_goal_progress",

        "view_documents",
        "upload_documents",
        "update_documents",
        "delete_documents",
    ],

    "DOCTOR": [
        "view_patients",
        "create_consultation",
        "update_consultation",
        "view_analytics",
        
        "manage_provider_profile",
        "view_providers",

        "view_labs",
        "create_lab_orders",
        "update_lab_orders",
        "create_lab_results",

        "view_optimization_programs",
        "create_optimization_programs",
        "update_optimization_programs",

        "view_optimization_habits",
        "create_optimization_habits",
        "update_optimization_habits",
        "view_habit_logs",

        "view_peptide_protocols",
        "create_peptide_protocols",
        "update_peptide_protocols",

        "view_goals",
        "create_goals",
        "update_goals",
        "view_goal_progress",
        "record_goal_progress",

        "view_documents",
        "upload_documents",
        "update_documents",
        "delete_documents",
    ],

    "PATIENT": [
        "view_providers",
        "view_labs",
        "view_optimization_programs",
        "view_optimization_habits",
        "view_habit_logs",
        "create_habit_logs",
        "view_peptide_protocols",
        "view_goals",
        "view_goal_progress",
        "view_analytics",
        "view_documents",
        "upload_documents",
        ],

    "NUTRITIONIST": [
        "manage_protocols",
        "view_analytics",
        
        "manage_provider_profile",
        "view_providers",

        "view_labs",
        "create_lab_orders",
        "update_lab_orders",
        "create_lab_results",

        "view_optimization_programs",
        "create_optimization_programs",
        "update_optimization_programs",

        "view_optimization_habits",
        "create_optimization_habits",
        "update_optimization_habits",
        "view_habit_logs",

        "view_peptide_protocols",
        "create_peptide_protocols",
        "update_peptide_protocols",

        "view_goals",
        "create_goals",
        "update_goals",
        "view_goal_progress",
        "record_goal_progress",

        "view_documents",
        "upload_documents",
        "update_documents",
        "delete_documents",
    ],

    "CARE_COORDINATOR": [
        "view_patients",
        
        "view_providers",
        "view_labs",
    ]
}


async def seed_role_permissions(
    db: AsyncSession
) -> None:

    for role_name, permissions in ROLE_PERMISSIONS.items():

        role_result = await db.execute(
            select(Role).where(
                Role.name == role_name
            )
        )

        role = role_result.scalar_one_or_none()

        if not role:
            continue

        for permission_name in permissions:

            permission_result = await db.execute(
                select(Permission).where(
                    Permission.name == permission_name
                )
            )

            permission = permission_result.scalar_one_or_none()

            if not permission:
                continue

            existing_result = await db.execute(
                select(RolePermission).where(
                    RolePermission.role_id == role.id,
                    RolePermission.permission_id == permission.id
                )
            )

            existing_mapping = (
                existing_result.scalar_one_or_none()
            )

            if existing_mapping:
                continue

            mapping = RolePermission(
                role_id=role.id,
                permission_id=permission.id
            )

            db.add(mapping)

    await db.commit()
