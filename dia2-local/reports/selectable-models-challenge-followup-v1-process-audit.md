# Official evaluation process audit

The participant reports that the professor finds the number of correct answers and scores unacceptable. This audit investigates the recorded outputs; it does not train, tune or repeat the browser challenge.

## Finding

No counting, model-selection or browser/Python inference mismatch was found in the preserved thirty predictions. Original input hashes match, each selected model has its frozen weight identity, and independently reconstructed Python models reproduce the browser classes. Python preprocessing reproduces all recorded inputs exactly; the largest score difference is below 0.00000028. See [measured checks](selectable-models-challenge-followup-v1-process-audit.json).

That establishes implementation consistency, not that the preprocessing is suitable. The [original images and actual model inputs](screenshots/selectable-models-challenge-followup-v1-inputs-audit.png) show substantial detail reduction at 28px. Background marks and crossing lines remain in the crop and influence its scale/centering. These are plausible contributors to recognition difficulty, not a demonstrated causal explanation of any individual error. The 64px residual model also differs in architecture and training, so its better results cannot be attributed to input resolution alone.

The supplementary experiment added 235,000 clean EMNIST handwriting examples and 12,000 generated CAPTCHA-style examples per epoch. This is primarily a handwriting extension, not training on a large representative real CAPTCHA collection. Its clean-digit improvement does not establish adequate CAPTCHA robustness. None of the models met the all-ten correct-with-score-at-least-90 target; the residual model already gets all ten classes right, so its remaining gap is the score criterion.

## Implication

The results should not be repaired by changing the answer comparison or increasing displayed scores. Future improvement must address the learned recognition pipeline, including input preparation and representative training data. Use an independent development set to isolate preprocessing effects and compare training/model changes; preserve these known official outcomes and do not use them to choose another transformation or checkpoint. A more confident output is useful only if independent correctness and confident-error measurements support it.

The completed follow-up is local, after prior exposure, and not a fresh blind population estimate or a completed published GitHub Pages submission. Those process limitations do not explain the recorded wrong class predictions. No model, application, score or default was changed during this audit.
