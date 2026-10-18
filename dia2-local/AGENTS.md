# Agent instructions — Digit Lab

## Scope and context

These instructions apply to `dia2-local/`, the existing implementation of the Day 2 Desafio exercise. Read [README.md](README.md) before making changes and use [SKILLS.md](SKILLS.md) for task-specific workflows. Follow the parent repository instructions as well.

The course requirements are in [the official challenge](../Dia2/Desafio/README.md) and [Exercise 3, Part 4](../Dia2/Exercicio-03/Parte-04-Teste-do-Desafio.md). This directory contains an implemented solution; extend it rather than creating another starter project.

## Project map

Published v3.12.0 retains the original MNIST-only course default and preserved
residual digit CNN. The supplementary digit CNN and TrOCR digit readers are
archived; Words retains its separate TrOCR handwriting reader, and single letters
retain the EMNIST Letters CNN. The full site and separate restricted Pages
numbers-v5 package are deployed; see [the release record](docs/release-3.12.0.md).
Historical experiments, model exports and evidence remain preserved.

- `digitlab/`: dataset loading, preprocessing, CNN training/export, browser verification, reporting and deployment utilities.
- `dist/`: static application; `v3/` contains the current interface. Retain earlier assets for cached releases.
- `dist/model/captcha-v3/digits/`: current 64px residual digit model. Letters use `dist/model/robust/letters/`; earlier exports remain preserved.
- `tests/`: Python unit tests for the learning and inference pipeline.
- `docs/`: experiment decisions, robustness protocol and hosting instructions.
- `reports/`: measured results and historical verification evidence.
- `artifacts/`, `data/`, `.venv/`: ignored local checkpoints, datasets and environment.

## Evaluation integrity

- The participant subsequently clarified that the professor excludes downloaded
  pretrained models from the submission. Use the separate
  [participant-trained submission package](docs/self-trained-submission.md), with
  the MNIST-only model as the course default and locally trained extensions labelled
  separately. Preserve existing pretrained-reader experiments and the deployed site;
  do not include their weights, remote loaders or word-reader runtime in the package.

- The participant has clarified the professor's current criterion: exactly 10/10
  correct and every original, unrounded score strictly >90%. Use
  `digitlab.acceptance` for new acceptance checks; historical >=90% metrics retain
  their original meaning. Supplementary training is acceptable as a separately
  documented extension; preserve the MNIST-only course model and never tune on the
  official ten. See [the requirement](docs/professor-acceptance.md).

- Never use `../Dia2/Desafio/caso_01.png` through `caso_10.png` for training, validation, model selection or preprocessing tuning.
- Never derive predictions from filenames, manually identified digits, generator labels or a hard-coded answer table. Classification must use image pixels and trained weights.
- Preserve the original `reports/challenge-raw.json`, `reports/challenge-freeze.json`, `artifacts/frozen-app.zip`, associated screenshots and model checkpoints. Do not rerun the original challenge as a new independent first test.
- Keep subsequent experiments and evaluations separate, with their own model identity and evidence. Do not overwrite historical reports to make them describe newer releases.
- Report MNIST accuracy and challenge results separately. The original recorded results are 99.28% on MNIST and 2/10 on the challenge; the robustness release reports 99.32% and 2/10. These are historical measurements, not promises about future changes.
- The v3.5.0 CAPTCHA-style digit release reports 99.20% clean MNIST, 96.97% raw synthetic accuracy and 7/10 on its frozen challenge follow-up. Preserve `reports/captcha-v1-challenge-*.json`; do not tune against or overwrite that completed evaluation.
- The v3.6.0 64px digit release reports 98.91% clean MNIST, 97.90% on its broader raw synthetic test (previous model: 95.09% on identical images), and 9/10 on its frozen challenge follow-up. Preserve `reports/captcha-v2-challenge-*.json` and keep these measurements separate from the earlier synthetic benchmark.
- The completed `ensemble-v1` experiment retained the 64px baseline. Its separate 20,000-image synthetic test measured 96.575% for the baseline and 96.55% for the pre-frozen 90%/10% ensemble. Preserve `reports/ensemble-v1-*.json` and the frozen selection; do not tune weights from the completed test cache or present it as real CAPTCHA population accuracy.
- Mark checks `PASS`, `FAIL`, `BLOCKED` or `NOT RUN` according to actual execution. Do not claim deployment, teacher review or accuracy without evidence.
- The residual `captcha-v3` experiment selected epoch 12 before opening its fresh synthetic test. It measured 99.10% clean MNIST and 98.73% on 20,000 raw synthetic images versus 98.115% for captcha-v2 on identical images. Preserve its selection and reports; do not train or tune against the completed test or subsequent official challenge follow-up.

## Implementation rules

- Keep inference in the browser; the Python server serves static files only.
- Preserve Python/JavaScript preprocessing and activation parity when modifying inference or model export.
- Maintain digit and letter modes, upload, drawing, prediction export and real activation displays when touching shared UI code.
- Treat softmax scores as model scores, not calibrated correctness probabilities.
- Scopedog uses authored local responses. Preserve its explicit fallback and safe text rendering; do not describe it as a generative chatbot.
- Match existing Python style: four spaces and `snake_case`. Keep changes focused and write project-specific documentation in English, as requested.
- Do not commit datasets, weights, caches, credentials or generated screenshots excluded by `.gitignore`. Do not display the contents of `ftp.local.json`.

## Cross-platform runtime

Use the [shared Windows/Linux setup guide](../PORTABILITY.md). The repository's
`setup_course.py` creates `.runtime/windows/day2/Scripts/python.exe` or
`.runtime/linux/day2/bin/python` relative to the repository root. Choose the
runtime for the current OS; an existing `.venv` may belong to the other OS.
Run modules from this directory with that interpreter. Historical PowerShell
examples below remain valid when their interpreter path is adapted.
New portable confidence work uses `digitlab.confidence_broad` and the pinned
open-font bundle; historical experiments still require their exact recorded fonts.
The subsequent `digitlab.confidence_suite` workflow adds diagnosis, consistency
training and capacity comparison; follow its fixed protocol in
[docs/confidence-suite.md](docs/confidence-suite.md). It never changes active assets.

## Validation

Run commands from this directory. Use the existing `.venv` when available:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

For browser changes, start the static server in another terminal and run the relevant checks:

For the local dataset selector use
`python -m digitlab.selectable_models_qa --url http://127.0.0.1:8765/`
with a new `--report`. Historical QA commands below assume
their named default model and matching preserved interface; they do not select
the previous residual model automatically in v3.11.0.

```powershell
.\.venv\Scripts\python.exe serve.py
.\.venv\Scripts\python.exe -m digitlab.robust_qa --url http://127.0.0.1:8765/ --digit-experiment captcha-v3 --report <new-report.json> --screenshot-prefix <new-prefix>
```

Use the specialized workflows in [SKILLS.md](SKILLS.md) for design and helper checks. Inspect report destinations before running collectors so historical evidence is preserved. For documentation-only changes, check relative links and command consistency instead of retraining or rerunning the challenge.

## Delivery

Summarize what changed, which checks actually ran, and any remaining limitations. Public deployment is a separate action from local validation; follow [the hosting guide](docs/hosting.md) when deployment is part of the requested task.
