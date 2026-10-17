# Participant submission and handover

Prepared 2026-10-17 in the personal fork. This is delivery of the local work to
the participant for review. It has **not been sent to a teacher** and does not
establish classroom attendance, mastery or instructor acceptance.

The subsequent [exercise coverage audit](EXERCISE-COVERAGE.md) identified twelve
missing or understated follow-ups, now unchecked in [TASKS.md](TASKS.md).
This index records delivery of existing artifacts; it does not establish full
exercise completion or that only teacher-dependent work remains.

## Day 1 research

The [research submission index](participant-work/day1/README.md) links all source
and process evidence. The principal deliverables are:

- [Research report](participant-work/day1/research-report.md) and [verification ledger](participant-work/day1/source-verification.md).
- [Transformer reading note](participant-work/day1/reading-transformer.md) and [FlashAttention reading note](participant-work/day1/reading-flashattention.md).
- [Original synthesis](participant-work/day1/synthesis-original.md), [preserved audit](participant-work/day1/synthesis-audit.md), [final revision](participant-work/day1/synthesis-final.md) and [correction summary](participant-work/day1/synthesis-corrections.md).

The original synthesis still matches its pre-audit hash. These are assistant-produced
participant-work artifacts with declared document-access and fresh-session limits;
the chosen assistant substitutes for Copilot by participant decision, pending
instructor acceptance.

## GSS demonstrations

The [consolidated twelve-lesson record](participant-work/day1/gss-language-final.md#consolidated-gss-delivery-and-reproduction)
links module 1 observations, vision/image-video checks and recorded language
demonstrations. [Environment/setup](participant-work/day1/gss-evidence/setup.json),
[module 1 execution](participant-work/day1/gss-evidence/execution.json),
[vision/language execution](participant-work/day1/gss-vision-language-evidence/execution.json)
and [final language/tests](participant-work/day1/gss-language-final-evidence/execution.json)
preserve what actually ran. The successful offline suite recorded **125 tests**;
failed sandbox attempts remain separate. This handover did not rerun that suite.
Live webcam capture, live LM Studio inference and human desktop interaction remain
outside the established evidence. UCI 8×8 digits remain distinct from Day 2 MNIST.

## Starter, skill and context

Deliver the [personal starter](participant-work/starter/README.md), including its
[bootstrap skill](participant-work/starter/.github/skills/bootstrap-project/SKILL.md),
[preservation context](participant-work/starter/context/project.md),
[decisions](participant-work/starter/context/decisions.md) and
[current handoff](participant-work/starter/context/handoff.md).
The [generic 1.0.0 archive](participant-work/day2/starter-generic-1.0.0.zip) and
[original identity manifest](participant-work/day2/starter-generic-1.0.0.json)
preserve reusable source before classifier-specific context.

[Fresh-session reuse](participant-work/day2/starter-fresh-session.md),
[bootstrap behavior](participant-work/day2/bootstrap-behavior.md) and
[recovery](participant-work/day2/bootstrap-recovery.md) record chosen-assistant
observations, including synthetic approval boundaries. The participant actually
confirmed preservation of the existing website; this is not original technical
design approval. Native Copilot discovery, standalone starter publication and
instructor acceptance remain unverified. The handoff is updated for observed
progress; no requirements or approval record is rewritten.

## Classifier, repository and commits

- Personal repository: [monkzzz/Formacao-de-IA](https://github.com/monkzzz/Formacao-de-IA).
- Real Issues: [#2 evidence](https://github.com/monkzzz/Formacao-de-IA/issues/2), [#3 artifacts](https://github.com/monkzzz/Formacao-de-IA/issues/3), [#4 verification](https://github.com/monkzzz/Formacao-de-IA/issues/4), [#5 hosting](https://github.com/monkzzz/Formacao-de-IA/issues/5), [#6 challenge](https://github.com/monkzzz/Formacao-de-IA/issues/6), [#7 process](https://github.com/monkzzz/Formacao-de-IA/issues/7). [Publication evidence](participant-work/day2/issue-register.md) is retrospective; no original approval is established.
- Existing application: [Digit Lab](https://naoquerosaber.pt/AI/), **v3.10.0**, default participant-trained **captcha-v3 residual CNN**. [Submission evidence index](participant-work/day2/submission-evidence-index.md), [artifact recovery](participant-work/day2/submission-artifacts.md), [fresh browser checks](participant-work/day2/submission-browser-delivery.md) and [preserved challenge chain](participant-work/day2/submission-challenge-chain.md) identify the actual deliverable.
- Selected digit weights SHA-256: `d962c7f1aefd4f86cf9fcc621e30a1e8fbbce092c5a47ab3dd88e0f64573b42c`.

Historical selected-model results are **99.10% clean MNIST**, **98.73% raw synthetic
robustness** and **10/10** in the known official challenge follow-up. They are
different evaluations; softmax scores are not calibrated correctness probabilities.
The original 99.28% MNIST and 2/10 challenge results remain preserved. No new
training, official challenge inference or deployment ran for this handover.

| Local delivery commit | Record |
| --- | --- |
| `809ef4d96e4e7f127b5e953ea733c714b59a7d39` ([URL pending push](https://github.com/monkzzz/Formacao-de-IA/commit/809ef4d96e4e7f127b5e953ea733c714b59a7d39)) | [CNN submission review](participant-work/day2/submission-review.md) |
| `4cd82621f0269134ffe46c301575ef703c1b9f96` ([URL pending push](https://github.com/monkzzz/Formacao-de-IA/commit/4cd82621f0269134ffe46c301575ef703c1b9f96)) | [Five browser submission tasks](participant-work/day2/submission-browser-delivery.md) |
| `da515d0f7d2d1b385e555a2b1a7f1089e26a7b15` ([URL pending push](https://github.com/monkzzz/Formacao-de-IA/commit/da515d0f7d2d1b385e555a2b1a7f1089e26a7b15)) | [Challenge/maintenance delivery](participant-work/day2/maintenance-next-ten.md) |
| This handover's containing commit | Resolve with `git log -1 --format=%H -- SUBMISSION.md` |

The read-only remote check returned `main` at
[preparation commit 1d8707c65666885861a2a90c7e39145f49c65f7b](https://github.com/monkzzz/Formacao-de-IA/commit/1d8707c65666885861a2a90c7e39145f49c65f7b).
The later delivery commits are local and were **not pushed in this batch**;
their files are delivered in this checkout. Their GitHub commit URLs must not be
represented as published evidence until a push and remote verification occur.
Ignored weights, checkpoints, original frozen archives and screenshots need
separate preservation; source delivery alone does not contain them.

## Review readiness and remaining dependencies

[Asset review](participant-work/day2/teaching-assets-review.md) and the
[handover validation](participant-work/day2/handover-validation.json) cover provenance,
links, exercise numbering, workflow paths and preservation. The actual checklist
is [TASKS.md](TASKS.md); completion does not mean every course requirement is met.

The [prepared feedback packet](participant-work/day2/teacher-feedback-packet.md)
contains review links and a blank actual-feedback record. It remains unsent.
Instructor acceptance of the chosen assistant, personal-fork layout, existing
hosting and missing original approvals is pending. Pages publication is deferred
to preserve the current site. No new origin exists to trigger another challenge
verification. These are external or conditional dependencies, not completed work.
