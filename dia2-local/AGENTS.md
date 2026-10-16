# Agent instructions — Digit Lab

## Scope and context

These instructions apply to `dia2-local/`, the existing implementation of the Day 2 Desafio exercise. Read [README.md](README.md) before making changes and use [SKILLS.md](SKILLS.md) for task-specific workflows. Follow the parent repository instructions as well.

The course requirements are in [the official challenge](../Dia2/Desafio/README.md) and [Exercise 3, Part 4](../Dia2/Exercicio-03/Parte-04-Teste-do-Desafio.md). This directory contains an implemented solution; extend it rather than creating another starter project.

## Project map

- `digitlab/`: dataset loading, preprocessing, CNN training/export, browser verification, reporting and deployment utilities.
- `dist/`: static application; `v3/` contains the current interface. Retain earlier assets for cached releases.
- `dist/model/captcha-v1/digits/`: current digit model. Letters use `dist/model/robust/letters/`; earlier exports remain preserved.
- `tests/`: Python unit tests for the learning and inference pipeline.
- `docs/`: experiment decisions, robustness protocol and hosting instructions.
- `reports/`: measured results and historical verification evidence.
- `artifacts/`, `data/`, `.venv/`: ignored local checkpoints, datasets and environment.

## Evaluation integrity

- Never use `../Dia2/Desafio/caso_01.png` through `caso_10.png` for training, validation, model selection or preprocessing tuning.
- Never derive predictions from filenames, manually identified digits, generator labels or a hard-coded answer table. Classification must use image pixels and trained weights.
- Preserve the original `reports/challenge-raw.json`, `reports/challenge-freeze.json`, `artifacts/frozen-app.zip`, associated screenshots and model checkpoints. Do not rerun the original challenge as a new independent first test.
- Keep subsequent experiments and evaluations separate, with their own model identity and evidence. Do not overwrite historical reports to make them describe newer releases.
- Report MNIST accuracy and challenge results separately. The original recorded results are 99.28% on MNIST and 2/10 on the challenge; the robustness release reports 99.32% and 2/10. These are historical measurements, not promises about future changes.
- The v3.5.0 CAPTCHA-style digit release reports 99.20% clean MNIST, 96.97% raw synthetic accuracy and 7/10 on its frozen challenge follow-up. Preserve `reports/captcha-v1-challenge-*.json`; do not tune against or overwrite that completed evaluation.
- Mark checks `PASS`, `FAIL`, `BLOCKED` or `NOT RUN` according to actual execution. Do not claim deployment, teacher review or accuracy without evidence.

## Implementation rules

- Keep inference in the browser; the Python server serves static files only.
- Preserve Python/JavaScript preprocessing and activation parity when modifying inference or model export.
- Maintain digit and letter modes, upload, drawing, prediction export and real activation displays when touching shared UI code.
- Treat softmax scores as model scores, not calibrated correctness probabilities.
- Scopedog uses authored local responses. Preserve its explicit fallback and safe text rendering; do not describe it as a generative chatbot.
- Match existing Python style: four spaces and `snake_case`. Keep changes focused and write project-specific documentation in English, as requested.
- Do not commit datasets, weights, caches, credentials or generated screenshots excluded by `.gitignore`. Do not display the contents of `ftp.local.json`.

## Validation

Run commands from this directory. Use the existing `.venv` when available:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

For browser changes, start the static server in another terminal and run the relevant checks:

```powershell
.\.venv\Scripts\python.exe serve.py
.\.venv\Scripts\python.exe -m digitlab.robust_qa --url http://127.0.0.1:8765/ --digit-experiment captcha-v1 --report <new-report.json> --screenshot-prefix <new-prefix>
```

Use the specialized workflows in [SKILLS.md](SKILLS.md) for design and helper checks. Inspect report destinations before running collectors so historical evidence is preserved. For documentation-only changes, check relative links and command consistency instead of retraining or rerunning the challenge.

## Delivery

Summarize what changed, which checks actually ran, and any remaining limitations. Public deployment is a separate action from local validation; follow [the hosting guide](docs/hosting.md) when deployment is part of the requested task.
