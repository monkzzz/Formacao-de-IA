# Balanced color experiment: gated follow-up commands

The [frozen training protocol](balanced-color-training.md) controls selection.
Training and development data, original source files, weights and active app
identities are hash-protected. This companion only describes later helpers.

Run from `dia2-local/` with the [portable interpreter](../../PORTABILITY.md).
After all four epochs, if no epoch/preprocessing pair qualifies:

```text
<python> -m digitlab.balanced_color_report --stage guards
<python> -m digitlab.balanced_color_report --stage summary
```

The actual refusal checks must leave reserved partitions unopened and must not
create a preview. Preserve the rejected model and all epoch measurements.

If an eligible pair is selected:

```text
<python> -m digitlab.balanced_color_browser --stage export
<python> -m digitlab.balanced_color_browser --stage qa
<python> -m digitlab.balanced_color --stage test
```

The full app copy lives only in `.tmp/balanced-color-training-v1-preview/`.
The RGB contract applies to 64px digits; 28px digit and letter models retain the
original grayscale contract. Verify weights, prepared inputs, actual uploads,
intermediate activations, mode switching and desktop p95 <150 ms before reserved
data are opened. Predeclared upload samples are the first sixty preparation-valid
fixtures for the selected contract; validity uses contrast alone, not model errors.

Only if the independent test passes both baseline comparisons:

```text
<python> -m digitlab.balanced_color_browser --stage official
<python> -m digitlab.balanced_color_browser --stage compare
```

These steps save all ten raw browser outputs before comparing reference labels.
Prior challenge exposure is disclosed. Never select another epoch or transform
from that outcome. Strict professor acceptance uses the original unrounded score
for every case. Active-app replacement and deployment do not happen automatically.

Finally run `digitlab.balanced_color_report --stage summary`. The report audits
source membership, class/source/group balance, baseline and epoch score vectors,
predeclared eligibility and selection. Completed destinations refuse overwriting.
Independent human readability review and fresh Windows execution must remain
NOT RUN unless actually performed. No CUDA setup, commit or push is part of this
experiment.
