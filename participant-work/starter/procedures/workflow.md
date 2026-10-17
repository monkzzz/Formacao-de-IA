# Planning, execution, verification and review

Load for any substantive change. Start with [the working agreement](../AGENTS.md)
and current [project context](../context/project.md).

## Plan

Read Git status, affected files and relevant nested instructions. Identify the
requested result, acceptance criteria, scope, dependencies and validation method.
Use a short plan for multiple dependent steps; do not require formal planning for
a trivial edit. Check existing [knowledge](../knowledge/README.md) before repeating
an expensive investigation. Treat unknown requirements as unknown.

Proceed with reversible work and reasonable routine assumptions. Record assumptions
that affect acceptance. Ask only when a material decision cannot be inferred or a
dependent action needs authorization; continue independent authorized work meanwhile.
Do not infer a reply or permission from elapsed time.

## Execute

Make focused changes using project conventions. Preserve unrelated work and original
evidence. Explain new findings or scope changes in brief progress updates. Diagnose
failures at the affected boundary before changing unrelated code or dependencies.
Load specialized procedures or skills only when the task needs them.

## Verify

Choose checks based on changed behavior: targeted tests for logic, integration checks
for boundaries, a build when compilation changes, local links for Markdown, and
interface interaction plus visual inspection for GUI changes. Broaden testing when
failures or unresolved risks justify it. Do not add tests that merely repeat a
low-impact implementation. Use deterministic fixtures and mocks where appropriate.

Capture the command, working directory, environment identifiers, exit code, observed
result, inputs/version and limitations in an [evidence record](../evidence/README.md).
Mark unrun checks `NOT RUN` and explain the cause. Keep original failures alongside
successful follow-up evidence; never silently overwrite historical results.

## Review and hand off

Review the diff for correctness, scope, provenance, secrets and unrelated files.
Compare results with acceptance criteria. If blocked, record the exact dependency
and complete unaffected work; do not mark the blocked activity done. Add approved
choices to [decisions](../context/decisions.md), reusable findings to knowledge and
the next action to [handoff](../context/handoff.md).

Use [Git and safety](git-and-safety.md) to commit within authorization. Report what
changed, why, checks actually run and remaining limits. Do not treat passing tests
as proof of broader behavior they did not exercise.
