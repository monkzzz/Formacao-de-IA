# Separate 64px CAPTCHA training extension

Protocol fixed before the run. Preserve the MNIST-only course model, previous
residual model, supplementary model, active application and earlier evidence.
The professor permits a separately documented supplementary extension and requires
10/10 official cases correct with every original score strictly >90%.

## Controlled scope

Initialize the existing 64px residual architecture from verified `captcha-v3`
weights. Keep production preprocessing unchanged to isolate training: no cleanup
or transformation alternatives are selected in this experiment. Never read the
official images, labels, generator or previous official predictions during data
preparation, training, selection, browser QA or reserved evaluation.

Seed 2026102201; four epochs; four CPU threads; batch 128; ordinary cross-entropy;
AdamW 0.00015, weight decay 0.0001, cosine decay to 0.00001; training dropout 0.15;
EMA decay 0.99. No temperature scaling, logit sharpening or display-score changes.
Select minimum raw validation NLL among eligible EMA epoch checkpoints. Preserve
all epoch metrics and the final rejected checkpoint if nothing qualifies.

## Data and readability limits

Each epoch uses 32,400 cached raw examples, balanced over ten digits, three sources
(printed, MNIST, EMNIST Digits), six conditions (clean, crossing lines, speckles,
short gaps, blur/JPEG, mixed), and three severity levels: 540 cells ×60 images.
Add 10,800 balanced clean MNIST training examples and 5,400 balanced clean EMNIST
training examples: 48,600 images per epoch, with fresh mild affine/noise variation.

The new independent renderer varies font axes where supported, glyph aspect ratio,
shear, size, rotation, polarity, ink/background colors, line placement and opacity,
speckles, bounded short gaps and blur/JPEG. No flips or quarter-turn rotations.
Short gaps remove at most 8% of annotated glyph ink; geometry and contrast checks
prevent blank/cropped-away labels. These checks do not prove human readability.

Use canonical MNIST train/validation indices, excluding exact duplicate training
pixels across the validation boundary. Deduplicate EMNIST training pixels and
exclude MNIST source pixels before a stratified 5,000-source development split.
Training sources and development sources are disjoint. Only source images assigned
to training supply training views; all augmentations stay in their source split.
No writer-disjoint or near-duplicate independence claim is made.

Pinned train fonts: NotoSans, NotoSerif, RobotoSlab, Oswald, with available italic
faces and varied axes. Development: Lato. Reserved synthetic test: Ubuntu. Current
font groups are disjoint, but baseline/font families have historical exposure.

Generate 5,400 balanced raw development examples (540 cells ×10), a separately
seeded 2,400-image legacy-renderer bridge and clean validation guards of 5,000
MNIST and 5,000 EMNIST images. Save hashes, source records, per-condition metrics,
raw scores and a fixed contact sheet across sources/conditions/severities. The
coding agent performs a visual spot-check; independent human review stays NOT RUN
unless actually supplied. This is synthetic CAPTCHA-style data plus labelled
handwriting, not a collected real CAPTCHA population. Do not claim otherwise.

## Gates and frozen evaluation

Require raw accuracy loss <=0.1 percentage points, both clean accuracy losses
<=0.1 points, legacy bridge accuracy loss <=0.1 points, correct-and-score-strictly
>90% raw coverage gain >=0.5 points, lower raw NLL, Brier increase <=0.001 and ECE
increase <=0.005. Do not increase the raw count of confidently wrong predictions
above 90%. Compare integer coverage gains to the ceiling of 0.5% of the sample
count. These development gates never substitute for official acceptance.

Freeze the selected checkpoint, sources and development report before exporting
an isolated browser preview. Verify weights, preprocessing, logits, intermediate
activations and uploads; require desktop inference p95 <150 ms. Only then decode
reserved MNIST/EMNIST partitions and generate 5,400 new Ubuntu-font synthetic test
examples and a new legacy bridge. Verify exact-pixel separation from training and
development, report any contamination honestly, and do not choose another model
after test metrics. Reapply the same gates to the frozen candidate against the
preserved baseline. Report MNIST, EMNIST, synthetic/condition/class results and
paired changes separately. Historical test exposure means this is not a fresh
blind real-world benchmark.

Only if the frozen candidate passes independent gates may it receive one further
official follow-up: freeze runtime, save all ten raw browser outputs before a
separate label comparison, use the strict professor criterion, retain failures,
and never select another checkpoint from that result. No automatic publication
or active-model replacement occurs. If no epoch qualifies, stop at development
and preserve reserved data and official test boundaries.

## Commands

From `dia2-local/` with [the portable runtime](../../PORTABILITY.md):

```text
<python> -m digitlab.captcha_extension --stage prepare
<python> -m digitlab.captcha_extension --stage train
```

Every completed destination is protected against overwriting. Later gated stages
are added to this separately named workflow without changing the frozen training
source files or relaxing its policy.
