# Separate 64px CAPTCHA training extension: actual results

Status: **RETAIN BASELINE: independent gate failed**. [Predeclared protocol](../docs/captcha-training-extension.md). This study changes training while preserving the original 64px residual architecture and production preprocessing. Official images, labels, generator and previous official predictions were not used for training or selection.

Each of four epochs used 48,600 images: 32,400 balanced independently generated CAPTCHA-style examples, 10,800 clean MNIST examples and 5,400 clean EMNIST examples. The 5,400 raw development images balance ten classes, three sources, six corruption conditions and three severities. Separate clean validation guards and a legacy bridge check preservation of earlier skills. Fonts, seed, source indices, data, raw scores and all epoch histories are recorded.

| Development model | Raw accuracy | Correct and score >90% | Confident wrong >90% | Raw NLL ↓ | MNIST | EMNIST | Bridge | Eligible |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Preserved baseline | 98.870% | 95.833% (5175) | 11 | 0.03835 | 99.300% | 99.440% | 98.667% | — |
| EMA epoch 1 | 98.907% | 96.130% (5191) | 10 | 0.03467 | 99.260% | 99.480% | 98.708% | False |
| EMA epoch 2 | 98.926% | 96.333% (5202) | 9 | 0.03319 | 99.260% | 99.500% | 98.583% | True |
| EMA epoch 3 | 98.963% | 96.537% (5213) | 9 | 0.03256 | 99.240% | 99.500% | 98.542% | False |
| EMA epoch 4 | 98.963% | 96.593% (5216) | 9 | 0.03312 | 99.300% | 99.460% | 98.583% | True |

Frozen selected epoch: **4**. The original MNIST-only and all current selectable models remain unchanged. No development threshold was relaxed and no epoch was selected using official or reserved results.

## Frozen independent evaluation

| Set | Baseline accuracy | Candidate accuracy | Baseline correct >90% | Candidate correct >90% |
| --- | ---: | ---: | ---: | ---: |
| raw | 99.056% | 99.056% | 95.111% | 96.111% |
| mnist | 99.100% | 99.140% | 97.740% | 97.930% |
| emnist | 99.413% | 99.398% | 98.237% | 98.400% |
| bridge | 98.833% | 98.542% | 94.750% | 94.417% |

Independent gates passed: **False**. Paired raw changes: 12 candidate-only correct; 12 baseline-only correct. These counts do not by themselves establish statistical significance.

The legacy-renderer bridge lost **0.292 percentage points**, exceeding the allowed **0.100 points**. The candidate is retained as an experimental result; the baseline stays active. [Actual official-stage refusal](captcha-training-extension-v1-official-gate.json) confirms that no official outputs were collected.

Official follow-up: **NOT RUN**. No new official confidence result is claimed.

## Evidence and limits

- [Full history, condition/class matrices and provenance](captcha-training-extension-v1.json).
- [Integrity audit](captcha-training-extension-v1-validation.json): preserved source/model identities, data hashes, balanced cells, source membership and saved score counts passed.
- [Unit suite](captcha-training-extension-v1-unit-tests.json): **61 tests passed**.
- [Browser parity and timing](captcha-training-extension-v1-browser.json).
- [Visual spot-check and ambiguous source record](captcha-training-extension-v1-visual-review.json).
- [Fixed raw contact sheet](screenshots/captcha-training-extension-v1-raw-review.png) and [actual 64px inputs](screenshots/captcha-training-extension-v1-prepared-review.png).

The coding agent visually inspected the fixed sample; independent human readability review is **NOT RUN**. Annotations bound geometry/gap loss but do not prove every corrupted digit remains unambiguous. Data are generated CAPTCHA-style images and labelled handwriting, not collected real CAPTCHAs. Font/model/dataset families have prior exposure; no writer-disjoint, near-duplicate or fresh blind population guarantee is made. Strict >90% uses unrounded original model scores; these are not calibrated correctness probabilities.

Linux CPU execution only; fresh Windows execution, public deployment, active-app replacement and push are **NOT RUN**. A successful engineering check is separate from the professor's acceptance criterion. The criterion remains unmet unless a frozen official follow-up actually demonstrates all ten correct with every score strictly >90%.
