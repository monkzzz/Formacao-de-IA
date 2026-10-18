# Balanced legacy/color training: actual results

Status: **RETAIN BASELINE; no development-eligible pair**. [Predeclared protocol](../docs/balanced-color-training.md).

Four CPU epochs; each uses 18,000 balanced synthetic examples (legacy, ordinary color, near-equal-luminance color) plus 6,000 clean MNIST training examples. One RGB-trained network is evaluated under two preprocessing contracts. Official inputs/results never enter preparation, training or selection.

| Development weights | Preparation | Raw accuracy | Correct >90% | Confident wrong >90% | NLL ↓ | Legacy bridge | Clean MNIST | Eligible against both baselines |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Preserved baseline | gray | 65.778% | 63.611% | 4 | 0.79500 | 98.542% | 99.300% | — |
| Preserved baseline | rgb | 98.722% | 95.500% | 5 | 0.03977 | 98.542% | 99.300% | — |
| EMA epoch 1 | gray | 65.722% | 63.556% | 3 | 0.79580 | 98.458% | 99.320% | False |
| EMA epoch 1 | rgb | 98.722% | 95.111% | 4 | 0.04095 | 98.458% | 99.320% | False |
| EMA epoch 2 | gray | 65.778% | 63.556% | 3 | 0.79574 | 98.458% | 99.220% | False |
| EMA epoch 2 | rgb | 98.778% | 95.111% | 4 | 0.04151 | 98.417% | 99.220% | False |
| EMA epoch 3 | gray | 65.778% | 63.500% | 4 | 0.79654 | 98.500% | 99.200% | False |
| EMA epoch 3 | rgb | 98.722% | 95.167% | 5 | 0.04217 | 98.500% | 99.200% | False |
| EMA epoch 4 | gray | 65.722% | 63.444% | 3 | 0.79695 | 98.458% | 99.220% | False |
| EMA epoch 4 | rgb | 98.722% | 95.000% | 4 | 0.04267 | 98.500% | 99.220% | False |

Selected epoch/contract: **None/None**. No gate was relaxed.

The last epoch's RGB contract failed: rgb baseline: strict_90_gain, lower_nll, brier.

Reserved test: **NOT RUN**; no development-eligible candidate.

Official follow-up: **NOT RUN**.

[Full history/provenance](balanced-color-training-v1.json), [integrity audit](balanced-color-training-v1-validation.json), [unit suite](balanced-color-training-v1-unit-tests.json).

[Visual review](balanced-color-training-v1-visual-review.json): fixed all-class/all-source/all-group sample inspected by the coding agent before training. Independent human readability review is NOT RUN. Synthetic labels, replay and source separation do not prove every distorted glyph is unambiguous. History includes font/model/source exposure; these are synthetic development/test figures, not real CAPTCHA population accuracy.

The MNIST-only model, earlier extensions and active application remain unchanged. No deployment, CUDA setup, commit or push is part of this run. Softmax scores are not calibrated correctness probabilities. The professor's criterion remains unmet unless a frozen official follow-up demonstrates all ten correct with every original score strictly >90%.
