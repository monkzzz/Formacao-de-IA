# GSS completion: attention, generation, prompts and image/text

Executed 2026-10-17. This record covers the remaining four module 2 lessons,
the offline suite and the consolidated execution record. Sources:
[setup guide](../../Dia1/Exercicios-GSS/README.md),
[module 2 index](../../Dia1/Exercicios-GSS/modulo2/README.md),
[resource attribution](../../Dia1/Exercicios-GSS/recursos/README.md) and the
unchanged [provenance manifest](../../Dia1/Exercicios-GSS/origem.json).

## Environment and method

Used the prepared GSS Python environment. The [execution JSON](gss-language-final-evidence/execution.json)
records its interpreter, packages, platform, backend, input/entry/recording hashes,
actions and results. All four unchanged entry scripts exited zero using `Agg`,
`FORMACAO_ML_NO_PAUSE=1` and `FORMACAO_LMSTUDIO_OFFLINE=1`.

The [recorder](run-gss-language-final.py) then instantiated real Tk-backed lesson
interfaces, invoked controls, dispatched a matrix click, polled the image/text
worker and exported 22 figures for assistant visual review. These are figure
renderings, not desktop screenshots. Checks establish the observed interface states
and scripted interactions; human mouse/keyboard testing, physical window visibility,
all control combinations and animation smoothness are not established. Some long
image/text headings and footers clip at the exported figure width; full strings
remain in JSON. This run does not certify layout robustness across display sizes.

Attention uses hand-authored teaching weights. Generation, prompts and image/text
use the unchanged model recordings, explicitly marked as recorded in the interfaces.
No live LM Studio, new model output, training or fine-tuning is claimed. Recorded
`seconds` fields describe the original recording, not this replay's latency.
Course examples remain in their original Portuguese; this participant record is English.

## Exercise 03: attention and causal masking

Opened the full matrix and compared [causal](gss-language-final-evidence/03-causal.png)
with [bidirectional](gss-language-final-evidence/03-bidirectional.png) attention.
Both 13-by-13 matrices have rows summing to one. The causal matrix has no nonzero
weights above the diagonal. For query index 9 (`a`), the teaching weight on `peça`
is .52 with masking; unmasking allocates .15 total to future tokens, including .10
to `caixa`, and rescales prior weights by .85.

Clicked matrix row 1, checked the selected query changed, navigated previous/next,
and reset to query 9 with masking enabled. The GUI's simple wording says past-only;
the measured implementation includes the current token on the diagonal. These
weights illustrate context mixing and causal information restrictions; they were
not measured from a trained model and do not prove a causal explanation of meaning.

## Exercise 04: next-token generation

Compared temperature .1, 1 and 2, plus top-p .5, on the same initial recorded step.
The first candidate's original model probability was .298801. After normalization
over the ten displayed candidates, the selection probability was approximately
.591, .320 and .226 as temperature increased. At temperature 1/top-p .5 only two
candidates remained, with selection probabilities .510/.490. See the
[distribution view](gss-language-final-evidence/04-sampling-settings.png) and exact arrays in JSON.

This demonstration samples only the displayed candidate list. The remaining model
vocabulary mass is displayed separately and excluded from selection. It therefore
does not reproduce unrestricted full-vocabulary sampling. Top-p here is applied
after temperature scaling within that listed set; apparent differences from the
original model probabilities are expected.

Ran three greedy steps, undo, seeded sampling, restart and context switching for
all three prepared starting sentences. Resetting repeated the seeded sampled
choice. The greedy first-context run eventually reached the end token after eight
new tokens. The unavailable recorded branch was rolled back with an explicit
message rather than fabricating a continuation. See examples for
[context 0](gss-language-final-evidence/04-context-0.png),
[context 1](gss-language-final-evidence/04-context-1.png) and
[context 2](gss-language-final-evidence/04-context-2.png).

Higher probability is not factual correctness. Altering sampling settings changes
selection from fixed outputs; it does not retrain the model.

## Exercise 05: prompt comparison

Compared seven recorded configurations, preserving exact prompts, references,
outputs, token limits and finish reasons in JSON.

| Configuration | Observed recorded output and interpretation |
| --- | --- |
| Ambiguous classification, no examples/rule, temperature 0 | Three `Manutenção` answers; the reference explicitly says a priority criterion is missing |
| Add physical-damage priority rule only | Still three `Manutenção` answers, disagreeing with the `Qualidade` reference; the rule alone did not fix this sample |
| Rule plus three examples | `Qualidade`, consistent with the stated priority rule |
| Same examples/rule, temperature .7 | Three `Qualidade` answers; this finite replay does not establish general reliability or a temperature effect |
| Summarize at 120-token limit | One sentence retained line 2, sensor failure, 10h15 stop and 10h35 restart after replacement |
| Extract at 120-token limit | Returned line 2, both times and 20 minutes; the stop-time field was awkwardly labelled `Linha de Paragem` |
| Extract at eight-token limit | Output ended after the line number and a bullet; finish reason was `length`, demonstrating truncation rather than task completion |

Inspected the [baseline](gss-language-final-evidence/05-classification-baseline.png),
[rule-only](gss-language-final-evidence/05-classification-rule.png),
[examples](gss-language-final-evidence/05-classification-examples.png),
[temperature](gss-language-final-evidence/05-classification-temperature.png),
[summary](gss-language-final-evidence/05-summary.png),
[extraction](gss-language-final-evidence/05-extraction.png) and
[truncation](gss-language-final-evidence/05-extraction-short.png) figures. Clearing
removed the answers. These are prompt-conditioned observations, not evidence that
weights changed or that the prompt improvement generalizes to an unseen dataset.

## Exercise 06: image/text outputs and limits

Ran description, question and limitations requests for all three available images:
the part schematic, synthetic downtime chart and generated part photograph.
All nine responses were recorded. The worker completed and image/request cycling
updated the displayed input. Inputs and answers are linked by hashes in JSON.

The [chart question](gss-language-final-evidence/06-grafico-1.png) answered line 2
and about 20 minutes, matching the synthetic values 5/20/8. The
[chart limits](gss-language-final-evidence/06-grafico-2.png) correctly avoided
inferring causes, aggregation period or stop frequency. These values describe
fictitious data, not an observed factory.

The [schematic question](gss-language-final-evidence/06-peca-1.png) identified the
visible crack between two holes; the [limits response](gss-language-final-evidence/06-peca-2.png)
did not claim a known material, physical dimensions or crack cause.
The [generated-photo description](gss-language-final-evidence/06-foto-0.png)
used ambiguous wording about two holes at each end, while the displayed image has
two holes total. This is a useful counting/wording limitation, not a validated
description. The [photo limits](gss-language-final-evidence/06-foto-2.png) withheld
the exact alloy, cause and intended application. The photograph is synthetic and
does not document a real damaged part. No diagnosis or physical safety conclusion
follows from these responses.

## Offline tests and failed attempts

An initial shell launch misquoted the backend value, hit the default Matplotlib
cache restriction and was interrupted. Its [diagnostic log](gss-language-final-evidence/initial-shell-attempt.txt)
is preserved with UTF-8 encoding and normalized line endings/trailing whitespace;
it is not a completed test result.

The recorder then ran the full documented offline suite with `Agg`, explicit offline
mode and a writable Matplotlib cache. It ran 125 tests with two errors, both due
to denied writes/cleanup in Windows system temporary directories. The
[failed-suite log](gss-language-final-evidence/offline-suite-restricted-temp-failure.txt)
and original exit code remain in `suite_attempts` in JSON.

A second run kept the same suite and assertions, setting `TEMP` and `TMP` to
ignored `.cache/test-temp` inside the GSS workspace. It still ran 125 tests with
the same two temporary-directory permission errors; see its
[separate failure log](gss-language-final-evidence/offline-suite-failed-attempt-2.txt).
Moving the parent directory alone did not resolve the sandbox restriction.

The next retry used reviewed execution outside the restricted sandbox, keeping
the workspace temporary directory, source, tests and installed dependencies
unchanged. The [final suite log](gss-language-final-evidence/offline-suite.txt)
and JSON record the actual retry result and execution context: **125 tests passed
in 125.075 seconds**, exit code zero. The lesson walkthrough is preserved;
`--suite-only` reruns only the environment-sensitive suite.

## Consolidated GSS delivery and reproduction

All twelve lesson entry scripts have now been executed across three batches:
[module 1 exercises 01–05](gss-observations.md),
[vision/tokens/embeddings](gss-vision-language.md), and this record. Their logs,
environment identities, GUI evidence and limitations remain separate. Earlier
module 1 execution used the documented reused environment while base installation
completed; later batches used the GSS environment. No claim of identical package
sets or human classroom participation is made.

The original entry files, recordings, resources and `origem.json` remain unchanged.
Their attribution remains with the course authors and applicable third parties.
UCI digits remain separate from Day 2 MNIST, and no reserved CAPTCHA input or
existing classifier artifact was used or modified in this batch.

From the root, after base setup:

```powershell
rtk proxy Dia1/Exercicios-GSS/.venv/Scripts/python.exe participant-work/day1/run-gss-language-final.py
```

The recorder sets offline mode, prepares local cache/temp paths and overwrites only
its evidence outputs. Copy the evidence elsewhere first to preserve this run.
For a suite-only retry after a saved walkthrough, append `--suite-only`.
The [batch validation](../ten-task-validation.json) checks evidence, hashes,
checklist ordering, documentation links, starter structure and Python syntax.
Validation passed for exactly the next ten tasks, 202 local links, 32 heading
anchors, all recorded source/input hashes and 22 nonblank figure exports. The
assistant visually reviewed all 22 exports using six contact sheets and inspected
selected figures at full size. `rtk git diff --check` passed. Human desktop testing,
live LM Studio, live webcam capture and participant mastery remain outside the
established evidence.
