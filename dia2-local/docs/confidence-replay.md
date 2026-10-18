# Independent confidence replay experiment

Protocol declared before results, 18 October 2026. The previous training studies
failed development or preservation gates. This bounded follow-up tests whether
retaining baseline distributions on correctly classified independent training
images limits regressions while replaying harder examples. It is an experiment,
not a promised confidence improvement.

Keep the production residual architecture, preprocessing and raw softmax. Start
from the exact preserved participant-trained residual checkpoint. Use no external
pretrained weights, official CAPTCHA images, their generator, labels or previous
predictions in training, diagnosis or selection. Do not deploy a candidate based
on these known official cases.

One fixed run: seed 2026101817, four epochs, batch 64, four CPU threads, AdamW
0.00003 with weight decay 0.0001 and cosine decay to 0.000005, dropout 0.1 and
EMA 0.98. Generate 4,800 balanced independent synthetic training images with the
existing paired-corruption renderer and use its noisy anchor view. Add 4,000
balanced clean examples from the original MNIST training partition. Keep the
55,000/5,000 MNIST split. Use 2,400 new synthetic development images, the full
5,000-image clean validation guard and 2,400 new legacy-renderer bridge examples.

Use the pinned open-font bundle: NotoSans/NotoSerif/RobotoSlab/Oswald for training,
Lato for development, Ubuntu reserved. The baseline has historical evaluations;
these are current-run splits and fresh seeds, not a claim of no prior font exposure.
The fixed training objective weights CE by `1 + 2 * (1 - baseline true-class score)`
and adds weight-2 KL from the frozen baseline to the student only on training
examples that the baseline classifies correctly. Teacher outputs are training
targets only. Inference has no temperature adjustment, score multiplier or
postprocessing intended to inflate confidence.

Select the eligible EMA epoch with lowest raw development NLL. Eligibility keeps
the previous gates: raw, clean and bridge accuracy loss at most 0.1 percentage
points, correct-and-strictly-above-90 coverage gain at least 0.5 points, lower
raw NLL, Brier increase at most 0.001 and ten-bin ECE increase at most 0.005.
Also require no increase in confidently wrong raw predictions. Exactly 90% fails
the strict coverage check. Keep all rejected epochs' metrics and the final
checkpoint; never lower gates after observing results.

Only an eligible frozen selection may open 6,000 new synthetic reserved images,
the canonical MNIST test and a fresh 2,400-image legacy bridge. Reapply all gates,
record raw vectors, and never select another epoch using final outcomes. A
qualified candidate still needs isolated browser parity before consideration for
publication. This workflow does not run another official challenge evaluation.

From `dia2-local/`, with the portable Day 2 interpreter:

```text
<python> -m digitlab.confidence_replay --stage train
<python> -m digitlab.confidence_replay --stage test
```

The second command refuses an ineligible selection before decoding reserved
data. Sources, fonts, datasets, baseline and historical evidence are hashed;
training caches/checkpoints remain in ignored `artifacts/captcha-confidence-replay-v1/`.
Results are recorded separately in `reports/captcha-confidence-replay-v1.json`.

## Completed result

All four epochs completed. None qualified; the baseline is retained. The best
strict correct-above-90 development coverage was 97.708%, versus 97.625% for
the baseline and the fixed requirement of 98.125%. The actual test command
refused the rejected selection before opening reserved samples. No candidate
export, official inference or publication followed this rejected experiment.
See [the measured summary](../reports/captcha-confidence-replay-v1-summary.md),
[full history](../reports/captcha-confidence-replay-v1.json) and
[integrity/gate checks](../reports/captcha-confidence-replay-v1-validation.json).
