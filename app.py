#!/usr/bin/env python3
"""
Provenance Guard — the web service.

    python app.py

Then, in another terminal:

    curl -X POST http://127.0.0.1:5000/ping \
      -H "Content-Type: application/json" \
      -d '{"message": "hello"}'

That's the example route. It works right now, before you've written anything.
**Leave it alone** — it's your control. When something breaks later, check that
`/ping` still answers: if it does, the problem is in your handler; if it
doesn't, it's the service itself.

Routes:

    POST /ping        the worked example. Already works. Don't edit it
    POST /submit      ← YOU BUILD THIS (Milestone 3, 4, 5)
    POST /appeal      ← YOU BUILD THIS (Milestone 5)
    GET  /log         the audit log. Already works
    GET  /health      is the service up, and is the model loaded
"""

import uuid

from flask import Flask, jsonify, request

import audit
import config
import detector
import stylometry
import scoring

app = Flask(__name__)


def _record_rejection(reason: str, http_status: int, **extra):
    """Record a refused request even when its body or IDs are malformed."""
    payload = request.get_json(silent=True)
    payload = payload if isinstance(payload, dict) else {}
    creator = payload.get("creator_id")
    creator = creator if isinstance(creator, str) and creator.strip() else "unknown"
    content_id = payload.get("content_id")
    if isinstance(content_id, str) and content_id.strip():
        extra["content_id"] = content_id
    return audit.log_rejection(
        creator_id=creator,
        reason=reason,
        http_status=http_status,
        route=request.path,
        remote_address=request.remote_addr,
        **extra,
    )


def _reject(message: str, reason: str, http_status: int = 400):
    _record_rejection(reason, http_status)
    return jsonify({"error": message}), http_status


# ── Rate limiting — UNIT 8 ────────────────────────────────────────────────────
# Enabled by default in config.py. Only /submit is limited, using the configured
# per-minute and per-day limits. Rejected requests count toward those limits.
#
# The storage backend is preconfigured, which stops Flask-Limiter printing a
# warning on every start. In-memory is right for one laptop and wrong for
# anything real — a restart forgets every count.

class _LimiterOff:
    """
    Stands in for the real limiter while rate limiting is off.

    It makes @limiter.limit(...) a decorator that returns the route
    untouched, so uncommenting the line before you flip the setting is
    harmless instead of a crash on startup.
    """

    def limit(self, *args, **kwargs):
        return lambda view: view


limiter = _LimiterOff()
if config.RATE_LIMITING_ENABLED:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address

    def rate_limit_key():
        """
        Who a request counts against.

        Falling back to the caller's address is the easy version. Unit 8's
        stretch asks about per-creator limits instead — and the difference
        matters: one script can look like a thousand callers, and one household
        can look like one.
        """
        payload = request.get_json(silent=True)
        # A body that parses as JSON but isn't an object — a bare list or
        # string — has no .get. Without this guard the key function raises
        # BEFORE the route runs, and a malformed request becomes a 500 that
        # looks like your handler crashed when your handler never ran.
        if not isinstance(payload, dict):
            return get_remote_address()
        creator = payload.get("creator_id")
        return creator if isinstance(creator, str) and creator.strip() else get_remote_address()

    limiter = Limiter(
        key_func=rate_limit_key,
        app=app,
        storage_uri=config.RATE_LIMIT_STORAGE,
        default_limits=[],
    )

    @app.errorhandler(429)
    def rate_limited(exc):
        """
        A rejected request still leaves a trace.

        ⚠️ An attack that shows up only as an absence is one you'll never find.
        """
        _record_rejection(
            "rate_limited",
            429,
            limit=str(exc.description),
        )
        return jsonify({
            "error": "rate_limited",
            "message": "Too many submissions. Try again shortly.",
            "limit": str(exc.description),
        }), 429


# ── The worked example. Already works. Don't edit. ────────────────────────────

@app.post("/ping")
def ping():
    """
    Everything a route needs, in six lines.

    JSON arrives as a dict. You pull things out of it. You return a dict and
    the framework turns it into a response. That's the whole idea.
    """
    payload = request.get_json(silent=True) or {}
    return jsonify({
        "ok": True,
        "you_sent": payload.get("message"),
        "service": "provenance-guard",
    })


@app.get("/health")
def health():
    """Is the service up, and has the model been downloaded yet?"""
    import detector

    loaded = detector._model is not None
    return jsonify({
        "ok": True,
        "detector_model": config.DETECTOR_MODEL,
        "detector_loaded": loaded,
        "rate_limiting": config.RATE_LIMITING_ENABLED,
        "log_entries": len(audit.read_entries()),
    })


# ── YOU BUILD THIS ────────────────────────────────────────────────────────────

@app.post("/submit")
@limiter.limit(f"{config.RATE_LIMIT_PER_MINUTE}/minute;{config.RATE_LIMIT_PER_DAY}/day")
def submit():
    """
    This function is the main entry point for the Provenance Guard service. It handles incoming submissions of text, analyzes them using both the model and style signals, combines the results, logs the decision, and returns a JSON response with the analysis results.
    """

    # 1. Read the incoming JSON
    payload = request.get_json(silent=True)

    if not isinstance(payload, dict):
        return _reject("Valid JSON object is required.", "invalid_json_object")

    text = payload.get("text")
    creator_id = payload.get("creator_id")

    # 2. Validate the incoming data
    if not isinstance(text, str) or not text.strip():
        return _reject("Text is required.", "invalid_text")

    if not isinstance(creator_id, str) or not creator_id.strip():
        return _reject("Creator ID is required.", "invalid_creator_id")

    # 3. Generate a unique submission ID
    content_id = str(uuid.uuid4())

    # 4. Run both detection signals
    try:
        model_score = detector.model_signal(text)
    except ValueError as exc:
        return _reject(str(exc), "text_too_short")
    except detector.DetectorUnavailable:
        return _reject(
            "The detector is unavailable. Please try again later.",
            "detector_unavailable",
            503,
        )
    style_score = stylometry.style_signal(text)

    # 5. Combine the signals (70% model, 30% style)
    combined_score = scoring.combine_signals(
        model_score,
        style_score
    )

    # 6. Convert the combined score into a readable label
    guess, label = scoring.score_to_label(combined_score)

    # 7. Record the decision in the audit log
    audit.log_decision(
        content_id=content_id,
        creator_id=creator_id,
        guess=guess,
        model_score=model_score,
        style_score=style_score,
        combined_score=combined_score,
        label=label,
        status="decided"
    )

    # 8. Return the result as JSON
    return jsonify({
        "content_id": content_id,
        "guess": guess,
        "confidence": combined_score,
        "label": label,
        "model_score": model_score,
        "style_score": style_score
    })

@app.post("/appeal")
def appeal():

    """
    This function handles appeals from users who wish to contest the decision made on their submitted text. It validates the appeal request, checks for the original submission, logs the appeal, and returns a confirmation response.
    """
    # 1. Read the request
    payload = request.get_json(silent=True)

    if not isinstance(payload, dict):
        return _reject("Valid JSON is required.", "invalid_json_object")

    content_id = payload.get("content_id")
    reasoning = payload.get("reasoning")

    # 2. Validate the input
    if not isinstance(content_id, str) or not content_id.strip():
        return _reject("Content ID is required.", "invalid_content_id")

    if not isinstance(reasoning, str) or not reasoning.strip():
        return _reject("Reasoning is required.", "invalid_reasoning")

    # 3. Find the original submission
    entries = audit.entries_for(content_id)

    original = next(
        (entry for entry in entries if entry.get("status") == "decided"),
        None
    )

    if original is None:
        return _reject("Content not found.", "content_not_found", 404)

    # 4. Get the original creator ID
    creator_id = original["creator_id"]

    # 5. Record the appeal
    audit.log_appeal(
        content_id=content_id,
        creator_id=creator_id,
        reasoning=reasoning
    )

    # 6. Confirm the appeal
    return jsonify({
        "content_id": content_id,
        "status": "under_review",
        "message": "Your appeal has been recorded."
    })

# ── Already works ─────────────────────────────────────────────────────────────

@app.get("/log")
def get_log():
    """
    The audit log, most recent last.

        curl "http://127.0.0.1:5000/log?limit=10"

    You need this in unit 8 to paste entries into your README, and you need it
    now to see whether your logging is actually working.
    """
    limit = request.args.get("limit", type=int)
    entries = audit.read_entries(limit=limit)
    return jsonify({"count": len(entries), "entries": entries})


def main():
    print(f"Provenance Guard on http://{config.HOST}:{config.PORT}")
    print(f"  detector model:  {config.DETECTOR_MODEL}")
    print(f"  rate limiting:   {'ON' if config.RATE_LIMITING_ENABLED else 'off'}")
    print(f"  audit log:       {config.AUDIT_LOG}")
    print()
    print("Check it's alive:")
    print(f'  curl -X POST http://{config.HOST}:{config.PORT}/ping \\')
    print('    -H "Content-Type: application/json" \\')
    print("    -d '{\"message\": \"hello\"}'")
    print()
    # debug=True hands out an interactive debugger, so it's local-only — see config.py
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)


if __name__ == "__main__":
    main()
