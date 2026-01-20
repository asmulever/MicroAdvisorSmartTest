from typing import List, Dict

TERMS = [
    ("Zorps", "Blins", "Craks"),
    ("Marns", "Tivels", "Gorps"),
    ("Luneks", "Vords", "Hapts"),
    ("Nerks", "Povels", "Siths"),
    ("Drelks", "Forns", "Mivens"),
]

WORDS = [
    "PARALELOGRAMO",
    "TRANSVERSAL",
    "ESTRATEGIA",
    "CONCIENCIA",
    "RESPONSABLE",
    "PERSPECTIVA",
]


def _matrix_item(item_id: str, difficulty: int, base: int) -> Dict:
    a = base
    b = base + 1
    c = base + 2
    prompt = (
        "Completa la matriz numerica:\n"
        f"{a} {b} {c}\n"
        f"{b} {c} {c + 1}\n"
        f"{c} {c + 1} ?"
    )
    correct = str(c + 2)
    options = [correct, str(c + 3), str(c + 1), str(c + 4)]
    return {
        "item_id": item_id,
        "domain": "matrix",
        "difficulty": difficulty,
        "prompt": prompt,
        "options": options,
        "correct": correct,
    }


def _logic_item(item_id: str, difficulty: int, terms: tuple) -> Dict:
    a, b, c = terms
    prompt = (
        f"Todos los {a} son {b}.\n"
        f"Algunos {b} son {c}.\n"
        "Entonces:"
    )
    options = [
        f"Todos los {c} son {a}",
        f"Algunos {c} pueden ser {a}",
        f"Ningun {c} es {a}",
        "No se puede determinar",
    ]
    correct = options[1]
    return {
        "item_id": item_id,
        "domain": "logic",
        "difficulty": difficulty,
        "prompt": prompt,
        "options": options,
        "correct": correct,
    }


def _numeric_item(item_id: str, difficulty: int, base: int) -> Dict:
    x = base
    a = base + 2
    b = base + 5
    prompt = f"Si {a}x + {b} = {a * x + b}, cuanto vale x?"
    correct = str(x)
    options = [correct, str(x + 1), str(max(1, x - 1)), str(x + 2)]
    return {
        "item_id": item_id,
        "domain": "numeric",
        "difficulty": difficulty,
        "prompt": prompt,
        "options": options,
        "correct": correct,
    }


def _attention_item(item_id: str, difficulty: int, word: str) -> Dict:
    target = "A"
    count = word.count(target)
    prompt = f"Cuantas veces aparece la letra {target}?\n{word}"
    correct = str(count)
    options = [correct, str(count + 1), str(max(0, count - 1)), str(count + 2)]
    return {
        "item_id": item_id,
        "domain": "attention",
        "difficulty": difficulty,
        "prompt": prompt,
        "options": options,
        "correct": correct,
    }


def get_item_pool() -> List[Dict]:
    items: List[Dict] = []
    item_index = 1
    for difficulty in range(1, 6):
        base = 2 + difficulty
        for i in range(4):
            items.append(_matrix_item(f"M{difficulty}-{i+1}", difficulty, base + i))
        for i in range(4):
            terms = TERMS[(difficulty + i) % len(TERMS)]
            items.append(_logic_item(f"L{difficulty}-{i+1}", difficulty, terms))
        for i in range(2):
            items.append(_numeric_item(f"N{difficulty}-{i+1}", difficulty, base + i))
        for i in range(2):
            word = WORDS[(difficulty + i) % len(WORDS)]
            items.append(_attention_item(f"A{difficulty}-{i+1}", difficulty, word))
        item_index += 1
    return items
