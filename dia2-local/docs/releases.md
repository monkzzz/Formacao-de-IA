# Application releases

## v3.4.0 — Secret SNES arcade

- The Konami code opens an isolated EmulatorJS / Snes9x arcade and automatically
  starts the separately supplied Zelda ROM. A local ROM picker remains available.
- Closing the arcade stops emulation and restores keyboard focus. Emulator
  downloads begin only after unlocking the arcade.
- Original and serving ROM directories are excluded from Git; deployment transfers
  the serving copy separately. See [setup and validation](snes-arcade.md).

Local Edge checks verified the supplied ROM boots, creates a visible game canvas,
and stops on close. Extended gameplay and save persistence remain untested.

## v3.3.0 — Larger word evaluation and visible percentages

- Adds a third homepage benchmark: **67.89% word accuracy (1 − WER)** for Full
  precision on 1,000 real English IAM test lines, with 8,912 reference word tokens.
- Expandable, keyboard-accessible details show word error rate (32.11%), character
  error rate (9.60%), exact whole-line accuracy (15.30%), and the metric definition.
- Publishes a downloadable summary and keeps Scopedog's explanation consistent
  with the displayed values. Digit/letter scores and inference remain unchanged.

The [frozen larger evaluation](words-large-evaluation.md) excludes all 16 earlier
test rows and performs no training or model selection. This is English line OCR;
the word percentage is not an isolated-word classification score. The evaluated
reader is from v3.2.0; byte-identical inference sources are retained in v3.3.0.

This release is live. All eight [local display checks](../reports/release-3.3.0-local-final-metrics-qa.json),
all eight [public display checks](../reports/release-3.3.0-public-metrics-qa.json),
all six [public helper groups](../reports/release-3.3.0-public-helper-qa.json), and
[all 31 public asset hashes](../reports/release-3.3.0-http-assets.json) passed.
The recorded 1,000 predictions and edit counts were independently checked against
the frozen source manifest before publication.

## v3.2.0 — Eraser, drawing history and full-precision words

- Adds a paint-style square eraser, adjustable size and cursor, Pen selection,
  and Undo/Redo for Digits, Letters and Words. Clear can also be undone.
- Supports Ctrl+Z, Ctrl+Shift+Z and Ctrl+Y while the canvas is focused. Editing
  clears stale predictions; loaded word images can be edited without disappearing.
- Defaults Words to full FP32 weights, with compact INT8 Standard mode available
  for smaller downloads and lower memory use. The pretrained model identity is
  unchanged; this project did not train or fine-tune the word reader.
- Records profile, weight precision and decoding alongside model and release
  identity. Leaving Words releases the model worker.

The [precision study](word-precision.md) records both unsuccessful candidates and
the selected full-precision comparison. Eight fresh English lines had 4.44%
character error versus 9.17% for compact weights; synthetic single-word results
did not improve. These small samples do not establish general accuracy.

All 19 [local browser groups](../reports/release-3.2.0-local-qa.json), the
[local character regression](../reports/release-3.2.0-local-character-qa.json),
all six [local helper groups](../reports/release-3.2.0-local-helper-qa.json), and
all 16 Python unit tests passed. Public deployment evidence is recorded separately.

This release is live. The [final public UI checks](../reports/release-3.2.0-final-public-ui-qa.json),
[both real reading profiles](../reports/release-3.2.0-public-qa.json),
[character regression](../reports/release-3.2.0-public-character-qa.json),
[helper regression](../reports/release-3.2.0-public-helper-qa.json), and
[all 30 final asset hashes](../reports/release-3.2.0-final-http-assets.json) passed.
The final UI check explicitly verifies that full precision is the default.

## v3.1.0 — Words and release tracking

- Adds Words mode for transcribing one word or a short English handwriting line.
- Supports drawing, cropped image upload, editable text, original transcription,
  copy, text download, cancellation and retry.
- Runs the separate pretrained TrOCR Small model in a browser worker, with lazy
  downloads. See [model identity, limitations and validation](words.md).
- Displays `v3.1.0` in the footer, including while models are loading.
- Records `application_version` in character JSON exports, Words result metadata,
  and deployment reports.

The displayed version identifies the application release; model hashes identify
weights, and preprocessing versions identify the input contract. These identifiers
serve different purposes. Earlier application releases did not display a release
number in the footer; their existing reports retain their original identities.

See [hosting evidence](hosting.md#words-release) for public deployment status.

Release 3.1.0 was deployed and verified. All 15
[local browser groups](../reports/release-3.1.0-local-qa.json) and all 15
[public browser groups](../reports/release-3.1.0-public-qa.json) passed, including
matching visible/exported versions and real handwriting recognition. The
[public character regression](../reports/release-3.1.0-character-qa.json) passed
all 36 uploads and activation parity. All 29 deployed assets passed
[FTPS verification](../reports/release-3.1.0-ftp-deployment.json) and independent
[HTTPS hash checks](../reports/release-3.1.0-http-assets.json). Older Words release
reports remain evidence for the original deployment before the visible version
was added.

## Updating the version

Use major/minor/patch numbering for incompatible changes, features and fixes.
Update the `#app-version` text in `dist/index.html`, the release entry here, and
the version shown in the README and hosting guide. Browser code reads the footer
text as its version source, so export metadata follows automatically.

Bump URL query versions for any changed scripts or styles, including module
imports. Verify the visible footer and exported metadata with `digitlab.words_qa`.
Record each deployment and check in new report destinations, preserving previous
release evidence.
