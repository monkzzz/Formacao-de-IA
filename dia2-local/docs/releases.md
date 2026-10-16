# Application releases

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

Release 3.1.0 is deployed and verified. All 15
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
