# Browser QA without replacing evidence

Run the full site with `serve.py` and use the platform-specific Day 2 interpreter
from [the runtime guide](../../PORTABILITY.md). Commands below assume
`dia2-local/` as the working directory. Each run needs a new report and screenshot
prefix. The maintained collectors preflight both before opening a browser.

```text
<python> -m digitlab.selectable_models_qa --url http://127.0.0.1:8765/ --report review-models.json --screenshot-prefix review-models
<python> -m digitlab.words_qa --url http://127.0.0.1:8765/ --digit-experiment mnist --report review-words.json --screenshot-prefix review-words
<python> -m digitlab.design_qa --url http://127.0.0.1:8765/ --report review-design.json --screenshot-prefix review-design
<python> -m digitlab.helper_qa --url http://127.0.0.1:8765/ --report-prefix review-helper
```

Reports normally go under `reports/`; screenshots go under `reports/screenshots/`
with the supplied prefix. Absolute report paths are supported. Helper keeps its
existing `--report-prefix` option, which chooses both `<prefix>-qa.json` and the
screenshot prefix. Design retains its historical defaults and `--public` switch;
fresh explicit destinations are recommended for local maintenance.

The submission collector uses the same output preflight, with `--build` selecting
a new package receipt and `--screenshot-prefix` separating its captures. See
[the deployment map](deployment.md) for build and verification commands. A report
and its screenshots belong to one source/package identity; do not overwrite them
after changing source. A failed run can leave screenshots, so its retry needs new
destinations too. Historical collectors retain their original release assumptions;
this shared contract applies to the five maintained commands listed here.

## What each check establishes

- Model-selector QA uses local checkpoints/exports and non-challenge fixtures. It
  verifies three digit CNNs, 30 uploads, activations, export identity, model-switch
  recovery and Letters/Words transitions.
- Words QA checks both canvases, pointer ownership, pixel-exact undo/redo, keyboard
  tools, local digit/letter activation parity, OCR plumbing, cancellation and
  edited text exports. Default OCR UI checks use an identified worker double.
  Actual pretrained TrOCR inference is NOT RUN unless `--live-image` is supplied;
  a single live smoke test is not a word-accuracy benchmark.
- Design QA checks keyboard navigation, gallery containment, viewport layouts,
  touch-target dimensions, contrast and reduced motion.
- Helper QA checks local authored responses, explicit fallback, safe text
  rendering, focus/navigation and prediction context. It does not test a chat API.
- Restricted submission QA checks the receipt/ZIP, four model identities and
  activations, 40 uploads, filename independence, downloads and local-only requests.

Read each report's actual statuses. A captured screenshot is not a human review;
record visual inspection separately. Linux Chromium execution does not establish
Windows execution. No maintained QA command needs official CAPTCHA inputs or
updates a completed evaluation. Credentials and remote deployment are separate.

The optional digit-reader collector also accepts `--digit-experiment mnist` for
the current default. Add `--live` to execute actual printed/handwritten Standard
OCR models; without it, reader UI checks use an identified worker double. Use a
fresh required `--report` filename. See the
[3.11.1 public verification](release-3.11.1.md) for executed commands' scope,
real-model smoke results and preserved unsuccessful attempts.
