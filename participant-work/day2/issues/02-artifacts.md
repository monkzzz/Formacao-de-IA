The existing exported weights/checkpoints are ignored and are not supplied by a
source clone. This Issue completes the submission artifact process, not training.

Depends on the evidence-index Issue in this batch (`evidence` in issue-plan.json).

Acceptance:

- Document an authorized artifact retrieval or reproducible training route with
  model identity, byte count, SHA-256 and restoration paths.
- Demonstrate restoration in an isolated clean directory/environment; preserve
  existing checkpoints, exports and frozen evaluation outputs.
- Keep secrets, datasets and weights outside Git; document font/runtime limits if
  using the historical training route.

Verification: record retrieval/restoration commands and manifest hash comparisons.
Do not overwrite historical outputs or claim a clone alone includes weights.
