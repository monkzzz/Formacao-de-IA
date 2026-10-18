# Digit Lab 3.12.0 — fewer digit recognition options

The participant requested removal of the weaker number readers while retaining
Words and single-letter recognition. This changes available choices, not weights,
preprocessing, decoding or model scores.

| Interface | Retained options | Removed from current selectors |
| --- | --- | --- |
| Full site | MNIST-only course CNN, preserved residual digit CNN, EMNIST Letters, CAPTCHA Digits, general DdddOCR and Legacy, Words | Supplementary digit CNN, TrOCR Printed and TrOCR Handwritten in digit mode |
| Restricted submission | MNIST-only course CNN, preserved residual digit CNN, EMNIST Letters | Supplementary digit CNN |

Words retains its separate TrOCR handwriting model and both precision choices.
The MNIST-only model remains the course default despite its weaker historical
CAPTCHA result. The single-digit CAPTCHA reader retains the DdddOCR Legacy
weights it shares with the general Legacy reader. The full site keeps archived
model exports for historical URLs; the new restricted package excludes the
supplementary export. Historical releases, experiments and evaluation reports
remain preserved in the repository and local artifacts.

The removal follows the participant's review of previously exposed official
results: handwritten TrOCR scored 0/10 in digit mode; printed TrOCR and the
supplementary CNN each scored 5/10. These results do not establish general
recognition accuracy. No new official evaluation, training or model selection
experiment was run for this interface change. The professor's strict confidence
criterion remains unmet.

## Local validation

All 103 unit tests passed. The
[current-interface browser suite](../reports/weak-digits-v1-ci.json) passed both
interfaces, actual activation/native upload parity, exports, mobile layout,
[design](../reports/weak-digits-v1-design.json),
[helper](../reports/weak-digits-v1-helper-qa.json),
[Words](../reports/weak-digits-v1-words.json) and
[retained digit readers](../reports/weak-digits-v1-readers.json).
OCR worker doubles are explicit integration tests; they do not measure new OCR
accuracy or claim fresh pretrained model downloads.

The separate `self-trained-submission-numbers-v5` package contains three
participant-trained models and 20 reviewed files. Its
[build receipt](../reports/self-trained-submission-numbers-v5-build.json) preserves
the archive/file hashes and checkpoint ancestry. Its
[browser verification](../reports/self-trained-submission-numbers-v5-browser.json)
passed 30 uploads, native score/input and activation parity, drawing, export,
mobile layout, retry and recovery without third-party requests.

## Publication and live verification

Source commit `10dbe2c` passed
[Linux and Windows CI](https://github.com/monkzzz/Formacao-de-IA/actions/runs/39172005359).
The full site was published locally over verified FTPS: six changed assets were
backed up, uploaded under temporary names, hash-checked and published by rename.
A subsequent index-only wording correction removed a stale TrOCR reference from
the digit reader hint; its separate backup/journal remains preserved. FTP
credentials stayed local and were not sent to GitHub.

The [final HTTPS comparison](../reports/release-3.12.0-final-https.json) matched
all 61 public files. [Live retained CNN checks](../reports/release-3.12.0-public-cnn.json)
passed actual activation and native upload-score parity for both digit CNNs and
single letters. [Digit reader integration](../reports/release-3.12.0-public-readers.json)
and [Words integration](../reports/release-3.12.0-public-words.json) passed;
their pretrained-worker doubles are explicit, and new real pretrained-model smoke
tests were NOT RUN. The [final option check](../reports/release-3.12.0-final-options.json)
confirmed the removed choices and stale hint are absent, while Words retains both
precision options and Letters retains 26 classes. Public mobile screenshots were
inspected manually.

The separate [Pages deployment](https://github.com/monkzzz/Formacao-de-IA/actions/runs/39172547980)
published the reviewed
[numbers-v5 release](https://github.com/monkzzz/Formacao-de-IA/releases/tag/self-trained-submission-numbers-v5).
[All 20 package file hashes and the published identity](../reports/release-3.12.0-pages-assets.json)
matched; [live browser QA](../reports/release-3.12.0-pages-browser.json) passed
three models and 30 uploads, drawing, export, native parity and mobile layout.
The later full-site hint correction did not change this package or its files.

See the [completion record](../reports/release-3.12.0-completion.json) and
[local FTP deployment journal](../reports/release-3.12.0-ftp-deployment.json).
