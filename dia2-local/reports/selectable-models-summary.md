# Selectable models: measured local results

Local v3.11.0 defaults to the preserved MNIST-only course model. The optional extension is a separate experiment. The previous residual model remains selectable with unchanged weights. [Dataset boundaries and reproduction](../docs/selectable-models.md). Public deployment: **NOT RUN**.

The extension trained for 4 epochs on 302,000 examples per epoch: 55,000 MNIST + 235,000 EMNIST Digits + 12,000 independent synthetic examples. Epoch **4** was frozen from validation NLL before test metrics were computed.

Both models below were evaluated on the same reserved inputs after that freeze. The synthetic test has 2,400 examples; EMNIST is real handwriting, not a real CAPTCHA collection. Neither is the ten-image official challenge.

| Reserved set | Model | Count | Accuracy | Correct with score ≥90% | NLL ↓ |
| --- | --- | ---: | ---: | ---: | ---: |
| mnist | MNIST only | 10,000 | 99.280% | 97.800% | 0.02178 |
| mnist | MNIST + supplementary | 10,000 | 99.310% | 98.070% | 0.01800 |
| emnist | MNIST only | 40,000 | 99.292% | 97.873% | 0.02292 |
| emnist | MNIST + supplementary | 40,000 | 99.405% | 98.323% | 0.01908 |
| synthetic | MNIST only | 2,400 | 72.083% | 46.792% | 0.83661 |
| synthetic | MNIST + supplementary | 2,400 | 88.042% | 64.375% | 0.36316 |

This is an optional model comparison, not a claim that the earlier confidence target has been met. The extension remains selectable even if some measurements regress; its results never overwrite the course model's results. The original default residual model's 99.10% MNIST result is historical and was not remeasured in this comparison.

## Executed validation

- [Unit checks](selectable-models-unit-tests.json): **50 passed**.
- [Browser checks](selectable-models-browser-qa.json): actual three-model selection, logits/activation parity, 30 image uploads with Python preprocessing/score parity, mixed-model exports, historical-card restoration, Letters/Words switching, pretrained-reader separation, failed-load recovery, selected-model drawing, and desktop/mobile selector checks.
- [Integrity audit](selectable-models-validation.json): original model identities, frozen selection, dataset split, source/font hashes and exported weights passed. Exact duplicate checks do not establish writer or near-duplicate independence.

| Model | Desktop median | Desktop p95 |
| --- | ---: | ---: |
| MNIST only | 5.4 ms | 6.5 ms |
| Supplementary | 6.6 ms | 8.0 ms |
| Preserved residual | 34.2 ms | 44.2 ms |

[Desktop screenshot](screenshots/selectable-models-desktop.png) · [Mobile screenshot](screenshots/selectable-models-mobile.png). Figures and binaries remain ignored local artifacts.

No official challenge inference, score rescaling, public deployment, fresh Windows run, hosted CI or teacher approval is claimed. Use MNIST-only evidence for the required exercise and identify supplementary results as an optional extension. Scores remain uncalibrated model outputs; test pixels were fingerprinted solely for data hygiene before training. No test labels or metrics chose the model, and no official challenge input or generator was used.
