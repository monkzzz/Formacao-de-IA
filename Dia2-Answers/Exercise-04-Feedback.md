# Exercise 4 — Feedback and Corrections

Original: [Exercise 4](../Dia2/Exercicio-04-Roda-de-Feedback.md).

## What should be presented?

Provide the personal repository, public application URL, approved Issues, trained model identity, MNIST evaluation, and the original ten CAPTCHA predictions. Explain what works and what remains unfinished. The teacher must test the application directly; a written answer cannot replace that activity.

## What should the teacher and classmates check?

Verify drawing, clearing, uploads, previews, per-image scores, real activations, model loading, and local inference. Try inputs beyond the prepared demonstration. Confirm that reported MNIST results are separate from CAPTCHA results and that the site uses the participant's trained weights.

## How should feedback become actionable work?

Separate observations from causes. For example, “uploading a transparent PNG produces an empty input preview” is an observation; “alpha handling is incorrect” is a hypothesis until investigated.

Create or update Issues with reproduction steps, expected and actual behavior, relevant version, evidence, and acceptance criteria. Prioritize broken inference, model loading, drawing/upload handling, and publication before cosmetic improvements.

For each selected correction, investigate the cause, implement a focused change, run relevant regression and functional checks, review the diff, and record the commit and before/after evidence. Keep unresolved items open with a clear next action.

## How should evaluation integrity be preserved?

Retain the initial challenge predictions and the version that produced them. Any model or preprocessing changes after inspecting those results belong to a new iteration. Report later improvements separately; they are not a new independent first evaluation.

## Feedback record to complete after the session

| Field | Current value |
| --- | --- |
| Session date and reviewer | Pending real session |
| Public URL and tested version | Not available |
| What the teacher actually tested | Not recorded |
| Observations and evidence | Not recorded |
| Questions and explanations discussed | Not recorded |
| Issues created or updated | Not created |
| Corrections and related commits | Not implemented |
| Before/after validation | Not run |
| Remaining limitations and next actions | To be identified during testing |

## What should improve in the starter?

Record transferable lessons, such as a missing parity check or an undocumented deployment path, in the starter's procedures or knowledge records. Keep classifier-specific details in project context. Do not turn an untested explanation into a permanent rule.

**Practical work remaining:** participate in the real feedback session, record observations, investigate selected Issues, and verify corrections. No teacher feedback or successful correction is claimed here.
