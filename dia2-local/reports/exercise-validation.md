# Day 2 exercise validation

Audit date: 2026-10-16. Scope: Exercise 3, including its final Desafio.

**Verdict: the technical implementation and local challenge evaluation pass;
the complete course deliverable is not yet demonstrated.** The exercise says
10/10 challenge accuracy is desirable, not mandatory. A recorded 2/10 result
does not itself mean the exercise failed.

## Requirement matrix

| Requirement | Status | Evidence |
| --- | --- | --- |
| Actual MNIST training, disjoint validation and held-out evaluation | PASS | [Original training](training.json), [original test](mnist-test.json), [updated experiment](robust-digits.json); 99.28% original / 99.32% updated MNIST accuracy |
| Automated behavior and data checks | PASS | Fresh `python -m unittest discover -s tests -v`: 11/11 passed |
| Browser inference, drawing, uploads, real activations and runtime parity | PASS | Fresh [public digit checks](exercise-audit-public-digits.json): 9/9 groups; [local updated-model checks](robust-browser-qa.json): activation parity and 36 digit/letter uploads |
| Ten official PNGs classified with raw scores and separate comparison | PASS locally | [Original predictions](challenge-raw.json), [comparison and error analysis](validation.md); [follow-up predictions](robust-challenge-raw.json) and [comparison](robust-challenge-comparison.json); both 2/10 |
| Preserve initial evaluation and identify subsequent iterations | PASS for recorded artifacts | Verified original freeze/raw/comparison hashes, frozen archive, original weights and all ten image hashes; verified follow-up frozen sources and record hashes. Follow-up explicitly records that it is not blind |
| Working public application | PASS | Fresh nine-group browser verification at `https://naoquerosaber.pt/AI/`; public release uses original digit weights |
| GitHub Pages hosting | NOT MET by current hosting | [Hosting guide](../docs/hosting.md) describes FTPS hosting, not GitHub Pages |
| Ten official challenge uploads on the published site | NOT EVIDENCED | Both recorded challenge runs target localhost. Public QA uses MNIST/synthetic fixtures, not the ten official CAPTCHA files |
| Approved GitHub Issues before implementation | NOT EVIDENCED | [Experiment plan](../docs/experiment.md) explicitly substitutes local tasks for published Issues; `git remote -v` returned no configured remote |
| Final committed and traceable submitted release | INCOMPLETE | Existing local commits are present, but the robustness release is uncommitted; no GitHub submission URL or approved Issue trail was found |

## Interpretation and remaining work

The implementation satisfies the documented local scope. Earlier local-only
decisions explain some deviations, but do not prove compliance with the
published exercise's GitHub Issues and GitHub Pages requirements. Obtain the
instructor's acceptance of those substitutions, or complete the required
publication and delivery steps.

For strict course completion, provide the participant's GitHub repository and
Issue history, commit the final reviewed release, publish it on GitHub Pages,
and record all ten official image uploads on that published release with URL,
commit and weight identity. Any further challenge run must be identified as a
follow-up after prior answer inspection; it cannot replace the original blind
record. Missing pre-implementation approvals cannot be established retroactively.

At the time of the initial audit, the robustness models had not been deployed. The
official challenge contains digits only; letter recognition is an extension.
Teacher feedback belongs to Exercise 4 and is not claimed by this audit.

This audit did not train, tune, deploy, create Issues or rerun the challenge.

## Subsequent authorized deployment

After this audit, the user requested deployment and a commit. Both robustness
models and the updated app were uploaded to the existing HTTPS website. All
22 assets passed FTPS download/hash verification, and the
[public robustness browser checks](public-robust-browser-qa.json) passed.
The deployment preserves the original model exports and evaluation records.
The source and evidence are included in the release commit containing this
update. GitHub Issues, GitHub Pages and the published-site ten-image challenge
evaluation remain outstanding requirements of the original course exercise.
