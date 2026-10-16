# CAPTCHA Digits: single-digit classifier (v3.10.0)

The **CAPTCHA Digits** selector option uses pretrained DdddOCR Legacy weights
with a separate classifier designed for an image containing exactly one digit.
Its frozen official follow-up scored **10/10**, compared with 9/10 for the
unrestricted text decoder using the same weights. This is a new inference
configuration, not newly trained or larger weights. The original CNN and all
previous external reader configurations remain available and unchanged.

## Independent selection and results

The experiment was defined before reading any official images under this new
configuration. Development compared exact single-digit CTC scores from the two
pretrained models and mixtures with current-model weights 0, 0.25, 0.5, 0.75 and
1. Selection maximized development accuracy, then minimized conditional log
loss, then favored equal weighting. The 1,000-image development set selected
**Legacy alone**, so no ensemble or additional weight download is used.

The separate native test used a different seed and font list. The actual browser
then ran a third, fresh 1,000-image set. Each set balanced 500 clean images with
500 images with stronger synthetic interference. These are independently
generated samples, not collected real CAPTCHA population data; the training
exposure of external models is not known.

| Evaluation | Digit classifier | Unrestricted Legacy text |
| --- | ---: | ---: |
| Native development, 1,000 images | 1,000/1,000 | 980/1,000 |
| Separate native test, 1,000 images | 1,000/1,000 | 970/1,000 |
| Fresh actual browser test, 1,000 images | **999/1,000** | 978/1,000 |
| Frozen official follow-up, ten images | **10/10** | 9/10 in its earlier frozen follow-up |

The browser test's unrestricted count is calculated from the original
transcriptions retained alongside the classified outputs on those same images.
Browser and native conditional scores on identical prepared input matched within
`1.65e-7`; a separate generated-image smoke test matched within `1.50e-6`.
The real white-on-dark drawing smoke test recognized a generated `7` correctly.

Evidence:

- [Predefined protocol](../reports/ctc-digits-v1-protocol.json),
  [development selection](../reports/ctc-digits-v1-selection.json),
  [development results](../reports/ctc-digits-v1-development.json),
  [separate native test](../reports/ctc-digits-v1-test.json).
- [Fresh browser test](../reports/ctc-digits-v1-browser-test.json),
  [raw scores, unrestricted text and parity](../reports/ctc-digits-v1-browser-test-captcha-digits-raw.json).
- [Runtime and actual drawing smoke](../reports/ctc-digits-v1-local-runtime-smoke-captcha-digits-raw.json).
- [Official follow-up freeze](../reports/ctc-digits-v1-frozen-challenge-freeze.json),
  [raw predictions](../reports/ctc-digits-v1-frozen-challenge-captcha-digits-raw.json),
  [comparison](../reports/ctc-digits-v1-frozen-challenge.json).

The new configuration, runtime sources and character tables were frozen before
the official follow-up. All ten raw outputs were durably saved before consulting
the historical labels. The official images and earlier outcomes were already
known, so 10/10 is a follow-up result, not a new blind benchmark or a guarantee of
perfect CAPTCHA recognition. No weights, preprocessing, classifier or default
selection changed after the result. Official images stayed in the local browser;
requests were GET-only with no bodies. Historical reports remain intact.

## What changed mathematically

The general reader chooses the most likely character at each timestep and
collapses the resulting CTC sequence into arbitrary text. CAPTCHA Digits instead
calculates the total CTC likelihood of each complete one-digit target, summing
every valid alignment. It then normalizes those ten target likelihoods and
selects the highest. This uses the model's raw logits directly; no transcription
substitutions, digit extraction, filename lookup, generator labels or answer
table are used. [PyTorch's CTC reference](https://docs.pytorch.org/docs/stable/generated/torch.nn.CTCLoss.html)
provides an independent numerical check of the alignment calculation.

For each target there are three forward states: blank before the character,
emitting the character, and blank after it. Once the path enters the final blank
state it cannot emit the character again, because that would represent a
two-character target. Computation uses log-space alignment sums. The common
full-vocabulary softmax denominator cancels during conditional normalization;
it does not change the ranking or the ten reported scores.

The conditional scores assume that the input contains **one of 0–9**. They are
not calibrated probabilities of correctness, and can be high for inappropriate
inputs. The original unrestricted transcription is preserved separately in the
interface and export. Thus a classified digit may differ from the displayed
unrestricted transcription without the transcription being edited.

## Model identity and interface

- Weights: `sml2h3/ddddocr/common_old.onnx`, 13,606,051 bytes, FP32.
- Source revision: `c40f56f95412e10bcb9bd0bd24411e92f896d238`.
- SHA-256: `b8f2ad9cbc1f2e3922a6cb9459e30824e7e2467f3fb4fd61420640e34ea0bf68`.
- Character table and MIT attribution: unchanged from [the DdddOCR release](captcha-readers.md).
- Input: unchanged `ddddocr-browser64-v1`, grayscale 64px height with preserved
  aspect ratio, normalized to [-1, 1].
- Configuration: `ctc-digits-v1`; decoding: `exact-single-digit-ctc-v1`.
- Runtime: pinned ONNX Runtime Web `1.20.1`, single-thread WASM inside a worker.

The first read downloads about 14 MB plus the runtime. Weights are verified
before use; browser caching is best-effort. Images remain on-device. The
precision selector is hidden because these weights are fixed FP32. The existing
project CNN remains the default. Earlier general OCR options retain their strict
original-text acceptance and null class scores.

New exports include the chosen digit, ten conditional scores, unchanged
`raw_text`, weight hash, configuration, decoding identity and explicit
`output_constraint` / `score_scope`. CNN activation displays remain specific to
the CNN modes; this option does not fabricate feature maps.

## Reproduction and checks

Optional native experiments/parity need `requirements-ctc-experiment.txt` in
addition to the normal project dependencies. Missing pinned model files can be
restored into ignored artifacts with:

```powershell
.\.venv\Scripts\python.exe -m digitlab.ctc_digits --restore-weights
```

The completed native stages refuse to overwrite their protocol or results. For
new browser synthetic checks, start `serve.py --port 8782` and use new report
prefixes:

```powershell
.\.venv\Scripts\python.exe -m digitlab.captcha_readers_qa --stage synthetic --readers captcha-digits --count 1000 --seed <new-seed> --noise 4 --native-parity --report-prefix <new-prefix>
.\.venv\Scripts\python.exe -m digitlab.digit_readers_qa --report <new-ui-report.json>
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Use `--cached-weights` only when supplying previously downloaded verified bytes
for integration checks; otherwise the actual online model download is exercised.
Do not rerun the completed official follow-up to tune this configuration.

Validation:

- Python suite: **30 tests PASS**, including comparison with PyTorch CTC loss
  and invariance to arbitrary full-vocabulary competitors and per-frame offsets.
- [16 browser interface groups](../reports/ctc-digits-v1-ui.json): PASS, including
  distinct classified digit versus unrestricted text and correctly scoped scores.
- [Existing digit/letter parity and 36 uploads](../reports/ctc-digits-v1-character-qa.json): PASS.
- [Words regression, 19 groups](../reports/ctc-digits-v1-words-qa.json): PASS.
- [Helper regression, 6 groups](../reports/ctc-digits-v1-helper-qa.json): PASS.

Two initial parallel browser runs timed out before application readiness.
Words and helper passed when rerun individually without source changes.

## Public release

v3.10.0 is published at [Digit Lab](https://naoquerosaber.pt/AI/). All seven
changed uploads and all 55 public asset hashes passed verification. The actual
online weight download, a generated synthetic upload, white-on-dark drawing
and conditional-score parity passed on the public origin. The public score
delta was `1.50e-6`. All 16 public interface groups passed. No official images
were used in that public smoke check.
See [deployment and public evidence](hosting.md#v3100-single-digit-classifier).
