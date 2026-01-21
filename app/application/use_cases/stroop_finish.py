from typing import Dict

from app.domain.entities.stroop_session import StroopSession
from app.infrastructure.repositories.stroop_session_repository import InMemoryStroopSessionRepository


class FinishStroopUseCase:
    """Finaliza sesión y calcula score híbrido."""

    def __init__(self, repo: InMemoryStroopSessionRepository) -> None:
        self._repo = repo

    def execute(self, session_id: str) -> Dict:
        session = self._repo.get(session_id)
        if not session:
            return {"error": "invalid_session"}, 400
        session.finished = True
        result = self._score(session)
        self._repo.save(session)
        return result, 200

    def _score(self, session: StroopSession) -> Dict:
        if not session.answers:
            return {"score": 0, "profile": "Sin datos"}

        total = len(session.answers)
        incong = [a for a in session.answers if a.trial.trial_type == "incongruente"]
        cong = [a for a in session.answers if a.trial.trial_type == "congruente"]
        correct = sum(1 for a in session.answers if a.correct)
        correct_incong = sum(1 for a in incong if a.correct)
        accuracy_weighted = (correct + correct_incong * 0.2) / total

        def avg_rt(arr):
            vals = [a.rt_ms for a in arr if a.rt_ms > 0]
            return sum(vals) / len(vals) if vals else 0

        rt_incong = avg_rt(incong)
        rt_cong = avg_rt(cong)
        stroop_control = 1.0
        if rt_cong and rt_incong:
            diff = rt_incong - rt_cong
            stroop_control = max(0.0, min(1.0, 1 - diff / 800.0))

        switch_errors = sum(1 for a in session.answers if a.rule_changed_before and not a.correct)
        switch_trials = max(1, sum(1 for a in session.answers if a.rule_changed_before))
        flexibility = 1 - (switch_errors / switch_trials)

        impulse_errors = sum(1 for a in session.answers if (a.rt_ms < 2500 and not a.correct))
        impulse_trials = max(1, len(session.answers))
        impulse_control = 1 - (impulse_errors / impulse_trials)

        score = (
            0.40 * accuracy_weighted
            + 0.20 * stroop_control
            + 0.25 * flexibility
            + 0.15 * impulse_control
        ) * 100
        score = max(0, min(100, round(score, 1)))

        profile = self._profile(flexibility, stroop_control, impulse_control)
        return {"score": score, "profile": profile}

    def _profile(self, flexibility: float, stroop_control: float, impulse: float) -> str:
        if flexibility < 0.6:
            return "Buena inhibicion, baja flexibilidad ante cambios."
        if impulse < 0.7:
            return "Tendencia a responder rapido con errores bajo presion."
        if stroop_control < 0.7:
            return "Interferencia alta en estimulos incongruentes."
        return "Control atencional y flexibilidad estables."
