import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from flask import Flask, Response, jsonify, request, send_from_directory

from app.container import AppContainer
from app.domain.entities.iq_answer import IqAnswer
from app.domain.exceptions import SessionNotFoundError

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "Frontend"
STATIC_DIR = FRONTEND_DIR

NO_CACHE_HEADERS = {
    "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
    "Pragma": "no-cache",
    "Expires": "0",
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")


def _validation_error(param: str, message: str, error_type: str) -> Response:
    return jsonify(detail=[{"loc": ["query", param], "msg": message, "type": error_type}]), 422


def _get_int_query(
    param: str, default: int, min_value: Optional[int] = None, max_value: Optional[int] = None
) -> Tuple[Optional[int], Optional[Response]]:
    raw_value = request.args.get(param, default)
    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        return None, _validation_error(param, "value is not a valid integer", "type_error.integer")
    if min_value is not None and value < min_value:
        return None, _validation_error(
            param, f"ensure this value is greater than or equal to {min_value}", "value_error.number.not_ge"
        )
    if max_value is not None and value > max_value:
        return None, _validation_error(
            param, f"ensure this value is less than or equal to {max_value}", "value_error.number.not_le"
        )
    return value, None


def create_app(container: AppContainer | None = None) -> Flask:
    """AppFactory principal que configura Flask y DI."""
    container = container or AppContainer()
    flask_app = Flask(__name__, static_folder=None)

    @flask_app.after_request
    def no_cache_static_headers(response: Response):
        if request.path.startswith("/static"):
            response.headers.update(NO_CACHE_HEADERS)
        return response

    def _render_view(filename: str):
        try:
            html_path = FRONTEND_DIR / filename
            html = html_path.read_text(encoding="utf-8")
            return Response(html, mimetype="text/html", headers=NO_CACHE_HEADERS)
        except Exception as exc:  # burbujea y loguea en capa externa
            logger.info("view_error_%s: %s", filename, exc)
            return jsonify(error="internal_error"), 500

    @flask_app.get("/")
    def root():
        return _render_view("index.html")

    @flask_app.get("/test")
    def test_view():
        return _render_view("test.html")

    @flask_app.get("/favicon.ico")
    def favicon():
        return jsonify(error="not_found"), 404

    @flask_app.get("/resultado")
    def resultado_view():
        return _render_view("resultado.html")

    @flask_app.get("/analitica")
    def analitica_view():
        return _render_view("analitica.html")

    @flask_app.get("/stroop")
    def stroop_view():
        return _render_view("stroop.html")

    @flask_app.get("/test-mixed")
    def mixed_view():
        return _render_view("test-mixed.html")

    @flask_app.get("/static/<path:filename>")
    def static_files(filename: str):
        response = send_from_directory(str(STATIC_DIR), filename)
        response.headers.update(NO_CACHE_HEADERS)
        return response

    @flask_app.get("/health")
    def health():
        try:
            return {"ok": True}
        except Exception as exc:
            logger.info("health_error: %s", exc)
            return jsonify(error="internal_error"), 500

    @flask_app.get("/db-check")
    def db_check():
        try:
            return container.get_db_check().execute()
        except Exception as exc:
            logger.info("db_check_error: %s", exc)
            return jsonify(error="internal_error"), 500

    @flask_app.get("/api/tests")
    def list_tests():
        try:
            return container.get_list_tests().execute()
        except Exception as exc:
            logger.info("list_tests_error: %s", exc)
            return jsonify(error="internal_error"), 500

    @flask_app.get("/api/analytics/summary")
    def analytics_summary():
        days, error = _get_int_query("days", 7, min_value=1, max_value=365)
        if error:
            return error
        try:
            return container.get_analytics_summary().execute(days)
        except Exception as exc:
            logger.info("analytics_summary_error: %s", exc)
            return jsonify(error="internal_error"), 500

    @flask_app.get("/api/analytics/funnel")
    def analytics_funnel():
        days, error = _get_int_query("days", 7, min_value=1, max_value=365)
        if error:
            return error
        try:
            return container.get_analytics_funnel().execute(days)
        except Exception as exc:
            logger.info("analytics_funnel_error: %s", exc)
            return jsonify(error="internal_error"), 500

    @flask_app.get("/api/analytics/profiles")
    def analytics_profiles():
        days, error = _get_int_query("days", 7, min_value=1, max_value=365)
        if error:
            return error
        try:
            return container.get_analytics_profiles().execute(days)
        except Exception as exc:
            logger.info("analytics_profiles_error: %s", exc)
            return jsonify(error="internal_error"), 500

    @flask_app.get("/api/analytics/dropoff")
    def analytics_dropoff():
        days, error = _get_int_query("days", 7, min_value=1, max_value=365)
        if error:
            return error
        try:
            return container.get_analytics_dropoff().execute(days)
        except Exception as exc:
            logger.info("analytics_dropoff_error: %s", exc)
            return jsonify(error="internal_error"), 500

    @flask_app.post("/api/iq/start")
    def iq_start():
        block_size, error = _get_int_query("block_size", 3, min_value=1, max_value=3)
        if error:
            return error
        try:
            return container.get_start_iq().execute(block_size=block_size)
        except Exception as exc:
            logger.info("iq_start_error: %s", exc)
            return jsonify(error="internal_error"), 500

    @flask_app.post("/api/iq/answer")
    def iq_answer():
        try:
            payload = request.get_json(silent=True) or {}
            session_id = payload.get("session_id")
            answers_payload: List[Dict] = payload.get("answers", [])
            answers = []
            for ans in answers_payload:
                item_id = ans.get("item_id")
                if not item_id:
                    continue
                answers.append(
                    IqAnswer(
                        item_id=item_id,
                        answer=str(ans.get("answer")) if ans.get("answer") is not None else "",
                        timed_out=bool(ans.get("timed_out", False)),
                        seconds=float(ans.get("seconds", 0) or 0),
                        changes=int(ans.get("changes", 0) or 0),
                    )
                )
            result = container.get_answer_iq().execute(session_id=session_id, answers=answers)
            return result
        except SessionNotFoundError:
            return jsonify(error="invalid_session"), 400
        except Exception as exc:
            logger.info("iq_answer_error: %s", exc)
            return jsonify(error="internal_error"), 500

    @flask_app.post("/api/iq/finish")
    def iq_finish():
        try:
            payload = request.get_json(silent=True) or {}
            session_id = payload.get("session_id")
            result = container.get_finish_iq().execute(session_id=session_id)
            return result
        except SessionNotFoundError:
            return jsonify(error="invalid_session"), 400
        except Exception as exc:
            logger.info("iq_finish_error: %s", exc)
            return jsonify(error="internal_error"), 500

    @flask_app.get("/tip/today")
    def tip_today():
        try:
            return container.get_tip_today().execute()
        except Exception as exc:
            logger.info("tip_today_error: %s", exc)
            return jsonify(error="internal_error"), 500

    # Stroop/WCST hibrido
    @flask_app.post("/api/stroop/start")
    def stroop_start():
        try:
            return container.get_stroop_start().execute()
        except Exception as exc:
            logger.info("stroop_start_error: %s", exc)
            return jsonify(error="internal_error"), 500

    @flask_app.post("/api/stroop/answer")
    def stroop_answer():
        try:
            payload = request.get_json(silent=True) or {}
            session_id = payload.get("session_id")
            selected = payload.get("answer")
            rt_ms = int(payload.get("rt_ms", 0))
            resp, status = container.get_stroop_answer().execute(session_id=session_id, selected=selected, rt_ms=rt_ms)
            return resp, status
        except Exception as exc:
            logger.info("stroop_answer_error: %s", exc)
            return jsonify(error="internal_error"), 500

    @flask_app.post("/api/stroop/finish")
    def stroop_finish():
        try:
            payload = request.get_json(silent=True) or {}
            session_id = payload.get("session_id")
            resp, status = container.get_stroop_finish().execute(session_id=session_id)
            return resp, status
        except Exception as exc:
            logger.info("stroop_finish_error: %s", exc)
            return jsonify(error="internal_error"), 500

    # Mixto IQ + Stroop
    @flask_app.post("/api/mixed/start")
    def mixed_start():
        iq_count, error = _get_int_query("iq_count", 10, min_value=4, max_value=20)
        if error:
            return error
        stroop_count, error = _get_int_query("stroop_count", 6, min_value=2, max_value=10)
        if error:
            return error
        try:
            return container.get_mixed_start().execute(iq_count=iq_count, stroop_count=stroop_count)
        except Exception as exc:
            logger.info("mixed_start_error: %s", exc)
            return jsonify(error="internal_error"), 500

    @flask_app.post("/api/mixed/answer")
    def mixed_answer():
        try:
            payload = request.get_json(silent=True) or {}
            session_id = payload.get("session_id")
            answer = str(payload.get("answer"))
            resp, status = container.get_mixed_answer().execute(session_id=session_id, answer=answer)
            return resp, status
        except Exception as exc:
            logger.info("mixed_answer_error: %s", exc)
            return jsonify(error="internal_error"), 500

    @flask_app.post("/api/mixed/finish")
    def mixed_finish():
        try:
            payload = request.get_json(silent=True) or {}
            session_id = payload.get("session_id")
            resp, status = container.get_mixed_finish().execute(session_id=session_id)
            return resp, status
        except Exception as exc:
            logger.info("mixed_finish_error: %s", exc)
            return jsonify(error="internal_error"), 500

    return flask_app


app = create_app()
