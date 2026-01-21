from typing import Dict, List


class ListTestsUseCase:
    """Caso de uso: listar tests disponibles."""

    def execute(self) -> Dict:
        # Mantiene contrato actual.
        return {
            "tests": [
                {
                    "slug": "iq-general",
                    "title": "Test de IQ General",
                    "description": "Evaluacion cognitiva recreativa con seleccion semi-adaptativa.",
                    "lang": "es",
                    "is_active": True,
                    "published_version": 1,
                }
                ,
                {
                    "slug": "stroop-wcst",
                    "title": "Test de Colores (Stroop/WCST)",
                    "description": "Flexibilidad e inhibicion con reglas dinamicas y estimulos Stroop.",
                    "lang": "es",
                    "is_active": True,
                    "published_version": 1,
                    "url": "/stroop",
                },
                {
                    "slug": "iq-stroop-mixed",
                    "title": "Test Combinado IQ + Colores",
                    "description": "Bloques alternados IQ y Stroop con score 50/50.",
                    "lang": "es",
                    "is_active": True,
                    "published_version": 1,
                    "url": "/test-mixed",
                }
            ]
        }
