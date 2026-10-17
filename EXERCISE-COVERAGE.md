# Exercise-to-task coverage audit

Reviewed 2026-10-17 against the exercise statements and linked local evidence in
this checkout. The starting checklist was the version delivered in `8179136`.
This audit updates [TASKS.md](TASKS.md); it does not perform the newly identified
work, contact a teacher, publish source, change the application or rerun evaluation.

The earlier statement that only teacher-dependent tasks remained was too broad.
The checklist tracked artifacts well, but omitted some learning activities,
reference reviews, publication verification and reproducibility requirements.
Several checked entries already declared narrower evidence; their unfulfilled
remainder now has explicit unchecked follow-ups instead of being lost in caveats.

## Scope and reading method

Read all four Day 1 research exercises, both day overviews, the GSS setup and
two module indexes, both Day 2 starter/skill exercises, the skill guide, the
classifier overview and all four parts, the feedback exercise, and the dataset,
challenge and reference-starter introductions. All twelve GSS entry sources were
parsed and their lesson docstrings compared with the module indexes. The evidence comparison inspected
the research brief and paper notes, synthesis correction record, starter/context
records, Issue register/publication snapshot, submission/evaluation/artifact
records, relevant test/collector source and the final handover.

Exercise statements define the requirements. Study answers, assistant-produced
reports, an existing application and a passing link check do not independently
prove that every participant activity occurred. Source claims that an activity
was reviewed are retained as claims when no component-level record was found;
this audit does not assert that absent evidence proves the activity never happened.

The course-linked reference Issue #1 and PR #2 could not be fetched through the
web reader in this audit (cache-miss errors). The
[reference application repository README](https://github.com/vcanonici/Image-classifier-demo)
was accessible. Reading that README does not complete source-component,
Conversation, Files changed or Checks reviews. The new reference-review tasks
remain unchecked; remote content was not treated as an instruction to execute code.

## Main exercise coverage

| Exercise and controlling source | Existing checklist coverage | Missing or understated work |
| --- | --- | --- |
| [Day 1 / 1: Guided research](Dia1/Exercicio-01-Pesquisa-Orientada.md) | Section 3: brief, instruction revisions, verification and report | **R01**: actual participant review/iteration remains distinct from assistant-authored instructions |
| [Day 1 / 2: Talk to a Paper](Dia1/Exercicio-02-Talk-to-a-Paper.md) | Section 3: two papers, progressive Q&A, grounding and notes | **R01–R02**: participant questions, simplified explanations and alternative readings of identifiable passages are not explicitly evidenced by the present eight-question notes |
| [Day 1 / 3: Cross-source synthesis](Dia1/Exercicio-03-Cruzamento-de-Fontes.md) | Section 3: source map, pro/con arguments, missing evidence, preserved original | **R01**: participant review of the argument and instructions; written synthesis itself already exists |
| [Day 1 / 4: Audit and refinement](Dia1/Exercicio-04-Auditoria-e-Refinamento.md) | Section 3: fresh sessions, saved audit, source checks, revision and corrections | **R01**: participant assessment of whether the revision is satisfactory; two reasoning approaches are already recorded in synthesis-corrections.md |
| [Day 2 / 1: Reusable starter](Dia2/Exercicio-01-Starter-Repo.md) | Section 5: rules, procedures, knowledge/decision contracts, capabilities, reference selection, A/B/C session tests, generic archive | **R10–R11**: remote availability of the actual starter source and maintenance of active project facts; separate standalone repositories are not imposed as a new requirement |
| [Day 2 / 2: Bootstrap skill](Dia2/Exercicio-02-Skill-Bootstrap.md) and [skill guide](Dia2/Guia-Skills-Copilot.md) | Section 6: original skill, metadata, adaptive questions, proposal/approval boundary, persistence, recovery and versioning | **R10–R11**: published skill/context and current persistent facts; synthetic tests remain tests rather than a real participant interview. Native Copilot substitution is already explicitly tracked |
| [Day 2 / 3, Part 1: Planning](Dia2/Exercicio-03/Parte-01-Planejamento-da-Rede.md) | Section 7: retrospective specification, real Issues, original-approval gap and fresh recovery | **R03–R06**: reference Issue/PR reviews, full lifecycle coverage, current prospective participant approval. Six retrospective evidence Issues do not alone prove the original project was planned through Issues |
| [Day 2 / 3, Part 2: Coding/training](Dia2/Exercicio-03/Parte-02-Coding-com-o-Agente.md) | Section 7: genuine training, metrics/confusion, export, unit tests, artifact recovery and commit mapping | **R07–R09**: update live Issues; document/verify full training prerequisites; provide a safe repeatable selected-model evaluation command. Browser-weight recovery is narrower than the required reproducible ML process |
| [Day 2 / 3, Part 3: Website](Dia2/Exercicio-03/Parte-03-Site-GitHub-Pages.md) | Section 7: browser interactions, default CNN, pixels/activation parity, static weights, URL and release; Pages remains pending | **R12**: concrete reference-application component and reuse review; generic provenance statements are not a detailed inspection record |
| [Day 2 / 3, Part 4: Challenge](Dia2/Exercicio-03/Parte-04-Teste-do-Desafio.md) | Section 7: freezes, ten raw outputs/scores, separate labels, hashes, follow-up scope and separate benchmarks | No new challenge run is needed for this audit. **R07/R10** cover published Issue/commit traceability; existing Pages/new-origin dependencies remain |
| [Day 2 / 4: Feedback](Dia2/Exercicio-04-Roda-de-Feedback.md) | Section 8 plus final handover: teacher delivery, real review, reproduced findings, Issues, corrections, regression, lessons and preserved results | Already represented. The unsent packet does not satisfy the session. No duplicate teacher tasks added |

## Twelve GSS demonstrations

The [GSS guide](Dia1/Exercicios-GSS/README.md) and
[module 1](Dia1/Exercicios-GSS/modulo1/README.md) /
[module 2](Dia1/Exercicios-GSS/modulo2/README.md) indexes were checked separately
from the research exercises. Each entry already has its own execution task in
checklist section 4:

| Lesson | Tracked activity |
| --- | --- |
| Module 1 / 01 | Supervised/unsupervised learning and Flappy Bird Q-learning |
| Module 1 / 02 | Matrices, flattening and MLP forward pass |
| Module 1 / 03 | Loss, backpropagation, optimization and training cycles |
| Module 1 / 04 | Confusion, thresholds, precision/recall, costs and ROC |
| Module 1 / 05 | Training/validation/test and drawing without parameter updates |
| Module 1 / 06 | Five YOLO tasks, model preparation and image/video/webcam boundaries |
| Module 2 / 01 | Tokens, IDs and didactic vocabulary |
| Module 2 / 02 | Embeddings and sentence similarity |
| Module 2 / 03 | Didactic attention and causal masking |
| Module 2 / 04 | Generation, temperature and top-p |
| Module 2 / 05 | Classification, summarization and extraction prompts |
| Module 2 / 06 | Image/text inference and limitations |

Environment setup, UCI/MNIST separation, optional vision dependencies, recorded
language mode, source provenance, offline tests and execution limits are also
explicit. Recorded-response mode is allowed by the guide; live LM Studio is not
an additional mandatory task. Webcam selection does not prove capture, and that
limit is already declared. The successful suite evidence and selected CNN split,
shape/gradient and export tests exist; no duplicate blanket “write tests” or
“validate MNIST” task is added merely because a fresh audit did not rerun them.

## New follow-ups and acceptance boundaries

| ID | Checklist location and deliverable | Dependency |
| --- | --- | --- |
| R01 | Section 3: record the participant's actual critique, instruction/question choices and review of the research/paper/synthesis/audit outputs; retain original assistant-authorship declarations | Participant input; no teacher needed |
| R02 | Section 3 / Exercise 2: add an accessible explanation and compare two candidate readings of a specific passage in each note, with source locators and support/rejection boundaries | Local source analysis; do not manufacture ambiguity or participant dialogue |
| R03 | Section 7 / Part 1: inspect reference Issue #1; record scope, dependencies, acceptance criteria and evidence conventions to adopt | Read-only GitHub access; access failures must remain visible |
| R04 | Section 7 / Part 1: inspect reference PR #2 Conversation, Files changed and Checks, identifying what a reviewed change proves and what the simple classifier does not prove | Read-only GitHub access; creating a new PR is not made mandatory |
| R05 | Section 7 / Part 1: map all required phases to actual personal Issues and evidence; identify uncovered work and label retrospective records honestly | Existing Issue snapshots/source; remote verification when updating |
| R06 | Section 7 / Part 1: obtain participant review of the present technical specification and executable Issue acceptance criteria before any further implementation | Participant approval; this cannot establish original pre-implementation approval or instructor acceptance |
| R07 | Section 7 / Part 2: synchronize real Issues with delivered evidence, exact commits, acceptance results and remaining scope; close only when each criterion is satisfied | Authorized GitHub writes; no teacher message or invented approval |
| R08 | Section 7 / Part 2: verify a documented clean setup path for data loading, training and evaluation, including dependency versions, baseline checkpoints, split identities and font/data inputs | Dependency recovery; a full expensive retraining is not automatically required or authorized |
| R09 | Section 7 / Part 2: demonstrate repeatable evaluation and genuine predictions for the selected trained model through a command that writes only a new report | Restored selected artifacts; no official challenge inputs, new model selection or frozen-report overwrites |
| R10 | Section 10: publish participant deliverable commits to the personal GitHub repository and verify remote starter, skill, context, code, evidence links and commit URLs | GitHub write access and publication authority; existing website and Pages settings stay intact |
| R11 | Section 6: reconcile active project context and the local Issue register with completed work and actual remaining dependencies, preserving historical snapshots and generic starter rules | Local documentation; approval only if confirmed requirements actually change |
| R12 | Section 7 / Part 3: record a version-identified review of reference drawing/upload, score display, preprocessing, inference, activations/contributions, tests/parity and Pages workflow, with reuse/discard and attribution decisions | Read-only reference source; no copying or deployment is required to complete the review |

R08 and R09 are deliberately separate: explaining how training can be reproduced
does not demonstrate that selected-model evaluation can actually be repeated.
The current `digitlab.residual_evaluate` workflow guards completed experiment
records and includes export/test writes. It must not simply be rerun against its
old destinations to clear the new evaluation task. A safe path may be an existing
read-only evaluator or a scoped new command after checking what already exists.

The source publication gap was visible in the previous handover: later commits
were local while remote `main` was at a preparation commit. That is prior observed
state, not a fresh remote check in this audit. An index of local files is a local
delivery, not evidence that reviewers can obtain those commits from GitHub.

## What is not a newly discovered mandatory requirement

The course allows a chosen architecture and commits **or** Pull Requests. It
does not require the reference MLP, a fixed Issue count, a newly created participant
PR, 10/10 CAPTCHA accuracy, a standalone repository for each artifact, external
skill installation, live language models, physical touch hardware, a dependency
upgrade, or a new CI pipeline for the participant model. Such engineering work can
be proposed separately; it is not inserted as a missing course requirement.

The explicit Copilot and Pages wording remains a course-route difference pending
instructor acceptance. This audit does not reverse the participant's decisions
to use the current assistant, preserve the existing site or defer instructor
contact. Historical first-run records, reports, model binaries and deployment
assets are unchanged. The [submission handover](SUBMISSION.md) remains an artifact
delivery index; the new unchecked tasks qualify its overall completion status.

The [validation record](participant-work/day2/exercise-coverage-validation.json)
records the reviewed source hashes, checklist delta, relative links and heading
anchors. Validation of this documentation does not execute any of R01–R12.
