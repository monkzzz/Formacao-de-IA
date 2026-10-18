# Website sources, packages and deployment

Local maintenance changes are not a live release. The two public sites have
independent inputs, evidence and delivery processes.

| Target | Source and artifact | Publication route | Preserved evidence |
| --- | --- | --- | --- |
| `naoquerosaber.pt/AI/` | Full `dist/` site, including optional pretrained readers | Verified FTPS process in [hosting](hosting.md#check-and-deploy) | Versioned release/deployment reports |
| GitHub Pages | `submission/` templates, selected shared `dist/v3/` modules and four verified participant-trained exports, assembled as a ZIP | Manual Pages workflow downloads a pinned reviewed archive | [Cleanup v4 receipt](../reports/self-trained-submission-cleanup-v4-build.json); [preserved v1 verification](self-trained-pages.md) |

Both interfaces use browser inference. Copying `dist/` to Pages would include
optional pretrained readers and would cross the restricted submission boundary.
The submission builder includes an explicit module list and checks every exported
tensor against its local training checkpoint. Training and official evaluation
are separate workflows; none is needed for a UI maintenance build.

## Prepare a new restricted package

From `dia2-local/`, with the [portable Day 2 runtime](../../PORTABILITY.md):

```text
<python> -m digitlab.self_trained_submission --name self-trained-submission-cleanup-v4
<python> -m digitlab.self_trained_submission_qa --build reports/self-trained-submission-cleanup-v4-build.json --report reports/self-trained-submission-cleanup-v4-browser.json --screenshot-prefix self-trained-submission-cleanup-v4
```

The builder creates `artifacts/<name>/site/`, `artifacts/<name>/<name>.zip` and
`reports/<name>-build.json`. A different `--output` is optional. Existing sites,
ZIPs and receipts are rejected before the audit or output creation. Use another
identity for another source revision; do not delete old evidence to reuse a name.
The site displays its package identity from the recorded evaluation manifest.

QA checks the chosen receipt and archive hashes, four models, 40 uploads, real
activation and score parity, drawing/export/mobile behavior and same-origin
requests. Maintained templates also exercise metadata retry, model-load failure
recovery and busy controls. These are software checks, not new accuracy results.

## Publish only the selected target

For the full site, follow the verified FTPS workflow, prepare local QA and a remote
backup, transfer shared dependencies/model assets before entry modules, and verify
deployed hashes and browser behavior. Keep local credential files ignored. New
`browser-utils.js` is a dependency of the cleaned entry modules and must accompany
them. Do not publish the restricted site over the full site accidentally.

For Pages, the manual workflow and restricted assembler are now pinned to the
reviewed `self-trained-submission-cleanup-v4` archive and its receipt. The original
v1 release remains preserved. A source push alone does not deploy the package.
Each future release needs a separate reviewed ZIP and build/QA evidence, followed
by updating the pinned release asset and receipt together. The restricted
Pages assembler verifies the exact allowlist, archive hash and weight identities.
Prepare and review that change before publishing; do not bypass its checks by
copying an arbitrary directory into the workflow.

Cleanup validation and publication are separate phases. The subsequent requested
release is documented in [the release record](release-3.11.1.md). Existing v1 and
historical measurements keep their scope. For maintenance verification, use
[fresh browser QA outputs](browser-qa.md).

Subsequent tooling changes add an explicit upload allowlist, verified temporary
remote files and incremental recovery receipts. Package QA/assembly now supports
relocated artifacts and caller-selected receipts. See
[operational reliability](operational-reliability.md) before the next deployment.

## Local FTPS deployment after CI

GitHub Actions runs tests only. Production FTP uploads run locally using the
ignored `ftp.local.json`; no FTP credentials are stored in GitHub or supplied to
hosted jobs. Deploy the exact commit that passed Windows and Linux CI, from a
clean checkout, using the portable runtime.

```text
<python> -m digitlab.deployment_assets --restore --report <identity>-prepare.json
<python> -m digitlab.browser_ci --prepare-only --prefix <identity>-weights --report <identity>-weights.json
<python> -m digitlab.ftp_deploy --upload --report <identity>-deployment.json
<python> -m digitlab.deployment_assets --verify-http --report <identity>-https.json
<python> -m digitlab.deployment_public_qa --report <identity>-browser.json --screenshot-prefix <identity>
```

Run these steps sequentially and stop on any failure. Restore/check assets and
prepare reviewed activation fixtures before connecting to FTP. The restore command
checks all eight historical/current weight exports against committed manifest
sizes and SHA-256 values, downloading missing exports from the public site only.
A future model release needs its matching reviewed export separately available;
this maintenance workflow never trains models or evaluates official CAPTCHAs.

The uploader backs up every replaced file, verifies a unique temporary upload,
then publishes by rename. After publication, compare all 61 public files over
HTTPS. Browser checks cover four models, actual activation parity, synthetic
upload scores against native tensors, prediction export and mobile layout. These
checks require reviewed activation fixtures, not training checkpoints or datasets.

Keep local backups under the ignored `artifacts/ftp-backup-*` directory and preserve
fresh reports/screenshots for every attempt, including failures. Failed publication
is not automatically rolled back: inspect the journal and restore the recorded
backup for affected files, preserving the failed evidence. The staged replacement
is per file rather than an atomic whole-site release.

GitHub Pages retains its separate manual workflow and pinned restricted package.

## Verified local publication on 2026-10-18

The maintenance branch and local deployment tools were merged into `main` at
`54ae276`. Its [platform CI run](https://github.com/monkzzz/Formacao-de-IA/actions/runs/39170323509)
passed on Windows and Linux: each OS ran 103 Day 2 tests (one optional EMNIST
dataset check skipped), all 125 Day 1 tests, and both frontend browser suites.

Publication ran locally with the existing ignored configuration. No FTP secret
was stored in GitHub, and no hosted FTP workflow was added. Only the four files
whose line endings differed from the clean checkout were uploaded:
`assets/ddddocr-LICENSE.txt`, `v3/helper-knowledge.js`, `v3/helper.js` and
`index.html`. Every replacement used a verified temporary upload and remote
rename, with previous bytes preserved in the local backup directory recorded in
the [deployment journal](../reports/local-ftps-20261018-deployment.json).

[HTTPS verification](../reports/local-ftps-20261018-https.json) matched all 61
public asset hashes. [Public browser checks](../reports/local-ftps-20261018-browser.json)
passed for four models, actual intermediate activations, synthetic upload scores
against native inference, export and mobile layout. The
[helper checks](../reports/local-ftps-20261018-helper-qa.json) passed all six groups.
The mobile screenshot was inspected manually. No weights, application behavior
or restricted Pages package changed; no official CAPTCHA evaluation was run.
See the [completion record](../reports/local-ftps-20261018-completion.json).
