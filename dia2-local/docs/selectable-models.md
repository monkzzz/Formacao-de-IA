# Selectable training datasets

Current release: [3.12.0](release-3.12.0.md) retains MNIST-only digits, the
preserved residual digit CNN and EMNIST single letters. The supplementary digit
choice is archived. The sections below preserve their historical experiment and
package scope; GitHub Pages now serves the three-model numbers-v5 package.

Current project acceptance is now clarified by the participant: **10/10 correct
and every score strictly >90%**. Supplementary training is acceptable as a
separately documented extension. See [the professor criterion and next-study
boundary](professor-acceptance.md). Earlier approval/NOT RUN statements below
retain their dated historical scope.

The local v3.11.0 interface separates the required exercise from an optional
supplementary-data experiment. No public deployment is implied by local changes.

In **Digits → Digit model → Digit Lab CNN**, use **CNN training data**:

| Option | Training scope | Role |
| --- | --- | --- |
| MNIST only | Original MNIST network, with training-only affine/noise augmentation | Default for the required exercise |
| MNIST + supplementary data | Separate network initialized from the original MNIST-only weights, then trained on MNIST, EMNIST Digits and independently generated CAPTCHA-style examples | Optional extension; report separately |
| Preserved residual CNN | Previous `captcha-v3` default, trained on MNIST and synthetic CAPTCHA-style images | Historical model, unchanged weights |

The [exercise](../../Dia2/Exercicio-03-Desenvolvimento-Issues.md) requires MNIST.
Keep the MNIST-only model and its evidence as the course submission path. The
written exercise does not explicitly authorize supplementary datasets; this
extension is identified separately and is not represented as teacher approval.
All ten official challenge images and their derivatives, labels and generator
remain excluded from training, validation, architecture and hyperparameter
selection. This extension does not run a new official challenge evaluation.

## Data and fixed training protocol

Supplement: [NIST EMNIST Digits](https://www.nist.gov/itl/products-and-services/emnist-dataset),
240,000 training and 40,000 test images, ten digit classes. Credit: Cohen,
Afshar, Tapson and van Schaik (2017), *EMNIST: an extension of MNIST to handwritten
letters*. Reuse the locally cached official archive, verify its canonical MD5
`58c8d27c78d21e728a6bc7b3cc06412e`, extract Digits into a separate directory,
record SHA-256 hashes, and transpose the stored image axes to upright handwriting.
The existing Letters extraction is preserved.

EMNIST adds real handwriting, **not a collected CAPTCHA database**. The additional
12,000 CAPTCHA-style examples use the independent renderer and pinned open fonts.
Train fonts are NotoSans, NotoSerif, RobotoSlab and Oswald; development uses Lato;
reserved synthetic evaluation uses Ubuntu. Source labels are not human readability
judgements. Neither synthetic accuracy nor handwriting accuracy establishes
real-world CAPTCHA accuracy.

Keep the original MNIST 55,000/5,000 training/validation split. Remove exact
supplementary duplicates and any supplementary training image matching MNIST or
the EMNIST test partition, then reserve 500 examples per class for EMNIST validation.
Test pixels are fingerprinted before training solely for split hygiene; no test
labels or test metrics select the model. Exact pixel hashes cannot rule out
near-duplicates or shared writers; no writer-independent claim is made.

Freeze before results: seed 2026102001, four epochs, original 28px CNN initialized
from the MNIST-only model, ordinary cross-entropy, batch 256, four CPU threads,
AdamW 0.0002, weight decay 0.0001, cosine decay to 0.00002, existing training-only
augmentation. Select the minimum equally weighted mean validation NLL across
MNIST, EMNIST and independent synthetic examples. Freeze the selected checkpoint
before computing reserved metrics. No confidence gate is loosened: this is a
selectable experiment, not an accepted replacement for `captcha-v3` or a claim
that the earlier confidence target has been met.

Evaluate the original MNIST-only model and frozen extension on identical MNIST
test images, deduplicated EMNIST test images and 2,400 independent synthetic test
images. Report accuracy, correct-at-90 coverage, NLL, Brier score, ECE and confusion
matrices separately. Model scores remain uncalibrated softmax outputs.

## Reproduce and run

Use the [Windows/Linux runtime](../../PORTABILITY.md) from `dia2-local/`:

```text
<python> -m digitlab.emnist_data
<python> -m digitlab.supplementary
<python> -m digitlab.selectable_models_report --stage evaluations
<python> serve.py
```

The first command downloads/verifies the official archive when absent and prepares
Letters; the supplementary trainer verifies that archive again and extracts only
Digits into `data/emnist-digits/`. Training refuses to overwrite an existing run
or model export. A checkout containing this run's tracked manifest already has
an export directory: reproduce in an isolated working copy, first relocating
that copy's `dist/model/mnist-supplementary-v1/` outside `dist/model/`. Likewise
retain any existing experiment report/artifact directory outside its active path;
never delete the original working copy's evidence. Keep the original MNIST and
preserved residual model exports available because the runner verifies them.
Datasets, checkpoints and binary weights stay ignored by Git. The optional local
weights are not fetched from an older public release. No inference API is used.

With the server running, verify the interface and publish a local audit:

```text
<python> -m digitlab.selectable_models_report --stage unit-tests
<python> -m digitlab.selectable_models_qa --url http://127.0.0.1:8765/
<python> -m digitlab.selectable_models_report --stage summary
```

The unit-test stage writes `reports/selectable-models-unit-tests.json` with the
actual `unittest` run status and count. All collectors preserve existing reports.

Switching CNNs changes the actual verified weights, input size, feature maps,
displayed MNIST result, training scope and evaluation download. Each exported
prediction carries its own CNN identifier and model hash. Selecting a historical
upload restores its model. If a model fails to load, the previous working model
and selector are retained with an error message. Letters and Words remain separate.

## Actual local delivery

All four epochs completed; epoch 4 was frozen before reserved metrics. The
extension measured **99.31% MNIST**, **99.405% EMNIST Digits**, and **88.042% on
2,400 independent synthetic images**. On the identical inputs, the original
MNIST-only model measured 99.28%, 99.2925% and 72.083%, respectively. These results
do not establish performance on real CAPTCHA collections or the ten official cases.

All **50 unit tests** and actual three-model browser checks passed, including
30 uploads, real activations, model-aware exports, restoring historical cards,
Letters/Words switching, failed-load recovery, drawing and mobile layout.
The original MNIST-only and previous residual weight hashes are unchanged.
See the [results and evidence](../reports/selectable-models-summary.md).

The app is available locally with the three options. Public deployment, a new
official challenge run, fresh Windows execution, hosted CI and teacher approval
are **NOT RUN**. Historical public/submission records retain their original scope.

## Subsequent official follow-up — user requested

After the local delivery above, the participant explicitly requested official
CAPTCHA evaluation. A separate frozen browser run recorded all three models on
the ten inputs, then consulted the preserved reference labels only after all raw
outputs had been saved. No training, preprocessing, default-model or score changes
followed the results.

| Model | Correct / 10 | Correct with score ≥90% / 10 |
| --- | ---: | ---: |
| MNIST only | 2 | 0 |
| MNIST + supplementary | 5 | 1 |
| Preserved residual CNN | 10 | 6 |

None met the all-ten confidence target. These ten previously exposed cases do
not establish general CAPTCHA accuracy. See the [per-image results and raw
evidence](../reports/selectable-models-challenge-followup-v1-summary.md) and
[integrity checks](../reports/selectable-models-challenge-followup-v1-validation.json).
The initial delivery report remains preserved with its original NOT RUN scope.

The collector is `python -m digitlab.selectable_challenge --stage record`, followed
by `--stage compare`. Completed freezes and predictions cannot be overwritten.
A NumPy JSON serialization issue in the post-recording comparator was repaired;
[repair evidence](../reports/selectable-models-challenge-followup-v1-comparison-repair.json)
confirms unchanged raw predictions and frozen identities, and two passing
comparison regression checks. No inference was repeated for this repair.
