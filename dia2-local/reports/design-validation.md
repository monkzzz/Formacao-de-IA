# Website Design Release

Public website: https://naoquerosaber.pt/AI/index.html

## Changes

- Clearer typography and visual hierarchy, with a distinct drawing workspace and prediction card.
- More visible Digits/Letters controls, measured benchmark cards, stronger key-text contrast, and consistent buttons and icons.
- A contained upload gallery, with two columns on phones, an accurate image count, and individual results that remain selectable.
- Expandable network activations and model fingerprints, keeping the main page focused while retaining the real model information.
- Keyboard skip navigation, an anchor that opens the network view, visible focus indicators, and reduced-motion support.
- Versioned `v3/` assets, with earlier assets retained for cached pages. The entry page was uploaded last.

## Verification

All **25 groups passed locally and on the published website**:

| Checks | Local evidence | Public evidence |
| --- | --- | --- |
| Six design groups | [Layout and accessibility checks](design-qa.json) | [Published layout checks](public-design-qa.json) |
| Nine digit regression groups | [Digit checks](design-digits-qa.json) | [Published digit checks](public-design-digits-qa.json) |
| Ten letter regression groups | [Letter checks](design-letters-qa.json) | [Published letter checks](public-design-letters-qa.json) |

Responsive checks cover 320, 390, 768, 1024, and 1440-pixel widths, with no horizontal document overflow. The mobile upload gallery remains two columns and at most 380 pixels tall. Main action controls are at least 40 pixels tall. Sampled primary text/control contrast ratios meet 4.5:1; this is a targeted check, not a claim of a comprehensive accessibility audit.

Keyboard checks verify the skip link, native expandable network section, and navigation anchor. Reduced-motion checks verify that smooth scrolling and transitions are disabled when requested.

Both recognition suites check real browser outputs against the original trained models, including uploads, mode changes, saved-result identity, and export. A letter-test assertion was updated to open the fingerprint's new expandable section before reading it; the model hash itself did not change.

## Model and evaluation integrity

This release changes presentation and interface behavior. The original digit and letter weights, shared preprocessing, inference calculations, and recorded test metrics are unchanged. The initial Desafio raw predictions remain preserved. No retraining or challenge-dependent tuning was performed.

The deployment downloaded and SHA-256-verified all 17 static assets. Training datasets, checkpoints, parity fixtures, and credentials were excluded from the website package.

## Screenshots

- [Published desktop layout](screenshots/public-design-1440.png)
- [Published mobile layout](screenshots/public-design-390.png)
