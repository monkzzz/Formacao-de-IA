---
name: bootstrap-project
description: Establish or update a repository's project context through a focused interview and persist requirements, decisions and a handoff. Use for project bootstrap or substantial context changes.
---

# Bootstrap or update project context

Find the root containing AGENTS.md and AgentDATA/. Read those instructions, current
project context, decisions and handoff. Inspect the existing repository and Git
status before asking questions. Reuse answers and authorization already supplied.
Do not assume a new project merely because the templates are unfilled.

Ask short, adaptive questions only for material gaps: intended users and outcome,
scope, constraints, existing stack, inputs/outputs, acceptance checks, Linux and
Windows support, and GitLab delivery. Discover existing tools before suggesting
new ones. Distinguish verified facts, user decisions, assumptions and unresolved
questions. Do not force the user through a fixed questionnaire.

Present a concise project-context proposal with affected paths and acceptance
criteria. Resolve consequential uncertainties with the user; do not request
approval again when the active request already authorizes these concrete updates.
Never treat elapsed time or silence as an answer. Nonblocking unknowns can remain
explicitly unresolved while independent authorized work proceeds.

Populate AgentDATA/context/project.md, append consequential decisions to AgentDATA/context/decisions.md and
update AgentDATA/context/handoff.md within the authorized scope. Preserve generic rules and
existing requirements; explicitly supersede changed decisions. Record the source
of confirmed requirements. Populate OS-specific commands only from discovery or
agreed stack choices, and mark commands NOT RUN until actually executed.

Check relative links and the diff. Report established context, remaining gaps and
next action. Do not implement an application, initialize Git, create remote
issues, publish, or change global assistant settings solely because bootstrap was
requested. Continue those actions when the user separately included them in scope.

On later invocations, recover the stored context and ask only about material
changes or contradictions. Do not restart the interview or erase prior evidence.
