from typing import Dict, Optional

from app.domain.entities.stroop_session import StroopSession, StroopTrial


class InMemoryStroopSessionRepository:
    """Repositorio en memoria para sesiones Stroop-WCST."""

    def __init__(self) -> None:
        self._sessions: Dict[str, StroopSession] = {}
        self._pending_trial: Dict[str, StroopTrial] = {}

    def save(self, session: StroopSession) -> None:
        self._sessions[session.session_id] = session

    def get(self, session_id: str) -> Optional[StroopSession]:
        return self._sessions.get(session_id)

    def set_pending_trial(self, session_id: str, trial: Optional[StroopTrial]) -> None:
        if trial is None:
            self._pending_trial.pop(session_id, None)
        else:
            self._pending_trial[session_id] = trial

    def get_pending_trial(self, session_id: str) -> Optional[StroopTrial]:
        return self._pending_trial.get(session_id)
