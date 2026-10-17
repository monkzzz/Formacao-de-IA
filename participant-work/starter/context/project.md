# Project context

Status: **existing classifier preservation context, version 1.2.0**, progress reconciled 2026-10-17. Owner: the project participant.
The agent maintains this record from confirmed requirements and labels assumptions.

| Field | Current value |
| --- | --- |
| Goal and intended users | Preserve the existing Day 2 Digit Lab website and prepare the course submission |
| Scope and exclusions | Preserve existing `dia2-local/` and external site; separately publish its verified static artifact on Pages; no replacement classifier, retraining or migration |
| Inputs, outputs and interfaces | MNIST source data and browser drawing/local uploads of single digits; current model consumes 64×64 grayscale and emits ten digit scores |
| Runtime and dependencies | Existing Python/PyTorch tools for training/export; static JavaScript browser inference; optional pretrained readers remain separate |
| Resource constraints | Historical protocol used four CPU threads, 12 epochs and batch 128; no new training budget or physical-phone performance assumed |
| Data/privacy/evaluation boundaries | Browser inference; never train/tune/select on official ten images, answers or completed evaluation caches; preserve historical frozen results |
| Acceptance criteria | Evidence index, actual relevant checks, verified artifacts, browser parity/real activations and submitted-origin behavior; retain current site |
| Validation commands and directory | From `dia2-local/`: `.venv/Scripts/python.exe -m unittest discover -s tests -v`; run only for the relevant verification Issue with new report names |
| Repository and branch | Personal `monkzzz/Formacao-de-IA`, current root branch `main`; retain existing root history |
| Deployment target and artifact process | Separate verified Pages site at `https://monkzzz.github.io/Formacao-de-IA/`; preserve `https://naoquerosaber.pt/AI/`. Manual artifact build restores seven hash-verified exports without committing binaries. Local checkpoint/font prerequisites are verified; portable public recovery remains limited |

Confirmed generic preferences: English communication, autonomous progress on
authorized reversible work, focused changes, evidence-based review and preservation
of unrelated files. The participant chose the current assistant for course work;
this starter does not require a particular assistant product.

Record approved technical choices in [decisions](decisions.md), observations in
[evidence](../evidence/README.md), reusable explanations in
[knowledge](../knowledge/README.md), and current progress in [handoff](handoff.md).
Keep assumptions and pending decisions visible. Update this file when requirements
change; retain superseded decisions and the reason for replacing them.

## Sources and status distinctions

Confirmed participant directive, 2026-10-17, after the context proposal:
“the current development of dia 2 local that is o websitw maintain it”. This confirms
preservation of the existing development and website, not new technical choices,
publication permission or instructor approval. It supersedes the proposed Pages
migration for this batch. No claim that every historical experiment was reviewed
or approved by the participant is made.

Observed implementation: `captcha-v3`, `residual64-16-32-128`, preprocessing
`border-gray-bilinear-com-64-v1`, 272,618 float32 parameters, weights SHA-256
`d962c7f1aefd4f86cf9fcc621e30a1e8fbbce092c5a47ab3dd88e0f64573b42c`.
Historical source split is 55,000/5,000; epoch 12 was selected before the recorded
synthetic test. Historical results: 99.10% clean MNIST, 98.73% synthetic and a
separate 10/10 official follow-up after exposure. These are not current reruns.
Original 99.28% / 2-of-10 evidence remains preserved separately.

Verified progress: [selected-model evidence](../../day2/submission-evidence-index.md),
[public browser identity/parity](../../day2/submission-browser-delivery.md) and
[clean ML prerequisites/re-evaluation](../../day2/ml-process-reproduction.md).
Historical metrics retain their identity; later checks are verification follow-ups.
The participant reconfirmed preservation of `dia2-local` and continuation of the
current development while finishing tasks; see [present scope](../../day2/participant-continuation-scope.md).
Source publication and real Issue synchronization are completion work, distinct
from production deployment. The old blanket “artifact/tests/live verification
pending” wording is superseded by these actual records.

Pending: actual participant research critique; portable off-machine checkpoint/font
availability beyond the documented local route; instructor acceptance of
assistant/fork/process deviations and an actual feedback session.

The participant subsequently requested the GitHub Pages task. The separate site
passed asset identities, real-model parity/uploads and drawing/touch checks;
see [publication evidence](../../day2/pages-publication.md). This supersedes only
the earlier deferred Pages scope, preserving the external site. The optional
official-image rerun was rejected by automatic approval review and not run;
deployment integrity uses frozen identities and non-challenge parity fixtures.

Detailed evidence and alternatives: [specification](../../day2/classifier-specification.md).
For a new unrelated project, use the preserved generic archive, not this populated
context. See [decisions](decisions.md) for limited authorization and history.
