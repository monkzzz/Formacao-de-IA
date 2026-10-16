# Digit Lab — Local Desafio Project

**Current application release: v3.7.0.** Enter the Konami code to open the secret
SNES arcade. The supplied Zelda ROM is a separate deployment asset excluded from
Git. See [arcade setup, controls and validation](docs/snes-arcade.md).

Two CNNs trained from scratch on MNIST and EMNIST Letters, with a static browser application for drawing, multi-image upload, real feature maps, and raw prediction export. Choose **Digits (0–9)** or **Letters (A–Z)** before classifying one character; uppercase and lowercase handwriting share a letter class. The additional **Words** mode uses a separate pretrained handwriting model to transcribe a word or short English line into editable text. Images are never submitted to an inference API.

**Public application:** [Digit Lab](https://naoquerosaber.pt/AI/index.html). All nine [digit regression groups](reports/public-browser-qa-v2.json) and ten [letter verification groups](reports/public-letters-browser-qa.json) passed on the updated HTTPS site. See the [hosting guide](docs/hosting.md). Original digit-only public verification is retained in [its historical report](reports/public-browser-qa.json).

**Design release:** the `v3/` interface adds a clearer workspace, readable prediction cards, a bounded image gallery with two columns on phones, and keyboard-accessible expandable model details. All 25 [design and recognition verification groups](reports/design-validation.md) passed locally and on the public website at that release. Those reports describe the original models.

The header logo, footer logo, and favicon use the supplied `65474617.jpg`, published unchanged as `dist/assets/65474617.jpg`. [Live logo verification](reports/logo-verification.json) confirms the image checksum, loading, mobile layout, and model readiness.

## Residual digits (v3.7.0)

Digits now use a compact residual CNN with the same 64px input contract. It was
selected on independent development data, then compared with v3.6.0 on a fresh
20,000-image synthetic test: **98.73% versus 98.115%** (123 more correct).
Clean MNIST improved from **98.91% to 99.10%**. This synthetic benchmark differs
from the earlier experiments and does not establish real CAPTCHA accuracy.

The model loads from `dist/model/captcha-v3/digits/`. Letters, Words and earlier
model folders remain preserved. Its frozen official challenge follow-up scored
**10/10**, versus 9/10 previously; known prior outcomes mean this is not a new
blind test. See [the protocol, results and deployment evidence](docs/residual-training.md).

## Higher-resolution digits (v3.6.0, historical)

**Independent ensemble experiment completed:** a new 10,000-image development
set and 20,000-image synthetic test use separate, previously unused font families
and a new renderer. The best development ensemble failed the preset improvement
gate. On the frozen test it scored **96.55%**, versus **96.58%** for the current
64px model. The current classifier remains deployed. These figures describe a
different synthetic benchmark from the v3.6.0 training evaluation below.
See the [protocol, results and decision](docs/ensemble-benchmark.md).

Digits now use **64 x 64 inputs** and broader independent synthetic training,
including 31 font faces, short stroke gaps, shear and denser interference.
Epoch 12 was selected using separate validation data before loading test data.
The official challenge images and generator were excluded from training and
selection. Letters retain their 28px model; Words retains its pretrained reader.

| Evaluation | Previous 28px digit model | New 64px digit model |
| --- | ---: | ---: |
| Clean MNIST, 10,000 images | 99.20% | **98.91%** |
| Broader raw synthetic test, 10,000 images | 95.09% | **97.90%** |
| Official Desafio follow-up, 10 images | 7/10 | **9/10** |

Both models use the same raw synthetic test images with their own preprocessing.
This broader benchmark differs from the v3.5.0 synthetic benchmark. Clean MNIST
accuracy decreased by 0.29 percentage points. The official challenge was uploaded
once after freezing the selected model and runtime; its earlier outcomes were
known, so this is a follow-up, not a new blind test. No tuning followed the result.
Nine of ten does not establish general CAPTCHA population accuracy.

Digits load from `dist/model/captcha-v2/digits/`. Real previews and feature maps
follow the selected model's dimensions; each exported image identifies its input
size and preprocessing contract. Older cached module entry points retain their
matching 28px models. All earlier checkpoints, exports and reports remain preserved.

All 23 Python tests passed. Local browser checks passed 36 clean uploads,
60 noisy uploads, activations, pixels, drawing, mode changes, exports, error
recovery, the helper and cached-page compatibility. Selected-model desktop Edge
inference measured 54.6ms median and 71.2ms p95; physical-phone speed is unmeasured.

See the [protocol and evidence](docs/highres-training.md),
[training/test results](reports/captcha-v2.json),
[browser regression](reports/captcha-v2-browser-qa.json),
[runtime and speed checks](reports/captcha-v2-runtime-qa.json), and
[frozen challenge comparison](reports/captcha-v2-challenge-comparison.json).

**v3.6.0 is live.** All nine changed uploads, all 44 HTTPS asset hashes and live
browser checks passed. Direct upload of all ten `caso_` files on the public site
also scored **9/10**, exactly matching the frozen local results. See
[deployment and direct live verification](docs/highres-training.md#public-deployment-and-direct-challenge-verification).

## CAPTCHA-style digit release (v3.5.0, historical)

The digit model now trains on independent printed and handwritten images with
clutter rendered **before** upload preprocessing. Epoch 11 was selected from a
fixed 12-epoch run. Validation uses separate handwriting samples and four
held-out font families. Official challenge images and their generator are
excluded from training and selection.

| Held-out evaluation | Previous robustness digits | CAPTCHA-style digits |
| --- | ---: | ---: |
| Clean MNIST, 10,000 images | 99.32% | **99.20%** |
| Raw synthetic noisy images, 10,000 | 87.27% | **96.97%** |
| Official Desafio, 10 images | 2/10 | **7/10** |

The synthetic benchmark includes the whole upload preprocessing pipeline and
differs from the earlier normalized-noise benchmark. The final challenge was
uploaded once after freezing the model and runtime. Prior challenge outcomes
were known: this is a follow-up evaluation, not a fresh blind test. No training
or inference changes followed that result. Seven of ten is a small sample
result, not a general CAPTCHA accuracy guarantee.

Digits load from `dist/model/captcha-v1/digits/`; Letters retain the robustness
model and Words retains its pretrained reader. Earlier models and reports remain
preserved. Weight binaries are ignored by Git and deployed separately; fresh
checkouts can restore verified release weights with `python serve.py --download-models`.

See the [protocol and validation](docs/captcha-training.md),
[training/test results](reports/captcha-v1.json),
[browser parity and regression](reports/captcha-v1-browser-qa.json),
[raw upload checks](reports/captcha-v1-raw-browser-qa.json), and
[final challenge comparison](reports/captcha-v1-challenge-comparison.json).

**v3.5.0 deployment:** All eight changed uploads, all 41 public asset hashes,
character regression, 40 raw synthetic uploads and six helper groups passed.
See the [public deployment evidence](docs/captcha-training.md#public-deployment).

## Start the application

From this directory in PowerShell:

```powershell
python serve.py --download-models
```

Open **http://127.0.0.1:8765**. Keep the terminal running; press Ctrl+C to stop it. Only `dist/` is served. Python serves static files; the browser computes every classification.

A fresh Git clone does not include the trained weight binaries. On first start,
`--download-models` downloads the missing digit and letter release weights from
the public application and verifies them against the SHA-256 hashes in the local
manifests. This requires internet access but no training or extra Python packages.
Subsequent starts can use `python serve.py` offline. If the public weights no longer
match this checkout, setup stops rather than loading a different model.

**Original measured results:** 9,928/10,000 correct on official MNIST (**99.28%**); 2/10 correct on the independent Desafio run (**20%**). See the [validation report](reports/validation.md) for predictions, limitations, curves, and parity checks. These are separate evaluations.

**Original letters:** 19,508/20,800 correct on the official EMNIST Letters test (**93.79%**). See the [letter validation report](reports/letters-validation.md). The original digit weights and first Desafio predictions remain unchanged.

## Improved recognition release

This section records the earlier robustness release. Current digit results and
model paths are documented in the v3.5.0 section above.

The local and public `v3/` apps now load separately trained robustness models from `dist/model/robust/`. Additional training varies handwriting shape, stroke width, noise and short occlusions while retaining clean examples. Selection uses the original validation splits, with no challenge images. The [public release verification](reports/public-robust-browser-qa.json) confirms both new weight identities, Python/JavaScript activation parity, 36 uploads, mixed-mode results and failure recovery. All 26 deployed assets passed SHA-256 download verification; replaced files were backed up.

| Held-out evaluation | Original | Updated |
| --- | ---: | ---: |
| Official MNIST, 10,000 digits | 99.28% | **99.32%** |
| Synthetic noisy MNIST | 97.03% | **98.18%** |
| Official EMNIST Letters, 20,800 letters | 93.79% | **93.86%** |
| Synthetic noisy EMNIST Letters | 87.17% | **90.83%** |
| Official Desafio, 10 digit images | 2/10 | **2/10** |

Both models improve on the synthetic noisy benchmark, with small clean-test gains. **The official Desafio score did not improve.** Synthetic perturbations act on normalized inputs and do not establish CAPTCHA robustness. The follow-up challenge was run once after freezing the selected runtime and weights; no subsequent tuning was performed.

See the [training and evaluation protocol](docs/robustness.md), [digit metrics](reports/robust-digits.json), [letter metrics](reports/robust-letters.json), [browser verification](reports/robust-browser-qa.json), and [final challenge comparison](reports/robust-challenge-comparison.json). Eleven unit tests pass; browser checks verify Python/JavaScript activations, 36 uploads, mixed-mode results, error handling and original checkpoint preservation.

To reproduce additional training from the original checkpoints, use `python -m digitlab.robust --epochs 10 --threads 4` in the existing environment. It refuses to overwrite existing robustness experiments. Model binaries are ignored by Git and are deployed separately; copy `dist/model/robust/` with the app.

The trained weights already exist locally in `dist/model/weights.bin`. They and intermediate checkpoints are ignored by Git. Preserve them if moving the project, or reproduce training using the commands below.

## Words mode

The footer displays the application release, currently **v3.7.0**. Character
prediction JSON includes `application_version`; Words result metadata also keeps
that version alongside the model identity. This release number identifies the
website, separately from model weight hashes and preprocessing versions.
See [release history and versioning instructions](docs/releases.md).

Use **Eraser** to remove individual marks, adjust **Eraser size**, and select
**Pen** to write again. **Undo** and **Redo** work in Digits, Letters and Words,
including after Clear. With the canvas focused, use Ctrl+Z and Ctrl+Shift+Z
(or Ctrl+Y). Read the handwriting again after editing it.

**v3.2.0 deployment evidence:** the [final public interface checks](reports/release-3.2.0-final-public-ui-qa.json),
[real reading-profile checks](reports/release-3.2.0-public-qa.json),
[digit/letter regression](reports/release-3.2.0-public-character-qa.json),
[helper checks](reports/release-3.2.0-public-helper-qa.json) and
[all 30 public asset hashes](reports/release-3.2.0-final-http-assets.json) passed.
The Python suite passed all 16 tests. The word model remains pretrained; this
release changes weight precision and drawing tools, with no additional training.

Choose **Words** to write one word or a short English handwriting line on a wider
canvas, or upload one cropped PNG, JPEG or WebP image. Select **Read my words**
after drawing; image selection starts reading automatically. Review and edit the
transcription, then **Copy text** or **Download .txt**. The original model output
remains available under **Original model transcription**. Cancel stops loading
or inference, and leaving Words mode cancels an active read.

This optional mode uses the pretrained [TrOCR Small handwriting model](https://huggingface.co/microsoft/trocr-small-handwritten),
fine-tuned on IAM English handwriting, through [Xenova's ONNX conversion](https://huggingface.co/Xenova/trocr-small-handwritten)
at revision `2432e24d184b1d964d07ed04f5d9e21d31a59141` and Transformers.js 2.17.2.
Full precision is the default and downloads approximately 250 MB of weights;
Standard downloads approximately 65 MB of compact weights from Hugging Face
plus the JavaScript/WebAssembly runtime from jsDelivr. The browser may cache these
files; offline use is not guaranteed. No account, API key, Python inference server
or additional local training is needed. Image pixels and text stay on the device.

A limited, separately sampled English handwriting comparison favored full-precision
weights; see [the measured results and limitations](docs/word-precision.md).
This does not establish general word accuracy. It can add, omit or
misread text; full pages, multiple lines and other languages are outside this
mode's scope. Digit/letter benchmark scores and CNN activation displays do not
apply to this separate sequence model. Existing character inference is unchanged.

The homepage now adds **67.89% word accuracy (1 − WER)** beside the digit and letter
percentages. The fixed Full precision reader was evaluated on **1,000 real English
IAM test lines**, containing **8,912 reference word tokens**. Word error rate is
32.11%, character error rate 9.60%, and exact whole-line accuracy 15.30%. These
measurements have different units from digit/letter image classification.
See [the larger evaluation protocol and results](docs/words-large-evaluation.md).

**v3.3.0 is live.** All eight [public metric-display checks](reports/release-3.3.0-public-metrics-qa.json),
all six [public helper groups](reports/release-3.3.0-public-helper-qa.json), and
[all 31 public asset hashes](reports/release-3.3.0-http-assets.json) passed.

See [the Words implementation and validation notes](docs/words.md).

**Original Words release evidence:** Words was deployed to the [public website](https://naoquerosaber.pt/AI/).
All 14 [public Words browser checks](reports/public-words-release-qa.json), the
[public digit/letter regression](reports/public-words-character-regression.json),
and all six [public helper groups](reports/public-words-helper-qa.json) passed.
All 29 deployed files passed [FTPS upload verification](reports/words-ftp-deployment.json)
and independent [HTTPS hash checks](reports/public-words-http-assets.json).

Local verification also passed all 14 [Words browser checks](reports/words-release-qa.json),
the [digit/letter regression](reports/words-character-regression.json), and all six
[Scopedog regression groups](reports/words-helper-qa.json) passed. The real model
transcribed the publisher's example as `Mr. Brown commented icily.`; this single
smoke test is not an accuracy benchmark. The Python unit suite passed all 14 tests.

With a local server running, check Words without downloading its model:

```powershell
.\.venv\Scripts\python.exe -m digitlab.words_qa --url http://127.0.0.1:8765/ --report words-ui-followup.json
```

This checks the interface with an explicitly identified worker double and checks
real digit/letter activation parity. Add `--live-image <handwriting-image.jpg>`
to exercise the real word reader. Use a new report name for each run; the Words
collector refuses to overwrite previous evidence.

## Scopedog page guide

Select **Ask Scopedog** in the lower-right corner for help using the page or
understanding the technology. Type a question or choose a suggested topic.
Scopedog covers drawing, uploads, modes, preprocessing, CNN layers, training,
datasets, scores, privacy, result exports and the Desafio. Navigation buttons
open the relevant page section; questions about the current prediction use
the displayed result without changing the classifier.

This is a browser-only guide with authored answers and keyword/phrase matching,
not a generative AI chatbot. It makes no chat API requests, requires no API key
and keeps no conversation after a reload. Unknown questions get an explicit
fallback rather than an invented answer. The supplied mascot is included
unchanged as `dist/assets/scopedog.jpg`.

With `serve.py --port 8766` running, verify the helper using:

```powershell
.\.venv\Scripts\python.exe -m digitlab.helper_qa
```

The browser checks cover question routing, live prediction context, navigation,
keyboard/focus behavior, safe text rendering, portrait/landscape layouts and
absence of remote chat requests. Screenshots are saved in `reports/screenshots/`.
See the captured [desktop](docs/images/scopedog-desktop.png) and
[mobile](docs/images/scopedog-mobile.png) interfaces.
The helper is deployed on the public website: all six
[public helper checks](reports/public-helper-qa.json) and the
[digit/letter regression checks](reports/public-helper-recognition-qa.json) pass.

## Reproduce the environment

Python 3.12 and installed Microsoft Edge are used for this verified Windows setup. If the environment is missing:

```powershell
python -m venv .venv
python -m pip --python .\.venv\Scripts\python.exe install -r requirements-lock.txt
```

The lock file records the versions actually installed. Initial dependency installation needs internet access; training uses the local course data and browser inference needs no external connection.

## Train, evaluate, and test

```powershell
.\.venv\Scripts\python.exe -m digitlab.train --epochs 18 --threads 4
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
# Start serve.py in another terminal before checking the current browser app:
.\.venv\Scripts\python.exe -m digitlab.robust_qa --url http://127.0.0.1:8765/ --digit-experiment captcha-v3 --report current-character-check.json
```

Training reads `../Dia2/Dataset-MNIST/data/` by default; override with `--data <directory>` if moving the personal project. It refuses to overwrite an existing checkpoint. Use a separate experiment directory for new training. To reevaluate the existing checkpoint, use `-m digitlab.train --evaluate-only` before challenge freezing; do not replace the frozen first-run artifacts afterward.

Architecture: Conv16 → pool → Conv32 → pool → Dense128 → 10. The recorded seed determines a stratified 55,000/5,000 training/validation split. The model is selected by validation loss. The 10,000 official test images are evaluated after selection. See [experiment decisions](docs/experiment.md), [training history](reports/training.json), and [MNIST metrics](reports/mnist-test.json).

## Train and verify letters

```powershell
.\.venv\Scripts\python.exe -m digitlab.emnist_data
.\.venv\Scripts\python.exe -m digitlab.letters --epochs 24 --threads 4
.\.venv\Scripts\python.exe -m digitlab.robust_qa --url http://127.0.0.1:8765/ --digit-experiment captcha-v3 --report current-letter-check.json
.\.venv\Scripts\python.exe -m digitlab.letters_report
```

The downloader retrieves the official approximately 540 MB NIST archive, verifies its canonical checksum, and extracts the Letters split into ignored `data/emnist/`. Letter training uses 114,400 training and 10,400 validation examples, selects by validation loss, then evaluates all 20,800 official test examples. It refuses to overwrite an existing letter checkpoint. The model uses the same spatial layout with 26 outputs and exports to `dist/model/letters/`.

Run `serve.py` before browser checks. The v2 digit and letter QA reports are separate from the original first-run records. Versioned assets in `dist/v2/` allow cached digit-only pages to continue using their original assets while the updated entry page is deployed.

## Original challenge protocol

The first run freezes source and trained weights, then uploads all ten official PNGs through the actual local UI:

```powershell
.\.venv\Scripts\python.exe -m digitlab.challenge
```

This command refuses to overwrite its freeze or raw predictions. It does not read the generator or labels. Preserve `reports/challenge-raw.json`, `reports/challenge-freeze.json`, `artifacts/frozen-app.zip`, and screenshots before comparing labels separately. Do not use challenge results to tune the first model.

The preserved run needed a collector-only repair to accept local blob preview URLs; its retry reused the original frozen inference. See the report for details. The completed raw record and comparison are retained; do not rerun them as a new independent first test.

To regenerate report figures without changing the model or raw record:

```powershell
python -m pip --python .\.venv\Scripts\python.exe install -r requirements-report.txt
.\.venv\Scripts\python.exe -m digitlab.report
```

`requirements-lock.txt` preserves the original training environment. The separate report dependency file adds plotting tools installed after evaluation.

## Project structure

- `digitlab/`: strict IDX loading, shared preprocessing, CNN, training/export, browser QA, and first-run challenge recording.
- `dist/`: entry page, retained v1/v2 assets, current interface in `v3/`, and digit/letter inference models. `v3/words.js`, `words-worker.js` and `words.css` provide the optional word reader; its pretrained weights download separately in the browser.
- `tests/`: data separation, preprocessing, gradients, learning, and export checks.
- `reports/`: real metrics, runtime parity results, and evaluation evidence.
- `artifacts/`: ignored checkpoint, split indices, and frozen application archive.

## Accuracy and limitations

MNIST test accuracy does not establish accuracy on noisy CAPTCHA images or arbitrary uploads. Displayed scores are softmax outputs, not calibrated correctness probabilities. The prepared input and real activations help inspect errors; they do not provide a complete causal explanation. The preprocessing assumes a broadly uniform border background and one digit per image.

The application has been uploaded over FTPS and verified on the public HTTPS website. Teacher review has not been performed. The original local validation report is retained as a record of the first evaluation.

## Attribution

Based on the Day 2 exercise requirements by Vinicius Canonici and Hugo Gomes; see the [course license](../LICENSE.md). MNIST is credited to Yann LeCun, Corinna Cortes and collaborators. The reference application was examined for design ideas; the digit/letter CNN implementation and its trained parameters were created independently. Words uses Microsoft's pretrained TrOCR model through Xenova's browser conversion; it was not trained by this project.

EMNIST: Cohen, Afshar, Tapson, and van Schaik (2017), [EMNIST: an extension of MNIST to handwritten letters](https://arxiv.org/abs/1702.05373), distributed by [NIST](https://www.nist.gov/itl/products-and-services/emnist-dataset).
