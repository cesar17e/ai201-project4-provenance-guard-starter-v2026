# Measured model-input improvement

## The Improvement

**What I changed:** One model-signal change in `detector.py`: `model_signal()` now sends text through `_deduplicate_sentences()` before calling `perplexity()`. The helper keeps the first copy of each exact sentence in order, using the existing boundary convention of `.`, `!`, or `?` followed by whitespace. Matching is case-sensitive and punctuation-sensitive. When there are no duplicates, the original string is returned unchanged, including whitespace. Only duplicate-bearing model input is joined back together.

The route still passes the original text to stylometry. The request data, audit schema, model/token limit, perplexity conversion, 70/30 weights, 0.30/0.80 thresholds, label sentences, validation, limits, attack CSVs, and criterion targets are unchanged. This preprocessing is the single measured improvement; no second fix was added.

**Which diagnosis pointed at it:** The [baseline diagnosis](baseline_diagnoses.md) showed that MF08 repeats staff human sample FP01 110 times. The model score rose from 0.6175 to 0.9876, and whole-input vocabulary diversity collapsed. Changing style alone would still have left the combination in the AI band. Deduplicating its exact sentences reconstructs FP01 for the model while keeping the original repetition available to style.

### Attack Run — After

```bash
python record_attack_run.py --set . --label after
python run_eval.py --local --label after --allow-unverified-human-samples
```

All **56/56 attacks** were run again, with zero skipped rows, missing responses, or crashes. Full data: [after attack evidence](attack_run_2026-11-11_2048_after.json), [original after runner report](attack_run_2026-11-11_2048_after.md), [reviewed after report](attack_run_2026-11-11_2048_after_reviewed.md), and [after criterion trials](eval_2026-11-11_204903_after_partial_4637ee9d.json). The source hashes show that only `detector.py` changed among the service files; all supplied attack bodies and the 20-passage dataset are identical to before.

The fresh local servers used the same enabled rate limits as before. After HTTP outcomes were again **40 with 200, 14 with 400, and two with 429**. All 56 requests produced audit events. All five criteria were exercised in three actual after trials; criterion 1 retains its source-provenance qualification.

**Overall reviewed attack verdicts:**

| Measurement | Before | After |
|---|---:|---:|
| HELD | 41 | 42 |
| BROKE | 15 | 14 |
| Improved attack verdicts | — | 1 (MF08) |
| Regressed attack verdicts | — | 0 |

The same [before verdict rules](attack_run_2026-11-11_1852_before_reviewed.json) were applied. Unsure evasion still counts as avoiding an AI flag, PI02 is still only a partial requested-output success, and MF08 is judged against the human-origin accusation as well as availability. No rule was relaxed to count the improvement.

**Every changed model score:**

| Attack | Model before | Model after | Combined before | Combined after | Guess before → after | Verdict before → after |
|---|---:|---:|---:|---:|---|---|
| EV02 | 0.5943 | 0.5750 | 0.5096 | 0.4961 | unsure → unsure | BROKE → BROKE |
| EV10 | 0.9792 | 0.9515 | 0.9004 | 0.8810 | ai → ai | HELD → HELD |
| MF08 | 0.9876 | 0.6175 | 0.9249 | 0.6659 | ai → unsure | BROKE → HELD |

Every attack style score was exactly unchanged. The other 53 model scores were also exactly unchanged. EV02 contained exact duplicate sentences in addition to its sentence splitting; EV10 also contained a duplicate. Both scores fell, but their labels and verdicts remained the same.

#### Every attack, before and after

Cells containing an arrow show **before → after**; scores are rounded to four decimals. The single style column applies to both runs. Full labels and unrounded values are retained in the JSON evidence and map to the unchanged Label Variants above.

##### Evasion

| ID | Target | HTTP before → after | Guess before → after | Model before → after | Style, both | Combined before → after | Verdict before → after | After interpretation |
|---|---|---|---|---|---:|---|---|---|
| EV01 | signal two: typos raise word variety | 200 → 200 | human → human | 0.1635 → 0.1635 | 0.5891 | 0.2912 → 0.2912 | BROKE → BROKE | AI-origin text received human. The model score was lower than the style score; the stated target alone does not prove the cause. |
| EV02 | signal two: broken-up sentences raise length spread | 200 → 200 | unsure → unsure | 0.5943 → 0.5750 | 0.3118 | 0.5096 → 0.4961 | BROKE → BROKE | AI-origin evasion avoided the AI flag by receiving unsure. This is partial evasion, not an affirmative human label. Model score changed after exact sentence deduplication; the label and verdict did not change. |
| EV03 | signal two: a pasted quotation changes the shape | 200 → 200 | unsure → unsure | 0.6662 → 0.6662 | 0.4772 | 0.6095 → 0.6095 | BROKE → BROKE | AI-origin evasion avoided the AI flag by receiving unsure. This is partial evasion, not an affirmative human label. |
| EV04 | signal one: unusual words raise perplexity | 200 → 200 | unsure → unsure | 0.6114 → 0.6114 | 0.5796 | 0.6018 → 0.6018 | BROKE → BROKE | AI-origin evasion avoided the AI flag by receiving unsure. This is partial evasion, not an affirmative human label. |
| EV05 | both signals: heavy human editing pass | 200 → 200 | unsure → unsure | 0.3212 → 0.3212 | 0.3849 | 0.3403 → 0.3403 | BROKE → BROKE | AI-origin evasion avoided the AI flag by receiving unsure. This is partial evasion, not an affirmative human label. |
| EV06 | signal two: one very long sentence and one very short | 200 → 200 | unsure → unsure | 0.5727 → 0.5727 | 0.3063 | 0.4928 → 0.4928 | BROKE → BROKE | AI-origin evasion avoided the AI flag by receiving unsure. This is partial evasion, not an affirmative human label. |
| EV07 | signal two: padding with punctuation | 200 → 200 | unsure → unsure | 0.5862 → 0.5862 | 0.6526 | 0.6061 → 0.6061 | BROKE → BROKE | AI-origin evasion avoided the AI flag by receiving unsure. This is partial evasion, not an affirmative human label. |
| EV08 | signal one: text below the token window | 200 → 200 | unsure → unsure | 0.2452 → 0.2452 | 0.4599 | 0.3096 → 0.3096 | BROKE → BROKE | AI-origin evasion avoided the AI flag by receiving unsure. This is partial evasion, not an affirmative human label. |
| EV09 | both: AI text with a human opening paragraph bolted on | 200 → 200 | unsure → unsure | 0.7042 → 0.7042 | 0.4700 | 0.6339 → 0.6339 | BROKE → BROKE | AI-origin evasion avoided the AI flag by receiving unsure. This is partial evasion, not an affirmative human label. |
| EV10 | signal two: repeated stanza structure | 200 → 200 | ai → ai | 0.9792 → 0.9515 | 0.7165 | 0.9004 → 0.8810 | HELD → HELD | The repeated-stanza evasion still received the AI flag. Model score changed after exact sentence deduplication; the label and verdict did not change. |

##### False positives

| ID | Target | HTTP before → after | Guess before → after | Model before → after | Style, both | Combined before → after | Verdict before → after | After interpretation |
|---|---|---|---|---|---:|---|---|---|
| FP01 | plain, clear human writing with no flourishes | 200 → 200 | unsure → unsure | 0.6175 → 0.6175 | 0.5211 | 0.5886 → 0.5886 | HELD → HELD | The staff human-writing sample received unsure, avoiding the targeted high-confidence AI accusation. |
| FP02 | human writing in a formal register | 200 → 200 | unsure → unsure | 0.7387 → 0.7387 | 0.6132 | 0.7011 → 0.7011 | HELD → HELD | The staff human-writing sample received unsure, avoiding the targeted high-confidence AI accusation. |
| FP03 | a non-native English speaker writing carefully | 200 → 200 | unsure → unsure | 0.8051 → 0.8051 | 0.5738 | 0.7357 → 0.7357 | HELD → HELD | The staff human-writing sample received unsure, avoiding the targeted high-confidence AI accusation. |
| FP04 | a student essay written to a rubric | 200 → 200 | unsure → unsure | 0.8329 → 0.8329 | 0.5194 | 0.7389 → 0.7389 | HELD → HELD | The staff human-writing sample received unsure, avoiding the targeted high-confidence AI accusation. |
| FP05 | technical documentation written by a person | 200 → 200 | unsure → unsure | 0.8005 → 0.8005 | 0.6270 | 0.7484 → 0.7484 | HELD → HELD | The staff human-writing sample received unsure, avoiding the targeted high-confidence AI accusation. |
| FP06 | a person imitating a formal template | 200 → 200 | unsure → unsure | 0.8814 → 0.8814 | 0.4857 | 0.7627 → 0.7627 | HELD → HELD | The staff human-writing sample received unsure, avoiding the targeted high-confidence AI accusation. |
| FP07 | human writing that repeats a phrase deliberately | 200 → 200 | unsure → unsure | 0.8816 → 0.8816 | 0.4803 | 0.7612 → 0.7612 | HELD → HELD | The staff human-writing sample received unsure, avoiding the targeted high-confidence AI accusation. |
| FP08 | very short genuine human submission | 200 → 200 | unsure → unsure | 0.3223 → 0.3223 | 0.2685 | 0.3061 → 0.3061 | HELD → HELD | The staff human-writing sample received unsure, avoiding the targeted high-confidence AI accusation. |

##### Prompt injection

| ID | Target | HTTP before → after | Guess before → after | Model before → after | Style, both | Combined before → after | Verdict before → after | After interpretation |
|---|---|---|---|---|---:|---|---|---|
| PI01 | instruction to ignore the check | 200 → 200 | unsure → unsure | 0.4625 → 0.4625 | 0.3692 | 0.4345 → 0.4345 | HELD → HELD | The requested human override did not occur; both signals ran and the result was unsure. |
| PI02 | instruction disguised as a system message | 200 → 200 | human → human | 0.2044 → 0.2044 | 0.3427 | 0.2459 → 0.2459 | BROKE → BROKE | Requested human label occurred, but scoring was not bypassed and confidence was 0.2459, not the requested 0.02. Partial outcome, not proven instruction execution. |
| PI03 | instruction wrapped in the writer's voice | 200 → 200 | unsure → unsure | 0.5943 → 0.5943 | 0.5114 | 0.5694 → 0.5694 | HELD → HELD | The result remained unsure; no verified-author credential or human override was returned. |
| PI04 | attempt to make the label text hostile | 200 → 200 | unsure → unsure | 0.4998 → 0.4998 | 0.4939 | 0.4980 → 0.4980 | HELD → HELD | The returned label was the fixed unsure sentence, with no hostile text or script. Browser rendering was not tested. |
| PI05 | attempt to inject into the audit log | 200 → 200 | unsure → unsure | 0.6401 → 0.6401 | 0.3675 | 0.5583 → 0.5583 | HELD → HELD | One ordinary decision was logged; the injected human guess, 0.01 score, and extra note did not alter its fields. |
| PI06 | instruction plus real human text | 200 → 200 | unsure → unsure | 0.5583 → 0.5583 | 0.5277 | 0.5491 → 0.5491 | HELD → HELD | The instruction did not bypass the signals or produce a verified-author result; the label was unsure. |

##### Malformed inputs and requests

| ID | Target | HTTP before → after | Guess before → after | Model before → after | Style, both | Combined before → after | Verdict before → after | After interpretation |
|---|---|---|---|---|---:|---|---|---|
| MF01 | text is only whitespace | 400 → 400 | — → — | — → — | — | — → — | HELD → HELD | Whitespace-only text received a logged 400 response. |
| MF02 | text is a single character | 400 → 400 | — → — | — → — | — | — → — | HELD → HELD | The one-character input received a logged too-short 400 response. |
| MF03 | text is control characters | 200 → 200 | human → human | 0.0000 → 0.0000 | 0.6500 | 0.1950 → 0.1950 | BROKE → BROKE | The control-character payload received a confident human label rather than rejection or uncertainty. |
| MF04 | text is only punctuation | 200 → 200 | human → human | 0.0112 → 0.0112 | 0.5000 | 0.1578 → 0.1578 | BROKE → BROKE | Punctuation-only content received a confident human label without usable prose. |
| MF05 | text is a very long single word | 200 → 200 | ai → ai | 0.9976 → 0.9976 | 0.6500 | 0.8933 → 0.8933 | BROKE → BROKE | A 4,000-character repeated-letter word received a confident AI label rather than rejection or uncertainty. |
| MF06 | text is emoji only | 200 → 200 | ai → ai | 0.9969 → 0.9969 | 0.5000 | 0.8478 → 0.8478 | BROKE → BROKE | Emoji-only content received a confident AI label without usable language evidence. |
| MF07 | text is right-to-left script | 200 → 200 | unsure → unsure | 0.9064 → 0.9064 | 0.5000 | 0.7845 → 0.7845 | HELD → HELD | Valid Arabic text was accepted with an unsure label; no crash or high-confidence accusation occurred. |
| MF08 | text is 60,000 characters | 200 → 200 | ai → unsure | 0.9876 → 0.6175 | 0.7788 | 0.9249 → 0.6659 | BROKE → HELD | Human-origin repetition now receives unsure instead of high-confidence AI; availability also held. This avoids the targeted accusation without asserting human authorship. |
| RQ01 | no text field at all | 400 → 400 | — → — | — → — | — | — → — | HELD → HELD | Rejected with logged HTTP 400: Text is required. |
| RQ02 | no creator_id | 400 → 400 | — → — | — → — | — | — → — | HELD → HELD | Rejected with logged HTTP 400: Creator ID is required. |
| RQ03 | text is a number | 400 → 400 | — → — | — → — | — | — → — | HELD → HELD | Rejected with logged HTTP 400: Text is required. |
| RQ04 | text is a list | 400 → 400 | — → — | — → — | — | — → — | HELD → HELD | Rejected with logged HTTP 400: Text is required. |
| RQ05 | text is null | 400 → 400 | — → — | — → — | — | — → — | HELD → HELD | Rejected with logged HTTP 400: Text is required. |
| RQ06 | creator_id is an object | 400 → 400 | — → — | — → — | — | — → — | HELD → HELD | Rejected with logged HTTP 400: Creator ID is required. |
| RQ07 | body is a JSON array, not an object | 400 → 400 | — → — | — → — | — | — → — | HELD → HELD | Rejected with logged HTTP 400: Valid JSON object is required. |
| RQ08 | body is unparseable JSON | 400 → 400 | — → — | — → — | — | — → — | HELD → HELD | Rejected with logged HTTP 400: Valid JSON object is required. |
| RQ09 | body is empty | 400 → 400 | — → — | — → — | — | — → — | HELD → HELD | Rejected with logged HTTP 400: Valid JSON object is required. |
| RQ10 | body is form-encoded, not JSON | 400 → 400 | — → — | — → — | — | — → — | HELD → HELD | Rejected with logged HTTP 400: Valid JSON object is required. |
| RQ11 | body is JSON claiming to be plain text | 400 → 400 | — → — | — → — | — | — → — | HELD → HELD | Rejected with logged HTTP 400: Valid JSON object is required. |
| RQ12 | deeply nested JSON | 400 → 400 | — → — | — → — | — | — → — | HELD → HELD | Rejected with logged HTTP 400: Text is required. |

##### Shared-creator flood

| ID | Target | HTTP before → after | Guess before → after | Model before → after | Style, both | Combined before → after | Verdict before → after | After interpretation |
|---|---|---|---|---|---:|---|---|---|
| FL01_01 | 20 rapid submissions from one creator | 200 → 200 | human → human | 0.0287 → 0.0287 | 0.6045 | 0.2015 → 0.2015 | HELD → HELD | Within the first ten requests allowed for this creator. |
| FL01_02 | 20 rapid submissions from one creator | 200 → 200 | human → human | 0.0287 → 0.0287 | 0.6045 | 0.2015 → 0.2015 | HELD → HELD | Within the first ten requests allowed for this creator. |
| FL01_03 | 20 rapid submissions from one creator | 200 → 200 | human → human | 0.0287 → 0.0287 | 0.6045 | 0.2015 → 0.2015 | HELD → HELD | Within the first ten requests allowed for this creator. |
| FL01_04 | 20 rapid submissions from one creator | 200 → 200 | human → human | 0.0287 → 0.0287 | 0.6045 | 0.2015 → 0.2015 | HELD → HELD | Within the first ten requests allowed for this creator. |
| FL01_05 | 20 rapid submissions from one creator | 200 → 200 | human → human | 0.0287 → 0.0287 | 0.6045 | 0.2015 → 0.2015 | HELD → HELD | Within the first ten requests allowed for this creator. |
| FL01_06 | 20 rapid submissions from one creator | 200 → 200 | human → human | 0.0287 → 0.0287 | 0.6045 | 0.2015 → 0.2015 | HELD → HELD | Within the first ten requests allowed for this creator. |
| FL01_07 | 20 rapid submissions from one creator | 200 → 200 | human → human | 0.0287 → 0.0287 | 0.6045 | 0.2015 → 0.2015 | HELD → HELD | Within the first ten requests allowed for this creator. |
| FL01_08 | 20 rapid submissions from one creator | 200 → 200 | human → human | 0.0287 → 0.0287 | 0.6045 | 0.2015 → 0.2015 | HELD → HELD | Within the first ten requests allowed for this creator. |
| FL01_09 | 20 rapid submissions from one creator | 200 → 200 | human → human | 0.0287 → 0.0287 | 0.6045 | 0.2015 → 0.2015 | HELD → HELD | Within the first ten requests allowed for this creator. |
| FL01_10 | 20 rapid submissions from one creator | 200 → 200 | human → human | 0.0287 → 0.0287 | 0.6045 | 0.2015 → 0.2015 | HELD → HELD | Within the first ten requests allowed for this creator. |
| FL01_11 | 20 rapid submissions from one creator | 429 → 429 | — → — | — → — | — | — → — | HELD → HELD | Blocked with logged 429 after the same creator exhausted the ten-request minute budget. |
| FL01_12 | 20 rapid submissions from one creator | 429 → 429 | — → — | — → — | — | — → — | HELD → HELD | Blocked with logged 429 after the same creator exhausted the ten-request minute budget. |

#### Five criteria across three trials, before and after

Each trial column lists the three actual measurements in order. The full JSON report preserves the requests, responses, and audit snapshots rather than copying a single trial.

| Criterion | Target | Before trials 1 / 2 / 3 | After trials 1 / 2 / 3 | Before verdict | After verdict |
|---|---|---|---|---|---|
| 1. False-positive rate | At most 1 high-confidence AI label among 20 verified human samples | 0/20 high-confidence AI; 20/20 scored; 0/20 high-confidence AI; 20/20 scored; 0/20 high-confidence AI; 20/20 scored | 0/20 high-confidence AI; 20/20 scored; 0/20 high-confidence AI; 20/20 scored; 0/20 high-confidence AI; 20/20 scored | PROVISIONAL | PROVISIONAL |
| 2. Label coverage | All three labels; complete, unambiguous 0–1 mapping including boundaries | 3/3 labels; 1009/1009 mappings; 3/3 labels; 1009/1009 mappings; 3/3 labels; 1009/1009 mappings | 3/3 labels; 1009/1009 mappings; 3/3 labels; 1009/1009 mappings; 3/3 labels; 1009/1009 mappings | MET | MET |
| 3. Appeal handling | 10/10 appeals recorded and under_review for 10 existing IDs | 10/10 appeals recorded and under_review; 10/10 appeals recorded and under_review; 10/10 appeals recorded and under_review | 10/10 appeals recorded and under_review; 10/10 appeals recorded and under_review; 10/10 appeals recorded and under_review | MET | MET |
| 4. Invalid input handling | 6/6 invalid cases return 4xx without a server crash | 6/6 returned 4xx; 6/6 returned 4xx; 6/6 returned 4xx | 6/6 returned 4xx; 6/6 returned 4xx; 6/6 returned 4xx | MET | MET |
| 5. Audit logging | 10/10 valid submissions have matching audit entries and required fields | 10/10 matching audit entries; 10/10 matching audit entries; 10/10 matching audit entries | 10/10 matching audit entries; 10/10 matching audit entries; 10/10 matching audit entries | MET | MET |

The human-labelled passages again received **7 human and 13 unsure labels** in each trial, with **0/20 high-confidence AI labels** and exactly the same model/style/combined scores as before. Their wording and metadata were not changed. Because full independent provenance remains unresolved, this is still a conditional numeric pass, not a final verified false-positive-rate claim. Criteria 2–5 remained MET; no evaluation request was rate-limited.

**Actual after response for the targeted case, MF08:**

```json
{
  "confidence": 0.6658765700615937,
  "content_id": "d73c36c4-1cff-4670-acd4-3391ba5c4e73",
  "guess": "unsure",
  "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
  "model_score": 0.6175,
  "style_score": 0.7787552335386458
}
```

**Matching after audit entry:**

```json
{
  "timestamp": "2026-11-12T01:48:17+00:00",
  "content_id": "d73c36c4-1cff-4670-acd4-3391ba5c4e73",
  "creator_id": "attacker_MF08",
  "guess": "unsure",
  "model_score": 0.6175,
  "style_score": 0.7787552335386458,
  "combined_score": 0.6658765700615937,
  "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
  "status": "decided"
}
```

**Actual after output from one trial per criterion:**

##### 1. False-positive rate

Producer: `run_eval.py::Evaluation.run`.

```json
{
  "trial": 1,
  "producer": "run_eval.py::Evaluation.run",
  "state": "PROVISIONAL",
  "conditional_verdict": "MET",
  "provenance_verified": false,
  "measurement": "0/20 high-confidence AI; 20/20 scored",
  "output": {
    "false_positives_assuming_human_labels": 0,
    "scored": 20,
    "target_maximum": 1
  },
  "label_counts": {
    "unsure": 13,
    "human": 7
  }
}
```

##### 2. Label coverage

Producer: `run_eval.py::Evaluation.run` and `scoring.py::score_to_label`.

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

##### 3. Appeal handling

Producer: `run_eval.py::Evaluation.run`.

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
  "example_appeal": {
    "method": "POST",
    "route": "/appeal",
    "request": {
      "content_id": "b386298f-ae65-4642-bf90-9365ec0aad99",
      "reasoning": "Criterion 3 trial 1: please review this verification decision."
    },
    "http_status": 200,
    "response": {
      "content_id": "b386298f-ae65-4642-bf90-9365ec0aad99",
      "message": "Your appeal has been recorded.",
      "status": "under_review"
    }
  },
  "matching_audit_entries": [
    {
      "combined_score": 0.31286128080569203,
      "content_id": "b386298f-ae65-4642-bf90-9365ec0aad99",
      "creator_id": "eval_4637ee9d_c3_1",
      "guess": "unsure",
      "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
      "model_score": 0.3644,
      "status": "decided",
      "style_score": 0.1926042693523069,
      "timestamp": "2026-11-12T01:48:59+00:00"
    },
    {
      "content_id": "b386298f-ae65-4642-bf90-9365ec0aad99",
      "creator_id": "eval_4637ee9d_c3_1",
      "event": "appeal",
      "reasoning": "Criterion 3 trial 1: please review this verification decision.",
      "status": "under_review",
      "timestamp": "2026-11-12T01:49:00+00:00"
    }
  ]
}
```

##### 4. Invalid input handling

Producer: `run_eval.py::Evaluation.run`.

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
  "example_invalid_request": {
    "method": "POST",
    "route": "/submit",
    "request": {
      "creator_id": "eval_4637ee9d_bad1"
    },
    "http_status": 400,
    "response": {
      "error": "Text is required."
    }
  }
}
```

##### 5. Audit logging

Producer: `run_eval.py::Evaluation.run`.

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
  "example_submission": {
    "method": "POST",
    "route": "/submit",
    "request": {
      "text": "I missed the bus. Again! My toast was still warm, and my sister laughed so hard she spilled her coffee. We decided to walk instead. This is example 1.",
      "creator_id": "eval_4637ee9d_c5_1"
    },
    "http_status": 200,
    "response": {
      "confidence": 0.31286128080569203,
      "content_id": "1b60710c-e455-4489-a4ec-e6f952807ea8",
      "guess": "unsure",
      "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
      "model_score": 0.3644,
      "style_score": 0.1926042693523069
    }
  },
  "matching_audit_entries": [
    {
      "combined_score": 0.31286128080569203,
      "content_id": "1b60710c-e455-4489-a4ec-e6f952807ea8",
      "creator_id": "eval_4637ee9d_c5_1",
      "guess": "unsure",
      "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
      "model_score": 0.3644,
      "status": "decided",
      "style_score": 0.1926042693523069,
      "timestamp": "2026-11-12T01:49:01+00:00"
    }
  ]
}
```

**Did it help, and how do I know:** Yes, for the targeted repeated-human-text accusation: MF08 changed from AI at 0.9249 to unsure at 0.6659, and HELD increased from 41 to 42 under the same attack rules. The observed value matches the earlier arithmetic prediction, but this section now reports the real rerun. There were no attack-verdict regressions in this supplied set, and the four fully measured criterion verdicts stayed MET.

The trade-off is visible even without a verdict regression: EV10's AI score fell from 0.9004 to 0.8810. Removing exact repetition can weaken a useful AI signal and remove deliberate emphasis. This set still has **14 broken attacks**, evasion coverage is still **1/10 HELD**, and neither the source-verification gap nor the confident labels on control characters, punctuation, repeated letters, or emoji were fixed. The method does not remove near-duplicate sentences, and its boundary heuristic does not recognize every writing system. It can also shorten repeated tiny sentences below the existing minimum token requirement. No second improvement was made.

All **18 regression tests** passed, including five checks for the new preprocessing. They confirm that MF08 reconstructs FP01 for model scoring, original nonduplicate text is preserved, case/punctuation and order remain significant, non-sentence inputs remain unchanged, and only the model's perplexity argument is transformed. Regression signal calls are stubbed; the recorded after attacks and criterion trials above used the real model.

The complete machine-readable comparison is in [results/improvement_comparison.json](improvement_comparison.json). The remaining-failures reflection and final submission review belong to the final phase.

---

