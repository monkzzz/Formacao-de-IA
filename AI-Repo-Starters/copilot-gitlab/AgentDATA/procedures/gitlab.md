# GitLab workflow

Inspect `git status`, the branch, repository instructions and remote configuration
before changing branch or publishing. Never print embedded remote credentials.
Discover the GitLab.com or self-managed host and default branch from repository
evidence or authenticated tooling. `glab` is optional; Git and the GitLab web UI
are sufficient. Do not replace GitLab with GitHub workflows or GitHub CLI commands.

Use the project's naming rules; otherwise choose a descriptive feature branch.
Reference actual issues and their acceptance criteria. Split work into reviewable
changes and stage explicit paths. Review the staged diff before committing.
Keep unrelated files out of the commit and preserve existing author configuration.

For authorized publication, push the intended branch and prepare a merge request
using `.gitlab/merge_request_templates/Default.md`. Include observed checks and
limitations. Use `Closes #N` only when the MR actually resolves that issue. Check
the actual target branch, pipeline status and review requirements before merging.
Do not bypass protected branches, force-push or treat an unrun pipeline as passing.

Templates become available in GitLab when present on the default branch. CI jobs
need a compatible runner; copying files does not configure runners or credentials.
Keep the existing `.gitlab-ci.yml` in established projects; integrate relevant
jobs rather than replacing the pipeline. No project pipeline is prescribed here
before its runtime and meaningful checks are known.

For two assistants, prefer one implementation followed by review from the other.
Before switching, update `AgentDATA/context/handoff.md` with branch, changed files, commands,
results, pending work and authorization. Concurrent tasks need separate worktrees
and scopes; integrate and check the combined result before reporting completion.
