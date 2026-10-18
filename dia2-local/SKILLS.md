# Digit Lab task workflows

For the professor's no-pretrained-model restriction, build the separate [participant-trained submission](docs/self-trained-submission.md) with `digitlab.self_trained_submission`; verify with `digitlab.self_trained_submission_qa` and a new report path. It bundles verified local checkpoints' exports only. Do not use the earlier general Pages builder for this restricted package: that builder preserves optional pretrained readers.

The [balanced legacy/color training experiment](docs/balanced-color-training.md) completed all four epochs without an eligible replacement. Preserve its [results](reports/balanced-color-training-v1-summary.md) and follow the [gated evaluation guide](docs/balanced-color-evaluation.md). Actual test/export refusal checks passed; reserved/official data remain unopened for this experiment.

The separate [color-aware preprocessing study](docs/color-preprocessing.md) is complete; [results](reports/color-preprocessing-v1-summary.md) show useful color recovery but one additional confidently wrong prediction. Keep active grayscale preprocessing and all weights unchanged. Use `digitlab.color_study`, `digitlab.color_preview` and `digitlab.color_audit` for this preserved development workflow; do not overwrite completed destinations.

The separate 64px training extension has [completed results](reports/captcha-training-extension-v1-summary.md) and a [gated evaluation workflow](docs/captcha-training-extension-evaluation.md). It passed browser parity but failed the independent legacy-renderer preservation gate. Preserve the baseline and frozen candidate; do not rerun its reserved test or open an official follow-up for the rejected candidate.

The new fixed-weight preprocessing phase uses `digitlab.preprocessing_study`,
`digitlab.preprocessing_preview` and `digitlab.preprocessing_study_report`.
Follow [the predeclared protocol](docs/preprocessing-study.md) and preserve the
[completed results](reports/fixed-weight-preprocessing-v1-summary.md).
The selected small-component cleanup passed development and isolated browser
checks only; it is not part of the active application or a verified official result.

Published v3.11.1 separates a default MNIST-only course model from the supplementary
experiment and preserved residual model. Follow
[the selectable-model workflow](docs/selectable-models.md) and run
`digitlab.selectable_models_qa` for the current dataset selector. Historical QA
commands below assume their named default model and matching preserved interface;
use the current selector collector for all three CNNs. The
[3.11.1 release record](docs/release-3.11.1.md) covers both deployed sites.

For Windows/Linux setup, interpreter selection, fonts and browser discovery, use
the [shared runtime guide](../PORTABILITY.md). The current portable confidence
experiment is documented in [its fixed protocol](docs/confidence-broad.md).
The subsequent [diagnostic/consistency/capacity suite](docs/confidence-suite.md)
adds paired-data diagnosis, matched training arms, a deeper isolated browser runtime
and gated final evaluation. Preserve both experiments and their separate identities.

Historical application release v3.10.0 used a default CNN introduced in v3.7.0,
uses 64px residual `captcha-v3` digits and robustness
letters. Use `digitlab.robust_qa --digit-experiment captcha-v3`,
`digitlab.captcha_qa --experiment captcha-v3`, `digitlab.residual_qa --interface`
and `digitlab.words_qa --digit-experiment captcha-v3` with new report paths.
See [the residual protocol and evidence](docs/residual-training.md). Its completed
test and official follow-up are never tuning inputs. Earlier workflows below
remain available for their named releases.

Historical v3.6.0 uses 64px `captcha-v2` digits and robustness letters. For
current character checks, add `--digit-experiment captcha-v2` and use a new
`--report` and `--screenshot-prefix` with `digitlab.robust_qa`. Use
`digitlab.captcha_qa --experiment captcha-v2 --report <new-report.json>` for
full-pipeline synthetic uploads and `digitlab.highres_qa` for dimensions, speed
and cached-entry compatibility. See [the current evidence](docs/highres-training.md).
The completed `captcha-v1-challenge-*.json` records must remain preserved;
do not rerun the official challenge to tune this release. Older examples below
describe their named workflows and original robustness experiments.
The `captcha-v2-challenge-*.json` evaluation is also complete and must be
preserved. `digitlab.deployed_challenge` writes separate live verification.
The completed independent ensemble comparison retained v3.6.0. Its renderer,
frozen development decision, 20,000-image test and rejected candidate are
documented in [the ensemble benchmark](docs/ensemble-benchmark.md). Preserve
those reports; do not rerun or retune the completed test as fresh evidence.

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
.\.venv\Scripts\python.exe -m digitlab.robust_qa --url http://127.0.0.1:8765/ --digit-experiment captcha-v3 --report <new-report.json>
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

For recognition-quality experiments, follow [the precision study](docs/word-precision.md).
Use separate development and fresh test samples, preserve failed candidates, and
identify pretrained models separately from locally trained CNNs. Do not treat a
small line sample or synthetic font words as general recognition accuracy. The
browser collector checks both quality profiles and pixel-exact eraser/undo/redo.

For the homepage word percentage, use the [larger frozen evaluation](docs/words-large-evaluation.md)
and `digitlab.word_metrics_qa --report <new-report.json>`. Keep the visible value,
metric definition, sample counts, helper answer and downloadable summary aligned
with the measured report. Word accuracy here is `1 − WER` on English lines;
do not present it as exact whole-line accuracy or isolated-word classification.
The larger evaluator is resumable and keeps reference labels/images in ignored
storage. Do not tune the reader against the finished benchmark or replace earlier evidence.

Use `digitlab.robust_qa --digit-experiment captcha-v3 --report <new-report.json>` and
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
