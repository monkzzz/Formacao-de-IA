# Classifier submission specification proposal

Version 1.0.0, prepared 2026-10-17. Status: **preservation scope confirmed by participant**.
This reconciles existing implementation evidence retrospectively; it is not a
pre-implementation design or approval record. Source baseline: `4342c32`.

## Scope and inputs

Retain [Digit Lab](../../dia2-local/README.md) in the personal repository
`monkzzz/Formacao-de-IA`. Complete the digit classifier submission, evidence and
submission preparation rather than building another application or retraining. English and
the current assistant follow the participant's existing decisions. Letters, Words
and pretrained OCR readers are optional extensions, separate from the trained CNN.

The course input is MNIST IDX images/labels; the browser accepts drawing and local
image uploads representing one digit. The selected model receives a 64×64 grayscale
tensor prepared by `border-gray-bilinear-com-64-v1`, and returns ten logits/scores
for 0–9. Treat softmax values as model scores, not calibrated correctness
probabilities. Multi-digit transcription is outside the core deliverable.

## Architecture, resources and selection

| Alternative | Tradeoff | Proposed submission treatment |
| --- | --- | --- |
| Flattened-image MLP | Simple browser export; lacks convolutional spatial bias | Explain as an alternative, no new experiment required |
| Existing plain convolutional baseline | Smaller and simpler than residual candidate | Preserve historical baseline and its separate results |
| Existing `captcha-v3` residual CNN | 272,618 parameters; selected with recorded development gates | Retain already frozen candidate; no new architecture selection |

The selected architecture is `residual64-16-32-128`: convolutions, pooling,
bottleneck residual blocks, Dense128 and ten outputs, with dropout 0.25 during
training. The [manifest](../../dia2-local/dist/model/captcha-v3/digits/manifest.json)
defines tensor order and shapes. Float32 little-endian weights occupy 1,090,472
bytes; SHA-256 `d962c7f1aefd4f86cf9fcc621e30a1e8fbbce092c5a47ab3dd88e0f64573b42c`.
Weights remain ignored artifacts; their availability needs a separate verified
artifact process, not a promise that cloning source supplies them.

Historical [protocol](../../dia2-local/docs/residual-training.md): four CPU threads,
deterministic PyTorch, 12 epochs, seed 20261123, AdamW 0.0003, weight decay 0.0001,
batch 128 and cosine decay to 0.00002. Each epoch mixes 40,000 new synthetic images
and 20,000 clean handwritten samples. No new compute expenditure or retraining is
requested. Physical-phone latency and a new training time budget remain unknown.

## Data, preprocessing and metrics

Preserve the original stratified 55,000/5,000 MNIST source split and existing
synthetic generation/font separation. Historical development uses 10,000 synthetic
samples, seed 20261124; the fresh synthetic test used 20,000, seed 20261125.
Development selected epoch 12 by minimum raw loss among candidates with ≥0.2
percentage-point raw improvement and ≤0.1-point clean degradation. Preserve the
[archived selection](../../dia2-local/reports/captcha-v3-development-selection.json).
The canonical MNIST test has been exposed in prior experiments, and later official
challenge runs are follow-ups; neither can be described as a new blind evaluation.

Report clean accuracy, raw synthetic accuracy, cross-entropy, confusion/error
analysis and historical test identities separately. Recorded candidate results
are 99.10% clean MNIST and 98.73% raw synthetic accuracy; 10/10 official cases is a
separate follow-up, not population CAPTCHA accuracy. Original 99.28% / 2-of-10
records retain their original identity. Do not rerun or tune on the ten official
images, labels, filenames or completed evaluation caches to improve the score.

Python and JavaScript must use the same grayscale, border/background treatment,
resampling, centering and input dimensions. Follow the versioned implementation
and parity fixtures rather than inventing a replacement preprocessing pipeline.

## Export, browser and interface acceptance

Export actual trained tensors using manifest offsets, sizes and hashes. Verify
Python/JavaScript logits, hidden units and both feature layers within 0.0001.
Historical Edge p95 gate is below 150ms; repeat only in a separately named
verification record, and do not infer physical-phone performance from desktop.

The static application must classify in-browser, with no remote inference API;
network downloads for static assets/optional weights are distinct from uploading
images. Require mouse/touch drawing, individual and batch uploads, clear/reset,
per-image scores, real activations, prediction export and visible failure recovery.
Check dimensions, invalid input and unavailable weight handling. Keep the trained
CNN default and identify optional pretrained readers explicitly.

## Publication and evidence

The participant explicitly instructed: “the current development of dia 2 local
that is o websitw maintain it”. Preserve the existing development and website at
`https://naoquerosaber.pt/AI/`. Do not migrate, replace, retrain or publish changes
as part of this batch. Current live behavior still needs fresh verification;
historical reports do not prove the present production state. GitHub Pages is a
course requirement with an instructor-substitution decision pending, rather than
an authorized migration. The previously planned Pages destination remains a
historical preparation choice, superseded for this batch by the participant's
preservation instruction.

Acceptance requires a model evidence index, fresh relevant tests, artifact hashes,
browser parity/interface checks, submitted URL/release identity and links to real
Issues. Preserve frozen outputs and record subsequent checks under new filenames.
The [Issue plan](issue-plan.json) separates remaining work and dependencies.

## Approval and process limits

The participant's direct preservation instruction confirms the existing-project
scope after the context proposal was presented in this conversation. It does not
approve a new architecture, retraining, migration, production changes or publication.
Technical details above reconcile observed implementation with that limited
scope; they are not claims of participant review of every historical experiment.
This retrospective instruction cannot establish that original implementation followed
an approved pre-implementation plan. No original approval trail has been found in
the inspected local documents; the public Issue audit found no Issues. Instructor
acceptance of the assistant substitution, personal fork layout, retrospective
planning and any hosting substitution is unconfirmed. See the
[prepared request](instructor-process-request.md).
