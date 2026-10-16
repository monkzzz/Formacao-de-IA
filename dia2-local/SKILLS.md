# Digit Lab task workflows

This is a project workflow reference loaded from [AGENTS.md](AGENTS.md). It is not an automatically installed Codex skill package. Run commands from `dia2-local/`; consult each module's `--help` before using unfamiliar options.

## 1. Understand the solution

**Use when:** starting maintenance or checking exercise compliance.

Read [README.md](README.md), [experiment decisions](docs/experiment.md), [original validation](reports/validation.md) and the [exercise requirements](../Dia2/Exercicio-03/Parte-04-Teste-do-Desafio.md). Identify the affected source, model version and reports before editing.

**Output:** a scoped change and a validation plan tied to the existing implementation. Historical reports describe their recorded versions; verify current behavior separately when needed.

## 2. Train or evaluate a model

**Use when:** explicitly working on training or an isolated model experiment. Do not run training for routine UI or documentation changes.

Read [the robustness protocol](docs/robustness.md), `digitlab/train.py`, `digitlab/letters.py` or `digitlab/robust.py`, according to the task. Use the recorded training/validation splits; select using validation data and reserve official test data for final evaluation. Keep challenge inputs outside this workflow.

Reference entry points:

```powershell
.\.venv\Scripts\python.exe -m digitlab.train --help
.\.venv\Scripts\python.exe -m digitlab.letters --help
.\.venv\Scripts\python.exe -m digitlab.robust --help
```

Use a separate experiment destination supported by the selected module. Preserve existing checkpoints and frozen exports. Record seeds, dependencies, configuration, selected checkpoint, weight hashes and measured metrics.

**Validation:** relevant unit tests, training logs and export/parity checks. A synthetic noisy benchmark does not establish CAPTCHA accuracy.

## 3. Change preprocessing or browser inference

**Use when:** changing image preparation, exported weights, model loading or inference.

Inspect `digitlab/preprocess.py`, model/export code and the corresponding browser implementation in `dist/`. Verify polarity, crop, resize, centering, tensor layout and output class order. Compare Python and JavaScript on identical inputs, including real intermediate activations.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
# Keep serve.py running in another terminal.
.\.venv\Scripts\python.exe -m digitlab.robust_qa --url http://127.0.0.1:8765/
```

**Output:** evidence for both digit and letter inference, uploads, mixed-mode records and error recovery. Use synthetic or non-challenge fixtures for debugging and tuning.

## 4. Change the interface or Scopedog helper

**Use when:** editing `dist/v3/`, navigation, responsive layouts or authored helper answers.

Keep drawing, uploads, mode selection, prediction export and model details usable. Check keyboard access, focus, mobile layouts and safe rendering of user text. Preserve the supplied logo and mascot attribution.

With the local server running, use the relevant collector:

```powershell
.\.venv\Scripts\python.exe -m digitlab.design_qa --help
.\.venv\Scripts\python.exe -m digitlab.helper_qa --url http://127.0.0.1:8765/
```

For classifier-facing UI changes, also run `digitlab.robust_qa`. Inspect collector defaults and report paths before execution; preserve historical evidence. Capture screenshots for visible changes and manually inspect the affected interaction.

**Output:** actual browser results and screenshots. Helper responses must stay consistent with the current application and acknowledge unsupported questions.

For Words changes, read [the Words notes](docs/words.md) and run
`python -m digitlab.words_qa --url http://127.0.0.1:8765/ --report <new-report.json>`.
The default checks distinguish worker doubles from real inference. Supply
`--live-image <non-challenge-handwriting.jpg>` for a real TrOCR smoke test and
optionally `--expected-text` for an exact comparison. Preserve the model revision,
lazy downloads, worker cancellation/retry, original versus edited transcription,
and local-only image processing. No word accuracy is established by a smoke test.
Keep digit/letter scores and activation displays specific to their CNNs.

Use `digitlab.robust_qa --report <new-report.json>` and
`digitlab.helper_qa --report-prefix <new-prefix>` for follow-up regressions without
replacing historical reports. The Words collector refuses existing report paths.

## 5. Document a challenge evaluation

**Use when:** reviewing existing challenge evidence or recording a separately identified follow-up evaluation.

Read [the original validation](reports/validation.md) and [the robustness protocol](docs/robustness.md). The original first run is complete: do not execute `digitlab.challenge` again to replace it.

For an authorized new iteration, freeze source, preprocessing and weight identities before evaluation. Upload all ten official images through the real browser UI; preserve filenames, predictions, all class scores and interface evidence before comparing labels separately. Record prior exposure to challenge outcomes, so a follow-up is not presented as a fresh independent test.

**Output:** a separate report with the runtime version, model hashes, ten raw predictions, comparison, total correct and error analysis. Distinguish model errors from preprocessing or integration failures; retain unsuccessful results.

## 6. Validate or deploy hosting

**Use when:** checking public behavior or carrying out a requested deployment.

Read [docs/hosting.md](docs/hosting.md) and inspect the deployment utility before execution. Verify the account's directory mapping; the documented FTP root maps directly to public `/AI/`. Keep credentials in ignored local configuration, use verified FTPS and preserve remote-file backups.

Prepare and validate local assets first. Use the guide's read-only checks before a requested upload; transfer models and versioned assets before switching the entry page. Download deployed files to verify hashes, then run current-model browser checks against the public URL with separate report destinations.

**Output:** deployment identity, verified asset hashes and public browser evidence. A local pass alone does not establish a public deployment pass.
