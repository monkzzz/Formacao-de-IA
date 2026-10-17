# R08–R09: reproducible ML prerequisites and repeat evaluation

Verified 2026-10-17 without changing the selected model, preprocessing, site or
historical results. [Clean prerequisite probe](ml-reproducibility-preflight.json),
[original-environment re-evaluation](selected-mnist-reevaluation.json) and
[clean-environment re-evaluation](selected-mnist-clean-reevaluation.json) record
actual execution; they are reproducibility follow-ups on previously exposed data.

## Clean dependency setup

Created a new venv without system site packages and installed the committed
`dia2-local/requirements.txt` through pip. The new environment is under ignored
`dia2-local/.tmp/repro-clean-20261017/`; package downloads/installations do not
change the original venv. The probe records installed package versions and the
pip installation report remains in the ignored temporary directory.

From the root, a fresh equivalent setup is:

```powershell
python -m venv dia2-local/.tmp/<new-clean-environment>
dia2-local/.tmp/<new-clean-environment>/Scripts/python.exe -m pip install -r dia2-local/requirements.txt
```

The historical training environment used Python 3.12.10, torch 2.14.1+cpu,
NumPy 2.5.4 and Pillow 12.3.0. The evidence records the actually restored
distribution versions; GPU availability is not assumed. Reproduction is scoped to
these dependencies and this Windows CPU host, not guaranteed across hardware.

## Data, checkpoints, fonts and source

The preflight copied only project Python source, four compressed MNIST archives
and the existing ignored captcha-v2 baseline checkpoint into a fresh disposable
layout with the same relative paths. It did not copy completed experiment reports
or a selected-output directory into the training destination. This matters:
running `digitlab.residual` in the original checkout correctly refuses to overwrite
the completed experiment.

The existing IDX loader verified canonical checksums, dimensions and labels.
The stratified seed-20261016 split had 55,000 train and 5,000 validation indices,
disjoint, with 10,000 canonical test samples held separately. Exact input and
index hashes are in the probe. The selected model and baseline state dictionaries
loaded successfully, and the copied seven recorded implementation sources matched
the historical source hashes.

The baseline checkpoint SHA-256 is
`36a6f330c0283bc47370cf262c308fa2dc4eed68083e760d041fe521c5310ec2`;
the selected checkpoint is
`bf3b6424c3f30815de9915b6158ea3d9ebcffa62356b2a6fd5a5243633afbec4`.
All 44 recorded font identities matched the Windows host: 36 training, four
development and four test faces. The preflight rendered twenty independent
training-split examples solely to verify tensor shape/finiteness and CLI readiness;
it did not optimize weights or create a new selected model.

To reproduce training later, use a fresh source layout with the relative
`Dia2/Dataset-MNIST/data/` and `dia2-local/artifacts/captcha-v2/best.pt` paths,
install the recorded dependencies, and provide the same locally licensed fonts
under `C:/Windows/Fonts`. The [historical protocol](../../dia2-local/docs/residual-training.md#commands)
defines the fixed training, export, browser gate and test order. The preflight
verified `digitlab.residual --help` and `digitlab.residual_evaluate --help` in the
isolated layout. **Full twelve-epoch retraining was not run** and bitwise recovery
of newly trained weights is not claimed.

The checkpoint copies came from this machine's preserved ignored artifacts.
There is still no independently verified public checkpoint archive or portable
font distribution. A source checkout plus browser-weight download alone cannot
provide those training prerequisites. This limitation is explicit rather than a
claim that an arbitrary fresh machine can train without additional artifacts.

## Safe selected-model evaluation

The [new helper](verify-selected-evaluation.py) loads the selected checkpoint,
compares every tensor exactly with the browser weight export, and evaluates only
the canonical MNIST test partition in batches. It saves genuine per-image outputs,
ten scores, confusion and loss into a **new** report; it never calls training,
export, selection or a challenge collector. Existing report paths and destinations
inside course data, serving assets or frozen artifact directories are refused.

Run from the repository root with either prepared Python environment:

```powershell
dia2-local/.venv/Scripts/python.exe participant-work/day2/verify-selected-evaluation.py --report participant-work/day2/<new-evaluation-report>.json
```

Both environments measured **9,910/10,000 correct (99.10%)** with the same clean
confusion matrix as the historical result. Loss comparison tolerance is `1e-5`;
actual differences and environment identities are in the reports. Frozen
checkpoint, weights, manifest and original challenge/training records matched
their before/after hashes. No official CAPTCHA image was opened or inferred.

Two focused [helper tests](test_selected_evaluation.py) passed: mutation of a
checkpoint/export is detected, and loss/confusion are independent of batch
boundaries on a synthetic fixture. These are helper tests, not another complete
classifier or GSS suite. Existing unit/browser evidence retains its actual dates.

The [preflight script](probe-ml-reproducibility.py) refuses its existing report and
workspace; choose new names before a follow-up. None of these checks reopens a
completed synthetic test for tuning or reclassifies a known result as a blind test.
