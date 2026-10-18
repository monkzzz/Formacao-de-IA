# CAPTCHA rerun in the participant-trained submission

Explicit user-requested official rerun in the frozen participant-trained package; historical exposure, no training, tuning or selection.

Preserved residual CNN: **10/10 correct**, **6/10 correct with original score strictly >90%**. Professor criterion met: **False**.

| File | Expected | Predicted | Original top score | Correct and >90% |
| --- | ---: | ---: | ---: | --- |
| caso_01.png | 8 | 8 | 99.26% | True |
| caso_02.png | 3 | 3 | 95.31% | True |
| caso_03.png | 0 | 0 | 99.76% | True |
| caso_04.png | 6 | 6 | 72.22% | False |
| caso_05.png | 1 | 1 | 58.14% | False |
| caso_06.png | 9 | 9 | 99.76% | True |
| caso_07.png | 4 | 4 | 76.93% | False |
| caso_08.png | 2 | 2 | 95.37% | True |
| caso_09.png | 7 | 7 | 98.50% | True |
| caso_10.png | 5 | 5 | 55.56% | False |

[Freeze](self-trained-submission-v1-challenge-rerun-v1-freeze.json) · [Raw browser output](self-trained-submission-v1-challenge-rerun-v1-raw.json) · [Strict comparison](self-trained-submission-v1-challenge-rerun-v1-comparison.json) · [Python/browser and preservation verification](self-trained-submission-v1-challenge-rerun-v1-validation.json).

The residual model was selected explicitly before this rerun. The submission still defaults to the MNIST-only course model; this result belongs to its separately labelled residual extension. No weights, preprocessing, submission archive, existing website or score display were changed. No training or selection followed this known-image result.
