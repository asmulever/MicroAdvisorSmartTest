from typing import List

from app.domain.entities.iq_item import IqItem


BETA_BY_DIFFICULTY = {1: -0.2, 2: 0.6, 3: 1.2, 4: 1.8, 5: 2.0}
TREF_BY_DIFFICULTY = {1: 8.0, 2: 10.0, 3: 12.0, 4: 14.0, 5: 14.0}


# Batería de 20 ítems: sistemas con reglas ocultas (bloques de dificultad 1-5).
SYSTEM_ITEMS = [
    # Bloque 1 – Deducción directa (5)
    {
        "id": "SYS1-1",
        "difficulty": 1,
        "prompt": (
            "Reglas:\n"
            "- Todo objeto tipo A activa B\n"
            "- Ningun objeto que activa B activa C\n\n"
            "Caso:\n"
            "Un objeto es tipo A.\n\n"
            "¿Que se puede afirmar?"
        ),
        "options": ["Activa C", "No activa C", "Activa B y C", "No se puede saber"],
        "correct": "No activa C",
    },
    {
        "id": "SYS1-2",
        "difficulty": 1,
        "prompt": (
            "Reglas:\n"
            "- Los objetos tipo D activan E\n"
            "- Algunos objetos que activan E activan F\n\n"
            "Caso:\n"
            "Un objeto es tipo D.\n\n"
            "Conclusión válida:"
        ),
        "options": ["Activa F", "No activa F", "Podría activar F", "No activa E"],
        "correct": "Podría activar F",
    },
    {
        "id": "SYS1-3",
        "difficulty": 1,
        "prompt": (
            "Reglas:\n"
            "- Todo objeto que activa X es estable\n"
            "- Ningun objeto inestable activa X\n\n"
            "Caso:\n"
            "Un objeto no es estable.\n\n"
            "¿Qué se deduce?"
        ),
        "options": ["Activa X", "No activa X", "Es inestable", "No se puede determinar"],
        "correct": "No activa X",
    },
    {
        "id": "SYS1-4",
        "difficulty": 1,
        "prompt": (
            "Reglas:\n"
            "- Todo objeto tipo P es tipo Q\n"
            "- Ningun objeto tipo Q es tipo R\n\n"
            "Caso:\n"
            "Un objeto es tipo P.\n\n"
            "Conclusión:"
        ),
        "options": ["Es tipo R", "No es tipo R", "Podría ser tipo R", "No se puede saber"],
        "correct": "No es tipo R",
    },
    {
        "id": "SYS1-5",
        "difficulty": 1,
        "prompt": (
            "Reglas:\n"
            "- Algunos objetos tipo M activan N\n"
            "- Todo objeto que activa N es detectable\n\n"
            "Caso:\n"
            "Un objeto es tipo M.\n\n"
            "Conclusión válida:"
        ),
        "options": ["Es detectable", "No es detectable", "Podría ser detectable", "No se puede saber"],
        "correct": "Podría ser detectable",
    },
    # Bloque 2 – Encadenamiento lógico (5)
    {
        "id": "SYS2-6",
        "difficulty": 2,
        "prompt": (
            "Reglas:\n"
            "- Todo objeto tipo A activa B\n"
            "- Todo objeto que activa B activa C\n"
            "- Ningun objeto que activa C es silencioso\n\n"
            "Caso:\n"
            "Un objeto es tipo A.\n\n"
            "¿Qué se puede afirmar?"
        ),
        "options": ["Es silencioso", "No es silencioso", "Podría ser silencioso", "No se puede saber"],
        "correct": "No es silencioso",
    },
    {
        "id": "SYS2-7",
        "difficulty": 2,
        "prompt": (
            "Reglas:\n"
            "- Todo objeto tipo K es rápido\n"
            "- Algunos objetos rápidos fallan\n\n"
            "Caso:\n"
            "Un objeto es tipo K.\n\n"
            "Conclusión válida:"
        ),
        "options": ["Falla", "No falla", "Podría fallar", "No se puede determinar"],
        "correct": "Podría fallar",
    },
    {
        "id": "SYS2-8",
        "difficulty": 2,
        "prompt": (
            "Reglas:\n"
            "- Todo objeto que falla es descartado\n"
            "- Ningun objeto estable es descartado\n\n"
            "Caso:\n"
            "Un objeto es estable.\n\n"
            "Conclusión:"
        ),
        "options": ["Falla", "No falla", "No es descartado", "No se puede saber"],
        "correct": "No es descartado",
    },
    {
        "id": "SYS2-9",
        "difficulty": 2,
        "prompt": (
            "Reglas:\n"
            "- Todo objeto tipo X activa Y\n"
            "- Todo objeto tipo Z activa Y\n"
            "- Ningun objeto que activa Y es pasivo\n\n"
            "Caso:\n"
            "Un objeto es tipo Z.\n\n"
            "Conclusión:"
        ),
        "options": ["Es pasivo", "No es pasivo", "Podría ser pasivo", "No se puede determinar"],
        "correct": "No es pasivo",
    },
    {
        "id": "SYS2-10",
        "difficulty": 2,
        "prompt": (
            "Reglas:\n"
            "- Algunos objetos tipo A son tipo B\n"
            "- Todo objeto tipo B es seguro\n\n"
            "Caso:\n"
            "Un objeto es tipo A.\n\n"
            "Conclusión válida:"
        ),
        "options": ["Es seguro", "No es seguro", "Podría ser seguro", "No se puede saber"],
        "correct": "Podría ser seguro",
    },
    # Bloque 3 – Ruido + control de hipótesis (5)
    {
        "id": "SYS3-11",
        "difficulty": 3,
        "prompt": (
            "Reglas:\n"
            "- Todo objeto tipo A activa B\n"
            "- Algunos objetos tipo C activan D\n"
            "- Ningun objeto que activa B activa E\n\n"
            "Caso:\n"
            "Un objeto es tipo A.\n\n"
            "Conclusión válida:"
        ),
        "options": ["Activa E", "No activa E", "Activa D", "No se puede saber"],
        "correct": "No activa E",
    },
    {
        "id": "SYS3-12",
        "difficulty": 3,
        "prompt": (
            "Reglas:\n"
            "- Todo objeto tipo X es confiable\n"
            "- Algunos objetos confiables son lentos\n"
            "- Ningun objeto lento es crítico\n\n"
            "Caso:\n"
            "Un objeto es tipo X.\n\n"
            "Conclusión válida:"
        ),
        "options": ["Es crítico", "No es crítico", "Podría no ser crítico", "No se puede determinar"],
        "correct": "Podría no ser crítico",
    },
    {
        "id": "SYS3-13",
        "difficulty": 3,
        "prompt": (
            "Reglas:\n"
            "- Todo objeto tipo P es Q\n"
            "- Algunos Q son R\n"
            "- Ningun R es S\n\n"
            "Caso:\n"
            "Un objeto es tipo P.\n\n"
            "Conclusión:"
        ),
        "options": ["Es S", "No es S", "Podría no ser S", "No se puede determinar"],
        "correct": "Podría no ser S",
    },
    {
        "id": "SYS3-14",
        "difficulty": 3,
        "prompt": (
            "Reglas:\n"
            "- Todo objeto tipo A activa B\n"
            "- Todo objeto tipo B activa C\n"
            "- Algunos objetos que activan C fallan\n\n"
            "Caso:\n"
            "Un objeto es tipo A.\n\n"
            "Conclusión válida:"
        ),
        "options": ["Falla", "No falla", "Podría fallar", "No se puede saber"],
        "correct": "Podría fallar",
    },
    {
        "id": "SYS3-15",
        "difficulty": 3,
        "prompt": (
            "Reglas:\n"
            "- Ningun objeto tipo M es N\n"
            "- Todo objeto tipo N es estable\n\n"
            "Caso:\n"
            "Un objeto no es estable.\n\n"
            "Conclusión válida:"
        ),
        "options": ["Es tipo N", "No es tipo N", "Es tipo M", "No se puede saber"],
        "correct": "No es tipo N",
    },
    # Bloque 4 – Detección de imposibilidad (5)
    {
        "id": "SYS4-16",
        "difficulty": 4,
        "prompt": (
            "Reglas:\n"
            "- Todo objeto tipo A activa B\n"
            "- Ningun objeto que activa B activa C\n"
            "- Todo objeto tipo A activa C\n\n"
            "¿Qué ocurre?"
        ),
        "options": ["Sistema válido", "Contradicción lógica", "Información incompleta", "No se puede determinar"],
        "correct": "Contradicción lógica",
    },
    {
        "id": "SYS4-17",
        "difficulty": 4,
        "prompt": (
            "Reglas:\n"
            "- Todo objeto tipo X es Y\n"
            "- Ningun objeto tipo Y es X\n\n"
            "Conclusión correcta:"
        ),
        "options": ["Es posible", "Es contradictorio solo si hay X", "Es contradictorio si existe algún X", "No se puede saber"],
        "correct": "Es contradictorio si existe algún X",
    },
    {
        "id": "SYS4-18",
        "difficulty": 4,
        "prompt": (
            "Reglas:\n"
            "- Todo objeto tipo A es B\n"
            "- Todo objeto tipo B es C\n"
            "- Ningun objeto tipo A es C\n\n"
            "Conclusión:"
        ),
        "options": ["Sistema válido", "Contradicción lógica", "Información incompleta", "No se puede determinar"],
        "correct": "Contradicción lógica",
    },
    {
        "id": "SYS4-19",
        "difficulty": 4,
        "prompt": (
            "Reglas:\n"
            "- Algunos objetos tipo M son N\n"
            "- Ningun objeto tipo N es M\n\n"
            "Conclusión:"
        ),
        "options": ["Contradicción", "Sistema válido", "Contradicción solo si hay M y N", "No se puede saber"],
        "correct": "Contradicción solo si hay M y N",
    },
    {
        "id": "SYS4-20",
        "difficulty": 4,
        "prompt": (
            "Reglas:\n"
            "- Todo objeto tipo A activa B\n"
            "- Todo objeto que activa B activa A\n\n"
            "Conclusión:"
        ),
        "options": ["Contradicción", "Sistema circular válido", "Información incompleta", "No se puede determinar"],
        "correct": "Sistema circular válido",
    },
]

# Ítems visuales tipo matriz/raven simplificados (SVG) para variedad.
MATRIX_VISUAL_ITEMS = [
    {
        "id": "MV-1",
        "difficulty": 2,
        "prompt": "Completa la grilla: sigue el patrón de cruces alternadas.",
        "visual": {"base": {"src": "/static/images/matrix/mv1-base.svg", "alt": "Patron de cruces"}},
        "options": [
            {"value": "mv1-a", "image": "/static/images/matrix/mv1-a.svg"},
            {"value": "mv1-b", "image": "/static/images/matrix/mv1-b.svg"},
            {"value": "mv1-c", "image": "/static/images/matrix/mv1-c.svg"},
            {"value": "mv1-d", "image": "/static/images/matrix/mv1-d.svg"},
        ],
        "correct": "mv1-a",
    },
    {
        "id": "MV-2",
        "difficulty": 3,
        "prompt": "Completa la grilla: respeta la alternancia de diamantes y espacios.",
        "visual": {"base": {"src": "/static/images/matrix/mv2-base.svg", "alt": "Diamantes alternados"}},
        "options": [
            {"value": "mv2-a", "image": "/static/images/matrix/mv2-a.svg"},
            {"value": "mv2-b", "image": "/static/images/matrix/mv2-b.svg"},
            {"value": "mv2-c", "image": "/static/images/matrix/mv2-c.svg"},
            {"value": "mv2-d", "image": "/static/images/matrix/mv2-d.svg"},
        ],
        "correct": "mv2-a",
    },
    {
        "id": "MV-3",
        "difficulty": 4,
        "prompt": "Completa la grilla: rota y desplaza el símbolo en diagonal.",
        "visual": {"base": {"src": "/static/images/matrix/mv3-base.svg", "alt": "Patron diagonal"}},
        "options": [
            {"value": "mv3-a", "image": "/static/images/matrix/mv3-a.svg"},
            {"value": "mv3-b", "image": "/static/images/matrix/mv3-b.svg"},
            {"value": "mv3-c", "image": "/static/images/matrix/mv3-c.svg"},
            {"value": "mv3-d", "image": "/static/images/matrix/mv3-d.svg"},
        ],
        "correct": "mv3-a",
    },
]


def get_item_pool() -> List[IqItem]:
    """Devuelve el pool fijo de ítems (sistemas lógicos + matrices visuales)."""
    items: List[IqItem] = []
    for spec in SYSTEM_ITEMS:
        items.append(
            IqItem(
                item_id=spec["id"],
                domain="system-logic",
                difficulty=spec["difficulty"],
                prompt=spec["prompt"],
                options=spec["options"],
                correct=spec["correct"],
                difficulty_b=BETA_BY_DIFFICULTY.get(spec["difficulty"], 0.0),
                t_ref=TREF_BY_DIFFICULTY.get(spec["difficulty"], 10.0),
            )
        )
    for spec in MATRIX_VISUAL_ITEMS:
        items.append(
            IqItem(
                item_id=spec["id"],
                domain="matrix-visual",
                difficulty=spec["difficulty"],
                prompt=spec["prompt"],
                options=spec["options"],
                correct=spec["correct"],
                visual=spec.get("visual"),
                difficulty_b=BETA_BY_DIFFICULTY.get(spec["difficulty"], 0.0),
                t_ref=TREF_BY_DIFFICULTY.get(spec["difficulty"], 10.0),
            )
        )
    return items
