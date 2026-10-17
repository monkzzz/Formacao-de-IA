# GitHub Pages publication

Published 2026-10-17 after the participant explicitly asked, “can do the github
pages task?”. This authorizes a separate Pages deployment while preserving the
existing development and external site. Earlier deferred-Pages statements describe
the prior scope and are superseded for this task.

Public application: [Digit Lab on GitHub Pages](https://monkzzz.github.io/Formacao-de-IA/).
Application v3.10.0 retains the participant-trained captcha-v3 residual CNN as
default. [Deployment run](https://github.com/monkzzz/Formacao-de-IA/actions/runs/39031154032)
completed successfully at source commit
`c144e551d760d0119e694048fe13906b69121a9f`; see [actual job receipt](pages-deployment-run.json).

## Build and preservation

[Manual workflow](../../.github/workflows/digit-lab-pages.yml) assembles a separate
temporary artifact from tracked static files. [Builder](build-pages.py) retrieves
all seven existing weight exports and verifies each byte count and manifest SHA-256
before publication. The site serves these weights locally on Pages; inference runs
in the browser. Weights remain outside Git. No datasets, checkpoints, secrets or
the separately supplied arcade ROM are published. Optional OCR downloads retain
their original behavior and were not exercised; the optional arcade has no bundled
ROM on Pages. This is not a change to the classifier or original development.

[Before](pages-before.json), [enabled settings](pages-enabled.json) and
[dispatch receipt](pages-dispatch.json) record the actual configuration. HTTPS is
enforced, `build_type` is `workflow`, and no custom domain is configured. The
workflow is manual so unrelated documentation commits do not redeploy the app.
To publish a future reviewed version, run **Publish Digit Lab to GitHub Pages**
from Actions. Existing frozen model identities remain the manifest authority.

The deployment approach follows GitHub's [custom workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
and [Pages API](https://docs.github.com/en/rest/pages/pages). The original
[external site](https://naoquerosaber.pt/AI/) was never written to; fresh checks
confirmed its entry page, app module and selected weights still match this local
development. No tracked `dia2-local` file changed in this task.

## Actual verification

- [Local subpath parity](pages-local-parity.json) passed before deployment.
- [Live Pages parity](pages-public-parity.json) passed real Python/JavaScript
  preprocessing, scores, logits and activation comparisons, 36 digit/letter
  uploads, mixed export, blank/corrupt input, failed-download recovery and mobile
  layout. Observed recognition requests are GETs under the Pages origin or blobs;
  no remote image inference API is used.
- [Live interactions and asset identities](pages-public-interactions-verified.json)
  passed all 55 asset hashes, JavaScript MIME types, default model, mouse drawing,
  eraser/undo/redo/clear, emulated touch classification, real feature maps and no
  page errors. The desktop screenshot was visually inspected. Screenshot path is
  recorded in that JSON and remains ignored locally.

The first asset-check attempt [failed](pages-public-interactions.json) because it
compared an LF Git blob with a CRLF working-tree text file. The verifier now checks
committed blobs for source assets and original local identities for weights. The
successful report preserves this distinction; the failed attempt remains intact.

The deployed selected weights match the frozen challenge model identity, and the
committed runtime/preprocessing are unchanged; existing parity fixtures reproduce
the model's real intermediate outputs on the new origin. This verifies deployment
integrity against the frozen evidence, not a new independent accuracy experiment.
The historical ten-image results remain in the [preserved challenge chain](submission-challenge-chain.md).
**Live official-image rerun: NOT RUN.** Automatic approval review rejected that
optional command because this request did not specifically authorize using the
evaluation images at the external Pages destination. No workaround was attempted;
the hash/parity and non-challenge checks above establish the Pages deliverable.
No new challenge score, training, tuning or original instructor approval is claimed.

Physical touchscreen testing, optional external readers and long-term archival
availability of checkpoints/fonts remain outside this verification. Teacher review
and process acceptance remain separate; publication satisfies the hosting target
without claiming acceptance of the original development chronology.
