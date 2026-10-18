# All current digit options: official CAPTCHA follow-up

Explicit user-requested official follow-up after prior exposure; no training, tuning, default changes or model selection.

All ten original images were uploaded through the real browser UI for each of 13 frozen configurations. Both TrOCR quality profiles were tested. Full-site and restricted submission inference used local frozen copies of the previously hash-verified public release artifacts. External weights/runtime were actually downloaded; no OCR stubs or image-upload requests were used. All raw outputs were saved before reference labels were opened. This is a known-case follow-up, not a fresh blind test.

| Configuration | Correct / 10 | Correct with original score >90% / 10 | Pretrained |
| --- | ---: | ---: | --- |
| full-mnist | 2 | 0 | no |
| full-mnist-supplementary-v1 | 5 | 1 | no |
| full-captcha-v3 | 10 | 6 | no |
| full-ddddocr | 8 | N/A | yes |
| full-ddddocr-old | 9 | N/A | yes |
| full-captcha-digits | 10 | 10 | yes |
| full-printed-standard | 5 | N/A | yes |
| full-printed-precise | 5 | N/A | yes |
| full-handwritten-standard | 0 | N/A | yes |
| full-handwritten-precise | 0 | N/A | yes |
| submission-mnist | 2 | 0 | no |
| submission-mnist-supplementary-v1 | 5 | 1 | no |
| submission-captcha-v3 | 10 | 6 | no |

OCR rows without scores cannot establish the strict confidence criterion. Pretrained readers are excluded from the restricted submission regardless of results. Scores from the conditional CAPTCHA digit classifier and CNN softmax scores have different meanings; none is a calibrated correctness probability. Full-site/submission CNN predictions and scores match.

| File | Expected | full-mnist | full-mnist-supplementary-v1 | full-captcha-v3 | full-ddddocr | full-ddddocr-old | full-captcha-digits | full-printed-standard | full-printed-precise | full-handwritten-standard | full-handwritten-precise | submission-mnist | submission-mnist-supplementary-v1 | submission-captcha-v3 |
| --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| caso_01.png | 8 | 0 (74.78%) ✗ | 0 (79.11%) ✗ | 8 (99.26%) ✓ | 8 ✓ | 8 ✓ | 8 (97.54%) ✓ | 8 ✓ | 8 ✓ | no single digit ✗ | no single digit ✗ | 0 (74.78%) ✗ | 0 (79.11%) ✗ | 8 (99.26%) ✓ |
| caso_02.png | 3 | 3 (42.34%) ✓ | 3 (57.47%) ✓ | 3 (95.31%) ✓ | 3 ✓ | 3 ✓ | 3 (100.00%) ✓ | 3 ✓ | 3 ✓ | no single digit ✗ | no single digit ✗ | 3 (42.34%) ✓ | 3 (57.47%) ✓ | 3 (95.31%) ✓ |
| caso_03.png | 0 | 0 (50.48%) ✓ | 0 (95.43%) ✓ | 0 (99.76%) ✓ | 0 ✓ | 0 ✓ | 0 (99.97%) ✓ | 0 ✓ | 0 ✓ | no single digit ✗ | no single digit ✗ | 0 (50.48%) ✓ | 0 (95.43%) ✓ | 0 (99.76%) ✓ |
| caso_04.png | 6 | 8 (37.84%) ✗ | 6 (59.56%) ✓ | 6 (72.22%) ✓ | 6 ✓ | 6 ✓ | 6 (99.43%) ✓ | 9 ✗ | 8 ✗ | no single digit ✗ | no single digit ✗ | 8 (37.84%) ✗ | 6 (59.56%) ✓ | 6 (72.22%) ✓ |
| caso_05.png | 1 | 3 (77.90%) ✗ | 3 (89.74%) ✗ | 1 (58.14%) ✓ | 1 ✓ | 1 ✓ | 1 (99.68%) ✓ | no single digit ✗ | no single digit ✗ | no single digit ✗ | no single digit ✗ | 3 (77.90%) ✗ | 3 (89.74%) ✗ | 1 (58.14%) ✓ |
| caso_06.png | 9 | 8 (78.05%) ✗ | 9 (68.74%) ✓ | 9 (99.76%) ✓ | 9 ✓ | 9 ✓ | 9 (99.99%) ✓ | 9 ✓ | 9 ✓ | no single digit ✗ | no single digit ✗ | 8 (78.05%) ✗ | 9 (68.74%) ✓ | 9 (99.76%) ✓ |
| caso_07.png | 4 | 6 (27.89%) ✗ | 8 (37.53%) ✗ | 4 (76.93%) ✓ | 4 ✓ | 4 ✓ | 4 (99.95%) ✓ | 2 ✗ | 2 ✗ | no single digit ✗ | no single digit ✗ | 6 (27.89%) ✗ | 8 (37.53%) ✗ | 4 (76.93%) ✓ |
| caso_08.png | 2 | 3 (59.33%) ✗ | 3 (48.70%) ✗ | 2 (95.37%) ✓ | no single digit ✗ | 2 ✓ | 2 (99.85%) ✓ | 2 ✓ | 2 ✓ | no single digit ✗ | no single digit ✗ | 3 (59.33%) ✗ | 3 (48.70%) ✗ | 2 (95.37%) ✓ |
| caso_09.png | 7 | 3 (31.98%) ✗ | 7 (74.13%) ✓ | 7 (98.50%) ✓ | no single digit ✗ | no single digit ✗ | 7 (92.21%) ✓ | 1 ✗ | 1 ✗ | no single digit ✗ | no single digit ✗ | 3 (31.98%) ✗ | 7 (74.13%) ✓ | 7 (98.50%) ✓ |
| caso_10.png | 5 | 8 (60.55%) ✗ | 3 (47.50%) ✗ | 5 (55.56%) ✓ | 5 ✓ | 5 ✓ | 5 (99.99%) ✓ | no single digit ✗ | no single digit ✗ | no single digit ✗ | no single digit ✗ | 8 (60.55%) ✗ | 3 (47.50%) ✗ | 5 (55.56%) ✓ |

[Frozen identities](release-3.11.1-all-captcha-followup-v1-freeze.json) · [Full comparison and raw-output hashes](release-3.11.1-all-captcha-followup-v1-comparison.json).

PASS means recording/integrity checks completed; classification results are reported above. No training, tuning, model/default change or deployment occurred. Prior evidence is preserved.
