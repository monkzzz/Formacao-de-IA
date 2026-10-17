# CLI registry

All entries below are discovery candidates, **not verified in a future project**.
No project runtime is selected. Use the shared [record contract](README.md).

| Capability | Need | Availability | Purpose and safe probe | Constraints |
| --- | --- | --- | --- | --- |
| Git | Required when using Git history | Not checked | Status, diff, log; probe `git --version` then repository status | Probe is read-only; writes follow the Git procedure |
| ripgrep | Desired | Not checked | Search paths/content; probe `rg --version` | Avoid exposing secret file contents; fall back to native search |
| RTK | Optional unless the target environment requires it | Not checked | Reduce terminal output; probe `rtk --version` | Use `rtk proxy` for exact raw output; output filtering is not validation |
| Project runtime/package manager | Undecided | Not checked | Build/run/check the selected project | Discover executable and version; do not assume Python or Node |
| Hosting/GitHub CLI | Undecided | Not checked | Authorized remote management | Read access does not prove write access; do not assume authentication |

Replace candidate states with dated probe evidence in the target project. Record
the exact command, directory, version, exit/result and limits. Follow local shell
rules, including any required command wrapper, rather than copying commands blindly.
