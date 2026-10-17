# Diagnostic, consistency and capacity suite

Prepared before results on 2026-10-17 after three confidence experiments failed
their development gates. Implement all requested steps without using the official
ten cases for diagnosis, preprocessing decisions, training or selection. This is
independent synthetic evidence, not newly collected real-world CAPTCHA data.

## Relationship to the exercise rules

The [exercise specification](../../Dia2/Exercicio-03-Desenvolvimento-Issues.md)
requires MNIST for training and evaluation. An external CAPTCHA database must
not replace that required experiment. The written rules do not explicitly
address supplementary datasets; treating them as an optional extension is an
interpretation, not recorded teacher approval. Keep any such extension and its
data provenance/results separate from the required MNIST evidence.

This suite uses MNIST and independently rendered examples, without downloading
an external CAPTCHA database. The official ten images, their derivatives,
labels and generator are excluded from training and model selection. A higher
score on synthetic images does not establish improvement on real CAPTCHA data.

## Fixed data and diagnostic protocol

Use the existing verified MNIST archives and stratified 55,000/5,000 split. Split
the 5,000 validation indices by class into 2,500 raw-diagnostic and 2,500 raw-selection
sources. These raw-source sets are disjoint; the historical clean-accuracy guard
still uses the full 5,000 clean validation images, so the separation is not claimed
for every validation metric. Fonts come from the portable pinned bundle: train on NotoSans, NotoSerif,
RobotoSlab and Oswald; use Lato for diagnostic/development; reserve Ubuntu for
final synthetic testing. The baseline has prior evaluations and may have seen some
font families; no fresh blind-population claim is made.

Build a new renderer with six balanced conditions: clean, background gradients
and particles, crossing lines, blur/JPEG, short stroke gaps, and mixed corruption.
Every digit/source/condition cell has equal count. No rotations that exchange
digit classes, flips or whole-stroke erasures. Short gaps are bounded to at most
8% of annotated glyph pixels. Labels come from the printed digit or supplied
MNIST source label; they are not human readability annotations.

Each source supplies a clean image, two independently corrupted views, and a
known foreground mask. Use 1,200 diagnostic, 3,600 development and 6,000 synthetic
training sources, plus 4,000 balanced clean training examples. Cache all views
with hashes. Test samples remain undecoded until a frozen eligible choice passes
browser checks. Archive checksum verification alone does not consume test samples.

Diagnose the preserved model before training: compare noisy production inputs
with clean-source inputs; report condition-specific accuracy, confidence, proper
scores, crop coverage, crop expansion, glyph size after resizing, and disagreements.
Generate a contact sheet of fixed printed/handwritten examples and their actual
64px inputs. A clean-source ablation is an oracle diagnostic, not an inference
algorithm that could recover a hidden clean image. Crop measurements distinguish
lost coverage from glyph shrinkage; correlations alone do not prove causality.
Keep production preprocessing unchanged in this suite rather than introducing an
unvalidated cleanup rule.

## Matched training arms

All three arms receive identical cached labelled views, common sample order,
four epochs, batch 64 sources/192 images, dropout 0.15, AdamW 0.00015 and cosine
decay to 0.00001, weight decay 0.0001, EMA 0.98, four CPU threads, seed 2026101901.
All begin with identical baseline functions; capacity blocks are identity-initialized.

1. **Control:** ordinary cross-entropy over all three views, current residual CNN.
2. **Consistency:** the same CE plus weight-3 Jensen–Shannon divergence among the
   three prediction distributions, current architecture.
3. **Capacity:** the same consistency objective, with one extra residual block at
   each spatial stage. Report actual parameter counts and measured browser speed.

The consistency idea is informed by the [AugMix authors’ implementation and
description](https://github.com/google-research/augmix). This is an independently
implemented paired-corruption/consistency study, not a reproduction of AugMix’s
mixing algorithm or reported ImageNet results. No external code or weights are copied.

Keep the prior gates unchanged on new raw development data: accuracy loss at most
0.1 percentage points; clean accuracy loss at most 0.1 points; correct-at-90 gain
at least 0.5 points; lower NLL; Brier increase at most 0.001 and binned ECE increase
at most 0.005. Add an independent 2,400-example legacy-renderer bridge set and
limit its accuracy loss to 0.1 points. Never lower gates after observing results.

Select the eligible epoch with minimum raw development NLL within each arm.
Prefer the best eligible smaller network unless the deeper choice gains at least
0.2 points raw accuracy, or reduces NLL by 2% without losing correct-at-90 coverage.
Save all epoch metrics and final rejected checkpoints. Record the selected model,
source, data, fonts and frozen development report before evaluating reserved data.

## Browser and final gates

Export only the development-selected candidate to an isolated preview; adapt its
copied runtime if extra blocks are needed. Verify preprocessing, logits, real
intermediate activations and uploads against Python. Require measured desktop
inference p95 below 150 ms before opening final data. Preserve active app assets.

Evaluate baseline and the frozen choice on the same fresh 6,000-image synthetic
test, 2,400-image legacy bridge and canonical MNIST test. Reapply the same gates,
record condition/class metrics and paired wins/losses, and preserve raw vectors.
Do not choose another arm or epoch after this test. Only a qualified candidate
may receive a single frozen official follow-up, explicitly labelled after prior
exposure, with raw predictions saved before separate label comparison. No outcome
from the ten may drive further changes. Public publication is outside this suite.

## Commands

On Windows or Linux follow [the runtime guide](../../PORTABILITY.md), then use the
printed Day 2 interpreter from `dia2-local/`. The diagnostic plot additionally
needs Matplotlib (`python -m pip install -r requirements-confidence.txt`).
Alternatively prepare it from the repository root using
`python setup_course.py --component day2 --install --confidence --fonts --browser`.

```text
<python> -m digitlab.confidence_suite_browser --stage self-test
<python> -m digitlab.confidence_suite_browser --stage baseline-self-test
<python> -m digitlab.confidence_suite --stage prepare
<python> -m digitlab.confidence_suite --stage train
<python> -m digitlab.confidence_suite_browser --stage export
<python> -m http.server 8881 --bind 127.0.0.1 --directory .tmp/captcha-consistency-suite-v1
<python> -m digitlab.confidence_suite_browser --stage qa
<python> -m digitlab.confidence_suite --stage test
```

If reserved gates pass, the final two stages are:

```text
<python> -m digitlab.confidence_suite_browser --stage official
<python> -m digitlab.confidence_suite_browser --stage compare
```

The comparator consults the preserved reference labels only after raw predictions
exist; it writes a separate comparison and distinguishes correct high-confidence
predictions from confident mistakes. For figures and a final audit summary:

```text
<python> -m digitlab.confidence_suite_report --stage figures
<python> -m digitlab.confidence_suite_report --stage summary
```

Each stage refuses overwriting completed work. The experiment cannot guarantee
90% on every official input; model scores remain uncalibrated unless independently
established otherwise. Source and binaries are kept separate; datasets, caches,
weights and screenshots remain ignored by Git.

## Actual outcome — 2026-10-17

All three arms completed four epochs. None qualified under the fixed gates;
the existing model and application remain unchanged. The highest correct-at-90
development coverage was 97.778%, against 97.611% for the baseline and the
required 98.111%. Every trained epoch also had worse raw NLL than the baseline.
The confidence target remains unmet.

The 1,200-example diagnosis measured 99.25% noisy accuracy versus 99.42% on
clean-source inputs. Crop expansion reduced glyph scale in many examples, but
these results do not establish a beneficial production preprocessing change.
They also do not explain individual official cases.

Validation: [47 automated tests passed](../reports/captcha-consistency-suite-v1-final-unit-tests.json),
both the [original](../reports/captcha-consistency-suite-v1-baseline-runtime-self-test.json)
and [deeper](../reports/captcha-consistency-suite-v1-runtime-self-test.json)
browser math checks passed, and the
[rejected-selection gates](../reports/captcha-consistency-suite-v1-gates.json)
blocked export and reserved evaluation. Candidate browser upload/speed testing,
reserved tests, official follow-up and publication were **NOT RUN**.

See the [measured summary](../reports/captcha-consistency-suite-v1-summary.md)
and [integrity audit](../reports/captcha-consistency-suite-v1-validation.json).
All 29 recorded baseline/application/prior-evidence identities were preserved;
source and dataset hashes also passed. Linux was executed; fresh Windows and
hosted CI execution remain **NOT RUN**.
