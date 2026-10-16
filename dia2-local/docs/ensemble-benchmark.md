# Independent benchmark and frozen-model ensemble experiment

This experiment compares the existing 28px and 64px digit models without
retraining either one. The ten official challenge images, their generator and
their outcomes are excluded from benchmark construction and parameter selection.
The v3.6.0 model remains the deployment baseline.

## Protocol fixed before development results

- Create **10,000 development** and **20,000 test** images using a new independent
  renderer, not either previous training renderer. Use nonsquare canvases,
  color gradients, wavy interference, short stroke cuts and speckles.
- Half the images are printed digits and half are MNIST handwriting. Include
  three severity levels. Report results separately by source and severity.
- Development fonts: Agency, Bookman Old Style, Century Gothic, Franklin Gothic
  Book, Maiandra and DejaVu Sans. Test fonts: Bodoni, Century, Garamond, Rockwell,
  Bahnschrift and Liberation Sans. These families are separate from each other
  and from the previous training and validation fonts. Fonts are not redistributed.
- Development handwriting uses the historical 5,000-image MNIST validation
  source split. Test handwriting uses the official 10,000-image test partition.
  These sources have been evaluated previously; the rendered images and font
  families are new. This is a synthetic benchmark, not newly collected real-world
  CAPTCHA data or a fresh blind evaluation of MNIST itself.
- Fix renderer seeds 20261111 and 20261112. Store model identities, generator
  and font hashes, environment, labels and component scores in ignored artifacts.
  Preserve old reports, weights and benchmark data.
- Compare the 64px baseline, the 28px model and weighted score averages using
  high-resolution weights **0, 0.25, 0.5, 0.75, 0.9 and 1**. Scores are not
  calibrated probabilities. Never choose the model from the correct label of
  an individual uploaded image.
- On development data, maximize noisy accuracy subject to clean MNIST validation
  accuracy within **0.1 percentage points** of the 64px baseline. Break ties by
  noisy cross-entropy, then favor the 64px baseline. Require at least **0.15
  percentage points** of development improvement to select a replacement.
- Verify the selected pipeline's desktop browser p95 inference below **150ms**
  before opening the benchmark test split. Freeze the weight; evaluate it once
  on the untouched synthetic test split, with both component baselines reported.
- Report complementary errors, ensemble fixes and regressions. Do not change the
  selected weight based on test outcomes. An unsuccessful candidate remains
  recorded, and does not justify tuning against the ten official challenge cases.

## Reproduce

From `dia2-local/`, with both frozen checkpoints, weight exports and fonts present:

```powershell
.\.venv\Scripts\python.exe -m digitlab.ensemble_benchmark --stage development
# Run the browser speed verification and freeze selection before test scoring.
.\.venv\Scripts\python.exe -m digitlab.ensemble_benchmark --stage test
```

Both stages refuse existing report/cache destinations. Test scoring requires a
matching successful browser-speed report first. This experiment creates no new
trained weights. Test results cannot be used to try another mixing weight.

The browser step is `python -m digitlab.ensemble_speed_qa` with the local server
running on port 8769. It saves the deployment decision and the best development
ensemble as separate frozen choices before test scoring. The deployment choice
may remain the baseline when the ensemble misses the preset improvement gate.
After the single test run, `python -m digitlab.ensemble_test_report` scores that
pre-frozen diagnostic candidate from the saved test cache. This diagnostic result
cannot override the development deployment decision.

## Results and decision

The development sweep selected **90% 64px scores + 10% 28px scores** as the best
diagnostic ensemble. It gained only **six correct images** over the baseline,
below the predeclared minimum of fifteen. The deployment decision was therefore
frozen as **retain the existing 64px model**, before opening test data.

| Pipeline | Development, 10,000 images | Test, 20,000 images |
| --- | ---: | ---: |
| Previous 28px component | 9,011 (90.11%) | 17,931 (89.66%) |
| Current 64px baseline | 9,692 (96.92%) | **19,315 (96.58%)** |
| Frozen 90%/10% diagnostic ensemble | 9,698 (96.98%) | 19,310 (96.55%) |

On test data, the ensemble fixed **21** baseline errors and introduced **26**.
The 28px component was correct alone on 180 images, while the 64px component was
correct alone on 1,564. Simple weighted averaging did not exploit that limited
complementarity effectively. This small test difference is not a claim of
statistical superiority; it provides no reason to replace the baseline.

The selected deployment pipeline's clean MNIST test remained **98.91%**, as
expected for unchanged weights. The new synthetic test differs from the earlier
97.90% v3.6.0 benchmark and must not be interpreted as a measured regression on
that previous distribution. This experiment does not establish real CAPTCHA
population accuracy. The official `caso_` files were not opened or rerun.

**PASS:** all 25 Python tests. Browser verification matched Python on 60 new
development images. Desktop Edge inference measured **54.2ms median / 89.0ms p95**
for the baseline and **64.0ms / 69.9ms** for the diagnostic ensemble, over 40 timed
inferences after warm-up. Timing variation explains the reversed p95 ordering;
the ensemble's median is slower. These are inference-only measurements on this
machine, not physical-phone benchmarks.

Evidence: [development sweep](../reports/ensemble-v1-development.json),
[browser speed and parity](../reports/ensemble-v1-speed-qa.json),
[pre-test freeze](../reports/ensemble-v1-evaluation-freeze.json),
[single test run](../reports/ensemble-v1-test.json), and
[frozen candidate test analysis](../reports/ensemble-v1-candidate-test.json).

The [public aggregate benchmark](../dist/evaluation/independent-captcha-benchmark.json)
contains counts, metrics and provenance without image data or per-image labels.
The existing digit evaluation download references it. The
[original v3.6.0 summary](../dist/evaluation/digits-captcha-v2-original.json)
is preserved separately. No model, preprocessing or browser inference changes
are deployed by this experiment.

## Publication verification

The site retains application **v3.6.0** and the same frozen 64px weight hash.
Only three evaluation JSON files were published: the new aggregate benchmark,
the original v3.6.0 summary copy and the current summary with its benchmark
reference. All three FTPS uploads passed download hash verification, and all
**46 HTTPS static assets** match local bytes. The frozen model and inference
source hashes remain unchanged. No official challenge evaluation was repeated
for this experiment.

See [publication evidence](../reports/ensemble-v1-ftp-deployment.json),
[HTTPS and unchanged-source verification](../reports/ensemble-v1-public-assets.json)
and the [public benchmark download](https://naoquerosaber.pt/AI/evaluation/independent-captcha-benchmark.json).

A later user-requested live upload recheck again scored **9/10**, with every
prediction, prepared input and score matching the frozen local v3.6.0 result.
Its separate [verification](../reports/ensemble-v1-post-publication-challenge-verification.json)
is deployment evidence, not another independent evaluation or tuning input.
The raw export is preserved locally and excluded from this commit.
