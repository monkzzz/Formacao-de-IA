# Fixed-weight color-aware preprocessing study

This protocol is fixed before running the comparison. Preserve the active app,
all model weights, historical evidence and completed test boundaries. No official
challenge images, labels, generator or prior predictions enter this study.

One candidate replaces grayscale border contrast with RGB root-mean-square
distance from the mean RGB border. Alpha is composited onto white first. Keep
the existing 0.12 contrast rejection, normalization, 0.06 suppression, 0.20 crop
threshold, bilinear resize and center of mass. No denoising, score scaling,
parameter search or training. The idea follows the
[reviewed RGB foreground approach](https://github.com/vcanonici/Image-classifier-demo/blob/99e4958/apps/web/src/preprocess.ts),
but uses our full-border estimate, thresholds and pixel-exact fitting contract.
The implementation is authored independently; it does not copy their code.

Fixed seed 2026102301; four CPU threads; preserved `captcha-v3` residual weights.
Use only the canonical 5,000-image MNIST validation source split, never its test
partition. Save source indices, dataset/font/source hashes and every raw fixture.
New renderings use the pinned Lato development fonts and existing broad renderer.
Previous model/font/source exposure means this is development evidence, not a
fresh blind population test. Generated labels do not establish human readability.

Compare both preparations on identical samples:

- 1,200 legacy-style images, balanced across digits and printed/handwritten sources.
- 600 colored images, balanced across digits, printed/handwritten sources and
  three fixed palettes: two near-equal-luminance palettes and one with a larger
  luminance difference. These deliberately test the hypothesized weakness; their
  frequency is not a claim about real CAPTCHA prevalence.
- All 5,000 clean MNIST validation images as a preservation guard.

For colored examples, reuse the rendered foreground intensity as an opacity mask
and map it into the fixed ink/background palette. This isolates color contrast;
it does not provide clean masks to the classifier. Both preparations receive only
the same final RGBA pixels. No sample is selected based on model errors.

Preparation rejection counts as incorrect, with prediction -1 and score 0.
For NLL/Brier only, use a uniform ten-class vector as a declared rejection penalty;
these vectors are placeholders, not emitted model predictions. Calculate ECE with
rejection correctness/score both zero. Save rejection masks and original scores
for successful inputs so the distinction remains reproducible.

Development eligibility requires no increase in rejection count; raw accuracy,
legacy accuracy and clean accuracy losses each <=0.1 percentage points; at least
ceil(0.5% × 1,800) additional correct raw predictions with unrounded score strictly
>90%; lower raw NLL; Brier increase <=0.001; ECE increase <=0.005; and no increase
in confidently wrong raw predictions. Check grayscale and color subsets separately.
These fixed gates do not establish the professor's official acceptance criterion.

Implement Python and JavaScript, test isoluminance, polarity, alpha, blank/low
contrast rejection and neutral grayscale equivalence, then verify real browser
uploads, prepared tensors, logits/feature maps and unchanged weights. Browser
parity is required even if the development candidate is rejected. Browser p95 must
remain below 150 ms for any future adoption. Never alter the active application
automatically. Reserved testing, official follow-up, deployment and CUDA setup are
NOT RUN in this development phase; a later phase needs its own frozen protocol.

From `dia2-local/`, using the [portable interpreter](../../PORTABILITY.md):

```text
<python> -m unittest tests.test_color_preprocess -v
<python> -m digitlab.color_study
<python> -m digitlab.color_preview
<python> -m digitlab.color_study --summary
```

Completed report destinations cannot be overwritten. Preserve unsuccessful results.
