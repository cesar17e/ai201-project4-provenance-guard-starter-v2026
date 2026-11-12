#!/usr/bin/env python3
"""Run the supplied attack runner against a fresh local server and retain evidence.

Example: python record_attack_run.py --set . --label before

The service, signals, limits, and attack inputs are not changed. The supplied
run_attacks.py produces its usual Markdown report. A JSON sidecar additionally
preserves each request, full parsed response, elapsed time, and audit events.
Verdicts beyond the runner's crash checks are left for review.
"""

import argparse
import copy
import hashlib
import json
import logging
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import requests
from werkzeug.serving import WSGIRequestHandler, make_server

import app
import audit
import config
import detector
import run_attacks


class QuietHandler(WSGIRequestHandler):
    def log(self, *args):
        pass


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--set", dest="folder", default=".")
    parser.add_argument("--label", required=True, choices=["before", "after"])
    args = parser.parse_args()
    if not config.RATE_LIMITING_ENABLED:
        parser.error("Rate limiting must be enabled for the attack run.")

    folder = Path(args.folder).resolve()
    sources = [config.ROOT / name for name in (
        "app.py", "config.py", "detector.py", "stylometry.py", "scoring.py", "audit.py", "criteria.md"
    )]
    sources += [folder / "attacks.csv", folder / "attacks_malformed_requests.csv"]
    hashes = {str(path.relative_to(config.ROOT) if path.is_relative_to(config.ROOT) else path): file_hash(path) for path in sources}
    original_audit = config.AUDIT_LOG.read_bytes() if config.AUDIT_LOG.exists() else b""
    initial_count = len(audit.read_entries())
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    calls, rows, problems = [], [], []
    original_send = run_attacks.send
    original_write = run_attacks.write_report
    original_load = run_attacks.load_attacks
    config.RESULTS_DIR.mkdir(exist_ok=True)
    previous_reports = set(config.RESULTS_DIR.glob(f"attack_run_*_{args.label}.md"))

    def capture_send(url, attack, timeout):
        offset = len(audit.read_entries())
        start = time.monotonic()
        status, payload, error = original_send(url, attack, timeout)
        calls.append({
            "attack": copy.deepcopy(attack),
            "http_status": status,
            "response": payload,
            "error": error,
            "elapsed_seconds": round(time.monotonic() - start, 4),
            "audit_entries": audit.read_entries()[offset:],
        })
        return status, payload, error

    def capture_write(results, arguments):
        rows.extend(copy.deepcopy(results))
        return original_write(results, arguments)

    def capture_load(path):
        attacks, errors = original_load(path)
        problems.extend(errors)
        return attacks, errors

    errors = StringIO()
    handler = logging.StreamHandler(errors)
    handler.setLevel(logging.ERROR)
    app.app.logger.addHandler(handler)
    server = make_server("127.0.0.1", 0, app.app, request_handler=QuietHandler)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    url = f"http://127.0.0.1:{server.server_port}"
    try:
        print("Loading the unchanged detector before the baseline run...", flush=True)
        print(detector.warm_up(), flush=True)
        health = requests.get(f"{url}/health", timeout=10).json()
        assert health["rate_limiting"] is True
        command = ["run_attacks.py", "--set", str(folder), "--label", args.label, "--url", url]
        with patch.object(sys, "argv", command), patch.object(run_attacks, "send", capture_send), patch.object(run_attacks, "write_report", capture_write), patch.object(run_attacks, "load_attacks", capture_load):
            run_attacks.main()
        assert len(calls) == len(rows)
        assert [call["attack"]["id"] for call in calls] == [row["id"] for row in rows]
        assert all(file_hash(path) == hashes[str(path.relative_to(config.ROOT) if path.is_relative_to(config.ROOT) else path)] for path in sources)
        assert config.AUDIT_LOG.read_bytes().startswith(original_audit)
        new_reports = set(config.RESULTS_DIR.glob(f"attack_run_*_{args.label}.md")) - previous_reports
        assert len(new_reports) == 1, "Expected one new runner report; use a different minute for a repeat."
        runner_report = new_reports.pop()
        entries = audit.read_entries()[initial_count:]
        fetched = requests.get(f"{url}/log", timeout=10).json()
        assert all(entry in fetched["entries"] for entry in entries)
        output = runner_report.with_suffix(".json")
        report = {
            "label": args.label,
            "started_utc": started,
            "finished_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "base_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
            "command": "python " + " ".join(command),
            "runner_report": str(runner_report.relative_to(config.ROOT)),
            "server": "Temporary local HTTP server with fresh in-memory limiter counters; stopped after the run.",
            "health": health,
            "source_and_input_sha256": hashes,
            "load_problems": problems,
            "requests": calls,
            "runner_rows": rows,
            "audit_entries": entries,
            "server_errors": errors.getvalue(),
        }
        output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Saved complete baseline evidence: {output.relative_to(config.ROOT)}", flush=True)
        print(f"Requests: {len(calls)}; new audit entries: {len(entries)}; skipped rows: {len(problems)}", flush=True)
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=5)
        app.app.logger.removeHandler(handler)


if __name__ == "__main__":
    main()
