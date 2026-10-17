Preserve and index existing frozen challenge evidence without tuning or rerunning
the official evaluation. Original recorded 99.28% MNIST / 2-of-10 and later follow-ups
retain separate model and runtime identities.

Depends on model evidence index (`evidence` in issue-plan.json).

Acceptance:

- Link frozen runtime/weights, ten raw predictions/scores, separate comparison,
  input hashes, error analysis and applicable public verification.
- Explain prior exposure and distinguish MNIST, synthetic and ten-image results.
- Preserve ignored raw artifacts through an appropriate artifact process rather
  than staging unrelated local files or completed test caches indiscriminately.

Verification: inspect existing hashes, sources and chronology only; no training,
model/preprocessing selection or score tuning using official images or answers.
Record absent artifacts and retrieval requirements instead of inventing evidence.
