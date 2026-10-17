# Project context

Status: **existing classifier preservation context, version 1.0.0**. Owner: the project participant.
The agent maintains this record from confirmed requirements and labels assumptions.

| Field | Current value |
| --- | --- |
| Goal and intended users | Preserve the existing Day 2 Digit Lab website and prepare the course submission |
| Scope and exclusions | Existing `dia2-local/`; no replacement classifier, retraining, migration or production changes in this batch |
| Inputs, outputs and interfaces | MNIST source data and browser drawing/local uploads of single digits; current model consumes 64×64 grayscale and emits ten digit scores |
| Runtime and dependencies | Existing Python/PyTorch tools for training/export; static JavaScript browser inference; optional pretrained readers remain separate |
| Resource constraints | Historical protocol used four CPU threads, 12 epochs and batch 128; no new training budget or physical-phone performance assumed |
| Data/privacy/evaluation boundaries | Browser inference; never train/tune/select on official ten images, answers or completed evaluation caches; preserve historical frozen results |
| Acceptance criteria | Evidence index, actual relevant checks, verified artifacts, browser parity/real activations and submitted-origin behavior; retain current site |
| Validation commands and directory | From `dia2-local/`: `.venv/Scripts/python.exe -m unittest discover -s tests -v`; run only for the relevant verification Issue with new report names |
| Repository and branch | Personal `monkzzz/Formacao-de-IA`, current root branch `main`; retain existing root history |
| Deployment target and artifact process | Preserve `https://naoquerosaber.pt/AI/`; ignored model retrieval and live verification remain work; Pages substitution needs instructor acceptance |

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

Assumption: existing exported manifest identity represents the intended current
default CNN; verify the submitted origin before claiming production parity.
Pending: artifact restoration proof, fresh tests, live-origin checks, instructor
acceptance of hosting/assistant/fork/process deviations and actual feedback.

Detailed evidence and alternatives: [specification](../../day2/classifier-specification.md).
For a new unrelated project, use the preserved generic archive, not this populated
context. See [decisions](decisions.md) for limited authorization and history.
