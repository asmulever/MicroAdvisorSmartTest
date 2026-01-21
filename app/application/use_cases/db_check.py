from typing import Dict

from app.application.ports.support_services import DbHealthChecker


class DbCheckUseCase:
    """Caso de uso: verificación simple de BD."""

    def __init__(self, checker: DbHealthChecker) -> None:
        self._checker = checker

    def execute(self) -> Dict:
        ok = self._checker.check()
        if not ok:
            return {"db": "error"}
        return {"db": "ok", "select": 1}
