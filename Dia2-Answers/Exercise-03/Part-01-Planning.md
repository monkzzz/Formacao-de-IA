# Exercise 3, Part 1 — Planning and GitHub Issues

Original: [Part 1](../../Dia2/Exercicio-03/Parte-01-Planejamento-da-Rede.md).

## Data and evaluation

MNIST contains 60,000 training images and 10,000 official test images. Each image has 28 × 28 grayscale pixels and one label from 0 to 9. IDX headers describe the data type and dimensions; verify magic numbers, counts, payload sizes, and image-label alignment.

A proposed reproducible split is 55,000 training and 5,000 validation examples from the training partition, using a recorded seed. Use training data to update weights and validation data to select checkpoints and hyperparameters. Reserve the official test partition for final evaluation after selection. Keep all ten CAPTCHA images outside every tuning decision.

The network should receive normalized pixel values and return ten class scores. Drawings and uploads can differ from MNIST in scale, contrast, placement, background, and noise; define and test preprocessing explicitly.

## Architecture alternatives

| Option | Benefit | Tradeoff |
| --- | --- | --- |
| Small multilayer perceptron | Straightforward export and activation visualization | Does not explicitly exploit spatial structure |
| Small convolutional network | Models local image patterns | More involved browser implementation and visualization |

A possible baseline is an MLP with 784 inputs, 128 ReLU hidden units, and 10 outputs, trained with cross-entropy. This is a proposal requiring approval, not a course-mandated architecture. Training budget, export format, and acceptance targets must be agreed before implementation.

## Training and browser contracts

Record the split, seed, preprocessing, architecture, optimizer, learning rate, batch size, epoch limit, and checkpoint rule. Use validation loss to detect deterioration while training loss improves. Report accuracy and a confusion matrix; inspect error examples rather than relying on accuracy alone.

Export architecture metadata and the actual trained parameters. The website must apply the same input contract. Compare both implementations on identical prepared tensors and document numerical tolerances before accepting parity.

## Proposed GitHub Issue sequence

1. **Prepare MNIST:** validate IDX files and create a reproducible, disjoint split.
2. **Implement approved model:** verify dimensions, finite outputs, loss, and gradients.
3. **Train and evaluate:** preserve configuration, logs, selected weights, test metrics, and confusion matrix.
4. **Export and verify parity:** document parameter layout and compare origin/browser outputs.
5. **Build interactions:** drawing, clear, multiple-image upload, previews, and per-image scores.
6. **Visualize the actual network:** show real inputs, activations, and selected connections.
7. **Publish to GitHub Pages:** verify public assets and browser-only inference.
8. **Run the frozen challenge:** preserve ten raw predictions before label comparison.

Each Issue needs context, scope, dependencies, deliverables, acceptance criteria, and verification steps. Training depends on data/model work; website integration depends on export; challenge evaluation depends on the verified published application.

**Practical work remaining:** approve the specification, publish actual Issues in the personal repository, record their URLs, and verify that a fresh session can locate the next task. Drafts alone do not satisfy this gate.
