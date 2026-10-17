# Starter and bootstrap batch

Completed 2026-10-17, following the next five unchecked activities in
[TASKS.md](../../TASKS.md). Scope: three remaining starter activities, interview
research and the first bootstrap skill source. No classifier context was populated.

1. [Reference selection](starter-reference-selection.md) records adaptations and
   discarded components, with course authorship and license.
2. [Fresh-session experiment](starter-fresh-session.md) records a no-history agent
   session, unrelated hypothetical reuse and a safe documentation task in an
   ignored disposable copy. It is the chosen-assistant adaptation, not Copilot
   auto-discovery or an independent participant interview.
3. [Generic 1.0.0 archive](starter-generic-1.0.0.zip) and
   [SHA-256 manifest](starter-generic-1.0.0.json) preserve the actual generic source
   from `cc349efac3aebfc26dafbb73724ca0ac85694d9c`, before skill creation or
   classifier-specific context. The manifest identifies every archived file.
   [Capture script](prepare-generic-snapshot.py) refuses to overwrite the snapshot.
   This is preservation now, not proof of an earlier original course sequence.
4. [Research](bootstrap-research.md) records primary documentation, an accessible
   interview skill comparison, unavailable Ask Me sources and concrete choices.
5. [Participant skill](../starter/.github/skills/bootstrap-project/SKILL.md) uses
   native Markdown name/description metadata at the exercise's requested location.
   No downloaded skill or installer substitutes for the implementation. Copy the
   starter contents to a target project root to obtain `.github/skills/...` there.

The skill-creator format validator passed with `Skill is valid!` using the GSS
Python environment. This proves format only. The skill's source includes adaptive
questions, approval and recovery instructions so it is usable, but their later
checklist activities remain unchecked until separately demonstrated. Copilot
execution, classroom acceptance and standalone publication are not claimed.

The batch [validator](validate-starter-batch.py) checks local links/anchors,
copyable-starter containment, archived hashes and source-commit identity, exact
next-five checklist updates and preservation of course/classifier sources.
[Validation results](starter-batch-validation.json) record its actual execution.
The first batch-check attempt failed because it interpreted Markdown inside a
fenced experiment script as report-relative links. The checker was corrected to
inspect prose links outside fenced code; the fixture's own 11 links were already
checked in the recorded fresh-session experiment. No missing submission link was
hidden or rewritten to suppress that failure.
No model tests or official challenge evaluations are needed for these changes.

The archived README/handoff preserve their pre-experiment status wording. Current
starter documentation describes the later skill presence and the scope of reuse
evidence. Historical [preparation](starter-preparation.md) remains unchanged.
