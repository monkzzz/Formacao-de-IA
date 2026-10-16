# Exercise 1 — Reusable Starter Repository

Original: [Exercise 1](../Dia2/Exercicio-01-Starter-Repo.md).

## 1. What should survive between projects?

The starter should preserve a working method: understand the task, inspect existing work, plan changes, implement, verify, review, and record the outcome. It should also preserve rules for protecting secrets and unrelated changes. Frameworks, deployment destinations, datasets, and application requirements belong to individual projects.

Suggested autonomy policy: let the agent perform routine, reversible work, while asking about unresolved product decisions and publication. This remains a proposal for the participant to choose.

## 2. How should context be organized?

Use a short root `AGENTS.md` for permanent rules and a map to supporting documents:

| Location | Responsibility |
| --- | --- |
| `README.md` | Explain how to reuse the starter |
| `docs/context.md` | Confirmed requirements, assumptions, and open questions |
| `docs/decisions.md` | Decisions, rationale, alternatives, and review conditions |
| `docs/knowledge.md` | Reusable findings supported by evidence |
| `docs/procedures/` | Task-specific workflows loaded when relevant |
| `docs/capabilities.md` | Tools, dependencies, availability, and verification |
| `docs/evidence.md` | Checks performed, results, and remaining gaps |

Add a concise Copilot entry document pointing to the shared rules, and verify discovery in the actual environment. Avoid maintaining contradictory copies of the rules.

## 3. How should the agent work?

Before editing, inspect instructions, relevant files, and Git status. State the problem, affected files, and intended checks. Keep changes within scope. Run checks appropriate to the behavior changed; investigate failures instead of weakening assertions. Report exactly what ran, what passed, and what remains unverified.

## 4. How should Git and knowledge be handled?

Review the diff and stage named files. Preserve existing work. Use focused commits such as `docs(starter): document validation workflow`. Ask before destructive operations or rewriting shared history. Agree separately on commit and publication autonomy.

Record an event in evidence, a durable choice in decisions, and a reproducible discovery in knowledge. Label hypotheses explicitly. Date records and revisit them when their underlying assumptions change.

## 5. How should capabilities be tracked?

For each useful CLI, skill, or MCP integration, record its purpose, inputs, outputs, dependencies, side effects, and an availability check. “Documented” does not mean “installed.” If unavailable, explain the limitation and propose an alternative. Keep credentials outside Git; document variable names without values.

## 6. How should a new project begin?

Keep generic rules intact. Start project context as undefined, then discover requirements with the participant. Do not carry over another project's stack or credentials. Exercise 2 will supply the interview mechanism.

## 7. What should be reused from the reference?

Adapt the reference's separation between permanent instructions and optional procedures, its validation discipline, and its protection of unrelated changes. Consolidate its separate capability catalogs initially. Omit npm/PyPI publication procedures, unused integrations, and personal policies that do not fit the participant. Preserve attribution when adapting text.

## 8. How can reuse be demonstrated?

Run three real checks: open a fresh agent session and recover the rules; apply the structure to an unrelated hypothetical project; request a safe documentation task and observe its investigation and verification. Record actual behavior and refine failures.

**Practical work remaining:** choose personal preferences, create and publish the separate starter repository, review its files, and collect these checks. Do not add a classifier or bootstrap skill during this exercise.
