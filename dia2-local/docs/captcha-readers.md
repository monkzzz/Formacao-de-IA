# CAPTCHA-specific pretrained readers (v3.9.0)

The [v3.10.0 single-digit classifier](ctc-digits.md) is a separate configuration
using the same Legacy weights with exact one-digit CTC likelihoods. Its new
frozen follow-up scored 10/10. The general readers and results below retain
their original unrestricted-text decoding and scope.

Digits adds **DdddOCR** and **DdddOCR Legacy** alongside the project CNN and
the earlier TrOCR text-line readers. Both are pretrained for visual CAPTCHAs,
download on demand and execute entirely in a browser worker. Neither model was
trained by this project. The existing project CNN remains the default.

These improve the tested external alternatives, but neither achieved 10/10 on
the official follow-up. No model guarantees perfect CAPTCHA recognition.

## Results and evaluation integrity

Both candidates were screened on independent synthetic images before opening
the official challenge. The exploratory Python screen used 200 newly generated
printed digits, balanced between 100 clean and 100 noisy examples. DdddOCR and
the current CNN scored 200/200; Legacy scored 196/200. A second, separately seeded
200-image set verified the actual browser pipeline: 200/200 and 196/200,
respectively. These small synthetic screens are not population accuracy estimates.

The browser runtime, model identities, character tables and preprocessing were
then frozen before one official ten-image follow-up per candidate. Raw results
were durably saved before consulting the historical answer key. The images and
earlier outcomes were already known; this is not a blind test. No weights,
preprocessing, decoder or defaults changed after the result.

| Reader | Official follow-up |
| --- | ---: |
| Existing project residual CNN, separate v3.8.0 verification | 10/10 |
| DdddOCR | **8/10** |
| DdddOCR Legacy | **9/10** |
| TrOCR Printed, Standard and Full precision | 5/10 each |
| TrOCR Handwritten, Standard and Full precision | 0/10 each |

Evidence:

- [Exploratory independent Python screen](../reports/ddddocr-independent-development-20261016.json).
- [Actual browser independent screen](../reports/ddddocr-browser-development-20261016.json),
  [frozen sources](../reports/ddddocr-browser-development-20261016-freeze.json).
- [Frozen official follow-up](../reports/ddddocr-frozen-challenge-followup-20261016.json),
  [freeze](../reports/ddddocr-frozen-challenge-followup-20261016-freeze.json),
  [DdddOCR raw outputs](../reports/ddddocr-frozen-challenge-followup-20261016-ddddocr-raw.json),
  [Legacy raw outputs](../reports/ddddocr-frozen-challenge-followup-20261016-ddddocr-old-raw.json).
- [Earlier CNN and TrOCR follow-up](../reports/release-3.8.0-local-captcha-readers-20261016.json).

Official images were selected in a **local** browser only. The collector blocked
non-GET requests and requests with bodies. Previously downloaded, hash-verified
model bytes were supplied by browser interception for repeatable recognition
checks; the runtime and inference were real, not prediction doubles. Sources and
weights match those used by the selector. No challenge images were transmitted
to a remote inference API. Earlier historical reports remain unchanged.

## Model provenance and browser contract

Source: [sml2h3/ddddocr](https://github.com/sml2h3/ddddocr), MIT license,
revision `c40f56f95412e10bcb9bd0bd24411e92f896d238`. The normalization and
greedy CTC decoding follow the project's historical tagged reference
`eb4babbfac06033c3a31c2ab5e9918df8f0905d0`. Both published character arrays were
checked against that reference without executing third-party Python code.

| Option | Published model | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| DdddOCR | `ddddocr/common.onnx` | 54,088,400 | `33b5cd351ee94e73a6bf8fa18c415ed8b819b3ffd342e267c30d8ad8334e34e8` |
| Legacy | `ddddocr/common_old.onnx` | 13,606,051 | `b8f2ad9cbc1f2e3922a6cb9459e30824e7e2467f3fb4fd61420640e34ea0bf68` |

Pinned weights download from `raw.githubusercontent.com`; ONNX Runtime Web
`1.20.1` and its WASM assets download from jsDelivr. Model hashes are verified
before session creation. Character tables are distributed with this release in
`dist/v3/ddddocr-charsets.json`; the MIT notice is retained in
`dist/assets/ddddocr-LICENSE.txt`. No model binaries are committed or copied into
the static serving directory. The pretrained models have fixed FP32 weights;
the TrOCR precision selector is hidden for them. Browser HTTP caching is best
effort and offline availability is not guaranteed.

`ddddocr-browser64-v1` composites transparency over white, preserves the entire
image, resizes to 64px height at its original aspect ratio, converts to grayscale,
and normalizes float32 pixels to [-1, 1]. It rejects uniform images and excessive
aspect ratios. Browser Canvas high-quality interpolation differs from Pillow's
Lanczos used by the exploratory Python screen; actual browser results above
are measured separately. Initial same-tensor browser/native checks returned
identical transcriptions for both models.

Inference uses single-thread WASM with a `[1, 1, 64, width]` input. Greedy CTC
decoding considers the full published 8,210-character vocabulary, removes
adjacent repeated indices and CTC blank tokens, and retains the resulting text.
There is no digit-only whitelist, letter substitution, answer table or filename
lookup. Exactly one original ASCII digit is accepted as a prediction; other
outputs remain visible and unaccepted. No fake class scores or feature maps
are displayed. Exported records identify the model hash, pinned revision,
FP32 precision, preprocessing contract and full-charset CTC decoder.

## Validation and reproduction

From `dia2-local/`, with the local server on port 8782 and new report prefixes:

```powershell
.\.venv\Scripts\python.exe serve.py --port 8782
.\.venv\Scripts\python.exe -m digitlab.captcha_readers_qa --stage synthetic --report-prefix <new-synthetic-prefix>
.\.venv\Scripts\python.exe -m digitlab.captcha_readers_qa --stage download-smoke --report-prefix <new-download-prefix>
.\.venv\Scripts\python.exe -m digitlab.digit_readers_qa --report <new-ui-report.json>
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

`--cached-weights` intercepts only the model download URLs and supplies already
downloaded model files from ignored `artifacts/ddddocr-candidates/`; the worker
still verifies their SHA-256 and executes actual WASM inference. Without this
flag the collector exercises the real online downloads. Do not rerun the completed
official evaluation for tuning. The reusable `--stage challenge` collector refuses
remote website URLs and writes separate freezes, raw outputs and comparisons.

Local checks:

- [15 selector/interface groups](../reports/ddddocr-ui-20261016.json): PASS.
- Python unit suite, 28 tests: PASS.
- [Digit/letter regression](../reports/ddddocr-character-regression-20261016.json): PASS.
- [Words regression](../reports/ddddocr-words-regression-20261016.json): PASS.
- [Helper regression](../reports/ddddocr-helper-20261016-qa.json): PASS.

## Public deployment

v3.9.0 is live at [Digit Lab](https://naoquerosaber.pt/AI/). All eight changed
uploads were backed up and hash-verified, all 54 public assets matched local
hashes, and all 15 public selector/interface groups passed. Actual remote model
downloads and browser inference also passed for both models, each returning `0`
for one synthetic digit. No official CAPTCHA images were used on the public
origin. See [deployment and public checks](hosting.md#v390-captcha-specific-readers).
