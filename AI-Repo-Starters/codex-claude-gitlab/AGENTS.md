# Shared agent working agreement

Read `AgentDATA/context/project.md` and `AgentDATA/context/handoff.md` before substantive work. Read relevant
decisions, procedures and nested instructions when needed. Explicit user requests
take precedence over this template; respect the host's permissions and policies.

- Inspect the repository and Git status first. Preserve unrelated changes.
- Complete the requested work autonomously. Resolve routine reversible choices;
  ask only about material missing requirements or actions lacking authorization.
  Carry existing authorization forward; avoid repeated confirmation requests.
- Explain the intended outcome briefly, then implement and verify it. Use a short
  plan for work with dependent steps; avoid ceremony for small edits.
- Match existing conventions. Do not impose a language, stack, package manager,
  model, deployment service or dependency merely because this starter exists.
- Detect the current OS and shell. Read `AgentDATA/procedures/portability.md` when adding
  commands or scripts. Use repository-relative paths and document both platforms.
- Use `AgentDATA/procedures/gitlab.md` for branches, issues and merge requests. Discover
  the actual GitLab host and default branch; do not assume github.com or main.
- Run checks relevant to changed behavior. Report actual results and limits;
  distinguish PASS, FAIL, BLOCKED and NOT RUN. Never invent an executed check.
- Keep confirmed facts, assumptions and open questions distinct. Update project
  context when it changes and the handoff when a task ends or switches assistants.
- Keep credentials out of source and logs. Do not override global configuration,
  discard work, rewrite history or publish outside the user's authorized scope.
- Commit, push, create remote issues/MRs, merge or deploy when the request or an
  established project agreement authorizes that action. A local edit alone does
  not grant all of these permissions. Prepare the result before seeking approval.
- Prefer sequential assistant handoffs. For concurrent work, use separate Git
  worktrees/branches with distinct scope; never have two agents edit one worktree.
  Do not spawn other agents unless the user authorizes delegation.

For initial setup or a substantial context update, use the `bootstrap-project`
skill. Skill discovery differs by assistant; its path is documented in START-HERE.md.
No tools, accounts, credentials or integrations are installed by these files.

Read [the AgentDATA directory guide](AgentDATA/README.md) for record ownership.
Use [the procedure index](AgentDATA/procedures/README.md) to load specialized
workflows on demand. Record important validation evidence in AgentDATA/logs/ or
AgentDATA/docs/ and reusable technical findings in AgentDATA/Knowledge/.
