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

**What it measures:** `detector.py::model_signal` uses GPT-2 to calculate perplexity: how surprising the text is to the language model. Lower perplexity becomes a higher AI-likeness score. The model examines at most the first 400 tokens; it stays loaded in memory after the first request. The conversion is:

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

Real submissions reached all three labels during verification. Scores in this table are rounded to four decimal places:

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

> Unit 8 work is recorded below. Milestones 1 and 2 are implemented and recorded below. The criterion trials, diagnoses, improvement, and final reflection will be completed during the remaining milestones.


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

These attack results do not yet supply the five-criterion, three-trial evaluation. In particular, eight dedicated staff human cases and a repetition stress case do not replace the 20 independently verified human samples required by my original false-positive criterion.

---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

```

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



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
