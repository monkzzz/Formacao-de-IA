# Desafio — Official CAPTCHA Challenge

Source: [challenge instructions](../../Dia2/Desafio/README.md).

## Objective

Use a neural network trained on MNIST to classify the ten official PNGs through the upload feature of a published browser application. Record the actual predictions and investigate limitations. The task is not to identify the digits manually or obtain answers from the generator.

## Inputs and prerequisites

- Inputs: `caso_01.png` through `caso_10.png` in `Dia2/Desafio/`, each 192 × 192 pixels.
- A genuinely trained MNIST model, selected using separate validation data.
- A browser application using those weights, supporting image upload and per-image scores.
- A working public GitHub Pages URL.
- Recorded model identity, weight hash, preprocessing configuration, and application commit before inspecting challenge images.

The challenge inputs must never be used for training, validation, architecture selection, or preprocessing tuning. Do not inspect the generator's labels before preserving the predictions.

## Execution

1. Freeze and record the application/model version.
2. Open the public application and verify that classification runs locally in the browser.
3. Upload the ten official PNGs, individually or together.
4. Save each prediction, all ten class scores, and a screenshot or exported interface record.
5. Preserve that raw record before consulting the answer key.
6. Compare labels in a separate step, preferably with the teacher.
7. Report the number correct out of ten, independently from official MNIST test accuracy.

## Answers to the analysis questions

**Why can an MNIST model fail here?** The challenge adds crossing lines, occlusion, broken strokes, deformation, and noise. Its image distribution differs from the clean, centered digits typically seen during MNIST training.

**Can preprocessing cause errors?** Yes. Background estimation, polarity, cropping, resizing, and centering can suppress useful strokes or emphasize unrelated fragments. Inspect the exact prepared input and compare implementations before attributing every error to the network.

**How do we establish that predictions are real?** Trace the deployed model to the recorded weights, verify origin/browser parity on the same tensors, and confirm that only image pixels enter inference. Filenames, labels, and generator internals must not influence predictions.

**Does a low challenge score invalidate the project?** No. Report the observed result honestly and investigate errors. Ten cases provide a limited robustness check, not a general accuracy estimate.

**Can the system be improved afterward?** Yes, but preserve the initial version and predictions. Any evaluation after inspecting challenge outcomes is a later iteration, not another independent first test.

## Current status

The local implementation is now in [dia2-local](../../dia2-local/README.md). A CNN was trained from scratch and evaluated through the actual browser upload interface:

- Official MNIST test: **9,928/10,000 correct (99.28%)**.
- Official Desafio images: **2/10 correct (20%)**.
- Browser/Python preprocessing and inference checks passed. Raw predictions were preserved before label inspection.
- The model and preprocessing remain unchanged after challenge evaluation. A collector-only blob-preview assertion repair is documented separately.

See the [validation report](../../dia2-local/reports/validation.md) for the actual ten predictions, source/model identity, figures, error analysis, and evidence. Everything was evaluated locally; public deployment and teacher review have not occurred.
