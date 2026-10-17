# Starter preparation: first four activities

Prepared on 2026-10-17 in the existing personal fork. The next ten-task batch in
[the checklist](../../TASKS.md) includes six GSS completion activities and the
first four starter activities. The [working decisions](../../PREPARATION.md#working-decisions)
establish English, the current assistant and this personal fork as the workspace.

## Deliverable and scope

The [reusable starter source](../starter/README.md) contains concise
[agent rules](../starter/AGENTS.md), a [Copilot entry point](../starter/.github/copilot-instructions.md),
reusable procedures, context records and capability registries. It is a copyable
directory under the participant's personal repository, rather than a separately
created and published GitHub repository. That course-rubric difference is explicit;
instructor acceptance and standalone publication are not claimed.

The participant declined Copilot. The compatibility entry is present, but actual
Copilot discovery/use was not tested. No bootstrap interview skill, classifier
requirements, datasets, architecture, training or site were added to this starter.
Existing `dia2-local/` remains untouched.

## Responsibilities and acceptance

| Activity | Concrete result | Review criterion |
| --- | --- | --- |
| Reusable starter and entry point | Agent agreement, README, `.github/copilot-instructions.md`, `.gitignore` | A reader can find the rules, understand copying/reuse and distinguish the chosen route from Copilot testing |
| Working procedures | [Workflow](../starter/procedures/workflow.md) and [Git/safety](../starter/procedures/git-and-safety.md) | Planning, execution, verification, review, preservation and authorization have observable actions and evidence requirements |
| Persistent records | [Project](../starter/context/project.md), [decisions](../starter/context/decisions.md), [handoff](../starter/context/handoff.md), [knowledge](../starter/knowledge/README.md), [evidence](../starter/evidence/README.md) | Facts, choices, reusable explanations and execution observations have distinct owners, fields and update rules |
| Capabilities | [Discovery contract](../starter/capabilities/README.md), [CLI](../starter/capabilities/cli.md), [skills](../starter/capabilities/skills.md), [MCP](../starter/capabilities/mcp.md) | Need and availability are separate; records define contracts, dependencies, risks, safe probes and evidence |

The procedures follow the participant's preference for autonomous reversible work,
brief progress updates, focused diffs and actual checks. They carry existing
authorization forward and reserve clarification for material unknowns or external
actions lacking authority. They do not impose a new approval step on routine edits.

Generic context deliberately leaves runtime, product goals, remote and deployment
unselected. Findings must be dated/scoped and rechecked after relevant changes.
Decision history is superseded rather than erased. Execution evidence must label
live, recorded, mocked, failed and unrun checks. These are written contracts, not
proof that an unseen fresh session already followed them.

## Environment evidence

The [read-only probe](probe-starter-environment.py) produced
[starter-environment.json](starter-environment.json). Six checks succeeded: RTK
version, Git version, ripgrep version, PowerShell version, the GSS Python version
and repository status. These verify executable/version or read-only repository
operations only. They do not establish remote authentication, write access or
availability on another machine.

`gh`, `node` and `npm` were checked on the current process's PATH; use the JSON
for actual presence results. Absence on PATH is not proof that software is absent
from the whole machine. No runtime for a future project is selected from these probes.

Skills were advertised in the current session catalog; no skill was invoked or
implemented for this batch. MCP tool metadata was inspected through the session's
tool catalog, but no external service was called or authenticated. No credentials
were read or written. The starter therefore carries candidate entries with
`not checked` states, while this environment's probe evidence remains outside it.

## Reference and validation boundaries

Read the course starter exercise, reference introduction, reference `AGENTS.md`,
standard workflow and Git procedure. The starter README attributes the course
authors and CC BY 4.0 and describes the English conceptual adaptation. No reference
file was copied verbatim. The full copied/adapted/discarded decision record remains
the next starter checklist activity, followed by fresh-session/reuse/safe-task
experiments and preservation of an identifiable generic release.

Review for this batch checks links, record responsibilities, no application-specific
context, capability status honesty and preservation of unrelated Git files. No
fresh session or independent agent was used. Documentation checks must not be
reported as those later behavioral experiments. The batch validator passed 202 local
links and 32 heading anchors, including the check that all starter-internal links
stay inside the copyable directory. Six environment probes passed. The checklist
comparison confirms only the next ten activities were checked; no classifier or
course source changed.
