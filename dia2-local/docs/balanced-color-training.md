# Balanced legacy/color training experiment

Freeze this protocol and sources before preparation. This separate extension keeps
the MNIST-only model, all existing extensions, active app and historical reports
unchanged. Official CAPTCHA images, labels, generator and previous predictions
are excluded from preparation, visual sample selection, training and selection.

One 64px residual CNN starts from verified preserved `captcha-v3` weights and uses
RGB foreground extraction. Compare the resulting weights with both grayscale and
RGB preprocessing on identical development images. This is one training run with
two inference contracts, not two matched training arms. Also measure the frozen
baseline under both contracts to separate preprocessing from training effects.

Seed 2026102401, four epochs, CPU four threads, batch 128, ordinary cross entropy,
AdamW learning rate 0.0001, weight decay 0.0001, cosine decay to 0.00001, dropout
0.15, EMA 0.99. No temperature scaling, score sharpening or displayed-score changes.
Each epoch uses 18,000 cached synthetic examples (6,000 legacy, 6,000 strong
grayscale-contrast colored, 6,000 near-equal-luminance colored) and 6,000 clean
MNIST training examples, with fresh mild affine/noise augmentation. All synthetic
groups balance ten classes and printed/handwritten sources. Legacy replay uses
the existing residual renderer's mixture of corruption families. Colors are
sampled independently of model predictions; equal-luminance palettes solve the
fixed grayscale equation with RGB RMS separation >=80. No rejection is silently
dropped from evaluation. Grayscale rejections are incorrect with score zero and
uniform penalties only for NLL/Brier, as in the completed color study.

Use canonical MNIST 55,000/5,000 source indices, excluding exact training pixels
matching validation. No EMNIST is added in this run. All augmented views remain in
their source split. Train fonts are pinned Noto/RobotoSlab/Oswald; development
uses Lato; test uses Ubuntu. Record hashes, seeds, split indices and every source
record. Model/font/dataset families have historical exposure; no writer-disjoint,
near-duplicate or blind real-world population claim is made.

Before training, produce a fixed sample of all ten classes, both sources and all
three groups. The coding agent inspects its raw/prepared contact sheet and records
ambiguities without claiming independent human review. Do not select samples from
errors or read official inputs for this review. Training requires that record.

Development: 1,800 newly rendered balanced raw images, 2,400 separately seeded
legacy-bridge images and 5,000 clean MNIST validation images. The production
preprocessing source and pretrained initialization remain unchanged.

Keep the existing thresholds: raw, legacy-subset, bridge and clean accuracy losses
each <=0.1 percentage points; strict correct-and-score->90% raw count gain
>=ceil(0.5% of raw count); lower raw NLL; Brier increase <=0.001; ECE increase
<=0.005; no increase in confidently wrong raw predictions or rejection counts.
A candidate must pass these same thresholds against BOTH baseline contracts.
Among eligible epoch/contract pairs, select minimum raw development NLL; ties use
the earlier epoch, then grayscale. Save every score vector and rejected result.
Never change thresholds or select another checkpoint using reserved/official data.

If nothing qualifies after all four epochs, retain baseline and do not open tests
or official cases. Otherwise freeze checkpoint, preprocessing and development
report, verify isolated browser uploads, activations, mode switching and p95
<150 ms, and only then open the canonical MNIST test partition. Verify exact-pixel
separation from all train/validation source pixels before generating 1,800 fresh
raw samples and 2,400 fresh bridge samples with a new seed and Ubuntu fonts.
Compare the frozen candidate and both baseline contracts on the same samples,
plus all 10,000 clean test digits; reapply all gates without reselection.

Only a passing independent result permits a frozen official follow-up: browser
predictions first, separate label comparison second, exactly 10/10 correct with
every original score strictly >90%. No automatic active-model replacement,
deployment, commit, push or CUDA setup is part of the experiment.

Run from `dia2-local/` using the [portable interpreter](../../PORTABILITY.md):

```text
<python> -m digitlab.balanced_color --stage prepare
<python> -m digitlab.balanced_color_report --stage figures
# Inspect contact sheet and write the actual visual-review record before training.
<python> -m digitlab.balanced_color --stage train
```

Later gated collectors and reporting are separate helpers; they cannot change
this frozen training source or selection policy. Completed destinations cannot
be overwritten. Synthetic results never substitute for official acceptance.
