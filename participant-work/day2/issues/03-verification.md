Verify the existing selected captcha-v3 CNN and application for submission.
Earlier test reports are retrospective context, not a current suite result.

Depends on verified artifacts (`artifacts` in issue-plan.json).

Acceptance:

- Run the relevant existing Python unit suite and preserve actual output/count.
- Check Python/JavaScript preprocessing, logits and real activations within 0.0001.
- Exercise drawing, upload/batch upload, clear/reset, scores, activation displays,
  export, invalid input and weight-download failure recovery.
- Label mocked versus real-model checks and desktop versus physical-phone limits;
  confirm inference uses browser pixels and weights, not a remote inference API.

Verification: use new report names, record environment and model hash, link final
commits and findings. No retraining or new official challenge accuracy experiment.
