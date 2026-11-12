# Verified human-writing dataset

Criterion 1 requires 20 distinct, independently verified human-written samples. `human_samples.json` contains the 20 passages supplied by the user, without changes to their wording. The user reports that many came from Reddit running/marathon discussion boards. Two source matches are documented below; the remaining 18 origins and full independent verification are not established.

Each of the 20 entries in the `samples` array needs this structure:

```json
{
  "samples": [
    {
      "id": "human-01",
      "text": "Your actual human-written passage goes here.",
      "source": "Where the original writing or earlier drafts can be checked",
      "verified_by": "Who verified its human provenance",
      "verification": "How that provenance was verified",
      "verified_human": true
    }
  ]
}
```

The example shows the format only; it is not a test sample. Use real prose, not AI-generated examples or twenty copies of the same passage. The loader checks the supplied metadata's structure, not whether the authorship claim is true.

Run all five criteria, three trials each once the actual provenance has been recorded and verified:

```bash
python run_eval.py --local --label before --human-samples evaluation/human_samples.json
```

Until the dataset is ready, an explicitly partial run can exercise criteria 2–5:

```bash
python run_eval.py --local --label before --allow-partial
```

A partial report keeps criterion 1 PENDING; it cannot complete this milestone. Both signals are deterministic, so matching trials are normal. The same passages must be used before and after the one improvement.

Each synthetic test writer submits at most three requests across the trials. The limiter stays enabled, and its counters are not reset between trials. Missing-ID and non-object cases count against the server's address. A 429 in an intended validation check is marked INCOMPLETE rather than credited as evidence that validation ran. The temporary local server starts with fresh counters and appends real audit events to the existing log.

## Measuring the currently supplied passages

The current dataset records `verified_human: false` because independent provenance has not been established. This does **not** mean the passages are AI-written; it distinguishes the user's human-authorship assertion from independent verification.

To measure their scores under the supplied labels without claiming a verified false-positive rate:

```bash
python run_eval.py --local --label before --allow-unverified-human-samples
```

This runs all 20 passages in each of three trials, plus criteria 2–5. Criterion 1 is reported as PROVISIONAL with a separate conditional numeric verdict. It cannot become a final MET or MISSED verdict under the original criterion merely by changing the metadata flag. Record the actual source and verification method for each passage first, then repeat the full before evaluation and retain the same dataset for the after comparison.

## Source checks

The passages human-02 and human-03 match an [r/running thread dated May 14, 2016](https://ca.reddit.com/r/running/comments/4jazw5/achievements_for_saturday_may_14_2016/): the former matches a full comment and the latter an initial excerpt of a longer comment. [source_checks.json](source_checks.json) records this check. It identifies sources for two passages; it does not establish the remaining 18 origins or certify all authorship labels. The measured dataset remains marked provisional.
