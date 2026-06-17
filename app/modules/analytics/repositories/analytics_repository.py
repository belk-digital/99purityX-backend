from uuid import UUID

from sqlalchemy import desc, distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.analytics.models.patient_health_score_model import (
    PatientHealthScore,
)
from app.modules.analytics.models.program_analytics_model import (
    ProgramAnalytics,
)
from app.modules.analytics.models.provider_analytics_model import (
    ProviderAnalytics,
)
from app.modules.goals.enums.goal_enums import HealthGoalStatus
from app.modules.goals.models.health_goal_model import HealthGoal
from app.modules.labs.models.lab_order_model import LabOrder
from app.modules.labs.models.lab_result_model import LabResult
from app.modules.optimization.enums.program_enums import (
    HabitProtocolStatus,
    OptimizationProgramStatus,
)
from app.modules.optimization.models.habit_log_model import HabitLog
from app.modules.optimization.models.habit_protocol_model import HabitProtocol
from app.modules.optimization.models.optimization_program_model import (
    OptimizationProgram,
)
from app.modules.patients.models.patient_model import Patient
from app.modules.providers.models.provider_model import Provider


class AnalyticsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_patient_health_score(
        self,
        score: PatientHealthScore,
    ) -> PatientHealthScore:
        self.db.add(score)

        await self.db.flush()
        await self.db.refresh(score)

        return score

    async def create_provider_analytics(
        self,
        analytics: ProviderAnalytics,
    ) -> ProviderAnalytics:
        self.db.add(analytics)

        await self.db.flush()
        await self.db.refresh(analytics)

        return analytics

    async def create_program_analytics(
        self,
        analytics: ProgramAnalytics,
    ) -> ProgramAnalytics:
        self.db.add(analytics)

        await self.db.flush()
        await self.db.refresh(analytics)

        return analytics

    async def get_patient_by_id(self, patient_id: UUID) -> Patient | None:
        result = await self.db.execute(
            select(Patient).where(Patient.id == patient_id)
        )

        return result.scalar_one_or_none()

    async def get_provider_by_id(self, provider_id: UUID) -> Provider | None:
        result = await self.db.execute(
            select(Provider).where(Provider.id == provider_id)
        )

        return result.scalar_one_or_none()

    async def get_program_by_id(
        self,
        program_id: UUID,
    ) -> OptimizationProgram | None:
        result = await self.db.execute(
            select(OptimizationProgram)
            .options(
                selectinload(OptimizationProgram.patient),
                selectinload(OptimizationProgram.provider),
            )
            .where(OptimizationProgram.id == program_id)
        )

        return result.scalar_one_or_none()

    async def provider_has_patient(
        self,
        provider_id: UUID,
        patient_id: UUID,
    ) -> bool:
        result = await self.db.execute(
            select(OptimizationProgram.id).where(
                OptimizationProgram.provider_id == provider_id,
                OptimizationProgram.patient_id == patient_id,
            )
        )

        return result.scalar_one_or_none() is not None

    async def get_habit_log_counts_for_patient(
        self,
        patient_id: UUID,
    ) -> tuple[int, int]:
        total_result = await self.db.execute(
            select(func.count(HabitLog.id)).where(
                HabitLog.patient_id == patient_id
            )
        )
        completed_result = await self.db.execute(
            select(func.count(HabitLog.id)).where(
                HabitLog.patient_id == patient_id,
                HabitLog.completed.is_(True),
            )
        )

        return (
            int(total_result.scalar_one() or 0),
            int(completed_result.scalar_one() or 0),
        )

    async def get_goal_counts_for_patient(
        self,
        patient_id: UUID,
    ) -> tuple[int, int, int]:
        tracked_result = await self.db.execute(
            select(func.count(HealthGoal.id)).where(
                HealthGoal.patient_id == patient_id,
                HealthGoal.status != HealthGoalStatus.CANCELLED,
            )
        )
        active_result = await self.db.execute(
            select(func.count(HealthGoal.id)).where(
                HealthGoal.patient_id == patient_id,
                HealthGoal.status == HealthGoalStatus.ACTIVE,
            )
        )
        achieved_result = await self.db.execute(
            select(func.count(HealthGoal.id)).where(
                HealthGoal.patient_id == patient_id,
                HealthGoal.status == HealthGoalStatus.ACHIEVED,
            )
        )

        return (
            int(tracked_result.scalar_one() or 0),
            int(active_result.scalar_one() or 0),
            int(achieved_result.scalar_one() or 0),
        )

    async def get_active_program_count_for_patient(
        self,
        patient_id: UUID,
    ) -> int:
        result = await self.db.execute(
            select(func.count(OptimizationProgram.id)).where(
                OptimizationProgram.patient_id == patient_id,
                OptimizationProgram.status == OptimizationProgramStatus.ACTIVE,
            )
        )

        return int(result.scalar_one() or 0)

    async def get_lab_results_for_patient(
        self,
        patient_id: UUID,
    ) -> list[LabResult]:
        result = await self.db.execute(
            select(LabResult)
            .join(LabOrder)
            .options(selectinload(LabResult.lab_order))
            .where(LabOrder.patient_id == patient_id)
            .order_by(
                LabResult.biomarker_name.asc(),
                LabResult.recorded_at.desc(),
            )
        )

        return list(result.scalars().all())

    async def get_patient_ids_for_provider(
        self,
        provider_id: UUID,
    ) -> list[UUID]:
        result = await self.db.execute(
            select(distinct(OptimizationProgram.patient_id)).where(
                OptimizationProgram.provider_id == provider_id
            )
        )

        return list(result.scalars().all())

    async def get_active_program_count_for_provider(
        self,
        provider_id: UUID,
    ) -> int:
        result = await self.db.execute(
            select(func.count(OptimizationProgram.id)).where(
                OptimizationProgram.provider_id == provider_id,
                OptimizationProgram.status == OptimizationProgramStatus.ACTIVE,
            )
        )

        return int(result.scalar_one() or 0)

    async def get_completed_goal_count_for_provider(
        self,
        provider_id: UUID,
    ) -> int:
        result = await self.db.execute(
            select(func.count(HealthGoal.id)).where(
                HealthGoal.provider_id == provider_id,
                HealthGoal.status == HealthGoalStatus.ACHIEVED,
            )
        )

        return int(result.scalar_one() or 0)

    async def get_latest_patient_health_scores(
        self,
        patient_ids: list[UUID],
    ) -> list[PatientHealthScore]:
        scores: list[PatientHealthScore] = []

        for patient_id in patient_ids:
            result = await self.db.execute(
                select(PatientHealthScore)
                .where(PatientHealthScore.patient_id == patient_id)
                .order_by(desc(PatientHealthScore.calculated_at))
                .limit(1)
            )

            score = result.scalar_one_or_none()

            if score:
                scores.append(score)

        return scores

    async def get_habit_log_counts_for_provider(
        self,
        provider_id: UUID,
    ) -> tuple[int, int]:
        total_result = await self.db.execute(
            select(func.count(HabitLog.id))
            .join(HabitProtocol)
            .where(HabitProtocol.provider_id == provider_id)
        )
        completed_result = await self.db.execute(
            select(func.count(HabitLog.id))
            .join(HabitProtocol)
            .where(
                HabitProtocol.provider_id == provider_id,
                HabitLog.completed.is_(True),
            )
        )

        return (
            int(total_result.scalar_one() or 0),
            int(completed_result.scalar_one() or 0),
        )

    async def get_patient_ids_for_program(
        self,
        program_id: UUID,
    ) -> list[UUID]:
        result = await self.db.execute(
            select(distinct(OptimizationProgram.patient_id)).where(
                OptimizationProgram.id == program_id
            )
        )

        return list(result.scalars().all())

    async def get_habit_log_counts_for_program(
        self,
        program_id: UUID,
    ) -> tuple[int, int]:
        total_result = await self.db.execute(
            select(func.count(HabitLog.id))
            .join(HabitProtocol)
            .where(HabitProtocol.program_id == program_id)
        )
        completed_result = await self.db.execute(
            select(func.count(HabitLog.id))
            .join(HabitProtocol)
            .where(
                HabitProtocol.program_id == program_id,
                HabitLog.completed.is_(True),
            )
        )

        return (
            int(total_result.scalar_one() or 0),
            int(completed_result.scalar_one() or 0),
        )

    async def get_goal_counts_for_program(
        self,
        program_id: UUID,
    ) -> tuple[int, int]:
        total_result = await self.db.execute(
            select(func.count(HealthGoal.id)).where(
                HealthGoal.program_id == program_id,
                HealthGoal.status != HealthGoalStatus.CANCELLED,
            )
        )
        achieved_result = await self.db.execute(
            select(func.count(HealthGoal.id)).where(
                HealthGoal.program_id == program_id,
                HealthGoal.status == HealthGoalStatus.ACHIEVED,
            )
        )

        return (
            int(total_result.scalar_one() or 0),
            int(achieved_result.scalar_one() or 0),
        )
