# Participant-trained submission published on GitHub Pages

The participant requested this Pages update on 2026-10-18 after clarifying that
downloaded pretrained models are excluded from the submission.

Live site: [Digit Lab — participant-trained submission](https://monkzzz.github.io/Formacao-de-IA/).
The [deployment run](https://github.com/monkzzz/Formacao-de-IA/actions/runs/39120676960)
completed successfully at source commit `3e69e8e839d1eb8691de9d19b9fea0189501b3ed`.
This supersedes the older Pages site's optional pretrained readers. The separate
`naoquerosaber.pt/AI/` website and local `dist/` remain unchanged.

## What is published

The exact reviewed [participant-trained package](self-trained-submission.md) is
published: MNIST-only course model by default, two separately labelled locally
trained digit extensions, and the locally trained EMNIST letter model. There are
no pretrained digit/word readers, remote model loaders, model hub/CDN runtimes,
datasets, checkpoints, credentials or arcade ROMs in the artifact.

To inspect the best recorded self-trained CAPTCHA result, select **MNIST +
synthetic · preserved residual extension**. Its preserved local official rerun
scored **10/10 correct**, with **6/10 correct and original score strictly >90%**.
The MNIST-only default has its separate recorded 2/10 result. These measurements
are not new live CAPTCHA evaluations, and the professor's full confidence target
remains unmet.

## Deployment integrity

Weights remain outside Git. The reviewed ZIP is stored as a
[GitHub release deployment asset](https://github.com/monkzzz/Formacao-de-IA/releases/tag/self-trained-submission-v1).
The manual [Pages workflow](../../.github/workflows/digit-lab-pages.yml) downloads
our own archive, not a third-party pretrained model. The
[restricted builder](../../participant-work/day2/build-restricted-pages.py)
checks the committed ZIP hash, exact file list, all 22 file hashes and four model
manifest/weight identities before assembling the Pages artifact. A tampered ZIP
was rejected locally before extraction. The original general builder remains
available as historical tooling but is no longer used by this workflow.

The browser reads our bundled weights from the Pages origin; inference stays in
the browser. The Content Security Policy restricts scripts and connections to
the same origin. The default remains MNIST-only rather than silently substituting
a supplementary model for the required exercise.

## Actual verification

- [Deployment job receipt](../reports/self-trained-pages-v1-deployment.json): build and deploy succeeded.
- [Release asset metadata](../reports/self-trained-pages-v1-release.json).
- [Public asset verification](../reports/self-trained-pages-v1-public-assets.json): all 22 hashes, JavaScript MIME types, source commit and archive identity matched.
- [Public browser checks](../reports/self-trained-pages-v1-browser.json): four models, forty non-challenge uploads, Python/JavaScript input/score parity, real logits/feature activations, drawing, undo/redo, blank and invalid files, filename independence, raw JSON downloads and mobile layout passed. No third-party requests were attempted. Loaded inference worked after blocking subsequent requests.
- [Separate existing-site snapshot](../reports/self-trained-pages-v1-preserved-origin-before.json): fresh entry-page, app-module and residual-weight hashes matched after deployment; no writes occurred there.

The coding agent inspected the public desktop screenshot. Automated mobile layout
checks passed; independent human review and fresh Windows execution are NOT RUN.
**Official CAPTCHA uploads on the public origin: NOT RUN.** No training, tuning,
model reselection or new accuracy claim accompanied deployment. Historical reports
retain their original scope, including earlier NOT RUN deployment statements.

The workflow stays manual. To publish a future version, first prepare and verify
a separately named package, create its deployment asset, and update the pinned
tag and build receipt. Do not overwrite the frozen v1 archive or use challenge
outcomes to choose a new model.
