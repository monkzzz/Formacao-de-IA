# Capability discovery

Consult [CLI tools](cli.md), [skills](skills.md), and [MCP integrations](mcp.md)
when a task needs them. No registry installs tools or grants external authority.

For each capability record purpose, when to use/avoid, inputs, outputs, dependencies,
side effects, access scope, risks, configuration variable names, validation method,
date/version and evidence. Keep required, desired and available as separate fields.

Use availability states `not checked`, `advertised`, `verified`, `unavailable`, or
`stale`. Advertised means found in a catalog/configuration; verified means a named
operation actually succeeded in the target environment. Verification is scoped to
that operation and environment, not every feature. Recheck after environment changes.

When a required capability is missing, use a safe available equivalent if it meets
the contract. Otherwise document the dependency, continue independent work and ask
for the minimum missing information or access. Do not install services, create
credentials or make paid/external changes merely to fill this registry.
