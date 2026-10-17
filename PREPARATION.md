# Participant Preparation

Prepared on 2026-10-17 for the first five open tasks in [TASKS.md](TASKS.md).

## Working decisions

| Topic | Decision and evidence |
| --- | --- |
| Assistant | The participant explicitly declined Copilot. Continue with the current assistant and local tools; no Microsoft/GitHub Copilot account or extension is required for this participant's route. |
| Language | Write new work and communication in English, as requested by the participant. Preserve original teaching materials and attribution. |
| Autonomy | Complete the requested task batch, investigate independently, make reversible changes, and validate them. Clarify material unresolved choices when necessary. |
| Review | Review affected files and the diff, run relevant checks, then report outcomes and limitations. No additional approval gate is needed for this authorized batch. |
| Git publication | The participant expressly requested a commit followed by a push for this batch. This does not authorize future unrelated publications or changes to the existing production site. |
| Assessment | Preserve the original course rubric. The assistant substitution is a participant choice; instructor acceptance of tool-specific rubric differences remains unconfirmed. |

Task 1 is resolved by this explicit tool substitution, not by claiming access to Copilot. Repository reads, edits, shell execution, and validation have been exercised in the current session. No equivalent fresh-session skill test or classroom research interaction is claimed yet.

The initial VS Code extension listing did not show a Copilot extension and emitted a log-directory permission warning. Further Copilot setup is unnecessary following the participant's decision.

## Git repository and Pages destination

- Personal repository: `https://github.com/monkzzz/Formacao-de-IA.git`.
- Existing branch: `main`; remote: `origin`.
- Preparation baseline: `93461811be4bd2edc77c3738a5bc3e578c733dfa`.
- `git ls-remote origin HEAD` succeeded on 2026-10-17 and matched that baseline. This establishes read connectivity; successful push must be verified separately.
- Selected future Pages project URL: `https://monkzzz.github.io/Formacao-de-IA/`.
- Static site source: `dia2-local/dist/`, published as the root of a Pages artifact, rather than exposing the repository root as a website.
- Future publication method: a GitHub Actions Pages deployment that assembles this static directory and verified model binaries, with the repository's Pages source configured for Actions.

This completes preparation of a concrete destination. It does not assert that Pages is enabled, that the target URL is live, or that an Actions deployment has occurred. Those remain Exercise 3 publication work. The existing separately hosted application remains a distinct release destination.

Git is installed and the repository already has classifier history. No GitHub CLI is installed; Git itself is sufficient for the requested push. No Git author identity was configured during inspection. Use the existing history's automation identity, `Codex <codex@localhost>`, as a command-scoped identity for this assistant-created documentation commit, without changing global Git configuration or impersonating the participant.

## Slide preparation

All eleven PDFs were opened for preparation review: 83 pages in the text-readable GSS deck and 396 image-only pages across the other ten decks (479 total). The earlier aggregate of 496 image-only pages was an arithmetic error, corrected by the [2026-10-17 asset audit](participant-work/day2/handover-asset-audit.json); individual deck counts in the slide review were correct. The latter were rendered into temporary contact sheets and visually reviewed. All files are below 20,000,000 bytes.

The [slide review](SLIDE-REVIEW.md) connects the decks to the exercises, records takeaways, and lists questions for the course. This is an assistant preparation review, not evidence of the participant attending lessons or mastering the material. Fine print in contact sheets and empirical claims in the slides were not independently fact-checked.

## Preserve and reference the existing implementation

Use this existing personal fork as the participant workspace, and reference the current `dia2-local/` implementation in place. Its code and release reports already belong to the root Git history; there is no separate `dia2-local/.git` in the inspected checkout. Do not create another classifier or migrate it during preparation. The upstream teaching repository remains the course reference.

The course asks for implementations in a participant repository. The configured `monkzzz/Formacao-de-IA` remote is the selected personal destination, distinct from the course author's repository. If the instructor requires a standalone classifier repository instead of a personal course fork, perform that later with preserved history and record the deviation; this preparation does not claim instructor approval.

The [artifact inventory](preparation-artifacts.json) records relative paths, byte sizes, and SHA-256 hashes of the current exported model files, selected checkpoints/splits/frozen archives, and course PDFs. It also records the source baseline. Hashes provide transfer verification; they are not backups.

| Material | Preservation decision |
| --- | --- |
| Source, tests, docs, tracked reports | Retain root Git history; clone the personal repository when moving machines. Preserve original report versions and attribution. |
| `dia2-local/dist/model/` | Keep all current and historical exports, including ignored weights and parity fixtures. Restore them separately after cloning and verify the inventory before inference. |
| `dia2-local/artifacts/` | Preserve this entire ignored directory privately, especially original `frozen-app.zip`, checkpoints, splits, later frozen evaluations, and deployment backups. The inventory covers selected reproducibility artifacts, not every generated fixture or backup. |
| `dia2-local/reports/` | Preserve tracked reports and separately retain ignored screenshots and challenge inputs needed as evidence. Existing unrelated untracked reports are left untouched. |
| Dataset files and environment | Preserve dataset provenance and checksums. Recreate the environment from documented requirements rather than copying `.venv/` into Git. |
| Credentials | Keep local credentials separate from source and public deployment artifacts. No credential contents were read for this preparation. |
| Optional ROM/assets | Keep ignored optional ROMs out of the repository and core classifier submission; they are not a classifier prerequisite. |

For a future transfer: clone the complete repository, restore ignored models and private evaluation artifacts from a private backup, compare their SHA-256 hashes with the inventory, then run the documented unit and browser checks with new output names. Do not overwrite old reports, regenerate the official challenge, or rerun training to recreate the original independent evaluation. If files differ, investigate the version mismatch before accepting the transfer.

No files were moved, no model weights or challenge records were modified, and no ignored binaries were added to Git as part of this preparation. Creation and validation of an off-machine backup remain a separate operational activity.
