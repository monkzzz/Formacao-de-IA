# Submission containing only participant-trained models

The participant clarified that the professor does not accept downloaded pretrained
models. Supplementary training data remain acceptable as separately documented
extensions. This package therefore excludes all pretrained digit and word readers,
their runtimes and remote model loaders. It preserves the existing website and
historical experiments without deploying anything.

## Deliverable

The v1 deliverable below remains frozen. Maintained source templates now support
readable shared browser utilities and model-load recovery. For a new local package,
use a distinct `--name`, a matching QA `--build` receipt and fresh screenshot/report
destinations; see [the release workflow](deployment.md). The default historical
name deliberately refuses an existing v1 artifact. Editing templates does not
update either public site.

The prepared local archive is
`artifacts/self-trained-submission-v1/self-trained-submission-v1.zip`.
The extracted/static site is `artifacts/self-trained-submission-v1/site/`.
Both include the trained weight files; they are ignored binary artifacts and are
not committed to Git. Do not submit only the source templates without the weights.
The [build receipt](../reports/self-trained-submission-v1-build.json) records every
file hash and the ZIP hash. [Validation](../reports/self-trained-submission-v1-validation.json)
records what actually passed.

The default is **MNIST only · required course model**. The selector also offers:

| Option | Weight origin | Recorded digit CAPTCHA result |
| --- | --- | --- |
| MNIST only | Random initialization, local MNIST training | 2/10 correct; 0/10 correct with score >90% |
| MNIST + EMNIST/synthetic | Further local training from our MNIST model | 5/10; 1/10 above 90% |
| Preserved residual extension | Our MNIST → robustness → synthetic → high-resolution → residual training chain | 10/10; 6/10 above 90% |
| Letters | Random initialization on EMNIST Letters, then local robustness training | Separate task; digit CAPTCHA score does not apply |

To inspect the strongest self-trained digit model, select **MNIST + synthetic ·
preserved residual extension**. Supplementary models are not represented as
MNIST-only work. The interface displays each selected model's own dataset scope,
recorded clean accuracy and historical challenge counts. No new official CAPTCHA
inference was needed to assemble or verify this version. The professor's all-ten
strictly-above-90% criterion remains unmet.

## Run on Windows or Linux

Extract the ZIP into a new folder and serve it with standard Python:

```text
python -m http.server 8765 --bind 127.0.0.1 --directory <extracted-folder>
```

Open `http://127.0.0.1:8765/`. Opening the HTML directly as a `file:` URL does not
provide the browser origin required for verified model loading. No training
runtime, GPU, model hub, API key or internet model download is required to run
the extracted package. The browser reads the bundled project-trained weights
from this local server; images are processed in the browser, not on the server.

To build from the repository, first use the [portable runtime](../../PORTABILITY.md),
then run from `dia2-local/`:

```text
<python> -m digitlab.self_trained_submission
<python> -m digitlab.self_trained_submission_qa --report reports/<new-report-name>.json
```

The builder requires the original local training checkpoints and verified
exported weights; it does not download missing models or retrain silently. It
refuses an existing destination/receipt. Preserve this completed package; a later
release needs a distinct identity and new evidence. Source templates live in
`submission/`; browser inference/preprocessing/activation code is copied unchanged
from the existing project. No preload, worker or hidden OCR route is included.

## Training provenance and verification limits

The builder verifies every exported tensor against the corresponding local
checkpoint, and the recorded parent checkpoint hashes through the digit and
letter training chains. It records root random initialization, training source
hashes and report identities. This is an audit of source code, local checkpoints
and recorded history, not independent proof of authorship or teacher approval.
MNIST and EMNIST are datasets; downloading data is distinct from importing
pretrained model weights. No pretrained initialization is used in these chains.

Browser verification covered four models, forty uploads, Python/JavaScript input
and score parity, actual intermediate activations, drawing, blank rejection,
undo/redo, invalid files, filename independence, raw JSON downloads and mobile
layout. Third-party requests were blocked and none were attempted. Loaded
inference also worked after all subsequent requests were blocked. The test does
not claim that a page can cold-start when its local server is unavailable.

The first collector failed because its string-based wait conflicted with the
strict Content Security Policy. The [failed report](../reports/self-trained-submission-v1-browser.json)
is preserved. Only collector polling changed; the exact same site/ZIP passed the
[subsequent browser run](../reports/self-trained-submission-v1-browser-retry.json).
The coding agent inspected the desktop/mobile screenshots. Independent human
review, a fresh Windows run, teacher acceptance and deployment are NOT RUN.

## Subsequently requested official rerun

After the package was built and verified, the participant explicitly requested a new run of the official ten. The unchanged package was served locally, the preserved residual extension was selected through its UI, and all ten raw browser predictions were saved before a separate label comparison. **10/10 were correct; 6/10 were correct with original scores strictly >90%.** The requirement remains unmet. Python prepared inputs and predictions matched the browser, and the package, ZIP and original active assets retained their hashes. [Separate rerun evidence](../reports/self-trained-submission-v1-challenge-rerun-v1-summary.md). Earlier NOT RUN receipts retain their original build/QA scope. No training, tuning, publication or default-model change followed.

## Subsequent GitHub Pages deployment

The participant subsequently requested publication on GitHub Pages. The [live participant-trained site](https://monkzzz.github.io/Formacao-de-IA/) now serves this exact package; [deployment and live verification](self-trained-pages.md) passed all 22 public asset hashes, four-model parity and forty non-challenge uploads. The separate original website remains unchanged. This supersedes earlier NOT RUN deployment statements for the later publication phase only.
