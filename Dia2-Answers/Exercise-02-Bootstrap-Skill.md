# Exercise 2 — Bootstrap Interview Skill

Original: [Exercise 2](../Dia2/Exercicio-02-Skill-Bootstrap.md).

## What does Ask Me mean?

The agent discovers missing information before implementing a solution. It reads existing context, asks relevant questions, clarifies contradictions, and distinguishes confirmed facts from assumptions. A bootstrap skill additionally turns approved answers into persistent project documents.

## What should trigger the skill?

A request to initialize a project, establish requirements, or update incomplete project context should trigger it. A clearly specified implementation task should not automatically restart an interview.

## How should the interview behave?

1. Inspect the starter's rules and current context.
2. Identify only unresolved questions that affect the next decisions.
3. Ask a small group of questions about purpose, users, scope, constraints, data, evaluation, or deployment.
4. Adapt subsequent questions to the answers. Do not repeat information already confirmed.
5. Resolve conflicting answers explicitly; never invent the participant's preferences.
6. Stop when there is sufficient context for planning, keeping unresolved items visible.

For the digit project, useful questions include whether training hardware is limited, what counts as an acceptable result, and which browser interactions must be supported. Requirements already mandated by the course should be recorded rather than presented as optional.

## What happens before files are written?

Present a proposed context with confirmed requirements, assumptions, open questions, and affected files. Ask the participant to validate it. Interview answers alone do not authorize arbitrary implementation. After approval, update project context and decisions without replacing the starter's generic rules or existing unrelated work.

## Where does the skill live?

The course guide specifies `.github/skills/<skill-name>/SKILL.md`, containing YAML `name` and `description` metadata followed by behavior instructions. Markdown skills do not themselves require Node.js or an installer. Check recognition in the participant's actual Copilot environment.

This answer describes the design; it does not supply or claim a tested executable skill. Research the course's linked interview examples critically and write an original implementation rather than installing an external answer.

## How should it be tested?

| Scenario | Expected behavior |
| --- | --- |
| Empty project context | Ask about missing requirements |
| Partially documented project | Ask only about gaps |
| Conflicting answers | Explain the conflict and seek clarification |
| Proposal not yet approved | Do not change context files |
| Approved proposal | Update only the agreed files |
| Fresh session | Recover decisions and pending questions from files |
| Changed requirement | Propose an update without repeating the whole interview |

**Practical work remaining:** research references, create the original skill, verify discovery and these behaviors, obtain context approval, persist the classifier requirements, and record a fresh-session check. Do not implement the classifier or create its Issues yet.
