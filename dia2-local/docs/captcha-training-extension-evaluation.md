# Evaluating the separate 64px training extension

The [training protocol](captcha-training-extension.md) was frozen before data
preparation and training. This companion describes the later evaluation commands;
it does not change that protocol or its eligibility thresholds.

Run from `dia2-local/` with the interpreter created by the
[Windows/Linux setup](../../PORTABILITY.md):

```text
<python> -m digitlab.captcha_extension_browser --stage export
<python> -m digitlab.captcha_extension_browser --stage qa
<python> -m digitlab.captcha_extension --stage test
```

Export requires a development-eligible frozen checkpoint. It creates an isolated
application in `.tmp/captcha-training-extension-v1-preview/`; it does not replace
the active application. Browser QA checks actual uploads, Python/JavaScript
preparation, scores, intermediate activations, inference speed and mode switching.
The test stage requires passing browser QA for the same checkpoint, checks source
pixel overlap, and then compares the candidate and preserved baseline. Completed
destinations cannot be overwritten. Do not rerun completed tests as new evidence.

Only if `independent_test_eligible` is true in the experiment report:

```text
<python> -m digitlab.captcha_extension_browser --stage official
<python> -m digitlab.captcha_extension_browser --stage compare
```

The first command freezes and records all ten official browser predictions before
the separate label comparison. Acceptance requires exactly ten correct and every
original, unrounded score strictly greater than 90%. This is a follow-up after
historical challenge exposure, not a fresh blind evaluation. A failed independent
gate stops this sequence without opening the official cases.

After the applicable stages finish:

```text
<python> -m digitlab.captcha_extension_report --stage summary
```

The summary audits preserved identities, splits, all epoch counts and reserved
score counts where available. It keeps synthetic development, independent tests
and official results separate. The original MNIST-only course model, existing
supplementary model and residual model remain selectable in the active app.
Model replacement, public deployment, GPU setup, commit and push are separate
actions. This run uses CPU; it does not require CUDA.
