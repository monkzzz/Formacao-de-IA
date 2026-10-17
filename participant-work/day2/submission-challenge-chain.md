# Preserved classifier challenge chain

Indexed 2026-10-17 for [Issue #6](https://github.com/monkzzz/Formacao-de-IA/issues/6).
The submitted application is v3.10.0 on the
[existing public origin](https://naoquerosaber.pt/AI/). Its default remains the
participant-trained captcha-v3 residual CNN introduced in v3.7.0. The optional
pretrained CAPTCHA Digits configuration has separate results and is not this chain.

## Selected evidence

| Stage | Preserved evidence | Meaning |
| --- | --- | --- |
| Development choice | [Selection](../../dia2-local/reports/captcha-v3-development-selection.json) and [training protocol](../../dia2-local/docs/residual-training.md) | Recorded selection before the synthetic test; no new training |
| Runtime/weights freeze | [Freeze](../../dia2-local/reports/captcha-v3-challenge-freeze.json) | Source and weight SHA-256, timestamp, explicit follow-up scope and no further tuning |
| Raw local predictions | [Unmodified raw export](../../dia2-local/reports/captcha-v3-challenge-raw.json) | Ten files, file hashes, prepared inputs, ten scores/logits per image, model identity; saved before the separate comparison |
| Label comparison | [Comparison](../../dia2-local/reports/captcha-v3-challenge-comparison.json) | References the exact raw SHA-256; ten correct out of ten |
| Public raw export | [Unmodified public export](../../dia2-local/reports/release-3.7.0-public-challenge-verification-raw.json) | Separate public-origin follow-up, not a new independent test |
| Public comparison | [Public verification](../../dia2-local/reports/release-3.7.0-public-challenge-verification.json) | References its raw SHA-256; all prepared inputs, scores and predictions agree with frozen local results |
| Current integrity | [Fresh byte/record checks](submission-challenge-integrity.json) and [checker](verify-challenge-chain.py) | Verified both raw hashes, official file hashes, ten input/score comparisons and unchanged listed CNN runtime/weights without running inference |
| Current public behavior | [v3.10.0 public browser record](submission-browser-delivery.md) | Selected model and non-challenge UI/parity checks; no fresh official-image accuracy measurement |

The two raw exports were previously untracked. They are included byte-for-byte
because their hashes match the already committed comparison records. They contain
prediction provenance, pixels and scores, not executable code or credentials.
Other pre-existing untracked files remain untouched and require their own review.

The [original first-run freeze](../../dia2-local/reports/challenge-freeze.json),
[original raw export](../../dia2-local/reports/challenge-raw.json) and
[original comparison](../../dia2-local/reports/challenge-comparison.json) remain
preserved. The fresh integrity check also verified the ignored original
`artifacts/frozen-app.zip` and original weights against their recorded SHA-256.
Ignored archives/checkpoints require separate preservation; their presence on
this machine does not establish an off-machine backup.

## Distinct results and limitations

| Evaluation | Selected captcha-v3 result | Scope |
| --- | --- | --- |
| Official MNIST test | 9,910 / 10,000, **99.10%** | Clean digit images; historical evaluation |
| Raw synthetic robustness test | 19,746 / 20,000, **98.73%** | Independent synthetic renderer/font split for that experiment; not real CAPTCHA population data |
| Official ten-image challenge | 10 / 10 | Known follow-up after prior exposure; public verification agrees |
| Original first-run baseline | 99.28% MNIST; 2 / 10 challenge | Different original model; eight errors remain documented |

The selected follow-up has no incorrect predictions in these ten cases. This
does not resolve ambiguity in heavily occluded digits, establish calibrated
scores or predict general CAPTCHA accuracy. The original eight errors and their
analysis remain in the [original validation](../../dia2-local/reports/validation.md).
A perfect challenge score is not a course-completion requirement. Softmax outputs
are model scores, not calibrated correctness probabilities.

All later challenge evaluations are follow-ups. Never use official pixels,
answers, filenames, generator labels or completed test caches to train, select
models or tune preprocessing. This batch only hashes files and compares existing
records. It neither uploads official inputs nor runs training or inference on them.

No new Pages origin or changed default CNN needs challenge verification in this
batch: the site is preserved at the participant's request. The entry page and app
module changed between v3.7.0 and v3.10.0; the integrity report identifies the
specific unchanged inference/preprocessing/residual files and weights. Do not
describe the full UI as the original frozen runtime. If a future origin or CNN
changes, record separate deployment verification against these frozen results
after prior challenge exposure; never overwrite them. The conditional checklist
item remains pending for that future event. Instructor review remains unperformed.
