# Exercise 3, Part 2 — Training and Evaluation

Original: [Part 2](../../Dia2/Exercicio-03/Parte-02-Coding-com-o-Agente.md).

## How should implementation proceed?

Work through approved Issues using Plan → Execute → Verify → Review → Commit. Inspect project context and existing changes before each task. Keep data loading, preprocessing, model definition, training, evaluation, and export responsibilities identifiable.

## How can correct data loading be demonstrated?

Check IDX headers, counts, pixel dimensions, label range, and matching image/label counts. Inspect sample images alongside their labels. Record split indices or a deterministic split procedure. Ensure training and validation indices do not overlap and never draw either from the official test partition.

## How can model behavior be tested?

Verify batch input/output shapes and finite values. Check that probabilities sum approximately to one when softmax is applied. Test gradients or use a small overfitting experiment on training-only examples to detect a broken learning pipeline. Use deterministic fixtures for export tests.

## What proves that training actually happened?

Preserve the training command, environment versions, seed, configuration, per-epoch losses and validation metrics, selected checkpoint, and weight hash. A screenshot or unsupported accuracy claim is insufficient. Select the checkpoint using validation evidence, not the official test set or CAPTCHA results.

Keep logs even when training fails; explain the cause and the next experiment. Record which sources of nondeterminism remain rather than promising identical results on every machine.

## What should final evaluation contain?

After model selection is fixed, evaluate on the 10,000 official MNIST test examples. Report sample count, loss, accuracy, a confusion matrix, and representative mistakes. Preserve the evaluation command and the exact weights used.

Compare exported inference against the original model on identical tensors. Check parameter dimensions and orientation, activation functions, normalization, class order, and a documented numerical tolerance. Test preprocessing independently so matching predictions do not hide inconsistent inputs.

## Required evidence

| Artifact | Purpose |
| --- | --- |
| Training/evaluation code and commands | Reproduce the experiment |
| Configuration and dependency versions | Identify the environment and choices |
| Training log and validation curves | Show learning and checkpoint selection |
| Trained weights and hash | Identify parameters used by the website |
| Test metrics and confusion matrix | Describe held-out performance |
| Model/export tests | Verify contracts and runtime consistency |
| Issue references and commits | Trace implementation to approved tasks |

Store large weights outside ordinary Git history as required by the repository policy; document their retrieval and integrity checks so the published application can obtain its deployment assets.

## Actual local results

The subsequent [local implementation](../../dia2-local/README.md) trained a Conv16 → Conv32 → Dense128 → 10 network for 18 epochs, selecting epoch 18 by validation loss. It correctly classified **9,928 of 10,000 official test images (99.28%)**.

Weight SHA-256: `8e9021e5ba3cb33a66e3dc8b8580a7388802a6938dd78162ebcee4c396e84338`.

See the [training history](../../dia2-local/reports/training.json), [test metrics](../../dia2-local/reports/mnist-test.json), and [validation report](../../dia2-local/reports/validation.md) for measured evidence. Six Python tests and nine browser QA groups passed. The separate Desafio evaluation scored 2/10; it must not be represented by the MNIST result.
