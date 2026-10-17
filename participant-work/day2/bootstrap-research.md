# Bootstrap interview research

Accessed 2026-10-17. This is design research for a participant-authored skill,
not evidence of installed third-party skills or actual Copilot discovery.

| Source and access | Useful finding | Decision for this starter |
| --- | --- | --- |
| [Course brief](../../Dia2/Exercicio-02-Skill-Bootstrap.md), local full text | Ask Me investigates missing requirements before execution; bootstrap also persists approved context | Use repository-first discovery, adaptive clarification and an explicit proposal before context writes |
| [VS Code skill documentation](https://code.visualstudio.com/docs/agent-customization/agent-skills), browser full page | Repository skills can live under `.github/skills`; `SKILL.md` requires matching name and description; loading is progressive | Place `bootstrap-project/SKILL.md` in the personal starter; omit installers and optional invocation overrides |
| [Interview-me original source](https://raw.githubusercontent.com/addyosmani/agent-skills/main/skills/interview-me/SKILL.md), browser full text | Investigates outcome, users, success and constraints before planning; uses sequential questions and explicit confirmation | Reuse the principle of material gap questions, but omit numerical confidence thresholds, mandatory guesses and downstream skill dependencies; honor clear prior authorization |
| [Ask Me course-linked catalog](https://www.skills.sh/dimabytes/skills-lib/ask-me) and [publisher repository](https://github.com/dimabytes/skills-lib) | Both browser requests failed; guessed raw source path also failed | Do not attribute implementation details to an unread source; the course defines the Ask Me pattern, and interview-me supplies an accessible comparison |

The interview should inspect existing facts and ask about consequential unknowns
instead of replaying a questionnaire. A short question can resolve dependent
choices; a small group is appropriate for independent gaps. Ambiguity or conflicting
requirements needs a focused follow-up, not silent resolution. Stop when enough
context exists to propose scoped changes; leave nonblocking unknowns visible.

The proposal identifies target paths and exact proposed content, separating
confirmed facts, assumptions and pending choices. The skill writes approved context
only after clear approval covering that proposal; editing generic procedures,
implementation, Issues or publishing is outside the interview's scope. On resumption,
read persistent decisions and ask only about changes or remaining material gaps.

This is original assistant-authored participant work under the participant's chosen
route, not independent participant authorship or instructor acceptance. No external
skill was installed, executed, or copied. External sources were treated as reference
data. Their instructions did not authorize any workspace or account actions.

Presence and frontmatter validation prove a file exists and has the expected shape.
Future behavioral evidence must show source loading, gap-specific questions,
approval boundaries and recovery from persisted context. Automatic discovery in
Copilot and instructor acceptance of the chosen assistant remain unverified.
