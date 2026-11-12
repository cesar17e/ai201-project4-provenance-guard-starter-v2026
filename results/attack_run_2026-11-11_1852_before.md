# Attack run — before

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-11-11 18:52
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
| EV01 | evasion | signal two: typos raise word variety | 200 | `5b73c6b0-6fab-450e-9e48-5402cef99a17` | human | 0.291 |  |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `84881944-6b39-40ec-96d7-2ff907ab4d6f` | unsure | 0.510 |  |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `ac4c9bdf-6c5c-4faf-98c7-809baf6eb61f` | unsure | 0.609 |  |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `2b4be714-cc28-4944-b8da-75bf8df39d37` | unsure | 0.602 |  |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `b8968ddc-6646-41d8-bf1f-e65a8d4a8b9e` | unsure | 0.340 |  |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `96398cc4-d1fb-47e3-ab81-8ae85ded34f1` | unsure | 0.493 |  |
| EV07 | evasion | signal two: padding with punctuation | 200 | `0c731561-53fa-4747-ba2c-974d217138fa` | unsure | 0.606 |  |
| EV08 | evasion | signal one: text below the token window | 200 | `d583bf88-ac2b-43c7-863c-ba2652645e7e` | unsure | 0.310 |  |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `1d6dcce3-dee8-4b51-a516-c837e61b57bc` | unsure | 0.634 |  |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `4d7d1e17-74d8-4f93-b84f-2da7134eceec` | ai | 0.900 |  |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `8b7134cb-e387-430f-bec5-a6c0e8edcf7e` | unsure | 0.589 |  |
| FP02 | false_positive | human writing in a formal register | 200 | `ab66a0e2-c2ae-4a19-b548-0664f3b33c84` | unsure | 0.701 |  |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `e6544f7e-4611-44c1-b559-c5cc1e6fb654` | unsure | 0.736 |  |
| FP04 | false_positive | a student essay written to a rubric | 200 | `1015676a-2b6a-4d7f-b419-5c7a3bfc83e1` | unsure | 0.739 |  |
| FP05 | false_positive | technical documentation written by a person | 200 | `1b6086f8-f6f8-4e1d-95a5-8c9326c08ae7` | unsure | 0.748 |  |
| FP06 | false_positive | a person imitating a formal template | 200 | `e9045208-7bdc-40e3-976d-739bc40fa374` | unsure | 0.763 |  |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `cee517f6-da67-4516-9986-0fe2798fb9ca` | unsure | 0.761 |  |
| FP08 | false_positive | very short genuine human submission | 200 | `1576b763-a8a9-4f5a-9029-2d803acec0eb` | unsure | 0.306 |  |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `ecf773f0-2eec-40da-859e-24bb168294bb` | unsure | 0.435 |  |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `e4111ca5-c0d2-4ba6-9617-29450e449eff` | human | 0.246 |  |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `de5b40b6-3ba3-4cea-b13c-44c70cef3472` | unsure | 0.569 |  |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `ffc4c943-7ad2-4e53-8eb2-269e615bbec6` | unsure | 0.498 |  |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `97d7ce2e-1761-4d93-9461-6c92cb982857` | unsure | 0.558 |  |
| PI06 | prompt_injection | instruction plus real human text | 200 | `53cd6e9a-b409-40f2-b824-51cc2f4118ce` | unsure | 0.549 |  |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — |  |
| MF02 | malformed | text is a single character | 400 | `—` | — | — |  |
| MF03 | malformed | text is control characters | 200 | `8884abe5-440f-4469-9bab-ca3925f0a034` | human | 0.195 |  |
| MF04 | malformed | text is only punctuation | 200 | `37054e2a-0465-4202-9ddf-8d6d2872fd20` | human | 0.158 |  |
| MF05 | malformed | text is a very long single word | 200 | `0bb1506c-ec07-4cc2-9128-ffacb4c6f1f7` | ai | 0.893 |  |
| MF06 | malformed | text is emoji only | 200 | `7c76e152-30df-4b6e-86d5-58d95ed494f4` | ai | 0.848 |  |
| MF07 | malformed | text is right-to-left script | 200 | `94a7f7e4-9bec-4934-88c3-e98357b90188` | unsure | 0.784 |  |
| MF08 | malformed | text is 60,000 characters | 200 | `76d65cf1-6769-48fc-b505-f660520ac549` | ai | 0.925 |  |
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
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `07541665-49c6-45cc-bed1-69f910362d90` | human | 0.201 |  |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `18d71824-c4bc-4da1-99ff-2f2109a39927` | human | 0.201 |  |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `b0cc64eb-cebb-4340-bad6-63f372ea9821` | human | 0.201 |  |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `96184236-3d22-4919-a013-81ed1e8ff3b6` | human | 0.201 |  |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `7a3ba300-3838-4be3-8cd4-c78eba7ed389` | human | 0.201 |  |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 200 | `edc7429e-aa5a-4329-97ae-cd7b7d263e83` | human | 0.201 |  |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 200 | `27a02264-2bbf-4094-94e6-cb8f4bedd8a7` | human | 0.201 |  |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 200 | `bb97143a-f2d6-4626-8daa-e4f2f701ec6a` | human | 0.201 |  |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 200 | `9826b908-0947-4394-97fd-7798c1ace060` | human | 0.201 |  |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 200 | `955ae77f-49b8-4b49-bad3-16909cd3a704` | human | 0.201 |  |
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
  "content_id": "5b73c6b0-6fab-450e-9e48-5402cef99a17",
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
  "content_id": "84881944-6b39-40ec-96d7-2ff907ab4d6f",
  "creator_id": "attacker_EV02",
  "guess": "unsure",
  "confidence": 0.50956275245597,
  "model_score": 0.5943,
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
  "content_id": "ac4c9bdf-6c5c-4faf-98c7-809baf6eb61f",
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
  "content_id": "2b4be714-cc28-4944-b8da-75bf8df39d37",
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
  "content_id": "b8968ddc-6646-41d8-bf1f-e65a8d4a8b9e",
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
  "content_id": "96398cc4-d1fb-47e3-ab81-8ae85ded34f1",
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
  "content_id": "0c731561-53fa-4747-ba2c-974d217138fa",
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
  "content_id": "d583bf88-ac2b-43c7-863c-ba2652645e7e",
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
  "content_id": "1d6dcce3-dee8-4b51-a516-c837e61b57bc",
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
  "content_id": "4d7d1e17-74d8-4f93-b84f-2da7134eceec",
  "creator_id": "attacker_EV10",
  "guess": "ai",
  "confidence": 0.9003815352167361,
  "model_score": 0.9792,
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
  "content_id": "8b7134cb-e387-430f-bec5-a6c0e8edcf7e",
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
  "content_id": "ab66a0e2-c2ae-4a19-b548-0664f3b33c84",
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
  "content_id": "e6544f7e-4611-44c1-b559-c5cc1e6fb654",
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
  "content_id": "1015676a-2b6a-4d7f-b419-5c7a3bfc83e1",
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
  "content_id": "1b6086f8-f6f8-4e1d-95a5-8c9326c08ae7",
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
  "content_id": "e9045208-7bdc-40e3-976d-739bc40fa374",
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
  "content_id": "cee517f6-da67-4516-9986-0fe2798fb9ca",
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
  "content_id": "1576b763-a8a9-4f5a-9029-2d803acec0eb",
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
  "content_id": "ecf773f0-2eec-40da-859e-24bb168294bb",
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
  "content_id": "e4111ca5-c0d2-4ba6-9617-29450e449eff",
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
  "content_id": "de5b40b6-3ba3-4cea-b13c-44c70cef3472",
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
  "content_id": "ffc4c943-7ad2-4e53-8eb2-269e615bbec6",
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
  "content_id": "97d7ce2e-1761-4d93-9461-6c92cb982857",
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
  "content_id": "53cd6e9a-b409-40f2-b824-51cc2f4118ce",
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
  "content_id": "8884abe5-440f-4469-9bab-ca3925f0a034",
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
  "content_id": "37054e2a-0465-4202-9ddf-8d6d2872fd20",
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
  "content_id": "0bb1506c-ec07-4cc2-9128-ffacb4c6f1f7",
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
  "content_id": "7c76e152-30df-4b6e-86d5-58d95ed494f4",
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
  "content_id": "94a7f7e4-9bec-4934-88c3-e98357b90188",
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
  "content_id": "76d65cf1-6769-48fc-b505-f660520ac549",
  "creator_id": "attacker_MF08",
  "guess": "ai",
  "confidence": 0.9249465700615936,
  "model_score": 0.9876,
  "style_score": 0.7787552335386458,
  "label": "Our analysis suggests this writing may have been AI-generated. This is not a definitive determination, and you can request a review.",
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
  "content_id": "07541665-49c6-45cc-bed1-69f910362d90",
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
  "content_id": "18d71824-c4bc-4da1-99ff-2f2109a39927",
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
  "content_id": "b0cc64eb-cebb-4340-bad6-63f372ea9821",
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
  "content_id": "96184236-3d22-4919-a013-81ed1e8ff3b6",
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
  "content_id": "7a3ba300-3838-4be3-8cd4-c78eba7ed389",
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
  "content_id": "edc7429e-aa5a-4329-97ae-cd7b7d263e83",
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
  "content_id": "27a02264-2bbf-4094-94e6-cb8f4bedd8a7",
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
  "content_id": "bb97143a-f2d6-4626-8daa-e4f2f701ec6a",
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
  "content_id": "9826b908-0947-4394-97fd-7798c1ace060",
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
  "content_id": "955ae77f-49b8-4b49-bad3-16909cd3a704",
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
