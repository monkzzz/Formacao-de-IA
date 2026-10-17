# Exercise 3, Part 4 — CAPTCHA Evaluation

Original: [Part 4](../../Dia2/Exercicio-03/Parte-04-Teste-do-Desafio.md).

## What is being evaluated?

The official challenge consists of `caso_01.png` through `caso_10.png` in `Dia2/Desafio/`. These ten external images evaluate the entire published pipeline, including uploads, preprocessing, and inference. Their result is separate from accuracy on the 10,000 MNIST test images. A perfect CAPTCHA score is not required.

## What is the correct procedure?

1. Freeze the model, preprocessing, and application before testing. Record commit, model hash, and public URL.
2. Open the published website and confirm browser-only inference.
3. Upload all ten official PNGs using the application's upload feature.
4. Save each filename, raw prediction, all ten scores, and interface evidence before consulting labels.
5. Preserve the raw record, then compare it with the answer key in a separate step, preferably with the teacher.
6. Count correct and incorrect predictions and document observations and hypotheses.
7. If changes follow label inspection, retain the initial results and report subsequent evaluations as new iterations.

Neither training nor preprocessing selection may use the challenge images. Filename order, labels, and generator internals must not feed the prediction process.

## Prediction record

| File | Predicted class | Ten scores / evidence | Label after recording | Correct? |
| --- | --- | --- | --- | --- |
| caso_01.png | 0 | Raw record below | 8 | No |
| caso_02.png | 3 | Raw record below | 3 | Yes |
| caso_03.png | 0 | Raw record below | 0 | Yes |
| caso_04.png | 8 | Raw record below | 6 | No |
| caso_05.png | 3 | Raw record below | 1 | No |
| caso_06.png | 8 | Raw record below | 9 | No |
| caso_07.png | 6 | Raw record below | 4 | No |
| caso_08.png | 3 | Raw record below | 2 | No |
| caso_09.png | 3 | Raw record below | 7 | No |
| caso_10.png | 8 | Raw record below | 5 | No |

The [raw prediction record](../../dia2-local/reports/challenge-raw.json) contains all ten scores and the prepared pixels for every image. It was saved before labels were consulted. The [separate comparison](../../dia2-local/reports/challenge-comparison.json) verifies all ten inputs and predictions against Python.

## How should errors be interpreted?

Crossing lines, broken strokes, clutter, and unusual backgrounds can differ substantially from training data. Inspect the prepared input to distinguish a preprocessing defect from a classification failure. Compare origin/browser inference on the same tensor to investigate integration errors. Treat proposed causes as hypotheses until tested.

## Verification matrix

The matrix below records the original local baseline. As of 2026-10-17,
[real Issues](../../participant-work/day2/issue-register.md) and
[existing-host browser verification](../../participant-work/day2/submission-browser-delivery.md)
have separate evidence. Pages and instructor acceptance remain pending. The
[selected CNN chain](../../participant-work/day2/submission-challenge-chain.md)
preserves all later results as follow-ups, without replacing this first score.

| Check | Status |
| --- | --- |
| Real training and official MNIST evaluation | PASS — 99.28% |
| Origin/browser parity | PASS |
| Drawing and classification | PASS |
| Ten uploads and individual results | PASS |
| Browser-only inference | PASS |
| Real network visualization | PASS |
| Public GitHub Pages URL | NOT RUN — local-only request |
| Predictions recorded before labels | PASS |
| Version and weights | PASS — frozen source and model hashes |
| Published GitHub Issues | NOT RUN — local task plan used |

**Measured first score: 2/10 (20%)**, with eight errors. A collector-only repair allowed local blob preview URLs; the retry retained the original frozen model, preprocessing, and application. No challenge-dependent tuning followed. See the [complete validation report](../../dia2-local/reports/validation.md) for the evaluation boundary, figures, and limitations.
