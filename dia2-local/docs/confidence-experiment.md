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

## Bounded alternative fixed before its results

The first six full-network epochs have not passed the development gates. Test
one alternative, `captcha-confidence-head-v1`: freeze all image-feature parameters,
extract features from 40,000 independent synthetic training examples and 20,000
clean training examples, and train only the actual final affine classifier.
Use seed 2026101702, sixteen epochs, AdamW 0.0002, weight decay 0.001 and batch
512. Use the same development set and unchanged acceptance gates; select minimum
development NLL before test. This changes trained class boundaries/weights, not
display arithmetic or a global temperature. The official ten remain excluded.
If neither strategy qualifies, retain the active model and report the failed
attempt honestly. Do not lower gates or test rejected candidates on the official
images. See [final-layer experiment](../digitlab/confidence_head.py).

## Actual outcome — 2026-10-17

**Target not achieved; existing default retained.** Both planned experiments ran
to completion. None of their epochs met every predeclared development gate.
The original model, original reports, application files and both public sites
remain unchanged. No score rescaling, temperature calibration or UI percentage
change was made.

| New development set, 6,000 images | Existing model | Full-network final epoch | Final-layer final epoch |
| --- | ---: | ---: | ---: |
| Raw synthetic accuracy | 98.750% | 98.800% | 98.567% |
| Correct prediction with score at least 90%, fraction of all inputs | 94.300% | 94.667% | 94.733% |
| Negative log likelihood, lower is better | 0.04789 | 0.04620 | 0.04674 |
| Clean development accuracy | See recorded baseline | 99.340% | 99.360% |
| Qualifying epoch | Baseline retained | None of eight | None of sixteen |

These final epochs are diagnostics, not selected replacements. Full-network
fine-tuning improved several aggregate measurements but did not reach the minimum
0.5-point correct-at-90 coverage improvement. Final-layer fine-tuning also failed
the raw-accuracy tolerance. The thresholds were not loosened after seeing results.

Actual histories, per-epoch proper-score/calibration diagnostics, environment and
provenance: [full-network report](../reports/captcha-confidence-v1.json) and
[final-layer report](../reports/captcha-confidence-head-v1.json).
The existing Python suite passed **32 tests**, including two new checks separating
confident wrong predictions from correct ones and rejecting apparent confidence
gains with worse proper scores. [Integrity/validation record](../reports/captcha-confidence-validation.json)
checks both completed histories, unchanged baseline identities and prior reports.

Fresh held-out tests, candidate browser QA and official challenge follow-ups were
**NOT RUN** because no candidate qualified. This preserves those test boundaries
and avoids using official outcomes to search for a replacement. Checkpoints are
retained locally in ignored experiment directories; binaries are not committed.

The existing frozen official follow-up remains 10/10 correct, with six top scores
at least 90% and four below it. No new per-image confidence is claimed. Therefore
the participant-reported teacher criterion remains open. The next defensible work
is a separately scoped improvement using broader independently labelled examples
and validation; neither more training nor a guaranteed 90%-on-all result is implied
by this failed attempt. Any subsequent final test must remain separate from model
selection and must preserve the current version.

## Portable follow-up — 2026-10-17

A third, separately scoped [broad-font and averaged-weight experiment](confidence-broad.md)
completed eight Linux epochs using the portable open-font bundle and unchanged
acceptance gates. Its correct-at-90 development gain was 0.25 percentage points,
below the required 0.5 points. No epoch qualified; reserved tests, candidate browser
checks and official follow-up were not run. The active model/sites remain intact,
and the confidence target remains open. See the new protocol/history rather than
attributing this run to the earlier two experiments.

## Diagnostic and architecture follow-up — 2026-10-17

The separately frozen [diagnostic/consistency/capacity suite](confidence-suite.md)
completed its independent preprocessing diagnosis and all three four-epoch arms.
No epoch passed the unchanged development gates. The baseline remains active;
no reserved evaluation, official follow-up or deployment ran. The
[measured summary](../reports/captcha-consistency-suite-v1-summary.md) separates
the synthetic findings from the unresolved official confidence target.
