# Ten-task challenge and maintenance batch

Completed 2026-10-17. The ten actionable tasks are the three unconditional
challenge-evidence tasks and the first seven maintenance tasks in `TASKS.md`.
Pages and instructor process requests remain deferred. Actual teacher feedback
cannot be performed locally; no teacher contact or acceptance is claimed.
The conditional new-origin challenge check remains pending because no new origin
or changed default model was submitted. No live site, inference or weights changed.

| Task | Result and evidence |
| --- | --- |
| Challenge evidence chain | [Selected freeze, raw records, comparison and public follow-up](submission-challenge-chain.md) |
| Preserve original records and follow-up scope | [Byte integrity check](submission-challenge-integrity.json); original archive and weights match their freeze |
| Separate evaluation results | [MNIST, synthetic and ten-image result table](submission-challenge-chain.md#distinct-results-and-limitations) |
| Repair evaluator workflow | [Collector](../../Dia2/Desafio/avaliar_captcha_no_site.py), [manual workflow](../../.github/workflows/avaliar-desafio-avancado.yml), [real non-challenge smoke](maintenance-evaluator-smoke.json) and [diagnostic failure](maintenance-evaluator-failure.json) |
| Resolve generator paths | [Generator](../../Dia2/Desafio/gerar_desafio_avancado.py) refuses the official directory and nonempty destinations; [workflow](../../.github/workflows/gerar-desafio-avancado.yml) saves a temporary separate artifact without Git writes |
| Correct count | [MNIST guide](../../Dia2/Dataset-MNIST/README.md) now says ten challenge images/cases |
| Reconcile status | Dated updates in [study answers](../../Dia2-Answers/README.md), [proposal](../../DIA2-PROPOSTA.md), [local README](../../dia2-local/README.md) and [audit/report guide](../../dia2-local/reports/README.md); historical records retained |
| Clarify submission release | [Hosting status](../../dia2-local/docs/hosting.md#submission-status--2026-10-17): application v3.10.0, trained captcha-v3 default; old release headings labelled historical |
| Label agent template | [Jarvis](../../.github/agents/Jarvis.agent.md) explicitly unfinished, with limits on bootstrap in this course repository; Copilot discovery remains unverified |
| Root navigation | [Personal-fork navigation](../../README.md#personal-fork-navigation--2026-10-17) explains answers, implementation, proposal, checklist and the personal-repository boundary |

## Actual validation

The [validation record](maintenance-validation.json) and
[reproducible checker](validate-maintenance.py) cover YAML parsing, workflow script
paths, relative document links, Python syntax, generated PNG structure and hashes,
same-environment deterministic regeneration, official image preservation, and
unchanged historical evidence. The generator ran twice into distinct ignored
directories below `dia2-local/.tmp/maintenance-20261017/`; neither output is used
for training, inference or accuracy measurement.

The repaired evaluator ran with installed Edge against the existing public app
using only the ten existing clean MNIST fixtures. It preserved all ten real raw
predictions and hashes. A separate invalid-URL run returned exit code 1 and a
`FAIL` diagnostic. Four focused automation unit tests passed after reviewed
sandbox escalation; the first restricted run had three temporary-directory
permission errors. Tests cover official-input consent, output preservation,
diagnostics, image/model identity, score validity and prediction counts.

Commands run from the repository root:

```powershell
dia2-local\.venv\Scripts\python.exe -m unittest discover -s Dia2/Desafio -p test_automation.py -v
dia2-local\.venv\Scripts\python.exe participant-work/day2/verify-challenge-chain.py
dia2-local\.venv\Scripts\python.exe Dia2/Desafio/gerar_desafio_avancado.py --output-dir dia2-local/.tmp/maintenance-20261017/generated
dia2-local\.venv\Scripts\python.exe Dia2/Desafio/gerar_desafio_avancado.py --output-dir dia2-local/.tmp/maintenance-20261017/generated-repeat
Dia1\Exercicios-GSS\.venv\Scripts\python.exe participant-work/day2/validate-maintenance.py
git diff --check
```

The evaluator smoke command is the documented CLI with
`--url https://naoquerosaber.pt/AI/`, `--input-dir dia2-local/reports/mnist-fixtures`,
`--output participant-work/day2/maintenance-evaluator-smoke.json` and
`--browser-executable "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"`.
Collectors/checkers refuse existing reports; select new destinations for follow-ups.

Local validation does not establish a successful GitHub-hosted Actions run.
The generator's Linux workflow pins Pillow 11.3.0; local validation records its
actual installed version and font hashes, without claiming cross-platform byte
identity. The manual evaluator supports Digit Lab's declared UI contract; it is
not a universal evaluator for the teacher's reference application.

The delivery commit can be resolved with
`git log -1 --format=%H -- participant-work/day2/maintenance-next-ten.md`.
Its Issue references connect the evidence to existing Issues without claiming
closure, teacher findings or acceptance. Only two individually verified raw
challenge records are added from the pre-existing untracked files. The remaining
JPGs and other raw reports are retained untouched for later review.
