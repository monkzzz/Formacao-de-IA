# Digit Lab — Local Desafio Project

Two CNNs trained from scratch on MNIST and EMNIST Letters, with a static browser application for drawing, multi-image upload, real feature maps, and raw prediction export. Choose **Digits (0–9)** or **Letters (A–Z)** before classifying one character. Uppercase and lowercase handwriting share a letter class; the app does not read words or distinguish case. Training runs locally; images are never submitted to an inference API.

**Public application:** [Digit Lab](https://naoquerosaber.pt/AI/index.html). All nine [digit regression groups](reports/public-browser-qa-v2.json) and ten [letter verification groups](reports/public-letters-browser-qa.json) passed on the updated HTTPS site. See the [hosting guide](docs/hosting.md). Original digit-only public verification is retained in [its historical report](reports/public-browser-qa.json).

**Design release:** the `v3/` interface adds a clearer workspace, readable prediction cards, a bounded image gallery with two columns on phones, and keyboard-accessible expandable model details. All 25 [design and recognition verification groups](reports/design-validation.md) passed locally and on the public website at that release. Those reports describe the original models.

The header logo, footer logo, and favicon use the supplied `65474617.jpg`, published unchanged as `dist/assets/65474617.jpg`. [Live logo verification](reports/logo-verification.json) confirms the image checksum, loading, mobile layout, and model readiness.

## Start the application

From this directory in PowerShell:

```powershell
python serve.py
```

Open **http://127.0.0.1:8765**. Keep the terminal running; press Ctrl+C to stop it. Only `dist/` is served. Python serves static files; the browser computes every classification.

**Original measured results:** 9,928/10,000 correct on official MNIST (**99.28%**); 2/10 correct on the independent Desafio run (**20%**). See the [validation report](reports/validation.md) for predictions, limitations, curves, and parity checks. These are separate evaluations.

**Original letters:** 19,508/20,800 correct on the official EMNIST Letters test (**93.79%**). See the [letter validation report](reports/letters-validation.md). The original digit weights and first Desafio predictions remain unchanged.

## Improved recognition release

The local and public `v3/` apps now load separately trained robustness models from `dist/model/robust/`. Additional training varies handwriting shape, stroke width, noise and short occlusions while retaining clean examples. Selection uses the original validation splits, with no challenge images. The [public release verification](reports/public-robust-browser-qa.json) confirms both new weight identities, Python/JavaScript activation parity, 36 uploads, mixed-mode results and failure recovery. All 22 deployed assets passed SHA-256 download verification; replaced files were backed up.

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
.\.venv\Scripts\python.exe -m digitlab.robust_qa --url http://127.0.0.1:8765/
```

Training reads `../Dia2/Dataset-MNIST/data/` by default; override with `--data <directory>` if moving the personal project. It refuses to overwrite an existing checkpoint. Use a separate experiment directory for new training. To reevaluate the existing checkpoint, use `-m digitlab.train --evaluate-only` before challenge freezing; do not replace the frozen first-run artifacts afterward.

Architecture: Conv16 → pool → Conv32 → pool → Dense128 → 10. The recorded seed determines a stratified 55,000/5,000 training/validation split. The model is selected by validation loss. The 10,000 official test images are evaluated after selection. See [experiment decisions](docs/experiment.md), [training history](reports/training.json), and [MNIST metrics](reports/mnist-test.json).

## Train and verify letters

```powershell
.\.venv\Scripts\python.exe -m digitlab.emnist_data
.\.venv\Scripts\python.exe -m digitlab.letters --epochs 24 --threads 4
.\.venv\Scripts\python.exe -m digitlab.robust_qa --url http://127.0.0.1:8765/
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
- `dist/`: entry page, retained v1/v2 assets, current interface in `v3/`, and digit/letter inference models.
- `tests/`: data separation, preprocessing, gradients, learning, and export checks.
- `reports/`: real metrics, runtime parity results, and evaluation evidence.
- `artifacts/`: ignored checkpoint, split indices, and frozen application archive.

## Accuracy and limitations

MNIST test accuracy does not establish accuracy on noisy CAPTCHA images or arbitrary uploads. Displayed scores are softmax outputs, not calibrated correctness probabilities. The prepared input and real activations help inspect errors; they do not provide a complete causal explanation. The preprocessing assumes a broadly uniform border background and one digit per image.

The application has been uploaded over FTPS and verified on the public HTTPS website. Teacher review has not been performed. The original local validation report is retained as a record of the first evaluation.

## Attribution

Based on the Day 2 exercise requirements by Vinicius Canonici and Hugo Gomes; see the [course license](../LICENSE.md). MNIST is credited to Yann LeCun, Corinna Cortes and collaborators. The reference application was examined for design ideas; this implementation and its trained parameters were created independently.

EMNIST: Cohen, Afshar, Tapson, and van Schaik (2017), [EMNIST: an extension of MNIST to handwritten letters](https://arxiv.org/abs/1702.05373), distributed by [NIST](https://www.nist.gov/itl/products-and-services/emnist-dataset).
