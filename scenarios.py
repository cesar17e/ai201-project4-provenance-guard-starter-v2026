"""Evaluation plans for the five original criteria; no service settings change."""

from pathlib import Path
import json

HUMAN_SAMPLES = Path(__file__).parent / 'evaluation' / 'human_samples.json'
VALID_TEXT = (
    'I missed the bus. Again! My toast was still warm, and my sister laughed '
    'so hard she spilled her coffee. We decided to walk instead.'
)
SCENARIOS = [
    {'criterion': 1, 'name': 'False-positive rate', 'target': 'At most 1 high-confidence AI label among 20 verified human samples', 'kind': 'human'},
    {'criterion': 2, 'name': 'Label coverage', 'target': 'All three labels; complete, unambiguous 0–1 mapping including boundaries', 'kind': 'labels'},
    {'criterion': 3, 'name': 'Appeal handling', 'target': '10/10 appeals recorded and under_review for 10 existing IDs', 'kind': 'appeals'},
    {'criterion': 4, 'name': 'Invalid input handling', 'target': '6/6 invalid cases return 4xx without a server crash', 'kind': 'invalid'},
    {'criterion': 5, 'name': 'Audit logging', 'target': '10/10 valid submissions have matching audit entries and required fields', 'kind': 'audit'},
]


def load_human_samples(path=HUMAN_SAMPLES, allow_unverified=False):
    """Validate dataset shape and supplied provenance, not the truth of authorship."""
    path = Path(path)
    if not path.exists():
        return [], [f'Missing {path}: supply 20 verified human samples (see evaluation/README.md).']
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (ValueError, OSError) as exc:
        return [], [str(exc)]
    samples = data.get('samples') if isinstance(data, dict) else None
    if not isinstance(samples, list) or len(samples) != 20:
        return [], ['The dataset must contain a samples list with exactly 20 entries.']
    problems = []
    for index, sample in enumerate(samples, 1):
        if not isinstance(sample, dict):
            problems.append(f'Sample {index} must be an object.')
            continue
        for field in ('id', 'text', 'source', 'verified_by', 'verification'):
            if not isinstance(sample.get(field), str) or not sample[field].strip():
                problems.append(f'Sample {index} needs a nonempty {field}.')
        if sample.get('verified_human') is not True and not (allow_unverified and sample.get('verified_human') is False):
            problems.append(f'Sample {index} needs verified_human: true after actual verification.')
    if not problems:
        if len({s['id'] for s in samples}) != 20 or len({s['text'].strip() for s in samples}) != 20:
            problems.append('Samples need distinct IDs and distinct texts; do not repeat one passage to reach 20.')
    return ([], problems) if problems else (samples, [])
