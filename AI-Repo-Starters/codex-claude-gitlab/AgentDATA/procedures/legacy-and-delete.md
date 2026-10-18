# Migrations and removal of obsolete files

Paths below refer to AgentDATA unless stated otherwise.

Identify consumers, compatibility requirements and the exact target boundaries.
Inspect Git status and references before removal. Prefer a focused migration with
appropriate verification; preserve unrelated data and historical evidence.
Destructive or irreversible actions need authorization within the active scope.
Update callers and documentation together, then verify that the old path is no
longer required. Do not delete a directory merely to make a command succeed.
