from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from fastapi import HTTPException, status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.analytics.models.patient_health_score_model import (
    PatientHealthScore,
)
from app.modules.analytics.models.program_analytics_model import (
    ProgramAnalytics,
)
from app.modules.analytics.models.provider_analytics_model import (
    ProviderAnalytics,
)
from app.modules.analytics.repositories.analytics_repository import (
    AnalyticsRepository,
)
from app.modules.analytics.schemas.analytics_schema import (
    PatientAnalyticsResponse,
)
from app.modules.labs.models.lab_result_model import LabResult


class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = AnalyticsRepository(db)

    @staticmethod
    def _is_admin(current_user) -> bool:
        return bool(
            current_user.role
            and current_user.role.name == "ADMIN"
        )

    @staticmethod
    def _provider_id(current_user):
        if current_user.provider_profile:
            return current_user.provider_profile.id

        return None

    @staticmethod
    def _patient_id(current_user):
        if current_user.patient:
            return current_user.patient.id

        return None

    @staticmethod
    def _score(value: float) -> Decimal:
        bounded = max(0.0, min(100.0, value))

        return Decimal(str(bounded)).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

    @staticmethod
    def _percentage(
        numerator: int,
        denominator: int,
    ) -> Decimal:
        if denominator <= 0:
            return Decimal("0.00")

        return AnalyticsService._score(
            (numerator / denominator) * 100
        )

    async def _validate_patient_analytics_access(
        self,
        patient_id: UUID,
        current_user,
    ) -> None:
        if self._is_admin(current_user):
            return

        current_patient_id = self._patient_id(current_user)

        if current_patient_id and current_patient_id == patient_id:
            return

        provider_id = self._provider_id(current_user)

        if provider_id:
            has_patient = await self.repository.provider_has_patient(
                provider_id=provider_id,
                patient_id=patient_id,
            )

            if has_patient:
                return

        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Unauthorized analytics access",
        )

    async def _validate_provider_analytics_access(
        self,
        provider_id: UUID,
        current_user,
    ) -> None:
        if self._is_admin(current_user):
            return

        current_provider_id = self._provider_id(current_user)

        if current_provider_id and current_provider_id == provider_id:
            return

        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Unauthorized provider analytics access",
        )

    async def _validate_program_analytics_access(
        self,
        program_id: UUID,
        current_user,
    ) -> None:
        program = await self.repository.get_program_by_id(program_id)

        if not program:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Optimization program not found",
            )

        if self._is_admin(current_user):
            return

        provider_id = self._provider_id(current_user)

        if provider_id and program.provider_id == provider_id:
            return

        patient_id = self._patient_id(current_user)

        if patient_id and program.patient_id == patient_id:
            return

        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Unauthorized program analytics access",
        )

    @staticmethod
    def _calculate_biomarker_score(
        lab_results: list[LabResult],
    ) -> Decimal:
        latest_by_biomarker: dict[str, LabResult] = {}

        for result in lab_results:
            if result.biomarker_name not in latest_by_biomarker:
                latest_by_biomarker[result.biomarker_name] = result

        if not latest_by_biomarker:
            return Decimal("0.00")

        scores: list[float] = []

        for result in latest_by_biomarker.values():
            value = float(result.value)

            if (
                result.reference_min is None
                or result.reference_max is None
            ):
                scores.append(50.0)
                continue

            reference_min = float(result.reference_min)
            reference_max = float(result.reference_max)

            if reference_min <= value <= reference_max:
                scores.append(100.0)
                continue

            reference_width = max(reference_max - reference_min, 1.0)

            if value < reference_min:
                distance = reference_min - value
            else:
                distance = value - reference_max

            scores.append(
                max(0.0, 100.0 - ((distance / reference_width) * 100))
            )

        return AnalyticsService._score(sum(scores) / len(scores))

    async def calculate_patient_health_score(
        self,
        patient_id: UUID,
        current_user,
    ) -> PatientHealthScore:
        patient = await self.repository.get_patient_by_id(patient_id)

        if not patient:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Patient not found",
            )

        await self._validate_patient_analytics_access(
            patient_id,
            current_user,
        )

        total_logs, completed_logs = (
            await self.repository.get_habit_log_counts_for_patient(
                patient_id
            )
        )
        tracked_goals, _, achieved_goals = (
            await self.repository.get_goal_counts_for_patient(patient_id)
        )
        lab_results = await self.repository.get_lab_results_for_patient(
            patient_id
        )

        adherence_score = self._percentage(
            completed_logs,
            total_logs,
        )
        goal_score = self._percentage(
            achieved_goals,
            tracked_goals,
        )
        biomarker_score = self._calculate_biomarker_score(lab_results)
        overall_score = self._score(
            (float(adherence_score) * 0.40)
            + (float(goal_score) * 0.35)
            + (float(biomarker_score) * 0.25)
        )

        score = PatientHealthScore(
            patient_id=patient_id,
            overall_score=overall_score,
            adherence_score=adherence_score,
            biomarker_score=biomarker_score,
            goal_score=goal_score,
            calculated_at=datetime.now(timezone.utc),
        )

        score = await self.repository.create_patient_health_score(score)

        await self.db.commit()
        await self.db.refresh(score)

        return score

    async def get_patient_analytics(
        self,
        patient_id: UUID,
        current_user,
    ) -> PatientAnalyticsResponse:
        health_score = await self.calculate_patient_health_score(
            patient_id=patient_id,
            current_user=current_user,
        )

        active_programs = (
            await self.repository.get_active_program_count_for_patient(
                patient_id
            )
        )
        total_logs, completed_logs = (
            await self.repository.get_habit_log_counts_for_patient(
                patient_id
            )
        )
        _, active_goals, completed_goals = (
            await self.repository.get_goal_counts_for_patient(patient_id)
        )

        return PatientAnalyticsResponse(
            health_score=health_score,
            active_programs=active_programs,
            active_goals=active_goals,
            completed_goals=completed_goals,
            habit_logs=total_logs,
            completed_habit_logs=completed_logs,
        )

    async def calculate_provider_analytics(
        self,
        provider_id: UUID,
        current_user,
    ) -> ProviderAnalytics:
        provider = await self.repository.get_provider_by_id(provider_id)

        if not provider:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Provider not found",
            )

        await self._validate_provider_analytics_access(
            provider_id,
            current_user,
        )

        patient_ids = await self.repository.get_patient_ids_for_provider(
            provider_id
        )
        total_logs, completed_logs = (
            await self.repository.get_habit_log_counts_for_provider(
                provider_id
            )
        )
        active_programs = (
            await self.repository.get_active_program_count_for_provider(
                provider_id
            )
        )
        completed_goals = (
            await self.repository.get_completed_goal_count_for_provider(
                provider_id
            )
        )

        health_scores = []

        for patient_id in patient_ids:
            score = await self.calculate_patient_health_score(
                patient_id=patient_id,
                current_user=current_user,
            )
            health_scores.append(float(score.overall_score))

        average_health_score = (
            self._score(sum(health_scores) / len(health_scores))
            if health_scores
            else Decimal("0.00")
        )

        analytics = ProviderAnalytics(
            provider_id=provider_id,
            active_patients=len(patient_ids),
            active_programs=active_programs,
            completed_goals=completed_goals,
            average_adherence=self._percentage(
                completed_logs,
                total_logs,
            ),
            average_health_score=average_health_score,
            calculated_at=datetime.now(timezone.utc),
        )

        analytics = await self.repository.create_provider_analytics(
            analytics
        )

        await self.db.commit()
        await self.db.refresh(analytics)

        return analytics

    async def calculate_program_analytics(
        self,
        program_id: UUID,
        current_user,
    ) -> ProgramAnalytics:
        await self._validate_program_analytics_access(
            program_id,
            current_user,
        )

        patient_ids = await self.repository.get_patient_ids_for_program(
            program_id
        )
        total_logs, completed_logs = (
            await self.repository.get_habit_log_counts_for_program(
                program_id
            )
        )
        total_goals, achieved_goals = (
            await self.repository.get_goal_counts_for_program(program_id)
        )

        health_scores = []

        for patient_id in patient_ids:
            score = await self.calculate_patient_health_score(
                patient_id=patient_id,
                current_user=current_user,
            )
            health_scores.append(float(score.overall_score))

        average_health_score = (
            self._score(sum(health_scores) / len(health_scores))
            if health_scores
            else Decimal("0.00")
        )

        analytics = ProgramAnalytics(
            program_id=program_id,
            enrolled_patients=len(patient_ids),
            average_adherence=self._percentage(
                completed_logs,
                total_logs,
            ),
            goal_completion_rate=self._percentage(
                achieved_goals,
                total_goals,
            ),
            average_health_score=average_health_score,
            calculated_at=datetime.now(timezone.utc),
        )

        analytics = await self.repository.create_program_analytics(
            analytics
        )

        await self.db.commit()
        await self.db.refresh(analytics)

        return analytics
