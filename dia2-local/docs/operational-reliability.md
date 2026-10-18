# CI, portable evaluation and deployment recovery

These tooling changes preserve the published 3.11.1 frontends and all model
weights. The separate [confidence replay study](confidence-replay.md) completed
four epochs without an eligible replacement; its reserved-test gate stayed closed.

## Browser checks on Linux and Windows

The Python workflow now triggers on relevant `main` pushes and pull requests,
including `dist/`, `submission/`, dependency, receipt and assembler changes.
Each OS installs Chromium and runs `digitlab.browser_ci`. The harness downloads
the reviewed restricted ZIP, checks its archive and every member hash, then
combines its four weight exports with **current checkout frontend sources** in
temporary directories. The fixture is not a new submission or deployment.

Both interfaces get actual activation parity, native Python upload-score checks,
exports and mobile checks. Full-site design, helper, drawing, Words and reader
recovery collectors also run. OCR worker doubles are explicit: this CI lane has
no external OCR model downloads, official CAPTCHA inference or training. Reports
and screenshots upload as workflow artifacts even when checks fail. This does
not place official-image evaluation in ordinary CI.

From `dia2-local/` with the portable Day 2 interpreter:

```text
<python> -m digitlab.browser_ci --report my-ci.json --prefix my-ci
```

For offline package reuse, supply `--archive <reviewed.zip>`. The optional
`--receipt <build.json>` selects another reviewed package. All subcollector
reports/screenshots preflight collisions. The job uses reviewed release weights,
so local ignored datasets and training checkpoints are unnecessary in a checkout.

## Portable package receipts and evaluation

New default build receipts use paths relative to `dia2-local/`. Historical
receipts keep their original bytes and hashes. Both submission QA commands accept
`--site`, `--archive` and `--artifact-root` overrides. A missing historical
absolute path falls back to `artifacts/<package-name>/site` and its named ZIP;
an explicit artifact root takes precedence. Hash verification remains required.
Full checkpoint-comparison QA still requires the original local checkpoints;
the CI harness independently reconstructs native tensors from reviewed exports.

```text
<python> -m digitlab.self_trained_submission_qa --build reports/self-trained-submission-cleanup-v4-build.json --artifact-root <copied-artifacts> --report moved-check.json --screenshot-prefix moved-check
<python> -m digitlab.self_trained_pages_qa --build reports/self-trained-submission-cleanup-v4-build.json --site <copied-site> --archive <copied.zip> --report public-check.json --screenshot-prefix public-check
```

The restricted Pages assembler also accepts `--receipt <build.json>` alongside
its archive/output flags. It still verifies the exact ZIP allowlist and hashes.
The official follow-up collector accepts `--name`, `--build`, package location
overrides, `--full-site`, verification report paths, `--reference`, `--report-root`
and `--snapshot-root`. Its default retains the historical completed identity and
therefore refuses a repeated evaluation. Every newly authorized evaluation must
use a separate identity, frozen artifacts and separate raw recording/comparison.
This work tests that configuration without running the official ten again.

## Failure evidence

Maintained design, helper, Words, reader, metric, selector and both submission
collectors reserve a fresh JSON report before browser work. Completed checks
survive an exception; status becomes FAIL with an error type/message. Reports
are replaced atomically after complete JSON serialization and file flush/fsync.
An interrupted process can leave RUNNING evidence rather than a false PASS.
Existing reports and screenshots are never replaced to retry a failed run.
Collectors for historical fixed releases retain their documented release scope.

## Staged FTPS publication

`deployment-files.json` is an explicit reviewed list of 61 public files.
Both upload and read-only FTP verification use it. Selected uploads must be a
subset; unsafe paths, ROMs, parity fixtures and unrelated files are rejected.
New public assets require reviewing this list before publication.

For each file the uploader first backs up its previous bytes. A unique temporary
remote name receives the new bytes; downloading and hashing that temporary file
must pass before RNFR/RNTO publication. The published bytes are verified again.
Dependencies still precede entry modules and `index.html` remains last.

The report is a progress journal: it records the plan, backup directory, current
file/phase, temporary name and every verified published file as work proceeds.
Failures retain that journal with error category/code only. Partial upload and
temporary corruption leave the original filename untouched. If a server refuses
rename-over-existing, publication fails rather than deleting the working file.
Temporary-file cleanup is best effort and its outcome is recorded.

This provides per-file staged publication, not an atomic whole-site release.
A connection failure around a rename can leave its outcome uncertain: inspect
the recorded filename/hash before retrying with a new receipt. Restore previous
bytes from the recorded backup when rollback is required. Never overwrite a failed
receipt or silently republish the already completed subset. Real server rename
behavior needs verification during a separately requested deployment. This work
uses injected transfer, corruption, connection and rename failures without
contacting the production FTP account.

Local evidence: [browser CI](../reports/reliability-v1-browser-ci.json),
[relocated package and 40 uploads](../reports/reliability-v1-relocated-submission.json)
and [research integrity](../reports/captcha-confidence-replay-v1-validation.json).
