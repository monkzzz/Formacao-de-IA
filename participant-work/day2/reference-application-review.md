# R12: versioned reference application review

Reviewed 2026-10-17 at commit
[`99e495852d146a86e29e519a70b1679740d81111`](https://github.com/vcanonici/Image-classifier-demo/tree/99e495852d146a86e29e519a70b1679740d81111).
REST resolved the commit and a shallow clone in ignored
`dia2-local/.tmp/reference-app-review/` matched it. Source was read; no third-party
code, installers, model weights or deployment workflow was executed. This is a
retrospective review, not evidence of a review before the existing implementation.

| Component / inspected source | Observation | Participant decision |
| --- | --- | --- |
| [DrawingBoard.tsx](https://github.com/vcanonici/Image-classifier-demo/blob/99e495852d146a86e29e519a70b1679740d81111/apps/web/src/components/DrawingBoard.tsx) | Pointer capture, scaled canvas coordinates, clear, configurable brush and eraser feed actual image data to the app | Retain the principle of shared pointer handling and actual pixels; keep existing Digit Lab drawing tools |
| [ImageUpload.tsx](https://github.com/vcanonici/Image-classifier-demo/blob/99e495852d146a86e29e519a70b1679740d81111/apps/web/src/components/ImageUpload.tsx) | PNG/JPEG/WebP, multi-file handling, type/size/dimension checks, decode, blob previews with revocation, per-file failures, local pixel inference and inspectable results | Reuse design ideas, not source or arbitrary limits. Existing Digit Lab upload/error/export behavior is independently verified |
| [PredictionPanel.tsx](https://github.com/vcanonici/Image-classifier-demo/blob/99e495852d146a86e29e519a70b1679740d81111/apps/web/src/components/PredictionPanel.tsx) | Predicted class and ten softmax bars are derived from actual outputs | Keep Digit Lab's model-score wording; do not copy uncalibrated “confidence” wording |
| [preprocess.ts](https://github.com/vcanonici/Image-classifier-demo/blob/99e495852d146a86e29e519a70b1679740d81111/apps/web/src/preprocess.ts) | Drawing grayscale/crop/resize/centering; upload foreground masking estimates border color and handles alpha before the shared preparation path | Keep the selected model's frozen 64px contract; do not replace it with the reference's 28px implementation |
| [model.ts](https://github.com/vcanonici/Image-classifier-demo/blob/99e495852d146a86e29e519a70b1679740d81111/apps/web/src/model.ts) and [inference.ts](https://github.com/vcanonici/Image-classifier-demo/blob/99e495852d146a86e29e519a70b1679740d81111/apps/web/src/inference.ts) | Static artifact fetch, schema/tensor checks and checksum; dense/ReLU inference and stable softmax use numbers, not filenames | Retain model identity checks and browser-only inference. Reject its fixed 784–16–16–10 topology/JSON contract as a requirement for the residual CNN. Checksum verification skips when Web Crypto is absent, so do not assume all environments verify it |
| [NetworkDiagram.tsx](https://github.com/vcanonici/Image-classifier-demo/blob/99e495852d146a86e29e519a70b1679740d81111/apps/web/src/components/NetworkDiagram.tsx) | Hidden values and weight×activation contributions determine node/edge display; input contributions are ranked | Retain real values and labelled subsets. Keep existing CNN feature maps instead of copying a small dense-network drawing |
| [App.tsx](https://github.com/vcanonici/Image-classifier-demo/blob/99e495852d146a86e29e519a70b1679740d81111/apps/web/src/App.tsx) | Model readiness/failure state, drawing preprocessing and frame-budgeted inference, uploaded-result inspection | Retain separation of UI/model state; no framework migration or copied branding |
| [parity.test.ts](https://github.com/vcanonici/Image-classifier-demo/blob/99e495852d146a86e29e519a70b1679740d81111/apps/web/src/parity.test.ts), preprocessing tests and `tests/` | Exported Python fixtures compare hidden activations, logits and softmax to TypeScript; upload-mask tests include colored/light/dark/uniform inputs | Adopt intermediate-value checks and independent edge-case fixtures; existing selected-model Python/JS parity evidence remains separate |
| [training/export.py](https://github.com/vcanonici/Image-classifier-demo/blob/99e495852d146a86e29e519a70b1679740d81111/training/export.py) | Explicit artifact schema/topology/preprocessing/metrics and checksum are exported with trained values | Keep explicit contracts and genuine trained parameters; do not copy external weights |
| [ci.yml](https://github.com/vcanonici/Image-classifier-demo/blob/99e495852d146a86e29e519a70b1679740d81111/.github/workflows/ci.yml) | Frozen dependency installation, Python checks, web lint/test/build and browser interaction checks | Useful workflow structure; no participant CI pipeline is asserted or added by this review |
| [pages.yml](https://github.com/vcanonici/Image-classifier-demo/blob/99e495852d146a86e29e519a70b1679740d81111/.github/workflows/pages.yml) and `apps/web/vite.config.ts` | Build artifact separated from Pages deployment, explicit permissions/environment/concurrency, project-path base URL | Record the pattern for a future authorized Pages task; preserve the current host and do not enable Pages |

The reference uses an [MIT notice](https://github.com/vcanonici/Image-classifier-demo/blob/99e495852d146a86e29e519a70b1679740d81111/LICENSE).
This review credits its contributors and records conceptual adaptations; no code
or weights were copied into Digit Lab. Its external historical source and MNIST
terms remain separate from that notice. Existing participant attribution is in
[experiment provenance](../../dia2-local/docs/experiment.md#references-and-implementation-provenance).

The review supports design understanding, not a fresh runtime or accuracy test
of the reference application. The [participant's public browser checks](submission-browser-delivery.md)
are evidence for the participant site, not for this reference commit.
