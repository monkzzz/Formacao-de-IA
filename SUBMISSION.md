# Participant submission and handover

**Day 2 clarification — participant-trained models only:** the professor excludes downloaded pretrained models. The separate [submission package and run instructions](dia2-local/docs/self-trained-submission.md) now include only our trained CNNs, with MNIST-only as the course default and supplementary extensions labelled separately. [Provenance and validation](dia2-local/reports/self-trained-submission-v1-validation.json) passed: 71 unit tests, four-model browser parity and 40 uploads. The existing published sites remain unchanged and contain historical pretrained experiments; they are not this restricted package. The CAPTCHA confidence target remains unmet.

Prepared 2026-10-17 in the personal fork. This is delivery of the local work to
the participant for review. It has **not been sent to a teacher** and does not
establish classroom attendance, mastery or instructor acceptance.

Pages update, 2026-10-17: [Digit Lab on GitHub Pages](https://monkzzz.github.io/Formacao-de-IA/)
is now published and verified. See the [deployment and browser evidence](participant-work/day2/pages-publication.md).
This supersedes the earlier deferred-Pages status below. The original external
site and tracked `dia2-local` development remain intact; instructor/process review
is still pending. The new-origin checks use hashes and non-challenge parity;
no official-image rerun or new challenge accuracy is claimed.

The subsequent [exercise coverage audit](EXERCISE-COVERAGE.md) identified twelve
missing or understated follow-ups. Eleven are now completed with
[follow-up evidence](participant-work/day2/independent-task-completion.md);
R01 still requires the participant's actual research critique in [TASKS.md](TASKS.md).
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

| Published delivery commit | Record |
| --- | --- |
| `809ef4d96e4e7f127b5e953ea733c714b59a7d39` ([published commit](https://github.com/monkzzz/Formacao-de-IA/commit/809ef4d96e4e7f127b5e953ea733c714b59a7d39)) | [CNN submission review](participant-work/day2/submission-review.md) |
| `4cd82621f0269134ffe46c301575ef703c1b9f96` ([published commit](https://github.com/monkzzz/Formacao-de-IA/commit/4cd82621f0269134ffe46c301575ef703c1b9f96)) | [Five browser submission tasks](participant-work/day2/submission-browser-delivery.md) |
| `da515d0f7d2d1b385e555a2b1a7f1089e26a7b15` ([published commit](https://github.com/monkzzz/Formacao-de-IA/commit/da515d0f7d2d1b385e555a2b1a7f1089e26a7b15)) | [Challenge/maintenance delivery](participant-work/day2/maintenance-next-ten.md) |
| This handover's containing commit | Resolve with `git log -1 --format=%H -- SUBMISSION.md` |

The earlier read-only remote check returned `main` at
[preparation commit 1d8707c65666885861a2a90c7e39145f49c65f7b](https://github.com/monkzzz/Formacao-de-IA/commit/1d8707c65666885861a2a90c7e39145f49c65f7b).
That was the original handover state. The subsequent source-only push published
these commits through
[9e7eb08](https://github.com/monkzzz/Formacao-de-IA/commit/9e7eb08bc9187f703c1e7c7a9ed2f6cbb42f99cf).
[Remote verification](participant-work/day2/source-publication-verification.json)
confirmed the main ref, commit/tree identities and fourteen required source/evidence
paths. [Actual Issue updates](participant-work/day2/issue-sync-result.json) closed
#4 verification and #6 challenge preservation; #2, #3, #5 and #7 remain open with
their unresolved acceptance limits. The receipt/checklist commit follows that
published evidence commit. No production site or hosting configuration changed.
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
missing original approvals is pending. Pages publication now satisfies the hosting
target while preserving the current site. New-origin integrity and non-challenge
parity checks passed; the optional official-image rerun was not performed. Actual
teacher delivery and feedback remain external dependencies.
