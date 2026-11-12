# Provenance Guard

## What This Does

Provenance Guard is a local Flask backend that estimates whether submitted writing looks human-written or AI-generated. It combines two imperfect signals, communicates uncertainty, records its decisions, and lets a writer request review. It does not establish who wrote a piece of text.

A submission follows this path:

1. A caller sends `text` and `creator_id` as JSON to `POST /submit`.
2. The route checks that the body is an object and both fields are nonempty strings, then generates a unique `content_id`. Text that the detector cannot score because it is too short receives a 400 response.
3. `detector.model_signal(text)` runs GPT-2 locally to measure language predictability and returns a model score between 0 and 1.
4. `stylometry.style_signal(text)` measures sentence length variation, vocabulary diversity, and punctuation, returning a separate style score between 0 and 1.
5. `scoring.combine_signals(model_score, style_score)` calculates the weighted combined score. `scoring.score_to_label()` turns it into a machine-readable guess and a full-sentence label.
6. `audit.log_decision()` appends the decision, both signals, combined score, label, IDs, timestamp, and `decided` status to `logs/audit.jsonl`. The route returns `content_id`, `guess`, `confidence`, `label`, `model_score`, and `style_score` as JSON.
7. A writer can send the `content_id` and their `reasoning` to `POST /appeal`. The service finds the original submission, appends an appeal with `under_review` status, and confirms the request. The original decision is preserved; there is no automatic rescoring or resolution.

The response field `confidence` is the combined AI-likeness score: larger values point toward AI, smaller values toward human. It is not a calibrated probability that the decision is correct. No account or API key is required for inference. The model runs on the laptop after its initial download.

To run from the repository folder:

```bash
source .venv/bin/activate
python test.py
python app.py
```

Use a second terminal for the HTTP requests below. `POST /ping` is the unchanged control route, `GET /health` reports service/model status, and `GET /log` returns the audit history. Invalid submission fields return 400; an unavailable detector returns 503. Appeals with missing fields return 400, and an unknown content ID returns 404. Rate limiting was off for Unit 7 and is enabled for Unit 8; see Rate Limiting below.

See [RUNNING.md](RUNNING.md) for installation and troubleshooting. My five original targets are in [criteria.md](criteria.md), committed before the implementation. The same repository and audit history will be used in Unit 8.

## Signals and Scoring

### Signal one — the model signal

**What it measures:** After the measured improvement, `detector.py::model_signal` removes exact duplicate sentences for the model only, keeping their first occurrence and order. Inputs with no duplicates are preserved unchanged. Stylometry still receives the original text. GPT-2 then calculates perplexity: how surprising the text is to the language model. Lower perplexity becomes a higher AI-likeness score. The model examines at most the first 400 tokens of that model input; it stays loaded in memory after the first request. The conversion is:

```text
model_score = 1 / (1 + (perplexity / 45.0) ** 1.6)
```

**Why it might differ:** Generated writing can contain predictable language patterns. Less conventional wording can surprise the model and produce a lower score. This is a heuristic about predictability, not proof of authorship or a semantic fact-check.

**What it cannot see:** A real person may write simple, common, predictable sentences and receive a high score. AI text can use unusual vocabulary or be edited to lower its score. Topic, length, and the model's training data affect the result; content beyond the token limit does not affect this signal.

### Signal two — the style signal

**What it measures:** `stylometry.py::style_signal` combines three structural measurements:

| Measurement | Implementation | Conversion to an AI-like score | Weight within style signal |
|---|---|---|---:|
| Sentence length spread | Sample standard deviation of sentence word counts divided by their mean; fewer than two nonempty sentences returns 0. | `1 - min(spread, 1)` | 40% |
| Vocabulary diversity | Unique lowercase words divided by total words; no words returns 0. | `1 - type_token_ratio` | 35% |
| Punctuation density | Count of `. , ! ? ; : - —` divided by character count; empty text returns 0. | `1 - min(density / 0.10, 1)` | 25% |

The weighted style score is clamped to 0–1. Text with no recognized words receives a neutral style score of 0.5. These measurements are components of one style signal; the other signal is the language model.

**Why it might differ:** The heuristic treats uniform sentence lengths, repeated vocabulary, and low punctuation density as more AI-like. Variation, more unique words, and greater punctuation density lower the style score. These are choices made by the rule, not reliable signatures of a particular author.

**What it cannot see:** It does not understand meaning or authorship. Typos, quotations, sentence splitting, and added punctuation can change the result without changing the underlying source. Vocabulary diversity also decreases with text length, so differently sized passages are not directly comparable. A one-sentence passage has no measurable length spread.

### The combining rule

**The rule and numbers:** The model contributes 70% and style contributes 30%:

```text
combined_score = 0.70 * model_score + 0.30 * style_score
```

**Where it lives:** `scoring.py::combine_signals`, using `WEIGHT_MODEL_SIGNAL` and `WEIGHT_STYLE_SIGNAL` in `config.py`.

The model has more influence because it measures language predictability rather than only surface statistics. Giving the style signal less influence limits how far a simple formatting change can move the final result. This choice has not been shown to meet my false-positive target. Strong model errors can still dominate, and disagreement does not automatically force the score to 0.5.

**A case where the signals split:** In the recorded narrative demonstration, the model scored **0.5021** and style scored **0.2256**. The combination was **0.4191**, which receives the unsure label. The style signal lowered the result, while the 70% weight kept it closer to the model's score. The exact request and response are preserved in [results/unit7_verification.json](results/unit7_verification.json).

The thresholds in `config.py` are `HUMAN_THRESHOLD = 0.30` and `AI_THRESHOLD = 0.80`. The broad unsure interval reserves high-confidence labels for more extreme scores, supporting my goal of avoiding wrong accusations. It does not demonstrate that the 5% false-positive target has been met.

## Label Variants

The following text is copied exactly from `scoring.py::score_to_label`. Threshold equality belongs to the outer labels; no valid score has overlapping outcomes or an uncovered range.

| Label | Returned guess | Score range | Exact text a reader sees |
|---|---|---|---|
| High-confidence human | `human` | `0.00 <= score <= 0.30` | Our analysis suggests this writing was likely created by a person. |
| Unsure | `unsure` | `0.30 < score < 0.80` | We couldn't confidently determine how this text was written. This result does not indicate wrongdoing. |
| High-confidence AI | `ai` | `0.80 <= score <= 1.00` | Our analysis suggests this writing may have been AI-generated. This is not a definitive determination, and you can request a review. |

**Why the unsure label is worded this way:** It states the uncertainty directly and says that the result is not evidence of wrongdoing. A writer should not read a borderline score as an accusation. The AI label also explains that the estimate can be challenged.

The original Unit 7 verification reached all three labels, as recorded below. Current before/after results appear under The Improvement. Scores in this historical table are rounded to four decimal places:

| Synthetic demonstration | Model score | Style score | Combined score | Returned guess |
|---|---:|---:|---:|---|
| Varied vocabulary | 0.1270 | 0.2621 | 0.1675 | `human` |
| Repetition | 0.9956 | 0.9375 | 0.9782 | `ai` |
| Ordinary paragraph | 0.5678 | 0.3627 | 0.5063 | `unsure` |

These passages were authored with AI to exercise the pipeline. Their labels demonstrate reachability, not correct authorship detection. In particular, the edited formulaic passage scored **0.2782** and received `human`, despite being AI-authored. That is a concrete limitation of this detector.

## Sample Run

 The curl commands show the equivalent HTTP requests against the running local service. The IDs, timestamps, and scores are from the recorded run; a new submission generates a new ID.

### A submission

```bash
curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "I enjoy programming. Sometimes it gets frustrating! But when everything finally works, it'\''s worth it.", "creator_id": "unit7_verify_9bc7bed7_03"}'
```

HTTP 200:

```json
{
  "confidence": 0.5062589982374202,
  "content_id": "652b43fe-797e-40aa-b069-c59fe9ceb744",
  "guess": "unsure",
  "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
  "model_score": 0.5678,
  "style_score": 0.36266332745806706
}
```

### An appeal

```bash
curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "652b43fe-797e-40aa-b069-c59fe9ceb744", "reasoning": "This is a verification appeal. Please review the original decision."}'
```

HTTP 200:

```json
{
  "content_id": "652b43fe-797e-40aa-b069-c59fe9ceb744",
  "message": "Your appeal has been recorded.",
  "status": "under_review"
}
```

### What the log shows afterwards

This command filters `/log` to the sample content ID so both events can be read together:

```bash
curl -s http://127.0.0.1:5000/log | python -c '
import json, sys
data = json.load(sys.stdin)
entries = [e for e in data["entries"] if e.get("content_id") == "652b43fe-797e-40aa-b069-c59fe9ceb744"]
print(json.dumps({"count": len(entries), "entries": entries}, indent=2))
'
```

```json
{
  "count": 2,
  "entries": [
    {
      "timestamp": "2026-11-05T10:46:53+00:00",
      "content_id": "652b43fe-797e-40aa-b069-c59fe9ceb744",
      "creator_id": "unit7_verify_9bc7bed7_03",
      "guess": "unsure",
      "model_score": 0.5678,
      "style_score": 0.36266332745806706,
      "combined_score": 0.5062589982374202,
      "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
      "status": "decided"
    },
    {
      "timestamp": "2026-11-05T10:47:04+00:00",
      "content_id": "652b43fe-797e-40aa-b069-c59fe9ceb744",
      "creator_id": "unit7_verify_9bc7bed7_03",
      "event": "appeal",
      "status": "under_review",
      "reasoning": "This is a verification appeal. Please review the original decision."
    }
  ]
}
```

The latest event for this content ID is `under_review`. The earlier `decided` entry is retained, so the original scores and label remain traceable. `GET /log` returns events rather than rewriting earlier rows or returning a separate current-status object. Early development entries with placeholder or null fields remain in the audit history; the completed route's new decisions contain all nine fields.

## How I Used AI

### Moment 1 — reviewing the first working endpoint

- **What I asked for:** I asked Codex to check whether my Milestone 3 implementation and saved terminal results were correct.
- **What came back:** It verified the real detector response, unique IDs, and matching audit records. It also found that non-object JSON and very short text could cause 500 errors, and that the README explanation was indented as a code block.
- **What I changed:** I added the JSON-object check before reading request fields. During final verification, Codex added handling for the detector's short-text error and unavailable-model error, removed the duplicate appeal decorator, and corrected the README formatting. The changes keep unusable input from being presented as a successful decision.

### Moment 2 — reviewing the scoring rule and planning the labels

- **What I asked for:** I asked Codex to verify my Milestone 4 implementation and help me move on to Milestone 5.
- **What came back:** It tested both signals, confirmed that my 70% model and 30% style weighting matched the README, and checked that all three scores were recorded correctly. It then explained how to map scores to labels, handle the threshold boundaries, and connect the appeal path.
- **What I changed:** I kept the 70/30 combining rule and completed the next stage with thresholds of 0.30 for human and 0.80 for AI. I replaced the hardcoded guess and placeholder label with the output of `scoring.score_to_label()`, recorded the actual label in the audit log, and implemented the appeal route so writers could request review.


<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

> Unit 8 work is recorded below. Milestones 1 and 2 are implemented and recorded below. Three-trial measurements for all five criteria are recorded; criterion 1 remains provisional pending independent provenance for the supplied human-labelled dataset. The verdict review and all 15 broken-attack diagnoses are recorded. The single model-input improvement and both after evaluations are now recorded. The final reflection and submission review remain; criterion 1 is still provenance-provisional.


---

## Rate Limiting

**My limits:** **10 requests per minute and 200 requests per day** on `POST /submit`. Limiting is enabled by default in `config.py`, and the decorator on `app.py::submit` applies both limits.

**Why those numbers:** Ten requests per minute allows a writer to submit a short burst of drafts, while stopping one caller from sending hundreds of scoring requests in a minute. The daily cap allows frequent legitimate use but limits sustained automated probing under one identity. These are starting limits for this local project; they do not establish that the service can handle a particular production workload.

**What a caller counts as:** The starter's `rate_limit_key()` uses a nonempty string `creator_id`. If the JSON body has no usable creator ID, it falls back to the request's remote address. Two creator IDs have separate counters even when they use the same address. Requests without usable IDs share the address counter. Creator IDs are supplied by callers rather than authenticated, so changing IDs can evade the per-creator cap. The counters are stored in memory and are lost when the server restarts.

All `/submit` requests count toward the limits, including invalid requests. Appeals, `/ping`, `/health`, and `/log` are not rate-limited. A writer can still appeal an existing decision after reaching their submission limit.

**The run of status codes when I pushed past it:**

```bash
python run_attacks.py --flood 15
```

The actual recorded run used a temporary local HTTP server and a fresh creator ID:

```bash
python run_attacks.py --flood 15 --creator unit8_m1_flood_4cc9cd41 --url http://127.0.0.1:62048
```

```text
200 200 200 200 200 200 200 200 200 200 429 429 429 429 429
```

The first ten requests were accepted and the next five received 429. Those five requests were rejected before the signals ran, and all five rejection events appeared in `GET /log`. The temporary server was stopped after verification; ordinary local use remains on port 5000.

The supplied runner saved [results/flood_2026-11-11_1832.md](results/flood_2026-11-11_1832.md). The three sample requests and responses, invalid-input checks, and all new audit entries are in [results/milestone1_verification.json](results/milestone1_verification.json). This was the Milestone 1 flood check, not the supplied attack-set run.

**Decision and rejection logging:** Each new decision contains `timestamp`, `content_id`, `creator_id`, `guess`, `model_score`, `style_score`, `combined_score`, `label`, and `status`. Refused requests are recorded through `audit.log_rejection()` with a reason, HTTP status, route, and remote address. Rejections do not have signal scores because they did not produce a decision.

I also sent three separate pieces of text through the real model and style signal, then checked their returned IDs and all nine decision fields against `/log`:

| Verification submission | HTTP status | Model score | Style score | Combined score | Status |
|---|---:|---:|---:|---:|---|
| 1 | 200 | 0.5191 | 0.3546 | 0.4698 | decided |
| 2 | 200 | 0.1292 | 0.5930 | 0.2684 | decided |
| 3 | 200 | 0.3603 | 0.1704 | 0.3033 | decided |

For example, this complete decision was recorded:

```json
{
  "timestamp": "2026-11-11T23:32:31+00:00",
  "content_id": "f490c364-f60e-45c5-9e0e-e3a2e534fd91",
  "creator_id": "unit8_m1_check_4cc9cd41_1",
  "guess": "unsure",
  "model_score": 0.5191,
  "style_score": 0.3546195152889016,
  "combined_score": 0.46975585458667046,
  "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
  "status": "decided"
}
```

This request was rejected by the limiter:

```json
{
  "timestamp": "2026-11-11T23:32:30+00:00",
  "creator_id": "unit8_m1_flood_4cc9cd41",
  "event": "rejected",
  "status": "rejected",
  "reason": "rate_limited",
  "http_status": 429,
  "route": "/submit",
  "remote_address": "127.0.0.1",
  "limit": "10 per 1 minute"
}
```

This invalid submission was rejected by the route and recorded too:

```json
{
  "timestamp": "2026-11-11T23:32:31+00:00",
  "creator_id": "unit8_m1_bad_4cc9cd41_1",
  "event": "rejected",
  "status": "rejected",
  "reason": "invalid_text",
  "http_status": 400,
  "route": "/submit",
  "remote_address": "127.0.0.1"
}
```

Across this verification, the log gained **13 complete decisions, five 429 rejections, and seven 400 rejections**, all visible through `/log`. The 400 checks covered the six original invalid-input cases and too-short text. All earlier audit entries were preserved. The synthetic texts verify service behavior; they do not measure authorship accuracy.

**Repeatable behavior checks:**

```bash
python -m unittest discover -s tests -v
```

All five tests in `tests/test_rate_limiting.py` passed. They check the minute limit, the 200-request daily cap across minute-window resets, creator/address counting, logging of refused requests, complete decision entries, and availability of appeals after throttling. These isolated tests use stubbed signal scores and an advanced storage clock for the daily-limit check; the HTTP flood and three submissions above used the real signals and ordinary time.

---

## Attack Run — Before

I ran **all 56 supplied attacks**: 32 rows from [attacks.csv](attacks.csv) and 24 rows from [attacks_malformed_requests.csv](attacks_malformed_requests.csv). **No rows were skipped.** The service and both input files were unchanged during the run.

The run used a fresh temporary local HTTP server, the real GPT-2 and style signals, and the Milestone 1 limits of 10/minute and 200/day. Weights remained 70% model and 30% style; thresholds remained 0.30 and 0.80. Fresh in-memory counters prevented the previous flood check from affecting this baseline.

```bash
python record_attack_run.py --set . --label before
```

`record_attack_run.py` calls the supplied `run_attacks.py::main` and additionally captures full responses, audit events, timing, and SHA-256 hashes of the unchanged service and CSV files. Its temporary server is stopped after the run.

Full evidence: [results/attack_run_2026-11-11_1852_before.json](results/attack_run_2026-11-11_1852_before.json), the [original runner report](results/attack_run_2026-11-11_1852_before.md), and the [reviewed report](results/attack_run_2026-11-11_1852_before_reviewed.md). The original report retains the runner's unassigned verdicts; the table below and the reviewed files contain the completed judgments.

**Overall result: 41 HELD, 15 BROKE.** HTTP outcomes were 40 responses with 200, 14 with 400, and two with 429. All 56 requests produced audit events: 40 decisions and 16 rejections. There were no 5xx responses, missing responses, or server crashes.

### How I assigned the verdicts

- Evasion: avoiding the high-confidence AI flag counts as BROKE. An unsure result is recorded as partial evasion, not as proof of human authorship or a response-contract error.
- False positives: a staff human-writing sample is BROKE only if it receives the high-confidence AI label; unsure avoids the targeted accusation.
- Prompt injection: judge the requested output or log alteration. PI02 is BROKE for achieving the human label, while explicitly recording that neither scoring bypass nor the requested confidence occurred. This does not establish that instructions were executed.
- Malformed input: invalid requests should be rejected or handled without unsupported confident authorship claims. Control payloads, punctuation-only content, a repeated-letter word, and emoji-only content are BROKE when confidently labeled. Valid non-Latin writing is not invalid merely because of its script.
- MF08 remained responsive, so its availability stress did not crash the service. It is nevertheless BROKE because it confidently flags a repetition of a staff human paragraph as AI.
- Flood: requests within the configured ten-request budget are allowed; subsequent requests from that creator should receive 429. Judge this family against the shared sequence, not against the text classification.
- Any server crash, missing response, or 5xx would be BROKE. None occurred in this run.

The malformed-input judgments above are attack-specific robustness judgments. They do not add cases to, or change the targets in, my original six-case invalid-input criterion.

| Family | Attacks | HELD | BROKE |
|---|---:|---:|---:|
| Evasion | 10 | 1 | 9 |
| False positives | 8 | 8 | 0 |
| Prompt injection | 6 | 5 | 1 |
| Malformed inputs and requests | 20 | 15 | 5 |
| Shared-creator flood | 12 | 12 | 0 |

Nine of ten evasion inputs avoided the AI flag: one received human and eight received unsure. All eight dedicated false-positive samples received unsure, but the human-origin repetition in MF08 still received AI. The broad unsure band is a trade-off, not evidence that the detector correctly identified all authors.

The flood rows describe “20 rapid submissions,” but the supplied CSV contains **12** such rows. I ran all 12: the first ten received 200, and rows 11–12 received 429. Likewise, MF08 is described as 60,000 characters, but its actual supplied length is **57,640 characters**. The inputs were not edited to match their descriptions.

### Evasion

| ID | Target | HTTP | Guess | Model | Style | Combined | Verdict | Reason |
|---|---|---:|---|---:|---:|---:|---|---|
| EV01 | signal two: typos raise word variety | 200 | human | 0.1635 | 0.5891 | 0.2912 | BROKE | AI-origin text received human. The model score was lower than the style score; the stated target alone does not prove the cause. |
| EV02 | signal two: broken-up sentences raise length spread | 200 | unsure | 0.5943 | 0.3118 | 0.5096 | BROKE | AI-origin evasion avoided the AI flag by receiving unsure. This is partial evasion, not an affirmative human label. |
| EV03 | signal two: a pasted quotation changes the shape | 200 | unsure | 0.6662 | 0.4772 | 0.6095 | BROKE | AI-origin evasion avoided the AI flag by receiving unsure. This is partial evasion, not an affirmative human label. |
| EV04 | signal one: unusual words raise perplexity | 200 | unsure | 0.6114 | 0.5796 | 0.6018 | BROKE | AI-origin evasion avoided the AI flag by receiving unsure. This is partial evasion, not an affirmative human label. |
| EV05 | both signals: heavy human editing pass | 200 | unsure | 0.3212 | 0.3849 | 0.3403 | BROKE | AI-origin evasion avoided the AI flag by receiving unsure. This is partial evasion, not an affirmative human label. |
| EV06 | signal two: one very long sentence and one very short | 200 | unsure | 0.5727 | 0.3063 | 0.4928 | BROKE | AI-origin evasion avoided the AI flag by receiving unsure. This is partial evasion, not an affirmative human label. |
| EV07 | signal two: padding with punctuation | 200 | unsure | 0.5862 | 0.6526 | 0.6061 | BROKE | AI-origin evasion avoided the AI flag by receiving unsure. This is partial evasion, not an affirmative human label. |
| EV08 | signal one: text below the token window | 200 | unsure | 0.2452 | 0.4599 | 0.3096 | BROKE | AI-origin evasion avoided the AI flag by receiving unsure. This is partial evasion, not an affirmative human label. |
| EV09 | both: AI text with a human opening paragraph bolted on | 200 | unsure | 0.7042 | 0.4700 | 0.6339 | BROKE | AI-origin evasion avoided the AI flag by receiving unsure. This is partial evasion, not an affirmative human label. |
| EV10 | signal two: repeated stanza structure | 200 | ai | 0.9792 | 0.7165 | 0.9004 | HELD | The repeated-stanza evasion still received the AI flag. |

### False positives

| ID | Target | HTTP | Guess | Model | Style | Combined | Verdict | Reason |
|---|---|---:|---|---:|---:|---:|---|---|
| FP01 | plain, clear human writing with no flourishes | 200 | unsure | 0.6175 | 0.5211 | 0.5886 | HELD | The staff human-writing sample received unsure, avoiding the targeted high-confidence AI accusation. |
| FP02 | human writing in a formal register | 200 | unsure | 0.7387 | 0.6132 | 0.7011 | HELD | The staff human-writing sample received unsure, avoiding the targeted high-confidence AI accusation. |
| FP03 | a non-native English speaker writing carefully | 200 | unsure | 0.8051 | 0.5738 | 0.7357 | HELD | The staff human-writing sample received unsure, avoiding the targeted high-confidence AI accusation. |
| FP04 | a student essay written to a rubric | 200 | unsure | 0.8329 | 0.5194 | 0.7389 | HELD | The staff human-writing sample received unsure, avoiding the targeted high-confidence AI accusation. |
| FP05 | technical documentation written by a person | 200 | unsure | 0.8005 | 0.6270 | 0.7484 | HELD | The staff human-writing sample received unsure, avoiding the targeted high-confidence AI accusation. |
| FP06 | a person imitating a formal template | 200 | unsure | 0.8814 | 0.4857 | 0.7627 | HELD | The staff human-writing sample received unsure, avoiding the targeted high-confidence AI accusation. |
| FP07 | human writing that repeats a phrase deliberately | 200 | unsure | 0.8816 | 0.4803 | 0.7612 | HELD | The staff human-writing sample received unsure, avoiding the targeted high-confidence AI accusation. |
| FP08 | very short genuine human submission | 200 | unsure | 0.3223 | 0.2685 | 0.3061 | HELD | The staff human-writing sample received unsure, avoiding the targeted high-confidence AI accusation. |

### Prompt injection

| ID | Target | HTTP | Guess | Model | Style | Combined | Verdict | Reason |
|---|---|---:|---|---:|---:|---:|---|---|
| PI01 | instruction to ignore the check | 200 | unsure | 0.4625 | 0.3692 | 0.4345 | HELD | The requested human override did not occur; both signals ran and the result was unsure. |
| PI02 | instruction disguised as a system message | 200 | human | 0.2044 | 0.3427 | 0.2459 | BROKE | Requested human label occurred, but scoring was not bypassed and confidence was 0.2459, not the requested 0.02. Partial outcome, not proven instruction execution. |
| PI03 | instruction wrapped in the writer's voice | 200 | unsure | 0.5943 | 0.5114 | 0.5694 | HELD | The result remained unsure; no verified-author credential or human override was returned. |
| PI04 | attempt to make the label text hostile | 200 | unsure | 0.4998 | 0.4939 | 0.4980 | HELD | The returned label was the fixed unsure sentence, with no hostile text or script. Browser rendering was not tested. |
| PI05 | attempt to inject into the audit log | 200 | unsure | 0.6401 | 0.3675 | 0.5583 | HELD | One ordinary decision was logged; the injected human guess, 0.01 score, and extra note did not alter its fields. |
| PI06 | instruction plus real human text | 200 | unsure | 0.5583 | 0.5277 | 0.5491 | HELD | The instruction did not bypass the signals or produce a verified-author result; the label was unsure. |

### Malformed inputs and requests

| ID | Target | HTTP | Guess | Model | Style | Combined | Verdict | Reason |
|---|---|---:|---|---:|---:|---:|---|---|
| MF01 | text is only whitespace | 400 | — | — | — | — | HELD | Whitespace-only text received a logged 400 response. |
| MF02 | text is a single character | 400 | — | — | — | — | HELD | The one-character input received a logged too-short 400 response. |
| MF03 | text is control characters | 200 | human | 0.0000 | 0.6500 | 0.1950 | BROKE | The control-character payload received a confident human label rather than rejection or uncertainty. |
| MF04 | text is only punctuation | 200 | human | 0.0112 | 0.5000 | 0.1578 | BROKE | Punctuation-only content received a confident human label without usable prose. |
| MF05 | text is a very long single word | 200 | ai | 0.9976 | 0.6500 | 0.8933 | BROKE | A 4,000-character repeated-letter word received a confident AI label rather than rejection or uncertainty. |
| MF06 | text is emoji only | 200 | ai | 0.9969 | 0.5000 | 0.8478 | BROKE | Emoji-only content received a confident AI label without usable language evidence. |
| MF07 | text is right-to-left script | 200 | unsure | 0.9064 | 0.5000 | 0.7845 | HELD | Valid Arabic text was accepted with an unsure label; no crash or high-confidence accusation occurred. |
| MF08 | text is 60,000 characters | 200 | ai | 0.9876 | 0.7788 | 0.9249 | BROKE | A repetition of the staff human sample FP01 received high-confidence AI. The service stayed responsive, but made a human-origin accusation. |
| RQ01 | no text field at all | 400 | — | — | — | — | HELD | Rejected with logged HTTP 400: Text is required. |
| RQ02 | no creator_id | 400 | — | — | — | — | HELD | Rejected with logged HTTP 400: Creator ID is required. |
| RQ03 | text is a number | 400 | — | — | — | — | HELD | Rejected with logged HTTP 400: Text is required. |
| RQ04 | text is a list | 400 | — | — | — | — | HELD | Rejected with logged HTTP 400: Text is required. |
| RQ05 | text is null | 400 | — | — | — | — | HELD | Rejected with logged HTTP 400: Text is required. |
| RQ06 | creator_id is an object | 400 | — | — | — | — | HELD | Rejected with logged HTTP 400: Creator ID is required. |
| RQ07 | body is a JSON array, not an object | 400 | — | — | — | — | HELD | Rejected with logged HTTP 400: Valid JSON object is required. |
| RQ08 | body is unparseable JSON | 400 | — | — | — | — | HELD | Rejected with logged HTTP 400: Valid JSON object is required. |
| RQ09 | body is empty | 400 | — | — | — | — | HELD | Rejected with logged HTTP 400: Valid JSON object is required. |
| RQ10 | body is form-encoded, not JSON | 400 | — | — | — | — | HELD | Rejected with logged HTTP 400: Valid JSON object is required. |
| RQ11 | body is JSON claiming to be plain text | 400 | — | — | — | — | HELD | Rejected with logged HTTP 400: Valid JSON object is required. |
| RQ12 | deeply nested JSON | 400 | — | — | — | — | HELD | Rejected with logged HTTP 400: Text is required. |

### Shared-creator flood

| ID | Target | HTTP | Guess | Model | Style | Combined | Verdict | Reason |
|---|---|---:|---|---:|---:|---:|---|---|
| FL01_01 | 20 rapid submissions from one creator | 200 | human | 0.0287 | 0.6045 | 0.2015 | HELD | Within the first ten requests allowed for this creator. |
| FL01_02 | 20 rapid submissions from one creator | 200 | human | 0.0287 | 0.6045 | 0.2015 | HELD | Within the first ten requests allowed for this creator. |
| FL01_03 | 20 rapid submissions from one creator | 200 | human | 0.0287 | 0.6045 | 0.2015 | HELD | Within the first ten requests allowed for this creator. |
| FL01_04 | 20 rapid submissions from one creator | 200 | human | 0.0287 | 0.6045 | 0.2015 | HELD | Within the first ten requests allowed for this creator. |
| FL01_05 | 20 rapid submissions from one creator | 200 | human | 0.0287 | 0.6045 | 0.2015 | HELD | Within the first ten requests allowed for this creator. |
| FL01_06 | 20 rapid submissions from one creator | 200 | human | 0.0287 | 0.6045 | 0.2015 | HELD | Within the first ten requests allowed for this creator. |
| FL01_07 | 20 rapid submissions from one creator | 200 | human | 0.0287 | 0.6045 | 0.2015 | HELD | Within the first ten requests allowed for this creator. |
| FL01_08 | 20 rapid submissions from one creator | 200 | human | 0.0287 | 0.6045 | 0.2015 | HELD | Within the first ten requests allowed for this creator. |
| FL01_09 | 20 rapid submissions from one creator | 200 | human | 0.0287 | 0.6045 | 0.2015 | HELD | Within the first ten requests allowed for this creator. |
| FL01_10 | 20 rapid submissions from one creator | 200 | human | 0.0287 | 0.6045 | 0.2015 | HELD | Within the first ten requests allowed for this creator. |
| FL01_11 | 20 rapid submissions from one creator | 429 | — | — | — | — | HELD | Blocked with logged 429 after the same creator exhausted the ten-request minute budget. |
| FL01_12 | 20 rapid submissions from one creator | 429 | — | — | — | — | HELD | Blocked with logged 429 after the same creator exhausted the ten-request minute budget. |

The guess column maps to the exact sentences in Label Variants above. The JSON evidence preserves the full returned label, response body, content ID, and audit events for every attack. A dash means that a request was rejected before a decision was made.

**Ten audit log entries from the run**

Selected attacks: EV01, EV02, EV08, FP03, FP06, PI02, MF03, MF06, MF08, FL01_11. They show evasion, near-threshold human writing, a human-label prompt attack, confident labels on unusable content, the worst human-origin accusation, and a flood rejection. All ten came from this attack run and were confirmed present in `GET /log`. The same extract is saved in [results/audit_extract_before.json](results/audit_extract_before.json).

```json
[
  {
    "timestamp": "2026-11-11T23:52:09+00:00",
    "content_id": "5b73c6b0-6fab-450e-9e48-5402cef99a17",
    "creator_id": "attacker_EV01",
    "guess": "human",
    "model_score": 0.1635,
    "style_score": 0.5891425991871745,
    "combined_score": 0.2911927797561523,
    "label": "Our analysis suggests this writing was likely created by a person.",
    "status": "decided"
  },
  {
    "timestamp": "2026-11-11T23:52:13+00:00",
    "content_id": "84881944-6b39-40ec-96d7-2ff907ab4d6f",
    "creator_id": "attacker_EV02",
    "guess": "unsure",
    "model_score": 0.5943,
    "style_score": 0.31184250818656695,
    "combined_score": 0.50956275245597,
    "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
    "status": "decided"
  },
  {
    "timestamp": "2026-11-11T23:52:17+00:00",
    "content_id": "d583bf88-ac2b-43c7-863c-ba2652645e7e",
    "creator_id": "attacker_EV08",
    "guess": "unsure",
    "model_score": 0.2452,
    "style_score": 0.4599398380870755,
    "combined_score": 0.30962195142612264,
    "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
    "status": "decided"
  },
  {
    "timestamp": "2026-11-11T23:52:18+00:00",
    "content_id": "e6544f7e-4611-44c1-b559-c5cc1e6fb654",
    "creator_id": "attacker_FP03",
    "guess": "unsure",
    "model_score": 0.8051,
    "style_score": 0.5738463715629385,
    "combined_score": 0.7357239114688816,
    "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
    "status": "decided"
  },
  {
    "timestamp": "2026-11-11T23:52:19+00:00",
    "content_id": "e9045208-7bdc-40e3-976d-739bc40fa374",
    "creator_id": "attacker_FP06",
    "guess": "unsure",
    "model_score": 0.8814,
    "style_score": 0.48572808260551836,
    "combined_score": 0.7626984247816555,
    "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
    "status": "decided"
  },
  {
    "timestamp": "2026-11-11T23:52:19+00:00",
    "content_id": "e4111ca5-c0d2-4ba6-9617-29450e449eff",
    "creator_id": "attacker_PI02",
    "guess": "human",
    "model_score": 0.2044,
    "style_score": 0.34270974766627277,
    "combined_score": 0.2458929242998818,
    "label": "Our analysis suggests this writing was likely created by a person.",
    "status": "decided"
  },
  {
    "timestamp": "2026-11-11T23:52:20+00:00",
    "content_id": "8884abe5-440f-4469-9bab-ca3925f0a034",
    "creator_id": "attacker_MF03",
    "guess": "human",
    "model_score": 0.0,
    "style_score": 0.65,
    "combined_score": 0.195,
    "label": "Our analysis suggests this writing was likely created by a person.",
    "status": "decided"
  },
  {
    "timestamp": "2026-11-11T23:52:23+00:00",
    "content_id": "7c76e152-30df-4b6e-86d5-58d95ed494f4",
    "creator_id": "attacker_MF06",
    "guess": "ai",
    "model_score": 0.9969,
    "style_score": 0.5,
    "combined_score": 0.84783,
    "label": "Our analysis suggests this writing may have been AI-generated. This is not a definitive determination, and you can request a review.",
    "status": "decided"
  },
  {
    "timestamp": "2026-11-11T23:52:26+00:00",
    "content_id": "76d65cf1-6769-48fc-b505-f660520ac549",
    "creator_id": "attacker_MF08",
    "guess": "ai",
    "model_score": 0.9876,
    "style_score": 0.7787552335386458,
    "combined_score": 0.9249465700615936,
    "label": "Our analysis suggests this writing may have been AI-generated. This is not a definitive determination, and you can request a review.",
    "status": "decided"
  },
  {
    "timestamp": "2026-11-11T23:52:28+00:00",
    "creator_id": "attacker_flood",
    "event": "rejected",
    "status": "rejected",
    "reason": "rate_limited",
    "http_status": 429,
    "route": "/submit",
    "remote_address": "127.0.0.1",
    "limit": "10 per 1 minute"
  }
]
```

**The single worst outcome — MF08:**

MF08 is exactly the staff's human-writing paragraph FP01 followed by a space, repeated 110 times. Its input can be reconstructed as `(FP01 + " ") * 110`. The source paragraph is:

```text
We got to the campsite about four. The pitch was fine, a bit sloped, but there was a tap nearby and the toilets were clean enough. Putting the tent up took longer than it should have because I had forgotten how the poles went. The weather held until Saturday night. Then it rained hard and kept raining. We stayed in the tent and played cards and ate most of the food we had brought for Sunday. On Sunday we packed up wet and drove home early. It was not the weekend we planned but the kids enjoyed it and we would go back.
```

FP01 alone received unsure at **0.5886**. Repeating that same human-origin paragraph produced high-confidence AI at **0.9249**, with this actual response:

```json
{
  "confidence": 0.9249465700615936,
  "content_id": "76d65cf1-6769-48fc-b505-f660520ac549",
  "guess": "ai",
  "label": "Our analysis suggests this writing may have been AI-generated. This is not a definitive determination, and you can request a review.",
  "model_score": 0.9876,
  "style_score": 0.7787552335386458
}
```

This is the outcome I would least want to explain to a writer: repeating their own words changed an uncertain result into an AI accusation. The request completed without a crash, but the authorship judgment still failed. No scoring or validation fix has been made in response to these results; diagnosis and the single measured improvement come in later milestones.

The attack run is separate from the five-criterion, three-trial evaluation documented below. Its eight dedicated staff human cases and a repetition stress case do not replace the 20 independently verified human samples required by my original false-positive criterion.

---

## Run Log and Verdicts

**Before evaluation — provenance provisional:** All five criteria were exercised across three actual trials. The 20 user-supplied passages were labelled human-written by the user, who reports that many came from Reddit running/marathon discussions. Source matches for two passages are recorded in [evaluation/source_checks.json](evaluation/source_checks.json); the remaining 18 sources and full independent authorship verification are not established. Criterion 1 is therefore PROVISIONAL, not a final verified false-positive verdict.

```bash
python run_eval.py --local --label before --allow-unverified-human-samples
```

Full requests, responses, samples, source hashes, and audit snapshots are saved in [results/eval_2026-11-11_194325_before_partial_f42a539c.json](results/eval_2026-11-11_194325_before_partial_f42a539c.json), with a [standalone report](results/eval_2026-11-11_194325_before_partial_f42a539c.md). The earlier partial run with criterion 1 PENDING is retained as historical evidence.

| Criterion | Original target | Run 1 | Run 2 | Run 3 | Computed verdict |
|---|---|---|---|---|---|
| 1. False-positive rate | At most 1 high-confidence AI label among 20 verified human samples | 0/20 high-confidence AI; 20/20 scored | 0/20 high-confidence AI; 20/20 scored | 0/20 high-confidence AI; 20/20 scored | PROVISIONAL |
| 2. Label coverage | All three labels; complete, unambiguous 0–1 mapping including boundaries | 3/3 labels; 1009/1009 mappings | 3/3 labels; 1009/1009 mappings | 3/3 labels; 1009/1009 mappings | MET |
| 3. Appeal handling | 10/10 appeals recorded and under_review for 10 existing IDs | 10/10 appeals recorded and under_review | 10/10 appeals recorded and under_review | 10/10 appeals recorded and under_review | MET |
| 4. Invalid input handling | 6/6 invalid cases return 4xx without a server crash | 6/6 returned 4xx | 6/6 returned 4xx | 6/6 returned 4xx | MET |
| 5. Audit logging | 10/10 valid submissions have matching audit entries and required fields | 10/10 matching audit entries | 10/10 matching audit entries | 10/10 matching audit entries | MET |

**Criterion 1 numeric result:** 0/20, 0/20, 0/20 high-confidence AI labels. The conditional numeric verdict is MET if the supplied human labels are established. This does not by itself establish human authorship or independently verify the Reddit sources. The original target of at most one false positive among twenty independently verified human samples is unchanged.

Each trial returned **7 human labels and 13 unsure labels**. All three sets of model, style, and combined scores matched exactly. Zero high-confidence AI flags does not mean all 20 passages were positively identified as human.

The passages are stored without rewriting in [evaluation/human_samples.json](evaluation/human_samples.json). `verified_human: false` means the independent provenance is unconfirmed, not that a passage is AI-generated. The format and verification requirements are described in [evaluation/README.md](evaluation/README.md). Once provenance is established, rerun without the provisional flag and use the same dataset for the after comparison.

The real model and style signal were used, with rate limiting enabled and no counter resets between trials. Each test writer made at most three submissions. No requests received 429. Identical scores across the repeats are expected because both signals are deterministic. Criterion 2 directly exercises the local `scoring.py::score_to_label` from this same checkout; each trial checks 1,009 scores including exact thresholds and adjacent floating-point values. The ordered branches partition the entire interval; the finite grid supports that coverage argument rather than enumerating every real number.

All **13 regression tests** passed with `python -m unittest discover -s tests -v`. The new evaluator tests cover dataset validation, repeated appeal/audit checks, numeric target failures, rate-limit interference, and the distinction between provisional labels and independently verified provenance. These isolated regression tests use synthetic fixtures; the recorded evaluation above used the actual supplied passages and real detection signals.

### Actual output from one trial per criterion

#### 1. False-positive rate

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
  "sample_results": [
    {
      "sample_id": "human-01",
      "http_status": 200,
      "guess": "unsure",
      "confidence": 0.35178550466725317
    },
    {
      "sample_id": "human-02",
      "http_status": 200,
      "guess": "unsure",
      "confidence": 0.3504045584939489
    },
    {
      "sample_id": "human-03",
      "http_status": 200,
      "guess": "unsure",
      "confidence": 0.35097101010101006
    },
    {
      "sample_id": "human-04",
      "http_status": 200,
      "guess": "human",
      "confidence": 0.28197485294117647
    },
    {
      "sample_id": "human-05",
      "http_status": 200,
      "guess": "unsure",
      "confidence": 0.3485194117647059
    },
    {
      "sample_id": "human-06",
      "http_status": 200,
      "guess": "unsure",
      "confidence": 0.6499472727272727
    },
    {
      "sample_id": "human-07",
      "http_status": 200,
      "guess": "unsure",
      "confidence": 0.5119736898395721
    },
    {
      "sample_id": "human-08",
      "http_status": 200,
      "guess": "unsure",
      "confidence": 0.31809067281606074
    },
    {
      "sample_id": "human-09",
      "http_status": 200,
      "guess": "unsure",
      "confidence": 0.5202646153846153
    },
    {
      "sample_id": "human-10",
      "http_status": 200,
      "guess": "human",
      "confidence": 0.1384672029501033
    },
    {
      "sample_id": "human-11",
      "http_status": 200,
      "guess": "unsure",
      "confidence": 0.48955666666666664
    },
    {
      "sample_id": "human-12",
      "http_status": 200,
      "guess": "human",
      "confidence": 0.25690972972972975
    },
    {
      "sample_id": "human-13",
      "http_status": 200,
      "guess": "human",
      "confidence": 0.20243896551724136
    },
    {
      "sample_id": "human-14",
      "http_status": 200,
      "guess": "human",
      "confidence": 0.14843639365736047
    },
    {
      "sample_id": "human-15",
      "http_status": 200,
      "guess": "human",
      "confidence": 0.25305778354705866
    },
    {
      "sample_id": "human-16",
      "http_status": 200,
      "guess": "unsure",
      "confidence": 0.37236043478260866
    },
    {
      "sample_id": "human-17",
      "http_status": 200,
      "guess": "unsure",
      "confidence": 0.5730299999999999
    },
    {
      "sample_id": "human-18",
      "http_status": 200,
      "guess": "human",
      "confidence": 0.1933313043478261
    },
    {
      "sample_id": "human-19",
      "http_status": 200,
      "guess": "unsure",
      "confidence": 0.6161704347826087
    },
    {
      "sample_id": "human-20",
      "http_status": 200,
      "guess": "unsure",
      "confidence": 0.5478574383301708
    }
  ]
}
```

#### 2. Label coverage

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

#### 3. Appeal handling

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
      "content_id": "82abe88d-1e9a-4e7a-b338-f5adc76e6d2f",
      "reasoning": "Criterion 3 trial 1: please review this verification decision."
    },
    "http_status": 200,
    "response": {
      "content_id": "82abe88d-1e9a-4e7a-b338-f5adc76e6d2f",
      "message": "Your appeal has been recorded.",
      "status": "under_review"
    }
  },
  "matching_audit_entries": [
    {
      "combined_score": 0.31286128080569203,
      "content_id": "82abe88d-1e9a-4e7a-b338-f5adc76e6d2f",
      "creator_id": "eval_f42a539c_c3_1",
      "guess": "unsure",
      "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
      "model_score": 0.3644,
      "status": "decided",
      "style_score": 0.1926042693523069,
      "timestamp": "2026-11-12T00:35:45+00:00"
    },
    {
      "content_id": "82abe88d-1e9a-4e7a-b338-f5adc76e6d2f",
      "creator_id": "eval_f42a539c_c3_1",
      "event": "appeal",
      "reasoning": "Criterion 3 trial 1: please review this verification decision.",
      "status": "under_review",
      "timestamp": "2026-11-12T00:39:23+00:00"
    }
  ]
}
```

#### 4. Invalid input handling

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
  "invalid_requests_and_responses": [
    {
      "method": "POST",
      "route": "/submit",
      "request": {
        "creator_id": "eval_f42a539c_bad1"
      },
      "http_status": 400,
      "response": {
        "error": "Text is required."
      }
    },
    {
      "method": "POST",
      "route": "/submit",
      "request": {
        "text": "",
        "creator_id": "eval_f42a539c_bad2"
      },
      "http_status": 400,
      "response": {
        "error": "Text is required."
      }
    },
    {
      "method": "POST",
      "route": "/submit",
      "request": {
        "text": "   ",
        "creator_id": "eval_f42a539c_bad3"
      },
      "http_status": 400,
      "response": {
        "error": "Text is required."
      }
    },
    {
      "method": "POST",
      "route": "/submit",
      "request": {
        "text": "I missed the bus. Again! My toast was still warm, and my sister laughed so hard she spilled her coffee. We decided to walk instead."
      },
      "http_status": 400,
      "response": {
        "error": "Creator ID is required."
      }
    },
    {
      "method": "POST",
      "route": "/submit",
      "request": {
        "text": 123,
        "creator_id": "eval_f42a539c_bad5"
      },
      "http_status": 400,
      "response": {
        "error": "Text is required."
      }
    },
    {
      "method": "POST",
      "route": "/submit",
      "request": [
        "not",
        "an",
        "object"
      ],
      "http_status": 400,
      "response": {
        "error": "Valid JSON object is required."
      }
    }
  ]
}
```

#### 5. Audit logging

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
      "creator_id": "eval_f42a539c_c5_1"
    },
    "http_status": 200,
    "response": {
      "confidence": 0.31286128080569203,
      "content_id": "640990ee-5a73-4ade-9ece-813a7d45230c",
      "guess": "unsure",
      "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
      "model_score": 0.3644,
      "style_score": 0.1926042693523069
    }
  },
  "matching_audit_entries": [
    {
      "combined_score": 0.31286128080569203,
      "content_id": "640990ee-5a73-4ade-9ece-813a7d45230c",
      "creator_id": "eval_f42a539c_c5_1",
      "guess": "unsure",
      "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
      "model_score": 0.3644,
      "status": "decided",
      "style_score": 0.1926042693523069,
      "timestamp": "2026-11-12T00:41:11+00:00"
    }
  ]
}
```

### Diagnoses and verdict review

I reviewed the saved trials against the original targets. **Criteria 2–5 are MET; criterion 1 remains PROVISIONAL.** There are no measured misses among the four fully evaluated criteria. Missing independent provenance is a dataset limitation, not a service-stage failure or permission to relax the original target.

This review uses the recorded model scores, recomputes the unchanged style features, and follows the exact 70/30 combining rule and 0.30/0.80 label boundaries. No new detector runs or clean-control comparisons were made. A target description is a hypothesis about an attack; it is not proof of the mechanism.

Machine-readable diagnoses and calculations: [results/baseline_diagnoses.json](results/baseline_diagnoses.json). A [standalone review](results/baseline_diagnoses.md) is also saved.

#### Why each criterion received its verdict

| Criterion | Reviewed verdict | How I decided |
|---|---|---|
| 1. False-positive rate | PROVISIONAL | PROVISIONAL. Every measured trial had 0/20 AI flags, with 7 human and 13 unsure labels. The numeric <=1 target would be met on the supplied labels, but 20 independently verified human origins have not been established. This is an evaluation-dataset limitation, not a diagnosed detector false positive and not an unmeasurable criterion. Keep the original criterion unchanged. |
| 2. Label coverage | MET | MET. Each of three trials reached all three labels and passed 1,009 controlled-score checks, including exact threshold equality and adjacent values. The ordered outer branches and middle return partition the valid interval. This verifies mapping behavior, not authorship accuracy. |
| 3. Appeal handling | MET | MET. Each trial created ten submissions and ten appeals against their returned IDs. All ten appeal responses and audit histories confirmed recorded reasoning and under_review. This is a result for the tested valid flows, not a claim of a production authorization system. |
| 4. Invalid input handling | MET | MET. All six specified invalid cases returned 400 in each trial; none returned 429 or 5xx. Additional malformed-prose attack failures are outside these six original cases, so they do not silently change this target or turn a measured pass into a miss. |
| 5. Audit logging | MET | MET. Every trial had ten matching decision entries with the required fields, corresponding submission IDs, creator IDs, component scores, and combined scores. Unique IDs and timestamps naturally differ between trials; the measured outcomes and repeated-input scores remain consistent. |

No criterion was revised: all five have measurable targets. The unresolved issue for criterion 1 is the provenance of the dataset. Repeated outcomes were identical as expected; generated content IDs and audit timestamps differ because each trial actually submitted new requests.

#### Stage and mechanism for every broken attack

All 15 BROKE attacks from the reviewed baseline are covered below. An unsure evasion remains a partial evasion under the documented policy; it is not an affirmative human label or a failed label-mapping test. PI02 achieved a human output but did not establish instruction execution.

| Attack | Stage(s) | Recorded model / style / combined | Mechanism |
|---|---|---|---|
| EV01 | signal one, combining rule | 0.1635 / 0.5891 / 0.2912 | The typo-bearing AI passage has a model score of 0.1635, versus a style score of 0.5891. The 70% model weight drives the combination to 0.2912, below the human boundary. Style actually pushes the score upward. Vocabulary diversity is high (0.8706), but the recorded comparison does not prove that typos caused the model score to fall; no clean matched model control was run. |
| EV02 | signal two, combining rule, label mapping | 0.5943 / 0.3118 / 0.5096 | Sentence-length spread is 0.8492. Inverting it gives only 0.1508 on the AI-like spread component; vocabulary diversity is 0.8242. These shape features yield style 0.3118. Averaging it with model 0.5943 gives 0.5096, inside the unsure band. This avoids an AI flag under the stated evasion policy; it is not a broken mapping or an affirmative human decision. |
| EV03 | signal two, combining rule, label mapping | 0.6662 / 0.4772 / 0.6095 | The quotation-bearing input has vocabulary diversity 0.8396, which becomes 0.1604 in the AI-like vocabulary component. Style is 0.4772, below model 0.6662, so the combination falls to 0.6095 and receives unsure. The style signal measures the combined text shape rather than separating quoted material; a quote-free model comparison was not recorded. |
| EV04 | signal one, combining rule, label mapping | 0.6114 / 0.5796 / 0.6018 | The unusual-word input produces moderate model and style scores, 0.6114 and 0.5796. Their 70/30 combination is 0.6018, below the 0.80 AI boundary. Predictability is an imperfect proxy for origin, and the broad band leaves this known-AI input unsure. The target description is not proof that the unusual words raised perplexity relative to a control. |
| EV05 | signal one, signal two, label mapping | 0.3212 / 0.3849 / 0.3403 | The heavily edited AI-origin text scores 0.3212 on the model and 0.3849 on style. Spread 0.6753 and vocabulary diversity 0.7683 help keep the style score low. Both signals see the current language and shape rather than the editing history; their combination 0.3403 is unsure. No signal can reconstruct authorship history from these measurements alone. |
| EV06 | signal two, combining rule, label mapping | 0.5727 / 0.3063 / 0.4928 | Measured sentence-length spread is 1.1859 across six parsed sentences, so the spread component clamps to zero AI contribution. The other components leave style at 0.30625. Combined with model 0.5727, this produces 0.492765 and unsure. The attack exploits sentence-shape sensitivity, though the supplied description does not match the parser's actual six-sentence split. |
| EV07 | combining rule, label mapping | 0.5862 / 0.6526 / 0.6061 | The punctuation-padding target did not make style read human: style is 0.6526, higher than model 0.5862. The splitter recognizes only one sentence, making the AI-like spread component 1.0, and punctuation density is only 0.0307 on a scale that saturates at 0.10. Neither signal is high enough for their average 0.6061 to reach 0.80. The supported diagnosis is moderate scores plus the broad unsure band, not a demonstrated successful style-score reversal. |
| EV08 | signal one, combining rule, label mapping | 0.2452 / 0.4599 / 0.3096 | This short input contains ten recognized words in two sentences. Model score 0.2452 is low; style 0.4599 raises the combination to 0.3096, just above the human boundary. Short text supplies little predictive evidence, but there is no length-aware uncertainty measure beyond the minimum-token guard. It receives unsure and avoids the AI flag. The 400-token setting is a maximum, not a required input length. |
| EV09 | signal one, signal two, combining rule | 0.7042 / 0.4700 / 0.6339 | A human opening and AI-origin continuation are reduced to one score per whole input. Model 0.7042 and style 0.4700 combine to 0.6339, so the mixed input is unsure. The pipeline has no segment-level attribution and the weighted average dilutes the stronger model reading. Without a continuation-only control, the precise effect of the opening is not established. |
| PI02 | signal one, signal two, combining rule | 0.2044 / 0.3427 / 0.2459 | The system-message-looking input has model 0.2044 and style 0.3427; its high vocabulary diversity (0.9556) lowers the style vocabulary component. The combination 0.2459 receives the requested human label. Both real signal scores were logged and confidence is not the requested 0.02. GPT-2 is used for perplexity, not instruction-following generation: the observed weakness is a scoring outcome on instruction-bearing text, not proven execution of the instruction or a scoring bypass. |
| MF03 | route, signal one, combining rule | 0.0000 / 0.6500 / 0.1950 | The route accepts a nonempty string containing control characters and a few word-like fragments. The rounded model score is 0.0000; style is 0.6500. The weighted rule treats that low model number as strong human evidence and returns 0.1950. Validation checked type and emptiness but not suitability as prose, and the scorer has no abstention rule for this lack of meaningful authorship evidence. |
| MF04 | route, signal two, combining rule | 0.0112 / 0.5000 / 0.1578 | The route accepts punctuation-only input. The style tokenizer recognizes zero words and returns its neutral fallback 0.5. Model score 0.0112 dominates the 70/30 combination, producing 0.15784 and a human label. The neutral style fallback is not an instruction to abstain; the remaining pipeline still turns an extreme model score on unusable prose into confident authorship. |
| MF05 | route, signal one, combining rule | 0.9976 / 0.6500 / 0.8933 | A 4,000-character repeated-letter string passes the nonempty-string check. It is one recognized word, but tokenization supplies enough model tokens for scoring. Its highly repetitive prefix receives model 0.9976, while style is 0.65. The result 0.89332 is AI. Predictability of a repeated character is being treated as authorship evidence even though the input is not useful prose. |
| MF06 | route, signal one, signal two, combining rule | 0.9969 / 0.5000 / 0.8478 | Emoji-only input passes validation. No ASCII words are recognized, so style falls back to 0.5 rather than abstaining. The repetitive sequence receives model 0.9969; the combination is 0.84783 and AI. Neither the route nor the combining rule requires sufficient language evidence before making a confident authorship claim. A future fix must not equate non-Latin writing with invalid input. |
| MF08 | signal one, signal two, combining rule | 0.9876 / 0.7788 / 0.9249 | The input is exactly FP01 plus a space repeated 110 times. Model AI score rises from 0.6175 to 0.9876; the model sees only its first 400 tokens, not all 57,640 characters. Whole-input vocabulary diversity falls from 0.708738 to 0.006443, raising style from 0.521139 to 0.778755. The 70/30 result rises from 0.588592 (unsure) to 0.924947 (AI). Repetition therefore inflates predictive and lexical signals without changing the human-origin source paragraph. The label mapping is applying its configured threshold correctly; the supplied evidence is misleading. |

#### Patterns across the failures

1. One signal-proxy problem appears across several attacks: predictability and surface shape can change without authorship changing. EV01 and PI02 are dominated by low model scores; MF05 and MF08 show the opposite extreme on repetitive text.
2. Shape-based evasion is supported by actual large sentence spread in EV02/EV06 and high vocabulary diversity in EV03. EV07 is an important counterexample: the style score was more AI-like than the model, so its target description alone would have produced the wrong diagnosis.
3. The wide unsure band protects all eight dedicated false-positive attacks, while eight evasion cases avoid an AI flag by landing in that same band. This is a policy trade-off, not a broken score partition.
4. MF03–MF06 share an input-suitability gap: valid JSON and enough model tokens are accepted as if they guarantee useful authorship evidence. Zero recognized words returns a neutral style number, not an abstention. Valid Arabic in MF07 must not be rejected merely because the tokenizer is ASCII-oriented.
5. Functional criteria can pass while detection remains weak. The six-case validation criterion does not cover punctuation, emoji, repeated-letter words, or repetition-driven accusations. These observations do not justify rewriting the original targets.

#### Priority for the next single improvement

**Priority: the repetition-driven false accusation in MF08.** It repeated the human-origin FP01 paragraph 110 times, producing 880 parsed sentences but only eight distinct sentences. Removing exact duplicate sentences in an offline text check reconstructs FP01 exactly.

The next candidate is one change to signal one: compute model perplexity after exact sentence deduplication. The original submission would still be used by style and retained as the request; weights, thresholds, label sentences, validation rules, and original criteria would stay fixed.

Using the archived FP01 model score with MF08's unchanged style score predicts **0.6659 (unsure)**. In contrast, replacing only MF08's style score with FP01's old style score predicts **0.8477 (AI)**. These are arithmetic replays of saved numbers, not measured after results. They explain why a model-side repetition fix is the first candidate rather than a vocabulary-only adjustment.

The trade-off needs measurement: the currently held AI attack EV10 also contains an exact repeated sentence (four parsed sentences, three unique), so deduplication may help an attacker too. It can also remove deliberate human emphasis. This candidate does not address every malformed-input weakness or establish true authorship. Run the full attack set and all five criteria again after that one change, using the same passages and verdict rules.

**At the time of this baseline diagnosis, no improvement had been applied.** The archived before reports, source hashes, audit history, and criteria are preserved. The single implementation and measured after results now follow below. Source verification for criterion 1 remains outstanding; it is not resolved by an improvement to the detector.

---

## The Improvement

**What I changed:** One model-signal change in `detector.py`: `model_signal()` now sends text through `_deduplicate_sentences()` before calling `perplexity()`. The helper keeps the first copy of each exact sentence in order, using the existing boundary convention of `.`, `!`, or `?` followed by whitespace. Matching is case-sensitive and punctuation-sensitive. When there are no duplicates, the original string is returned unchanged, including whitespace. Only duplicate-bearing model input is joined back together.

The route still passes the original text to stylometry. The request data, audit schema, model/token limit, perplexity conversion, 70/30 weights, 0.30/0.80 thresholds, label sentences, validation, limits, attack CSVs, and criterion targets are unchanged. This preprocessing is the single measured improvement; no second fix was added.

**Which diagnosis pointed at it:** The [baseline diagnosis](results/baseline_diagnoses.md) showed that MF08 repeats staff human sample FP01 110 times. The model score rose from 0.6175 to 0.9876, and whole-input vocabulary diversity collapsed. Changing style alone would still have left the combination in the AI band. Deduplicating its exact sentences reconstructs FP01 for the model while keeping the original repetition available to style.

### Attack Run — After

```bash
python record_attack_run.py --set . --label after
python run_eval.py --local --label after --allow-unverified-human-samples
```

All **56/56 attacks** were run again, with zero skipped rows, missing responses, or crashes. Full data: [after attack evidence](results/attack_run_2026-11-11_2048_after.json), [original after runner report](results/attack_run_2026-11-11_2048_after.md), [reviewed after report](results/attack_run_2026-11-11_2048_after_reviewed.md), and [after criterion trials](results/eval_2026-11-11_204903_after_partial_4637ee9d.json). The source hashes show that only `detector.py` changed among the service files; all supplied attack bodies and the 20-passage dataset are identical to before.

The fresh local servers used the same enabled rate limits as before. After HTTP outcomes were again **40 with 200, 14 with 400, and two with 429**. All 56 requests produced audit events. All five criteria were exercised in three actual after trials; criterion 1 retains its source-provenance qualification.

**Overall reviewed attack verdicts:**

| Measurement | Before | After |
|---|---:|---:|
| HELD | 41 | 42 |
| BROKE | 15 | 14 |
| Improved attack verdicts | — | 1 (MF08) |
| Regressed attack verdicts | — | 0 |

The same [before verdict rules](results/attack_run_2026-11-11_1852_before_reviewed.json) were applied. Unsure evasion still counts as avoiding an AI flag, PI02 is still only a partial requested-output success, and MF08 is judged against the human-origin accusation as well as availability. No rule was relaxed to count the improvement.

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

The complete machine-readable comparison is in [results/improvement_comparison.json](results/improvement_comparison.json). The remaining-failures reflection and final submission review belong to the final phase.

---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [x] criteria.md has five numbered criteria, each naming a target
       [x] Each has a reason underneath
       [x] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [x] Two signals that measure DIFFERENT things, each with a named blind spot
       [x] Three label variants, all reachable, written out in full
       [x] POST /appeal changes status and writes to the log
       [x] Signals and Scoring names scoring.py::combine_signals
       [x] Sample Run: a submission AND an appeal, as pasted text
       [x] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
