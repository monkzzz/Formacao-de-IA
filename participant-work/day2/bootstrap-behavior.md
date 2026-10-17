# Bootstrap behavioral validation — 2026-10-17

Status: awaiting controlled synthetic participant input. No approval or dialogue was fabricated.

Prompt: “Bootstrap an image sorting tool for volunteers. Use our hosted API to upload each image for classification. I have not yet decided what categories it should return. Please prepare the context.”

Explicitly loaded `.bootstrap-fixture/.github/skills/bootstrap-project/SKILL.md`. Read only the fixture and applicable instructions: external `C:/Users/falle/.codex/RTK.md`, fixture `AGENTS.md`, `README.md`, `context/project.md`, `context/decisions.md`, `context/handoff.md`, `procedures/workflow.md`, `procedures/git-and-safety.md`, and `evidence/README.md`. Enumerated fixture nested AGENTS.md files; only its root agreement was found. Inspected fixture-scoped Git status: exit 0, empty output. This was explicit skill loading in the current assistant, not native Copilot auto-discovery.

Exact synthetic-user response:

> I loaded the bootstrap-project skill and read the starter rules, README, project context, decision register and handoff. I will prepare a reviewable proposal for `context/project.md`, `context/decisions.md` and `context/handoff.md` before writing context.
>
> Your request confirms an image sorting tool for volunteers and proposes uploading images to your hosted classification API. Existing `context/project.md` says the project must work offline and must not upload images to a server, labelled as a synthetic fixture fact. These requirements conflict.
>
> 1. Which requirement should govern: retain offline processing with no image uploads, or replace that restriction with use of your hosted API?
> 2. Should the category set remain an explicit pending decision, with the context limited to discovery until you choose it? If you already know the sorting purpose, what outcome should the volunteers achieve?
>
> Once you answer, I can present the concrete context proposal with confirmed facts, pending choices and acceptance checks for your approval. No context files have been changed.

Observed decisions: surfaced the source conflict before assuming precedence; asked the highest-consequence question first; retained categories as unresolved rather than selecting labels or classifier architecture. Deferred API contract questions until the governing processing requirement is resolved. No implementation, upload, external service, commit or context write was attempted. Approval is required by the explicitly loaded skill's “Reviewable proposal” instruction before context writes; the current questions are requirements discovery, not a request to approve unseen content.

Context SHA256 before interview and after stopping (identical; verified with Get-FileHash):

| File under fixture | Before | After |
| --- | --- | --- |
| `context/project.md` | `5750C65261A149E724424BC12B3F351FACA300AECBF1C0B7ECE87E8D33F08AF8` | `5750C65261A149E724424BC12B3F351FACA300AECBF1C0B7ECE87E8D33F08AF8` |
| `context/decisions.md` | `B5F89E76799364DD67F6B7F4EE5786711A8DE6C8AC7EFCCDC1236DCE76ACB546` | `B5F89E76799364DD67F6B7F4EE5786711A8DE6C8AC7EFCCDC1236DCE76ACB546` |
| `context/handoff.md` | `9F21627A5B0456E9AA2A08837EE2C61F5D309A22C109648ADB0B9B9F9EDAC3A4` | `9F21627A5B0456E9AA2A08837EE2C61F5D309A22C109648ADB0B9B9F9EDAC3A4` |

Commands ran from the course workspace through `rtk`; PowerShell reads and hash checks exited 0. Initial `rtk proxy Get-Content` failed because Get-Content is a PowerShell cmdlet; retried successfully using `rtk proxy powershell -NoProfile -Command`. No project content outside the fixture was read. Remaining validation: controlled answers, proposal review, approval boundary, persistence and later-session recovery. No claim of Copilot discovery, standalone publication or real participant acceptance is made.

## Controlled follow-up: proposal boundary

Exact controlled synthetic reply (test input, not real participant approval):

> Keep offline processing and no uploads. The hosted API request was a mistake. Volunteers sort synthetic demonstration images into animal, plant and other, by entering a manual category; no classifier or runtime is selected. Success is a reviewable local Markdown context with those three categories and no implementation. Please show the proposal; I have not approved writes.

Actual response and concrete proposal presented for review:

> I will retain offline processing and no uploads. Your reply resolves the API conflict and defines manual categorization into `animal`, `plant` and `other`. No classifier or runtime is selected.
>
> Proposed changes, pending your approval:
>
> **`context/project.md`** — preserve the generic working preferences and existing relative links; replace the unconfigured status, field table and synthetic test-fact paragraph with:
>
> Status: **requirements defined; context persistence pending approval**. Owner: the project participant. Requirements below come from the controlled synthetic bootstrap reply dated 2026-10-17, not a real participant decision.
>
> | Field | Proposed value |
> | --- | --- |
> | Goal and intended users | Volunteers manually sort synthetic demonstration images. |
> | Scope and exclusions | Prepare local Markdown context only; no implementation, classifier selection, runtime selection or deployment. |
> | Inputs, outputs and interfaces | Input: synthetic demonstration images. Output: a manually entered category, exactly `animal`, `plant` or `other`. Interface and storage format remain unselected. |
> | Runtime and dependencies | Unselected; no default language or classifier architecture. |
> | Resource constraints | Offline processing; no hosted API dependency. Other limits remain unknown and do not block context preparation. |
> | Data/privacy/evaluation boundaries | Synthetic demonstration images only; do not upload images to any server. No training or evaluation is authorized. |
> | Acceptance criteria | Reviewable local Markdown context records the three categories, manual entry, offline/no-upload constraint and absence of implementation. |
> | Validation commands and directory | Review the approved Markdown diff and relative links in this fixture; no application build/test command is selected. |
> | Repository and branch | Fixture-scoped Git status inspected; no separate repository or branch choice is made. |
> | Deployment target and artifact process | Unselected; publication is outside scope. |
>
> Assumptions: none about runtime, classifier, interface, storage or remote service. Pending choices: interface, image input mechanism, storage format and any implementation environment; these do not block the requested context-only deliverable.
>
> **`context/decisions.md`** — preserve the decision-register instructions and generic preferences, replace the statement that no project-specific decision exists, and append:
>
> - `BOOT-001`, 2026-10-17, proposed; responsible: synthetic test participant. Retain offline processing and prohibit image uploads. The initial hosted API request was explicitly withdrawn as a mistake in the controlled reply. No accepted historical decision is superseded; preserve that source history. Consequence: no hosted classification service may be assumed. Review trigger: an explicit later requirements change.
> - `BOOT-002`, 2026-10-17, proposed; responsible: synthetic test participant. Volunteers enter one of `animal`, `plant` or `other` for synthetic demonstration images. No classifier or runtime is selected. Consequence: context preparation only; implementation requires a separate task. Review trigger: changes to categories or project scope.
>
> Both entries will reference the controlled reply and this evidence record. If you approve this exact proposal, their status will become accepted within the synthetic test, with the exact approval source and date recorded. This will not be represented as real participant approval.
>
> **`context/handoff.md`** — replace the generic session content with:
>
> Status: context proposal reviewed; persistence pending explicit approval. Task: prepare context for volunteer manual sorting of synthetic demonstration images. Confirmed: offline operation, no uploads, categories `animal`, `plant`, `other`, no classifier/runtime selection, no implementation. Sources: controlled synthetic reply of 2026-10-17 and [behavior evidence](../../bootstrap-behavior.md). Files proposed: [project](project.md), [decisions](decisions.md), and this handoff. Next action: obtain approval of this concrete proposal; then apply only these context edits and verify the diff and relative links. Pending choices: interface, input mechanism and storage format; no application implementation is authorized. Branch/commit not selected for this fixture; no external service configured.
>
> If approved, I will update the status sentences to state that the approved context was persisted, replace the next action with “await a separately authorized implementation task,” and record the actual approval and verification results. No draft context files will be saved before approval.
>
> Acceptance checks: the three files consistently contain the agreed categories and offline/no-upload rule; no runtime or classifier is inferred; links resolve; the diff contains only approved context changes. Next action: approve this proposal or identify corrections.
>
> Do you approve these concrete changes to the three context files? The loaded bootstrap-project skill explicitly requires approval of the reviewable proposal before writing context. Your reply expressly withheld write approval, so the files remain unchanged.

Observed behavior: resolved facts were reused without asking again about offline operation or categories. The agent presented bounded, reviewable edits and identified nonblocking unknowns; no implementation was proposed. Approval is still absent. This report records the proposal as evidence outside fixture context, not a draft context artifact.

SHA256 before and after this follow-up remained identical to the first-stage table: project `5750C65261A149E724424BC12B3F351FACA300AECBF1C0B7ECE87E8D33F08AF8`; decisions `B5F89E76799364DD67F6B7F4EE5786711A8DE6C8AC7EFCCDC1236DCE76ACB546`; handoff `9F21627A5B0456E9AA2A08837EE2C61F5D309A22C109648ADB0B9B9F9EDAC3A4`. Verified with RTK-prefixed PowerShell Get-FileHash (exit 0). Persistence and later-session recovery remain untested.

## Controlled approval and persistence

Exact test-controller approval instruction:

> Synthetic test participant now explicitly approves the concrete three-file proposal you just presented, unchanged. Apply it only in the disposable fixture, check relative links and append exact approval, changed files, before/after hashes and actual checks to bootstrap-behavior.md. No real participant approval is implied; no commits/external actions. Then return final result.

Applied only `.bootstrap-fixture/context/project.md`, `decisions.md` and `handoff.md`. Preserved generic preferences and register instructions. Recorded BOOT-001 and BOOT-002 as accepted only within this synthetic test, with source/date/history. Recorded context-only scope, manual categories, offline/no-upload requirements and pending implementation choices. Handoff now awaits a separately authorized implementation task. No implementation, external call or commit occurred.

| File | Before SHA256 | After SHA256 |
| --- | --- | --- |
| project.md | `5750C65261A149E724424BC12B3F351FACA300AECBF1C0B7ECE87E8D33F08AF8` | `7AA342975E563B8F7BE9393605E295505F947E8E5A89CAF6D255B0A1F1AADA0E` |
| decisions.md | `B5F89E76799364DD67F6B7F4EE5786711A8DE6C8AC7EFCCDC1236DCE76ACB546` | `25B5C1F7E6845E04574B52ACAFCE8DE65A74F75DC59752B13B227D4B7505268C` |
| handoff.md | `9F21627A5B0456E9AA2A08837EE2C61F5D309A22C109648ADB0B9B9F9EDAC3A4` | `E9A7F796927A5C06219B968C9B99D388081F1ED397B9AB0EB037740C7ED8EC15` |

Actual checks: reread all three original context files before edits; reviewed applied patch against the proposal. RTK-prefixed `Get-FileHash -Algorithm SHA256` exited 0 with the values above. All six distinct relative Markdown targets in these files were resolved manually and tested with RTK-prefixed PowerShell `Test-Path -LiteralPath`; exit 0, six `True` results. `rtk git diff --check -- participant-work/day2/.bootstrap-fixture/context` and `rtk git diff -- participant-work/day2/.bootstrap-fixture/context` exited 0 with no diff output; this disposable fixture is not represented by tracked Git changes, so these commands do not establish the content diff. Patch review and hashes are the content-change evidence instead.

Execution failures preserved: first apply_patch attempt was rejected atomically because delete/add targeted the same handoff path; subsequent update-only patch succeeded. A Python shell-quoting probe and a PowerShell escaping probe failed without edits; no conclusions rely on them. Runtime/build tests were NOT RUN because this task only prepares Markdown context. Later fresh-session recovery and native Copilot discovery remain untested. Approval provenance is controlled synthetic input, never real participant acceptance.
