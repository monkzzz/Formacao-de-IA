# Fixed-weight preprocessing: first-phase results

The preserved 64px residual CNN and its weights were held fixed. All four preparations saw the same new 1,800 balanced independent development examples and 5,000 clean MNIST validation examples. [Protocol fixed before results](../docs/preprocessing-study.md). No official challenge input, label, generator or previous prediction cache was used.

| Preparation | Raw correct | Raw accuracy | Correct and score >90% | Confident wrong >90% | Raw NLL ↓ | Clean accuracy | Eligible |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| current | 1768/1,800 | 98.222% | 1690/1,800 (93.889%) | 6 | 0.06814 | 99.300% | False |
| median_border | 1767/1,800 | 98.167% | 1690/1,800 (93.889%) | 5 | 0.06708 | 99.300% | False |
| small_components | 1767/1,800 | 98.167% | 1714/1,800 (95.222%) | 5 | 0.06575 | 99.300% | True |
| median_filter | 1775/1,800 | 98.611% | 1698/1,800 (94.333%) | 7 | 0.06747 | 98.020% | False |

Frozen development choice: **small_components**. Small-component cleanup produced 24 more correct predictions above 90%, one fewer correct prediction overall, and one fewer confident incorrect prediction. Its 0.056-point raw accuracy loss is within the predeclared 0.1-point tolerance. Clean accuracy is unchanged; raw NLL improves. This is a measured trade-off, not an across-the-board accuracy improvement.

Median filtering improves raw accuracy but drops clean accuracy by 1.28 percentage points and increases confident errors; it is rejected. Median background estimation does not improve strict confidence coverage enough to qualify.

## Browser and preservation

[Unit checks](fixed-weight-preprocessing-v1-unit-tests.json): **57 passed**. [Isolated browser parity](fixed-weight-preprocessing-v1-browser.json): **60 development uploads passed**, maximum input error 0.0, maximum score error 2.43e-07, real activation parity passed; desktop median inference 34.1 ms and p95 38.8 ms. This is an isolated runtime harness, not an active-app deployment.

[Integrity audit](fixed-weight-preprocessing-v1-validation.json) checks source and raw fixture hashes, source splits, font hashes, saved scores, preview assets and unchanged existing model/app identities. [Actual recorded history](fixed-weight-preprocessing-v1.json).

[Fixed raw/prepared examples](screenshots/fixed-weight-preprocessing-v1-inputs.png). These were inspected visually by the coding agent; independent human readability review remains **NOT RUN**. Labels come from source datasets and rendered classes. This synthetic/font distribution is not a collected real CAPTCHA population, and source-index separation does not establish writer or near-duplicate independence.

## Next boundary

The selected preparation is a development candidate only. Reserved data and the official ten remain unopened in this study. A separately frozen training extension can now compare the preserved 64px model against representative CAPTCHA-style training with this preparation. Final independent evaluation must come after model selection; official outcomes must never choose another transformation, epoch or model. Keep the MNIST-only course model and all current selectable models intact.

No new model training, active-app replacement, official challenge run, deployment or push was performed. The participant cancelled pushing. The professor's 10/10 correct and every score strictly >90% target is still **unmet**; these development figures do not establish it.
