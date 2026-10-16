# Raw-image CAPTCHA-style experiment

The previous robustness release added noise to normalized 28 x 28 tensors.
This experiment renders independent full-size images first, then runs the
unchanged Python/browser preprocessing. Stray marks therefore affect the crop,
scale and center during training as they do in uploaded images.

## Protocol fixed before final challenge evaluation

- Start from the robustness digit checkpoint; preserve every earlier export,
  checkpoint, frozen archive and report. Letters and Words keep their models.
- Keep the original MNIST training/validation split: 55,000 / 5,000 source images.
  Never load challenge images or their generator for training or selection.
- Train for 12 epochs. Each epoch renders 40,000 new raw images, half handwriting
  and half printed digits, and mixes in 20,000 clean training examples.
- Use 17 installed Windows font faces for training. Reserve Cambria, Candara,
  Constantia and Corbel families for validation and synthetic test rendering.
  Fonts stay on the machine and are not redistributed. Record font hashes.
- Vary glyph shape, stroke thickness, rotation, scale and position; render color
  backgrounds, both polarities, lines, arcs and speckles on a 64 x 64 canvas.
  These parameters are generic, not extracted from the official CAPTCHA images.
- Freeze 5,000 raw validation examples with seed 20261022. Select the lowest raw
  validation cross-entropy among checkpoints that improve raw accuracy and keep
  clean validation accuracy within 0.3 percentage points of the starting model.
- After selection ends, load official MNIST test data once. Report clean test
  accuracy and a separate 10,000-image raw synthetic test (seed 20261023), with
  the starting model measured on identical test inputs. Synthetic accuracy does
  not establish real CAPTCHA accuracy.
- Export the same CNN architecture and preprocessing contract into a separate
  `dist/model/captcha-v1/digits/` folder. Verify weights, browser/Python logits,
  intermediate activations, raw uploads, drawing, letters, mixed exports and
  failure recovery before official challenge evaluation.
- Freeze source and model hashes before one final upload of `caso_01.png` through
  `caso_10.png`. Write raw predictions before comparing against historical labels.
  Existing challenge outcomes are known, so this is a follow-up, not a blind test.
  Do not change training, preprocessing or inference based on this final result.

## Reproduce

From `dia2-local/`, with the robustness checkpoint and Windows fonts present:

```powershell
.\.venv\Scripts\python.exe -m digitlab.captcha --name captcha-v1
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The trainer refuses existing experiment destinations. A different `--name` is
required for a separate experiment. Training checkpoints, raw fixtures, font
files and weight binaries are not committed. The JSON report records selection,
metrics, source split, seeds and hashes. Browser inference remains local.

## Results

Epoch 11 was selected on validation cross-entropy. On the official clean MNIST
test it scored **9,920 / 10,000 (99.20%)**, compared with 99.32% for the starting
robustness model. On the separate full-pipeline raw synthetic test it scored
**9,697 / 10,000 (96.97%)**, compared with **8,727 / 10,000 (87.27%)**.
These are separate distributions and should not be combined into one score.

After freezing source and weight hashes, the single final browser upload of the
official challenge scored **7 / 10**, compared with **2 / 10** previously.
There were no subsequent training, preprocessing or inference adjustments.
The prior outcomes were known, so this remains a follow-up evaluation.

Selected weight SHA-256:
`9531ae35882aa8ba348911f41e506bc00bb359d8110116ce98a2c6c1f8e04b13`.

- **PASS:** all 18 Python tests.
- **PASS:** digit and letter activation parity, 36 clean uploads, mixed-mode
  exports, blank/invalid uploads, failure recovery and mobile layout.
- **PASS:** 40 raw synthetic uploads match Python preprocessing and scores;
  filename independence and real drawing work.
- **PASS:** all six authored-helper browser groups.
- **PASS:** one frozen official challenge collection, raw predictions saved
  before historical-label comparison.

Evidence: [training and test metrics](../reports/captcha-v1.json),
[environment](../reports/captcha-v1-environment.json),
[browser regression](../reports/captcha-v1-browser-qa.json),
[raw uploads](../reports/captcha-v1-raw-browser-qa.json),
[helper checks](../reports/captcha-v1-helper-qa.json),
[freeze](../reports/captcha-v1-challenge-freeze.json),
[raw challenge](../reports/captcha-v1-challenge-raw.json), and
[comparison](../reports/captcha-v1-challenge-comparison.json).

The [public aggregate summary](../dist/evaluation/digits-captcha.json) contains
metrics and provenance, without challenge labels or image pixels.

Browser commands (the local server must be running on port 8767):

```powershell
.\.venv\Scripts\python.exe -m digitlab.robust_qa --url http://127.0.0.1:8767/ --digit-experiment captcha-v1 --report <new-report.json> --screenshot-prefix <new-prefix>
.\.venv\Scripts\python.exe -m digitlab.captcha_qa --url http://127.0.0.1:8767/ --report <new-raw-report.json>
```

The completed challenge command was `python -m digitlab.robust_challenge --url
http://127.0.0.1:8767/ --experiment captcha-v1 --qa-report captcha-v1-browser-qa.json`.
It refuses to overwrite the completed evaluation; do not rerun it to tune results.

## Public deployment

Release v3.5.0 is deployed at [Digit Lab](https://naoquerosaber.pt/AI/).
All eight changed assets passed verified FTPS upload with replacement backups.
All **41 public static asset hashes** match the local release over HTTPS;
JavaScript MIME types and frozen-source integrity also pass.

Live browser checks passed digit/letter activations and 36 clean uploads,
40 independent noisy uploads, drawing, filename independence, failure recovery,
mobile layout and all six helper groups. The official challenge was not rerun
for deployment; the public model hash matches the frozen evaluation.

Evidence: [FTPS deployment](../reports/release-3.5.0-ftp-deployment.json),
[HTTPS assets](../reports/release-3.5.0-http-assets.json),
[live character regression](../reports/release-3.5.0-public-character-qa.json),
[live raw uploads](../reports/release-3.5.0-public-raw-qa.json), and
[live helper checks](../reports/release-3.5.0-public-helper-qa.json).
