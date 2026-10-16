# Selectable digit readers (v3.8.0)

Digits retains the project-trained residual CNN as its default and adds two
pretrained OCR alternatives. Select **Digit model**, choose Standard or Full
precision, and read the drawing or choose images. Re-upload an image to compare
models; each gallery result retains its own model, precision and original output.
Selecting a previous result restores its reader and quality. Letters and Words
keep their existing models.

| Reader | Source | Pinned revision |
| --- | --- | --- |
| Printed | [Xenova/trocr-small-printed](https://huggingface.co/Xenova/trocr-small-printed) | `56c1626ea0b4aab378f3228235be2e824d4256bd` |
| Handwritten | [Xenova/trocr-small-handwritten](https://huggingface.co/Xenova/trocr-small-handwritten) | `2432e24d184b1d964d07ed04f5d9e21d31a59141` |

The printed model derives from Microsoft's SROIE receipt-text reader, and the
handwritten model from its IAM English handwriting reader. These are line OCR
models, not CAPTCHA-specific models. Neither is trained by this project. Their
performance on isolated digits and noisy CAPTCHAs is unmeasured. Larger models
or full precision do not automatically imply better CAPTCHA recognition. The
homepage's MNIST and completed challenge metrics belong to the default CNN.

## Downloads and execution

The same Transformers.js `2.17.2` runtime as Words runs inside a dedicated module
worker, using single-thread WebAssembly. Standard uses INT8 weights, about 65 MB;
Full precision uses FP32 weights, about 250 MB. The printed graphs total
63,610,553 bytes (INT8) or 246,543,658 bytes (FP32), excluding runtime and tokenizer
assets. Each model/quality combination has separate cached assets. Initial use
requires internet access to Hugging Face and jsDelivr. Browser cache reuse is
best-effort; offline availability is not guaranteed. No API key or inference API
is used, and image pixels stay on the device.

Changing readers or quality, leaving Digits, cancellation, errors and a four-minute
timeout terminate the OCR worker. Successful consecutive reads reuse it. During
a read, controls are locked and Cancel digit reading stops the current batch.
Cancellation and errors release controls for retry. Large FP32 models may exceed
the memory available on mobile devices; Standard remains selectable.

## Inputs, output and provenance

OCR reuses Words' transparent-background compositing, polarity normalization,
foreground crop and padding (`word-crop-display-v1`). The prepared image is shown
and then resized/normalized by the pretrained model's own processor. It does not
use the CNN's 64px tensor. Generation is greedy with a 16-token output limit.

Original text is displayed safely without HTML interpretation or substitutions.
Only exactly one ASCII digit is accepted. Empty output, `O`, `7.`, multiple digits
and surrounding whitespace remain unaccepted original output; no text is silently
stripped or mapped to a preferred digit. Such records export `accepted: false`,
`predicted: null`, `predicted_label: null`, and their original `raw_text`.

OCR records include the source model/revision, precision, decoding, preprocessing,
prepared dimensions and a SHA-256 of the prepared RGBA pixels. Model weight hash,
class scores, logits and CNN input size are null rather than borrowed from the
project CNN. The prepared-pixel hash is distinct from the CNN's float-input hash.
The CNN activation and class-score views are hidden for OCR readers and restored
when viewing CNN results. Export schema 2 retains its existing fields and adds
per-record OCR metadata. Consumers must allow null prediction/score fields.

## Validation

Run from `dia2-local/`, using new report names to preserve existing evidence:

```powershell
.\.venv\Scripts\python.exe serve.py --port 8782
.\.venv\Scripts\python.exe -m digitlab.digit_readers_qa --report <new-report.json>
# Optional: downloads both Standard models and runs a synthetic-image smoke test.
.\.venv\Scripts\python.exe -m digitlab.digit_readers_qa --report <new-live-report.json> --live
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The browser collector separates worker-double integration checks from optional
real-model smoke tests. It checks unchanged digit/letter activation parity, lazy
loading, blank rejection, per-model exports, strict acceptance, safe text, gallery
restoration, cancellation, download failure recovery, modes and mobile overflow.
It saves desktop/mobile screenshots under a report-specific prefix. These checks
do not establish CAPTCHA accuracy. Official challenge files and historical
evaluation reports are excluded. Public deployment passed; see the separate
[deployment record and public verification](hosting.md#v380-selectable-digit-readers).

Recorded local checks on 2026-10-16:

| Check | Result | Evidence |
| --- | --- | --- |
| Digit reader interface, drawing, cancellation, timeout, exports and responsive layout, 14 groups | PASS | [Final browser checks](../reports/digit-readers-final-local-20261016.json) |
| Both real Standard OCR models, one synthetic digit each | PASS | [Real-model smoke checks](../reports/digit-readers-local-20261016.json) |
| Existing digit/letter parity, 36 uploads and mixed exports | PASS | [Character regression](../reports/digit-readers-character-20261016.json) |
| Existing Words integration, 19 groups | PASS | [Words regression](../reports/digit-readers-words-20261016.json) |
| Scopedog helper, 6 groups | PASS | [Helper regression](../reports/digit-readers-helper-20261016-qa.json) |
| Python unit suite, 28 tests | PASS | `python -m unittest discover -s tests -v` |
| Real FP32 OCR inference | NOT RUN | Precision switching verified with worker doubles only |
| CAPTCHA accuracy comparison | NOT RUN | No official challenge inputs used |

Both Standard models transcribed the synthetic seven as `7`. This is an
integration smoke check, not evidence of improved CAPTCHA accuracy. Desktop and
mobile screenshots were captured separately; the mobile layout was visually
inspected. Previous release and challenge reports remain unchanged.

The [public digit reader checks](../reports/release-3.8.0-public-digit-readers-qa.json)
also passed all 14 groups and real Standard-model smoke tests for both readers.
Both transcribed the same synthetic `7` correctly from the deployed origin.
All 52 public assets matched local hashes; character, Words and helper regressions
passed separately. See [all public evidence](hosting.md#v380-selectable-digit-readers).
