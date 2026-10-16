# Website Hosting

Public URL: https://naoquerosaber.pt/AI/index.html

Static application assets and both trained models are served by the hosting account. Inference remains in the browser; no Python service is deployed. Use HTTPS because the model-integrity and upload-record APIs use secure browser capabilities.

## Current robustness release

The public app now loads the improved digit and letter models from
`model/robust/digits/` and `model/robust/letters/`. All 26 uploaded assets passed
SHA-256 verification by downloading them over FTPS. Replaced files were backed
up locally; unrelated remote files were retained. See the
[deployment record](../reports/ftp-deployment.json).

[Public browser verification](../reports/public-robust-browser-qa.json) passed
for both selected model identities, all 36 classes, activation parity against
Python, image uploads, mixed-mode records, invalid inputs, mobile layout and
recovery from a failed model download. Inference remains entirely in-browser.
The original digit and letter exports are retained for older cached releases.

The verification commands below describe the earlier original-model releases.
Use `digitlab.robust_qa` for the current models. Its default report target is
`reports/robust-browser-qa.json`; the public run was saved separately to
`reports/public-robust-browser-qa.json` to preserve local evidence.

## Scopedog helper release

The Scopedog helper adds `assets/scopedog.jpg`, `v3/helper.js`,
`v3/helper-knowledge.js` and `v3/helper.css`. Deploy these before the updated
`index.html`. The helper uses authored local answers and needs no backend or
API secret. Verify it with `python -m digitlab.helper_qa --url
https://naoquerosaber.pt/AI/ --public`; this writes a separate public report.
The trained weights are unchanged by this interface release.
The [public helper checks](../reports/public-helper-qa.json) and
[recognition checks](../reports/public-helper-recognition-qa.json) pass on the
deployed release. The latest FTPS deployment record covers all 26 assets.

## Words release

Words is deployed at [the public application](https://naoquerosaber.pt/AI/).
All 29 files passed [FTPS verification](../reports/words-ftp-deployment.json),
with replaced files backed up, and independent
[HTTPS hash and JavaScript MIME checks](../reports/public-words-http-assets.json).
The deployment records above remain evidence for their earlier releases.

All 14 [public Words checks](../reports/public-words-release-qa.json) passed,
including real-model transcription of the publisher's handwriting example,
editing, copy/download, cancellation, failure recovery and responsive layouts.
The [public character regression](../reports/public-words-character-regression.json)
passed both models' activation parity, 36 uploads, mixed-mode export and invalid
input checks. All six [public helper groups](../reports/public-words-helper-qa.json)
also passed. This smoke test does not establish word accuracy.

The release adds `v3/words.js`, `v3/words-worker.js` and `v3/words.css`, and updates
`v3/app.js`, `v3/helper.js`, `v3/helper-knowledge.js` and `index.html`. Transfer the
dependencies before the entry page. The deployment utility discovers these assets
automatically; preserve the earlier versioned assets and model exports.

The optional word reader downloads its pinned pretrained weights from Hugging Face
and Transformers.js/WebAssembly from jsDelivr on first use. These are separate
from the digit/letter weights uploaded to this host. First use requires internet
access, and browser caching does not guarantee offline operation. Inference stays
in a browser worker; no server-side recognition service is required.

Use HTTPS and serve `.js` as JavaScript. If hosting enforces a Content Security
Policy, allow same-origin module workers, the pinned jsDelivr runtime, and Hugging
Face model downloads including file-delivery redirects. See [Words notes](words.md)
for the model identity, limitations and validation commands. Run the real-model
smoke test on the deployed origin after any requested deployment, using a fresh
report destination and a non-challenge fixture; local evidence alone is insufficient.

For future uploads, `python -m digitlab.ftp_deploy --upload --report <new-deployment.json>`
preserves the earlier deployment record. For follow-up browser checks, use a fresh
`--report` and `--screenshot-prefix` with `digitlab.words_qa` and
`digitlab.robust_qa`, and a fresh `--report-prefix` with `digitlab.helper_qa`.

## Credentials and directory mapping

Copy the structure in `ftp.example.json` into the ignored `ftp.local.json`. Never commit real credentials. FTPS verifies the server certificate; `tls_hostname` can identify the provider's canonical certificate hostname when it resolves to the same server as the configured host.

The current FTP login directory maps directly to the public `/AI/` directory. Its configuration uses `remote_dir: "/"` and `allow_ftp_root: true`. Do not create another `AI` folder inside it. Recheck this mapping if the FTP account changes.

## Check and deploy

From the project directory:

```powershell
python -m digitlab.ftp_deploy
python -m digitlab.ftp_verify
python -m digitlab.ftp_deploy --upload
.\.venv\Scripts\python.exe -m digitlab.public_qa
.\.venv\Scripts\python.exe -m digitlab.letters_qa --url https://naoquerosaber.pt/AI/ --public
```

The first two commands are read-only. Upload backs up existing files to ignored local artifacts, transfers the application assets, and downloads each uploaded file to verify its SHA-256. It does not delete unrelated remote files. Versioned `v2/` assets and both model directories are uploaded before `index.html` is switched; original root assets remain available for cached v1 pages.

The current design uses `v3/` assets and retains both older versions for cached pages. Verify it with:

```powershell
.\.venv\Scripts\python.exe -m digitlab.design_qa --url https://naoquerosaber.pt/AI/ --public
.\.venv\Scripts\python.exe -m digitlab.public_qa --report public-design-digits-qa.json
.\.venv\Scripts\python.exe -m digitlab.letters_qa --url https://naoquerosaber.pt/AI/ --public --report public-design-letters-qa.json
```

All 25 groups passed for the design release. Earlier report names remain evidence for their own releases rather than being overwritten.

Public QA uses clean handwriting and synthetic fixtures, keeping original local reports and screenshots separate. The historical digit-only result is in `reports/public-browser-qa.json`; new digit and letter results use `reports/public-browser-qa-v2.json` and `reports/public-letters-browser-qa.json` respectively. These checks do not train or tune either model.

Earlier hosting diagnostic reports document genuine 404 and verification-page failures before the directory mapping was corrected. They are historical evidence, not the current public-site status. The trained weights and original challenge record were not changed by deployment.
