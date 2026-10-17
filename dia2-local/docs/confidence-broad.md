# Portable confidence experiment

Protocol fixed before results, 2026-10-17. This continues the requested confidence
work while preparing the same implementation for Windows and Linux. It is a
separate candidate; active application/model assets and previous reports stay
preserved. The official challenge and its generator are excluded from all
training, development and selection.

The previous two strategies did not qualify. This bounded alternative changes
the independent training font distribution, reduces training-only dropout from
0.25 to 0.1, and averages learned weights over optimizer steps (EMA decay 0.99).
Inference still uses the same residual architecture, preprocessing and raw
softmax, with no score multiplier or temperature adjustment. Weight averaging
is part of training; it does not alter displayed percentages after inference.

One run: seed 2026101801, eight epochs, 24,000 newly rendered synthetic training
images per epoch plus a fixed 12,000-image clean training subset, batch 128,
four CPU threads, AdamW 0.0001 with cosine decay to 0.00001 and weight decay
0.0001. The original stratified 55,000/5,000 MNIST split is retained. Each epoch's
EMA candidate is evaluated on 5,000 clean validation examples and 6,000 independent
synthetic development images. Fonts: NotoSans/NotoSerif/RobotoSlab/Oswald for
training, Lato for development, Ubuntu for the reserved synthetic test. Font
files and licenses are downloaded into ignored storage and hashed. The baseline
may have encountered some families previously; these are current-run splits,
not a claim of no prior font exposure in the model's history.

Keep the previous acceptance gates: at least a 0.5 percentage point improvement
in correct predictions scoring at least 90%; raw/clean accuracy each within
0.1 point of baseline; lower raw NLL; Brier no more than 0.001 worse and binned
ECE no more than 0.005 worse. Select the eligible epoch with lowest raw
development NLL. Do not loosen gates after results.

Only an eligible frozen selection can open the separate 10,000-image Ubuntu
synthetic test and canonical MNIST test. Passing the same gates there is required
before export/browser checks. A browser-verified frozen candidate can receive a
separately labelled official follow-up; prior exposure remains explicit. No
official outcome may select an epoch or trigger tuning on those inputs. If no
candidate qualifies, retain the baseline and report the unmet target.

From the repository root, run `python setup_course.py --install --fonts --browser`
with Python 3.12+. Use the printed runtime Python. From `dia2-local/`, run:

```text
<runtime-python> -m digitlab.confidence_broad --stage train
<runtime-python> -m digitlab.confidence_broad --stage test
```

For this Linux session the isolated runtime is `.tmp/confidence-linux/bin/python`
relative to `dia2-local/`. Run destinations refuse overwriting previous results.
This protocol is synthetic evidence, not a guarantee of confidence on all ten
official cases or of real-world probability calibration.

For a fresh checkout, restore missing browser weights with `serve.py --download-models`
(first allowing its hash checks to finish, then stopping the static server) and
run `python -m digitlab.restore_checkpoint` before training. This reconstructs
identical residual tensors without requiring the original serialized checkpoint
container. Existing checkpoint files are never replaced. Historical experiment
source hashes still identify their original source versions; portability changes
are new source, and this experiment records its own current source hashes.

## Actual outcome — 2026-10-17

**No eligible candidate; baseline retained.** All eight epochs completed on Linux.
None met the unchanged development gates. The final EMA checkpoint is retained
in ignored experiment storage for provenance, not selected for deployment.

| Development metric | Preserved baseline | Final epoch |
| --- | ---: | ---: |
| Raw synthetic accuracy | 98.650% | 98.683% |
| Correct prediction with score at least 90%, fraction of all inputs | 95.317% | 95.567% |
| Raw negative log likelihood | 0.04645 | 0.04442 |
| Raw Brier score | 0.02108 | 0.02064 |
| Clean accuracy | 99.300% | 99.220% |

The final correct-at-90 gain is **0.25 percentage points**, below the fixed
0.5-point requirement. Lower loss and a small accuracy improvement do not satisfy
that requirement. No gates were relaxed. The [complete history](../reports/captcha-confidence-broad-v1.json)
records every rejected epoch; [validation](../reports/captcha-confidence-broad-validation.json)
verifies preserved artifact/source identities and that the test command refused
an ineligible selection before opening test data.

Fresh synthetic/MNIST tests, candidate browser QA, official-image follow-up and
publication were **NOT RUN**. The existing model, site assets and original
reports remain unchanged. The confidence-on-all-ten target remains unmet; this
experiment supplies no new per-image official score. There was no output-score
rescaling, temperature adjustment or challenge-driven selection.

Cross-platform setup, browser baseline checks, the pinned font bundle and exact
checkpoint recovery were verified separately in the [portability record](../reports/portability-validation.json).
Windows branches are prepared and tested with mocks; full Windows and hosted CI
execution remain **NOT RUN**.
