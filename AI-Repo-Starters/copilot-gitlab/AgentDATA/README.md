# AgentDATA

Original course directory structure, with project-neutral English instructions.

- [context/](context/README.md): Current project requirements, decisions and the next-session handoff.
- [memories/](memories/README.md): Dated session observations and lessons; keep current next actions in context/handoff.md.
- [docs/](docs/README.md): Auxiliary design documents, validation reports and operational explanations.
- [logs/](logs/README.md): Dated structured execution evidence. Record real commands and outcomes; redact sensitive values.
- [scripts/](scripts/README.md): Project operational helpers. Choose the project runtime; TypeScript is only the supplied example.
- [references/](references/README.md): External technical references with source, revision/date and applicable attribution.
- [Knowledge/](Knowledge/README.md): Maintained, reusable technical findings with evidence, scope and invalidation conditions.
- [procedures/](procedures/README.md): Operational instructions loaded only when the task needs them.
- [skills/](skills/README.md): Catalog of skills and their native assistant discovery paths; no installations happen here.
- [mcp/](mcp/README.md): Catalog of MCP integrations, required access and verified operations; credentials stay local.
- [tools/](tools/README.md): Catalog of CLI tools, dependencies, command contracts and availability evidence.
- [secrets/](secrets/README.md): Ignored local credential material and safe versioned examples; prefer the environment secret store.

Keep exact filename case on Linux and Windows. AgentDATA is shared by assistants;
load only relevant records. Assistant entry files remain at the repository root
and native skills remain in their assistant-specific directories.
