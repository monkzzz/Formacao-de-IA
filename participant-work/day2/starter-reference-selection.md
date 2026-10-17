# Starter reference selection

Reviewed 2026-10-17 against reference source at course commit
`cc349efac3aebfc26dafbb73724ca0ac85694d9c`. This records the selection rationale
for the existing English adaptation; it does not claim a previously recorded review.

Base: [reference introduction](../../Dia2/Referencia-Starter-Repo/LEIA-PRIMEIRO.md)
and [reference source](../../Dia2/Referencia-Starter-Repo/Starter-Repo/README.md).
No file was copied verbatim into the personal starter. The following decisions
cover the reference components, including categories intentionally omitted.

| Reference component | Decision and destination | Reason |
| --- | --- | --- |
| `AGENTS.md` and standard workflow | Adapt concepts into [agreement](../starter/AGENTS.md) and [workflow](../starter/procedures/workflow.md) | Short permanent rules; load detail when needed; preserve scope and evidence |
| Git operation, validation, documentation and code quality | Consolidate into workflow and [Git/safety](../starter/procedures/git-and-safety.md) | Review, checks and preservation apply across projects without language-specific commands |
| `AgentDATA/context`, memories and docs | Consolidate into [context](../starter/context/project.md), decisions and handoff | Separate durable requirements, approved choices and next actions; avoid overlapping memory stores |
| `AgentDATA/Knowledge`, logs and logging procedure | Adapt into [knowledge](../starter/knowledge/README.md) and [evidence](../starter/evidence/README.md) | Keep interpretation separate from executed observations; use real dates, not template timestamps |
| Skills, tools, MCP indexes/templates and procedures | Adapt into [capabilities](../starter/capabilities/README.md) | Preserve inputs, outputs, effects, prerequisites and availability checks; no assumed installation or service access |
| AgentDATA bootstrap procedure | Discard mandatory twelve-folder scaffold and TypeScript-only scripts | Copyable starter needs fewer responsibilities and no selected runtime |
| npm/PyPI publication procedures | Discard package commands and author-specific `mahout-bench` / `elephant-prompt-bench` promotion rules | No package or publication request exists in a generic project |
| CLI build/documentation and `script_template.ts` | Retain contract ideas in capability entries; omit implementation template | Runtime and executable tools must be selected by the new project |
| Legacy/delete procedure | Consolidate preservation checks into Git/safety | No standalone destructive-maintenance workflow is needed |
| References, secrets directory and credential examples | Keep attribution and credential boundaries; omit credential JSON and extra folders | No configured integration needs a credential schema; never imply valid access |
| Default camelCase, line-count targets, framework/type preferences | Discard defaults; use target project conventions | Generic procedures should not impose another author's implementation choices |
| Historical context/knowledge timestamps | Discard fixed example dates | Future records need actual event dates |

The [personal starter](../starter/README.md) adds a Copilot compatibility entry,
explicit English preferences, unresolved project fields and honest verification
states. These are participant adaptations, not proof of Copilot execution.

Attribution: course reference by **Vinicius Canonici and Hugo Gomes**, under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), as specified in the
[repository license](../../LICENSE.md). Changes: English rewrite, consolidated
directory layout, selective omissions and participant-specific autonomy rules.
No author endorsement is implied. No external interview implementation was copied.
