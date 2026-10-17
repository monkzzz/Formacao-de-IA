# Official CAPTCHA follow-up: selectable CNNs

User-requested frozen official follow-up after prior exposure; descriptive comparison only, never training, tuning or model selection.

Models/runtime were frozen together before uploading the ten official inputs. Raw predictions were saved before reference labels were opened for comparison. No weights, preprocessing, default selection or displayed scores were changed.

| Model | Correct / 10 | Correct with score ≥90% / 10 | All-ten confidence target |
| --- | ---: | ---: | --- |
| mnist | 2 | 0 | False |
| mnist-supplementary-v1 | 5 | 1 | False |
| captcha-v3 | 10 | 6 | False |

Each cell below shows predicted digit, top score, and whether the digit was correct. A confident error remains an error.

| File | Expected | MNIST only | Supplementary | Preserved residual |
| --- | ---: | --- | --- | --- |
| caso_01.png | 8 | 0 · 74.78% · wrong | 0 · 79.11% · wrong | 8 · 99.26% · correct |
| caso_02.png | 3 | 3 · 42.34% · correct | 3 · 57.47% · correct | 3 · 95.31% · correct |
| caso_03.png | 0 | 0 · 50.48% · correct | 0 · 95.43% · correct | 0 · 99.76% · correct |
| caso_04.png | 6 | 8 · 37.84% · wrong | 6 · 59.56% · correct | 6 · 72.22% · correct |
| caso_05.png | 1 | 3 · 77.90% · wrong | 3 · 89.74% · wrong | 1 · 58.14% · correct |
| caso_06.png | 9 | 8 · 78.05% · wrong | 9 · 68.74% · correct | 9 · 99.76% · correct |
| caso_07.png | 4 | 6 · 27.89% · wrong | 8 · 37.53% · wrong | 4 · 76.93% · correct |
| caso_08.png | 2 | 3 · 59.33% · wrong | 3 · 48.70% · wrong | 2 · 95.37% · correct |
| caso_09.png | 7 | 3 · 31.98% · wrong | 7 · 74.13% · correct | 7 · 98.50% · correct |
| caso_10.png | 5 | 8 · 60.55% · wrong | 3 · 47.50% · wrong | 5 · 55.56% · correct |

[Frozen identities](selectable-models-challenge-followup-v1-freeze.json) · [Raw browser outputs](selectable-models-challenge-followup-v1-raw.json) · [Separate comparison](selectable-models-challenge-followup-v1-comparison.json).

PASS describes successful recording/integrity checks, not a perfect classification result. Prior official outcomes were already known, so this is not a fresh blind test or a general CAPTCHA accuracy estimate. Scores are uncalibrated softmax outputs. The optional extension remains distinct from the required MNIST-only exercise. Historical reports, model weights and public deployment remain unchanged. Do not use this follow-up to tune another checkpoint.
