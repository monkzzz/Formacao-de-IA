# Teaching assets and attribution review

Reviewed 2026-10-17. [Machine inventory](handover-asset-audit.json) and
[audit script](audit-handover-assets.py) preserve exact identities. This is a
review of supplied local materials and notices, not rights clearance or independent
verification of every claim made in the teaching slides.

## Slides and navigation

All eleven PDFs opened successfully and remain below 20,000,000 bytes. Individual
counts match [SLIDE-REVIEW.md](../../SLIDE-REVIEW.md): 83 GSS pages plus 396 pages
in the other ten decks, **479 total**. The older preparation aggregate of 496
image-only pages was an arithmetic error; [PREPARATION.md](../../PREPARATION.md)
now records the corrected count and its source. No PDF was modified.

The root navigation's numbered sequence remains Whoami (0), the joint GSS modules
(1 and 2), then The Basics through Model Chosing (3–7); Day 2 lists Coding Agents
through VDD and Autonomy (2–5). These are course module numbers, not missing files.
Relative slide links resolve to the inventoried decks, including encoded spaces
and the accented joint GSS filename.

The assistant visually inspected a fresh contact sheet of all eleven covers and
full renders of LLM Anatomy PDF page 18 and From LLM to Chatbot PDF page 27.
The solid blue page and presentation-development screenshot are still present;
they remain observations, not automatic correction targets. Whoami's first page
is black in the cover sheet. The earlier full-deck contact-sheet review remains
the evidence for broader content review; this batch does not claim a fresh
page-by-page reading. Fresh renders are local ignored files under
`dia2-local/.tmp/handover-assets/`.

## Attribution and provenance

| Material | Verified local evidence | Limits |
| --- | --- | --- |
| Course materials | [LICENSE.md](../../LICENSE.md) and [CITATION.cff](../../CITATION.cff) name Vinicius Canonici and Hugo Gomes and identify CC BY 4.0 | Citation retains upstream course identity; it does not identify the participant fork as the original work |
| Imported GSS demonstrations | All **63** destination hashes match [origem.json](../../Dia1/Exercicios-GSS/origem.json); eight source/destination differences are already declared import adaptations | Remote origin was not fetched again; no imported file or provenance entry was changed |
| GSS images and recordings | [Resource guide](../../Dia1/Exercicios-GSS/recursos/README.md) identifies PyTorch/Ultralytics sources and separates synthetic images and recorded outputs | Photograph ownership and every upstream redistribution permission were not independently established |
| Starter adaptation | [Selection record](starter-reference-selection.md) and [starter attribution](../starter/README.md#attribution-and-adaptation) credit course concepts and explain changes | No standalone publication, endorsement or native Copilot behavior is implied |
| Digit Lab | [Implementation attribution](../../dia2-local/README.md#attribution) credits course requirements, MNIST, EMNIST and external TrOCR | Trained CNNs and optional pretrained readers remain separate deliverables |
| DdddOCR | [Retained MIT notice](../../dia2-local/dist/assets/ddddocr-LICENSE.txt) includes source revision; [model provenance](../../dia2-local/docs/captcha-readers.md#model-provenance-and-browser-contract) identifies hashes and character-table provenance | The upstream notice literally contains a copyright-holder placeholder; it is preserved as supplied, not silently filled with an invented owner |
| Optional runtime/word/arcade dependencies | [Words](../../dia2-local/docs/words.md), [CAPTCHA readers](../../dia2-local/docs/captcha-readers.md) and [arcade documentation](../../dia2-local/docs/snes-arcade.md) identify external downloads and the separate ROM | This audit does not establish redistribution rights for optional ROMs, externally downloaded weights, supplied logo or mascot images |

The root license's “unless otherwise indicated” boundary remains relevant to
third-party resources. The audit does not replace retained third-party notices
with the course license. Unresolved ownership and distribution questions stay
recorded for review before any new redistribution; no asset was newly deployed,
relicensed, or added from an external source in this batch.

## Remaining untracked files

All five files left after the previous commit were reviewed individually:

| File under `dia2-local/` | Decision and evidence |
| --- | --- |
| `65474617.jpg` | Exact SHA-256 duplicate of tracked `dist/assets/65474617.jpg`; retain locally and ignore this duplicate path |
| `scopedog-asset.jpg` | Exact duplicate of tracked `dist/assets/scopedog.jpg`; retain locally and ignore this duplicate path |
| `reports/ensemble-v1-post-publication-challenge-verification-raw.json` | Preserve in Git unchanged: exact hash matches its tracked comparison and all ten recorded inputs/scores match the captcha-v2 baseline |
| `reports/release-3.7.0-public-challenge-recheck-20261016-raw.json` | Preserve in Git unchanged: exact hash matches the paired recheck and all ten recorded inputs/scores match the captcha-v3 baseline |
| `reports/release-3.7.0-public-challenge-recheck-20261016.json` | Preserve the paired historical comparison unchanged: 10/10, expressly a follow-up; its raw hash and case results agree |

The ensemble verification records 9/10 for the retained v3.6.0 baseline; its name
does not mean a different ensemble was deployed. The captcha-v3 recheck records
10/10. Neither is a new evaluation in this batch. No local file was deleted and
no image was classified; hashing and comparison of existing records are distinct
from inference. Exact hashes and dimensions are in the machine inventory.
