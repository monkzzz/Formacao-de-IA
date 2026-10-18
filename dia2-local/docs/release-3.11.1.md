# Maintenance release 3.11.1

The participant requested a commit, deployment to both sites and comprehensive
post-deployment checks after [the maintenance cleanup](maintenance-cleanup.md).

## Prepared artifacts

- Full site: `dist/`, version 3.11.1, with fresh module URLs for the shared drawing
  and image I/O code. The default is the MNIST-only course model, with separate
  supplementary/residual options. No model weights or recorded scores changed.
- Pages: the independently built `self-trained-submission-cleanup-v4` package,
  with [build identity](../reports/self-trained-submission-cleanup-v4-build.json)
  and [local browser checks](../reports/self-trained-submission-cleanup-v4-browser.json).
  It contains 23 files and four participant-trained model exports; no pretrained
  reader runtime is included. Original v1 and intermediate packages are preserved.

The public full-site preflight identified 14 changed/missing files among 61
application assets. ROMs and parity fixtures are excluded from the transfer plan.
FTPS connectivity and the account's documented root mapping were checked without
changing remote files. The uploader backs up replaced files and verifies every
transferred byte. Its dependency-order regression now includes the Words import
used by the digit reader. Existing deployment receipts are refused before upload.

Publication and public verification results will be appended after execution.
No official CAPTCHA evaluation, training or tuning is required for this release.
