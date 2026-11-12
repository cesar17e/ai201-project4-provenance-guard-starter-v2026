# Reviewed baseline attack run

## Attack Run — Before

I ran **all 56 supplied attacks**: 32 rows from [attacks.csv](../attacks.csv) and 24 rows from [attacks_malformed_requests.csv](../attacks_malformed_requests.csv). **No rows were skipped.** The service and both input files were unchanged during the run.

The run used a fresh temporary local HTTP server, the real GPT-2 and style signals, and the Milestone 1 limits of 10/minute and 200/day. Weights remained 70% model and 30% style; thresholds remained 0.30 and 0.80. Fresh in-memory counters prevented the previous flood check from affecting this baseline.

```bash
python record_attack_run.py --set . --label before
```

`record_attack_run.py` calls the supplied `run_attacks.py::main` and additionally captures full responses, audit events, timing, and SHA-256 hashes of the unchanged service and CSV files. Its temporary server is stopped after the run.

Full evidence: [results/attack_run_2026-11-11_1852_before.json](attack_run_2026-11-11_1852_before.json), the [original runner report](attack_run_2026-11-11_1852_before.md), and the [reviewed report](attack_run_2026-11-11_1852_before_reviewed.md). The original report retains the runner's unassigned verdicts; the table below and the reviewed files contain the completed judgments.

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

Selected attacks: EV01, EV02, EV08, FP03, FP06, PI02, MF03, MF06, MF08, FL01_11. They show evasion, near-threshold human writing, a human-label prompt attack, confident labels on unusable content, the worst human-origin accusation, and a flood rejection. All ten came from this attack run and were confirmed present in `GET /log`. The same extract is saved in [results/audit_extract_before.json](audit_extract_before.json).

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

