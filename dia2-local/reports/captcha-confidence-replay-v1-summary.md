# Confidence replay: completed experiment

**Baseline retained: no eligible epoch.** All four predeclared epochs completed. No gate was relaxed and no score rescaling occurred.

| Development measure | Baseline | Final EMA epoch |
| --- | ---: | ---: |
| Raw accuracy | 99.125% | 99.167% |
| Correct with score strictly >90% | 97.625% | 97.583% |
| Clean MNIST accuracy | 99.300% | 99.320% |
| Legacy bridge accuracy | 98.750% | 98.792% |
| Raw NLL | 0.031065 | 0.030071 |

The highest strict confidence coverage among all epochs was 97.708%; the fixed requirement was at least 98.125%. The required 0.5 percentage point gain was not reached.

The actual reserved-test command refused the rejected selection before loading test samples. Reserved evaluation, candidate export/browser checks, official CAPTCHA inference and deployment are NOT RUN. The original MNIST-only model and every deployed model remain preserved.

Fresh seeds and train/development font/source splits were used. These are synthetic development results, not real CAPTCHA population accuracy or a fresh blind challenge test.

[Predeclared protocol](../docs/confidence-replay.md) · [Full history and hashes](captcha-confidence-replay-v1.json).
