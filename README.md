# Provenance Guard

A local writing-analysis API with two detection signals, uncertainty-aware labels, an append-only audit trail, and writer appeals.

**Measured improvement:** Removing exact duplicate sentences before model scoring changed a repeated human-origin passage from **AI (0.9249)** to **unsure (0.6659)**. Across the same 56 attacks, HELD increased from **41 to 42**, with no verdict regressions in that set.

**Stack:** Python · Flask · local GPT-2/PyTorch · JSONL logging · Flask-Limiter

## What This Does

1. `POST /submit` receives `text` and `creator_id` as JSON.
2. The route validates the request and assigns a unique `content_id`.
3. `detector.model_signal()` measures predictability, after exact sentence deduplication.
4. `stylometry.style_signal()` measures the original text's sentence variation, vocabulary, and punctuation.
5. `scoring.combine_signals()` combines the signals; `score_to_label()` chooses human, unsure, or AI.
6. `audit.log_decision()` records the decision; the response returns the ID, guess, confidence, label, and both signal scores.
7. `POST /appeal` records a content ID and reasoning with `under_review` status, preserving the original decision. It does not automatically rescore the text.

The `confidence` field is an AI-likeness score, not a calibrated probability of correctness. Inference runs locally without an API key. Follow [RUNNING.md](RUNNING.md) for installation, then start the service:

```bash
source .venv/bin/activate
python test.py
python app.py
```

Use a second terminal for requests. `/ping` checks the service, `/health` reports model/limiter status, and `/log` returns audit events.

## Signals and Scoring

| Signal | What it measures and why | Blind spot |
|---|---|---|
| `detector.py::model_signal` | GPT-2 perplexity: predictable text produces a higher AI score. The model reads at most 400 tokens after deduplication. | Predictability is not authorship: plain human prose can score high; unusual or edited AI text can score low. |
| `stylometry.py::style_signal` | Sentence-length spread, vocabulary diversity, and punctuation. Uniform sentences and repeated vocabulary are treated as more AI-like. | Typos, quotations, and formatting can change the score. Vocabulary diversity depends on length; the tokenizer is ASCII-oriented. |

The style signal combines normalized measurements:

```text
style = 0.40 × (1 − min(sentence-length CV, 1))
      + 0.35 × (1 − unique words / total words)
      + 0.25 × (1 − min(punctuation density / 0.10, 1))
```

CV is sentence-length standard deviation divided by mean length; fewer than two nonempty sentences gives zero spread. No recognized words gives a neutral style score of 0.5. The final style score is clamped to 0–1.

**Combining rule:** `combined = 0.70 × model + 0.30 × style`, implemented in **`scoring.py::combine_signals`**, with weights and thresholds in `config.py`. The model has more influence; surface formatting has less. This is a design choice, not a proven accuracy advantage.

A recorded disagreement—model **0.5021**, style **0.2256**—combined to **0.4191 (unsure)**. [Original evidence](results/unit7_verification.json).

## Label Variants

These are the exact strings returned by `scoring.py::score_to_label`:

| Guess | Range | Reader-facing label |
|---|---|---|
| `human` | `0 ≤ score ≤ 0.30` | Our analysis suggests this writing was likely created by a person. |
| `unsure` | `0.30 < score < 0.80` | We couldn't confidently determine how this text was written. This result does not indicate wrongdoing. |
| `ai` | `0.80 ≤ score ≤ 1` | Our analysis suggests this writing may have been AI-generated. This is not a definitive determination, and you can request a review. |

The middle label admits uncertainty without accusing the writer. Every valid score maps to exactly one label, including both boundaries; real submissions reached all three labels in the recorded attack runs.

## Sample Run

Captured from the real after-run HTTP evaluation using a synthetic test passage. These curl commands reproduce the requests; fresh submissions receive new IDs. [Full record](results/eval_2026-11-11_204903_after_partial_4637ee9d.json).

**Submission → HTTP 200**

```bash
curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "I missed the bus. Again! My toast was still warm, and my sister laughed so hard she spilled her coffee. We decided to walk instead. This is example 1.", "creator_id": "eval_4637ee9d_c3_1"}'
```

```json
{
  "confidence": 0.31286128080569203,
  "content_id": "b386298f-ae65-4642-bf90-9365ec0aad99",
  "guess": "unsure",
  "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
  "model_score": 0.3644,
  "style_score": 0.1926042693523069
}
```

**Appeal → HTTP 200**

```bash
curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "b386298f-ae65-4642-bf90-9365ec0aad99", "reasoning": "Criterion 3 trial 1: please review this verification decision."}'
```

```json
{
  "content_id": "b386298f-ae65-4642-bf90-9365ec0aad99",
  "message": "Your appeal has been recorded.",
  "status": "under_review"
}
```

**Audit history** — the matching entries below are an excerpt from `/log`'s `entries` array. The decision remains intact; the later event records `under_review`.

```bash
curl -s http://127.0.0.1:5000/log
```

```json
[
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
```

## How I Used AI

Codex helped implement requested changes, run checks, analyze evidence, and draft this README. I supplied the original criteria and the 20 human-labelled passages.

| What I asked | What came back | What I adopted or changed |
|---|---|---|
| Review my first endpoint. | Working response/log checks; invalid-JSON and short-text failures. | Added JSON-object validation and error handling. |
| Review scoring and help with labels. | A check of the 70/30 rule, boundaries, and appeal flow. | Kept the weights; added the 0.30/0.80 labels and appeals. |
| Run attacks and three-trial evaluations. | Limiter/logging code, test tools, recorded outcomes, and a provenance gap. | Used the evidence for verdicts and stage-specific diagnoses; kept the human-source result provisional. |
| Make one measured improvement. | Model-input deduplication, full reruns, and a comparison. | Kept the targeted fix and documented its limits and the 14 remaining failures. |

## Rate Limiting

**10 requests/minute and 200/day** on `/submit`. The minute budget permits a short burst of drafts; the daily cap limits sustained probing under one identity.

A caller is a nonempty `creator_id`, with remote-address fallback. Invalid requests count too. Appeals and diagnostic routes remain available. IDs are caller-supplied and counters are in memory, so identity rotation and restarts weaken the protection.

```bash
python run_attacks.py --flood 15
```

Recorded result—ten accepted, then five blocked:

```text
200 200 200 200 200 200 200 200 200 200 429 429 429 429 429
```

Every new decision records timestamp, content ID, creator ID, guess, both signals, combined score, label, and status. Rejections record their reason, HTTP status, route, and address. [Flood report](results/flood_2026-11-11_1832.md) · [HTTP and audit checks](results/milestone1_verification.json).

## Attack Run — Before

All **56 supplied inputs** ran before any scoring fix. Both runs used real signals, fresh limiter counters, the same attack files, and the same settings except the one documented model change.

| Result | Before | After |
|---|---:|---:|
| HELD / BROKE | 41 / 15 | 42 / 14 |
| HTTP 200 / 400 / 429 | 40 / 14 / 2 | 40 / 14 / 2 |
| Skipped inputs / crashes | 0 / 0 | 0 / 0 |

**Verdict rules:** Evasion is BROKE when AI-origin text avoids the AI flag; unsure is partial evasion, not a human finding. Human-writing attacks are BROKE when wrongly flagged AI. Injection is judged against its requested effect; PI02 achieved a human label but neither skipped scoring nor proved instruction execution. Confident authorship labels on unusable prose count as malformed-input failures. Flood rows are judged against the shared ten-request budget.

**Worst outcome, MF08:** Repeating staff human sample FP01 110 times changed its result from **0.5886 unsure** to **0.9249 AI**. Predictability and vocabulary repetition increased without changing the source paragraph's origin. This was the failure chosen for the single improvement.

### All 56 attacks

One table preserves every before **and** after outcome. Arrows mark changes; a single value applies to both runs. Scores are rounded to four decimals; `—` means rejected before scoring. Exact labels are defined above. Full responses, IDs, precision, and review rationales: [before](results/attack_run_2026-11-11_1852_before_reviewed.md) · [after](results/attack_run_2026-11-11_2048_after_reviewed.md) · [machine-readable comparison](results/improvement_comparison.json).

<details>
<summary>Expand all 56 before/after outcomes</summary>

| ID | Target | HTTP, both | Model B → A | Style, both | Combined / guess B → A | Verdict B → A |
|---|---|---:|---|---:|---|---|
| EV01 | typos raise word variety | 200 | 0.1635 | 0.5891 | 0.2912 / human | BROKE |
| EV02 | broken-up sentences raise length spread | 200 | 0.5943 → 0.5750 | 0.3118 | 0.5096 / unsure → 0.4961 / unsure | BROKE |
| EV03 | a pasted quotation changes the shape | 200 | 0.6662 | 0.4772 | 0.6095 / unsure | BROKE |
| EV04 | unusual words raise perplexity | 200 | 0.6114 | 0.5796 | 0.6018 / unsure | BROKE |
| EV05 | heavy human editing pass | 200 | 0.3212 | 0.3849 | 0.3403 / unsure | BROKE |
| EV06 | one very long sentence and one very short | 200 | 0.5727 | 0.3063 | 0.4928 / unsure | BROKE |
| EV07 | padding with punctuation | 200 | 0.5862 | 0.6526 | 0.6061 / unsure | BROKE |
| EV08 | text below the token window | 200 | 0.2452 | 0.4599 | 0.3096 / unsure | BROKE |
| EV09 | AI text with a human opening paragraph bolted on | 200 | 0.7042 | 0.4700 | 0.6339 / unsure | BROKE |
| EV10 | repeated stanza structure | 200 | 0.9792 → 0.9515 | 0.7165 | 0.9004 / ai → 0.8810 / ai | HELD |
| FP01 | plain, clear human writing with no flourishes | 200 | 0.6175 | 0.5211 | 0.5886 / unsure | HELD |
| FP02 | human writing in a formal register | 200 | 0.7387 | 0.6132 | 0.7011 / unsure | HELD |
| FP03 | a non-native English speaker writing carefully | 200 | 0.8051 | 0.5738 | 0.7357 / unsure | HELD |
| FP04 | a student essay written to a rubric | 200 | 0.8329 | 0.5194 | 0.7389 / unsure | HELD |
| FP05 | technical documentation written by a person | 200 | 0.8005 | 0.6270 | 0.7484 / unsure | HELD |
| FP06 | a person imitating a formal template | 200 | 0.8814 | 0.4857 | 0.7627 / unsure | HELD |
| FP07 | human writing that repeats a phrase deliberately | 200 | 0.8816 | 0.4803 | 0.7612 / unsure | HELD |
| FP08 | very short genuine human submission | 200 | 0.3223 | 0.2685 | 0.3061 / unsure | HELD |
| PI01 | instruction to ignore the check | 200 | 0.4625 | 0.3692 | 0.4345 / unsure | HELD |
| PI02 | instruction disguised as a system message | 200 | 0.2044 | 0.3427 | 0.2459 / human | BROKE |
| PI03 | instruction wrapped in the writer's voice | 200 | 0.5943 | 0.5114 | 0.5694 / unsure | HELD |
| PI04 | attempt to make the label text hostile | 200 | 0.4998 | 0.4939 | 0.4980 / unsure | HELD |
| PI05 | attempt to inject into the audit log | 200 | 0.6401 | 0.3675 | 0.5583 / unsure | HELD |
| PI06 | instruction plus real human text | 200 | 0.5583 | 0.5277 | 0.5491 / unsure | HELD |
| MF01 | text is only whitespace | 400 | — | — | — | HELD |
| MF02 | text is a single character | 400 | — | — | — | HELD |
| MF03 | text is control characters | 200 | 0.0000 | 0.6500 | 0.1950 / human | BROKE |
| MF04 | text is only punctuation | 200 | 0.0112 | 0.5000 | 0.1578 / human | BROKE |
| MF05 | text is a very long single word | 200 | 0.9976 | 0.6500 | 0.8933 / ai | BROKE |
| MF06 | text is emoji only | 200 | 0.9969 | 0.5000 | 0.8478 / ai | BROKE |
| MF07 | text is right-to-left script | 200 | 0.9064 | 0.5000 | 0.7845 / unsure | HELD |
| MF08 | text is 60,000 characters | 200 | 0.9876 → 0.6175 | 0.7788 | 0.9249 / ai → 0.6659 / unsure | BROKE → HELD |
| RQ01 | no text field at all | 400 | — | — | — | HELD |
| RQ02 | no creator_id | 400 | — | — | — | HELD |
| RQ03 | text is a number | 400 | — | — | — | HELD |
| RQ04 | text is a list | 400 | — | — | — | HELD |
| RQ05 | text is null | 400 | — | — | — | HELD |
| RQ06 | creator_id is an object | 400 | — | — | — | HELD |
| RQ07 | body is a JSON array, not an object | 400 | — | — | — | HELD |
| RQ08 | body is unparseable JSON | 400 | — | — | — | HELD |
| RQ09 | body is empty | 400 | — | — | — | HELD |
| RQ10 | body is form-encoded, not JSON | 400 | — | — | — | HELD |
| RQ11 | body is JSON claiming to be plain text | 400 | — | — | — | HELD |
| RQ12 | deeply nested JSON | 400 | — | — | — | HELD |
| FL01_01 | Shared-creator flood 01 | 200 | 0.0287 | 0.6045 | 0.2015 / human | HELD |
| FL01_02 | Shared-creator flood 02 | 200 | 0.0287 | 0.6045 | 0.2015 / human | HELD |
| FL01_03 | Shared-creator flood 03 | 200 | 0.0287 | 0.6045 | 0.2015 / human | HELD |
| FL01_04 | Shared-creator flood 04 | 200 | 0.0287 | 0.6045 | 0.2015 / human | HELD |
| FL01_05 | Shared-creator flood 05 | 200 | 0.0287 | 0.6045 | 0.2015 / human | HELD |
| FL01_06 | Shared-creator flood 06 | 200 | 0.0287 | 0.6045 | 0.2015 / human | HELD |
| FL01_07 | Shared-creator flood 07 | 200 | 0.0287 | 0.6045 | 0.2015 / human | HELD |
| FL01_08 | Shared-creator flood 08 | 200 | 0.0287 | 0.6045 | 0.2015 / human | HELD |
| FL01_09 | Shared-creator flood 09 | 200 | 0.0287 | 0.6045 | 0.2015 / human | HELD |
| FL01_10 | Shared-creator flood 10 | 200 | 0.0287 | 0.6045 | 0.2015 / human | HELD |
| FL01_11 | Shared-creator flood 11 | 429 | — | — | — | HELD |
| FL01_12 | Shared-creator flood 12 | 429 | — | — | — | HELD |

</details>

The supplied files contain **12 flood rows**, despite their “20 rapid submissions” description; rows 11–12 received 429. MF08 contains **57,640 characters**, despite its “60,000” description. All supplied rows were run unchanged.

<details>
<summary>Ten before-run audit entries, including a 429 rejection</summary>

Selected attacks: EV01, EV02, EV08, FP03, FP06, PI02, MF03, MF06, MF08, FL01_11. These show the interesting failures and near-threshold cases. [Readable extract](results/audit_extract_before.json).

```json
[
  {"timestamp":"2026-11-11T23:52:09+00:00","content_id":"5b73c6b0-6fab-450e-9e48-5402cef99a17","creator_id":"attacker_EV01","guess":"human","model_score":0.1635,"style_score":0.5891425991871745,"combined_score":0.2911927797561523,"label":"Our analysis suggests this writing was likely created by a person.","status":"decided"},
  {"timestamp":"2026-11-11T23:52:13+00:00","content_id":"84881944-6b39-40ec-96d7-2ff907ab4d6f","creator_id":"attacker_EV02","guess":"unsure","model_score":0.5943,"style_score":0.31184250818656695,"combined_score":0.50956275245597,"label":"We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.","status":"decided"},
  {"timestamp":"2026-11-11T23:52:17+00:00","content_id":"d583bf88-ac2b-43c7-863c-ba2652645e7e","creator_id":"attacker_EV08","guess":"unsure","model_score":0.2452,"style_score":0.4599398380870755,"combined_score":0.30962195142612264,"label":"We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.","status":"decided"},
  {"timestamp":"2026-11-11T23:52:18+00:00","content_id":"e6544f7e-4611-44c1-b559-c5cc1e6fb654","creator_id":"attacker_FP03","guess":"unsure","model_score":0.8051,"style_score":0.5738463715629385,"combined_score":0.7357239114688816,"label":"We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.","status":"decided"},
  {"timestamp":"2026-11-11T23:52:19+00:00","content_id":"e9045208-7bdc-40e3-976d-739bc40fa374","creator_id":"attacker_FP06","guess":"unsure","model_score":0.8814,"style_score":0.48572808260551836,"combined_score":0.7626984247816555,"label":"We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.","status":"decided"},
  {"timestamp":"2026-11-11T23:52:19+00:00","content_id":"e4111ca5-c0d2-4ba6-9617-29450e449eff","creator_id":"attacker_PI02","guess":"human","model_score":0.2044,"style_score":0.34270974766627277,"combined_score":0.2458929242998818,"label":"Our analysis suggests this writing was likely created by a person.","status":"decided"},
  {"timestamp":"2026-11-11T23:52:20+00:00","content_id":"8884abe5-440f-4469-9bab-ca3925f0a034","creator_id":"attacker_MF03","guess":"human","model_score":0.0,"style_score":0.65,"combined_score":0.195,"label":"Our analysis suggests this writing was likely created by a person.","status":"decided"},
  {"timestamp":"2026-11-11T23:52:23+00:00","content_id":"7c76e152-30df-4b6e-86d5-58d95ed494f4","creator_id":"attacker_MF06","guess":"ai","model_score":0.9969,"style_score":0.5,"combined_score":0.84783,"label":"Our analysis suggests this writing may have been AI-generated. This is not a definitive determination, and you can request a review.","status":"decided"},
  {"timestamp":"2026-11-11T23:52:26+00:00","content_id":"76d65cf1-6769-48fc-b505-f660520ac549","creator_id":"attacker_MF08","guess":"ai","model_score":0.9876,"style_score":0.7787552335386458,"combined_score":0.9249465700615936,"label":"Our analysis suggests this writing may have been AI-generated. This is not a definitive determination, and you can request a review.","status":"decided"},
  {"timestamp":"2026-11-11T23:52:28+00:00","creator_id":"attacker_flood","event":"rejected","status":"rejected","reason":"rate_limited","http_status":429,"route":"/submit","remote_address":"127.0.0.1","limit":"10 per 1 minute"}
]
```

</details>

## Run Log and Verdicts

Five original targets, three real trials **before (B1–B3)** and **after (A1–A3)**. [Before output](results/eval_2026-11-11_194325_before_partial_f42a539c.json) · [After output](results/eval_2026-11-11_204903_after_partial_4637ee9d.json) · [Original criteria and reasons](criteria.md).

| Criterion | Target | B1 | B2 | B3 | A1 | A2 | A3 | Verdict, both runs |
|---|---|---|---|---|---|---|---|---|
| 1. Human samples flagged AI | ≤1/20 | 0/20 | 0/20 | 0/20 | 0/20 | 0/20 | 0/20 | PROVISIONAL |
| 2. Label coverage | All 3; complete boundary mapping | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | MET |
| 3. Appeals recorded and under review | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 | MET |
| 4. Invalid cases return 4xx | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 | MET |
| 5. Matching complete audit entries | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 | MET |

MET requires the target to hold in every trial. Each label trial checked **1,009 scores**, including exact thresholds and adjacent values; the code's ordered branches cover the full interval. All ten appeals matched recorded reasoning and `under_review`; all audit IDs and required fields matched the responses. All six invalid cases returned **400**, with no 429 masking or server crashes. They were missing, empty, whitespace-only, or non-string text, missing creator ID, and a non-object JSON body.

**Provenance qualification:** The 20 passages were supplied as human-written, reportedly from Reddit running discussions. Two source matches are recorded; 18 remain untraced. Each trial produced **7 human and 13 unsure labels**, not 20 positive human identifications. The numeric false-positive condition would be met on those labels, but independent verification is incomplete. [Dataset and source status](evaluation/README.md).

Both signals are deterministic; repeated scores matched exactly. Each test writer submitted at most three times, limits stayed enabled, and counters were not reset between trials. Controlled mapping checks called the local `scoring.py::score_to_label`; the other criteria used real HTTP and the real model.

<details>
<summary>Actual JSON excerpts: one trial per criterion, before and after</summary>

Producer: `run_eval.py::Evaluation.run`; mapping output also comes from `scoring.py::score_to_label`. These excerpts copy the recorded state, measurement, and output fields. The linked reports retain every request, response, and audit snapshot.

```json
[
  {"criterion":1,"before":{"trial":1,"producer":"run_eval.py::Evaluation.run","state":"PROVISIONAL","measurement":"0/20 high-confidence AI; 20/20 scored","output":{"false_positives_assuming_human_labels":0,"scored":20,"target_maximum":1},"conditional_verdict":"MET","provenance_verified":false},"after":{"trial":1,"producer":"run_eval.py::Evaluation.run","state":"PROVISIONAL","measurement":"0/20 high-confidence AI; 20/20 scored","output":{"false_positives_assuming_human_labels":0,"scored":20,"target_maximum":1},"conditional_verdict":"MET","provenance_verified":false}},
  {"criterion":2,"before":{"trial":1,"producer":"run_eval.py::Evaluation.run","state":"MET","measurement":"3/3 labels; 1009/1009 mappings","output":{"producer":"scoring.py::score_to_label","boundaries":[{"score":0.0,"guess":"human","label":"Our analysis suggests this writing was likely created by a person.","expected":"human"},{"score":0.3,"guess":"human","label":"Our analysis suggests this writing was likely created by a person.","expected":"human"},{"score":0.30000000000000004,"guess":"unsure","label":"We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.","expected":"unsure"},{"score":0.7999999999999999,"guess":"unsure","label":"We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.","expected":"unsure"},{"score":0.8,"guess":"ai","label":"Our analysis suggests this writing may have been AI-generated. This is not a definitive determination, and you can request a review.","expected":"ai"},{"score":1.0,"guess":"ai","label":"Our analysis suggests this writing may have been AI-generated. This is not a definitive determination, and you can request a review.","expected":"ai"},{"score":0.51,"guess":"unsure","label":"We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.","expected":"unsure"},{"score":0.95,"guess":"ai","label":"Our analysis suggests this writing may have been AI-generated. This is not a definitive determination, and you can request a review.","expected":"ai"}],"failures":[],"checked":1009,"coverage_argument":"Ordered inclusive outer branches plus the middle return partition the entire valid interval."}},"after":{"trial":1,"producer":"run_eval.py::Evaluation.run","state":"MET","measurement":"3/3 labels; 1009/1009 mappings","output":{"producer":"scoring.py::score_to_label","boundaries":[{"score":0.0,"guess":"human","label":"Our analysis suggests this writing was likely created by a person.","expected":"human"},{"score":0.3,"guess":"human","label":"Our analysis suggests this writing was likely created by a person.","expected":"human"},{"score":0.30000000000000004,"guess":"unsure","label":"We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.","expected":"unsure"},{"score":0.7999999999999999,"guess":"unsure","label":"We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.","expected":"unsure"},{"score":0.8,"guess":"ai","label":"Our analysis suggests this writing may have been AI-generated. This is not a definitive determination, and you can request a review.","expected":"ai"},{"score":1.0,"guess":"ai","label":"Our analysis suggests this writing may have been AI-generated. This is not a definitive determination, and you can request a review.","expected":"ai"},{"score":0.51,"guess":"unsure","label":"We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.","expected":"unsure"},{"score":0.95,"guess":"ai","label":"Our analysis suggests this writing may have been AI-generated. This is not a definitive determination, and you can request a review.","expected":"ai"}],"failures":[],"checked":1009,"coverage_argument":"Ordered inclusive outer branches plus the middle return partition the entire valid interval."}}},
  {"criterion":3,"before":{"trial":1,"producer":"run_eval.py::Evaluation.run","state":"MET","measurement":"10/10 appeals recorded and under_review","output":{"passed":10,"required":10}},"after":{"trial":1,"producer":"run_eval.py::Evaluation.run","state":"MET","measurement":"10/10 appeals recorded and under_review","output":{"passed":10,"required":10}}},
  {"criterion":4,"before":{"trial":1,"producer":"run_eval.py::Evaluation.run","state":"MET","measurement":"6/6 returned 4xx","output":{"http_statuses":[400,400,400,400,400,400]}},"after":{"trial":1,"producer":"run_eval.py::Evaluation.run","state":"MET","measurement":"6/6 returned 4xx","output":{"http_statuses":[400,400,400,400,400,400]}}},
  {"criterion":5,"before":{"trial":1,"producer":"run_eval.py::Evaluation.run","state":"MET","measurement":"10/10 matching audit entries","output":{"passed":10,"required":10}},"after":{"trial":1,"producer":"run_eval.py::Evaluation.run","state":"MET","measurement":"10/10 matching audit entries","output":{"passed":10,"required":10}}}
]
```

</details>

### Diagnoses

The four fully evaluated criteria had no measured misses. Criterion 1's gap is dataset provenance, not a diagnosed signal failure. No criterion was revised. All **15 broken baseline attacks** have a stage-and-mechanism diagnosis below; [full calculations](results/baseline_diagnoses.md) preserve the detail.

<details>
<summary>Stage and mechanism for every broken baseline attack</summary>

| Attack | Stage(s) | Mechanism supported by the recorded evidence |
|---|---|---|
| EV01 | Model; combining rule | Model 0.1635 outweighs style 0.5891 and pushes the result below 0.30. No paired control proves typos alone caused the drop. |
| EV02 | Style; combining rule | Spread 0.8492 becomes only 0.1508 on the AI-like spread component; low style pulls the model reading into unsure. |
| EV03 | Style; combining rule | Vocabulary diversity 0.8396 lowers style. Quotes and prose are measured together, producing an unsure result. |
| EV04 | Model; label mapping | Both signals are moderate; their 0.6018 combination never reaches 0.80. Rare-word causality remains unproven without a control. |
| EV05 | Both signals | Edited AI-origin text scores 0.3212/0.3849. Current language and shape cannot reconstruct its editing history. |
| EV06 | Style; combining rule | Spread 1.1859 clamps the AI-like spread component to zero; style 0.30625 lowers the result to unsure. |
| EV07 | Combining rule; labels | Style 0.6526 is more AI-like than model 0.5862. The supported issue is moderate scores plus the wide band, not a demonstrated style reversal. |
| EV08 | Model; labels | Ten words provide little context: model 0.2452 leaves the combined result at 0.3096, just above the human boundary. |
| EV09 | Both signals; combining rule | Whole-input scores blend the human opening with AI text; there is no segment-level attribution. |
| PI02 | Both signals; combining rule | Low scores produce the requested human label, but both signals ran and confidence was 0.2459, not the requested 0.02. No instruction execution is established. |
| MF03 | Route; model; combining rule | Control characters pass the nonempty check. Rounded model score 0.0 combines with style 0.65 to yield human. |
| MF04 | Route; style; combining rule | Zero recognized words triggers neutral style 0.5, not abstention. The near-zero model score then produces human. |
| MF05 | Route; model | A repeated-letter word passes validation. Its predictable prefix scores 0.9976 on the model and produces AI. |
| MF06 | Route; both signals | Emoji yields no recognized words and style falls back to 0.5; model 0.9969 still pushes the result into AI. |
| MF08 | Both signals; combining rule | Repetition raises model predictability and collapses vocabulary diversity from 0.7087 to 0.0064, despite unchanged source authorship. |

</details>

These failures cluster around **predictability mistaken for authorship**, **editable surface statistics**, and **confident scoring of unsuitable prose**. The wide unsure band protects human-writing cases while allowing partial evasion; passing functional criteria does not establish detection accuracy.

## The Improvement

**One change, driven by MF08:** `detector.py::_deduplicate_sentences` keeps the first occurrence of each exact sentence before model perplexity is computed. Case, punctuation, and order matter; nonduplicate input is preserved unchanged. Style still receives the original text. Weights, thresholds, labels, limits, validation, datasets, and targets stayed fixed.

### Attack Run — After

```bash
python record_attack_run.py --set . --label after
python run_eval.py --local --label after --allow-unverified-human-samples
```

Every after outcome appears in the [56-attack comparison](#all-56-attacks); all three after criterion trials appear in the table above. [Full comparison](results/improvement_comparison.md) · [Raw after responses](results/attack_run_2026-11-11_2048_after.json).

Only three model scores changed; every style score and the other 53 model scores stayed identical:

| Attack | Model before → after | Combined before → after | Label before → after | Verdict before → after |
|---|---|---|---|---|
| EV02 | 0.5943 → 0.5750 | 0.5096 → 0.4961 | unsure → unsure | BROKE → BROKE |
| EV10 | 0.9792 → 0.9515 | 0.9004 → 0.8810 | ai → ai | HELD → HELD |
| MF08 | 0.9876 → 0.6175 | 0.9249 → 0.6659 | ai → unsure | BROKE → HELD |

**Outcome:** MF08 became unsure, correcting the targeted human-origin accusation with no verdict regressions in this set. Evasion coverage remained **1/10 HELD**; the human-sample criterion stayed provisional and 14 attacks remained broken.

The trade-off is visible: EV10's AI score fell from 0.9004 to 0.8810, though it stayed above the AI threshold. Deduplication can weaken useful repetition evidence or remove deliberate emphasis; it misses near-duplicates and can shorten tiny repeated sentences below the model's minimum context. No second fix was added.

**Verification:** 18 regression tests and 9 environment checks passed. Five new regression checks cover deduplication, original-input preservation, exact matching, and model-only preprocessing. Unit tests use isolated fixtures; both recorded evaluations used real signals.

```bash
python -m unittest discover -s tests -v
```

## What's Still Broken

The after run still has **14 BROKE attacks**. I stopped after one isolated change to preserve a measurable comparison; the proposals below are not implemented or claimed successes. [Case-by-case review](results/final_review.json).

| Remaining attacks | Next step | Why deferred |
|---|---|---|
| EV01, EV04 | Test matched clean/noisy vocabulary pairs before model recalibration. | Causality needs controls; another model change would confound this measurement. |
| EV02, EV06 | Test sentence-variation reliability by sample size. | A separate style-rule experiment is needed. |
| EV03 | Test quote-aware segmentation. | No quote-free matched control is recorded. |
| EV05, EV09 | Evaluate mixed-origin segments and provenance; preserve uncertainty. | Text patterns cannot reconstruct editing history. |
| EV07 | Compare punctuation padding against the original. | Style did not reverse as the attack description suggested. |
| EV08 | Retain unsure or request more context. | Forcing certainty on ten words risks accusing real writers. |
| PI02 | Test matched system-looking prefixes; continue treating them as text. | Scoring was not bypassed; instruction execution was not shown. |
| MF03 | Reject unsupported non-whitespace control characters. | This would be an additional route change. |
| MF04, MF06 | Test Unicode-aware suitability checks or abstention. | An ASCII-only guard could reject legitimate languages. |
| MF05 | Test abstention on extreme repeated-character runs. | Character-level handling is outside the measured sentence fix. |

**Unresolved criterion:** Collect individual sources and verification evidence for all 20 human-labelled passages, including the 18 still untraced, then evaluate both implementations with the same verified texts. Until then, criterion 1 remains PROVISIONAL; its target is unchanged. [Source checks](evaluation/source_checks.json).

**The trade I'd make in production:** I would keep a wide unsure band and send disputed decisions to human review instead of automatically penalizing writers. More AI-assisted text would get through and the platform would bear extra review costs, while real writers would face fewer unsupported accusations.

**Submission:** The same repository has the required commit history and saved before/after evidence. Resolve the provenance qualification, commit and push the final documentation, and submit [this repository](https://github.com/cesar17e/ai201-project4-provenance-guard-starter-v2026) through the Course Portal. Portal submission is not confirmed.
