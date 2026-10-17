# Submission evidence batch review

Reviewed 2026-10-17. Baseline source commit:
`450a14fe0338bbf3200986b8649497ae5a8c5808`. The commit containing this record is
the delivery commit; its Git subject/body links the work to the Issues below.
Resolve its exact hash with `git log -1 --format=%H -- participant-work/day2/submission-review.md`.

| Issue | Reviewed deliverable | Limits |
| --- | --- | --- |
| [#2 Evidence](https://github.com/monkzzz/Formacao-de-IA/issues/2) | [Submission index](submission-evidence-index.md), weight/checkpoint hashes, history and derived confusion analysis | Historical metrics, current identity verification; no new accuracy claim |
| [#3 Artifacts](https://github.com/monkzzz/Formacao-de-IA/issues/3) | [Isolated model restoration](submission-artifacts.md), successful real downloads matching local files | Browser weights only; no checkpoint distribution or retraining verification |
| [#4 Verification](https://github.com/monkzzz/Formacao-de-IA/issues/4) | [Current full unit suite](submission-unit-tests.json), all 30 passed | Fresh browser/parity and submitted-origin checks remain pending |
| [#7 Process deviation](https://github.com/monkzzz/Formacao-de-IA/issues/7) | Existing request remains prepared and unsent | Participant explicitly deferred the approval request on 2026-10-17; no acceptance claimed |

Review scope: evidence scripts and records, relative Markdown links, selected
model/checkpoint identities, restoration isolation, and checklist updates.
No training, preprocessing, model selection, UI, deployment or frozen challenge
record changed. The test suite uses existing local dependencies/data; restoration
uses a clean stdlib-only venv. The new scripts refuse to overwrite their evidence
destinations. Generated unit results are a transcribed summary of this batch's
observed run, rather than historical test counts.

Final documentation validation passed: 25 relative links resolved, all new JSON
records parsed, both evidence scripts parsed, both confusion-matrix totals and
diagonal sums matched their recorded metrics, and `git diff --check` passed.

The delivery commit references Issues without closing them: #3 retains broader
artifact questions, #4 retains browser verification, and #7 requires an actual
instructor decision. No Issue comments or other messages were sent in this batch.
