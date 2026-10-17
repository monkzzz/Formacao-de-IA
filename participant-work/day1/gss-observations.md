# GSS execution and observations: module 1, exercises 01–05

Executed 2026-10-17. Course sources: [setup guide](../../Dia1/Exercicios-GSS/README.md), [module 1 index](../../Dia1/Exercicios-GSS/modulo1/README.md), and unchanged [provenance manifest](../../Dia1/Exercicios-GSS/origem.json). This record covers the seven GSS tasks in the current ten-task batch. The other three tasks delivered the [final synthesis](synthesis-final.md) and [correction record](synthesis-corrections.md).

## Environment and method

Created `Dia1/Exercicios-GSS/.venv` with Python 3.12.10 and installed the documented base requirements. [Setup evidence](gss-evidence/setup.json) records successful installation and `pip check`: no broken requirements. NumPy, Torch, Matplotlib, and Pillow imports also succeeded. The initial sandboxed `ensurepip` failed; reviewed escalation allowed environment creation and installation to complete. Both the environment and downloaded cache remain ignored by Git.

While installation completed, the demonstrations used the already available `dia2-local/.venv` interpreter, whose base dependencies were verified. Its actual executable, package versions, and installed distribution inventory are in [execution.json](gss-evidence/execution.json) and [environment.txt](gss-evidence/environment.txt). The environments have different Pillow versions and are not claimed identical. That reused environment has no pip, so its `pip check` was not run; the separate new GSS environment passed that check.

Tk 8.6.15 and the TkAgg backend worked. A preliminary sandboxed Tk probe reported a 1280×720 screen; the escalated walkthrough captured 1920×1010 window client areas. These are observations from different execution contexts, not a claim that one resolution was used throughout.

The [recorder](run-gss-module1.py) first ran all five unchanged entry scripts with `MPLBACKEND=Agg` and `FORMACAO_ML_NO_PAUSE=1`. Every exit code was zero. It then instantiated the lessons' actual interfaces using TkAgg, advanced controls programmatically, and dispatched Matplotlib mouse events for drawing. All nine own-window screenshots were visually inspected by the assistant for the recorded states and readable content. This is automated assistant execution plus visual inspection, not human mouse/keyboard testing, participant mastery, or classroom attendance. Timed animation smoothness and every possible control sequence were not assessed.

## Dataset boundary

The existing loader downloaded UCI Optical Recognition of Handwritten Digits to `Dia1/Exercicios-GSS/.cache/datasets/optical_digits.zip`. The archive hash is `0d7b054fea010270e9b3f06411c654c5e59547732ad626381980baffe0a23fb0`. It contains 3,823 official training and 1,797 official test images, each 8×8 with intensities 0–16. Class counts and the exact download URL are in the execution record. Exercises 02 and 03 selected examples from official training data through the existing loader; exercise 05 split that training data into 3,251 training and 572 validation examples.

This cache is separate from Day 2's 28×28 MNIST and official CAPTCHA images. No Day 2 dataset, challenge, model, or evaluation record was changed or evaluated.

## Observed lessons

| Exercise | Actions and observations | Evidence |
| --- | --- | --- |
| 01: learning paradigms | Trained the synthetic supervised and unsupervised models and introduced a new session with 4.1 page visits / 40% exit rate. The supervised model predicted purchase; clustering assigned group 1. Group identity is not a purchase label. | [GUI](gss-evidence/01-paradigms.png), [entry log](gss-evidence/entry-01.txt) (empty output, successful exit recorded in JSON) |
| 01: Q-learning | Advanced one transition, then completed 200 training episodes. First reward: +0.1; 521 Q-values became nonzero. First/last 20 episode means were both 0.1 pipes; maximum was one pipe. Policy playback set exploration to zero and 100 transitions left Q-values unchanged. This shows an update/inference distinction, not evidence of improved play. | [Flappy GUI](gss-evidence/01-flappy.png), JSON lesson 1 |
| 02: forward pass | Inspected 8×8 pixels, a 64-value vector, and two selected normalized inputs at indices 2/10: 0.625/0.875. The didactic 2–2–2 network produced hidden activations 0.79875/0 and class scores after softmax of 0.33343/0.66657 for 0/5. Its prediction is from an untrained network and two pixels, not a digit accuracy result. | [GUI](gss-evidence/02-forward.png), [entry output](gss-evidence/entry-02.txt) |
| 03: learning cycle | Revealed forward/loss/derivatives/update/comparison, then cycled examples to 21 updates. The first sample loss fell 0.405610→0.346342; hidden-gradient norm was 0.369290. Mean loss over the six demonstration training examples changed 0.781074→0.689103; the plotted trajectory was not monotonic. These are training observations, not held-out results. | [GUI](gss-evidence/03-learning.png), [entry output](gss-evidence/entry-03.txt) |
| 04: evaluation | Compared thresholds 0.2/0.5/0.8 on the same fixed synthetic scores. At 0.5: TP=16, FP=8, FN=4, TN=72; accuracy=.88, precision=.6667, recall=.8, F1=.7273. Lowering the threshold raised recall with more false alarms; raising it yielded precision=1 and recall=.3 in this example. Swapping illustrative FN/FP costs yielded 84 units with unchanged predictions. ROC AUC=.88875 measures ranking across thresholds, not accuracy or retraining. | [Cost GUI](gss-evidence/04-costs.png), [ROC GUI](gss-evidence/04-roc.png), [entry output](gss-evidence/entry-04.txt) |
| 05: training/evaluation | Used the unchanged 64–32–10 MLP, CPU, seed 23, SGD .1, and twelve epochs / 312 updates. Validation loss selected epoch 12. Initial/final validation loss: 2.308497/.264071. Reserved-test accuracy=.908737, macro precision=.910837, macro recall=.908262, macro F1=.908680, loss=.355843. The confusion matrix includes 24 class-8 samples predicted as 1. | [Training GUI](gss-evidence/05-training.png), [evaluation GUI](gss-evidence/05-evaluation.png), [entry output](gss-evidence/entry-05.txt), full history/matrix in JSON |
| 05: drawing | Checked empty-input recovery, dispatched a synthetic vertical stroke onto the 24×24 canvas, inferred through its 8×8 reduction, then cleared it. Predicted class 1 with softmax score .773496. Clearing emptied the canvas. Frozen-model state hashes before/after inference agreed. This score is not a calibrated probability of correctness or a test-set metric. | [Drawing GUI](gss-evidence/05-drawing.png), JSON lesson 5 drawing checks |

The entry script and Tk walkthrough each created their own deterministic teaching model for exercise 05. Test evaluation occurred once per run after validation-based selection; no test-guided tuning or extra epochs were used to improve the reported result. The drawing was supplied only after freezing and was not training data. No model weights were exported or committed.

## Reproduction and limits

From the repository root, use the environment prepared for these lessons:

```powershell
rtk proxy Dia1/Exercicios-GSS/.venv/Scripts/python.exe participant-work/day1/run-gss-module1.py
```

This command needs a desktop for the Tk walkthrough and network access only when the UCI archive is absent. It performs fresh training and overwrites files in `gss-evidence/`; copy the existing evidence elsewhere first if preserving this particular run. The saved result records the interpreter actually used for this run, not an unexecuted result from the new environment. The recorder does not run optional YOLO or module 2 lessons.

No course source was edited, and entry-script / provenance hashes are retained in JSON. No new unit tests were added because the task executes existing lessons rather than changing them. The repository's full offline unit suite remains a later unchecked task; GUI evidence here does not certify every interaction or interface robustness on other displays.

Batch validation passed: 161 relative file links and 18 local heading anchors; exactly the next ten unchecked tasks were completed. The preserved original and audit remain byte-identical, the recorder parses, all five entry exits are zero, and nine screenshots exist. The validator also confirmed entry-script and UCI archive hashes and consistency of the test confusion matrix with its sample count and accuracy. `git diff --check` passed. The temporary validator was removed after use.
