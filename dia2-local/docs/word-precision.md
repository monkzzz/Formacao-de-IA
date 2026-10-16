# Word recognition precision study

This page preserves the small experiments used to select the reader. The current
website word percentage comes from the later
[1,000-line frozen evaluation](words-large-evaluation.md), using the same released
reader without further tuning. Do not substitute these older eight-line scores
for the larger result.

Words uses Microsoft's pretrained TrOCR Small through Xenova's browser conversion.
**This project did not train or fine-tune the word model.** The digit and individual
letter CNNs were trained locally, independently of this optional reader.

## Selection and separate evaluation

Release 3.1.0 used compact INT8 weights and greedy decoding. We compared
alternatives in the actual browser runtime, keeping the model revision and
Transformers.js version pinned. No challenge images, manually corrected
predictions or answer tables were used in inference. Labels were used only for
computing errors after each pixel-based prediction.

An initial experiment compared compact Small/Base models, a three-beam decoder
and a direct-upload preparation path. Its selected candidate improved on eight
adjacent validation lines but worsened on eight separate test lines. The
[selection](../reports/words-precision-selection.json),
[test](../reports/words-precision-test.json) and
[rejection](../reports/words-precision-decision.json) remain recorded. That
candidate was not adopted. The larger Base candidate also performed worse in
the development comparison; size alone did not justify replacing the reader.

The second study sampled eight validation rows at offsets 0, 100, …, 700 from
[Teklia/IAM-line](https://huggingface.co/datasets/Teklia/IAM-line), and compared the
existing compact model, three-beam decoding with unchanged preparation, and the
same Small model with full FP32 weights and greedy decoding. Full precision had
the lowest character error. It was
[frozen before the fresh test](../reports/words-fp32-selection.json), which used
test rows 50, 150, …, 750. The first test sample was not reused for this decision.

| Eight fresh English handwritten test lines | Standard INT8 | Full FP32 |
| --- | ---: | ---: |
| Character error rate, case-sensitive | 9.17% | **4.44%** |
| Word error rate, case-sensitive | 23.68% | **17.11%** |
| Exact complete-line matches | 1/8 | 1/8 |
| Mean inference time on the test machine, excluding model loading | 1.01 s | 1.18 s |

See the [diverse validation comparison](../reports/words-precision-diverse-validation.json)
and [fresh test outputs](../reports/words-fp32-fresh-test.json). Rates use total
Levenshtein edits divided by reference characters or whitespace-separated words.
Case and punctuation/spacing errors count. Word errors are not correctness
probabilities. Inference time is machine-specific.

The [acceptance decision](../reports/words-fp32-decision.json) records the release
choice and its limited scope. Public inference and editing checks are linked in
the [hosting record](hosting.md#current-release-v320).

Eight additional synthetic words, rendered using Segoe Print, were checked
separately in each comparison. The fresh synthetic check had 5/8 exact matches
for both compact and full weights, with identical 5.66% character error. This
does **not** show an improvement for isolated words. Synthetic font rendering
does not represent arbitrary mouse, touch or cursive handwriting.

This is a small engineering comparison, not the full official IAM benchmark,
an independent audit of the pretrained model's training data, or a guarantee for
the user's handwriting. It does not establish Portuguese or multilingual
performance. Exact-line matches remained unchanged, and recognition still needs
review. No further model/preprocessing tuning used the fresh test results.

## Release behavior

Release 3.2.0 defaults to **Full precision**, with **Standard** available for lower
download and memory requirements. They use the same model/revision and greedy
decoding; the profile determines whether the runtime requests the compact or full
graphs. Upload preparation remains the original display-canvas path because the
direct-input candidate did not generalize in the first comparison.

The two full graphs total 246,543,658 bytes (about 247 MB, rounded to 250 MB in the
interface); the compact graphs total 63,610,555 bytes (rounded to 65 MB). Both need
additional runtime/configuration assets. Downloads are lazy and may be cached.
The quality selector discloses the tradeoff before loading, and download errors
suggest Standard on memory-constrained devices. Leaving Words terminates its
worker, releasing the loaded model. No image is submitted to a recognition API.

Result metadata identifies application version, profile, FP32/INT8 precision,
decoding, preprocessing and pretrained model revision. The original transcription
remains distinct from edits; no correction is used to retrain a model.

## Reproduction

Use the existing environment and local static server. Downloads of public IAM
examples and all generated font fixtures go into ignored `data/words-evaluation/`.
Reports retain source indices, labels, image hashes, raw predictions and metrics;
images and weights are not committed.

```powershell
.\.venv\Scripts\python.exe -m digitlab.words_benchmark --split validation --stride 100 --candidates small:1:legacy small:3:legacy small-fp32:1:legacy --report <new-validation-report.json>
.\.venv\Scripts\python.exe -m digitlab.words_benchmark --split test --offset 50 --stride 100 --candidates small:1:legacy small-fp32:1:legacy --report <new-reproduction-report.json>
```

Reproducing the same indices is a regression check; it is not another fresh test.
The benchmark refuses an existing report path. Preserve unsuccessful comparisons
and record any subsequent selection separately.
