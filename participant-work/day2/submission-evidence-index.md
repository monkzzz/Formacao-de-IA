# Selected trained CNN submission evidence

Assembled 2026-10-17 for [Issue #2](https://github.com/monkzzz/Formacao-de-IA/issues/2).
The selected participant-trained default is **captcha-v3**, epoch 12, architecture
`residual64-16-32-128`, introduced in v3.7.0 and retained by the v3.10.0 interface.
Optional pretrained OCR readers are separate deliverables. This index preserves
the current application and does not constitute new instructor approval.

| Requirement | Evidence and interpretation |
| --- | --- |
| Identity | [Fresh identity/hash record](submission-model-identity.json), [browser manifest](../../dia2-local/dist/model/captcha-v3/digits/manifest.json). Weight SHA-256: `d962c7f1aefd4f86cf9fcc621e30a1e8fbbce092c5a47ab3dd88e0f64573b42c`; local checkpoint SHA-256: `bf3b6424c3f30815de9915b6158ea3d9ebcffa62356b2a6fd5a5243633afbec4`. |
| Configuration and seed | [Fixed protocol](../../dia2-local/docs/residual-training.md), [trainer](../../dia2-local/digitlab/residual.py): seed 20261123, 12 epochs, 40,000 raw synthetic and 20,000 clean samples per epoch, AdamW 0.0003, weight decay 0.0001, batch 128, cosine decay, four CPU threads. |
| Split and selection | [Split implementation](../../dia2-local/digitlab/data.py), seed 20261016: stratified 55,000 training / 5,000 validation; [archived selection](../../dia2-local/reports/captcha-v3-development-selection.json) fixes epoch 12 before fresh test loading. Font families are separated by protocol. |
| Environment and history | [Preserved training report](../../dia2-local/reports/captcha-v3.json): `environment`, `history` (12 epochs), `policy`, `split`, training/font hashes; [dependency lock](../../dia2-local/requirements-lock.txt). Recorded Python 3.12.10, CPU torch 2.14.1, NumPy 2.5.4, Pillow 12.3.0. |
| Held-out results | Same report: `test` is 9,910/10,000 clean MNIST (99.10%); `raw_test` is 19,746/20,000 synthetic (98.73%). Canonical MNIST has been evaluated in earlier iterations. Synthetic accuracy does not establish general CAPTCHA accuracy. |
| Confusion/error analysis | Full matrices remain in `test.confusion_matrix` and `raw_test.confusion_matrix`; [derived summary](submission-model-identity.json) reports 90 clean and 254 synthetic errors. Largest clean confusions: 9→4 and 9→7, seven each; synthetic: 7→1, eighteen. Paired raw comparison fixed 159 baseline errors and broke 36. |
| Preprocessing/export | Manifest contract `border-gray-bilinear-com-64-v1`, 64×64 input, float32 little-endian, labels 0–9; [preprocessing](../../dia2-local/digitlab/preprocess.py), [64px implementation](../../dia2-local/digitlab/highres.py), [export/evaluation](../../dia2-local/digitlab/residual_evaluate.py). |
| Browser parity | Historical [runtime checks](../../dia2-local/reports/captcha-v3-runtime-qa.json) and [character regression](../../dia2-local/reports/captcha-v3-browser-qa.json); these are not fresh browser checks of the current submission. |
| Current unit verification | [Actual 30-test result](submission-unit-tests.json), 2026-10-17, exit 0, no skips. This is a current unit result, distinct from historical 28-test records. |
| Artifact recovery | [Clean-environment restoration](submission-artifacts.md), real verified digit and letter downloads. Browser weights are recoverable; checkpoint distribution/retraining reproducibility was not tested. |

Original official challenge results remain 2/10; later captcha-v3 follow-ups
record 10/10 after prior exposure. Neither metric replaces MNIST or synthetic
results. Challenge-chain delivery remains its own checklist task. No official
challenge image was opened or evaluated in this batch.

The [review and Issue mapping](submission-review.md) identifies scope, checks,
deviations and the delivery commit. Instructor contact is deferred by participant
instruction; no request was sent and no acceptance is claimed.
