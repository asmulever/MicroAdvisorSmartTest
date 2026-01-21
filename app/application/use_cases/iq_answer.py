from typing import Dict, List, Sequence

from app.application.ports.iq_repositories import IqItemProvider, IqSessionRepository
from app.domain.entities.iq_answer import IqAnswer
from app.domain.entities.iq_item import IqItem
from app.domain.entities.iq_session import IqSession
from app.domain.exceptions import SessionNotFoundError
from app.domain.services.iq_logic import IqSelectorService, IqScoringService
from app.domain.services.iq_scoring_modes import IqScoringModesService
from app.domain.value_objects.iq_config import IqConfig


class AnswerIqBlockUseCase:
    """Caso de uso: responder un bloque de ítems IQ."""

    def __init__(
        self,
        session_repo: IqSessionRepository,
        item_provider: IqItemProvider,
        selector: IqSelectorService,
        scorer: IqScoringService,
        scorer_modes: IqScoringModesService,
        config: IqConfig,
    ) -> None:
        self._session_repo = session_repo
        self._item_provider = item_provider
        self._selector = selector
        self._scorer = scorer
        self._scorer_modes = scorer_modes
        self._config = config

    def execute(self, session_id: str, answers: Sequence[IqAnswer]) -> Dict:
        session = self._session_repo.get(session_id)
        if not session:
            raise SessionNotFoundError(session_id)

        pool = self._item_provider.get_pool()
        for answer in answers:
            item = next((it for it in pool if it.item_id == answer.item_id), None)
            if item:
                self._scorer_modes.process_answer(session, item, answer)
        # Scoring adaptativo previo (mantener dificultad/puntaje legacy)
        self._scorer.apply_answers(session, answers, pool, self._config)

        if session.answers_count >= session.n_items:
            self._session_repo.save(session)
            return {"done": True}

        remaining = session.n_items - session.answers_count
        block = self._selector.select_block(pool, session.difficulty, session.used_items, min(session.block_size, remaining))
        if not block:
            self._session_repo.save(session)
            return {"done": True}

        session.used_items.extend([item.item_id for item in block])
        self._session_repo.save(session)
        return {"done": False, "block": [self._serialize_item(item) for item in block]}

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
