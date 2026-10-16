# Frozen experiment design

## Scope and user requirements

Build and evaluate everything locally, in English, with an emphasis on measured accuracy. The personal project is isolated from the course materials. Publication and teacher review are outside this local run.

## Decisions made before challenge inspection

- Use a small convolutional network rather than the reference application's small MLP: spatial filters offer a useful inductive bias for image recognition.
- Architecture: padded 3×3 Conv(1→16), ReLU, 2×2 max pool; padded 3×3 Conv(16→32), ReLU, 2×2 max pool; flatten 1568; Linear(1568→128), ReLU, dropout .25 during training; Linear(128→10).
- Use all 60,000 official training examples, reserving a stratified 500 per class for validation. The remaining 55,000 examples update weights. Seed: 20261016.
- Apply one shared preprocessing contract to MNIST and uploaded/drawn inputs. Use border grayscale background estimation, contrast normalization, a fixed foreground threshold, bilinear resizing to a 20-pixel box, and center-of-mass placement in 28×28. No image-specific rules or filename lookups.
- Train for 18 epochs, batch size 256, AdamW at .001 with weight decay .0001 and cosine decay to .00005. Select the checkpoint by minimum validation cross-entropy, not official test accuracy.
- Use training-only modest affine transforms and Gaussian noise. Parameters are recorded in `reports/training.json`. Do not derive augmentation or cleanup settings from challenge pixels.
- Evaluate the selected checkpoint on the 10,000 official MNIST test examples only after model selection is finished. Accuracy is an observation, not a guaranteed outcome.
- Export little-endian float32 weights and a manifest with dimensions and SHA-256. Validate origin/browser logits and intermediate activations within absolute tolerance .0001, and preprocessing pixels within .000001.
- Freeze application source and weights before uploading the official challenge PNGs. Preserve raw predictions before reading the generator or labels.

## Local task sequence

| Task | Acceptance evidence |
| --- | --- |
| Validate MNIST and split | Canonical checksums, header checks, disjoint/reproducible split test |
| Implement and train network | Gradient/learning tests, training history, selected checkpoint |
| Evaluate and export | Test metrics, confusion matrix, weight hash, runtime fixtures |
| Implement local app | Drawing, multi-upload, scores, prepared input, real activations/contributions |
| Verify browser behavior | Preprocessing/model parity, upload checks, error cases, raw export, mobile layout |
| Freeze and run challenge | Source/model hashes, original ten raw predictions from the upload interface |
| Compare labels and explain limits | Separate comparison record without overwriting raw predictions |

These are local tasks rather than published GitHub Issues, in accordance with the user's local-only request.

## References and implementation provenance

Course materials: Vinicius Canonici and Hugo Gomes, [repository license](../../LICENSE.md). MNIST: Yann LeCun, Corinna Cortes and collaborators; original compressed IDX files are read from the course dataset without modification.

The [reference application](https://github.com/vcanonici/Image-classifier-demo) was reviewed for its separation of training, browser inference, parity fixtures, and activation displays. This project uses an independently written CNN and buildless interface; no reference model weights or implementation were copied.

Affine augmentation follows the documented PyTorch [`affine_grid` / `grid_sample` contract](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.grid_sample.html), with `align_corners=False`. Reproducibility is scoped to the recorded environment; floating-point results can vary across library versions and hardware.
