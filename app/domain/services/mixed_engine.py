import random
from typing import List

from app.domain.entities.mixed_session import MixedItem, MixedSession
from app.iq_items import get_item_pool
from app.domain.services.stroop_engine import StroopEngine


class MixedEngine:
    """Genera secuencia combinada IQ + Stroop para un test híbrido."""

    def __init__(self, stroop_engine: StroopEngine) -> None:
        self.stroop_engine = stroop_engine

    def build_session(self, session_id: str, iq_count: int = 10, stroop_count: int = 6) -> MixedSession:
        pool = get_item_pool()
        iq_items = random.sample(pool, min(iq_count, len(pool)))
        stroop_trials = [self.stroop_engine._pick_trial("ink") for _ in range(stroop_count // 2)]
        stroop_trials += [self.stroop_engine._pick_trial("word") for _ in range(stroop_count - len(stroop_trials))]

        mixed_items: List[MixedItem] = []
        idx_iq = 0
        idx_st = 0
        toggle = True
        while idx_iq < len(iq_items) or idx_st < len(stroop_trials):
            if toggle and idx_iq < len(iq_items):
                item = iq_items[idx_iq]
                mixed_items.append(
                    MixedItem(
                        item_id=item.item_id,
                        kind="iq",
                        payload={
                            "prompt": item.prompt,
                            "options": item.options,
                            "correct": item.correct,
                            "time_limit": 40,
                        },
                    )
                )
                idx_iq += 1
            elif idx_st < len(stroop_trials):
                trial = stroop_trials[idx_st]
                mixed_items.append(
                    MixedItem(
                        item_id=f"ST-{idx_st+1}",
                        kind="stroop",
                        payload={
                            "word": trial.word,
                            "ink": trial.ink,
                            "expected": trial.expected,
                        },
                    )
                )
                idx_st += 1
            toggle = not toggle

        session = MixedSession(session_id=session_id, items=mixed_items)
        session.iq_total = len([i for i in mixed_items if i.kind == "iq"])
        session.stroop_total = len([i for i in mixed_items if i.kind == "stroop"])
        return session

    def next_item(self, session: MixedSession):
        if session.finished or session.index >= len(session.items):
            session.finished = True
            return None
        return session.items[session.index]

    def register_answer(self, session: MixedSession, item: MixedItem, answer: str) -> bool:
        correct = False
        if item.kind == "iq":
            correct = answer == str(item.payload.get("correct"))
            if correct:
                session.iq_correct += 1
        else:
            correct = answer == str(item.payload.get("expected"))
            if correct:
                session.stroop_correct += 1
        session.index += 1
        if session.index >= len(session.items):
            session.finished = True
        return correct

    def finalize(self, session: MixedSession) -> dict:
        iq_pct = (session.iq_correct / session.iq_total) if session.iq_total else 0
        st_pct = (session.stroop_correct / session.stroop_total) if session.stroop_total else 0
        score = round((iq_pct * 0.5 + st_pct * 0.5) * 100, 1)
        return {
            "score": score,
            "iq_pct": round(iq_pct * 100, 1),
            "stroop_pct": round(st_pct * 100, 1),
        }
