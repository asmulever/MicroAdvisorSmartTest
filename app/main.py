import logging
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from app.db import SessionLocal
from app.iq_items import get_item_pool

app = FastAPI(title="Micro-Advisor API", version="0.1.0")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "Frontend"
STATIC_DIR = FRONTEND_DIR

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

NO_CACHE_HEADERS = {
    "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
    "Pragma": "no-cache",
    "Expires": "0",
}

IQ_CONFIG = {
    "n_items": 20,
    "score_max": 45.0,
    "difficulty_weights": {1: 1.0, 2: 1.5, 3: 2.0, 4: 2.5, 5: 3.0},
    "time_limits": {1: 25, 2: 25, 3: 35, 4: 45, 5: 55},
}

IQ_SESSIONS = {}
IQ_ANALYTICS = {
    "starts": 0,
    "finishes": 0,
    "total_time_sec": 0,
    "iq_bands": {
        "<90": 0,
        "90-109": 0,
        "110-119": 0,
        "120-129": 0,
        ">=130": 0,
    },
}


def _iq_band(iq_value: int) -> str:
    if iq_value < 90:
        return "<90"
    if iq_value <= 109:
        return "90-109"
    if iq_value <= 119:
        return "110-119"
    if iq_value <= 129:
        return "120-129"
    return ">=130"


def _iq_label(iq_value: int) -> str:
    if iq_value < 90:
        return "Por debajo del promedio"
    if iq_value <= 109:
        return "Promedio"
    if iq_value <= 119:
        return "Por encima del promedio"
    if iq_value <= 129:
        return "Superior"
    return "Muy superior"


def _select_items(pool, difficulty, used_ids, count):
    candidates = [item for item in pool if item["difficulty"] == difficulty and item["item_id"] not in used_ids]
    if len(candidates) < count:
        for diff in (difficulty - 1, difficulty + 1):
            if diff < 1 or diff > 5:
                continue
            extra = [item for item in pool if item["difficulty"] == diff and item["item_id"] not in used_ids]
            candidates.extend(extra)
            if len(candidates) >= count:
                break
    return candidates[:count]


def _serialize_item(item):
    return {
        "item_id": item["item_id"],
        "domain": item["domain"],
        "difficulty": item["difficulty"],
        "prompt": item["prompt"],
        "options": item["options"],
        "time_limit": IQ_CONFIG["time_limits"][item["difficulty"]],
    }


def _render_view(filename: str):
    try:
        html_path = FRONTEND_DIR / filename
        html = html_path.read_text(encoding="utf-8")
        return HTMLResponse(content=html, headers=NO_CACHE_HEADERS)
    except Exception as exc:
        logger.info("view_error_%s: %s", filename, exc)
        return JSONResponse(status_code=500, content={"error": "internal_error"})


@app.middleware("http")
async def no_cache_static_headers(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static"):
        response.headers.update(NO_CACHE_HEADERS)
    return response

@app.get("/")
def root():
    return _render_view("index.html")


@app.get("/test")
def test_view():
    return _render_view("test.html")


@app.get("/favicon.ico")
def favicon():
    return JSONResponse(status_code=404, content={"error": "not_found"})


@app.get("/resultado")
def resultado_view():
    return _render_view("resultado.html")


@app.get("/analitica")
def analitica_view():
    return _render_view("analitica.html")



@app.get("/health")
def health():
    try:
        return {"ok": True}
    except Exception as exc:
        logger.info("health_error: %s", exc)
        return JSONResponse(status_code=500, content={"error": "internal_error"})

@app.get("/db-check")
def db_check():
    try:
        with SessionLocal() as db:
            v = db.execute(text("select 1")).scalar_one()
        return {"db": "ok", "select": v}
    except Exception as exc:
        logger.info("db_check_error: %s", exc)
        return JSONResponse(status_code=500, content={"error": "internal_error"})

@app.get("/api/tests")
def list_tests():
    try:
        return {"tests": [{
            "slug": "iq-general",
            "title": "Test de IQ General",
            "description": "Evaluacion cognitiva recreativa con seleccion semi-adaptativa.",
            "lang": "es",
            "is_active": True,
            "published_version": 1,
        }]}
    except Exception as exc:
        logger.info("list_tests_error: %s", exc)
        return JSONResponse(status_code=500, content={"error": "internal_error"})


@app.get("/api/analytics/summary")
def analytics_summary(days: int = Query(7, ge=1, le=365)):
    try:
        starts = IQ_ANALYTICS["starts"]
        finishes = IQ_ANALYTICS["finishes"]
        finish_rate = (finishes / starts) if starts else 0
        avg_time = (IQ_ANALYTICS["total_time_sec"] / finishes) if finishes else 0

        return {
            "active_tests": 1,
            "finish_rate": round(finish_rate * 100, 1),
            "avg_time_sec": int(avg_time),
        }
    except Exception as exc:
        logger.info("analytics_summary_error: %s", exc)
        return JSONResponse(status_code=500, content={"error": "internal_error"})


@app.get("/api/analytics/funnel")
def analytics_funnel(days: int = Query(7, ge=1, le=365)):
    try:
        labels = ["Start", "Finish"]
        values = [IQ_ANALYTICS["starts"], IQ_ANALYTICS["finishes"]]
        return {"labels": labels, "values": values}
    except Exception as exc:
        logger.info("analytics_funnel_error: %s", exc)
        return JSONResponse(status_code=500, content={"error": "internal_error"})


@app.get("/api/analytics/profiles")
def analytics_profiles(days: int = Query(7, ge=1, le=365)):
    try:
        labels = list(IQ_ANALYTICS["iq_bands"].keys())
        values = [IQ_ANALYTICS["iq_bands"][label] for label in labels]
        return {"labels": labels, "values": values}
    except Exception as exc:
        logger.info("analytics_profiles_error: %s", exc)
        return JSONResponse(status_code=500, content={"error": "internal_error"})


@app.get("/api/analytics/dropoff")
def analytics_dropoff(days: int = Query(7, ge=1, le=365)):
    try:
        labels = [f"Q{i}" for i in range(1, 7)]
        values = [0 for _ in labels]
        return {"labels": labels, "values": values}
    except Exception as exc:
        logger.info("analytics_dropoff_error: %s", exc)
        return JSONResponse(status_code=500, content={"error": "internal_error"})


@app.post("/api/iq/start")
def iq_start(block_size: int = Query(3, ge=1, le=3)):
    try:
        pool = get_item_pool()
        session_id = str(uuid.uuid4())
        IQ_ANALYTICS["starts"] += 1
        session = {
            "id": session_id,
            "started_at": time.time(),
            "difficulty": 3,
            "score": 0.0,
            "answers_count": 0,
            "used_items": [],
            "n_items": IQ_CONFIG["n_items"],
            "block_size": block_size,
        }
        remaining = session["n_items"] - session["answers_count"]
        block = _select_items(pool, session["difficulty"], session["used_items"], min(block_size, remaining))
        session["used_items"].extend([item["item_id"] for item in block])
        IQ_SESSIONS[session_id] = session
        return {
            "session_id": session_id,
            "block": [_serialize_item(item) for item in block],
            "config": IQ_CONFIG,
        }
    except Exception as exc:
        logger.info("iq_start_error: %s", exc)
        return JSONResponse(status_code=500, content={"error": "internal_error"})


@app.post("/api/iq/answer")
def iq_answer(payload: dict):
    try:
        session_id = payload.get("session_id")
        answers = payload.get("answers", [])
        session = IQ_SESSIONS.get(session_id)
        if not session:
            return JSONResponse(status_code=400, content={"error": "invalid_session"})

        pool = get_item_pool()
        for answer in answers:
            item_id = answer.get("item_id")
            selected = answer.get("answer")
            timed_out = answer.get("timed_out", False)
            item = next((it for it in pool if it["item_id"] == item_id), None)
            if not item:
                continue
            correct = (not timed_out) and (selected == item["correct"])
            if correct:
                session["score"] += IQ_CONFIG["difficulty_weights"][item["difficulty"]]
            session["answers_count"] += 1
            if correct and session["difficulty"] < 5:
                session["difficulty"] += 1
            elif not correct and session["difficulty"] > 1:
                session["difficulty"] -= 1

        if session["answers_count"] >= session["n_items"]:
            return {"done": True}

        remaining = session["n_items"] - session["answers_count"]
        block = _select_items(pool, session["difficulty"], session["used_items"], min(session["block_size"], remaining))
        if not block:
            return {"done": True}
        session["used_items"].extend([item["item_id"] for item in block])
        return {"done": False, "block": [_serialize_item(item) for item in block]}
    except Exception as exc:
        logger.info("iq_answer_error: %s", exc)
        return JSONResponse(status_code=500, content={"error": "internal_error"})


@app.post("/api/iq/finish")
def iq_finish(payload: dict):
    try:
        session_id = payload.get("session_id")
        session = IQ_SESSIONS.get(session_id)
        if not session:
            return JSONResponse(status_code=400, content={"error": "invalid_session"})

        if session.get("finished"):
            return session["result"]

        score = session["score"]
        iq_value = int(round(80 + (score / IQ_CONFIG["score_max"]) * 70))
        iq_value = max(80, min(150, iq_value))
        label = _iq_label(iq_value)

        duration = int(time.time() - session["started_at"])
        IQ_ANALYTICS["finishes"] += 1
        IQ_ANALYTICS["total_time_sec"] += duration
        band = _iq_band(iq_value)
        IQ_ANALYTICS["iq_bands"][band] += 1

        session["result"] = {
            "iq": iq_value,
            "label": label,
            "score": round(score, 2),
            "duration_sec": duration,
        }
        session["finished"] = True
        return session["result"]
    except Exception as exc:
        logger.info("iq_finish_error: %s", exc)
        return JSONResponse(status_code=500, content={"error": "internal_error"})

@app.get("/tip/today")
def tip_today():
    try:
        # MVP: hardcoded. Luego: tabla tips + rotación por día + segmentación por usuario
        return {
            "date": "today",
            "title": "Consejo del día",
            "tip": "Antes de comprar, esperá 10 minutos. Reduce compras impulsivas."
        }
    except Exception as exc:
        logger.info("tip_today_error: %s", exc)
        return JSONResponse(status_code=500, content={"error": "internal_error"})
