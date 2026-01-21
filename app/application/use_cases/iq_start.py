import time
import uuid
from dataclasses import asdict
from typing import Dict, List

from app.application.ports.iq_repositories import IqAnalyticsRepository, IqItemProvider, IqSessionRepository
from app.domain.entities.iq_item import IqItem
from app.domain.entities.iq_session import IqSession
from app.domain.services.iq_logic import IqSelectorService
from app.domain.value_objects.iq_config import IqConfig


class StartIqTestUseCase:
    """Caso de uso: iniciar test IQ."""

    def __init__(
        self,
        session_repo: IqSessionRepository,
        analytics_repo: IqAnalyticsRepository,
        item_provider: IqItemProvider,
        selector: IqSelectorService,
        scoring_mode: int,
        config: IqConfig,
    ) -> None:
        self._session_repo = session_repo
        self._analytics_repo = analytics_repo
        self._item_provider = item_provider
        self._selector = selector
        self._scoring_mode = scoring_mode
        self._config = config

    def execute(self, block_size: int) -> Dict:
        pool = self._item_provider.get_pool()
        session_id = str(uuid.uuid4())
        session = IqSession(
            session_id=session_id,
            started_at=time.time(),
            difficulty=3,
            score=0.0,
            answers_count=0,
            used_items=[],
            n_items=self._config.n_items,
            block_size=block_size,
            scoring_mode=self._scoring_mode,
        )

        self._analytics_repo.increment_start()

        remaining = session.n_items - session.answers_count
        block = self._selector.select_block(pool, session.difficulty, session.used_items, min(block_size, remaining))
        session.used_items.extend([item.item_id for item in block])
        self._session_repo.save(session)

        return {
            "session_id": session_id,
            "block": [self._serialize_item(item) for item in block],
            "config": asdict(self._config),
        }

    def _serialize_item(self, item: IqItem) -> Dict:
        return {
            "item_id": item.item_id,
            "domain": item.domain,
            "difficulty": item.difficulty,
            "prompt": item.prompt,
            "options": item.options,
            "time_limit": self._config.time_limits[item.difficulty],
            "visual": item.visual,
        }
