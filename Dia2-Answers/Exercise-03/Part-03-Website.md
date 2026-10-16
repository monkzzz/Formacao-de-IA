# Exercise 3, Part 3 — Browser Application

Original: [Part 3](../../Dia2/Exercicio-03/Parte-03-Site-GitHub-Pages.md).

## What must the interface provide?

- A drawing canvas supporting mouse, pen, and touch, with clear and classify actions.
- Local selection of one or multiple images, with a preview and individual result for each file.
- The predicted digit and scores for all ten classes.
- Visualizations based on the current input and actual model activations or weights.
- Useful messages for model-loading failures, invalid files, empty input, and image-decoding failures.

An activation display is an observation of the model, not a complete explanation of why it predicted a class.

## How should input be prepared?

Define background handling, grayscale conversion, polarity, cropping, resizing, placement, and normalization before final evaluation. Transparent images need an explicit compositing background. Avoid separate undocumented transformations for drawing and upload: route both through the same preparation contract.

Test light and dark backgrounds, different dimensions, blank images, and unsupported inputs. Show the final 28 × 28 input so users can inspect what the model actually received. Do not derive predictions from filenames or labels.

## How should inference and visualization work?

Load the approved architecture and actual exported weights as static assets. Compute predictions locally. Connect visualizations to real intermediate values: prepared pixels, hidden activations, output scores, and selected learned connections. If showing only a subset of neurons or connections, label that limitation clearly.

Check browser outputs against the training implementation for identical prepared tensors. Separately verify image preprocessing. Confirm that the deployed weights match the recorded hash and model version.

## What should be reused from the reference application?

Before implementation, inspect the course-linked reference application's drawing, upload, preprocessing, export, tests, and deployment design. Reuse suitable components only after checking their license and recording attribution. Replace assumptions tied to a different architecture. This answer does not claim that external reference inspection has occurred.

## How should publication be verified?

Publish the participant's static application to GitHub Pages. Verify project-relative asset URLs, model loading, drawing, multiple uploads, and error handling on the public URL. Inspect network activity to confirm that image inference does not call a remote classifier; static asset downloads are expected.

Record the public URL, deployment/commit identity, model hash, browser used, parity results, and interaction evidence. A local preview alone does not establish that GitHub Pages works.

## Actual local implementation

The [local browser application](../../dia2-local/README.md) now supports drawing, clear, multi-image uploads, previews, ten-class scores, prepared inputs, real feature maps, hidden activations, learned output contributions, and raw JSON export. The reference application's design was reviewed; its code and weights were not copied.

Browser QA passed, including input preparation, origin/browser parity, error handling, mobile layout, and local-only requests. The maximum clean-fixture logit difference was approximately 0.00000382. See the [QA evidence](../../dia2-local/reports/browser-qa.json).

Public deployment remains unperformed because the user requested local-only work. Start `python serve.py` from `dia2-local/` and open `http://127.0.0.1:8765`.
