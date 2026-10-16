import {loadModel, predict} from "./inference.js?v=captcha-3";
import {prepareCanvas, PREPROCESS_VERSION} from "./preprocess.js?v=3.6.0";
import {createWordsWorkspace} from "./words.js?v=3.2.0";
import {createDrawingTools} from "./canvas-tools.js?v=3.2.0";
import {createDigitReader, DIGIT_READERS} from "./digit-readers.js?v=3";

const $ = id => document.getElementById(id);
const state = {model: null, models: {}, mode: "digits", uploads: [], busy: false, loading: false, ready: false};
const canvas = $("drawing"), ctx = canvas.getContext("2d", {willReadFrequently: true});
let drawing = false, previousPoint = null;
const APPLICATION_VERSION = $("app-version").textContent.trim().slice(1);
const words = createWordsWorkspace(APPLICATION_VERSION);
const digitReader = createDigitReader(message => status(message));
let cancelled = false;
const selectedReader = () => state.mode === "digits" ? $("digit-reader").value : "local";
const externalReader = () => selectedReader() !== "local";

function readerViews() {
  const external = externalReader(), wordMode = state.mode === "words";
  $("digit-reader-options").hidden = state.mode !== "digits";
  $("digit-quality-options").hidden = !external || DIGIT_READERS[selectedReader()].engine === "ddddocr";
  $("digit-reader-about").hidden = !external;
  for (const id of ["network", "model"]) $(id).hidden = wordMode || external;
  $("scores").hidden = external;
  document.querySelector(".scores-heading").hidden = external;
  document.querySelector(".input-preview").hidden = external;
  $("digit-ocr-output").hidden = !external;
  const singleDigit = DIGIT_READERS[selectedReader()].single_digit;
  $("uncertainty").textContent = singleDigit ? "Assumes exactly one digit. A conditional digit score is not a calibrated correctness probability."
    : external ? "An OCR transcription can be wrong. Review the original output below."
    : "A model score is a prediction, not a promise. Ambiguous handwriting can be misread.";
  $("digit-ocr-output").querySelector(".word-note").textContent = singleDigit
    ? "Rates the ten single-digit hypotheses directly from the model. The unrestricted character transcription is preserved below for comparison."
    : "OCR transcription, without a correctness score. Review the original output before using it.";
  $("digit-ocr-output").querySelector("summary").textContent = singleDigit ? "Unrestricted character transcription" : "Original digit reader output";
  const link = document.querySelector("nav a:last-child");
  link.href = wordMode ? "#word-about" : external ? "#digit-reader-about" : "#network";
  link.textContent = wordMode ? "About the word reader" : external ? "About the digit reader" : "Inside the model";
}

function changeReader(reader, profile = $("digit-quality").value) {
  digitReader.stop();
  if (DIGIT_READERS[reader].engine === "ddddocr") profile = "standard";
  $("digit-reader").value = reader; $("digit-quality").value = profile;
  resetOutput(); readerViews();
}
for (const id of ["digit-reader", "digit-quality"]) $(id).addEventListener("change", () => {
  changeReader($("digit-reader").value);
  status(selectedReader() === "local" ? "Digit Lab CNN selected. Read your drawing or choose images."
    : `${DIGIT_READERS[selectedReader()].name} selected. Downloads start only when you read a drawing or image.`);
});
$("digit-cancel").addEventListener("click", () => {cancelled = true; digitReader.stop();});
const drawingTools = createDrawingTools(canvas, {prefix: "drawing", background: "#14251d", penWidth: 20, eraserWidth: 36,
  onRestore: () => {drawing = false; previousPoint = null; resetOutput(); status("Drawing restored. Read it again when ready.");}});
const MODES = ["digits", "letters", "words"];

function displayMode(mode) {
  const wordMode = mode === "words";
  for (const name of MODES) $("mode-" + name).setAttribute("aria-pressed", String(name === mode));
  $("words-workspace").hidden = !wordMode;
  for (const id of ["character-workspace", "mode-hint", "status", "network", "model"]) $(id).hidden = wordMode;
  $("uploads-section").hidden = wordMode || !state.uploads.length;
  const modelLink = document.querySelector("nav a:last-child");
  modelLink.href = wordMode ? "#word-about" : "#network";
  modelLink.textContent = wordMode ? "About the word reader" : "Inside the model";
  words.activate(wordMode);
  readerViews();
}

function status(message, error = false) {
  $("status").textContent = message;
  $("status").classList.toggle("error", error);
}

function paintMap(canvas, values, side) {
  if (canvas.width !== side || canvas.height !== side) canvas.width = canvas.height = side;
  const context = canvas.getContext("2d");
  const maximum = Math.max(1e-9, ...values);
  const data = context.createImageData(side, side);
  for (let i = 0; i < values.length; i++) {
    const v = Math.min(1, Math.max(0, values[i] / maximum));
    data.data.set([Math.round(16 + v * 181), Math.round(34 + v * 202), Math.round(26 + v * 122), 255], i * 4);
  }
  context.putImageData(data, 0, 0);
}

function initializeViews() {
  renderScores(Array.from("0123456789"));
  for (const [id, count, side] of [["layer-one", 16, 14], ["layer-two", 32, 7]]) {
    for (let i = 0; i < count; i++) {
      const map = document.createElement("canvas"); map.width = map.height = side;
      map.title = `Actual feature map ${i + 1}`; map.setAttribute("aria-label", map.title);
      $(id).append(map); paintMap(map, new Float32Array(side * side), side);
    }
  }
}

function renderScores(labels) {
  $("scores").replaceChildren();
  $("scores").classList.toggle("letters", labels.length === 26);
  for (const label of labels) {
    const row = document.createElement("div"); row.className = "score-row";
    row.innerHTML = `<span>${label}</span><div class="score-track"><div class="score-fill"></div></div><span>—</span>`;
    $("scores").append(row);
  }
}

function setControls() {
  drawingTools.setDisabled(!state.ready || state.busy || state.loading);
  $("classify").disabled = $("files").disabled = !state.ready || state.busy || state.loading;
  $("clear").disabled = state.busy || state.loading;
  $("export").disabled = !state.uploads.length || state.busy || state.loading;
  for (const mode of MODES) $("mode-" + mode).disabled = state.busy || state.loading;
  $("digit-reader").disabled = $("digit-quality").disabled = state.busy || state.loading;
  $("digit-cancel").hidden = !state.busy || !externalReader();
}

async function activateMode(mode) {
  if (state.busy || state.loading) return false;
  if (mode !== "digits") digitReader.stop();
  if (mode === "words") {
    state.mode = mode; state.ready = false;
    displayMode(mode); setControls();
    return true;
  }
  state.loading = true; setControls();
  $("status").hidden = false;
  status(`Loading and verifying the ${mode} model…`);
  try {
    const model = state.models[mode] || await loadModel(mode);
    state.models[mode] = model; state.model = model; state.mode = mode; state.ready = true;
    const letters = mode === "letters", manifest = model.manifest, test = manifest.training.test;
    for (const name of ["digits", "letters"]) $("mode-" + name).setAttribute("aria-pressed", String(name === mode));
    $("canvas-hint").textContent = letters ? "DRAW A SINGLE LETTER · A–Z" : "DRAW A SINGLE DIGIT · 0–9";
    canvas.setAttribute("aria-label", letters ? "Draw one handwritten letter, A to Z" : "Draw one digit, from zero to nine");
    $("mode-hint").textContent = letters
      ? "One handwritten letter at a time. Uppercase and lowercase forms are recognized as the same A–Z class."
      : "Choose Digits for 0–9. Use Letters for A–Z, especially for similar shapes such as O and 0.";
    $("test-dataset").textContent = letters ? "Official EMNIST Letters test" : "Official MNIST test";
    $("test-accuracy").textContent = `${(test.accuracy * 100).toFixed(2)}% · ${test.correct.toLocaleString()} / ${test.count.toLocaleString()}`;
    $("architecture").textContent = manifest.architecture === "residual64-16-32-128"
      ? "64px · Conv 16 → Residual 16 → Conv 32 → Average pool → Residual 32 → Dense 128 → 10"
      : `${model.inputSide}px · Conv 16 → Conv 32${model.inputSide === 64 ? " → Average pool" : ""} → Dense 128 → ${model.labels.length}`;
    document.querySelector(".input-preview p").textContent = `Your image, prepared as ${model.inputSide} × ${model.inputSide} pixels. Check this view if a prediction surprises you.`;
    document.querySelector(".input-dimensions").textContent = `${model.inputSide} × ${model.inputSide}`;
    for (const [id, count, side] of [["layer-one", 16, model.featureSides[0]], ["layer-two", 32, model.featureSides[1]]]) {
      $(id).parentElement.querySelector("h3 small").textContent = `${count} maps · ${side} × ${side} pixels`;
      for (const map of $(id).children) map.width = map.height = side;
    }
    $("data-split").textContent = `${manifest.training.split.train.toLocaleString()} / ${manifest.training.split.validation.toLocaleString()} · no challenge inputs`;
    $("hash").textContent = manifest.sha256;
    renderScores(model.labels); resetOutput();
    displayMode(mode);
    status(`${letters ? "Letters A–Z" : "Digits 0–9"} ready. Draw one character or choose an image to begin.`);
    return true;
  } catch (error) {status(error.message, true); return false;}
  finally {state.loading = false; setControls();}
}
for (const mode of MODES) $("mode-" + mode).addEventListener("click", () => activateMode(mode));

function resetDrawing() {
  drawing = false; previousPoint = null;
  drawingTools.clear();
}

function showPrediction(result, input, title, elapsed, model = state.model) {
  $("prediction").classList.remove("is-empty");
  $("predicted").textContent = result.label;
  $("prediction-label").textContent = title;
  if (result.ocr) {
    $("confidence").textContent = result.singleDigit ? `${(result.scores[result.digit] * 100).toFixed(2)}% conditional digit score`
      : result.accepted ? "OCR transcription · no class score" : "No single digit recognized";
    $("digit-raw").textContent = result.rawText || "(empty output)";
    $("digit-ocr-preview").src = input.toDataURL("image/png");
    $("digit-ocr-preview").hidden = false;
    $("timing").textContent = `${elapsed.toFixed(1)} MS / INFERENCE`;
    return;
  }
  $("confidence").textContent = `${(result.scores[result.digit] * 100).toFixed(2)}% model score`;
  $("timing").textContent = `${elapsed.toFixed(1)} MS / INFERENCE`;
  const rows = $("scores").children;
  for (let i = 0; i < result.scores.length; i++) {
    rows[i].classList.toggle("winner", i === result.digit);
    rows[i].querySelector(".score-fill").style.width = `${result.scores[i] * 100}%`;
    rows[i].lastElementChild.textContent = `${(result.scores[i] * 100).toFixed(2)}%`;
  }
  paintMap($("prepared"), input, model.inputSide);
  for (const [id, values, side] of [["layer-one", result.first, model.featureSides[0]], ["layer-two", result.second, model.featureSides[1]]]) {
    Array.from($(id).children).forEach((map, i) => paintMap(map, values.slice(i * side * side, (i + 1) * side * side), side));
  }
  const hiddenContext = $("hidden").getContext("2d");
  const maximum = Math.max(1e-9, ...result.hidden);
  for (let i = 0; i < 128; i++) {
    const v = result.hidden[i] / maximum;
    hiddenContext.fillStyle = `rgb(${16 + v * 181}, ${34 + v * 202}, ${26 + v * 122})`;
    hiddenContext.fillRect((i % 16) * 8, Math.floor(i / 16) * 8, 7, 7);
  }
  const connections = Array.from(result.hidden, (activation, i) => ({i,
    value: activation * model.weights["fc2.weight"][result.digit * 128 + i]}))
    .sort((a, b) => Math.abs(b.value) - Math.abs(a.value)).slice(0, 8);
  const scale = Math.max(1e-9, ...connections.map(c => Math.abs(c.value)));
  $("connections").replaceChildren();
  for (const connection of connections) {
    const row = document.createElement("div"); row.className = "connection-row";
    row.innerHTML = `<span>h${connection.i}</span><div class="connection-track"><div class="connection-fill ${connection.value < 0 ? "negative" : ""}" style="width:${Math.abs(connection.value) / scale * 100}%"></div></div><span>${connection.value.toFixed(3)}</span>`;
    row.title = `hidden activation × learned output weight for class ${result.label}; bias is not included`;
    $("connections").append(row);
  }
}

function run(input) {
  const start = performance.now(), result = predict(state.model, input);
  return {result, elapsed: performance.now() - start};
}

function point(event) {
  const rect = canvas.getBoundingClientRect();
  return [(event.clientX - rect.left) * canvas.width / rect.width,
    (event.clientY - rect.top) * canvas.height / rect.height];
}
canvas.addEventListener("pointerdown", event => {
  if (!state.ready || state.busy || state.loading) return;
  drawingTools.snapshot(); resetOutput();
  event.preventDefault(); canvas.setPointerCapture(event.pointerId);
  drawing = true; previousPoint = point(event);
  const brush = drawingTools.brush;
  status(brush.eraser ? "Erase unwanted marks, then read the drawing again." : "Drawing updated. Read it when ready.");
  ctx.fillStyle = brush.color;
  if (brush.eraser) ctx.fillRect(previousPoint[0] - brush.width / 2, previousPoint[1] - brush.width / 2, brush.width, brush.width);
  else {ctx.beginPath(); ctx.arc(...previousPoint, brush.width / 2, 0, Math.PI * 2); ctx.fill();}
});
canvas.addEventListener("pointermove", event => {
  if (!drawing) return;
  const current = point(event);
  const brush = drawingTools.brush;
  ctx.strokeStyle = brush.color; ctx.lineWidth = brush.width; ctx.lineCap = brush.eraser ? "square" : "round"; ctx.lineJoin = "round";
  ctx.beginPath(); ctx.moveTo(...previousPoint); ctx.lineTo(...current); ctx.stroke(); previousPoint = current;
});
for (const name of ["pointerup", "pointercancel", "lostpointercapture"]) canvas.addEventListener(name, () => {drawing = false; previousPoint = null;});
function resetOutput() {
  $("digit-raw").textContent = "No transcription yet.";
  $("digit-ocr-preview").hidden = true; $("digit-ocr-preview").removeAttribute("src");
  $("prediction").classList.add("is-empty");
  $("predicted").textContent = "—"; $("prediction-label").textContent = state.mode === "letters" ? "Waiting for a letter" : "Waiting for a digit";
  $("confidence").textContent = "Your next mark goes here"; $("timing").textContent = "READY WHEN YOU ARE";
  for (const row of $("scores").children) {
    row.classList.remove("winner"); row.querySelector(".score-fill").style.width = "0%"; row.lastElementChild.textContent = "—";
  }
  const inputSide = state.model?.inputSide || 28;
  paintMap($("prepared"), new Float32Array(inputSide * inputSide), inputSide);
  for (const id of ["layer-one", "layer-two"]) for (const map of $(id).children) paintMap(map, new Float32Array(map.width ** 2), map.width);
  $("hidden").getContext("2d").clearRect(0, 0, 128, 64);
  $("connections").textContent = "Classify an input to inspect learned connections.";
  for (const card of $("uploads").children) card.classList.remove("active");
}
$("clear").addEventListener("click", () => {
  resetDrawing(); resetOutput();
  status(`Canvas cleared. Draw one ${state.mode === "letters" ? "letter" : "digit"} or choose local images.`);
});
$("classify").addEventListener("click", async () => {
  if (state.busy || !state.ready) return;
  state.busy = true; cancelled = false; setControls();
  try {
    const {result, input, elapsed} = await readSource(canvas);
    showPrediction(result, input, "Your drawing", elapsed);
    status(result.ocr && !result.accepted ? "The reader did not return exactly one digit. Review its original output or try another model."
      : "Prediction ready. Review the result or try another character.", result.ocr && !result.accepted);
  } catch (error) { status(error.message, true); }
  finally {state.busy = false; setControls();}
});

async function readSource(source) {
  if (!externalReader()) {
    const input = prepareCanvas(source, state.model.inputSide);
    return {...run(input), input, identity: null};
  }
  const output = await digitReader.read(source, selectedReader(), $("digit-quality").value);
  return {...output, input: output.prepared};
}

async function sha256(bytes) {
  return Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256", bytes)), b => b.toString(16).padStart(2, "0")).join("");
}

async function uploadFile(file, batch) {
  const model = state.model, mode = state.mode, reader = selectedReader(), profile = $("digit-quality").value;
  const record = {file: file.name, bytes: file.size, batch, recorded_at: new Date().toISOString(),
    mode, model_sha256: model.manifest.sha256, labels: model.labels,
    input_side: model.inputSide, preprocessing: model.manifest.preprocessing,
    architecture: model.manifest.architecture, reader};
  if (reader !== "local") Object.assign(record, {model_sha256: null, input_side: null,
    preprocessing: "word-crop-display-v1", architecture: "vision-encoder-decoder", labels: null,
    model: DIGIT_READERS[reader].model, revision: DIGIT_READERS[reader].revision,
    trained_by_project: false, profile, precision: profile === "precise" ? "float32" : "int8", decoding: "greedy"});
  if (DIGIT_READERS[reader].engine === "ddddocr") Object.assign(record, {
    model_sha256: DIGIT_READERS[reader].sha256, preprocessing: DIGIT_READERS[reader].preprocessing,
    architecture: "captcha-ctc", precision: "float32", decoding: DIGIT_READERS[reader].decoding});
  if (DIGIT_READERS[reader].single_digit) Object.assign(record, {architecture: "captcha-ctc-single-digit",
    labels: Array.from("0123456789"), configuration: DIGIT_READERS[reader].configuration,
    output_constraint: "exactly one ASCII digit", score_scope: "conditional on one of ten single-digit CTC targets"});
  const card = document.createElement("button"); card.type = "button"; card.className = "upload-result";
  const name = document.createElement("strong"); name.textContent = file.name;
  const summary = document.createElement("span"); summary.textContent = "Processing…";
  card.append(name, summary); $("uploads").append(card);
  let previewURL;
  try {
    if (file.size > 30 * 1024 * 1024) throw new Error("Image exceeds the 30 MB limit.");
    if (file.type && !["image/png", "image/jpeg", "image/webp"].includes(file.type)) throw new Error("Use PNG, JPEG, or WebP images.");
    const bytes = await file.arrayBuffer(); record.file_sha256 = await sha256(bytes);
    const bitmap = await createImageBitmap(file);
    if (bitmap.width * bitmap.height > 16000000) {bitmap.close(); throw new Error("Image exceeds 16 million pixels.");}
    const imageCanvas = document.createElement("canvas"); imageCanvas.width = bitmap.width; imageCanvas.height = bitmap.height;
    imageCanvas.getContext("2d").drawImage(bitmap, 0, 0); bitmap.close();
    if (cancelled) throw new Error("Digit reading cancelled.");
    const {input, result, elapsed} = await readSource(imageCanvas);
    record.width = imageCanvas.width; record.height = imageCanvas.height;
    if (result.ocr) {
      record.raw_text = result.rawText; record.accepted = result.accepted;
      record.prepared_width = input.width; record.prepared_height = input.height;
      record.input_sha256 = await sha256(input.getContext("2d").getImageData(0, 0, input.width, input.height).data.buffer);
    } else {record.input = Array.from(input); record.input_sha256 = await sha256(input.buffer);}
    record.predicted = mode === "digits" ? result.digit : result.label;
    record.predicted_label = result.ocr && !result.accepted ? null : result.label; record.class_index = result.digit;
    record.scores = result.scores; record.logits = result.logits;
    record.inference_ms = elapsed;
    previewURL = URL.createObjectURL(file);
    const preview = document.createElement("img"); preview.src = previewURL; preview.alt = `Uploaded image: ${file.name}`;
    preview.onload = () => URL.revokeObjectURL(previewURL); card.prepend(preview);
    summary.textContent = result.ocr ? `${result.accepted ? result.label : "No single digit"} · ${DIGIT_READERS[reader].name} · ${DIGIT_READERS[reader].engine === "ddddocr" ? "FP32" : profile}`
      : `${result.label} · ${(result.scores[result.digit] * 100).toFixed(2)}% model score · ${mode}`;
    const select = async (automatic = false) => {
      if (!automatic && (state.busy || state.loading)) return;
      if (state.mode !== mode && !await activateMode(mode)) return;
      if (mode === "digits" && (selectedReader() !== reader || $("digit-quality").value !== profile)) changeReader(reader, profile);
      for (const item of $("uploads").children) item.classList.remove("active");
      card.classList.add("active"); showPrediction(result, input, file.name, elapsed, model);
    };
    card.addEventListener("click", () => select()); await select(true);
  } catch (error) {
    if (previewURL) URL.revokeObjectURL(previewURL);
    record.error = error.message; summary.textContent = error.message; summary.classList.add("error"); card.disabled = true;
  }
  state.uploads.push(record);
  $("upload-count").textContent = state.uploads.length;
}

function exportRecord() {
  return {schema: 2, exported_at: new Date().toISOString(), origin: location.origin,
    application: "Digit Lab " + APPLICATION_VERSION, application_version: APPLICATION_VERSION,
    mode: state.mode, reader: selectedReader(), model_sha256: state.mode === "words" ? null : externalReader() ? DIGIT_READERS[selectedReader()].sha256 || null : state.model.manifest.sha256,
    preprocessing: state.mode === "words" ? null : externalReader() ? DIGIT_READERS[selectedReader()].preprocessing || "word-crop-display-v1" : state.model.manifest.preprocessing, labels_consulted_by_app: false,
    note: "Raw model outputs only; each record identifies its own mode, class labels and model hash. No answer key is loaded or used.",
    predictions: state.uploads};
}
$("files").addEventListener("change", async event => {
  if (!state.ready || state.busy) return;
  const files = Array.from(event.target.files); if (!files.length) return;
  state.busy = true; setControls();
  cancelled = false;
  $("uploads-section").hidden = false;
  const batch = crypto.randomUUID();
  try {for (let i = 0; i < files.length; i++) {
    if (cancelled) break;
    status(`Processing image ${i + 1} of ${files.length} locally…`);
    await new Promise(resolve => requestAnimationFrame(resolve));
    await uploadFile(files[i], batch);
  }
  const records = state.uploads.filter(r => r.batch === batch), errors = records.filter(r => r.error || r.accepted === false).length;
  status(`${cancelled ? "Reading cancelled. " : ""}${records.length - errors} of ${files.length} images ready. Select a result to explore it, or export your session.`, errors > 0);
  } catch (error) {status(error.message, true);}
  finally {state.busy = false; setControls(); event.target.value = "";}
});
$("export").addEventListener("click", () => {
  const url = URL.createObjectURL(new Blob([JSON.stringify(exportRecord(), null, 2)], {type: "application/json"}));
  const link = document.createElement("a"); link.href = url; link.download = `digitlab-predictions-${Date.now()}.json`; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});

initializeViews(); drawingTools.reset();
document.querySelector('nav a:last-child').addEventListener("click", () => {
  $(state.mode === "words" ? "word-about" : externalReader() ? "digit-reader-about" : "network").open = true;
});
await activateMode("digits");

// A narrow QA surface invokes the same functions and weights as the interface.
window.digitLab = {state, predict: input => predict(state.model, Float32Array.from(input)),
  prepareCanvas: (canvas, side = state.model?.inputSide || 28) => prepareCanvas(canvas, side),
  exportRecord, activateMode, wordsContext: words.context,
  applicationVersion: APPLICATION_VERSION,
  get version() {return state.model?.manifest.preprocessing || PREPROCESS_VERSION;}};
