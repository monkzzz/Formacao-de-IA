# GSS vision, tokens and embeddings

Executed on 2026-10-17 using the existing course demonstrations and the participant's chosen assistant. This completes the next five checklist activities with the limits below. Sources: [GSS setup](../../Dia1/Exercicios-GSS/README.md), [module 1](../../Dia1/Exercicios-GSS/modulo1/README.md), [module 2](../../Dia1/Exercicios-GSS/modulo2/README.md), and the unchanged [provenance manifest](../../Dia1/Exercicios-GSS/origem.json).

## Preparation and method

Installed the exact optional requirements into the ignored `Dia1/Exercicios-GSS/.venv`, then ran module 1 exercise 06 with `--preparar`. All five official checkpoints are in the ignored `.cache/yolo/models/` directory. The initial restricted installation failed to find packages; the network-enabled retry succeeded. No requirement versions or course sources were changed. Preparation occurred during this execution; no claim of preparation before a past class is made.

The [execution record](gss-vision-language-evidence/execution.json) includes Python/package versions, successful `pip check`, model sizes/hashes, entry-script hashes and exit codes, input hashes, predictions, token IDs, and recording hashes. All three unchanged entry scripts exited zero in the documented noninteractive mode. The [recorder](run-gss-vision-language.py) additionally instantiated the actual Tk interfaces and invoked their controls, with real CPU inference for vision and recorded responses for language. This is assistant execution, not human interaction or classroom attendance.

Desktop capture returned foreground-terminal pixels or black images. Those captures were discarded. The images below are exports of the lessons' own annotated arrays and Matplotlib figures; they are **not desktop screenshots** and do not establish window visibility, layout on a physical display, or animation smoothness. Scripted GUI state and rendering were checked; a human desktop walkthrough remains useful.

## Vision: module 1 exercise 06

| Task | Observed result at the default .25 threshold | Rendered output |
| --- | --- | --- |
| Detection | Five objects in `bus.jpg`; classes and boxes localize individual detections. | [Annotated image](gss-vision-language-evidence/vision-detect.png) |
| Classification | One whole-image classification of `dog.jpg`, with five ranked ImageNet class scores. This task does not localize objects. | [Input shown by lesson](gss-vision-language-evidence/vision-classify.png); scores in JSON |
| Segmentation | Six objects and six instance masks in `bus.jpg`; masks do not partition every pixel into semantic classes. | [Masks](gss-vision-language-evidence/vision-segment.png) |
| Pose | Four people, with 17 possible keypoints per person; this estimates pose rather than identity or action. | [Keypoints](gss-vision-language-evidence/vision-pose.png) |
| Oriented boxes | 170 detections on aerial `boats.jpg`; dense legends were automatically hidden while rotated boxes remained. | [Oriented boxes](gss-vision-language-evidence/vision-obb.png) |

For video, the recorder created an ignored two-frame MJPEG fixture from the attributed `bus.jpg` (second frame horizontally flipped). The actual OpenCV worker loaded frame 1 and the next-frame control advanced to frame 2 with inference. See the [second-frame rendering](gss-vision-language-evidence/vision-video.png) and JSON. This verifies local decoding and stepping, not arbitrary video codecs or prolonged playback.

The webcam selector configured index 0 without opening a capture handle, as intended. **Live webcam inference was not run:** no classroom camera input was supplied. No camera frames were acquired or saved. The exercise is recorded as executed with this explicit input limitation, not as camera hardware validation.

The numeric scores describe outputs of pretrained models. No labelled evaluation set was used here, so no accuracy claim follows from the counts or scores. Changing tasks, input, or thresholds performs inference; no models were trained or tuned. Day 2 MNIST and the reserved CAPTCHA images were not accessed.

## Recorded language mode

The recorder explicitly sets `FORMACAO_LMSTUDIO_OFFLINE=1` before importing the lessons. Token counts come from `contagem_tokens.json`; embeddings come from `embeddings.json`. These existing recordings were read and hashed, not regenerated. No live LM Studio output or new LLM training is claimed. Unknown text is rejected when no recording exists, rather than silently inventing a vector or count.

To use the same mode in a new PowerShell session:

```powershell
$env:FORMACAO_LMSTUDIO_OFFLINE = "1"
rtk proxy Dia1/Exercicios-GSS/.venv/Scripts/python.exe Dia1/Exercicios-GSS/modulo2/dia1_modulo2_01_tokens_ids.py
rtk proxy Dia1/Exercicios-GSS/.venv/Scripts/python.exe Dia1/Exercicios-GSS/modulo2/dia1_modulo2_02_mapa_embeddings.py
```

## Tokens: module 2 exercise 01

Compared all four prepared texts. The didactic vocabulary produced 12, 10, 13, and 3 tokens; recorded AMALIA counts were respectively 10, 14, 12, and 7. Tokenization depends on the vocabulary, so words, tokens, and character counts are different quantities. Repeated pieces retain their IDs; `##` marks continuation. `Rolamento sobreaquecido!` yielded two `[UNK]` tokens and punctuation in the small teaching vocabulary, while the recorded model used seven tokens.

Opened the [vocabulary view](gss-vision-language-evidence/tokens-vocabulary.png), inspected the [unknown-token example](gss-vision-language-evidence/tokens-unknown.png), attempted unrecorded text and observed the explicit missing-recording message, then cleared the input successfully. Exact token pieces and IDs are in JSON. Numeric IDs are vocabulary indices, not semantic distances.

## Embeddings: module 2 exercise 02

Loaded 16 recorded vectors of 1,024 dimensions and inspected the [nearest-neighbour panel](gss-vision-language-evidence/embeddings-neighbours.png). Neighbours are computed using the full vectors; the two-dimensional projection is only a visualization. For the selected sensor sentence, the displayed top similarities rounded to .55 across maintenance, logistics and quality examples. This limited sample should not be interpreted as uniformly clean topic separation.

Added the recorded suggestion `Rolamento gasto na linha 3`, opened the [ambiguous banco comparison](gss-vision-language-evidence/embeddings-bank.png), and compared money/garden anchors. The money sentence scored approximately .57/.48; the garden sentence .47/.61. Context changed similarity despite sharing the word `banco`. Similarity is not a correctness probability or proof of human understanding. An unrecorded sentence produced the expected missing-vector message; clearing restored the original set and selection state.

## Reproduction and validation limits

From the repository root, after preparing the dependencies and weights:

```powershell
rtk proxy Dia1/Exercicios-GSS/.venv/Scripts/python.exe participant-work/day1/run-gss-vision-language.py
```

This overwrites only `gss-vision-language-evidence/` outputs; preserve the current evidence separately before re-running. The fixture and weights remain ignored. Original image attribution remains in [resources](../../Dia1/Exercicios-GSS/recursos/README.md); derivative vision images retain the same source obligations. The course provenance manifest is unchanged.

Validation covers three successful entry runs, real five-task inference, successful environment dependency checking, video frame advancement, webcam selection without activation, token/embedding controls, and missing-recording recovery. No course implementation was changed or new unit tests added. The full offline unit suite remains a separate later checklist task. Live camera capture, live LM Studio, human GUI interaction and participant mastery remain unverified.

The [batch validator](validate-gss-batch.py) passed: exactly the next five checklist entries changed, 115 local links and 22 heading anchors resolved, entry/model/recording/provenance hashes matched, and ten rendered images existed. All ten exports were visually inspected by the assistant. `rtk git diff --check` passed. Run the validator with the GSS Python interpreter before committing the batch; its checklist comparison intentionally uses the current `HEAD` as the baseline.
