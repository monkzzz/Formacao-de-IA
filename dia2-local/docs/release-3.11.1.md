# Maintenance release 3.11.1

The participant requested a commit, deployment to both sites and comprehensive
post-deployment checks after [the maintenance cleanup](maintenance-cleanup.md).

## Prepared artifacts

- Full site: `dist/`, version 3.11.1, with fresh module URLs for the shared drawing
  and image I/O code. The default is the MNIST-only course model, with separate
  supplementary/residual options. No model weights or recorded scores changed.
- Pages: the independently built `self-trained-submission-cleanup-v4` package,
  with [build identity](../reports/self-trained-submission-cleanup-v4-build.json)
  and [local browser checks](../reports/self-trained-submission-cleanup-v4-browser.json).
  It contains 23 files and four participant-trained model exports; no pretrained
  reader runtime is included. Original v1 and intermediate packages are preserved.

The public full-site preflight identified 14 changed/missing files among 61
application assets. ROMs and parity fixtures are excluded from the transfer plan.
FTPS connectivity and the account's documented root mapping were checked without
changing remote files. The uploader backs up replaced files and verifies every
transferred byte. Its dependency-order regression now includes the Words import
used by the digit reader. Existing deployment receipts are refused before upload.

## Published and independently verified

Source commit: `e592cb16bfdc3360a55001d22df200007b7bef3e`.
Both sites were published on 18 October 2026:

- [Full site](https://naoquerosaber.pt/AI/): 14 files uploaded using verified FTPS,
  with remote backups and transfer verification in the
  [upload receipt](../reports/release-cleanup-3.11.1-ftps.json).
  Independent public HTTPS downloads matched all
  [61 application assets](../reports/release-cleanup-3.11.1-public-assets.json).
- [Restricted Pages site](https://monkzzz.github.io/Formacao-de-IA/):
  [workflow 39142098249](https://github.com/monkzzz/Formacao-de-IA/actions/runs/39142098249)
  succeeded using the separate
  [cleanup-v4 release](https://github.com/monkzzz/Formacao-de-IA/releases/tag/self-trained-submission-cleanup-v4).
  All [23 public assets](../reports/self-trained-pages-cleanup-v4-public-assets.json)
  match the reviewed receipt. Public `pages-build.json` also matches the archive,
  asset list and source commit. The
  [deployment record](../reports/self-trained-pages-cleanup-v4-deployment.json)
  preserves the workflow identity.

## Post-deployment results

| Check | Result and evidence |
| --- | --- |
| Day 1 offline unit suite | PASS: 125 tests, four GUI tests skipped |
| Day 2 unit suite | PASS: 80 tests |
| Python/JavaScript syntax and documentation | [PASS](../reports/release-cleanup-3.11.1-static-checks-v2.json): 117 Python files, 17 JS modules and 256 relative links in 12 documents |
| Full-site model selector | [PASS](../reports/release-cleanup-3.11.1-public-models.json): three digit CNNs, 30 uploads, real activation parity, Letters, exports and failed-load recovery |
| Full-site Words UI and real inference | [PASS](../reports/release-cleanup-3.11.1-public-words-live.json): drawing/eraser/undo/redo, cancellation, exports and real TrOCR inference in both Standard and Precise profiles |
| Digit-reader integration | [PASS](../reports/release-cleanup-3.11.1-public-readers-v2.json): 16 integration checks plus actual printed/handwritten OCR model inference |
| Three CAPTCHA reader downloads | [PASS](../reports/release-cleanup-3.11.1-public-captcha-downloads.json): actual downloads/inference on a font-free synthetic image, including conditional digit scores |
| Responsive design and helper | [Design PASS](../reports/release-cleanup-3.11.1-public-design.json), [helper PASS](../reports/release-cleanup-3.11.1-public-helper-qa.json): six groups each |
| Public Pages classifiers | [PASS](../reports/self-trained-pages-cleanup-v4-browser.json): four models, 40 uploads, preprocessing/scores/activations, filename independence, drawing, downloads, mobile layout and same-origin requests |
| Public recovery and arcade launcher | [PASS](../reports/release-cleanup-3.11.1-public-recovery-v3.json): Pages metadata retry, busy controls and failed-switch preservation; arcade keyboard launch, picker validation, close and focus restoration |

The reader collector now accepts `--digit-experiment mnist` so parity checks use
the active course model rather than the previous residual default. The final
reader report records both its URL and fixture identity. The model-selector
collector retains its historical `public_deployment: NOT RUN` field: it does not
upload files. Its recorded public URL, separate upload/HTTPS receipts and browser
checks establish this deployment verification.

Desktop/mobile Pages screenshots and the full-site mobile design screenshot were
visually inspected. Chromium on Linux was used; Windows execution, the four
skipped GUI tests and game emulation remain NOT RUN. Real OCR checks establish
download/inference integration only, not recognition accuracy.

Earlier attempts remain preserved: the legacy CAPTCHA smoke collector stopped
before inference because its exact licensed fonts are absent on Linux; the
font-free smoke above passed. Recovery attempts 1/2 passed the Pages checks but
stopped at arcade test timing/URL assumptions. The corrected third attempt waits
for iframe readiness and the asynchronous close handler and passes. No website
code changed between those attempts. The initial full-site preflight FAIL means
the expected pre-deployment differences, resolved by the published asset checks.

No official CAPTCHA evaluation, training or tuning ran for this release.
