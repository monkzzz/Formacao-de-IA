# Fresh-session starter reuse and safe-task experiment

Date: 2026-10-17. Actor: a separate agent session given the fixture path and explicit scenario, without inherited parent chat. Platform system/developer instructions and the direct experiment assignment were present. This is not an independent human test.

## Exact hypothetical user scenario

> Reuse this starter for my household book lending ledger. This is a hypothetical documentation exercise. English, local Markdown only, no runtime, accounts, deployment, personal names or real records. Success: document fields book title, borrower alias, due date, returned flag; provide one clearly synthetic row; verify local links. You are authorized to update context/project.md, context/handoff.md and create docs/lending-example.md in this fixture. Preserve generic rules, record checks, no Git commit/push.

## Scope and instruction discovery

Only the copied fixture was inspected and changed. The real starter was not read or edited. The parent requested this report outside the fixture; that report is experiment evidence rather than part of the hypothetical ledger. Explicitly read fixture AGENTS.md and its referenced relevant instructions. This demonstrates behavior after explicit file instructions, not automatic discovery by Copilot or any other assistant.

Read files, all relative to `participant-work/day2/.starter-reuse-fixture/`:

- AGENTS.md
- README.md
- context/project.md
- context/handoff.md
- context/decisions.md
- procedures/workflow.md
- procedures/git-and-safety.md
- evidence/README.md
- knowledge/README.md
- capabilities/README.md
- capabilities/cli.md

Listed nested AGENTS.md files: only the fixture root file was found. Listed context and knowledge directories; knowledge contained only its README. Read the final three affected files directly for review.

## Observed behavior and choices

Replaced unknown project goals with the supplied ledger requirements. Kept generic rules, procedures, attribution and capability registries unchanged. Used English, an ISO date, true/false flag values, and an unmistakably synthetic title and alias. No question was necessary to implement this reversible scope. Did not invent real records, personal names, accounts, deployment settings or runtime requirements.

Python 3.12.10 was used only as an available local verification tool, with no installation or project runtime selection. The shell wrapper RTK and Python paths were discovered using Get-Command. No external tool, authentication or service was needed.

Unknowns remain branch/commit, remote, deployment target and real household details. These did not block the request and were not inspected. Git status had no fixture entries, but check-ignore reported the fixture is ignored; a clean status therefore does not establish an unchanged fixture. Contents were reviewed directly.

Evidence is retained here and summarized in the authorized handoff. No extra evidence or decision files were added inside the fixture, because the hypothetical authorization named only three files. Routine formatting choices are recorded in context/project.md.

## Commands, actions and results

All shell commands were RTK-prefixed. Unless specified, working directory was the fixture absolute path:
`C:\Users\falle\Nextcloud\dev_server\IA_Formation\Formacao-de-IA\participant-work\day2\.starter-reuse-fixture`.

1. From the workspace root, exit 0:

```powershell
rtk proxy powershell -NoProfile -Command "Get-ChildItem -Force participant-work/day2/.starter-reuse-fixture; Get-Content participant-work/day2/.starter-reuse-fixture/AGENTS.md"
```

Result: listed the copied starter and read its agreement.

2. Exit 0:

```powershell
rtk proxy powershell -NoProfile -Command "Get-Content README.md,context/project.md,context/handoff.md,procedures/workflow.md,procedures/git-and-safety.md,evidence/README.md,knowledge/README.md,capabilities/README.md; Get-ChildItem -Recurse -Filter AGENTS.md; Get-ChildItem context,knowledge; git status --short -- ."
```

Result: read rules/context; no nested agreements; no status entries.

3. Exit 0:

```powershell
rtk proxy powershell -NoProfile -Command "Get-Content context/decisions.md,capabilities/cli.md; Get-Command python,rtk | Select-Object Name,Source; git status --short --untracked-files=all -- .; git check-ignore ."
```

Result: empty generic decision register; Python and RTK executables found; status empty; check-ignore printed a dot.

4. FAIL: attempted an RTK-wrapped nested PowerShell command containing a Python here-string to write and verify the three files. Exit 1. The outer invocation was `rtk proxy powershell -NoProfile -Command @' ... '@`. The nested here-string lost its opening double quote and PowerShell reported `$script = @`, "Unrecognized token in source text", then interpreted Python as PowerShell ("The 'from' keyword is not supported"). Parsing failed before any writes or checks. No passing result was claimed.

5. FAIL: direct apply_patch attempted Delete File plus Add File operations for the same existing paths. Tool validation rejected it: "invalid patch: multiple operations target ...context/project.md". No edits were applied.

6. PASS: corrected execution by using UTF-16LE Base64 for a PowerShell EncodedCommand. Exit 0. The actual command is preserved below; its decoded script follows for readability.

```powershell
rtk proxy powershell -NoProfile -EncodedCommand JABwAHIAbwBqAGUAYwB0ACAAPQAgAEAAJwAKACMAIABQAHIAbwBqAGUAYwB0ACAAYwBvAG4AdABlAHgAdAAKAAoAUwB0AGEAdAB1AHMAOgAgAGgAeQBwAG8AdABoAGUAdABpAGMAYQBsACAAaABvAHUAcwBlAGgAbwBsAGQAIABiAG8AbwBrACAAbABlAG4AZABpAG4AZwAgAGwAZQBkAGcAZQByAC4ACgBDAG8AbgBmAGkAcgBtAGUAZAA6ACAARQBuAGcAbABpAHMAaAAsACAAbABvAGMAYQBsACAATQBhAHIAawBkAG8AdwBuACAAbwBuAGwAeQA7ACAAbgBvACAAcgB1AG4AdABpAG0AZQAsACAAYQBjAGMAbwB1AG4AdABzACwAIABkAGUAcABsAG8AeQBtAGUAbgB0ACwAIABwAGUAcgBzAG8AbgBhAGwAIABuAGEAbQBlAHMAIABvAHIAIAByAGUAYQBsACAAcgBlAGMAbwByAGQAcwAuAAoAQQBjAGMAZQBwAHQAYQBuAGMAZQA6ACAAZABvAGMAdQBtAGUAbgB0ACAAYgBvAG8AawAgAHQAaQB0AGwAZQAsACAAYgBvAHIAcgBvAHcAZQByACAAYQBsAGkAYQBzACwAIABkAHUAZQAgAGQAYQB0AGUAIABhAG4AZAAgAHIAZQB0AHUAcgBuAGUAZAAgAGYAbABhAGcAOwAgAHAAcgBvAHYAaQBkAGUAIABvAG4AZQAgAGMAbABlAGEAcgBsAHkAIABzAHkAbgB0AGgAZQB0AGkAYwAgAHIAbwB3ADsAIAB2AGUAcgBpAGYAeQAgAGwAbwBjAGEAbAAgAGwAaQBuAGsAcwAuAAoAUwBlAGUAIABbAGUAeABhAG0AcABsAGUAXQAoAC4ALgAvAGQAbwBjAHMALwBsAGUAbgBkAGkAbgBnAC0AZQB4AGEAbQBwAGwAZQAuAG0AZAApACAAYQBuAGQAIABbAGgAYQBuAGQAbwBmAGYAXQAoAGgAYQBuAGQAbwBmAGYALgBtAGQAKQAuAAoACgBSAG8AdQB0AGkAbgBlACAAYwBoAG8AaQBjAGUAcwA6ACAASQBTAE8AIABkAGEAdABlACAAWQBZAFkAWQAtAE0ATQAtAEQARAAgAGEAbgBkACAAdAByAHUAZQAvAGYAYQBsAHMAZQAgAGYAbABhAGcAcwA7ACAAZQB4AHAAbABpAGMAaQB0AGwAeQAgAHMAeQBuAHQAaABlAHQAaQBjACAAdABpAHQAbABlACAAYQBuAGQAIABhAGwAaQBhAHMALgAKAFUAbgBrAG4AbwB3AG4AIABhAG4AZAAgAHUAbgBuAGUAYwBlAHMAcwBhAHIAeQA6ACAAcgBlAGEAbAAgAGgAbwB1AHMAZQBoAG8AbABkACAAZABhAHQAYQAsACAAYgByAGEAbgBjAGgALwBjAG8AbQBtAGkAdAAsACAAcgBlAG0AbwB0AGUAIABhAG4AZAAgAGQAZQBwAGwAbwB5AG0AZQBuAHQAIAB0AGEAcgBnAGUAdAAuAAoARwBlAG4AZQByAGkAYwAgAHAAcgBlAGYAZQByAGUAbgBjAGUAcwAgAHIAZQBtAGEAaQBuACAARQBuAGcAbABpAHMAaAAsACAAYQB1AHQAbwBuAG8AbQBvAHUAcwAgAGEAdQB0AGgAbwByAGkAegBlAGQAIAByAGUAdgBlAHIAcwBpAGIAbABlACAAdwBvAHIAawAsACAAZgBvAGMAdQBzAGUAZAAgAGMAaABhAG4AZwBlAHMALAAgAGUAdgBpAGQAZQBuAGMAZQAtAGIAYQBzAGUAZAAgAHIAZQB2AGkAZQB3ACAAYQBuAGQAIABwAHIAZQBzAGUAcgB2AGEAdABpAG8AbgAuAAoAUAByAGUAcwBlAHIAdgBlACAAWwByAHUAbABlAHMAXQAoAC4ALgAvAEEARwBFAE4AVABTAC4AbQBkACkALAAgAFsAdwBvAHIAawBmAGwAbwB3AF0AKAAuAC4ALwBwAHIAbwBjAGUAZAB1AHIAZQBzAC8AdwBvAHIAawBmAGwAbwB3AC4AbQBkACkALAAgAFsAZABlAGMAaQBzAGkAbwBuAHMAXQAoAGQAZQBjAGkAcwBpAG8AbgBzAC4AbQBkACkALAAgAFsAawBuAG8AdwBsAGUAZABnAGUAXQAoAC4ALgAvAGsAbgBvAHcAbABlAGQAZwBlAC8AUgBFAEEARABNAEUALgBtAGQAKQAgAGEAbgBkACAAWwBlAHYAaQBkAGUAbgBjAGUAIABjAG8AbgB0AHIAYQBjAHQAXQAoAC4ALgAvAGUAdgBpAGQAZQBuAGMAZQAvAFIARQBBAEQATQBFAC4AbQBkACkALgAKACcAQAAKACQAaABhAG4AZABvAGYAZgAgAD0AIABAACcACgAjACAAUwBlAHMAcwBpAG8AbgAgAGgAYQBuAGQAbwBmAGYACgAKAFMAdABhAHQAdQBzADoAIABhAHUAdABoAG8AcgBpAHoAZQBkACAAaAB5AHAAbwB0AGgAZQB0AGkAYwBhAGwAIABkAG8AYwB1AG0AZQBuAHQAYQB0AGkAbwBuACAAdABhAHMAawAgAGMAbwBtAHAAbABlAHQAZQBkACAAbwBuACAAMgAwADIANgAtADEAMAAtADEANwAuAAoAQwBoAGEAbgBnAGUAZAA6ACAAWwBwAHIAbwBqAGUAYwB0ACAAYwBvAG4AdABlAHgAdABdACgAcAByAG8AagBlAGMAdAAuAG0AZAApACwAIAB0AGgAaQBzACAAaABhAG4AZABvAGYAZgAgAGEAbgBkACAAWwBzAHkAbgB0AGgAZQB0AGkAYwAgAGUAeABhAG0AcABsAGUAXQAoAC4ALgAvAGQAbwBjAHMALwBsAGUAbgBkAGkAbgBnAC0AZQB4AGEAbQBwAGwAZQAuAG0AZAApAC4ACgBHAGUAbgBlAHIAaQBjACAAcgB1AGwAZQBzACAAcAByAGUAcwBlAHIAdgBlAGQALgAgAEUAeABhAG0AcABsAGUAIABkAG8AYwB1AG0AZQBuAHQAcwAgAGEAbABsACAAZgBvAHUAcgAgAHIAZQBxAHUAaQByAGUAZAAgAGYAaQBlAGwAZABzACAAYQBuAGQAIABvAG4AZQAgAGMAbABlAGEAcgBsAHkAIABzAHkAbgB0AGgAZQB0AGkAYwAgAHIAbwB3AC4ACgAKAEUAdgBpAGQAZQBuAGMAZQA6ACAAdABoAGUAIABzAGUAcABhAHIAYQB0AGUAIABmAHIAZQBzAGgALQBzAGUAcwBzAGkAbwBuACAAcgBlAHAAbwByAHQAIAByAGUAYwBvAHIAZABzACAAYwBvAG0AbQBhAG4AZABzACwAIAByAGUAcwB1AGwAdABzACAAYQBuAGQAIABsAGkAbQBpAHQAcwAuAAoAUAB5AHQAaABvAG4AIABpAHMAIABhACAAbABvAGMAYQBsACAAdgBlAHIAaQBmAGkAYwBhAHQAaQBvAG4AIAB0AG8AbwBsACAAbwBuAGwAeQA7ACAAbgBvACAAcAByAG8AagBlAGMAdAAgAHIAdQBuAHQAaQBtAGUAIABvAHIAIABkAGUAcABlAG4AZABlAG4AYwBpAGUAcwAgAHMAZQBsAGUAYwB0AGUAZAAuAAoAVABoAGUAIABmAGkAcgBzAHQAIABuAGUAcwB0AGUAZAAgAFAAbwB3AGUAcgBTAGgAZQBsAGwAIAB3AHIAaQB0AGUAIABhAHQAdABlAG0AcAB0ACAAZgBhAGkAbABlAGQAIABwAGEAcgBzAGkAbgBnACAAYgBlAGYAbwByAGUAIABlAGQAaQB0AHMALgAgAEEAIABkAGkAcgBlAGMAdAAgAHAAYQB0AGMAaAAgAGEAbABzAG8AIABmAGEAaQBsAGUAZAAgAHYAYQBsAGkAZABhAHQAaQBvAG4AIABiAGUAZgBvAHIAZQAgAGUAZABpAHQAcwAuACAAQQBuACAAZQBuAGMAbwBkAGUAZAAgAFAAbwB3AGUAcgBTAGgAZQBsAGwAIABjAG8AbQBtAGEAbgBkACAAYwBvAHIAcgBlAGMAdABlAGQAIAB0AGgAZQAgAGUAeABlAGMAdQB0AGkAbwBuACAAYQBwAHAAcgBvAGEAYwBoAC4ACgBHAGkAdAAgAHMAdABhAHQAdQBzACAAcwBoAG8AdwBlAGQAIABuAG8AIABmAGkAeAB0AHUAcgBlACAAZQBuAHQAcgBpAGUAcwA7ACAAZwBpAHQAIABjAGgAZQBjAGsALQBpAGcAbgBvAHIAZQAgAHIAZQB0AHUAcgBuAGUAZAAgAGEAIABkAG8AdAA6ACAAdABoAGUAIABmAGkAeAB0AHUAcgBlACAAaQBzACAAaQBnAG4AbwByAGUAZAAsACAAcwBvACAAcwB0AGEAdAB1AHMAIABjAGEAbgBuAG8AdAAgAGUAcwB0AGEAYgBsAGkAcwBoACAAYQAgAGMAbABlAGEAbgAgAGQAaQBmAGYALgAgAFIAZQB2AGkAZQB3ACAAYwBvAG4AdABlAG4AdABzACAAZABpAHIAZQBjAHQAbAB5AC4ACgAKAFUAbgBrAG4AbwB3AG4AOgAgAGIAcgBhAG4AYwBoAC8AYwBvAG0AbQBpAHQAIABhAG4AZAAgAHIAZQBtAG8AdABlACAAdwBlAHIAZQAgAG4AbwB0ACAAaQBuAHMAcABlAGMAdABlAGQAIABiAGUAYwBhAHUAcwBlACAAcgBlAGEAZABzACAAYQByAGUAIABsAGkAbQBpAHQAZQBkACAAdABvACAAdABoAGkAcwAgAGYAaQB4AHQAdQByAGUALgAKAE4AbwAgAHIAZQBhAGwAIABkAGEAdABhACwAIABhAGMAYwBvAHUAbgB0AHMALAAgAGQAZQBwAGwAbwB5AG0AZQBuAHQALAAgAGMAbwBtAG0AaQB0ACAAbwByACAAcAB1AHMAaAAuACAATgBvACAAYQBjAGMAZQBwAHQAYQBuAGMAZQAtAGIAbABvAGMAawBpAG4AZwAgAHEAdQBlAHMAdABpAG8AbgAgAHIAZQBtAGEAaQBuAHMALgAKAE4AZQB4AHQAIABhAGMAdABpAG8AbgA6ACAAcgBlAHYAaQBlAHcAIAB0AGgAZQBzAGUAIAB0AGgAcgBlAGUAIABNAGEAcgBrAGQAbwB3AG4AIABmAGkAbABlAHMAIABhAG4AZAAgAHQAaABlACAAZQB4AHAAZQByAGkAbQBlAG4AdAAgAHIAZQBwAG8AcgB0ADsAIABuAG8AIABmAHUAcgB0AGgAZQByACAAdABhAHMAawAgAGEAcwBzAHUAbQBlAGQALgAKACcAQAAKACQAZQB4AGEAbQBwAGwAZQAgAD0AIABAACcACgAjACAASABvAHUAcwBlAGgAbwBsAGQAIABiAG8AbwBrACAAbABlAG4AZABpAG4AZwAgAGwAZQBkAGcAZQByAAoACgBUAGgAaQBzACAAZQB4AGUAcgBjAGkAcwBlACAAYwBvAG4AdABhAGkAbgBzACAAbwBuAGwAeQAgAHMAeQBuAHQAaABlAHQAaQBjACAAZABhAHQAYQAsACAAcgBlAHAAcgBlAHMAZQBuAHQAaQBuAGcAIABuAG8AIAByAGUAYQBsACAAcABlAHIAcwBvAG4ALAAgAGgAbwB1AHMAZQBoAG8AbABkACAAbwByACAAbABvAGEAbgAuAAoACgB8ACAARgBpAGUAbABkACAAfAAgAE0AZQBhAG4AaQBuAGcAIAB8ACAARQB4AGEAbQBwAGwAZQAgAGYAbwByAG0AYQB0ACAAfAAKAHwAIAAtAC0ALQAgAHwAIAAtAC0ALQAgAHwAIAAtAC0ALQAgAHwACgB8ACAAQgBvAG8AawAgAHQAaQB0AGwAZQAgAHwAIABUAGkAdABsAGUAIABvAGYAIAB0AGgAZQAgAGIAbwByAHIAbwB3AGUAZAAgAGIAbwBvAGsAIAB8ACAAUABsAGEAaQBuACAAdABlAHgAdAAgAHwACgB8ACAAQgBvAHIAcgBvAHcAZQByACAAYQBsAGkAYQBzACAAfAAgAEYAaQBjAHQAaQB0AGkAbwB1AHMAIABpAGQAZQBuAHQAaQBmAGkAZQByACAAdwBpAHQAaABvAHUAdAAgAGEAIABwAGUAcgBzAG8AbgBhAGwAIABuAGEAbQBlACAAfAAgAHMAeQBuAHQAaABlAHQAaQBjAC0AcgBlAGEAZABlAHIALQAwADEAIAB8AAoAfAAgAEQAdQBlACAAZABhAHQAZQAgAHwAIABFAHgAcABlAGMAdABlAGQAIAByAGUAdAB1AHIAbgAgAGQAYQB0AGUAIAB8ACAAWQBZAFkAWQAtAE0ATQAtAEQARAAgAHwACgB8ACAAUgBlAHQAdQByAG4AZQBkACAAZgBsAGEAZwAgAHwAIABXAGgAZQB0AGgAZQByACAAdABoAGUAIABiAG8AbwBrACAAdwBhAHMAIAByAGUAdAB1AHIAbgBlAGQAIAB8ACAAdAByAHUAZQAgAG8AcgAgAGYAYQBsAHMAZQAgAHwACgAKACMAIwAgAEMAbABlAGEAcgBsAHkAIABzAHkAbgB0AGgAZQB0AGkAYwAgAGUAeABhAG0AcABsAGUACgAKAHwAIABCAG8AbwBrACAAdABpAHQAbABlACAAfAAgAEIAbwByAHIAbwB3AGUAcgAgAGEAbABpAGEAcwAgAHwAIABEAHUAZQAgAGQAYQB0AGUAIAB8ACAAUgBlAHQAdQByAG4AZQBkACAAZgBsAGEAZwAgAHwACgB8ACAALQAtAC0AIAB8ACAALQAtAC0AIAB8ACAALQAtAC0AIAB8ACAALQAtAC0AIAB8AAoAfAAgAEkAbQBhAGcAaQBuAGEAcgB5ACAAQQB0AGwAYQBzACAAbwBmACAAUABhAHAAZQByACAATQBvAG8AbgBzACAAKABzAHkAbgB0AGgAZQB0AGkAYwApACAAfAAgAHMAeQBuAHQAaABlAHQAaQBjAC0AcgBlAGEAZABlAHIALQAwADEAIAB8ACAAMgAwADMAMAAtADAAMQAtADEANQAgAHwAIABmAGEAbABzAGUAIAB8AAoACgBSAGUAdAB1AHIAbgAgAHQAbwAgAFsAcAByAG8AagBlAGMAdAAgAGMAbwBuAHQAZQB4AHQAXQAoAC4ALgAvAGMAbwBuAHQAZQB4AHQALwBwAHIAbwBqAGUAYwB0AC4AbQBkACkAIABvAHIAIABbAGgAYQBuAGQAbwBmAGYAXQAoAC4ALgAvAGMAbwBuAHQAZQB4AHQALwBoAGEAbgBkAG8AZgBmAC4AbQBkACkALgAKACcAQAAKAE4AZQB3AC0ASQB0AGUAbQAgAC0ASQB0AGUAbQBUAHkAcABlACAARABpAHIAZQBjAHQAbwByAHkAIAAtAEYAbwByAGMAZQAgAGQAbwBjAHMAIAB8ACAATwB1AHQALQBOAHUAbABsAAoAUwBlAHQALQBDAG8AbgB0AGUAbgB0ACAALQBMAGkAdABlAHIAYQBsAFAAYQB0AGgAIABjAG8AbgB0AGUAeAB0AC8AcAByAG8AagBlAGMAdAAuAG0AZAAgAC0AVgBhAGwAdQBlACAAJABwAHIAbwBqAGUAYwB0ACAALQBFAG4AYwBvAGQAaQBuAGcAIABVAFQARgA4AAoAUwBlAHQALQBDAG8AbgB0AGUAbgB0ACAALQBMAGkAdABlAHIAYQBsAFAAYQB0AGgAIABjAG8AbgB0AGUAeAB0AC8AaABhAG4AZABvAGYAZgAuAG0AZAAgAC0AVgBhAGwAdQBlACAAJABoAGEAbgBkAG8AZgBmACAALQBFAG4AYwBvAGQAaQBuAGcAIABVAFQARgA4AAoAUwBlAHQALQBDAG8AbgB0AGUAbgB0ACAALQBMAGkAdABlAHIAYQBsAFAAYQB0AGgAIABkAG8AYwBzAC8AbABlAG4AZABpAG4AZwAtAGUAeABhAG0AcABsAGUALgBtAGQAIAAtAFYAYQBsAHUAZQAgACQAZQB4AGEAbQBwAGwAZQAgAC0ARQBuAGMAbwBkAGkAbgBnACAAVQBUAEYAOAAKAEcAZQB0AC0AQwBvAG4AdABlAG4AdAAgAGMAbwBuAHQAZQB4AHQALwBwAHIAbwBqAGUAYwB0AC4AbQBkACwAYwBvAG4AdABlAHgAdAAvAGgAYQBuAGQAbwBmAGYALgBtAGQALABkAG8AYwBzAC8AbABlAG4AZABpAG4AZwAtAGUAeABhAG0AcABsAGUALgBtAGQA
```

Decoded exact payload:

```powershell
$project = @'
# Project context

Status: hypothetical household book lending ledger.
Confirmed: English, local Markdown only; no runtime, accounts, deployment, personal names or real records.
Acceptance: document book title, borrower alias, due date and returned flag; provide one clearly synthetic row; verify local links.
See [example](../docs/lending-example.md) and [handoff](handoff.md).

Routine choices: ISO date YYYY-MM-DD and true/false flags; explicitly synthetic title and alias.
Unknown and unnecessary: real household data, branch/commit, remote and deployment target.
Generic preferences remain English, autonomous authorized reversible work, focused changes, evidence-based review and preservation.
Preserve [rules](../AGENTS.md), [workflow](../procedures/workflow.md), [decisions](decisions.md), [knowledge](../knowledge/README.md) and [evidence contract](../evidence/README.md).
'@
$handoff = @'
# Session handoff

Status: authorized hypothetical documentation task completed on 2026-10-17.
Changed: [project context](project.md), this handoff and [synthetic example](../docs/lending-example.md).
Generic rules preserved. Example documents all four required fields and one clearly synthetic row.

Evidence: the separate fresh-session report records commands, results and limits.
Python is a local verification tool only; no project runtime or dependencies selected.
The first nested PowerShell write attempt failed parsing before edits. A direct patch also failed validation before edits. An encoded PowerShell command corrected the execution approach.
Git status showed no fixture entries; git check-ignore returned a dot: the fixture is ignored, so status cannot establish a clean diff. Review contents directly.

Unknown: branch/commit and remote were not inspected because reads are limited to this fixture.
No real data, accounts, deployment, commit or push. No acceptance-blocking question remains.
Next action: review these three Markdown files and the experiment report; no further task assumed.
'@
$example = @'
# Household book lending ledger

This exercise contains only synthetic data, representing no real person, household or loan.

| Field | Meaning | Example format |
| --- | --- | --- |
| Book title | Title of the borrowed book | Plain text |
| Borrower alias | Fictitious identifier without a personal name | synthetic-reader-01 |
| Due date | Expected return date | YYYY-MM-DD |
| Returned flag | Whether the book was returned | true or false |

## Clearly synthetic example

| Book title | Borrower alias | Due date | Returned flag |
| --- | --- | --- | --- |
| Imaginary Atlas of Paper Moons (synthetic) | synthetic-reader-01 | 2030-01-15 | false |

Return to [project context](../context/project.md) or [handoff](../context/handoff.md).
'@
New-Item -ItemType Directory -Force docs | Out-Null
Set-Content -LiteralPath context/project.md -Value $project -Encoding UTF8
Set-Content -LiteralPath context/handoff.md -Value $handoff -Encoding UTF8
Set-Content -LiteralPath docs/lending-example.md -Value $example -Encoding UTF8
Get-Content context/project.md,context/handoff.md,docs/lending-example.md
```

Result: created docs/ and wrote the three authorized Markdown files, then printed their contents for direct review. PowerShell also emitted a CLIXML module-initialization progress record; no error was reported.

7. PASS: RTK-wrapped encoded PowerShell fed a Python standard-library checker through stdin and repeated read-only Git inspection. Exit 0.

```powershell
rtk proxy powershell -NoProfile -EncodedCommand JABjAGgAZQBjAGsAIAA9ACAAQAAnAAoAZgByAG8AbQAgAHAAYQB0AGgAbABpAGIAIABpAG0AcABvAHIAdAAgAFAAYQB0AGgACgBpAG0AcABvAHIAdAAgAHIAZQAsAHMAeQBzAAoAcgBvAG8AdAA9AFAAYQB0AGgALgBjAHcAZAAoACkACgBmAGkAbABlAHMAPQBbACcAYwBvAG4AdABlAHgAdAAvAHAAcgBvAGoAZQBjAHQALgBtAGQAJwAsACcAYwBvAG4AdABlAHgAdAAvAGgAYQBuAGQAbwBmAGYALgBtAGQAJwAsACcAZABvAGMAcwAvAGwAZQBuAGQAaQBuAGcALQBlAHgAYQBtAHAAbABlAC4AbQBkACcAXQAKAGMAbwB1AG4AdAA9ADAACgBmAG8AcgAgAG4AYQBtAGUAIABpAG4AIABmAGkAbABlAHMAOgAKACAAcAA9AHIAbwBvAHQALwBuAGEAbQBlAAoAIABjAG8AbgB0AGUAbgB0AD0AcAAuAHIAZQBhAGQAXwB0AGUAeAB0ACgAZQBuAGMAbwBkAGkAbgBnAD0AJwB1AHQAZgAtADgALQBzAGkAZwAnACkACgAgAGYAbwByACAAbABpAG4AawAgAGkAbgAgAHIAZQAuAGYAaQBuAGQAYQBsAGwAKAByACcAXABbAFsAXgBcAF0AXQArAFwAXQBcACgAKABbAF4AKQBdACsAKQBcACkAJwAsAGMAbwBuAHQAZQBuAHQAKQA6AAoAIAAgAGEAcwBzAGUAcgB0ACAAKABwAC4AcABhAHIAZQBuAHQALwBsAGkAbgBrACkALgByAGUAcwBvAGwAdgBlACgAKQAuAGkAcwBfAGYAaQBsAGUAKAApACwAKABuAGEAbQBlACwAbABpAG4AawApAAoAIAAgAGMAbwB1AG4AdAArAD0AMQAKACAAcAByAGkAbgB0ACgAJwBSAEUAVgBJAEUAVwAnACwAbgBhAG0AZQAsAGwAZQBuACgAYwBvAG4AdABlAG4AdAAuAHMAcABsAGkAdABsAGkAbgBlAHMAKAApACkALAAnAGwAaQBuAGUAcwAnACkACgBlAHgAYQBtAHAAbABlAD0AKAByAG8AbwB0AC8AZgBpAGwAZQBzAFsAMgBdACkALgByAGUAYQBkAF8AdABlAHgAdAAoAGUAbgBjAG8AZABpAG4AZwA9ACcAdQB0AGYALQA4AC0AcwBpAGcAJwApAAoAZgBvAHIAIABmAGkAZQBsAGQAIABpAG4AIABbACcAQgBvAG8AawAgAHQAaQB0AGwAZQAnACwAJwBCAG8AcgByAG8AdwBlAHIAIABhAGwAaQBhAHMAJwAsACcARAB1AGUAIABkAGEAdABlACcALAAnAFIAZQB0AHUAcgBuAGUAZAAgAGYAbABhAGcAJwBdADoACgAgAGEAcwBzAGUAcgB0ACAAZgBpAGUAbABkACAAaQBuACAAZQB4AGEAbQBwAGwAZQAsAGYAaQBlAGwAZAAKAGEAcwBzAGUAcgB0ACAAZQB4AGEAbQBwAGwAZQAuAGMAbwB1AG4AdAAoACcAfAAgAEkAbQBhAGcAaQBuAGEAcgB5ACAAQQB0AGwAYQBzACAAbwBmACAAUABhAHAAZQByACAATQBvAG8AbgBzACAAKABzAHkAbgB0AGgAZQB0AGkAYwApACAAfAAnACkAPQA9ADEACgBhAHMAcwBlAHIAdAAgACcAQwBsAGUAYQByAGwAeQAgAHMAeQBuAHQAaABlAHQAaQBjACAAZQB4AGEAbQBwAGwAZQAnACAAaQBuACAAZQB4AGEAbQBwAGwAZQAKAHAAcgBpAG4AdAAoACcAUABBAFMAUwA6ACcALABjAG8AdQBuAHQALAAnAGwAbwBjAGEAbAAgAGwAaQBuAGsAcwA7ACAAZgBvAHUAcgAgAGYAaQBlAGwAZABzADsAIABvAG4AZQAgAGUAeABwAGwAaQBjAGkAdABsAHkAIABzAHkAbgB0AGgAZQB0AGkAYwAgAGUAeABhAG0AcABsAGUAIAByAG8AdwAnACkACgBwAHIAaQBuAHQAKAAnAFYAZQByAGkAZgBpAGMAYQB0AGkAbwBuACAAdABvAG8AbAA6ACcALABzAHkAcwAuAHYAZQByAHMAaQBvAG4ALgBzAHAAbABpAHQAKAApAFsAMABdACkACgAnAEAACgAkAGMAaABlAGMAawAgAHwAIABwAHkAdABoAG8AbgAgAC0ACgBnAGkAdAAgAHMAdABhAHQAdQBzACAALQAtAHMAaABvAHIAdAAgAC0ALQB1AG4AdAByAGEAYwBrAGUAZAAtAGYAaQBsAGUAcwA9AGEAbABsACAALQAtACAALgAKAGcAaQB0ACAAYwBoAGUAYwBrAC0AaQBnAG4AbwByAGUAIAAuAA==
```

Decoded exact payload:

```powershell
$check = @'
from pathlib import Path
import re,sys
root=Path.cwd()
files=['context/project.md','context/handoff.md','docs/lending-example.md']
count=0
for name in files:
 p=root/name
 content=p.read_text(encoding='utf-8-sig')
 for link in re.findall(r'\[[^\]]+\]\(([^)]+)\)',content):
  assert (p.parent/link).resolve().is_file(),(name,link)
  count+=1
 print('REVIEW',name,len(content.splitlines()),'lines')
example=(root/files[2]).read_text(encoding='utf-8-sig')
for field in ['Book title','Borrower alias','Due date','Returned flag']:
 assert field in example,field
assert example.count('| Imaginary Atlas of Paper Moons (synthetic) |')==1
assert 'Clearly synthetic example' in example
print('PASS:',count,'local links; four fields; one explicitly synthetic example row')
print('Verification tool:',sys.version.split()[0])
'@
$check | python -
git status --short --untracked-files=all -- .
git check-ignore .
```

Observed output (excluding PowerShell module-progress CLIXML):

```text
REVIEW context/project.md 11 lines
REVIEW context/handoff.md 14 lines
REVIEW docs/lending-example.md 18 lines
PASS: 11 local links; four fields; one explicitly synthetic example row
Verification tool: 3.12.10
.
```

The dot is git check-ignore output; status emitted nothing. Assertions completed without error. Local links were checked for target-file existence, not web reachability or Markdown rendering. Fields and synthetic-row checks were confined to the example. No application build, GUI check or runtime test applies; none was run.

## Outcome and limits

PASS for this scoped hypothetical task: three files adapted, four fields documented, one clearly synthetic row, 11 local links verified, generic rules preserved. The fixture's generic README still describes starter preparation and is deliberately unchanged outside the authorized scope.

Observed recovery includes two failed execution approaches and a successful corrected approach. This is one controlled agent-session trial with explicit fixture instructions. It does not prove automatic instruction discovery, Copilot compatibility in execution, independent human usability, behavior across other agents or projects, standalone repository publication, or compliance under every future scenario. No Git commit, push or external action occurred.

Changed paths:

- .starter-reuse-fixture/context/project.md
- .starter-reuse-fixture/context/handoff.md
- .starter-reuse-fixture/docs/lending-example.md
- starter-fresh-session.md (this report)

All paths in the list are relative to participant-work/day2/.
