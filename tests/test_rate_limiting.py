"""Behavior checks for Unit 8 Milestone 1; scoring is stubbed only in these tests."""

import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import app
import audit
import config
import detector


TEXT = "A valid paragraph for checking request limits and audit logging."


class RateLimitingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="provenance_limits_")
        self.addCleanup(self.temp.cleanup)
        for name, value in [
            ("LOG_DIR", Path(self.temp.name)),
            ("AUDIT_LOG", Path(self.temp.name) / "audit.jsonl"),
        ]:
            patcher = patch.object(config, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.model = patch.object(detector, "model_signal", return_value=0.6)
        self.model_mock = self.model.start()
        self.addCleanup(self.model.stop)
        style = patch.object(app.stylometry, "style_signal", return_value=0.4)
        style.start()
        self.addCleanup(style.stop)
        self.assertTrue(config.RATE_LIMITING_ENABLED)
        app.limiter.reset()
        app.app.config["TESTING"] = True
        self.client = app.app.test_client()

    def submit(self, creator="writer"):
        return self.client.post("/submit", json={"text": TEXT, "creator_id": creator})

    def test_minute_limit_logs_every_request_and_preserves_appeals(self):
        responses = [self.submit() for _ in range(15)]
        self.assertEqual([r.status_code for r in responses], [200] * 10 + [429] * 5)
        self.assertEqual(self.model_mock.call_count, 10)
        entries = self.client.get("/log").get_json()["entries"]
        self.assertEqual(len(entries), 15)
        required = {
            "timestamp", "content_id", "creator_id", "guess", "model_score",
            "style_score", "combined_score", "label", "status",
        }
        for entry in entries[:10]:
            self.assertTrue(required <= entry.keys())
            self.assertEqual(entry["status"], "decided")
            self.assertTrue(all(entry[key] is not None for key in required))
        for entry in entries[10:]:
            self.assertEqual(entry["reason"], "rate_limited")
            self.assertEqual(entry["http_status"], 429)
            self.assertEqual(entry["creator_id"], "writer")
            self.assertEqual(entry["route"], "/submit")
        self.assertTrue(self.client.get("/health").get_json()["rate_limiting"])
        self.assertEqual(self.submit("another_writer").status_code, 200)
        content_id = responses[0].get_json()["content_id"]
        response = self.client.post("/appeal", json={
            "content_id": content_id, "reasoning": "Please review this decision."
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(audit.entries_for(content_id)[-1]["status"], "under_review")

    def test_daily_limit_survives_minute_window_resets(self):
        start = time.time()
        # Advance only the limiter's storage clock; no waiting or setting changes.
        with patch("limits.storage.memory.time.time", return_value=start) as clock:
            for minute in range(20):
                clock.return_value = start + minute * 61
                for _ in range(10):
                    self.assertEqual(self.submit("daily_writer").status_code, 200)
            clock.return_value = start + 20 * 61
            response = self.submit("daily_writer")
            self.assertEqual(response.status_code, 429)
            self.assertIn("200 per 1 day", response.get_json()["limit"])
            clock.return_value = start + 86401
            self.assertEqual(self.submit("daily_writer").status_code, 200)

    def test_invalid_submissions_are_logged_before_signals(self):
        bodies = [
            {"creator_id": "missing_text"},
            {"text": "", "creator_id": "empty_text"},
            {"text": "   ", "creator_id": "whitespace"},
            {"text": TEXT},
            {"text": 123, "creator_id": "non_string"},
            ["not", "an", "object"],
        ]
        for body in bodies:
            self.assertEqual(self.client.post("/submit", json=body).status_code, 400)
        self.assertEqual(self.model_mock.call_count, 0)
        entries = audit.read_entries()
        self.assertEqual(len(entries), 6)
        self.assertTrue(all(e["event"] == "rejected" and e["http_status"] == 400 for e in entries))
        self.assertTrue(all(e["route"] == "/submit" and e["reason"] for e in entries))

    def test_missing_creator_uses_address_and_rejections_count(self):
        responses = [self.client.post("/submit", json={"text": TEXT}) for _ in range(11)]
        self.assertEqual([r.status_code for r in responses], [400] * 10 + [429])
        other = self.client.post("/submit", json={"text": TEXT}, environ_overrides={"REMOTE_ADDR": "127.0.0.2"})
        self.assertEqual(other.status_code, 400)
        self.assertEqual(audit.read_entries()[-1]["remote_address"], "127.0.0.2")
        self.assertEqual(self.model_mock.call_count, 0)

    def test_signal_failures_and_invalid_appeals_are_logged(self):
        self.model_mock.side_effect = ValueError("Text is too short to score.")
        self.assertEqual(self.submit("short_text").status_code, 400)
        self.model_mock.side_effect = detector.DetectorUnavailable("not loaded")
        self.assertEqual(self.submit("unavailable").status_code, 503)
        cases = [
            (["invalid"], 400),
            ({}, 400),
            ({"content_id": "missing", "reasoning": " "}, 400),
            ({"content_id": "missing", "reasoning": "Please review."}, 404),
        ]
        for body, expected in cases:
            self.assertEqual(self.client.post("/appeal", json=body).status_code, expected)
        entries = audit.read_entries()
        self.assertEqual(len(entries), 6)
        self.assertEqual(entries[0]["reason"], "text_too_short")
        self.assertEqual(entries[1]["reason"], "detector_unavailable")
        self.assertEqual(entries[-1]["content_id"], "missing")
        self.assertTrue(all(e["status"] == "rejected" for e in entries))


if __name__ == "__main__":
    unittest.main()
