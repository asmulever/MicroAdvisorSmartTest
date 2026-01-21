import random
from typing import List, Tuple

from app.domain.entities.stroop_session import StroopAnswer, StroopSession, StroopTrial


class StroopEngine:
    """Genera trials y gestiona cambios de regla para el test Stroop-WCST híbrido."""

    COLORS = ["rojo", "verde", "azul", "amarillo"]
    OPPOSITE = {"rojo": "verde", "verde": "rojo", "azul": "amarillo", "amarillo": "azul"}

    def __init__(self) -> None:
        self.rule_cycle = ["ink", "word", "opposite"]
        self.change_threshold = 6  # aciertos antes de cambiar regla
        self.max_trials = 24

    def _pick_trial(self, rule: str) -> StroopTrial:
        trial_type = random.choices(["incongruente", "congruente", "neutro"], weights=[0.4, 0.4, 0.2])[0]
        word = random.choice(self.COLORS)
        ink = random.choice(self.COLORS)
        if trial_type == "congruente":
            ink = word
        elif trial_type == "incongruente":
            while ink == word:
                ink = random.choice(self.COLORS)
        else:  # neutro
            word = "XXXX"
        expected = self._expected_color(rule, word, ink)
        return StroopTrial(word=word, ink=ink, trial_type=trial_type, rule_id=rule, expected=expected)

    def _expected_color(self, rule: str, word: str, ink: str) -> str:
        if rule == "ink":
            return ink
        if rule == "word":
            return word if word in self.COLORS else ink
        if rule == "opposite":
            base = ink if word not in self.COLORS else word
            return self.OPPOSITE.get(base, base)
        return ink

    def start_session(self, session_id: str) -> Tuple[StroopSession, StroopTrial]:
        rule = "ink"
        session = StroopSession(session_id=session_id, current_rule=rule)
        trial = self._pick_trial(rule)
        return session, trial

    def next_trial(self, session: StroopSession) -> StroopTrial:
        if session.finished or session.total_trials >= self.max_trials:
            session.finished = True
            return None
        self._maybe_change_rule(session)
        return self._pick_trial(session.current_rule)

    def _maybe_change_rule(self, session: StroopSession) -> None:
        if session.correct_in_rule >= self.change_threshold:
            idx = self.rule_cycle.index(session.current_rule)
            next_idx = (idx + 1) % len(self.rule_cycle)
            session.current_rule = self.rule_cycle[next_idx]
            session.correct_in_rule = 0
            session.block_id += 1

    def register_answer(self, session: StroopSession, trial: StroopTrial, selected: str, rt_ms: int) -> StroopAnswer:
        correct = selected == trial.expected
        rule_changed_before = session.correct_in_rule == 0 and session.total_trials > 0
        answer = StroopAnswer(trial=trial, selected=selected, correct=correct, rt_ms=rt_ms, rule_changed_before=rule_changed_before)
        session.answers.append(answer)
        session.total_trials += 1
        if correct:
            session.correct_in_rule += 1
        return answer
