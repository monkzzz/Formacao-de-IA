# Personal reusable starter

This is the participant's reusable starter, maintained in the personal course
fork. Generic rules and procedures are preserved; its current context records the
existing Day 2 website preservation scope. It contains no duplicate application
implementation. A participant-authored [bootstrap interview skill](.github/skills/bootstrap-project/SKILL.md)
is included; its native Copilot discovery and standalone publication remain unverified.

The participant chose English and the current assistant. A Copilot-compatible
[entry file](.github/copilot-instructions.md) is included for reuse, but Copilot
discovery and execution have not been tested or required for the chosen route.

## Start here

1. Read [AGENTS.md](AGENTS.md), [project context](context/project.md) and
   [handoff](context/handoff.md). Remaining unknowns are explicitly unresolved.
2. Read [workflow](procedures/workflow.md) and [Git and safety](procedures/git-and-safety.md).
3. Discover necessary [capabilities](capabilities/README.md) in the target environment.
4. Work within the request; save observations in [evidence](evidence/README.md),
   approved choices in [decisions](context/decisions.md), and reusable explanations
   in [knowledge](knowledge/README.md).

## Reuse in a different project

For unrelated reuse, start from the preserved generic 1.0.0 archive in the course
submission, or reset the three populated context records before copying this
directory. Do not inherit classifier requirements or the website decision. Copy
the chosen generic contents, including `.github/` and `.gitignore`, into an empty
personal project directory. Do not copy this course's parent Git metadata,
datasets, environments, reports or classifier. Initialize Git in the destination
only when creating that separate repository is authorized. Review the diff and
retain the attribution below when adapting the starter.

Keep the generic procedures and working preferences. Fill `context/project.md`
with the new project's confirmed goals, constraints, interfaces and checks; use
`context/decisions.md` for approved choices. Replace the starter handoff with the
actual next task. Discover runtime and integrations again, and keep the target
environment's evidence separate. No capability is installed by copying Markdown.

There is no default build or test command until a project selects a runtime.
For starter documentation, verify local links, responsibility boundaries and Git
changes. Behavioral testing with a fresh session is a separate acceptance step;
file/link validation alone does not establish instruction discovery or compliance.

## Attribution and adaptation

Adapted conceptually from the course reference at
`Dia2/Referencia-Starter-Repo/Starter-Repo/`: always-active rules, procedures loaded
on demand, persistent context/knowledge/evidence, and capability registries.
Course materials credit **Vinicius Canonici and Hugo Gomes**, under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
This English participant adaptation consolidates the structure, removes language
and publication assumptions, and follows the participant's chosen assistant and
authorization preferences. It does not imply endorsement by the course authors.

No reference files were copied verbatim. The containing course submission records
the reference-selection review, a fresh agent session using a disposable unrelated
project, and a hash-identified generic 1.0.0 archive captured before the skill was
added. Those records stay outside this copyable directory. They establish scoped
observations, not automatic Copilot discovery or classroom acceptance.

To use the interview, open this directory as the target project and request
`bootstrap-project` in a host that supports `.github/skills`, or explicitly provide
the skill file to the chosen assistant. The skill reads current context, asks about
material gaps and presents a proposal before writing approved project context.
No installer is required. Presence alone does not prove host discovery or behavior.
