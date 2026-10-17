# Course Completion Tasks

Initial assessment date: 2026-10-17. This checklist covers both course participation and repository maintenance. It is based on the local exercise instructions, source layout, workflows, study answers, and recorded implementation evidence. The initial documentation audit did not independently check remote GitHub state, the live website, GUI behavior, test suites, or PDF contents. The subsequent [preparation record](PREPARATION.md) documents the Git connectivity check and slide review completed for the first five open tasks, including their limits.

An unchecked task means work or completion evidence is still needed; it does not necessarily mean the functionality is absent. Checked items identify existing artifacts or recorded results, rather than fresh execution. Historical reports remain valid for their named versions.

## 1. Folder coverage and existing work

| Location | Purpose and completion implications |
| --- | --- |
| [Dia1](Dia1/README.md) | Four research exercises; participant deliverables were not found in this repository. |
| [GSS exercises](Dia1/Exercicios-GSS/README.md) | Twelve implemented Python demonstrations, support modules, resources, recordings, and unit tests; run and observe them. |
| [Day 1 slides](Dia1/Teorico/) and [Day 2 slides](Dia2/Teorico/) | Teaching references; review alongside the corresponding exercises. |
| [Dia2](Dia2/README.md) | Four exercises, including four parts of the classifier project. |
| [MNIST](Dia2/Dataset-MNIST/README.md) | Four compressed IDX archives and an integrity-checking downloader already exist. |
| [Official challenge](Dia2/Desafio/README.md) | Ten final-evaluation PNGs; preserve them and exclude them from training and tuning. |
| [Starter reference](Dia2/Referencia-Starter-Repo/LEIA-PRIMEIRO.md) | Agent instructions, procedures, context/knowledge templates, and capability registries for selective adaptation. |
| [Study answers](Dia2-Answers/README.md) | English explanations and proposed answers; these do not prove completion of practical activities. |
| [Local implementation](dia2-local/README.md) | Existing trained models, static website, training/evaluation utilities, tests, documentation, and release evidence. Extend this implementation rather than building a duplicate. |
| [.github](.github/) | Custom agent and three workflows; concrete maintenance issues appear below. |
| [Day 2 proposal](DIA2-PROPOSTA.md) | Earlier preparation proposal; reconcile its pending claims with subsequent implementation. |
| Root documentation | Course navigation, contribution instructions, licensing, attribution, and citation metadata. |

- [x] Locate all twelve GSS entry scripts and their support/resource/test folders.
- [x] Locate MNIST archives, the downloader, and all ten official challenge PNGs.
- [x] Locate the implemented classifier, browser application, and recorded training/evaluation evidence.
- [x] Identify recorded public deployment and public challenge follow-up evidence. For example, the [v3.7.0 public verification](dia2-local/reports/release-3.7.0-public-challenge-verification.json) records 10/10 and agreement with frozen local inputs/scores. This is a later verification, not the original independent test.
- [x] Locate [v3.10.0 public interface evidence](dia2-local/reports/release-3.10.0-public-ui-qa.json); its real-model and CAPTCHA accuracy checks are explicitly marked `NOT RUN` in that report.

## 2. Preparation

- [x] Resolve the assistant choice and access prerequisite: the participant explicitly declined Copilot; continue with the current assistant and verified local tools. This replaces the original Copilot access check by participant decision, without claiming instructor acceptance. See [working decisions](PREPARATION.md#working-decisions).
- [x] Prepare Git, a personal GitHub repository, and a GitHub Pages publication destination. Verified the existing personal remote and selected the future Pages URL/static artifact source; actual Pages configuration/publication remains Part 3 work. See [repository and destination](PREPARATION.md#git-repository-and-pages-destination).
- [x] Establish the participant's working preferences: English, the current assistant, autonomous work within the requested batch, evidence/diff review, and the expressly authorized commit/push. See [working decisions](PREPARATION.md#working-decisions).
- [x] Review the Day 1 and Day 2 slides with their corresponding lessons; record questions to resolve during the course. All eleven decks were inspected through text extraction or visual contact sheets; see [review notes and limits](SLIDE-REVIEW.md).
- [x] Keep participant submissions in their own repository and decide how to reference the existing implementation: retain `dia2-local/` in the existing personal fork with root Git history and preserve ignored artifacts separately. See [preservation plan](PREPARATION.md#preserve-and-reference-the-existing-implementation) and [artifact hashes](preparation-artifacts.json). No migration or off-machine backup is claimed.

Participant route update (2026-10-17): Copilot will not be used, by explicit participant instruction. The original exercise links retain their course wording. For future work, adapt tool-specific steps to the chosen assistant while preserving the learning objectives and declaring any rubric differences. Fresh-session checks, skill behavior, and instructor acceptance still require their own evidence.

## 3. Day 1 — Research exercises

Complete in order; each exercise consumes the preceding outputs. The initial audit found no participant research submissions. The 2026-10-17 batch adds the [research submission](participant-work/day1/README.md), using the participant's chosen assistant and English; instructor acceptance of the Copilot substitution remains unconfirmed.

### Exercise 1 — Guided research

Source: [research instructions](Dia1/Exercicio-01-Pesquisa-Orientada.md).

- [x] Define the research objective, timeframe, scope, questions, acceptable evidence, report structure, and length. See the [research brief](participant-work/day1/research-brief.md).
- [x] Develop and refine research instructions for LLM evolution, Transformers, multimodality, MoE, and attention efficiency using the chosen assistant. See [instruction revisions and authorship limits](participant-work/day1/research-brief.md#initial-instruction-specification); this is the declared adaptation of the Copilot task.
- [x] Verify important claims against traceable sources and distinguish evidence, interpretation, and uncertainty. See the [verification ledger and access limits](participant-work/day1/source-verification.md).
- [x] Save the structured Markdown report, conclusions, uncertainties, and source list for subsequent exercises. See the [2017-2023 research report](participant-work/day1/research-report.md).

### Exercise 2 — Talk to a Paper

Source: [paper analysis instructions](Dia1/Exercicio-02-Talk-to-a-Paper.md).

- [x] Select two scientific papers from Exercise 1 and provide their contents to the chosen assistant; record document-access limitations. See the [versioned full-text handoff](participant-work/day1/paper-selection.md); no Copilot upload is claimed.
- [x] Ask progressive questions about each paper's problem, objectives, methods, data, results, assumptions, and limitations. See the assistant-formulated questions in the [Transformer](participant-work/day1/reading-transformer.md) and [FlashAttention](participant-work/day1/reading-flashattention.md) notes; no participant dialogue is fabricated.
- [x] Check responses against identifiable sections/pages and separate author claims, paraphrases, and model inference. Both [reading notes](participant-work/day1/README.md) identify source sections/tables, answer status, and inference; PDF pagination and replication were not verified.
- [x] Save two reading notes with grounded questions/answers, conclusions, and references to the original papers. See [Transformer](participant-work/day1/reading-transformer.md) and [FlashAttention](participant-work/day1/reading-flashattention.md).

### Exercise 3 — Cross-source synthesis

Source: [synthesis instructions](Dia1/Exercicio-03-Cruzamento-de-Fontes.md).

- [x] Combine the research report, both papers, and their reading notes with traceable source identities. See the [original synthesis source map](participant-work/day1/synthesis-original.md#materials-and-source-identities).
- [x] Investigate the speculative attention/training/consciousness question, defining ambiguous terms and examining supporting and opposing arguments. See the [original synthesis](participant-work/day1/synthesis-original.md); its analogy is conditional and does not establish subjective experience.
- [x] Identify agreements, contradictions, redundancy, and missing evidence across the sources. See the [cross-source comparison](participant-work/day1/synthesis-original.md#agreements-tensions-and-missing-evidence).
- [x] Save an argued synthesis that explicitly separates established evidence, interpretation, and speculation. See [version 1](participant-work/day1/synthesis-original.md).
- [x] Preserve the original synthesis for the next exercise. See the [pre-audit SHA-256 record](participant-work/day1/synthesis-preservation.json); the original remains unchanged after review.

### Exercise 4 — Audit and refinement

Source: [audit instructions](Dia1/Exercicio-04-Auditoria-e-Refinamento.md).

- [x] Start a fresh reviewer session with the chosen assistant to audit claims, citations, omissions, confidence, and requested format. See the [session adaptation and limits](participant-work/day1/review-process.md#fresh-audit-session); this uses a reviewer agent without inherited chat history, not Copilot or independent human review.
- [x] Save at least one Markdown audit containing proposed edits before changing the original paper. See the [audit and proposed edits A1-A8](participant-work/day1/synthesis-audit.md); revision remains the next task.
- [x] Use another fresh session with the original paper and audit to produce a traceable revision. See [final version 2](participant-work/day1/synthesis-final.md) and the [declared session adaptation](participant-work/day1/synthesis-corrections.md#session-and-chosen-route).
- [x] Verify disputed claims using the original sources; repeat review if necessary. See the [targeted versioned-source checks](participant-work/day1/synthesis-corrections.md#targeted-primary-source-verification), two comparison methods, and unresolved limits.
- [x] Deliver the final paper, preserved audit, and a brief record of the principal corrections. See the [final paper](participant-work/day1/synthesis-final.md), [unchanged audit](participant-work/day1/synthesis-audit.md), and [A1-A8 correction record](participant-work/day1/synthesis-corrections.md).

## 4. Day 1 — GSS Python demonstrations

Source: [setup and validation guide](Dia1/Exercicios-GSS/README.md). These are existing demonstrations to execute and understand; no missing implementation was established by this audit.

- [x] Create or reuse the GSS virtual environment, install base requirements, and verify Tk GUI availability. Created the ignored GSS environment; [setup](participant-work/day1/gss-evidence/setup.json) records installation/imports/pip checks. The [Tk walkthrough](participant-work/day1/gss-observations.md#environment-and-method) used the verified existing environment while installation completed.
- [x] Prepare the UCI Optical Digits cache for module 1 exercises 02, 03, and 05; keep this 8×8 dataset separate from Day 2 MNIST. See [dataset boundary](participant-work/day1/gss-observations.md#dataset-boundary) and the archive hash/counts in [execution evidence](participant-work/day1/gss-evidence/execution.json).
- [x] Run module 1 exercise 01: compare supervised/unsupervised learning and observe Flappy Bird Q-learning. See [observations and screenshots](participant-work/day1/gss-observations.md#observed-lessons); 200 episodes updated Q-values but did not establish improved play.
- [x] Run module 1 exercise 02: inspect image matrices, flattening, and the MLP forward pass. See the [recorded untrained forward pass](participant-work/day1/gss-observations.md#observed-lessons) and [GUI](participant-work/day1/gss-evidence/02-forward.png).
- [x] Run module 1 exercise 03: observe loss, backpropagation, optimization, and training cycles. See [21-update observations](participant-work/day1/gss-observations.md#observed-lessons) and [GUI](participant-work/day1/gss-evidence/03-learning.png).
- [x] Run module 1 exercise 04: explore confusion matrices, thresholds, precision/recall, costs, and ROC behavior. See [threshold measurements](participant-work/day1/gss-evidence/execution.json), [cost GUI](participant-work/day1/gss-evidence/04-costs.png), and [ROC GUI](participant-work/day1/gss-evidence/04-roc.png).
- [x] Run module 1 exercise 05: train/evaluate the digit MLP and test drawing inference without treating it as additional training. See [12-epoch observations](participant-work/day1/gss-observations.md#observed-lessons), [evaluation](participant-work/day1/gss-evidence/05-evaluation.png), and [drawing](participant-work/day1/gss-evidence/05-drawing.png); frozen parameter hashes agreed before/after inference.
- [x] For the optional vision exercise, install `requirements-visao.txt` and prepare YOLO weights using `--preparar` before class. Installed and prepared all five models during this batch; no retrospective pre-class timing is claimed. See [preparation and hashes](participant-work/day1/gss-vision-language.md#preparation-and-method).
- [x] Run module 1 exercise 06: inspect classification, detection, segmentation, pose, and oriented boxes using the intended image/video/webcam inputs; distinguish model scores from accuracy. Real five-task image inference and local video stepping ran; webcam selection was checked without activation. Live camera capture remains unverified. See [observations and input limits](participant-work/day1/gss-vision-language.md#vision-module-1-exercise-06).
- [x] Enable recorded-response mode for module 2, or configure the documented LM Studio endpoint and compatible models for live demonstrations. Explicit offline mode used the unchanged recordings; see [mode and reproduction](participant-work/day1/gss-vision-language.md#recorded-language-mode).
- [x] Run module 2 exercise 01: compare text, tokens, IDs, and the didactic vocabulary. Compared all four prepared texts, vocabulary/unknown tokens, missing-recording handling and clearing; see [token observations](participant-work/day1/gss-vision-language.md#tokens-module-2-exercise-01).
- [x] Run module 2 exercise 02: explore embeddings and sentence similarity. Inspected full-vector neighbours, a recorded suggestion, banco ambiguity, missing-vector handling and reset; see [embedding observations](participant-work/day1/gss-vision-language.md#embeddings-module-2-exercise-02).
- [x] Run module 2 exercise 03: inspect attention weights and causal masking. Compared both matrices, row normalization and future-token masking; clicked a matrix row and checked navigation/reset. See [attention observations](participant-work/day1/gss-language-final.md#exercise-03-attention-and-causal-masking).
- [x] Run module 2 exercise 04: explore next-token generation, temperature, and top-p. Compared four sampling settings and three contexts, undo/restart, recording-boundary recovery and end-token stopping. See [generation observations](participant-work/day1/gss-language-final.md#exercise-04-next-token-generation).
- [x] Run module 2 exercise 05: compare classification, summarization, and extraction prompts. Compared seven recorded configurations, including rule failure and eight-token truncation. See [prompt comparisons](participant-work/day1/gss-language-final.md#exercise-05-prompt-comparison).
- [x] Run module 2 exercise 06: inspect image/text inference and its limitations. Inspected nine recorded image/request pairs, chart values, crack observations and unsupported conclusions. See [image/text limits](participant-work/day1/gss-language-final.md#exercise-06-imagetext-outputs-and-limits).
- [x] Run the documented offline unit suite and investigate failures; manually check the affected windows and interactions. All 125 tests passed after reviewed sandbox escalation; two preceding temporary-directory failures are preserved. Scripted Tk controls and assistant visual review of figure renderings supplement the tests. Human desktop interaction remains unverified. See [test attempts and result](participant-work/day1/gss-language-final.md#offline-tests-and-failed-attempts).
- [x] Record what was actually run, observations, environment limitations, and whether outputs were live or recorded. Preserve resource attribution and `origem.json` provenance. See the [consolidated twelve-lesson delivery](participant-work/day1/gss-language-final.md#consolidated-gss-delivery-and-reproduction), separate execution records and unchanged provenance hashes.

## 5. Day 2 — Exercise 1: Reusable starter repository

Source: [starter instructions](Dia2/Exercicio-01-Starter-Repo.md). The [reusable starter source](participant-work/starter/README.md) and [preparation record](participant-work/day2/starter-preparation.md) are supplemented by [reference review, scoped fresh-session reuse and generic preservation](participant-work/day2/starter-next-five.md). It remains in the personal fork; separate publication and native Copilot discovery remain unverified.

- [x] Create the personal reusable starter with concise agent rules, a Copilot entry point, and documentation explaining reuse. See the [starter](participant-work/starter/README.md) and [scope adaptation](participant-work/day2/starter-preparation.md#deliverable-and-scope); this is source in the personal fork, not a separately published repository or verified Copilot session.
- [x] Define planning, execution, verification, review, Git, security, and autonomy procedures that match the participant's preferences. See [workflow](participant-work/starter/procedures/workflow.md) and [Git/safety](participant-work/starter/procedures/git-and-safety.md).
- [x] Provide persistent context, decisions, reusable knowledge, and evidence records with clear responsibilities. See [responsibilities and acceptance](participant-work/day2/starter-preparation.md#responsibilities-and-acceptance); project-specific requirements remain deliberately unconfigured.
- [x] Document useful skills, CLI tools, and MCP capabilities; distinguish documented capabilities from verified availability. See [capability contracts](participant-work/starter/capabilities/README.md) and [scoped local probes](participant-work/day2/starter-preparation.md#environment-evidence); catalogs are not treated as verified service access.
- [x] Record what was copied, adapted, or discarded from the reference and why; preserve applicable attribution. See the [selection and attribution record](participant-work/day2/starter-reference-selection.md).
- [x] Test a fresh session, reuse for an unrelated hypothetical project, and a safe agent task; save observed behavior and correct failures. See the [no-history agent experiment](participant-work/day2/starter-fresh-session.md); explicit chosen-assistant loading, not Copilot auto-discovery.
- [x] Preserve an identifiable generic starter version before classifier-specific context is added. Do not describe a later reconstruction as proof that the original sequence occurred. See the [actual pre-skill archive and manifest](participant-work/day2/starter-next-five.md); no classifier context was added.

## 6. Day 2 — Exercise 2: Bootstrap interview skill

Source: [bootstrap instructions](Dia2/Exercicio-02-Skill-Bootstrap.md). The study answer remains a design explanation; [research and participant skill source](participant-work/day2/starter-next-five.md) now exist separately. Format validation does not establish behavioral testing or native Copilot discovery.

- [x] Research interview-style skills and the Ask Me pattern, recording sources and useful design choices. See the [research and access limitations](participant-work/day2/bootstrap-research.md).
- [x] Create the participant's native Copilot skill at `.github/skills/<skill-name>/SKILL.md` in the personal starter, with appropriate metadata and instructions; no special installer is required. See [bootstrap-project](participant-work/starter/.github/skills/bootstrap-project/SKILL.md); authored through the chosen assistant, format validated, Copilot execution unverified.
- [x] Make the skill inspect existing context, ask adaptive questions, clarify contradictions, avoid repetition, and distinguish facts, assumptions, and pending decisions. See [controlled behavior evidence](participant-work/day2/bootstrap-behavior.md); no fabricated participant answers.
- [x] Require a reviewable context proposal and participant approval before the skill writes project context. [Unchanged hashes before synthetic approval and writes afterward](participant-work/day2/bootstrap-behavior.md) test the boundary; synthetic approval is not actual participant approval.
- [x] Apply it to the classifier requirements while preserving generic starter rules; support subsequent updates without restarting the interview. See [populated preservation context](participant-work/starter/context/project.md), the participant's current-website directive and [bounded update/recovery evidence](participant-work/day2/bootstrap-recovery.md).
- [x] Verify actual Copilot discovery/use, insufficient-context behavior, approval handling, and fresh-session recovery; preserve evidence. **Chosen-assistant adaptation:** explicit skill loading and [two no-history session records](participant-work/day2/bootstrap-next-ten.md); Copilot discovery/use was not tested because the participant declined it. Instructor acceptance remains pending.
- [x] Version the skill and populated context. Do not substitute a downloaded external skill for the participant's implementation. See [version hashes and provenance](participant-work/day2/bootstrap-context-version.json); participant-authored skill source retained, no third-party installation.

## 7. Day 2 — Exercise 3: Classifier project

### Part 1 — Planning and GitHub Issues

Source: [planning instructions](Dia2/Exercicio-03/Parte-01-Planejamento-da-Rede.md).

- [x] Reconcile the existing experiment decisions with an approved project specification covering inputs/outputs, architecture alternatives, resource constraints, preprocessing, data splits, metrics, export, browser parity, UI, and publication. See [retrospective specification](participant-work/day2/classifier-specification.md); participant confirmed preservation of the current development/site, not new technical design or original pre-implementation approval.
- [x] Locate and link any real personal GitHub Issues and original approvals; local task notes are insufficient evidence of published Issues. [Initial public audit](participant-work/day2/github-issues-before.json) returned no Issues; no original approval established in the inspected records. [New real Issues and search limits](participant-work/day2/issue-register.md) are explicitly retrospective.
- [x] Create missing Issues for remaining work with scope, dependencies, acceptance criteria, and verification evidence. Record existing implementation honestly as retrospective context. [Six published Issues #2–#7](participant-work/day2/issue-register.md) cover remaining evidence, artifacts, verification, hosting and instructor decisions; current website preserved.
- [ ] Identify the missing pre-implementation approval trail explicitly and seek the instructor's acceptance of that process deviation; later Issues cannot establish earlier approval. Gap recorded and [request prepared](participant-work/day2/instructor-process-request.md), but **not sent**: instructor recipient/channel and actual acceptance are external dependencies. Tracked in [Issue #7](https://github.com/monkzzz/Formacao-de-IA/issues/7).
- [x] Verify that a fresh agent session can identify the next actionable Issue using repository context alone. See [no-history recovery](participant-work/day2/bootstrap-recovery.md): real Issue #2, dependencies, verification and preservation limits.

### Part 2 — Training and evaluation

Source: [implementation instructions](Dia2/Exercicio-03/Parte-02-Coding-com-o-Agente.md).

- [x] Existing implementation includes MNIST loading, separated training/validation, genuine CNN training, exported weights, metrics, and original evaluation records.
- [x] Existing tests and browser verification tools cover learning/inference behavior and Python/JavaScript parity.
- [ ] Assemble a submission evidence index linking the selected model to its configuration, seed, split, environment, training history, held-out metrics, confusion/error analysis, preprocessing, and weight hash.
- [ ] Run the existing relevant unit suite for the selected submission version and record the actual result; do not reuse historical test counts as a current result.
- [ ] Confirm that a clean environment can obtain the correct ignored weights/checkpoints or reproduce them through documented training commands. Preserve existing frozen outputs instead of overwriting them.
- [ ] Link reviewed changes and final commits to the personal project's Issues, including explicit limitations and deviations.

### Part 3 — Browser application and publication

Source: [website instructions](Dia2/Exercicio-03/Parte-03-Site-GitHub-Pages.md).

- [x] Existing application provides drawing, clearing, local image uploads, model scores, and real network information with browser inference.
- [x] Recorded public releases exist on the separately hosted HTTPS application; public deployment is no longer wholly missing.
- [ ] Publish the participant repository and selected application on GitHub Pages, or obtain instructor acceptance of the existing hosting substitution.
- [ ] Supply the ignored model binaries required by the static deployment through a documented artifact process; a source checkout alone does not include them.
- [ ] Verify the submitted origin's loading, drawing with mouse/touch, individual/batch uploads, clear/reset, per-image results, real activations, and failure recovery.
- [ ] Verify preprocessing and inference parity for the selected trained CNN, and confirm that classification is executed in-browser without a remote inference API.
- [ ] Clearly distinguish the participant-trained default CNN from optional pretrained digit/word readers; those extensions do not replace the trained-model deliverable.
- [ ] Record the submitted URL, release/commit, model identity, validation results, and screenshots. Include model scores and limitations without presenting softmax as calibrated correctness probability.

### Part 4 — Official CAPTCHA challenge

Source: [challenge evaluation instructions](Dia2/Exercicio-03/Parte-04-Teste-do-Desafio.md).

- [x] Original frozen local evaluation and separate comparison exist: 99.28% MNIST and 2/10 official CAPTCHA cases.
- [x] Later frozen iterations and public verification exist, including the recorded v3.7.0 10/10 follow-up; preserve their distinct identities and evaluation histories.
- [ ] Select and link the complete evidence chain for the submitted version: frozen runtime/weights, ten raw predictions and scores, separate comparison, input hashes, errors/limitations, and public verification where applicable.
- [ ] If a new GitHub Pages origin or changed submission needs checking, verify it against the already frozen results and label it as deployment verification after prior challenge exposure.
- [ ] Preserve original records and explain that later evaluations are follow-ups. Never use the official images, known answers, filenames, or completed test caches to tune the model or preprocessing.
- [ ] Report MNIST, synthetic robustness, and ten-image challenge results separately. A perfect ten-image score is not required for course completion and does not establish general CAPTCHA accuracy.

## 8. Day 2 — Exercise 4: Teacher feedback and corrections

Source: [feedback instructions](Dia2/Exercicio-04-Roda-de-Feedback.md). No completed teacher feedback session was established locally.

- [ ] Provide the teacher with the personal repository, starter, skill, Issues, public URL, trained model identity, and evaluation evidence.
- [ ] Participate in the actual teacher/class feedback session and record the date, reviewer, tested URL/version, observed behavior, and questions discussed.
- [ ] Distinguish reproduced problems from suspected causes; create or update Issues with reproduction steps and acceptance criteria.
- [ ] Prioritize functional and integrity problems, investigate selected corrections with the agent, and preserve before/after evidence.
- [ ] Review diffs, run relevant regression checks, and link correction commits and any published versions to their Issues.
- [ ] Record resolved and unresolved findings with next actions, and add reusable lessons to the starter.
- [ ] Preserve original challenge results when corrections create a new iteration; do not claim teacher approval before it occurs.

## 9. Repository maintenance findings

These are concrete documentation/automation issues found locally; complete them separately from participant submissions.

- [ ] **Repair the challenge evaluation workflow:** [.github/workflows/avaliar-desafio-avancado.yml](.github/workflows/avaliar-desafio-avancado.yml) invokes `Dia2/Desafio/avaliar_captcha_no_site.py`, which is absent from the inspected file inventory. Restore a suitable evaluator or update the workflow to a maintained implementation; verify its CLI, dependencies, output artifact, and failure reporting.
- [ ] **Resolve challenge output paths:** the generator and [.github/workflows/gerar-desafio-avancado.yml](.github/workflows/gerar-desafio-avancado.yml) target `Dia2/Desafio/Avancado/`, whereas the official ten files are directly in `Dia2/Desafio/`. Decide whether this is an explicit separate set or stale behavior and align code/workflow/documentation without silently replacing the reserved evaluation images. Verify generation in an isolated output directory.
- [ ] **Correct the challenge count:** [the MNIST guide](Dia2/Dataset-MNIST/README.md) still says nine challenge images/cases; the official set has ten.
- [ ] **Reconcile current and historical status:** `Dia2-Answers/`, `DIA2-PROPOSTA.md`, and the local README/audit contain earlier local-only or pending-publication claims. Add a dated current status and link later releases while preserving historical findings and original metrics.
- [ ] **Clarify release documentation:** the local README describes v3.7.0 as current, while release evidence reaches v3.10.0; the hosting guide contains multiple historical sections labelled current. Establish one clearly identified submission release and label older sections by version.
- [ ] **Complete or label the custom agent template:** [.github/agents/Jarvis.agent.md](.github/agents/Jarvis.agent.md) retains placeholder description, argument hint, and closing instructions. Define its intended scope and discovery behavior or clearly mark it as an unfinished example; check that its bootstrap policy fits this course repository.
- [ ] **Update root navigation:** document the role of `Dia2-Answers/`, `dia2-local/`, the proposal, and this checklist, while making the separate student-repository requirement clear.
- [ ] **Review existing untracked files individually:** the initial Git status contains two local JPGs and several raw/follow-up reports. Decide which are required evidence, duplicates, or local-only artifacts; do not delete or stage them indiscriminately.
- [ ] **Check teaching assets and attribution:** verify slide links/order/size claims, resource provenance, third-party notices, and consistency between `LICENSE.md` and `CITATION.cff`; review PDF contents manually where necessary.
- [ ] **Validate maintenance changes:** check relative links, exercise numbering, workflow script paths, and relevant script behavior. Run GSS or Digit Lab tests only when their corresponding behavior changes; do not retrain or rerun the official challenge for documentation edits.

## 10. Completion and handover

Recommended order: repair broken course automation/documentation; collect missing Day 1 outputs; establish starter/skill evidence; reconcile project Issues and process deviations; finalize the existing model/app submission; publish on Pages or document the accepted substitution; complete teacher feedback.

- [ ] Deliver the Day 1 report, two reading notes, original synthesis, audit, final revision, and correction summary.
- [ ] Deliver the GSS execution/observation record and relevant validation results.
- [ ] Deliver the personal starter, bootstrap skill, approved project context, and actual fresh-session test evidence.
- [ ] Deliver repository/Issue/commit URLs, the trained-model evidence index, deployment URL, and preserved challenge records.
- [ ] Deliver the teacher feedback log, correction evidence, and explicit remaining limitations or instructor-accepted deviations.
- [ ] Update this checklist using linked evidence. Treat account access, instructor decisions, and real classroom activities as external dependencies rather than completed work.

Creating this checklist does not execute the tasks, publish anything, create GitHub Issues, or certify course completion.
