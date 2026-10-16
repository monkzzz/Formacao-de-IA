# Larger word-recognition evaluation

This evaluation measures the released Full precision word reader on 1,000 real
English handwriting lines, containing 8,912 reference word tokens. The model and
preprocessing are frozen before inference; no training, model selection or tuning
uses these results. It replaces the eight-image synthetic check as the basis of
the website's word percentage.

## Recorded results

| Measurement | Result |
| --- | ---: |
| Real English handwriting lines | 1,000 |
| Reference word tokens | 8,912 |
| Word accuracy, `1 − WER` | **67.89%** |
| Word error rate | 32.11% |
| Character error rate | 9.60% |
| Exact whole-line accuracy | 15.30% (153/1,000) |

All 1,000 selected lines were processed. Word errors total 2,862 edits against
8,912 reference tokens; character errors total 4,155 edits against 43,259 reference
characters. This larger result is less optimistic than the earlier eight-line
FP32 comparison; no settings were changed to improve the reported score.

The [evaluation summary](../reports/words-1000-evaluation.json),
[raw model predictions and edit counts](../reports/words-1000-raw.jsonl), and
[downloadable website summary](../dist/evaluation/words-1000.json) identify the
sample, metrics and hashes. All raw reference hashes, image identities, word/
character edit counts and unique sample counts were audited against the ignored
manifest before publication. Earlier synthetic-word exact-match results are a
different metric on a different task and must not be compared as a before/after
accuracy change.

## Frozen source and sample

- Dataset: [TEKLIA IAM-line](https://huggingface.co/datasets/Teklia/IAM-line),
  revision `fbdad97500ce54635c0d1ba306bf535cb40656cf`, published test split.
- Population: 2,915 test lines; sample: 1,000, selected with seed `20261016`.
- All 16 line indices used in the previous small test comparisons are excluded.
- Original `data/test.parquet` is downloaded from the pinned source revision,
  verified against its source metadata checksum, and retained in ignored storage.
  The preview API proved unreliable, so it is not required for reproduction.
- Images and reference transcriptions remain in ignored `data/words-evaluation/`.
  Published evidence records row indices and hashes; it does not redistribute
  the source images or reference-label manifest.

The [frozen protocol](../reports/words-1000-protocol.json) identifies every selected
row, the original file hash, individual-image manifest hash, and browser inference
source hashes. It was written before the first prediction.

## Reader and execution

The reader is pretrained `Xenova/trocr-small-handwritten`, revision
`2432e24d184b1d964d07ed04f5d9e21d31a59141`, using full FP32 weights, greedy
decoding and Transformers.js 2.17.2. It is the Full precision reader released in
v3.2.0; the later metrics display does not change those inference sources.

Evaluation uses the real browser worker and the same upload preparation as the
application: crop and normalize the original image, draw it on the white
1000×300 canvas, and apply the final crop. Reference transcriptions stay in Python;
workers receive only image pixels and a completion identifier. No labels,
filenames or known answers guide the prediction.

Two persistent single-thread workers process the fixed sample. Every completed
prediction is appended to a resumable raw record. Empty recognition counts as
deletions. Infrastructure errors stop the run rather than dropping difficult
samples; resumption requires the same frozen source and manifest hashes.
Reported inference timing includes concurrent-worker load and is not a promise
of latency on another device.

## Metric definitions

Both reference and prediction have whitespace collapsed and trimmed. Case and
punctuation are preserved. Word tokens are separated by whitespace, including
standalone punctuation tokens in the published transcription.

- **Word error rate (WER):** total word insertions, deletions and substitutions
  divided by the total number of reference tokens.
- **Word accuracy:** `100 × (1 − WER)`. This is the website's primary word
  percentage. Insertions count against it; it is not the fraction of perfectly
  recognized lines or a correctness probability for an uploaded image.
- **Character error rate (CER):** total character edits divided by total
  reference characters after the same whitespace normalization.
- **Exact line accuracy:** the fraction of entire normalized transcriptions
  matching their references, including case and punctuation.

These units differ from single-image digit/letter classification accuracy. The
website must label the word percentage as `1 − WER`, identify Full precision and
the test sample size, and offer the other measured rates in expandable details.

The sample is substantially larger than the earlier experiments, but is still
English line OCR from one published dataset. It does not establish recognition
accuracy for Portuguese, arbitrary uploads, full pages or isolated-word crops.
It is not an independent audit of the pretrained model's training data.
Earlier small-sample reports and unsuccessful candidates remain unchanged.

## Reproduce or resume

Install the optional source-file reader in the existing environment:

```powershell
python -m pip --python .\.venv\Scripts\python.exe install -r requirements-evaluation.txt
```

Start `python serve.py --port 8770` separately. For a new named reproduction:

```powershell
.\.venv\Scripts\python.exe -m digitlab.words_evaluate --prepare --name words-1000-reproduction --count 1000
.\.venv\Scripts\python.exe -m digitlab.words_evaluate --run --name words-1000-reproduction
```

After interruption, use `--run --resume --name <same-name>`. A completed evaluation
cannot be overwritten. Rerunning the same sample is a reproduction, not another
fresh test. Use a separately specified sample/protocol for a new experiment and
record prior exposure to results.
