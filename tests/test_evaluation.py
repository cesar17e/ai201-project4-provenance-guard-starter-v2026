"""Evaluation-harness regression tests; synthetic fixtures are not accuracy evidence."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import app
import config
import run_eval
import scenarios


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='eval_tests_')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for obj, name, value in [
            (config, 'LOG_DIR', self.root),
            (config, 'AUDIT_LOG', self.root/'audit.jsonl'),
            (app.detector, 'model_signal', lambda text: 0.6),
            (app.stylometry, 'style_signal', lambda text: 0.4),
        ]:
            patcher = patch.object(obj, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        app.limiter.reset()
        self.client = app.app.test_client()
        self.evaluator = run_eval.Evaluation('http://test', 'fixture')

        def request(method, url, json=None, timeout=None):
            response = self.client.open(url.removeprefix('http://test'), method=method, json=json)
            class Adapter:
                status_code = response.status_code
                def json(self):
                    return response.get_json()
            return Adapter()
        patcher = patch.object(run_eval.requests, 'request', side_effect=request)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_missing_human_samples_are_pending(self):
        samples, errors = scenarios.load_human_samples(self.root/'missing.json')
        self.assertTrue(errors)
        result = self.evaluator.run(scenarios.SCENARIOS[0], 1, samples, errors)
        self.assertEqual(result['state'], 'PENDING')
        self.assertEqual(result['requests'], [])

    def test_dataset_requires_twenty_distinct_provenance_records(self):
        path = self.root/'fixtures.json'
        samples = [dict(id=str(i), text=f'Synthetic loader fixture {i}.', source='unit-test fixture only', verified_by='fixture', verification='Not actual human evidence', verified_human=True) for i in range(20)]
        path.write_text(json.dumps({'samples': samples}))
        loaded, problems = scenarios.load_human_samples(path)
        self.assertEqual(len(loaded), 20)
        self.assertFalse(problems)
        samples[1]['text'] = samples[0]['text']
        path.write_text(json.dumps({'samples': samples}))
        self.assertTrue(scenarios.load_human_samples(path)[1])
        samples.pop()
        path.write_text(json.dumps({'samples': samples}))
        self.assertTrue(scenarios.load_human_samples(path)[1])

    def test_four_criteria_run_three_times_without_rate_limit_interference(self):
        for spec in scenarios.SCENARIOS[1:]:
            for trial in range(1, 4):
                result = self.evaluator.run(spec, trial, [], [])
                self.assertEqual(result['state'], 'MET', (spec, result))
                self.assertFalse(any(r.get('http_status') == 429 for r in result['requests']))

    def test_unscored_human_samples_cannot_pass_false_positive_target(self):
        with patch.object(self.evaluator, 'submit', return_value={'http_status': 429, 'response': {'error':'rate_limited'}}):
            result = self.evaluator.run(scenarios.SCENARIOS[0], 1, [{'text':'synthetic fixture'}]*20, [])
        self.assertEqual(result['state'], 'INCOMPLETE')
        self.assertEqual(result['output']['scored'], 0)

    def test_two_false_positives_miss_the_original_target(self):
        fake = [dict(http_status=200, response={'content_id':str(i), 'guess':'ai' if i<2 else 'human'}) for i in range(20)]
        with patch.object(self.evaluator, 'submit', side_effect=fake):
            result = self.evaluator.run(scenarios.SCENARIOS[0], 1, [{'text':'fixture'}]*20, [])
        self.assertEqual(result['state'], 'MISSED')
        self.assertEqual(result['output']['false_positives_assuming_human_labels'], 2)

    def test_unverified_labels_produce_provisional_measurement(self):
        fake = [dict(http_status=200, response={'content_id':str(i), 'guess':'human'}) for i in range(20)]
        with patch.object(self.evaluator, 'submit', side_effect=fake):
            result = self.evaluator.run(scenarios.SCENARIOS[0], 1, [{'text':'fixture'}]*20, [], provenance_verified=False)
        self.assertEqual(result['state'], 'PROVISIONAL')
        self.assertEqual(result['conditional_verdict'], 'MET')
        self.assertFalse(result['provenance_verified'])

    def test_unverified_dataset_requires_explicit_opt_in(self):
        path = self.root/'unverified.json'
        samples = [dict(id=str(i), text=f'Synthetic test fixture {i}.', source='fixture', verified_by='fixture', verification='unverified fixture', verified_human=False) for i in range(20)]
        path.write_text(json.dumps({'samples': samples}))
        self.assertTrue(scenarios.load_human_samples(path)[1])
        loaded, errors = scenarios.load_human_samples(path, allow_unverified=True)
        self.assertEqual(len(loaded), 20)
        self.assertFalse(errors)

    def test_429_cannot_masquerade_as_input_validation(self):
        with patch.object(self.evaluator, 'request', return_value={'http_status':429}):
            result = self.evaluator.run(scenarios.SCENARIOS[3], 1, [], [])
        self.assertEqual(result['state'], 'INCOMPLETE')


if __name__ == '__main__':
    unittest.main()
