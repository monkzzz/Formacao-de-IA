# Website Hosting

## Submission status — 2026-10-17

The submission application is **v3.10.0** at the existing
[Digit Lab origin](https://naoquerosaber.pt/AI/), using the **captcha-v3**
participant-trained residual CNN by default. See the
[fresh browser/weight checks](../../participant-work/day2/submission-browser-delivery.md).
The participant requested preservation of this site. GitHub Pages publication
and instructor acceptance of the hosting substitution remain pending.
Sections below are versioned deployment history, not competing current releases.

## v3.10.0 single-digit classifier

Release v3.10.0 is published at [Digit Lab](https://naoquerosaber.pt/AI/).
Choose **Digits → Digit model → CAPTCHA Digits** to use the pretrained Legacy
weights with exact single-digit CTC classification. It downloads about 14 MB
and runs in the browser. The existing CNN remains the default and earlier
reader configurations remain available.

All seven scoped uploads passed hash verification with backups and HTML last:
`v3/ctc-digits.js`, `v3/digit-reader-worker.js`, `v3/digit-readers.js`,
`v3/helper-knowledge.js`, `v3/helper.js`, `v3/app.js`, `index.html`.
All 55 public static assets matched local hashes and JavaScript MIME types.
The real public model download, synthetic upload, white-on-dark drawing and
native/browser conditional-score parity checks passed. The maximum score
difference for the public synthetic input was `1.50e-6`.

- [Verified scoped deployment](../reports/release-3.10.0-ftp-deployment.json).
- [All 55 HTTPS asset hashes and MIME types](../reports/release-3.10.0-http-assets.json).
- [All 16 public interface groups](../reports/release-3.10.0-public-ui-qa.json).
- [Actual public download and inference](../reports/release-3.10.0-public-runtime-smoke.json),
  [raw provenance, drawing result and score parity](../reports/release-3.10.0-public-runtime-smoke-captcha-digits-raw.json).
- [Independent experiment and frozen 10/10 local follow-up](ctc-digits.md).

Only generated synthetic inputs were used on the public origin. Official
CAPTCHA images stayed in the local browser; their new frozen follow-up scored
10/10 without subsequent runtime or weight changes. That is a known ten-image
follow-up, not a universal accuracy guarantee. Conditional scores explicitly
assume a single digit and are not calibrated correctness probabilities.

## v3.9.0 CAPTCHA-specific readers

Release v3.9.0 is published at [Digit Lab](https://naoquerosaber.pt/AI/).
It adds selectable DdddOCR and DdddOCR Legacy models, with pinned, SHA-256-verified
weights downloaded from `raw.githubusercontent.com`. Allow that origin alongside
the existing jsDelivr runtime origin if a hosting Content Security Policy is added.
Both run on-device using ONNX Runtime Web `1.20.1` and fixed FP32 weights; model
binaries are not uploaded to this host or committed to Git.

The scoped deployment transferred eight assets, with backups, verified hashes
and HTML last: `assets/ddddocr-LICENSE.txt`, `v3/ddddocr-charsets.json`,
`v3/digit-reader-worker.js`, `v3/digit-readers.js`, `v3/helper-knowledge.js`,
`v3/helper.js`, `v3/app.js` and `index.html`. All 54 public assets match their
local SHA-256 hashes; JavaScript MIME types passed. All 15 public selector/UI
groups passed. Existing model folders and arcade assets remain preserved.

- [Eight verified uploads](../reports/release-3.9.0-ftp-deployment.json).
- [All 54 public asset hashes and MIME types](../reports/release-3.9.0-http-assets.json).
- [Public selector and interface checks](../reports/release-3.9.0-public-ui-qa.json).
- [Both actual public model downloads and synthetic inference](../reports/release-3.9.0-public-download-smoke.json).
- [Model identities, independent screening and frozen follow-up results](captcha-readers.md).

No official images were sent to the public site during this release's evaluation.
The local frozen follow-up measured 8/10 and 9/10 for the two external candidates;
neither is presented as perfect, and the existing project CNN remains the default.
Both actual GitHub weight downloads, hash verification and WASM inference passed
on the public origin, each transcribing a newly generated synthetic `0` correctly.
These are download/integration smoke checks, not accuracy benchmarks. All observed
requests were GET with no bodies. The release's frozen runtime sources remained
unchanged after the official follow-up.

## v3.8.0 selectable digit readers

Release v3.8.0 is published at [Digit Lab](https://naoquerosaber.pt/AI/).
The scoped FTPS deployment uploaded `v3/digit-reader-worker.js`,
`v3/digit-readers.js`, `v3/helper-knowledge.js`, `v3/helper.js`, `v3/app.js`
and `index.html`, switching HTML last. Replaced files were backed up locally;
all six uploaded hashes passed verification. All 52 public static assets
matched their local SHA-256 hashes, including earlier model and arcade assets.
JavaScript MIME types also passed.

- [Scoped FTPS deployment](../reports/release-3.8.0-ftp-deployment.json)
- [All public asset hashes and MIME types](../reports/release-3.8.0-http-assets.json)
- [Public digit reader integration and both real Standard OCR models](../reports/release-3.8.0-public-digit-readers-qa.json)
- [Public character parity, 36 uploads and mixed-export regression](../reports/release-3.8.0-public-character-qa.json)
- [Public Words regression, 19 groups](../reports/release-3.8.0-public-words-qa.json)
- [Public helper regression, 6 groups](../reports/release-3.8.0-public-helper-qa.json)

The default digit CNN and Letters/Words sources and weights are unchanged.
TrOCR alternatives download from Hugging Face when requested and execute in the
browser. See [reader identities and limitations](digit-readers.md). No official
challenge inputs were used in this deployment's checks; no new CAPTCHA accuracy
claim is made.

All 14 digit reader browser groups passed. Both actual Standard readers
transcribed a synthetic `7` correctly on the public origin. This confirms loading
and execution, not CAPTCHA accuracy. Real FP32 OCR inference was not rerun.

## v3.7.0 residual digits

Digits load `model/captcha-v3/digits/`; retain all earlier model folders.
Upload its manifest and weights, `v3/residual.js`, `v3/inference.js`, `v3/app.js`,
`v3/helper-knowledge.js`, `v3/helper.js` and `evaluation/digits-captcha-v3.json`
before switching `index.html`. The deployer sends the residual module before
the inference module. Cached `captcha-2` imports continue to use captcha-v2.

Use the current checks listed in [SKILLS.md](../SKILLS.md), with new report
destinations. The selected model passed independent development and fresh-test
gates before the default changed. See [the complete evidence](residual-training.md).

All nine uploads, all 50 HTTPS assets and live character/raw/runtime/helper/Words
checks passed. Direct live challenge verification scored 10/10, matching the
frozen local input pixels, scores and predictions exactly. No tuning followed.

## Independent benchmark metadata publication

The `ensemble-v1` experiment rejected its diagnostic ensemble and retains the
v3.6.0 classifier. Its publication transfers only
`evaluation/independent-captcha-benchmark.json`,
`evaluation/digits-captcha-v2-original.json` and
`evaluation/digits-captcha-v2.json`. No application source or weights change.
All three uploads and all 46 HTTPS asset hashes passed verification. See
[the experiment and publication evidence](ensemble-benchmark.md).

## v3.6.0 higher-resolution digits

Digits use `model/captcha-v2/digits/`; Letters keep `model/robust/letters/`.
Preserve all earlier model folders. Transfer the new manifest and weights,
`evaluation/digits-captcha-v2.json`, `v3/preprocess.js`, `v3/inference.js`,
`v3/app.js`, `v3/helper-knowledge.js`, `v3/helper.js` and `index.html`.
The deployer orders model/data assets first, shared runtimes before entry
modules, and HTML last. The updated inference file pairs cached `captcha-1`
and `robust-1` imports with their original 28px models.

Use `digitlab.robust_qa --digit-experiment captcha-v2`,
`digitlab.captcha_qa --experiment captcha-v2` and `digitlab.highres_qa` for
that release's model checks, always with new report destinations. The reusable
`digitlab.deployed_challenge` collector verifies public results against the
already frozen local evaluation; it does not select or tune weights.
See [the 64px protocol and evidence](highres-training.md).

The v3.6.0 deployment passed all nine upload hash checks, all 44 HTTPS asset
hashes, public browser checks and direct live challenge verification (9/10,
identical to the frozen local model). Deployment and verification reports are
linked in the protocol document; earlier release evidence remains preserved.

## v3.5.0 digit release

Digits now load `model/captcha-v1/digits/`; Letters still load
`model/robust/letters/`. Preserve the earlier model directories for cached pages.
Deploy the new manifest and weights, `evaluation/digits-captcha.json`,
`v3/inference.js`, `v3/app.js`, `v3/helper-knowledge.js` and `v3/helper.js`
before switching `index.html`. The entry page and changed module imports use new
version queries. The selected digit weight hash is recorded in the
[training/evaluation protocol](captcha-training.md).

Use `digitlab.robust_qa --digit-experiment captcha-v1` for that release's model checks,
with new report and screenshot prefixes. `digitlab.captcha_qa` checks raw
synthetic uploads. Do not rerun the completed official challenge for deployment
verification: match the deployed weight hash and verify independent inputs.

Historical sections below describe the named earlier releases.

The v3.5.0 deployment passed all eight upload hash checks, all 41 HTTPS asset
hashes and live character/raw-upload/helper browser checks. See the
[deployment evidence](captcha-training.md#public-deployment).

For v3.4.2, deploy both Konami assets, `v3/helper.js` and all three SNES frame
assets before `index.html`. This updates the shared module import and frame CSS
for expanded mobile layouts. The separate ROM is unchanged.

For v3.4.1, deploy `v3/konami.js` and `v3/helper.js` before `index.html`.
The helper imports the same versioned arcade module as the entry page. ROM
and emulator frame assets from v3.4.0 remain required.

## v3.4.0 arcade deployment

Deploy `v3/snes.html`, `v3/snes.js`, `v3/snes.css`, `v3/konami.js`,
`v3/konami.css` and the separately supplied `roms/zelda.sfc` before switching
`index.html`. ROM folders are Git-ignored; restore the serving copy manually
on a fresh checkout. See [arcade setup and validation](snes-arcade.md).

Public URL: https://naoquerosaber.pt/AI/index.html

Static application assets and both trained models are served by the hosting account. Inference remains in the browser; no Python service is deployed. Use HTTPS because the model-integrity and upload-record APIs use secure browser capabilities.

## Historical robustness release (before v3.5.0)

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
Use `digitlab.robust_qa --digit-experiment captcha-v3` for the submission CNN. Its default report target is
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

## Historical release: v3.3.0

The [public application](https://naoquerosaber.pt/AI/) displays **v3.3.0** and adds
**67.89% word accuracy (1 − WER)** alongside the digit and letter percentages.
The frozen evaluation used 1,000 real English test lines with 8,912 reference word
tokens. Expandable details show the other error rates and a downloadable summary.
See [the evaluation method and results](words-large-evaluation.md).

All eight [public display checks](../reports/release-3.3.0-public-metrics-qa.json)
and all six [public helper groups](../reports/release-3.3.0-public-helper-qa.json)
passed. All 31 site assets passed [HTTPS hash verification](../reports/release-3.3.0-http-assets.json).
Five changed files were [uploaded with backups and verified hashes](../reports/release-3.3.0-ftp-deployment.json):
`index.html`, `v3/style.css`, `v3/helper.js`, `v3/helper-knowledge.js` and
`evaluation/words-1000.json`. Earlier assets and model binaries remain present.

The downloadable JSON contains metrics and provenance hashes, not dataset images
or the reference-label manifest. The inference sources are byte-identical to the
evaluated v3.2.0 reader. This release performs no additional training or model selection.

<a id="current-release-v320"></a>

## Release v3.2.0

Release **v3.2.0** added a paint-style eraser, adjustable size, Undo/Redo, and
full-precision Words reading by default. Standard remains available for a smaller download.

All 19 [final public UI checks](../reports/release-3.2.0-final-public-ui-qa.json)
passed, including the default quality selection and pixel-exact drawing history.
The separate [real-model checks](../reports/release-3.2.0-public-qa.json) passed
both FP32 and compact reading profiles. The
[public character regression](../reports/release-3.2.0-public-character-qa.json)
passed parity, all 36 uploads, mixed exports and failure recovery; all six
[helper groups](../reports/release-3.2.0-public-helper-qa.json) passed.

The [main upload](../reports/release-3.2.0-ftp-deployment.json) changed nine static
assets, backed up replaced files and verified each uploaded hash. A
[separate entry-page correction](../reports/release-3.2.0-default-ftp-deployment.json)
set the full-precision option as the default. All 30 final site assets passed
[independent HTTPS hash and MIME checks](../reports/release-3.2.0-final-http-assets.json).
The original model files and earlier release assets remain present.

The deployment utility accepts `--files <relative-dist-path> ...` for a scoped
upload. It permits only known local static asset paths and still switches the
entry page last. Use an unused `--report` filename for every deployment, and
verify the complete public asset set after a scoped upload. Reading-profile
weights download from Hugging Face in the browser and are not part of the FTP
upload. See [the precision study](word-precision.md) for sizes and limitations.

## Words release

Release 3.1.0 introduced the visible application version in the footer.
The [versioned deployment record](../reports/release-3.1.0-ftp-deployment.json),
[public browser checks](../reports/release-3.1.0-public-qa.json),
[character regression](../reports/release-3.1.0-character-qa.json) and
[HTTPS asset checks](../reports/release-3.1.0-http-assets.json) all passed.
Keep this version consistent with the `application_version` in exported prediction
JSON. The static `#app-version` text in `dist/index.html` is the version source;
JavaScript reads it for result metadata. It remains visible if model loading fails.
Use major/minor/patch releases for incompatible changes, added features and fixes,
respectively. When changing a browser module or stylesheet, bump its URL version
as well so cached dependencies cannot hide a new release. Model hashes and the
preprocessing contract version remain independent identifiers.

The initial Words release was deployed at [the public application](https://naoquerosaber.pt/AI/).
Its 29 files passed [FTPS verification](../reports/words-ftp-deployment.json),
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
