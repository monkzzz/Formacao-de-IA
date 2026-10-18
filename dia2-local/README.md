# Digit Lab

Digit and letter CNNs trained in this project, with browser drawing, image uploads,
raw prediction exports and real neural activations. The full local site also
retains optional pretrained OCR experiments, Words and Scopedog.

## Choose the website

| Variant | Source | Delivery | Current scope |
| --- | --- | --- | --- |
| Full site | `dist/`, current UI in `dist/v3/` | `naoquerosaber.pt/AI/` via verified FTPS | Published 3.11.1; MNIST-only course default |
| Participant-trained submission | `submission/` plus selected shared modules and verified local weights | GitHub Pages from a separately built ZIP | Published cleanup v4 package; original v1 remains frozen |

The [deployment map](docs/deployment.md) explains source, artifact and hosting
boundaries. The [release history](docs/release-history.md) preserves earlier
releases and results. Neither live site changes when local files change.
The [3.11.1 release record](docs/release-3.11.1.md) records both deployments and
their public verification results.

## Setup on Linux or Windows

Use Python 3.12+ and the [shared runtime guide](../PORTABILITY.md). From the
repository root, prepare the platform-specific Day 2 environment:

```bash
python3 setup_course.py --component day2 --install --fonts --browser
```

```powershell
py -3.12 setup_course.py --component day2 --install --fonts --browser
```

Use `.runtime/linux/day2/bin/python` or
`.runtime/windows/day2/Scripts/python.exe` directly; activation is optional.
Commands below run from `dia2-local/` with that interpreter substituted for
`<python>`. Never share virtual environments between Linux and Windows.

## Start the application

```text
<python> serve.py
```

Open `http://127.0.0.1:8765/`. The server serves static files only; classification
runs in the browser. If release weights are missing, `serve.py --download-models`
can restore matching published exports after hash verification. The optional
supplementary model requires its own local artifact; see
[selectable models](docs/selectable-models.md). No training runs automatically.
For the restricted site, use [the submission guide](docs/self-trained-submission.md)
and [the new-release workflow](docs/deployment.md).

## Verify the current source

```text
<python> -m unittest discover -s tests
<python> -m digitlab.selectable_models_qa --url http://127.0.0.1:8765/ --report my-check-models.json --screenshot-prefix my-check-models
<python> -m digitlab.words_qa --url http://127.0.0.1:8765/ --digit-experiment mnist --report my-check-words.json --screenshot-prefix my-check-words
```

Choose new report and screenshot identities for each run. The maintained collectors
refuse existing evidence. [Browser QA](docs/browser-qa.md) documents commands,
prerequisites, worker doubles and limitations. Unit tests do not replace browser
checks. [Frontend maintenance](docs/frontend-cleanup.md) records the first phase;
the [completed maintenance cleanup](docs/maintenance-cleanup.md) records the shared
utilities, submission recovery, documentation and final package verification.

## Project structure

- `digitlab/`: data loading, training, export, browser verification and delivery tools.
- `dist/`: full static site, current UI, shared modules and preserved legacy assets.
- `submission/`: source templates for the restricted participant-trained site.
- `tests/`: repeatable pipeline, utility and preservation checks.
- `docs/`: current guides, fixed protocols and archived release history.
- `reports/`: measured results and separately named maintenance evidence.
- `artifacts/`, `data/`, `.venv/`, `.tmp/`: ignored local artifacts and environments.

## Training and original challenge protocol

Read [AGENTS.md](AGENTS.md), [task workflows](SKILLS.md) and the relevant fixed
protocol before training or evaluating. Keep the official ten CAPTCHA files and
their derivatives outside training, tuning and model selection. Never overwrite
a completed result or present a known-case rerun as a fresh blind test.

## Accuracy and limitations

MNIST accuracy and CAPTCHA performance measure different things. The recorded
MNIST-only result is 99.28% on 10,000 test images; its official follow-up is 2/10.
The preserved residual extension has a separate 10/10 follow-up, with only 6/10
correct and original score strictly above 90%. The full confidence criterion
remains unmet. These are recorded results, not new maintenance tests. See
[model evidence](reports/selectable-models-challenge-followup-v1-summary.md).
Scores are uncalibrated softmax outputs.

## Words mode and Scopedog

Words uses a separate pretrained handwriting reader in the full site and is
excluded from the participant-trained package. Scopedog uses authored local
responses with an explicit fallback. See [Words](docs/words.md),
[helper history](docs/release-history.md#scopedog-page-guide) and
[the submission boundary](docs/self-trained-submission.md).

## Attribution

Course exercise concepts: Vinicius Canonici and Hugo Gomes; see
[the course license](../LICENSE.md). MNIST: Yann LeCun, Corinna Cortes and
collaborators. EMNIST: Cohen, Afshar, Tapson and van Schaik, distributed by NIST.
Optional Words uses Microsoft TrOCR through Xenova; those weights were not trained
here. Resource attribution remains in [the preserved history](docs/release-history.md#attribution).
