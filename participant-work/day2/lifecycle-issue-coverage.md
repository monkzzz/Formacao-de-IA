# R05: full classifier lifecycle and personal Issues

Mapped 2026-10-17 from current public personal Issue bodies captured in
[reference/Issue snapshot](reference-github-review.json), the course requirements
and actual submission evidence. [Published status updates](issue-sync-result.json)
record the later writes and returned Issue states. No original planning chronology
is reconstructed: the classifier predates these evidence Issues.

| Required phase | Personal Issue owner | Acceptance/evidence mapping |
| --- | --- | --- |
| MNIST preparation and IDX contract | [#2](https://github.com/monkzzz/Formacao-de-IA/issues/2), tested under [#4](https://github.com/monkzzz/Formacao-de-IA/issues/4) | Loader checksums/headers/labels, disjoint seeded split, dataset identity in the evidence index and clean preflight |
| Architecture and approved technical plan | [#2](https://github.com/monkzzz/Formacao-de-IA/issues/2), process gap under [#7](https://github.com/monkzzz/Formacao-de-IA/issues/7) | Retrospective alternatives/specification and model identity exist. Current participant technical review R06 and original instructor-acceptance gap remain separate; no new architecture work is authorized |
| Training/configuration/model selection | [#2](https://github.com/monkzzz/Formacao-de-IA/issues/2), reproduction under [#3](https://github.com/monkzzz/Formacao-de-IA/issues/3) | Twelve-epoch history, seeds, split, frozen selection and baseline identity; no new training run |
| Unit, held-out evaluation and error analysis | [#4](https://github.com/monkzzz/Formacao-de-IA/issues/4) and [#2](https://github.com/monkzzz/Formacao-de-IA/issues/2) | Actual 30-test record, confusion/errors, selected-model re-evaluation in original and clean environments |
| Export and artifact restoration | [#3](https://github.com/monkzzz/Formacao-de-IA/issues/3), parity under [#4](https://github.com/monkzzz/Formacao-de-IA/issues/4) | Manifest/tensor layout, browser weights verified from HTTPS, exact checkpoint/export tensor comparison; public checkpoint/font portability remains limited |
| Drawing and local single/batch upload | [#4](https://github.com/monkzzz/Formacao-de-IA/issues/4), origin under [#5](https://github.com/monkzzz/Formacao-de-IA/issues/5) | Existing public UI behavior, per-image scores, clear/reset, emulated touch, error/retry and export evidence |
| Real network visualization and runtime parity | [#4](https://github.com/monkzzz/Formacao-de-IA/issues/4) | Python/JS prepared pixels, logits and hidden/feature activations; selected model identity, no remote classification API |
| Publication and submitted origin | [#5](https://github.com/monkzzz/Formacao-de-IA/issues/5) | Existing v3.10.0 host retained; source-only repository publication is separate from site deployment. Pages/instructor substitution remains pending |
| Ten-image challenge and traceability | [#6](https://github.com/monkzzz/Formacao-de-IA/issues/6) | Preserved freeze, raw scores, separate labels, input/runtime hashes and public follow-up; no new official-image inference |
| Deviations and teacher feedback | [#7](https://github.com/monkzzz/Formacao-de-IA/issues/7), new feedback Issues only after real findings | Prepared unsent request/packet; actual teacher observations, acceptance and corrections remain unknown |

The earlier six Issues focused on submission evidence, leaving lifecycle ownership
implicit. Their status updates now link this explicit matrix and the corresponding
artifacts. No fixed Issue count is required; additional Issues would be useful for
new uncovered work, not for presenting already completed implementation as newly
planned work. Issue #1 concerns a closed agent-configuration change and is untouched.

The update operation keeps existing scope and appends a dated evidence/status
section. #2 remains open with original process/evidence acceptance limits; #3 remains open for
portable checkpoint/host limitations; #5 and #7 retain instructor dependencies.
#4 and #6 can close against their actually satisfied verification/preservation
criteria, without claiming classroom feedback or instructor approval. The receipt
is authoritative for whether each update/closure actually succeeded.
