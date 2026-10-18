# Linux and Windows

Detect the OS, shell and executable paths instead of reusing commands blindly.
Treat native Windows and WSL as different runtime environments. Keep virtual
environments, dependencies and generated binaries local to each OS; do not copy
them between Windows and Linux or share the same environment in a synced folder.

Use repository-relative paths, exact filename case and quoted arguments. Avoid
hard-coded home directories, drive letters and hostnames. Prefer standard library
path handling in scripts. Do not require symlinks, executable permission bits,
Unix-only utilities or globally installed command wrappers for basic setup.

Document the actual project's Bash and PowerShell commands in `AgentDATA/context/project.md`.
If Python is selected, typical interpreter locations differ:

| Task | Linux / Bash | Windows / PowerShell |
| --- | --- | --- |
| Create environment | `python3 -m venv .venv` | `py -3 -m venv .venv` |
| Use interpreter | `.venv/bin/python` | `.\.venv\Scripts\python.exe` |

These are conditional examples, not a requirement to use Python. Direct executable
paths avoid activation policy changes. Use an available interpreter if `py` or
`python3` is absent. Pin relevant dependencies according to the selected stack.

Retain the project's line-ending policy. The supplied `.gitattributes` only
normalizes starter Markdown files; do not renormalize an existing repository
as a side effect. Verify behavior on each OS before claiming cross-platform tests.
