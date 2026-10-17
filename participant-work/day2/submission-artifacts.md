# Clean-environment model recovery

Verified 2026-10-17 for [Issue #3](https://github.com/monkzzz/Formacao-de-IA/issues/3).
The existing server can restore the selected CNN and companion letter weights
from the public host without installing ML packages or retraining.

From a fresh checkout's `dia2-local/` directory:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe serve.py --download-models
```

The downloader fetches missing `captcha-v3/digits/weights.bin` and
`robust/letters/weights.bin` under `dist/model/` and verifies byte length and
SHA-256 against the committed manifests before replacing each temporary file.
Keep the manifests with the checkout; a changed remote model fails verification.
Existing files are skipped by the server, so this recovery check used an empty
destination and independently hashed both downloaded files afterward.

[Verification script](verify-submission-artifacts.py) copied only the server and
two manifests into a new ignored directory, created a venv without pip or system
site packages, and used real HTTPS downloads. [Successful retry](submission-artifact-verification-retry.json)
records 1,090,472 digit bytes and 835,944 letter bytes, matching both manifests
and the unchanged originals. The [initial restricted-network failure](submission-artifact-verification.json)
is retained; retry succeeded after sandbox escalation. An earlier attempt to
create children of a `tempfile.mkdtemp` directory hit a Windows access error;
the script now creates a unique directory directly under the ignored `.tmp/`.

To reproduce the isolated check from the repository root, choose a new report:

```powershell
dia2-local\.venv\Scripts\python.exe participant-work/day2/verify-submission-artifacts.py --report participant-work/day2/submission-artifact-next-check.json
```

This confirms browser weight recovery, not checkpoint recovery or deterministic
retraining. The local ignored `artifacts/captcha-v3/best.pt` hash is recorded in
the [identity index](submission-model-identity.json); no public checkpoint archive
is established. [Historical training commands](../../dia2-local/docs/residual-training.md#commands)
also require MNIST, baseline checkpoint and the documented Windows fonts. They
were not executed, and preserved experiment outputs must not be overwritten.
Optional OCR downloads, frozen archives and long-term host availability remain
outside this check. No application assets or original model files were changed.
