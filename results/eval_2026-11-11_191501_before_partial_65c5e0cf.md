# Criterion evaluation — before

- Producer: `run_eval.py::Evaluation.run`
- Full requests, responses, and log snapshots: [eval_2026-11-11_191501_before_partial_65c5e0cf.json](eval_2026-11-11_191501_before_partial_65c5e0cf.json)

| Criterion | Target | Run 1 | Run 2 | Run 3 | Computed verdict |
|---|---|---|---|---|---|
| 1. False-positive rate | At most 1 high-confidence AI label among 20 verified human samples | Not run: verified-human dataset missing or invalid | Not run: verified-human dataset missing or invalid | Not run: verified-human dataset missing or invalid | PENDING |
| 2. Label coverage | All three labels; complete, unambiguous 0–1 mapping including boundaries | 3/3 labels; 1009/1009 mappings | 3/3 labels; 1009/1009 mappings | 3/3 labels; 1009/1009 mappings | MET |
| 3. Appeal handling | 10/10 appeals recorded and under_review for 10 existing IDs | 10/10 appeals recorded and under_review | 10/10 appeals recorded and under_review | 10/10 appeals recorded and under_review | MET |
| 4. Invalid input handling | 6/6 invalid cases return 4xx without a server crash | 6/6 returned 4xx | 6/6 returned 4xx | 6/6 returned 4xx | MET |
| 5. Audit logging | 10/10 valid submissions have matching audit entries and required fields | 10/10 matching audit entries | 10/10 matching audit entries | 10/10 matching audit entries | MET |

Verdicts are computed from the original numeric targets; final review and diagnoses follow separately. A pending dataset is not a passing or failing trial.

## 1. False-positive rate

```json
{
  "trial": 1,
  "producer": "run_eval.py::Evaluation.run",
  "state": "PENDING",
  "measurement": "Not run: verified-human dataset missing or invalid",
  "reasons": [
    "Missing /Users/cesarestrada/ai201-project4-provenance-guard-starter-v2026/evaluation/human_samples.json: supply 20 verified human samples (see evaluation/README.md)."
  ]
}
```

## 2. Label coverage

```json
{
  "trial": 1,
  "producer": "run_eval.py::Evaluation.run",
  "state": "MET",
  "measurement": "3/3 labels; 1009/1009 mappings",
  "output": {
    "producer": "scoring.py::score_to_label",
    "boundaries": [
      {
        "score": 0.0,
        "guess": "human",
        "label": "Our analysis suggests this writing was likely created by a person.",
        "expected": "human"
      },
      {
        "score": 0.3,
        "guess": "human",
        "label": "Our analysis suggests this writing was likely created by a person.",
        "expected": "human"
      },
      {
        "score": 0.30000000000000004,
        "guess": "unsure",
        "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
        "expected": "unsure"
      },
      {
        "score": 0.7999999999999999,
        "guess": "unsure",
        "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
        "expected": "unsure"
      },
      {
        "score": 0.8,
        "guess": "ai",
        "label": "Our analysis suggests this writing may have been AI-generated. This is not a definitive determination, and you can request a review.",
        "expected": "ai"
      },
      {
        "score": 1.0,
        "guess": "ai",
        "label": "Our analysis suggests this writing may have been AI-generated. This is not a definitive determination, and you can request a review.",
        "expected": "ai"
      },
      {
        "score": 0.51,
        "guess": "unsure",
        "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
        "expected": "unsure"
      },
      {
        "score": 0.95,
        "guess": "ai",
        "label": "Our analysis suggests this writing may have been AI-generated. This is not a definitive determination, and you can request a review.",
        "expected": "ai"
      }
    ],
    "failures": [],
    "checked": 1009,
    "coverage_argument": "Ordered inclusive outer branches plus the middle return partition the entire valid interval."
  }
}
```

## 3. Appeal handling

```json
{
  "trial": 1,
  "producer": "run_eval.py::Evaluation.run",
  "state": "MET",
  "measurement": "10/10 appeals recorded and under_review",
  "output": {
    "passed": 10,
    "required": 10
  },
  "first_request_and_response": {
    "method": "POST",
    "route": "/submit",
    "request": {
      "text": "I missed the bus. Again! My toast was still warm, and my sister laughed so hard she spilled her coffee. We decided to walk instead. This is example 1.",
      "creator_id": "eval_65c5e0cf_c3_1"
    },
    "http_status": 200,
    "response": {
      "confidence": 0.31286128080569203,
      "content_id": "5f796e01-b072-4404-adc0-e3e4d4e8d979",
      "guess": "unsure",
      "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
      "model_score": 0.3644,
      "style_score": 0.1926042693523069
    }
  }
}
```

## 4. Invalid input handling

```json
{
  "trial": 1,
  "producer": "run_eval.py::Evaluation.run",
  "state": "MET",
  "measurement": "6/6 returned 4xx",
  "output": {
    "http_statuses": [
      400,
      400,
      400,
      400,
      400,
      400
    ]
  },
  "first_request_and_response": {
    "method": "POST",
    "route": "/submit",
    "request": {
      "creator_id": "eval_65c5e0cf_bad1"
    },
    "http_status": 400,
    "response": {
      "error": "Text is required."
    }
  }
}
```

## 5. Audit logging

```json
{
  "trial": 1,
  "producer": "run_eval.py::Evaluation.run",
  "state": "MET",
  "measurement": "10/10 matching audit entries",
  "output": {
    "passed": 10,
    "required": 10
  },
  "first_request_and_response": {
    "method": "POST",
    "route": "/submit",
    "request": {
      "text": "I missed the bus. Again! My toast was still warm, and my sister laughed so hard she spilled her coffee. We decided to walk instead. This is example 1.",
      "creator_id": "eval_65c5e0cf_c5_1"
    },
    "http_status": 200,
    "response": {
      "confidence": 0.31286128080569203,
      "content_id": "17657010-3dd0-40d3-a28b-748b72897b15",
      "guess": "unsure",
      "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
      "model_score": 0.3644,
      "style_score": 0.1926042693523069
    }
  }
}
```
