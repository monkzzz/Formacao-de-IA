# Independent confidence follow-up

The participant reports that the teacher wants the correct digit to receive at
least about 90% on each official CAPTCHA. The current frozen model recognized
10/10 but assigned less than 90% to four inputs. This is participant-reported
feedback, not a separately witnessed teacher session or approval.

Preserve the active model, original development and both public sites. Train one
separate residual candidate from the captcha-v3 checkpoint, using unmodified cross
entropy and the existing raw synthetic renderers. There is no score rescaling,
temperature adjustment, label lookup or challenge-specific preprocessing.

Protocol fixed before running: seed 2026101701, eight epochs of 30,000 freshly
rendered training examples and 15,000 clean training examples, original stratified
55,000/5,000 split, AdamW 0.0001 with cosine decay to 0.000005, batch 128, four CPU
threads. Retain the existing 36 training font faces. Development uses six separate
fonts and 6,000 new images; the 10,000-image test uses four separate font families
and a distinct seed. Checkpoints, datasets and raw caches remain ignored.

Select on independent development only: minimize raw negative log likelihood
among epochs meeting all recorded accuracy, correct-at-90 coverage, Brier and
calibration-error gates. These diagnostics discourage simply becoming more
confident while making more confident mistakes. Calibration error is a binned
sample diagnostic, not proof of calibrated real-world probabilities. Selection
ends before test data is loaded; test results are not used for further tuning.
Preserve rejected epochs and retain the original model if no epoch qualifies.

The exact gates, source/font hashes, environment, history and selected epoch are
recorded by [the experiment](../digitlab/confidence.py) in a new report. Only a
qualified candidate proceeds to fresh independent test and real browser parity.
Before any official follow-up, freeze the model/runtime and report all ten raw
predictions and scores honestly. Do not use that outcome to pick another epoch,
retrain, rescale scores or tune preprocessing. No 90%-on-all outcome is promised.
Prior exposure means any official follow-up is not a new blind accuracy test.

Commands from `dia2-local/`:

```powershell
.\.venv\Scripts\python.exe -m digitlab.confidence --stage train
.\.venv\Scripts\python.exe -m digitlab.confidence --stage test
```

Both stages preserve completed outputs. The test refuses to proceed without a
frozen eligible selection. Application publication is a separate reviewed step;
this experiment never changes an active model or public site.
