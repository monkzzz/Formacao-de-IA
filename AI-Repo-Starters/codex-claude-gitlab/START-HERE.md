# Codex + Claude Code + GitLab

Copy this folder's **contents**, including hidden folders, into your repository
root. Keep this guide as START-HERE.md so it does not replace your project README.
The starter has no application stack, account configuration or installed tools.

## Copy into a new empty directory

Replace the example source and destination paths. These commands target a new
empty directory only; they deliberately refuse an existing destination.

Linux / Bash:

```bash
starter_source="/path/to/AI-Repo-Starters/codex-claude-gitlab"
project_destination="/path/to/new-project"
(mkdir -- "$project_destination" && cp -R -- "$starter_source"/. "$project_destination"/)
```

Windows / PowerShell:

```powershell
$starterSource = 'C:\path\to\AI-Repo-Starters\codex-claude-gitlab'
$projectDestination = 'C:\path\to\new-project'
if (Test-Path -LiteralPath $projectDestination) { throw 'Choose a new destination directory.' }
New-Item -ItemType Directory -Path $projectDestination -ErrorAction Stop | Out-Null
Get-ChildItem -LiteralPath $starterSource -Force | Copy-Item -Destination $projectDestination -Recurse -Force -ErrorAction Stop
```

For an **existing repository**, copy missing files and merge overlapping files,
especially AGENTS.md, .gitignore, .gitattributes and assistant configuration.
Preserve its README, license, instructions, CI pipeline and uncommitted changes.
Do not replace populated AgentDATA/ records with blank templates or copy Git metadata.
Use one variant per repository. The combined Codex/Claude variant shares one policy.

## First session

Open the repository root in Codex or Claude Code. Install/authenticate the selected assistant separately if needed.
In Codex, request `$bootstrap-project`. In Claude Code, use `/bootstrap-project`. If skill discovery is unavailable, explicitly ask the assistant to
read [.agents/skills/bootstrap-project/SKILL.md](.agents/skills/bootstrap-project/SKILL.md) and follow it.

Suggested first message:

> Read AGENTS.md and use bootstrap-project. Inspect this repository first, ask
> only for missing project context, and prepare it for development on Linux and
> Windows with GitLab. Preserve existing files and document actual commands.

The interview populates [AgentDATA/context/project.md](AgentDATA/context/project.md),
[decisions](AgentDATA/context/decisions.md) and [handoff](AgentDATA/context/handoff.md). Then request your first
implementation task. On later sessions, ask the assistant to resume from the
handoff. Keep generic rules stable; project-specific information belongs in AgentDATA/.

## Included files

- [AGENTS.md](AGENTS.md): shared working rules.
- [AgentDATA/](AgentDATA/): the original context, memories, docs, logs, scripts, references, secrets, Knowledge, procedures, skills, mcp and tools folders.
- [GitLab procedure](AgentDATA/procedures/gitlab.md): branches, reviews and assistant handoffs.
- [Portability procedure](AgentDATA/procedures/portability.md): Linux/Windows conventions.
- [.gitlab/](.gitlab/): issue and merge request description templates.
- [.gitignore](.gitignore) and [.gitattributes](.gitattributes): minimal local-file rules.
- [Attribution](ATTRIBUTION.md): reusable course material provenance.

GitLab templates must reach the default branch to be offered by GitLab. Assistant
authentication is separate from GitLab authentication. Local editing does not need
an assistant cloud repository integration; remote operations require GitLab access.
Self-managed GitLab is supported by discovering its actual host, not hard-coding it.
For Copilot, this package targets local IDE agent work, not a GitHub cloud-agent job.

No universal CI job is enabled: bootstrap must select meaningful checks and a
compatible GitLab runner for the actual stack. Validate each OS separately before
claiming portability. The starter does not lower sandbox or approval settings.
For parallel Codex/Claude work, use separate branches/worktrees and scopes; the
default is sequential implementation/review with the shared handoff.

## Verify after copying

Start a fresh assistant session in the destination. Ask it to identify the loaded
instructions, explain the current project and next task, and locate its bootstrap
skill. Verify that it uses the GitLab procedure and can recover the handoff without
the previous chat. File presence alone does not prove automatic discovery.

## Documentation

- [Codex AGENTS.md](https://developers.openai.com/codex/guides/agents-md)
- [Codex repository skills](https://developers.openai.com/blog/skills-agents-sdk)
- [Claude Code memory](https://code.claude.com/docs/en/memory)
- [Claude Code skills](https://code.claude.com/docs/en/skills)

- [GitLab description templates](https://docs.gitlab.com/user/project/description_templates/)

## Original AgentDATA tree

- [context/](AgentDATA/context/README.md): Current project requirements, decisions and the next-session handoff.
- [memories/](AgentDATA/memories/README.md): Dated session observations and lessons; keep current next actions in context/handoff.md.
- [docs/](AgentDATA/docs/README.md): Auxiliary design documents, validation reports and operational explanations.
- [logs/](AgentDATA/logs/README.md): Dated structured execution evidence. Record real commands and outcomes; redact sensitive values.
- [scripts/](AgentDATA/scripts/README.md): Project operational helpers. Choose the project runtime; TypeScript is only the supplied example.
- [references/](AgentDATA/references/README.md): External technical references with source, revision/date and applicable attribution.
- [Knowledge/](AgentDATA/Knowledge/README.md): Maintained, reusable technical findings with evidence, scope and invalidation conditions.
- [procedures/](AgentDATA/procedures/README.md): Operational instructions loaded only when the task needs them.
- [skills/](AgentDATA/skills/README.md): Catalog of skills and their native assistant discovery paths; no installations happen here.
- [mcp/](AgentDATA/mcp/README.md): Catalog of MCP integrations, required access and verified operations; credentials stay local.
- [tools/](AgentDATA/tools/README.md): Catalog of CLI tools, dependencies, command contracts and availability evidence.
- [secrets/](AgentDATA/secrets/README.md): Ignored local credential material and safe versioned examples; prefer the environment secret store.

All original AgentDATA reference filenames and templates are included. Content
is adapted for these assistants, GitLab and portable workflows. Optional npm/PyPI
procedures and the TypeScript scaffold do not select a stack or authorize release.
