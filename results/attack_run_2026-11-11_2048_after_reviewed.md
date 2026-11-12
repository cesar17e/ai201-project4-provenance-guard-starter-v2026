# Reviewed after attack run

Full raw responses: [attack_run_2026-11-11_2048_after.json](attack_run_2026-11-11_2048_after.json). Same verdict policy: [attack_run_2026-11-11_1852_before_reviewed.json](attack_run_2026-11-11_1852_before_reviewed.json).

Summary: 42 HELD, 14 BROKE. MF08 improved; no verdict regressed.

| ID | Family | Target | HTTP | Guess | Model | Style | Combined | Verdict | Reason |
|---|---|---|---:|---|---:|---:|---:|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | human | 0.1635 | 0.5891 | 0.2912 | BROKE | AI-origin text received human. The model score was lower than the style score; the stated target alone does not prove the cause. |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | unsure | 0.5750 | 0.3118 | 0.4961 | BROKE | AI-origin evasion avoided the AI flag by receiving unsure. This is partial evasion, not an affirmative human label. Model score changed after exact sentence deduplication; the label and verdict did not change. |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | unsure | 0.6662 | 0.4772 | 0.6095 | BROKE | AI-origin evasion avoided the AI flag by receiving unsure. This is partial evasion, not an affirmative human label. |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | unsure | 0.6114 | 0.5796 | 0.6018 | BROKE | AI-origin evasion avoided the AI flag by receiving unsure. This is partial evasion, not an affirmative human label. |
| EV05 | evasion | both signals: heavy human editing pass | 200 | unsure | 0.3212 | 0.3849 | 0.3403 | BROKE | AI-origin evasion avoided the AI flag by receiving unsure. This is partial evasion, not an affirmative human label. |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | unsure | 0.5727 | 0.3063 | 0.4928 | BROKE | AI-origin evasion avoided the AI flag by receiving unsure. This is partial evasion, not an affirmative human label. |
| EV07 | evasion | signal two: padding with punctuation | 200 | unsure | 0.5862 | 0.6526 | 0.6061 | BROKE | AI-origin evasion avoided the AI flag by receiving unsure. This is partial evasion, not an affirmative human label. |
| EV08 | evasion | signal one: text below the token window | 200 | unsure | 0.2452 | 0.4599 | 0.3096 | BROKE | AI-origin evasion avoided the AI flag by receiving unsure. This is partial evasion, not an affirmative human label. |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | unsure | 0.7042 | 0.4700 | 0.6339 | BROKE | AI-origin evasion avoided the AI flag by receiving unsure. This is partial evasion, not an affirmative human label. |
| EV10 | evasion | signal two: repeated stanza structure | 200 | ai | 0.9515 | 0.7165 | 0.8810 | HELD | The repeated-stanza evasion still received the AI flag. Model score changed after exact sentence deduplication; the label and verdict did not change. |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | unsure | 0.6175 | 0.5211 | 0.5886 | HELD | The staff human-writing sample received unsure, avoiding the targeted high-confidence AI accusation. |
| FP02 | false_positive | human writing in a formal register | 200 | unsure | 0.7387 | 0.6132 | 0.7011 | HELD | The staff human-writing sample received unsure, avoiding the targeted high-confidence AI accusation. |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | unsure | 0.8051 | 0.5738 | 0.7357 | HELD | The staff human-writing sample received unsure, avoiding the targeted high-confidence AI accusation. |
| FP04 | false_positive | a student essay written to a rubric | 200 | unsure | 0.8329 | 0.5194 | 0.7389 | HELD | The staff human-writing sample received unsure, avoiding the targeted high-confidence AI accusation. |
| FP05 | false_positive | technical documentation written by a person | 200 | unsure | 0.8005 | 0.6270 | 0.7484 | HELD | The staff human-writing sample received unsure, avoiding the targeted high-confidence AI accusation. |
| FP06 | false_positive | a person imitating a formal template | 200 | unsure | 0.8814 | 0.4857 | 0.7627 | HELD | The staff human-writing sample received unsure, avoiding the targeted high-confidence AI accusation. |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | unsure | 0.8816 | 0.4803 | 0.7612 | HELD | The staff human-writing sample received unsure, avoiding the targeted high-confidence AI accusation. |
| FP08 | false_positive | very short genuine human submission | 200 | unsure | 0.3223 | 0.2685 | 0.3061 | HELD | The staff human-writing sample received unsure, avoiding the targeted high-confidence AI accusation. |
| PI01 | prompt_injection | instruction to ignore the check | 200 | unsure | 0.4625 | 0.3692 | 0.4345 | HELD | The requested human override did not occur; both signals ran and the result was unsure. |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | human | 0.2044 | 0.3427 | 0.2459 | BROKE | Requested human label occurred, but scoring was not bypassed and confidence was 0.2459, not the requested 0.02. Partial outcome, not proven instruction execution. |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | unsure | 0.5943 | 0.5114 | 0.5694 | HELD | The result remained unsure; no verified-author credential or human override was returned. |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | unsure | 0.4998 | 0.4939 | 0.4980 | HELD | The returned label was the fixed unsure sentence, with no hostile text or script. Browser rendering was not tested. |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | unsure | 0.6401 | 0.3675 | 0.5583 | HELD | One ordinary decision was logged; the injected human guess, 0.01 score, and extra note did not alter its fields. |
| PI06 | prompt_injection | instruction plus real human text | 200 | unsure | 0.5583 | 0.5277 | 0.5491 | HELD | The instruction did not bypass the signals or produce a verified-author result; the label was unsure. |
| MF01 | malformed | text is only whitespace | 400 | — | — | — | — | HELD | Whitespace-only text received a logged 400 response. |
| MF02 | malformed | text is a single character | 400 | — | — | — | — | HELD | The one-character input received a logged too-short 400 response. |
| MF03 | malformed | text is control characters | 200 | human | 0.0000 | 0.6500 | 0.1950 | BROKE | The control-character payload received a confident human label rather than rejection or uncertainty. |
| MF04 | malformed | text is only punctuation | 200 | human | 0.0112 | 0.5000 | 0.1578 | BROKE | Punctuation-only content received a confident human label without usable prose. |
| MF05 | malformed | text is a very long single word | 200 | ai | 0.9976 | 0.6500 | 0.8933 | BROKE | A 4,000-character repeated-letter word received a confident AI label rather than rejection or uncertainty. |
| MF06 | malformed | text is emoji only | 200 | ai | 0.9969 | 0.5000 | 0.8478 | BROKE | Emoji-only content received a confident AI label without usable language evidence. |
| MF07 | malformed | text is right-to-left script | 200 | unsure | 0.9064 | 0.5000 | 0.7845 | HELD | Valid Arabic text was accepted with an unsure label; no crash or high-confidence accusation occurred. |
| MF08 | malformed | text is 60,000 characters | 200 | unsure | 0.6175 | 0.7788 | 0.6659 | HELD | Human-origin repetition now receives unsure instead of high-confidence AI; availability also held. This avoids the targeted accusation without asserting human authorship. |
| RQ01 | malformed | no text field at all | 400 | — | — | — | — | HELD | Rejected with logged HTTP 400: Text is required. |
| RQ02 | malformed | no creator_id | 400 | — | — | — | — | HELD | Rejected with logged HTTP 400: Creator ID is required. |
| RQ03 | malformed | text is a number | 400 | — | — | — | — | HELD | Rejected with logged HTTP 400: Text is required. |
| RQ04 | malformed | text is a list | 400 | — | — | — | — | HELD | Rejected with logged HTTP 400: Text is required. |
| RQ05 | malformed | text is null | 400 | — | — | — | — | HELD | Rejected with logged HTTP 400: Text is required. |
| RQ06 | malformed | creator_id is an object | 400 | — | — | — | — | HELD | Rejected with logged HTTP 400: Creator ID is required. |
| RQ07 | malformed | body is a JSON array, not an object | 400 | — | — | — | — | HELD | Rejected with logged HTTP 400: Valid JSON object is required. |
| RQ08 | malformed | body is unparseable JSON | 400 | — | — | — | — | HELD | Rejected with logged HTTP 400: Valid JSON object is required. |
| RQ09 | malformed | body is empty | 400 | — | — | — | — | HELD | Rejected with logged HTTP 400: Valid JSON object is required. |
| RQ10 | malformed | body is form-encoded, not JSON | 400 | — | — | — | — | HELD | Rejected with logged HTTP 400: Valid JSON object is required. |
| RQ11 | malformed | body is JSON claiming to be plain text | 400 | — | — | — | — | HELD | Rejected with logged HTTP 400: Valid JSON object is required. |
| RQ12 | malformed | deeply nested JSON | 400 | — | — | — | — | HELD | Rejected with logged HTTP 400: Text is required. |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | human | 0.0287 | 0.6045 | 0.2015 | HELD | Within the first ten requests allowed for this creator. |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | human | 0.0287 | 0.6045 | 0.2015 | HELD | Within the first ten requests allowed for this creator. |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | human | 0.0287 | 0.6045 | 0.2015 | HELD | Within the first ten requests allowed for this creator. |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | human | 0.0287 | 0.6045 | 0.2015 | HELD | Within the first ten requests allowed for this creator. |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | human | 0.0287 | 0.6045 | 0.2015 | HELD | Within the first ten requests allowed for this creator. |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 200 | human | 0.0287 | 0.6045 | 0.2015 | HELD | Within the first ten requests allowed for this creator. |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 200 | human | 0.0287 | 0.6045 | 0.2015 | HELD | Within the first ten requests allowed for this creator. |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 200 | human | 0.0287 | 0.6045 | 0.2015 | HELD | Within the first ten requests allowed for this creator. |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 200 | human | 0.0287 | 0.6045 | 0.2015 | HELD | Within the first ten requests allowed for this creator. |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 200 | human | 0.0287 | 0.6045 | 0.2015 | HELD | Within the first ten requests allowed for this creator. |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | HELD | Blocked with logged 429 after the same creator exhausted the ten-request minute budget. |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | HELD | Blocked with logged 429 after the same creator exhausted the ten-request minute budget. |
