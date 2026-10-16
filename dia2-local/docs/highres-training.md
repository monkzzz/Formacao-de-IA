# Higher-resolution digit experiment

This protocol is fixed before final evaluation of the official challenge.
The earlier 28px CAPTCHA model and all its evaluation records remain preserved.

## Training and selection

- Use 64 x 64 digit inputs, with a 48px foreground box and center-of-mass
  alignment. Keep the existing grayscale, border-background and contrast rules.
  Letters continue to use the unchanged 28px contract.
- The network uses Conv16/max-pool (32px maps), Conv32/max-pool/average-pool
  (8px maps), Dense128 and ten outputs. Initialize from the v3.5.0 checkpoint;
  interpolate only its spatial dense weights to the new 8px layout.
- Preserve the original 55,000 / 5,000 MNIST source split. Train for a fixed
  12 epochs, each with 40,000 independently rendered raw images and 20,000
  clean handwriting samples. Half the raw images use printed fonts.
- Extend training from 17 to 31 font faces. Cambria, Candara, Constantia and
  Corbel remain held-out families. Font files are not redistributed.
- Mix 30% of the previous independent renderer with 70% larger native glyphs,
  short stroke gaps, shear/rotation, lines/arcs and speckles. Neither the official
  challenge generator nor the `caso_` images are used to define perturbations.
- Use seed 20261030, fixed 5,000-image validation seed 20261031 and a separate
  10,000-image final synthetic test with seed 20261032. Evaluate the previous
  model on exactly the same raw images using its own 28px preprocessing.
- Select the lowest raw validation loss among checkpoints that improve raw
  validation accuracy and keep clean validation within 0.3 percentage points
  of the previous model. Load official MNIST test images only after selection.
- Record the clean and synthetic test scores separately. Synthetic success does
  not establish real CAPTCHA population accuracy.

## Browser and final evaluation

Validate Python/JavaScript input pixels, logits and intermediate activations for
both resolutions. Maintain upload, drawing, mixed exports, actual feature maps,
Letters, Words, the helper and the arcade. Exports identify each image's input
size and preprocessing contract.

The versioned inference entry preserves the 28px model for an older cached page
that imports `captcha-1` or `robust-1`. The refreshed page imports `captcha-2` and
uses the selected 64px model. Earlier model folders remain available.

Measure both classifiers on the same desktop browser. Require the 64px model's
95th-percentile inference time to remain below 150ms in this environment; report
the measured values and the limits of emulated mobile checks.

After validation, freeze model and inference source hashes before one final
official challenge upload. The prior challenge outcomes are known, so this is a
follow-up, not a new blind test. Do not tune against that result. Keep any live
site verification separate and preserve earlier evaluation records.

Only deploy a candidate that passes independent validation and browser checks.
Document the actual result even if the official challenge does not improve.

## Reproduce

From `dia2-local/`, with the previous checkpoint and installed Windows fonts:

```powershell
.\.venv\Scripts\python.exe -m digitlab.highres --name captcha-v2
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The trainer refuses existing experiment destinations. Checkpoints, font files,
datasets, raw fixtures and weight binaries are ignored by Git. Training metrics,
environment, font hashes, selection history and exported weight identity are
recorded separately in `reports/captcha-v2.json`.

Start `python serve.py --port 8768` for local verification. The checks use separate
report destinations and never replace the completed v3.5.0 reports:

```powershell
.\.venv\Scripts\python.exe -m digitlab.highres_qa --report captcha-v2-runtime-qa.json
.\.venv\Scripts\python.exe -m digitlab.robust_qa --url http://127.0.0.1:8768/ --digit-experiment captcha-v2 --report captcha-v2-browser-qa.json --screenshot-prefix captcha-v2
.\.venv\Scripts\python.exe -m digitlab.captcha_qa --url http://127.0.0.1:8768/ --experiment captcha-v2 --report captcha-v2-raw-browser-qa.json
```

The final challenge collector accepts `--experiment captcha-v2 --qa-report
captcha-v2-browser-qa.json` and refuses to overwrite an existing evaluation.
After deployment, `digitlab.deployed_challenge` verifies the public site against
the frozen local predictions and writes separate evidence. The public summary
builder `digitlab.release_summary` publishes aggregate metrics without labels or
image pixels in `evaluation/digits-captcha-v2.json`, preserving the v3.5.0 summary.

## Measured results

Epoch 12 was selected on validation before the final test data was loaded.

| Evaluation | Previous 28px model | Selected 64px model |
| --- | ---: | ---: |
| Clean MNIST, 10,000 images | 9,920 / 10,000 (99.20%) | 9,891 / 10,000 (98.91%) |
| Broader raw synthetic test, 10,000 images | 9,509 / 10,000 (95.09%) | 9,790 / 10,000 (97.90%) |
| Official challenge follow-up | 7 / 10 | 9 / 10 |

The synthetic comparison uses identical raw images for both models. This is a
broader distribution than the earlier v3.5.0 synthetic benchmark. Clean test
accuracy decreased by 0.29 percentage points. The challenge result comes from
one browser upload after freezing model and source hashes. Prior outcomes were
known; no training, preprocessing or inference changes followed the result.

Weight SHA-256:
`c415bceb885677c1f57c800f22feaf1659ea184f7cf39c2bca462cde4e1f5c9c`.

**PASS:** all 23 Python tests, 36 clean digit/letter uploads, 60 raw synthetic
uploads, Python/JavaScript activation and pixel parity, filename independence,
drawing, mixed exports, blank/invalid inputs, recovery, helper behavior, Words
entry, mobile layout and cached previous model entry points.

Selected-model local desktop Edge inference measured **54.6ms median / 71.2ms
p95**, compared with 10.1ms / 11.4ms for the previous model. Public-site testing
measured **55.8ms / 61.8ms**, compared with 10.9ms / 14.6ms. These are 30 timed
inferences per model after warm-up on this machine. Physical-phone speed is
**NOT RUN**; mobile layout uses Edge viewport emulation.

Local evidence: [training and test metrics](../reports/captcha-v2.json),
[character regression](../reports/captcha-v2-browser-qa.json),
[raw uploads](../reports/captcha-v2-raw-browser-qa.json),
[runtime and speed](../reports/captcha-v2-runtime-qa.json),
[helper](../reports/captcha-v2-helper-qa.json),
[freeze](../reports/captcha-v2-challenge-freeze.json),
[raw challenge](../reports/captcha-v2-challenge-raw.json) and
[comparison](../reports/captcha-v2-challenge-comparison.json).

## Public deployment and direct challenge verification

Release **v3.6.0** is live at [Digit Lab](https://naoquerosaber.pt/AI/).
All **nine changed uploads** passed FTPS hash verification with replacement
backups. All **44 HTTPS static asset hashes**, JavaScript MIME types and frozen
source hashes passed independent verification.

Live browser checks passed character regression, 60 noisy uploads, drawing,
helper behavior, dimensions, cached-page compatibility and the speed limit.
All ten official images were also uploaded on the live site in a fresh Edge
session: **9/10 correct**, with every prediction, input pixel and score matching
the frozen local evaluation. This is deployment verification of the same model,
not another independent accuracy test or a selection/tuning run.

Evidence: [FTPS deployment](../reports/release-3.6.0-ftp-deployment.json),
[HTTPS assets](../reports/release-3.6.0-http-assets.json),
[live character regression](../reports/release-3.6.0-public-character-qa.json),
[live raw uploads](../reports/release-3.6.0-public-raw-qa.json),
[live runtime and speed](../reports/release-3.6.0-public-runtime-qa.json),
[live helper](../reports/release-3.6.0-public-helper-qa.json),
[direct live challenge verification](../reports/release-3.6.0-public-challenge-verification.json)
and [raw live export](../reports/release-3.6.0-public-challenge-verification-raw.json).

The [public aggregate summary](../dist/evaluation/digits-captcha-v2.json)
contains metrics and provenance without the challenge answer key or image pixels.

A subsequent user-requested live-site recheck again scored 9/10, with all inputs,
scores and predictions matching the frozen result. Its separate
[verification report](../reports/release-3.6.0-public-challenge-recheck.json) and
[raw export](../reports/release-3.6.0-public-challenge-recheck-raw.json) are preserved.
This recheck preceded the independent ensemble benchmark and was not used to
construct that benchmark or select its weights.
