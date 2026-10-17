# Fixed-weight preprocessing study

Protocol declared before results, after the participant requested moving forward
without pushing commits. This is the first phase of the controlled improvement
study: isolate preprocessing with the preserved `captcha-v3` weights fixed.
No official challenge image, label, generator or prediction cache is read.

## Frozen comparison

Seed 2026102101; four CPU threads; all variants receive exactly the same 1,800
new development images and 5,000 clean MNIST validation images. Development is
balanced across digits and printed/handwritten sources. Use the existing broad
independent renderer, pinned Lato development fonts and newly stratified EMNIST
Digits training sources (500 per class), with exact duplicate pixels removed
before splitting; save the source split and raw fixtures.
The remaining EMNIST training indices are reserved for subsequent training.
Reserve EMNIST test images and Ubuntu fonts for a later frozen evaluation.

The dataset is generated CAPTCHA-style data, not a collected real CAPTCHA
population. Fonts and baseline weights have prior experimental exposure. Synthetic
source labels do not establish human readability; save a fixed contact sheet for
review and mark human review NOT RUN until actually performed.

Compare exactly four predeclared preparations at 64px:

1. **Current:** unchanged production preprocessing.
2. **Median border:** estimate background with border median rather than mean,
   retaining the same foreground thresholds, interpolation and centering.
3. **Small components:** current background estimate, discard only disconnected
   foreground components smaller than both 1.5% of the largest component and
   `max(4, ceil(0.0008 × image area))` pixels; retain the largest component.
4. **Median filter:** a fixed 3×3 median filter before unchanged production preparation.

No parameter grid or challenge-specific rule is permitted. Blank or unreadable
prepared inputs fail the entire variant's eligibility gate, with their indices
recorded and no performance claim for that variant; they are never silently omitted.

For a candidate to qualify, require development accuracy loss <=0.1 percentage
points, clean MNIST accuracy loss <=0.1 points, correct-with-score-strictly->90%
coverage gain >=0.5 points, lower raw NLL, Brier increase <=0.001 and ECE increase
<=0.005, and no increase in confident incorrect predictions above 90%.
Select the qualifying variant with lowest development NLL; otherwise retain
current preprocessing. These are development gates, not proof of the professor's
official requirement (10/10 correct and every score strictly >90%).

Record confusion matrices, raw scores, strict-threshold coverage, confident errors,
environment and all source/font/model hashes. Preserve existing models, app assets,
previous evidence and official outcomes. Do not choose a variant after seeing
reserved or official results. No score rescaling, candidate deployment or model
training occurs in this preprocessing-only phase.

## Run

From `dia2-local/`, use the [portable runtime](../../PORTABILITY.md) with confidence
plotting dependencies and the verified EMNIST archive/font bundle already prepared:

```text
<python> -m unittest tests.test_preprocessing_study -v
<python> -m digitlab.preprocessing_study
```

The runner refuses to overwrite an existing study. A qualifying preparation must
still be implemented and tested in an isolated browser preview before it can be
used by a selected extension. Further training needs a separate frozen protocol;
this study does not silently start it or replace a selectable model.
