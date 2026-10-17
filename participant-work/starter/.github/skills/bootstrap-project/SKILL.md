---
name: bootstrap-project
description: Interview the participant to establish or update project requirements in this starter, then persist a reviewed context proposal after approval. Use for project bootstrap or material context updates, not ordinary implementation tasks.
---

# Bootstrap project context

Resolve the project root containing `AGENTS.md`, `context/` and `procedures/`;
do not confuse a containing course repository with this copyable starter. Read
the applicable rules, README, `context/project.md`, `context/decisions.md` and
`context/handoff.md`. Inspect Git status and relevant evidence before proposing
changes. State that this skill was loaded and identify the context sources used.

## Interview

Compare the active request with existing requirements. Distinguish confirmed
facts (with their source), assumptions and pending decisions. Reuse established
working preferences and authorization; do not ask for answers already present.

Ask focused questions about material gaps. Depending on the project, these may
include users and goals, scope, input/output contracts, resource or privacy
constraints, data and evaluation boundaries, tools, success criteria and delivery.
Ask the most consequential question first; group only independent questions.
Let answers determine follow-ups instead of requiring a fixed questionnaire.

When requirements conflict, show the conflicting sources and ask which governs.
Do not silently replace an accepted decision or promote a guess into a fact.
If the user cannot answer, keep the decision pending and explain whether it blocks
the proposal. In a noninteractive session, report blocking gaps without inventing
an interview or approval. Enough context to propose a limited scope is sufficient;
do not prolong the interview over irrelevant or nonblocking unknowns.

## Reviewable proposal

Before writing or altering project context, present proposed paths and their
reviewable content or diff in the conversation. Include confirmed requirements,
labelled assumptions, pending choices, acceptance checks and the next action.
Normally update `context/project.md`, append decisions to `context/decisions.md`
and update `context/handoff.md`. Use the starter's existing responsibilities.

Require clear participant approval covering this concrete proposal before writing
it. General permission to conduct an interview is not approval of unseen context.
If approval already covers the same proposal, use it without asking again. Silence
and elapsed time do not authorize writes. Incorporate requested corrections into
the proposal; seek approval again only for material changes outside its scope.
Do not save draft context files as a shortcut around this boundary.

## Persist and resume

Apply only approved context changes. Preserve generic agent rules, procedures,
prior decisions and unrelated work. Record approval source, date and affected
decision IDs; supersede old decisions explicitly. Check the diff and relative links,
then report actual checks and outstanding limits. Do not put secrets in context.

On a later session, recover requirements, decisions and next actions from these
files. Summarize what is known and ask only about new contradictions or material
unknowns. Updates use the same proposal/approval boundary without restarting the
interview. A context approval does not authorize implementation, training, Issues,
commits or publication; those require their own task scope. Never preselect a
classifier architecture or infer that a deployed experiment is an approved spec.
