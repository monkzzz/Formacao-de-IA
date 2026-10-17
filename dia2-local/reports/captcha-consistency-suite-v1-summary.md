# Consistency/capacity suite: actual delivery

Status: **RETAIN BASELINE; no eligible arm**. See the [predeclared protocol](../docs/confidence-suite.md) and [full measured history](captcha-consistency-suite-v1.json). This is independent synthetic evidence, not a real-world CAPTCHA accuracy claim.

## Preprocessing diagnosis

Across 1,200 balanced independent examples, the unchanged model scored 99.25% on noisy inputs versus 99.42% on the corresponding clean sources. The crop window covered 99.973% of annotated glyph mass on average, but 43.75% of glyphs shrank below 32 pixels. This measures coverage and scale, not preservation of every visible stroke after occlusion. The small clean/noisy accuracy gap does not justify deploying an unvalidated cleanup rule. No production preprocessing change was made.

The clean-source view is an oracle ablation, not an implementable method for recovering a hidden clean image. These results do not identify the causes of the four lower-scoring official cases.

[Readable diagnostic contact sheet](screenshots/captcha-consistency-suite-v1-diagnostic-readable.png) · [Per-example annotations and condition results](captcha-consistency-suite-v1-diagnostic.json)

| Diagnostic condition | Accuracy | Correct and score ≥90% |
| --- | ---: | ---: |
| clean | 99.50% | 99.00% |
| background | 99.50% | 98.00% |
| crossing_lines | 98.00% | 93.50% |
| blur_jpeg | 99.50% | 99.00% |
| short_gaps | 99.50% | 97.50% |
| mixed | 99.50% | 96.00% |
| printed | 100.00% | 100.00% |
| handwritten | 98.50% | 94.33% |

## Matched training comparison

The table reports the selected eligible epoch of each arm, when one exists. Otherwise it shows the lowest-loss rejected development epoch as a diagnostic, not a replacement selection. All arms received the same data/order and four epochs. Reserved results never change the arm choice.

| Arm | Parameters | Epoch shown | Raw accuracy | Correct at ≥90% | Raw NLL | Clean accuracy | Bridge accuracy | Eligible epoch |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Preserved baseline | — | — | 99.111% | 97.611% | 0.02580 | 99.300% | 98.667% | — |
| control | 272,618 | 1 | 99.250% | 97.556% | 0.02703 | 99.240% | 98.583% | None |
| consistency | 272,618 | 4 | 99.111% | 97.778% | 0.02705 | 99.220% | 98.583% | None |
| capacity | 276,874 | 1 | 99.250% | 97.667% | 0.02696 | 99.280% | 98.583% | None |

Frozen choice: **none; retain baseline**. The deeper arm must satisfy the extra incremental-benefit rule; added capacity alone is not a reason to select it.

## Reserved evaluation and official scope

Reserved data: **NOT RUN**. An eligible frozen development selection and matched browser parity/speed are required before final data are decoded. No rejected checkpoint is tested on the official images.

Official follow-up: **NOT RUN**. Prior official exposure remains explicit. No new official confidence score is claimed without that raw record. No public deployment was performed.

## Preservation and limits

Verified 29 preserved identities: **unchanged**. See [integrity record](captcha-consistency-suite-v1-validation.json). Datasets, views, weights and figures remain in ignored local storage.

The raw diagnostic and raw selection sources are disjoint. The full 5,000 clean validation guard is shared across arms and includes both raw-source subsets. The font/data generator distribution is synthetic; fonts and MNIST have prior exposure in historical experiments. Labels are generated/source labels, not independent human readability judgements. Binned ECE and softmax scores do not establish calibrated real-world correctness probabilities.

Linux execution and a portable implementation do not establish a fresh Windows execution or hosted CI pass. The confidence-on-all-ten target can only be assessed by a properly frozen official follow-up, never by training against those ten or raising displayed percentages.
