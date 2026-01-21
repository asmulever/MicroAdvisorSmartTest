"""AppFactory + contenedor DI simple para APB (monolito)."""

from app.application.use_cases.analytics import (
    GetAnalyticsDropoffUseCase,
    GetAnalyticsFunnelUseCase,
    GetAnalyticsProfilesUseCase,
    GetAnalyticsSummaryUseCase,
)
from app.application.use_cases.db_check import DbCheckUseCase
from app.application.use_cases.iq_answer import AnswerIqBlockUseCase
from app.application.use_cases.iq_finish import FinishIqTestUseCase
from app.application.use_cases.iq_start import StartIqTestUseCase
from app.application.use_cases.tests_catalog import ListTestsUseCase
from app.application.use_cases.tip_today import GetTipTodayUseCase
from app.application.use_cases.mixed_start import StartMixedUseCase
from app.application.use_cases.mixed_answer import AnswerMixedUseCase
from app.application.use_cases.mixed_finish import FinishMixedUseCase
from app.application.use_cases.stroop_start import StartStroopUseCase
from app.application.use_cases.stroop_answer import AnswerStroopUseCase
from app.application.use_cases.stroop_finish import FinishStroopUseCase
import os

from app.domain.services.iq_logic import IqBandingService, IqResultService, IqScoringService, IqSelectorService
from app.domain.services.iq_scoring_modes import IqScoringModesService, ScoringParams
from app.domain.services.stroop_engine import StroopEngine
from app.domain.services.mixed_engine import MixedEngine
from app.domain.value_objects.iq_config import IqConfig
from app.infrastructure.providers.static_iq_item_provider import StaticIqItemProvider
from app.infrastructure.providers.static_tip_provider import StaticTipProvider
from app.infrastructure.repositories.in_memory_analytics_repository import InMemoryIqAnalyticsRepository
from app.infrastructure.repositories.in_memory_session_repository import InMemoryIqSessionRepository
from app.infrastructure.repositories.stroop_session_repository import InMemoryStroopSessionRepository
from app.infrastructure.repositories.mixed_session_repository import InMemoryMixedSessionRepository
from app.infrastructure.services.db_health_checker import InMemoryDbHealthChecker


class AppContainer:
    """Container/IoC básico para instanciar casos de uso y dependencias."""

    def __init__(self) -> None:
        self.iq_config = IqConfig(
            n_items=20,
            score_max=45.0,
            difficulty_weights={1: 1.0, 2: 1.5, 3: 2.0, 4: 2.5, 5: 3.0},
            time_limits={1: 25, 2: 25, 3: 35, 4: 45, 5: 55},
        )
        self.session_repo = InMemoryIqSessionRepository()
        self.analytics_repo = InMemoryIqAnalyticsRepository()
        self.item_provider = StaticIqItemProvider()
        self.tip_provider = StaticTipProvider()
        self.db_checker = InMemoryDbHealthChecker()
        self.stroop_repo = InMemoryStroopSessionRepository()
        self.mixed_repo = InMemoryMixedSessionRepository()

        # Servicios de dominio compartidos.
        self.selector = IqSelectorService()
        self.scorer = IqScoringService()
        self.banding = IqBandingService()
        self.result_service = IqResultService(self.banding)
        self.stroop_engine = StroopEngine()
        self.mixed_engine = MixedEngine(self.stroop_engine)
        self.scoring_mode = int(os.getenv("SCORING_MODE", "2"))
        self.scorer_modes = IqScoringModesService(
            ScoringParams(
                eta=0.35,
                t_guess=2.5,
                time_k=0.12,
                time_min=0.80,
                time_max=1.08,
                theta_scale=1.2,
                weights_by_difficulty={1: 1.0, 2: 1.3, 3: 1.6, 4: 2.0, 5: 2.0},
                t_ref_by_difficulty={1: 8.0, 2: 10.0, 3: 12.0, 4: 14.0, 5: 14.0},
            ),
            default_mode=2,
        )
        self.scorer_modes.set_mode(self.scoring_mode)

    # Factories de casos de uso
    def get_start_iq(self) -> StartIqTestUseCase:
        return StartIqTestUseCase(
            session_repo=self.session_repo,
            analytics_repo=self.analytics_repo,
            item_provider=self.item_provider,
            selector=self.selector,
            scoring_mode=self.scoring_mode,
            config=self.iq_config,
        )

    def get_answer_iq(self) -> AnswerIqBlockUseCase:
        return AnswerIqBlockUseCase(
            session_repo=self.session_repo,
            item_provider=self.item_provider,
            selector=self.selector,
            scorer=self.scorer,
            scorer_modes=self.scorer_modes,
            config=self.iq_config,
        )

    def get_finish_iq(self) -> FinishIqTestUseCase:
        return FinishIqTestUseCase(
            session_repo=self.session_repo,
            analytics_repo=self.analytics_repo,
            banding_service=self.banding,
            scorer_modes=self.scorer_modes,
            config=self.iq_config,
        )

    def get_analytics_summary(self) -> GetAnalyticsSummaryUseCase:
        return GetAnalyticsSummaryUseCase(self.analytics_repo)

    def get_analytics_funnel(self) -> GetAnalyticsFunnelUseCase:
        return GetAnalyticsFunnelUseCase(self.analytics_repo)

    def get_analytics_profiles(self) -> GetAnalyticsProfilesUseCase:
        return GetAnalyticsProfilesUseCase(self.analytics_repo)

    def get_analytics_dropoff(self) -> GetAnalyticsDropoffUseCase:
        return GetAnalyticsDropoffUseCase()

    def get_list_tests(self) -> ListTestsUseCase:
        return ListTestsUseCase()

    def get_tip_today(self) -> GetTipTodayUseCase:
        return GetTipTodayUseCase(self.tip_provider)

    def get_db_check(self) -> DbCheckUseCase:
        return DbCheckUseCase(self.db_checker)

    # Stroop/WCST híbrido
    def get_stroop_start(self) -> StartStroopUseCase:
        return StartStroopUseCase(self.stroop_repo, self.stroop_engine)

    def get_stroop_answer(self) -> AnswerStroopUseCase:
        return AnswerStroopUseCase(self.stroop_repo, self.stroop_engine)

    def get_stroop_finish(self) -> FinishStroopUseCase:
        return FinishStroopUseCase(self.stroop_repo)

    # Mixto IQ + Stroop
    def get_mixed_start(self) -> StartMixedUseCase:
        return StartMixedUseCase(self.mixed_repo, self.mixed_engine)

    def get_mixed_answer(self) -> AnswerMixedUseCase:
        return AnswerMixedUseCase(self.mixed_repo, self.mixed_engine)

    def get_mixed_finish(self) -> FinishMixedUseCase:
        return FinishMixedUseCase(self.mixed_repo, self.mixed_engine)
