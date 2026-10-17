# Reading, synthesis, and audit process

Date: 2026-10-17. This batch covers the next ten unchecked items in [TASKS.md](../../TASKS.md): three remaining Exercise 2 tasks, all five Exercise 3 tasks, and the first two Exercise 4 tasks. English and the current assistant follow the participant's [working decisions](../../PREPARATION.md#working-decisions).

## Reading and synthesis

The assistant formulated broad-to-specific questions for both papers, retrieved their versioned primary texts, checked answers against the identified sections/tables, and saved [two](reading-transformer.md) [notes](reading-flashattention.md). Author claims and results are labelled; answers are paraphrases, while conclusions are labelled inference. These are the recorded questions and checked answers rather than a fabricated transcript of participant dialogue. No paper experiments were reproduced.

The [original synthesis](synthesis-original.md) combines those notes, the [prior report](research-report.md), both papers, and a separately identified theory source. It distinguishes source evidence, theory-dependent accounts, interpretation, and speculation. The [integrity record](synthesis-preservation.json) captures the original bytes before the audit output existed. The original is to remain unchanged.

## Fresh audit session

The checklist expressly calls for a new conversation. A fresh reviewer agent session named `synthesis_audit` was started with no inherited chat history (`fork_turns=none`). It received file paths and an audit request, then read the original and supporting documents itself. This is a declared adaptation using the chosen assistant rather than Copilot. The separate agent uses shared files and is not an independent human reviewer or proof that model bias has been removed. Instructor acceptance remains unconfirmed.

The request instructed the reviewer to inspect claims, citations, omissions, confidence, and format, use a second review approach, and save concrete proposed edits with section targets, source locators, severity, and limitations. It explicitly prohibited edits to the original or creation of a revised paper. The resulting [audit](synthesis-audit.md) preserves proposed changes for the next task.

This batch ends before the second fresh conversation for revision. No final revised paper or correction summary is claimed. The audit's findings must be resolved and source-checked during that later work.

Subsequent batch, 2026-10-17: another fresh agent session produced the [final revision](synthesis-final.md) and [correction record](synthesis-corrections.md), including targeted primary-source checks. The paragraph above records the earlier batch boundary; it is not the current revision status. The original and audit remain preserved separately.

## Validation

Validation checks file links and local heading anchors in the changed Markdown, verifies that exactly ten checklist items changed to complete, recomputes the preserved original's SHA-256, and checks Git whitespace. Results are recorded after execution below. No training, challenge evaluation, or application test is appropriate for these documentation artifacts.

Executed results: 99 relative file links and 10 local heading anchors passed; exactly 10 additional checklist items are complete. The original's SHA-256 still matches `06bddb955a1091a3c1be22717e6c57bd7a6c0d4685b543e7f2a193ef0595960a`. `git diff --check` passed. A temporary Python validator performed the link, heading, checklist-count, and hash checks and was removed after use. Existing unrelated untracked files were preserved.

The audit contains six proposed clarifications/corrections (A1-A6) and two keep decisions (A7-A8). These remain proposals for the next revision session; the audit does not certify that the original needs no changes.
