from typing import Dict, List, Sequence

from app.domain.entities.iq_answer import IqAnswer
from app.domain.entities.iq_item import IqItem
from app.domain.entities.iq_session import IqSession
from app.domain.exceptions import InvalidAnswerError
from app.domain.value_objects.iq_config import IqConfig
from app.domain.value_objects.iq_result import IqResult


class IqBandingService:
    """Lógica de bandas y etiquetas de IQ (dominio IQ)."""

    @staticmethod
    def band(iq_value: int) -> str:
        if iq_value < 90:
            return "<90"
        if iq_value <= 109:
            return "90-109"
        if iq_value <= 119:
            return "110-119"
        if iq_value <= 129:
            return "120-129"
        return ">=130"

    @staticmethod
    def label(iq_value: int) -> str:
        if iq_value < 90:
            return "Por debajo del promedio"
        if iq_value <= 109:
            return "Promedio"
        if iq_value <= 119:
            return "Por encima del promedio"
        if iq_value <= 129:
            return "Superior"
        return "Muy superior"


class IqSelectorService:
    """Selecciona bloques de ítems según la dificultad y disponibilidad."""

    def select_block(self, pool: Sequence[IqItem], difficulty: int, used_ids: List[str], count: int) -> List[IqItem]:
        candidates = [item for item in pool if item.difficulty == difficulty and item.item_id not in used_ids]
        if len(candidates) < count:
            for diff in (difficulty - 1, difficulty + 1):
                if diff < 1 or diff > 5:
                    continue
                extra = [item for item in pool if item.difficulty == diff and item.item_id not in used_ids]
                candidates.extend(extra)
                if len(candidates) >= count:
                    break
        return list(candidates[:count])


class IqScoringService:
    """Procesa respuestas y ajusta dificultad/puntaje."""

    def apply_answers(self, session: IqSession, answers: Sequence[IqAnswer], pool: Sequence[IqItem], config: IqConfig) -> None:
        pool_by_id: Dict[str, IqItem] = {item.item_id: item for item in pool}
        for answer in answers:
            item = pool_by_id.get(answer.item_id)
            if not item:
                # Ignora items desconocidos manteniendo compatibilidad con flujo actual.
                continue
            correct = (not answer.timed_out) and (answer.answer == item.correct)
            if correct:
                session.score += config.difficulty_weights.get(item.difficulty, 0)
            if correct and session.difficulty < 5:
                session.difficulty += 1
            elif (not correct) and session.difficulty > 1:
                session.difficulty -= 1


class IqResultService:
    """Construye resultados finales de IQ."""

    def __init__(self, banding_service: IqBandingService) -> None:
        self._banding = banding_service

    def build_result(self, session: IqSession, config: IqConfig, now_ts: float) -> IqResult:
        score = session.score
        iq_value = int(round(80 + (score / config.score_max) * 70))
        iq_value = max(80, min(150, iq_value))
        label = self._banding.label(iq_value)
        duration = int(now_ts - session.started_at)
        return IqResult(iq=iq_value, label=label, score=round(score, 2), duration_sec=duration)
