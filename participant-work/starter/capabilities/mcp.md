# MCP and connector registry

Required integrations: **none selected**. Configured or authenticated integrations
in a new project: **not checked**. This starter carries no server configuration.

For a needed integration record its purpose, owner/source, protocol/transport,
tool contracts, input/output data, dependencies, permission scope, side effects,
failure behavior, configuration variable names and verification evidence using the
[shared contract](README.md). Keep real credentials in an approved local secret
store or ignored configuration; never add token values to this registry.

Discover only the tools relevant to the active task using the host's available
tool catalog. Separate an advertised tool schema from a successful read probe,
authenticated access and authorized writes. Prefer a read-only representative
probe when needed. Do not contact third parties, create accounts, install servers
or request broad permissions just to mark an integration available.

If discovery or a call fails, record its exact scope and error without credential
contents. Use a local equivalent where suitable, or leave the dependent work
explicitly pending and report the minimum needed access.
