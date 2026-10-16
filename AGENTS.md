# Repository Guidelines

## Project Structure & Module Organization

This repository contains Portuguese-language materials for a two-day AI course.

- `Dia1/` contains research exercises and theoretical slides in `Teorico/`.
- `Dia1/Exercicios-GSS/` contains Python demonstrations in `modulo1/` and `modulo2/`, supporting assets in `recursos/`, and automated tests in `tests/`.
- `Dia2/` contains agent-engineering exercises, `Dataset-MNIST/`, the official CAPTCHA images in `Desafio/`, and a reference starter repository in `Referencia-Starter-Repo/`.
- `.github/workflows/` contains dataset-import and challenge-generation/evaluation workflows.

Keep student implementations in their own repositories, as directed by the exercises. Read nested `AGENTS.md` files before editing their directories.

## Build, Test, and Development Commands

There is no repository-wide build. Run these commands from `Dia1/Exercicios-GSS/` in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe .\modulo2\dia1_modulo2_01_tokens_ids.py
```

These create an environment, install the base dependencies, and launch a demonstration. Install `requirements-visao.txt` for the optional YOLO exercises; follow the local README to prepare model downloads.

## Coding Style & Naming Conventions

Match existing Python style: four-space indentation, `snake_case` functions and variables, and descriptive class names. Preserve exercise filenames such as `dia1_modulo<N>_<ordem>_<nome>.py`. Keep course documentation in Portuguese and use relative Markdown links. No shared formatter or linter configuration is established; avoid unrelated formatting changes.

## Testing Guidelines

The demonstrations use Python's `unittest` framework. From the exercise directory, run:

```powershell
$env:MPLBACKEND = "Agg"
$env:FORMACAO_LMSTUDIO_OFFLINE = "1"
.\.venv\Scripts\python.exe -m unittest discover -s tests -t .
```

Use `test_*.py` files and `test_*` methods. Prefer synthetic inputs, recorded responses, and mocks for repeatable checks. No coverage threshold is documented. For documentation changes, verify relative links and exercise numbering; for GUI changes, also check the affected interface manually.

## Commit & Pull Request Guidelines

Recent commits use prefixes such as `docs:`, `docs(slides):`, and `feat(exercicios):`, followed by an imperative description. Follow this pattern and keep commits focused.

In pull requests, describe the change, link related issues, and report validation commands and results. Include screenshots for visible interface changes and identify affected lessons when changing teaching material.

## Data & Teaching Integrity

Reserve `Dia2/Desafio/caso_01.png` through `caso_10.png` for final evaluation; never use them for training or tuning. Keep downloaded caches and model weights out of Git. Preserve resource attribution and consult `origem.json` when modifying imported demonstrations.
