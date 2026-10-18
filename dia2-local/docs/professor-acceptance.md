# Professor's acceptance criterion

After the completed work was committed, the participant explicitly clarified the
professor's requirements in this conversation:

- Exactly **10/10 correct** on the official CAPTCHA cases.
- Every correct prediction must have an original model score **strictly >90%**.
- Supplementary training is acceptable as a **separate, correctly documented extension**.
- Downloaded pretrained models are **not acceptable for the submission**, according
  to the participant's subsequent clarification. Keep pretrained digit/word readers
  as historical experiments only. Use the separate
  [participant-trained submission package](self-trained-submission.md); downloading
  MNIST/EMNIST training datasets does not import pretrained model weights.

This is the participant's report of the professor's criterion. It does not claim
an independently witnessed review or approval of the current implementation.
The generic course wording remains preserved; this project-specific requirement
is stronger than its statement that a perfect challenge score is not mandatory.

Apply the comparison to unrounded scores. Exactly 0.90 fails; rounding a value
for display must not change acceptance. Correct classification alone, mean score,
or a confident incorrect answer cannot satisfy the requirement. Model scores are
not established calibrated correctness probabilities. Do not inflate them through
display arithmetic to meet this criterion.

[The explicit check](../digitlab/acceptance.py) is separate from historical
`correct_at_90` measurements, which used >=90%. Preserve those reports and their
original definitions; new work uses `correct_above_90` and the strict policy.

## Current status and next experiment

Rechecking saved outputs requires no new inference: MNIST-only has 2/10 correct
and 0/10 correct above 90%; the supplementary model has 5/10 and 1/10; the preserved
residual model has 10/10 and 6/10. **No current model satisfies acceptance.**

[Validation evidence](../reports/professor-acceptance-validation.json) records
53 passing unit tests, including strict-boundary checks, and the policy applied
to saved outputs. No new official inference or training was needed.

Keep the MNIST-only model selectable with its own training and evaluation evidence.
Document extension data origins, labels, augmentation, splits, hashes, architecture,
selection rule and measured results. Supplementary permission does not permit
training, validation or model/preprocessing selection on the official ten, their
derivatives, labels, generator or previous outcomes.

The next controlled study should focus on independent CAPTCHA-style development
data and the preserved 64px residual model. First isolate preprocessing with fixed
weights; then compare one bounded training extension using the selected preparation.
Separate source/font families and exact duplicates across training, development and
reserved test; record human readability checks and limitations. Predeclare the
development criteria, including correct-above-90 coverage and confident mistakes,
before results. Preserve clean MNIST performance and browser/Python parity.

Select and freeze the candidate using independent development evidence before
reserved evaluation. A later official run is a labelled follow-up after prior
exposure, never a reason to search another checkpoint. No success or public
deployment is promised. This clarification does not start another training run.
