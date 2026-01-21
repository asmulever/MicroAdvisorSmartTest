from app.application.ports.support_services import DbHealthChecker


class InMemoryDbHealthChecker(DbHealthChecker):
    """Health checker sin BD; siempre reporta OK en entorno sin persistencia."""

    def check(self) -> bool:
        return True
