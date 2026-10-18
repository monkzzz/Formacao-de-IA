# Local website cleanup

The preceding Python cleanup is committed as `6d21ce5`. This subsequent change
cleans the local v3.11.0 interface in `dist/v3/`; it does not rebuild the frozen
submission archive or publish a website.

## Changes

- `canvas-tools.js` now owns the shared character/word pen and eraser handlers.
  Workspaces opt in with an `onDraw` callback; consumers that already implement
  drawing, including the submission template, retain their existing handlers.
- A stroke belongs to its initiating pointer. Other pointers cannot paint or end
  it, secondary-button clicks do not paint, and undo, clearing or disabling the
  tools cancels an active shared stroke.
- `app.js` and `words.js` retain workspace-specific output/status updates while
  removing duplicate coordinate conversion and stroke handling.
- The model-navigation update has one owner, `readerViews`, and character uploads
  close decoded image bitmaps in `finally`, including failure paths.
- Browser QA includes pointer-ownership and undo-during-stroke regressions, accepts
  the current MNIST-only default, and permits separate model-selector screenshot
  prefixes so maintenance checks preserve earlier captures.

## Executed verification

From `dia2-local/`, with the repository's Linux Day 2 runtime and local server on
`http://127.0.0.1:8779/`:

```text
<python> -m unittest discover -s tests
<python> -m digitlab.words_qa --url http://127.0.0.1:8779/ --digit-experiment mnist --report frontend-cleanup-v1-words.json --screenshot-prefix frontend-cleanup-v1-words
<python> -m digitlab.selectable_models_qa --url http://127.0.0.1:8779/ --report frontend-cleanup-v1-models.json --screenshot-prefix frontend-cleanup-v1-models
```

- All 74 Python unit tests passed.
- [Words/drawing report](../reports/frontend-cleanup-v1-words.json): 18 verification
  groups passed; the separate real pretrained TrOCR smoke test was NOT RUN. The
  UI worker double is explicitly identified and makes no accuracy claim. Checks
  include both canvases, pixel-exact undo/redo, pointer isolation, keyboard tools,
  digit/letter activation parity, cancellation, exports and responsive layouts.
- [Model-selector report](../reports/frontend-cleanup-v1-models.json): all 19
  groups passed, including three digit CNNs, 30 non-challenge uploads, real
  activations, Python/browser score parity, Letters/Words transitions, historical
  card restoration, failed-load recovery and static browser-only requests.
- Node syntax checks passed for the three changed JavaScript modules; Git's
  whitespace check passed for the changed source and QA files.
- The coding agent inspected the new desktop/mobile model-selector screenshots.
  Independent human visual review and fresh Windows execution are NOT RUN.

The unrelated-pointer issue was reproduced in Chromium on both canvases before
the refactor. These checks use non-challenge fixtures; they do not train models,
select weights, rerun official CAPTCHA evaluation or establish new accuracy.
Existing historical reports, trained weights and the frozen submission package
are preserved. Deployment and remote publication are NOT RUN for this cleanup.
