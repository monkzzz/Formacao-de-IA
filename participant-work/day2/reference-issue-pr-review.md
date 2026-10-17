# Reference Issue and Pull Request review

Read 2026-10-17 through GitHub REST. [Captured public evidence](reference-github-review.json)
contains the returned bodies, file patches, comments/reviews and check results.
The first web-reader attempts in the coverage audit failed; this later REST
retrieval succeeded. Nothing was posted to the reference repository.

## R03: planning Issue

[Reference Issue #1](https://github.com/vcanonici/Formacao-de-IA/issues/1)
separates a specification from implementation. Its dependencies are an existing
starter, participant-authored bootstrap context, repository/Git inspection and
accessible IDX data. It blocks implementation until an actual design review.
Its scope covers data contracts, at least two architecture alternatives,
training/validation/test separation, measurable acceptance, export/browser parity,
real network visualization and distinct facts/assumptions/approved decisions.

The eight named acceptance checks cover context, data, integrity, alternatives,
verifiability, publication requirements, traceability and the specification-only
scope. Evidence should be a versioned document, linked commit, human review,
dependency check and a fresh-session explanation of the next actionable Issue.
Adopt that bounded structure and evidence-based completion criteria in the
personal repository, rather than copying its architecture or pretending that
retrospective Issues existed before the already implemented classifier.

Two historical statements must **not** be copied: the Issue says nine challenge
images and says filenames reveal labels. The current local course challenge has
ten neutral `caso_XX.png` names. Use the [current challenge instructions](../../Dia2/Desafio/README.md)
and preserve the pixel-only inference boundary. Record stale reference wording
as a finding, not as permission to use labels or the generator during inference.

## R04: PR Conversation, Files changed and Checks

[Reference PR #2](https://github.com/vcanonici/Formacao-de-IA/pull/2)
was **open and unmerged** at retrieval, head
`e769d55758e8e68c2f6aa472865727731855d84c`, base
`4d128cf017b03f15acfed9d12f3c255fd5d0bc1b`.
Its body explains the problem, four-file scope, runnable commands, acceptance,
actual tests, omitted features and questions for reviewers. Conversation comments,
submitted reviews and inline review comments were all empty. No human review or
approval can be inferred from a well-written description.

| Changed file | Reviewed responsibility and boundary |
| --- | --- |
| `mnist_centroid.py` | Streams paired IDX/gzip records, validates headers/counts/pixels/labels, averages training pixels per class, predicts nearest centroid from pixels only, reports actual evaluated count and accuracy |
| `test_mnist_centroid.py` | Six synthetic tests cover IDX/limits, pixel-dependent prediction, empty training, invalid magic, mismatched counts and CLI integration; they do not measure real full-MNIST accuracy |
| Example README | Reproduction commands and explicit baseline limitations; a 200-image smoke result must not be described as a 10,000-image test |
| `exemplo-classificador-python.yml` | Path-scoped PR job, Python 3.12 and stdlib unittest, read-only content permission |

The head's `test` check was completed with conclusion **success**:
[captured check run](https://github.com/vcanonici/Formacao-de-IA/actions/runs/38545268176/job/115789638371).
The separate commit-status API returned `pending` with no equivalent success
claim; Checks and legacy commit statuses are distinct response channels.
This review did not rerun third-party tests. The PR's reported local test result
and the actually observed remote check remain separate evidence.

The code is nearest-centroid classification, not a neural network, gradient
training, a web export or a published browser app. It does not close the
reference design Issue. Adopt small diffs, executable verification, clear subset
counts, input/label separation and explicit unrun checks. Do not substitute this
baseline for the participant-trained CNN or merge the teaching PR.

Attribution: course reference by Vinicius Canonici and Hugo Gomes, under the
[course license](../../LICENSE.md). The snapshot preserves source attribution;
the participant implementation remains independent. Read-only review does not
establish original pre-implementation chronology or teacher acceptance.
