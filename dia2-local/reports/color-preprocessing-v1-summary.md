# Color-aware preprocessing: development results

Fixed weights; single candidate; [frozen protocol](../docs/color-preprocessing.md).

| Set | Current accuracy | RGB accuracy | Current correct >90% | RGB correct >90% | Current/RGB rejections |
| --- | ---: | ---: | ---: | ---: | ---: |
| raw (1800) | 76.278% | 98.278% | 73.944% | 95.333% | 400/0 |
| legacy (1200) | 98.083% | 98.083% | 95.083% | 95.083% | 0/0 |
| color (600) | 32.667% | 98.667% | 31.667% | 95.833% | 400/0 |
| clean (5000) | 99.300% | 99.300% | 97.760% | 97.760% | 0/0 |

Development eligible: **False**; selected: **current**.

Gate results: no_more_rejections=PASS, raw_accuracy=PASS, legacy_accuracy=PASS, clean_accuracy=PASS, strict_90_gain=PASS, lower_nll=PASS, brier=PASS, ece=PASS, confident_errors=FAIL.

[Raw measurements and provenance](color-preprocessing-v1.json). [Actual browser parity, uploads, activation and timing evidence](color-preprocessing-v1-browser.json).

Rejections count as incorrect; uniform vectors are only explicit NLL/Brier penalties. Strict >90% uses original unrounded model scores. Two palettes deliberately have almost identical grayscale brightness. Their frequency here does not estimate real CAPTCHA prevalence. The coding agent's visual spot-check is separate from independent human readability review, which is NOT RUN.

Active app and all model weights remain unchanged. No training, reserved test, official CAPTCHA follow-up, deployment, CUDA setup, commit or push ran in this phase. Development eligibility is not official acceptance; the professor's all-ten confidence target remains unmet.

## Validation and failed gate

The sole failed gate was the raw count of confidently wrong predictions: **2 → 3**. Legacy-style confidently wrong predictions remained 2; the recovered colored set added one. No threshold was relaxed after seeing the result. Color recovery is useful development evidence, but this candidate does not qualify for automatic replacement.

- [Unit suite](color-preprocessing-v1-unit-tests.json): **65 tests passed**.
- [Integrity audit](color-preprocessing-v1-validation.json): **15 checks passed**, including saved-score reproduction, balanced sources/classes, fixture hashes, validation-only source membership and preservation of active assets.
- [Fixed contact sheet](screenshots/color-preprocessing-v1-inputs.png): the coding agent inspected all ten displayed samples; RGB retains the glyphs where grayscale rejects equal-brightness colors. Noise and crossing lines remain. This spot-check does not establish independent human readability or official CAPTCHA accuracy.

To reproduce the audit and contact sheet after a new, separately named run, use `<python> -m digitlab.color_audit` before writing its final summary. Completed outputs are preserved.
