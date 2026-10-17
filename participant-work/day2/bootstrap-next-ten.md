# Bootstrap and planning batch

Prepared 2026-10-17 from baseline `4342c320a0f570de729f8fc517850c9cebb6767d`.
Scope is the next ten unchecked checklist activities: five bootstrap activities
and five planning/Issue activities. Preserve existing `dia2-local/` and its website,
as explicitly directed by the participant after the context proposal.

## Skill behavior and context

The existing [participant skill](../starter/.github/skills/bootstrap-project/SKILL.md)
already specifies repository inspection, adaptive questions, conflict resolution,
fact/assumption/pending distinctions and proposal approval. This batch tests those
instructions rather than copying an external skill or adding redundant rules.
The `skill-creator` guidance was consulted for scoped behavioral validation.

[Behavior evidence](bootstrap-behavior.md) comes from a separate no-history agent
using an isolated copy. The initial synthetic request contradicted the fixture's
offline constraint and left categories unknown. The agent asked material questions
and left context hashes unchanged. A controlled reply resolved both gaps; the agent
reused the answers, presented three concrete file changes and again left hashes
unchanged. Only a subsequent explicit synthetic approval led to fixture writes.
This is controlled test input, not a real participant interview or approval.
Failures and corrections remain in the report.
The [final fixture context](bootstrap-fixture-context.json) preserves actual
synthetic outputs and hashes so evidence survives without the ignored work copy.

[Recovery evidence](bootstrap-recovery.md) uses another no-history session. It
recovers persisted fixture requirements and proposes a bounded update without
restarting resolved questions or writing unapproved context. It separately
identifies the next real Issue using the actual repository's persistent records.
Neither agent demonstrates native Copilot discovery. The participant declined
Copilot, so explicit chosen-assistant skill loading is the declared route;
instructor acceptance of that substitution remains pending.

For the actual classifier, the assistant presented a context proposal and asked
for approval. The participant clarified: “the current development of dia 2 local
that is o websitw maintain it”. This directly confirms preservation, not a new
architecture, retraining or migration. [Populated context](../starter/context/project.md)
records observed implementation facts, limited authority, assumptions and pending
checks separately. [Decisions](../starter/context/decisions.md) retain that provenance;
[handoff](../starter/context/handoff.md) supports later updates. Do not claim explicit
participant approval of every technical statement or historical experiment.

Generic `AGENTS.md`, procedures, capability contracts, knowledge and evidence
responsibilities remain unchanged. The [generic archive](starter-generic-1.0.0.json)
predates population and remains available for unrelated projects. Populated context
now intentionally links to course-submission records outside the copyable directory.
Do not copy these requirements as generic defaults into another project.

## Specification and real Issues

[Specification](classifier-specification.md) reconciles existing inputs/outputs,
architecture alternatives, resources, preprocessing, splits, metrics, export,
browser parity, UI and hosting under the participant's preservation scope. It is
retrospective. Current live behavior, artifact restoration and fresh tests remain
future work; no model or official challenge was rerun in this batch.

Public GitHub REST read returned no existing Issues. The first creation attempt
returned HTTP 410; repository inspection confirmed Issues were disabled on the
fork. The assistant enabled Issues only, then created [six real Issues](issue-register.md),
with dependency links, acceptance criteria and verification requirements. No
website configuration or deployment was changed. Authentication used Git's
credential helper in memory; no credential values were printed or stored.
[Read/publication records](github-issues-after.json) distinguish actual URLs and
creation dates from the local [body plan](issue-plan.json).

No original pre-implementation approval was found in the inspected local documents
or initial public Issues. This is a scoped finding, not proof that private or
deleted approvals never existed. Today's instruction and Issues cannot establish
original chronology. The [instructor request](instructor-process-request.md) is
ready, but **not sent**: no recipient/channel or real response has been provided.
That checklist activity remains incomplete rather than being relabelled done.

## Version and verification

Skill source version remains 1.0.0; no instruction-body change was needed. Populated
context version is 1.0.0. The [version manifest](bootstrap-context-version.json)
identifies source baseline and file hashes; Git commit history versions the actual
files without inventing a standalone release or published tag.
[Batch validation](bootstrap-planning-validation.json) records format, evidence
links/anchors, context/generic preservation, weight hash read-only verification and
the exact checklist scope. Historical reports and unrelated untracked files remain
untouched. No application code, weights, official images or production site changed.

One validation attempt caught CRLF normalization while serializing the disposable
fixture: reading as text changed its bytes before hash comparison. The evidence
capture was corrected to decode original bytes with line endings intact, preserving
the actual files and the hashes recorded by the sessions.
