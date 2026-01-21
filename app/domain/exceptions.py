class DomainError(Exception):
    """Error de dominio genérico para reglas de negocio."""


class SessionNotFoundError(DomainError):
    """Sesión de IQ no encontrada."""


class InvalidAnswerError(DomainError):
    """Respuesta inválida para un ítem de IQ."""
