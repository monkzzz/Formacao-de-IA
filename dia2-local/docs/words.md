# Words mode

Words adds a separate browser handwriting transcription pipeline alongside the
existing Digits and Letters modes. It accepts a canvas drawing or one cropped
image containing a word or short English line. Results are editable and can be
copied or downloaded as UTF-8 text. The raw model transcription remains separate
from corrections; neither corrections nor drawings retrain a model.

## Model and runtime

- Original model: [Microsoft TrOCR Small, fine-tuned on IAM](https://huggingface.co/microsoft/trocr-small-handwritten).
- Browser weights: [Xenova/trocr-small-handwritten](https://huggingface.co/Xenova/trocr-small-handwritten),
  pinned to revision `2432e24d184b1d964d07ed04f5d9e21d31a59141`.
- Runtime: Transformers.js `2.17.2`, loaded from jsDelivr in a module worker.
- Inference: quantized ONNX, single-thread WebAssembly, greedy decoding with a
  64-token output limit. It does not require WebGPU or special isolation headers.
- The two quantized graphs total 63,610,555 bytes (about 64 MB), plus runtime and
  tokenizer/configuration downloads. UI copy rounds the model size to 65 MB.

The [model card](https://huggingface.co/microsoft/trocr-small-handwritten) describes
single-text-line OCR; this release does not segment pages or multiple lines.
Its English handwriting training does not establish multilingual performance.
Do not apply the MNIST/EMNIST metrics to this model. A word accuracy benchmark and
teacher review are **NOT RUN**. Public deployment and browser verification passed;
see [the hosting record](hosting.md#words-release).

## Implementation

`dist/v3/words.js` owns the wider canvas, uploads, input preparation, worker
lifecycle and text controls. Preparation composites transparency on white,
estimates background polarity from the border, crops foreground with padding,
converts to dark ink on white, and bounds the crop to 1400×320 before padding.
Unlike character inference, it preserves the word's spatial layout rather than
normalizing it to 28×28. Photographs should be cropped to a line on a broadly
uniform background. The prepared image is visible below the text.

`dist/v3/words-worker.js` loads the pinned image-to-text pipeline on the first
read. It reports download progress and performs recognition away from the UI
thread. Cancel and mode changes terminate active work; a 240-second timeout and
worker/download errors leave the mode usable for retry. Completed workers are
reused. No model is downloaded merely by opening Words mode.

Images and transcriptions stay on the device. External requests download static
runtime and model assets from jsDelivr and Hugging Face; no recognition endpoint,
credentials or API keys are used. Browser caching is best-effort, so offline
availability is not guaranteed. Character modes still use their original local
verified models and real activations; those views are hidden in Words mode.
Word text downloads are separate from the character gallery's JSON export.

## Validation

Recorded local checks for this release:

| Check | Result | Evidence |
| --- | --- | --- |
| Words interface and real TrOCR smoke test, 14 groups | PASS | [Words release checks](../reports/words-release-qa.json) |
| Digit/letter parity, 36 uploads, mixed export, invalid inputs and frozen model preservation | PASS | [Character regression](../reports/words-character-regression.json) |
| Scopedog routing, keyboard/focus, safe rendering, live context and responsive layout, 6 groups | PASS | [Helper regression](../reports/words-helper-qa.json) |
| Python unit suite, 14 tests | PASS | `python -m unittest discover -s tests -v` |
| Relative documentation links and whitespace checks | PASS | Local checks |
| Word accuracy benchmark and teacher review | NOT RUN | No claims made |

The real model transcribed the publisher's example as `Mr. Brown commented icily.`,
matching the expected text. Requests observed during the checked workflows used
GET only; no image upload endpoint was called. Desktop and mobile screenshots
were captured and visually inspected. Earlier challenge and release evidence
was retained separately.

Public verification also passed all 14
[Words checks](../reports/public-words-release-qa.json), the
[digit/letter regression](../reports/public-words-character-regression.json), and
all six [helper groups](../reports/public-words-helper-qa.json). All 29 deployed
files matched their recorded hashes over both FTPS and
[public HTTPS](../reports/public-words-http-assets.json). The real public model
returned the same expected transcription as the local smoke test. Separate
public screenshots were captured, and the live desktop result was visually
inspected. These are integration checks rather than an accuracy benchmark.

Start a separate local server:

```powershell
python serve.py --port 8770
```

Run browser UI checks without loading external model weights:

```powershell
.\.venv\Scripts\python.exe -m digitlab.words_qa --url http://127.0.0.1:8770/ --report words-ui-check.json
```

For a real-model smoke test, supply a non-challenge handwriting image:

```powershell
.\.venv\Scripts\python.exe -m digitlab.words_qa --url http://127.0.0.1:8770/ --live-image <handwriting-image.jpg> --expected-text "Mr. Brown commented icily." --report words-live-check.json
```

The example text above belongs to the public
[Transformers.js handwriting fixture](https://huggingface.co/datasets/Xenova/transformers.js-docs/resolve/main/handwriting.jpg).
Only use `--expected-text` when it matches the supplied image. This is a smoke
test, not an independent accuracy benchmark. Keep downloaded fixtures in ignored
local storage. The collector refuses to overwrite existing reports.

The collector distinguishes worker doubles used to test editing, safe text
rendering, copying, downloading and cancellation from real TrOCR recognition.
It also checks dark/light input parity, pointer drawing, invalid and blank
uploads, failed worker loading, model switching, helper guidance, keyboard access,
four viewport sizes, GET-only requests and digit/letter activation parity.
Screenshots are saved under ignored `reports/screenshots/words-*.png`.

The separate full character regression command supports a fresh report name:

```powershell
.\.venv\Scripts\python.exe -m digitlab.robust_qa --url http://127.0.0.1:8770/ --report words-character-regression.json
```

These example report names already have recorded evidence; choose unused names
for another run. The helper collector also accepts `--report-prefix` to preserve
its earlier report and screenshots.

## Hosting

Deploy `words.js`, `words-worker.js`, `words.css`, and the changed app/helper files
before switching `index.html`. The existing deployment utility discovers files
under `dist/` automatically. Host over HTTPS, or use loopback locally. A restrictive
Content Security Policy must permit same-origin module workers and the pinned
runtime/model download hosts, including Hugging Face's file-delivery redirects.
No new server endpoint or Python inference dependency is required.

Follow [the hosting guide](hosting.md) for subsequent deployments. Use new report
and screenshot names for each verification so the recorded local and public
release evidence remains intact.
