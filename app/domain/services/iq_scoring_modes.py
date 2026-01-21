import math
from dataclasses import dataclass
from typing import Dict

from app.domain.entities.iq_answer import IqAnswer
from app.domain.entities.iq_item import IqItem
from app.domain.entities.iq_session import IqSession


@dataclass(frozen=True)
class ScoringParams:
    eta: float
    t_guess: float
    time_k: float
    time_min: float
    time_max: float
    theta_scale: float
    weights_by_difficulty: Dict[int, float]
    t_ref_by_difficulty: Dict[int, float]


class IqScoringModesService:
    """Servicio de scoring multi-modo (0 simple, 1 ponderado, 2 IRT-lite)."""

    def __init__(self, params: ScoringParams, default_mode: int = 2) -> None:
        self._p = params
        self._mode = default_mode

    def set_mode(self, mode: int) -> None:
        if mode in (0, 1, 2):
            self._mode = mode

    def process_answer(self, session: IqSession, item: IqItem, answer: IqAnswer) -> None:
        correct = answer.answer == item.correct and not answer.timed_out
        session.answers_count += 1

        if self._mode in (0, 1):
            if correct:
                session.simple_corrects += 1
            weight = self._p.weights_by_difficulty.get(item.difficulty, 1.0)
            session.weighted_total += weight
            if correct:
                session.weighted_sum += weight

        if self._mode == 2:
            b = item.difficulty_b if item.difficulty_b is not None else 0.0
            theta = session.theta
            x = 1 if correct else 0
            P = 1 / (1 + math.exp(-(theta - b)))
            delta = self._p.eta * (x - P)

            t_ref = item.t_ref or self._p.t_ref_by_difficulty.get(item.difficulty, 10.0)
            seconds = answer.seconds if answer.seconds and answer.seconds > 0 else t_ref
            r = max(0.3, min(2.0, seconds / t_ref))
            time_factor = 1 - self._p.time_k * math.log(r)
            time_factor = max(self._p.time_min, min(self._p.time_max, time_factor))
            delta *= time_factor

            guessed = (seconds < self._p.t_guess) and (answer.changes == 0)
            if guessed:
                delta *= 0.65 if x == 1 else 1.10

            session.theta = theta + delta

    def finalize_scores(self, session: IqSession) -> Dict[str, float]:
        """Retorna score principal (0-100) y theta estimada."""
        if self._mode == 0:
            total = max(1, session.answers_count)
            score = (session.simple_corrects / total) * 100
            theta_est = (score - 50) / 15.0  # aproximación para IQ recreativo
        elif self._mode == 1:
            total_w = max(1e-6, session.weighted_total)
            score = (session.weighted_sum / total_w) * 100
            theta_est = (score - 50) / 18.0
        else:
            theta_est = session.theta
            score = round(100 * (1 / (1 + math.exp(-(theta_est / self._p.theta_scale)))))
        score = max(0.0, min(100.0, score))
        return {"score": score, "theta": theta_est}
