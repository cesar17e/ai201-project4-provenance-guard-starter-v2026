# Attack run — after

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-11-11 20:48
- Auto-marked BROKE (5xx, crash, no response): **0**
- Left for you to judge: **56**

The Verdict column is blank where a script can't honestly decide. Whether
an evasion worked depends on where you put your thresholds — read the
`targets` column, look at what came back, and write HELD or BROKE yourself.

Each attack submits as creator_id `attacker_<id>`, and the content_id it
came back with is in the table — either one will match this run against your
audit log when you go looking for the ten entries to paste.

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `0fe9305e-2273-4bb6-a408-3d2c0c4d792f` | human | 0.291 |  |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `f1751c70-e7a0-4d78-b3d7-82c75a314658` | unsure | 0.496 |  |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `1edfd0b2-7c5e-4ffe-aede-4aaad3bd08e8` | unsure | 0.609 |  |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `40d11d34-c453-49e4-b99f-39b31106a671` | unsure | 0.602 |  |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `ad63ffb5-ea4e-4d1d-88d2-e9b7378b1527` | unsure | 0.340 |  |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `db8f7598-de20-4224-9540-0077536f4308` | unsure | 0.493 |  |
| EV07 | evasion | signal two: padding with punctuation | 200 | `6645adc5-5cf4-4cc9-a12b-a4207b2e9d21` | unsure | 0.606 |  |
| EV08 | evasion | signal one: text below the token window | 200 | `e14aab2d-eb19-4b8d-b01e-988290aced01` | unsure | 0.310 |  |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `e66c9e2d-73c5-4335-93f1-ca794aa97f08` | unsure | 0.634 |  |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `8784ff1a-3c3a-4ac5-a452-9a5e843b44d9` | ai | 0.881 |  |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `9cb9001f-fa81-4a4a-945c-73126fdc5d8c` | unsure | 0.589 |  |
| FP02 | false_positive | human writing in a formal register | 200 | `62da40c2-ed25-4921-80ad-ad2902bd0bbb` | unsure | 0.701 |  |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `a4ade8e1-88fd-4380-a832-5ba644309e94` | unsure | 0.736 |  |
| FP04 | false_positive | a student essay written to a rubric | 200 | `3f3b6c71-00c1-44eb-bcab-84420523364c` | unsure | 0.739 |  |
| FP05 | false_positive | technical documentation written by a person | 200 | `020d939e-04a1-44cb-b8c6-3217606bdc7c` | unsure | 0.748 |  |
| FP06 | false_positive | a person imitating a formal template | 200 | `e315bf83-d412-43fb-a894-5be15585001a` | unsure | 0.763 |  |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `866d44f4-d11a-45eb-b166-2a05485f8cff` | unsure | 0.761 |  |
| FP08 | false_positive | very short genuine human submission | 200 | `c3a4b7a2-3e4d-4bc0-aec5-e9e1e589c09f` | unsure | 0.306 |  |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `9186deca-1333-4387-b9f3-ab3e7c3ef3e1` | unsure | 0.435 |  |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `1a933029-2823-4b0b-8b49-2382c716b0bf` | human | 0.246 |  |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `040ec7cf-3b68-442d-bfe4-e187d9460bed` | unsure | 0.569 |  |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `eb9a2468-f111-4e0e-ad60-171dcc4cdd6c` | unsure | 0.498 |  |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `57a6375d-87d3-4bd7-a9fb-599bc6af1eb0` | unsure | 0.558 |  |
| PI06 | prompt_injection | instruction plus real human text | 200 | `6dd557c6-d59e-4981-bd5e-f9c8038c2a72` | unsure | 0.549 |  |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — |  |
| MF02 | malformed | text is a single character | 400 | `—` | — | — |  |
| MF03 | malformed | text is control characters | 200 | `e6a58701-04bd-4f99-a6c3-0f99b612050b` | human | 0.195 |  |
| MF04 | malformed | text is only punctuation | 200 | `a597cd99-7b12-43cd-969d-6ee41f68edca` | human | 0.158 |  |
| MF05 | malformed | text is a very long single word | 200 | `c66133e2-2aeb-4137-803d-160f61778816` | ai | 0.893 |  |
| MF06 | malformed | text is emoji only | 200 | `a78d1e69-bfbc-4931-968d-483662a06027` | ai | 0.848 |  |
| MF07 | malformed | text is right-to-left script | 200 | `252eba93-b6c0-49a3-95f8-29827f43421e` | unsure | 0.784 |  |
| MF08 | malformed | text is 60,000 characters | 200 | `d73c36c4-1cff-4670-acd4-3391ba5c4e73` | unsure | 0.666 |  |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — |  |
| RQ02 | malformed | no creator_id | 400 | `—` | — | — |  |
| RQ03 | malformed | text is a number | 400 | `—` | — | — |  |
| RQ04 | malformed | text is a list | 400 | `—` | — | — |  |
| RQ05 | malformed | text is null | 400 | `—` | — | — |  |
| RQ06 | malformed | creator_id is an object | 400 | `—` | — | — |  |
| RQ07 | malformed | body is a JSON array, not an object | 400 | `—` | — | — |  |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — |  |
| RQ09 | malformed | body is empty | 400 | `—` | — | — |  |
| RQ10 | malformed | body is form-encoded, not JSON | 400 | `—` | — | — |  |
| RQ11 | malformed | body is JSON claiming to be plain text | 400 | `—` | — | — |  |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — |  |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `a18310c0-a1f6-4f98-96e9-3e0144f4b7ec` | human | 0.201 |  |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `1983b580-0cc9-4add-b49d-43bbf0c4e705` | human | 0.201 |  |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `0c8f91e7-3e2e-433b-95f4-e33e8cc037c2` | human | 0.201 |  |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `04a25245-c8be-41bc-a7b5-4c1da4a72880` | human | 0.201 |  |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `660a8f1e-bc05-4ee8-9613-8be0a519d77c` | human | 0.201 |  |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 200 | `70425766-81ee-47bb-bbf2-145d6b47bd3a` | human | 0.201 |  |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 200 | `f6b7fab9-5653-4871-9260-1e9ef92ab145` | human | 0.201 |  |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 200 | `0ef2a8ce-5d99-4df6-9f64-fe7cd23935a3` | human | 0.201 |  |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 200 | `ec4365ed-1a4e-44a5-9818-6511b1273aa8` | human | 0.201 |  |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 200 | `2d0dcbcd-be64-4951-9847-cc87ffa4965e` | human | 0.201 |  |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |

---

## By family

| Family | Attacks | Auto-BROKE | Left to judge |
|---|---|---|---|
| `evasion` | 10 | 0 | 10 |
| `false_positive` | 8 | 0 | 8 |
| `flood_same_creator` | 12 | 0 | 12 |
| `malformed` | 20 | 0 | 20 |
| `prompt_injection` | 6 | 0 | 6 |

> The **false_positive** family is the one to look at hardest. Those are
> written to be genuine human writing that reads as machine-like. Every one
> your service calls AI is a real writer it would have accused.

---

## What came back

The detail behind the table. Paste the interesting failures into your
README — the ones that show something, not the ten easiest.

### EV01 — `evasion`

*Targeting:* signal two: typos raise word variety

```json
{
  "id": "EV01",
  "status": 200,
  "content_id": "0fe9305e-2273-4bb6-a408-3d2c0c4d792f",
  "creator_id": "attacker_EV01",
  "guess": "human",
  "confidence": 0.2911927797561523,
  "model_score": 0.1635,
  "style_score": 0.5891425991871745,
  "label": "Our analysis suggests this writing was likely created by a person.",
  "error": null,
  "verdict": ""
}
```

### EV02 — `evasion`

*Targeting:* signal two: broken-up sentences raise length spread

```json
{
  "id": "EV02",
  "status": 200,
  "content_id": "f1751c70-e7a0-4d78-b3d7-82c75a314658",
  "creator_id": "attacker_EV02",
  "guess": "unsure",
  "confidence": 0.49605275245597,
  "model_score": 0.575,
  "style_score": 0.31184250818656695,
  "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
  "error": null,
  "verdict": ""
}
```

### EV03 — `evasion`

*Targeting:* signal two: a pasted quotation changes the shape

```json
{
  "id": "EV03",
  "status": 200,
  "content_id": "1edfd0b2-7c5e-4ffe-aede-4aaad3bd08e8",
  "creator_id": "attacker_EV03",
  "guess": "unsure",
  "confidence": 0.6094906132296944,
  "model_score": 0.6662,
  "style_score": 0.4771687107656484,
  "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
  "error": null,
  "verdict": ""
}
```

### EV04 — `evasion`

*Targeting:* signal one: unusual words raise perplexity

```json
{
  "id": "EV04",
  "status": 200,
  "content_id": "40d11d34-c453-49e4-b99f-39b31106a671",
  "creator_id": "attacker_EV04",
  "guess": "unsure",
  "confidence": 0.6018487518725051,
  "model_score": 0.6114,
  "style_score": 0.5795625062416837,
  "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
  "error": null,
  "verdict": ""
}
```

### EV05 — `evasion`

*Targeting:* both signals: heavy human editing pass

```json
{
  "id": "EV05",
  "status": 200,
  "content_id": "ad63ffb5-ea4e-4d1d-88d2-e9b7378b1527",
  "creator_id": "attacker_EV05",
  "guess": "unsure",
  "confidence": 0.3403117577269487,
  "model_score": 0.3212,
  "style_score": 0.3849058590898291,
  "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
  "error": null,
  "verdict": ""
}
```

### EV06 — `evasion`

*Targeting:* signal two: one very long sentence and one very short

```json
{
  "id": "EV06",
  "status": 200,
  "content_id": "db8f7598-de20-4224-9540-0077536f4308",
  "creator_id": "attacker_EV06",
  "guess": "unsure",
  "confidence": 0.49276499999999995,
  "model_score": 0.5727,
  "style_score": 0.30625,
  "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
  "error": null,
  "verdict": ""
}
```

### EV07 — `evasion`

*Targeting:* signal two: padding with punctuation

```json
{
  "id": "EV07",
  "status": 200,
  "content_id": "6645adc5-5cf4-4cc9-a12b-a4207b2e9d21",
  "creator_id": "attacker_EV07",
  "guess": "unsure",
  "confidence": 0.606123725379544,
  "model_score": 0.5862,
  "style_score": 0.6526124179318129,
  "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
  "error": null,
  "verdict": ""
}
```

### EV08 — `evasion`

*Targeting:* signal one: text below the token window

```json
{
  "id": "EV08",
  "status": 200,
  "content_id": "e14aab2d-eb19-4b8d-b01e-988290aced01",
  "creator_id": "attacker_EV08",
  "guess": "unsure",
  "confidence": 0.30962195142612264,
  "model_score": 0.2452,
  "style_score": 0.4599398380870755,
  "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
  "error": null,
  "verdict": ""
}
```

### EV09 — `evasion`

*Targeting:* both: AI text with a human opening paragraph bolted on

```json
{
  "id": "EV09",
  "status": 200,
  "content_id": "e66c9e2d-73c5-4335-93f1-ca794aa97f08",
  "creator_id": "attacker_EV09",
  "guess": "unsure",
  "confidence": 0.6339415672329092,
  "model_score": 0.7042,
  "style_score": 0.4700052241096975,
  "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
  "error": null,
  "verdict": ""
}
```

### EV10 — `evasion`

*Targeting:* signal two: repeated stanza structure

```json
{
  "id": "EV10",
  "status": 200,
  "content_id": "8784ff1a-3c3a-4ac5-a452-9a5e843b44d9",
  "creator_id": "attacker_EV10",
  "guess": "ai",
  "confidence": 0.8809915352167361,
  "model_score": 0.9515,
  "style_score": 0.7164717840557873,
  "label": "Our analysis suggests this writing may have been AI-generated. This is not a definitive determination, and you can request a review.",
  "error": null,
  "verdict": ""
}
```

### FP01 — `false_positive`

*Targeting:* plain, clear human writing with no flourishes

```json
{
  "id": "FP01",
  "status": 200,
  "content_id": "9cb9001f-fa81-4a4a-945c-73126fdc5d8c",
  "creator_id": "attacker_FP01",
  "guess": "unsure",
  "confidence": 0.5885916680468156,
  "model_score": 0.6175,
  "style_score": 0.5211388934893852,
  "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
  "error": null,
  "verdict": ""
}
```

### FP02 — `false_positive`

*Targeting:* human writing in a formal register

```json
{
  "id": "FP02",
  "status": 200,
  "content_id": "62da40c2-ed25-4921-80ad-ad2902bd0bbb",
  "creator_id": "attacker_FP02",
  "guess": "unsure",
  "confidence": 0.7010642073134402,
  "model_score": 0.7387,
  "style_score": 0.6132473577114677,
  "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
  "error": null,
  "verdict": ""
}
```

### FP03 — `false_positive`

*Targeting:* a non-native English speaker writing carefully

```json
{
  "id": "FP03",
  "status": 200,
  "content_id": "a4ade8e1-88fd-4380-a832-5ba644309e94",
  "creator_id": "attacker_FP03",
  "guess": "unsure",
  "confidence": 0.7357239114688816,
  "model_score": 0.8051,
  "style_score": 0.5738463715629385,
  "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
  "error": null,
  "verdict": ""
}
```

### FP04 — `false_positive`

*Targeting:* a student essay written to a rubric

```json
{
  "id": "FP04",
  "status": 200,
  "content_id": "3f3b6c71-00c1-44eb-bcab-84420523364c",
  "creator_id": "attacker_FP04",
  "guess": "unsure",
  "confidence": 0.7388649812383834,
  "model_score": 0.8329,
  "style_score": 0.5194499374612783,
  "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
  "error": null,
  "verdict": ""
}
```

### FP05 — `false_positive`

*Targeting:* technical documentation written by a person

```json
{
  "id": "FP05",
  "status": 200,
  "content_id": "020d939e-04a1-44cb-b8c6-3217606bdc7c",
  "creator_id": "attacker_FP05",
  "guess": "unsure",
  "confidence": 0.7484479320292436,
  "model_score": 0.8005,
  "style_score": 0.6269931067641457,
  "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
  "error": null,
  "verdict": ""
}
```

### FP06 — `false_positive`

*Targeting:* a person imitating a formal template

```json
{
  "id": "FP06",
  "status": 200,
  "content_id": "e315bf83-d412-43fb-a894-5be15585001a",
  "creator_id": "attacker_FP06",
  "guess": "unsure",
  "confidence": 0.7626984247816555,
  "model_score": 0.8814,
  "style_score": 0.48572808260551836,
  "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
  "error": null,
  "verdict": ""
}
```

### FP07 — `false_positive`

*Targeting:* human writing that repeats a phrase deliberately

```json
{
  "id": "FP07",
  "status": 200,
  "content_id": "866d44f4-d11a-45eb-b166-2a05485f8cff",
  "creator_id": "attacker_FP07",
  "guess": "unsure",
  "confidence": 0.7612103680142664,
  "model_score": 0.8816,
  "style_score": 0.4803012267142216,
  "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
  "error": null,
  "verdict": ""
}
```

### FP08 — `false_positive`

*Targeting:* very short genuine human submission

```json
{
  "id": "FP08",
  "status": 200,
  "content_id": "c3a4b7a2-3e4d-4bc0-aec5-e9e1e589c09f",
  "creator_id": "attacker_FP08",
  "guess": "unsure",
  "confidence": 0.3061484757729337,
  "model_score": 0.3223,
  "style_score": 0.268461585909779,
  "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
  "error": null,
  "verdict": ""
}
```

### PI01 — `prompt_injection`

*Targeting:* instruction to ignore the check

```json
{
  "id": "PI01",
  "status": 200,
  "content_id": "9186deca-1333-4387-b9f3-ab3e7c3ef3e1",
  "creator_id": "attacker_PI01",
  "guess": "unsure",
  "confidence": 0.43451269870534925,
  "model_score": 0.4625,
  "style_score": 0.3692089956844975,
  "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
  "error": null,
  "verdict": ""
}
```

### PI02 — `prompt_injection`

*Targeting:* instruction disguised as a system message

```json
{
  "id": "PI02",
  "status": 200,
  "content_id": "1a933029-2823-4b0b-8b49-2382c716b0bf",
  "creator_id": "attacker_PI02",
  "guess": "human",
  "confidence": 0.2458929242998818,
  "model_score": 0.2044,
  "style_score": 0.34270974766627277,
  "label": "Our analysis suggests this writing was likely created by a person.",
  "error": null,
  "verdict": ""
}
```

### PI03 — `prompt_injection`

*Targeting:* instruction wrapped in the writer's voice

```json
{
  "id": "PI03",
  "status": 200,
  "content_id": "040ec7cf-3b68-442d-bfe4-e187d9460bed",
  "creator_id": "attacker_PI03",
  "guess": "unsure",
  "confidence": 0.5694420418216309,
  "model_score": 0.5943,
  "style_score": 0.5114401394054366,
  "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
  "error": null,
  "verdict": ""
}
```

### PI04 — `prompt_injection`

*Targeting:* attempt to make the label text hostile

```json
{
  "id": "PI04",
  "status": 200,
  "content_id": "eb9a2468-f111-4e0e-ad60-171dcc4cdd6c",
  "creator_id": "attacker_PI04",
  "guess": "unsure",
  "confidence": 0.4980307237189508,
  "model_score": 0.4998,
  "style_score": 0.4939024123965027,
  "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
  "error": null,
  "verdict": ""
}
```

### PI05 — `prompt_injection`

*Targeting:* attempt to inject into the audit log

```json
{
  "id": "PI05",
  "status": 200,
  "content_id": "57a6375d-87d3-4bd7-a9fb-599bc6af1eb0",
  "creator_id": "attacker_PI05",
  "guess": "unsure",
  "confidence": 0.5583113166600058,
  "model_score": 0.6401,
  "style_score": 0.3674710555333526,
  "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
  "error": null,
  "verdict": ""
}
```

### PI06 — `prompt_injection`

*Targeting:* instruction plus real human text

```json
{
  "id": "PI06",
  "status": 200,
  "content_id": "6dd557c6-d59e-4981-bd5e-f9c8038c2a72",
  "creator_id": "attacker_PI06",
  "guess": "unsure",
  "confidence": 0.5491094930336539,
  "model_score": 0.5583,
  "style_score": 0.5276649767788464,
  "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
  "error": null,
  "verdict": ""
}
```

### MF01 — `malformed`

*Targeting:* text is only whitespace

```json
{
  "id": "MF01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF02 — `malformed`

*Targeting:* text is a single character

```json
{
  "id": "MF02",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF02",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF03 — `malformed`

*Targeting:* text is control characters

```json
{
  "id": "MF03",
  "status": 200,
  "content_id": "e6a58701-04bd-4f99-a6c3-0f99b612050b",
  "creator_id": "attacker_MF03",
  "guess": "human",
  "confidence": 0.195,
  "model_score": 0.0,
  "style_score": 0.65,
  "label": "Our analysis suggests this writing was likely created by a person.",
  "error": null,
  "verdict": ""
}
```

### MF04 — `malformed`

*Targeting:* text is only punctuation

```json
{
  "id": "MF04",
  "status": 200,
  "content_id": "a597cd99-7b12-43cd-969d-6ee41f68edca",
  "creator_id": "attacker_MF04",
  "guess": "human",
  "confidence": 0.15783999999999998,
  "model_score": 0.0112,
  "style_score": 0.5,
  "label": "Our analysis suggests this writing was likely created by a person.",
  "error": null,
  "verdict": ""
}
```

### MF05 — `malformed`

*Targeting:* text is a very long single word

```json
{
  "id": "MF05",
  "status": 200,
  "content_id": "c66133e2-2aeb-4137-803d-160f61778816",
  "creator_id": "attacker_MF05",
  "guess": "ai",
  "confidence": 0.8933199999999999,
  "model_score": 0.9976,
  "style_score": 0.65,
  "label": "Our analysis suggests this writing may have been AI-generated. This is not a definitive determination, and you can request a review.",
  "error": null,
  "verdict": ""
}
```

### MF06 — `malformed`

*Targeting:* text is emoji only

```json
{
  "id": "MF06",
  "status": 200,
  "content_id": "a78d1e69-bfbc-4931-968d-483662a06027",
  "creator_id": "attacker_MF06",
  "guess": "ai",
  "confidence": 0.84783,
  "model_score": 0.9969,
  "style_score": 0.5,
  "label": "Our analysis suggests this writing may have been AI-generated. This is not a definitive determination, and you can request a review.",
  "error": null,
  "verdict": ""
}
```

### MF07 — `malformed`

*Targeting:* text is right-to-left script

```json
{
  "id": "MF07",
  "status": 200,
  "content_id": "252eba93-b6c0-49a3-95f8-29827f43421e",
  "creator_id": "attacker_MF07",
  "guess": "unsure",
  "confidence": 0.78448,
  "model_score": 0.9064,
  "style_score": 0.5,
  "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
  "error": null,
  "verdict": ""
}
```

### MF08 — `malformed`

*Targeting:* text is 60,000 characters

```json
{
  "id": "MF08",
  "status": 200,
  "content_id": "d73c36c4-1cff-4670-acd4-3391ba5c4e73",
  "creator_id": "attacker_MF08",
  "guess": "unsure",
  "confidence": 0.6658765700615937,
  "model_score": 0.6175,
  "style_score": 0.7787552335386458,
  "label": "We couldn't confidently determine how this text was written. This result does not indicate wrongdoing.",
  "error": null,
  "verdict": ""
}
```

### RQ01 — `malformed`

*Targeting:* no text field at all

```json
{
  "id": "RQ01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ02 — `malformed`

*Targeting:* no creator_id

```json
{
  "id": "RQ02",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ03 — `malformed`

*Targeting:* text is a number

```json
{
  "id": "RQ03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ04 — `malformed`

*Targeting:* text is a list

```json
{
  "id": "RQ04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ05 — `malformed`

*Targeting:* text is null

```json
{
  "id": "RQ05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ06 — `malformed`

*Targeting:* creator_id is an object

```json
{
  "id": "RQ06",
  "status": 400,
  "content_id": null,
  "creator_id": {
    "id": "x"
  },
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ07 — `malformed`

*Targeting:* body is a JSON array, not an object

```json
{
  "id": "RQ07",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ08 — `malformed`

*Targeting:* body is unparseable JSON

```json
{
  "id": "RQ08",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ09 — `malformed`

*Targeting:* body is empty

```json
{
  "id": "RQ09",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ10 — `malformed`

*Targeting:* body is form-encoded, not JSON

```json
{
  "id": "RQ10",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ11 — `malformed`

*Targeting:* body is JSON claiming to be plain text

```json
{
  "id": "RQ11",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ12 — `malformed`

*Targeting:* deeply nested JSON

```json
{
  "id": "RQ12",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ12",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_01 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_01",
  "status": 200,
  "content_id": "a18310c0-a1f6-4f98-96e9-3e0144f4b7ec",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.20145363636363636,
  "model_score": 0.0287,
  "style_score": 0.6045454545454546,
  "label": "Our analysis suggests this writing was likely created by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_02 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_02",
  "status": 200,
  "content_id": "1983b580-0cc9-4add-b49d-43bbf0c4e705",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.20145363636363636,
  "model_score": 0.0287,
  "style_score": 0.6045454545454546,
  "label": "Our analysis suggests this writing was likely created by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_03 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_03",
  "status": 200,
  "content_id": "0c8f91e7-3e2e-433b-95f4-e33e8cc037c2",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.20145363636363636,
  "model_score": 0.0287,
  "style_score": 0.6045454545454546,
  "label": "Our analysis suggests this writing was likely created by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_04 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_04",
  "status": 200,
  "content_id": "04a25245-c8be-41bc-a7b5-4c1da4a72880",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.20145363636363636,
  "model_score": 0.0287,
  "style_score": 0.6045454545454546,
  "label": "Our analysis suggests this writing was likely created by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_05 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_05",
  "status": 200,
  "content_id": "660a8f1e-bc05-4ee8-9613-8be0a519d77c",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.20145363636363636,
  "model_score": 0.0287,
  "style_score": 0.6045454545454546,
  "label": "Our analysis suggests this writing was likely created by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_06 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_06",
  "status": 200,
  "content_id": "70425766-81ee-47bb-bbf2-145d6b47bd3a",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.20145363636363636,
  "model_score": 0.0287,
  "style_score": 0.6045454545454546,
  "label": "Our analysis suggests this writing was likely created by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_07 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_07",
  "status": 200,
  "content_id": "f6b7fab9-5653-4871-9260-1e9ef92ab145",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.20145363636363636,
  "model_score": 0.0287,
  "style_score": 0.6045454545454546,
  "label": "Our analysis suggests this writing was likely created by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_08 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_08",
  "status": 200,
  "content_id": "0ef2a8ce-5d99-4df6-9f64-fe7cd23935a3",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.20145363636363636,
  "model_score": 0.0287,
  "style_score": 0.6045454545454546,
  "label": "Our analysis suggests this writing was likely created by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_09 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_09",
  "status": 200,
  "content_id": "ec4365ed-1a4e-44a5-9818-6511b1273aa8",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.20145363636363636,
  "model_score": 0.0287,
  "style_score": 0.6045454545454546,
  "label": "Our analysis suggests this writing was likely created by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_10 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_10",
  "status": 200,
  "content_id": "2d0dcbcd-be64-4951-9847-cc87ffa4965e",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.20145363636363636,
  "model_score": 0.0287,
  "style_score": 0.6045454545454546,
  "label": "Our analysis suggests this writing was likely created by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_11 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_11",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_12 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_12",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```
