from typing import Dict, Optional

from app.application.ports.iq_repositories import IqSessionRepository
from app.domain.entities.iq_session import IqSession


class InMemoryIqSessionRepository(IqSessionRepository):
    """Repositorio en memoria de sesiones IQ (Infrastructure)."""

    def __init__(self) -> None:
        self._sessions: Dict[str, IqSession] = {}

    def save(self, session: IqSession) -> None:
        self._sessions[session.session_id] = session

    def get(self, session_id: str) -> Optional[IqSession]:
        return self._sessions.get(session_id)
