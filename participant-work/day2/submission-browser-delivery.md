# Public browser submission verification

Verified 2026-10-17 for Issues [#3](https://github.com/monkzzz/Formacao-de-IA/issues/3),
[#4](https://github.com/monkzzz/Formacao-de-IA/issues/4) and
[#5](https://github.com/monkzzz/Formacao-de-IA/issues/5).
The participant requested that the existing site remain intact. No deployment,
hosting setting, runtime, preprocessing, weights or frozen evaluation changed.
GitHub Pages publication and instructor acceptance of the hosting substitution
remain pending; this record completes five subsequent actionable checklist items.
The process approval request also remains deferred and unsent.

## Submission identity and artifacts

- Submitted existing origin: [Digit Lab](https://naoquerosaber.pt/AI/).
- Observed application release: **v3.10.0**. The default trained model is the
  **captcha-v3 residual CNN** introduced in v3.7.0; application and model versions
  identify different artifacts.
- Source baseline: `809ef4d96e4e7f127b5e953ea733c714b59a7d39`.
  The deployed entry page and app module matched this checkout. This is a scoped
  byte comparison, not proof of the original deployment's Git commit or a complete
  site asset audit. The containing evidence commit is discoverable with
  `git log -1 --format=%H -- participant-work/day2/submission-browser-delivery.md`.
- Digit weights: 1,090,472 bytes, SHA-256
  `d962c7f1aefd4f86cf9fcc621e30a1e8fbbce092c5a47ab3dd88e0f64573b42c`.
- Letter weights: 835,944 bytes, SHA-256
  `0fef4b3155457eb1be91547590b48ebc61823c68b79fd414b406835cbfe1b101`.

The ignored deployment binaries are already supplied by the existing static
host at `model/captcha-v3/digits/weights.bin` and
`model/robust/letters/weights.bin` relative to that origin. Both real HTTPS
downloads matched local files in the [current identity record](submission-public-interactions.json).
For a clean checkout, use the [verified recovery process](submission-artifacts.md)
(`python serve.py --download-models` from `dia2-local/`). Keep manifests and
relative directory paths with those binaries when assembling a future static
artifact; copying source alone is insufficient. The existing host is the current
artifact source, not a promise of permanent archival availability. No weights,
checkpoints, datasets, ROMs or credentials enter this commit.

## Executed checks

[Existing robust QA results](../../dia2-local/reports/submission-20261017-browser-qa.json)
record a fresh PASS for the selected CNN and companion letter model:

- Ten digit and 26 letter image uploads with per-image results and mixed export.
- Python/JavaScript prepared input agreement within `1e-6`, score agreement within
  `1e-5`, and intermediate activation/logit agreement within `1e-4`.
- Blank/corrupt image errors, failed letter-model download, preservation of the
  working digit mode, and successful retry.
- Mobile layout, no uncaught page errors, preservation of the original frozen
  digit weight identity, and observed network requests restricted to GETs on the
  submitted origin or blob URLs. No image inference API was used.

[Supplemental public interactions](submission-public-interactions.json) record
mouse drawing, erasing, undo/redo, pixel-exact clearing, emulated touch drawing,
real CNN classification, output reset and a single-file upload. The existing
parity checks compare real feature-map values with Python. Touch was dispatched
through Edge's browser protocol; no physical touchscreen or human desktop
walkthrough is claimed. The initial sandbox launch failed with Windows error 5;
the existing collector then passed after reviewed escalation, as did the new
supplemental collector.

The live selector defaults to `local` and visibly says
“Digit Lab residual CNN · trained here · default”. Its details explicitly identify
CAPTCHA Digits/DdddOCR/TrOCR as pretrained extensions; Words has a separate
pretrained model disclosure. No optional reader inference or accuracy test ran.
They do not replace the participant-trained CNN deliverable.

## Screenshots, reproduction and limits

Screenshots were captured under the intentionally ignored
`dia2-local/reports/screenshots/` directory: `submission-20261017-mobile.png` and
`submission-20261017-desktop.png`. The assistant visually inspected the desktop
capture, including default-model disclosure, per-class scores, upload preview,
architecture and release footer. The JSON records remain committed evidence;
local screenshots must be retained separately with other ignored artifacts.

From `dia2-local/`, reproduce the parity/upload collector with a **new** report
and screenshot prefix:

```powershell
.\.venv\Scripts\python.exe -m digitlab.robust_qa --url https://naoquerosaber.pt/AI/ --digit-experiment captcha-v3 --report <new-report.json> --screenshot-prefix <new-prefix>
```

The [supplemental collector](verify-submitted-browser.py) runs from the repository
root with `dia2-local\.venv\Scripts\python.exe participant-work/day2/verify-submitted-browser.py`.
It refuses the existing report destination; choose a new destination in its source
before a follow-up run. Both collectors use installed Edge and existing local
dependencies. The supplemental collector reuses the existing drawing helper.

These are behavior, deployment identity and numerical parity checks, not fresh
accuracy measurements. Historical 99.10% clean MNIST, 98.73% synthetic robustness
and the ten-image challenge follow-up retain their separate provenance in the
[submission evidence index](submission-evidence-index.md). A model score is not a
calibrated probability of correctness. No official challenge images were opened,
no training ran, and no inference or UI changes required a new unit-suite run.
