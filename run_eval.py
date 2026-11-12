#!/usr/bin/env python3
"""Measure the five original criteria across three unchanged trials.

python run_eval.py --local --label before --human-samples evaluation/human_samples.json
Use --allow-partial explicitly to run criteria 2–5 while criterion 1 is pending.
Both signals are deterministic; identical repeated scores are expected.
"""

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import threading
import uuid

import requests
import config
import scenarios
import scoring


@contextmanager
def service_url(local, url):
    if not local:
        yield url
        return
    import app
    import detector
    from werkzeug.serving import make_server
    from record_attack_run import QuietHandler
    server = make_server('127.0.0.1', 0, app.app, request_handler=QuietHandler)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        print(detector.warm_up(), flush=True)
        yield f'http://127.0.0.1:{server.server_port}'
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=5)


class Evaluation:
    def __init__(self, url, run_id):
        self.url, self.run_id = url, run_id

    def request(self, method, route, body=None):
        record = {'method': method, 'route': route, 'request': body}
        try:
            response = requests.request(method, self.url + route, json=body, timeout=90)
            record.update(http_status=response.status_code, response=response.json())
        except (requests.RequestException, ValueError) as exc:
            record.update(http_status=locals().get('response').status_code if 'response' in locals() else None, error=str(exc))
        return record

    def submit(self, criterion, index, text):
        # Independent test writers, each making at most three submissions per run.
        return self.request('POST', '/submit', {
            'text': text, 'creator_id': f'eval_{self.run_id}_c{criterion}_{index}',
        })

    def run(self, spec, trial, samples, pending, provenance_verified=True):
        kind = spec['kind']
        result = {'trial': trial, 'producer': 'run_eval.py::Evaluation.run', 'requests': []}
        calls = result['requests']
        if kind == 'human' and pending:
            return dict(result, state='PENDING', measurement='Not run: verified-human dataset missing or invalid', reasons=pending)
        if kind == 'labels':
            low, high = config.HUMAN_THRESHOLD, config.AI_THRESHOLD
            assert 0 <= low < high <= 1, 'Invalid threshold configuration'
            boundaries = [0.0, low, math.nextafter(low, 1), math.nextafter(high, 0), high, 1.0, 0.51, 0.95]
            scores = [i / 1000 for i in range(1001)] + boundaries
            observed, failures, examples = set(), [], []
            for index, score in enumerate(scores):
                guess, label = scoring.score_to_label(score)
                expected = 'human' if score <= low else 'ai' if score >= high else 'unsure'
                observed.add(guess)
                case = {'score': score, 'guess': guess, 'label': label, 'expected': expected}
                if index >= 1001:
                    examples.append(case)
                if guess != expected or not label or 'PLACEHOLDER' in label:
                    failures.append(case)
            passed = not failures and observed == {'human', 'unsure', 'ai'}
            return dict(result, state='MET' if passed else 'MISSED', measurement=f'{len(observed)}/3 labels; {len(scores)-len(failures)}/{len(scores)} mappings', output={'producer': 'scoring.py::score_to_label', 'boundaries': examples, 'failures': failures, 'checked': len(scores), 'coverage_argument': 'Ordered inclusive outer branches plus the middle return partition the entire valid interval.'})
        if kind == 'invalid':
            bodies = [
                {'creator_id': f'eval_{self.run_id}_bad1'},
                {'text': '', 'creator_id': f'eval_{self.run_id}_bad2'},
                {'text': '   ', 'creator_id': f'eval_{self.run_id}_bad3'},
                {'text': scenarios.VALID_TEXT},
                {'text': 123, 'creator_id': f'eval_{self.run_id}_bad5'},
                ['not', 'an', 'object'],
            ]
            calls.extend(self.request('POST', '/submit', body) for body in bodies)
            passed = sum(400 <= (c.get('http_status') or 0) < 500 for c in calls)
            state = 'MET' if passed == 6 else 'MISSED'
            if any(c.get('http_status') == 429 for c in calls):
                state = 'INCOMPLETE'  # throttling masks the intended validation check
            return dict(result, state=state, measurement=f'{passed}/6 returned 4xx', output={'http_statuses': [c.get('http_status') for c in calls]})
        texts = [s['text'] for s in samples] if kind == 'human' else [scenarios.VALID_TEXT + f' This is example {i}.' for i in range(1, 11)]
        submissions = [self.submit(spec['criterion'], i, text) for i, text in enumerate(texts, 1)]
        calls.extend(submissions)
        valid = [c for c in submissions if c.get('http_status') == 200 and isinstance(c.get('response'), dict) and c['response'].get('content_id') and c['response'].get('guess') in ('human', 'unsure', 'ai')]
        if kind == 'human':
            flagged = sum(c['response'].get('guess') == 'ai' for c in valid)
            state = 'INCOMPLETE' if len(valid) != 20 else 'MET' if flagged <= 1 else 'MISSED'
            conditional = state
            if not provenance_verified and state in ('MET', 'MISSED'):
                state = 'PROVISIONAL'
            return dict(result, state=state, conditional_verdict=conditional, provenance_verified=provenance_verified, measurement=f'{flagged}/20 high-confidence AI; {len(valid)}/20 scored', output={'false_positives_assuming_human_labels': flagged, 'scored': len(valid), 'target_maximum': 1})
        appeals = []
        if kind == 'appeals':
            for submission in valid:
                appeals.append(self.request('POST', '/appeal', {
                    'content_id': submission['response']['content_id'],
                    'reasoning': f'Criterion 3 trial {trial}: please review this verification decision.',
                }))
            calls.extend(appeals)
        log = self.request('GET', '/log')
        calls.append(log)
        entries = log.get('response', {}).get('entries', []) if isinstance(log.get('response'), dict) else []
        passed = 0
        for index, submission in enumerate(valid):
            payload = submission['response']
            history = [e for e in entries if e.get('content_id') == payload['content_id']]
            if kind == 'appeals':
                response = appeals[index]
                # Earlier trial appeals have different IDs; use this trial's exact reasoning.
                matching = [e for e in history if e.get('event') == 'appeal' and e.get('reasoning') == response['request']['reasoning']]
                lifecycle = [e for e in history if e.get('status') in ('decided', 'under_review')]
                ok = (response.get('http_status') == 200 and response.get('response', {}).get('content_id') == payload['content_id'] and response.get('response', {}).get('status') == 'under_review' and len(matching) == 1 and matching[0].get('status') == 'under_review' and matching[0].get('creator_id') == submission['request']['creator_id'] and lifecycle and lifecycle[-1]['status'] == 'under_review')
            else:
                required = {'timestamp','content_id','creator_id','model_score','style_score','combined_score','status'}
                decisions = [e for e in history if e.get('status') == 'decided']
                ok = len(decisions) == 1 and all(decisions[0].get(k) is not None for k in required)
                if ok:
                    entry = decisions[0]
                    ok = entry['creator_id'] == submission['request']['creator_id'] and entry['combined_score'] == payload['confidence'] and all(entry[k] == payload[k] for k in ('model_score','style_score'))
            passed += bool(ok)
        incomplete = any(c.get('http_status') == 429 or c.get('http_status') is None for c in calls)
        state = 'INCOMPLETE' if incomplete else 'MET' if passed == 10 else 'MISSED'
        return dict(result, state=state, measurement=f'{passed}/10 ' + ('appeals recorded and under_review' if kind == 'appeals' else 'matching audit entries'), output={'passed': passed, 'required': 10})


def write_report(report):
    config.RESULTS_DIR.mkdir(exist_ok=True)
    suffix = '_partial' if report['partial'] else ''
    stem = f"eval_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}_{report['label']}{suffix}_{report['run_id']}"
    path = config.RESULTS_DIR / (stem + '.json')
    lines = ['# Criterion evaluation — ' + report['label'], '', '- Producer: `run_eval.py::Evaluation.run`', '- Full requests, responses, and log snapshots: [' + path.name + '](' + path.name + ')', '', '| Criterion | Target | Run 1 | Run 2 | Run 3 | Computed verdict |', '|---|---|---|---|---|---|']
    for row in report['criteria']:
        states = [t['state'] for t in row['trials']]
        verdict = 'PENDING' if 'PENDING' in states else 'INCOMPLETE' if 'INCOMPLETE' in states else 'PROVISIONAL' if 'PROVISIONAL' in states else 'MET' if all(s == 'MET' for s in states) else 'MISSED'
        row['verdict'] = verdict
        values = [t['measurement'] for t in row['trials']]
        lines.append('| ' + ' | '.join([str(row['criterion']) + '. ' + row['name'], row['target'], *values, verdict]) + ' |')
    lines += ['', 'Verdicts are computed from the original numeric targets; final review and diagnoses follow separately. PENDING is not a trial. PROVISIONAL means scores were measured using user-supplied authorship labels, but independent provenance remains unconfirmed.', '']
    for row in report['criteria']:
        trial = row['trials'][0]
        # One actual output per criterion; complete request lists stay in the JSON sidecar.
        excerpt = {k: v for k, v in trial.items() if k != 'requests'}
        if trial['requests']:
            excerpt['first_request_and_response'] = trial['requests'][0]
        lines += ['## ' + str(row['criterion']) + '. ' + row['name'], '', '```json', json.dumps(excerpt, indent=2, ensure_ascii=False), '```', '']
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    path.with_suffix('.md').write_text('\n'.join(lines))
    print(f'Saved {path.relative_to(config.ROOT)}', flush=True)
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--label', required=True, choices=['before','after'])
    parser.add_argument('--url', default=f'http://{config.HOST}:{config.PORT}')
    parser.add_argument('--local', action='store_true', help='Use a fresh temporary HTTP server with real signals')
    parser.add_argument('--human-samples', type=Path, default=scenarios.HUMAN_SAMPLES)
    parser.add_argument('--allow-partial', action='store_true', help='Explicitly leave criterion 1 pending if its dataset is unavailable')
    parser.add_argument('--allow-unverified-human-samples', action='store_true', help='Measure supplied labels provisionally without claiming independent provenance')
    args = parser.parse_args()
    samples, problems = scenarios.load_human_samples(args.human_samples, args.allow_unverified_human_samples)
    if problems and not args.allow_partial:
        parser.error('\n'.join(problems) + '\nUse --allow-partial only for an explicitly incomplete run.')
    files = ['app.py','config.py','detector.py','stylometry.py','scoring.py','audit.py','criteria.md','scenarios.py','run_eval.py']
    if samples:
        files.append(str(args.human_samples))
    hashes = {f: hashlib.sha256(Path(f).read_bytes()).hexdigest() for f in files}
    provenance_verified = bool(samples) and all(sample['verified_human'] is True for sample in samples)
    report = {'run_id': uuid.uuid4().hex[:8], 'label': args.label, 'started_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'partial': bool(problems) or not provenance_verified, 'human_provenance_verified': provenance_verified, 'dataset_problems': problems, 'human_samples': samples, 'source_and_dataset_sha256': hashes, 'trial_count': 3, 'criteria': []}
    with service_url(args.local, args.url) as url:
        evaluation = Evaluation(url, report['run_id'])
        health = evaluation.request('GET','/health')
        if health.get('http_status') != 200 or not health.get('response',{}).get('rate_limiting'):
            parser.error('The service must be healthy with rate limiting enabled.')
        report['health'] = health
        report['transport'] = 'Real HTTP; local score_to_label called directly for controlled score coverage'
        for spec in scenarios.SCENARIOS:
            row = dict(spec, trials=[])
            for trial in range(1,4):
                result = evaluation.run(spec, trial, samples, problems, provenance_verified)
                row['trials'].append(result)
                print(f"Criterion {spec['criterion']}, trial {trial}: {result['state']} — {result['measurement']}", flush=True)
            report['criteria'].append(row)
    assert all(hashlib.sha256(Path(f).read_bytes()).hexdigest() == digest for f,digest in hashes.items()), 'Inputs or source changed during evaluation'
    write_report(report)


if __name__ == '__main__':
    main()
