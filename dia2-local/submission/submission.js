import {loadModel, predict} from "./v3/inference.js?v=self-trained-1";
import {prepareCanvas} from "./v3/preprocess.js?v=3.6.0";
import {createDrawingTools} from "./v3/canvas-tools.js?v=3.11.1";
import {imageCanvas, imagePreview, downloadBlob} from "./v3/browser-utils.js?v=3.11.1";

const $ = id => document.getElementById(id);
const datasets = ["mnist", "mnist-supplementary-v1", "captcha-v3"];
const state = {mode: "digits", dataset: "mnist", model: null, ready: false,
  busy: false, records: [], current: null};
const canvas = $("drawing");
const tools = createDrawingTools(canvas, {
  prefix: "drawing", background: "#14251d", penWidth: 20, eraserWidth: 36,
  onDraw: resetOutput, onRestore: resetOutput,
});
let evaluation = null;

function status(text) {$("status").textContent = text;}

function controls() {
  // Mode selection and retry remain available when initial loading fails.
  for (const id of ["mode", "dataset"]) $(id).disabled = state.busy;
  for (const id of ["files", "read", "clear"]) $(id).disabled = state.busy || !state.ready;
  $("export").disabled = state.busy || !state.records.length;
  $("retry").hidden = state.busy || state.ready;
  for (const button of $("uploads").children) button.disabled = state.busy;
  tools.setDisabled(state.busy || !state.ready);
}

function resetOutput() {
  state.current = null; $("prediction").textContent = "—"; $("scores").replaceChildren();
  const input = $("input");
  input.getContext("2d").clearRect(0, 0, input.width, input.height);
  for (const id of ["first", "second"]) $(id).replaceChildren();
  $("hidden").getContext("2d").clearRect(0, 0, 128, 1);
}

function clearRecords() {
  state.records = []; $("uploads").replaceChildren(); resetOutput();
}

function paint(target, values, width, height) {
  target.width = width; target.height = height;
  const context = target.getContext("2d"), pixels = context.createImageData(width, height);
  for (let i = 0; i < values.length; i++) {
    const value = Math.max(0, Math.min(255, Math.round(values[i] * 255)));
    pixels.data.set([value, value, value, 255], i * 4);
  }
  context.putImageData(pixels, 0, 0);
}

function maps(id, values, side) {
  const area = side * side, children = [];
  for (let i = 0; i < values.length / area; i++) {
    const map = Array.from(values.slice(i * area, (i + 1) * area));
    const maximum = Math.max(...map, 1e-12), target = document.createElement("canvas");
    target.setAttribute("aria-label", `${id} feature ${i + 1}`);
    paint(target, map.map(value => value / maximum), side, side); children.push(target);
  }
  $(id).replaceChildren(...children);
}

function scoreRow(label, score) {
  const row = document.createElement("div"), name = document.createElement("span");
  const bar = document.createElement("progress"), value = document.createElement("span");
  row.className = "score"; name.textContent = label;
  bar.max = 1; bar.value = score; bar.setAttribute("aria-label", `${label} score`);
  value.textContent = (score * 100).toFixed(2) + "%"; row.append(name, bar, value);
  return row;
}

function show(record, result) {
  state.current = record;
  $("prediction").textContent = `${record.label} · ${(record.scores[record.predicted] * 100).toFixed(2)}%`;
  paint($("input"), record.input, state.model.inputSide, state.model.inputSide);
  $("scores").replaceChildren(...record.labels.map((label, i) => scoreRow(label, record.scores[i])));
  maps("first", result.first, state.model.featureSides[0]);
  maps("second", result.second, state.model.featureSides[1]);
  const maximum = Math.max(...result.hidden, 1e-12);
  paint($("hidden"), Array.from(result.hidden, value => value / maximum), 128, 1);
}

function classify(source, file) {
  const started = performance.now(), input = prepareCanvas(source, state.model.inputSide);
  const result = predict(state.model, input);
  const record = {file, mode: state.mode, dataset: state.mode === "digits" ? state.dataset : "emnist-letters",
    model_sha256: state.model.manifest.sha256, preprocessing: state.model.manifest.preprocessing,
    labels: state.model.labels, predicted: result.digit, label: result.label, scores: result.scores,
    input: Array.from(input), milliseconds: performance.now() - started};
  return {record, result};
}

async function loadEvaluation() {
  if (!evaluation) {
    const response = await fetch("./evaluation.json");
    if (!response.ok) throw new Error("Cannot load recorded evaluations. Try loading the model again.");
    const candidate = await response.json();
    if (![...datasets, "letters"].every(name => {
      const entry = candidate.models?.[name];
      return entry && typeof entry.scope === "string" && typeof entry.dataset === "string"
        && Number.isFinite(entry.clean_accuracy) && Number.isInteger(entry.clean_count)
        && typeof entry.model_sha256 === "string";
    })) {
      throw new Error("Recorded evaluations are incomplete. Restore the matching package.");
    }
    evaluation = candidate;
  }
  return evaluation;
}

function modelViews(entry) {
  $("mode").value = state.mode; $("dataset").value = state.dataset;
  $("dataset-control").hidden = state.mode === "letters";
  $("model-scope").textContent = entry.scope;
  $("metrics").textContent = `Recorded ${entry.dataset} accuracy: ${(entry.clean_accuracy * 100).toFixed(2)}% (${entry.clean_count.toLocaleString()} test images).`;
  $("challenge").textContent = entry.official
    ? `Recorded official follow-up: ${entry.official.correct}/10 correct; ${entry.official.correct_above_90}/10 correct with original score strictly >90%. Target remains unmet.`
    : "Letters are a separate EMNIST extension; no digit CAPTCHA score applies.";
  $("submission-version").textContent = evaluation.package_name || "Participant-trained submission";
}

async function activate(mode = state.mode, dataset = state.dataset) {
  if (state.busy) throw new Error("Finish current processing first.");
  if (!["digits", "letters"].includes(mode) || !datasets.includes(dataset)) throw new Error("Unsupported submission model.");
  state.busy = true; controls(); status("Verifying bundled model weights…");
  try {
    const metadata = await loadEvaluation(), entry = metadata.models[mode === "letters" ? "letters" : dataset];
    const model = await loadModel(mode, dataset);
    if (entry.model_sha256 !== model.manifest.sha256) throw new Error("Recorded evaluation and model identities do not match.");
    // Commit the selection only after loading and identity checks succeed.
    state.mode = mode; state.dataset = dataset; state.model = model; state.ready = true;
    clearRecords(); modelViews(entry); status("Ready. Draw one character or choose images.");
  } catch (error) {
    $("mode").value = state.mode; $("dataset").value = state.dataset;
    status(String(error)); throw error;
  } finally {state.busy = false; controls();}
}

async function upload(file) {
  try {
    const source = await imageCanvas(file, {
      maxBytes: 8 * 1024 * 1024, maxPixels: Infinity, maxSide: 4096, allowUnknownType: false,
      sizeError: "Use PNG, JPEG or WebP, up to 8 MB.", typeError: "Use PNG, JPEG or WebP, up to 8 MB.",
      dimensionsError: "Maximum image dimensions are 4096 × 4096.",
    });
    const {record, result} = classify(source, file.name); state.records.push(record);
    const button = document.createElement("button"), text = document.createElement("span");
    button.type = "button"; button.disabled = state.busy; text.textContent = `${file.name}: ${record.label}`;
    button.append(imagePreview(file, file.name), text);
    button.addEventListener("click", () => {if (!state.busy) show(record, result);});
    $("uploads").append(button); show(record, result); return true;
  } catch (error) {
    state.records.push({file: file.name, error: String(error), mode: state.mode,
      dataset: state.dataset, model_sha256: state.model.manifest.sha256});
    return false;
  }
}

function exportRecord() {
  return {schema: 1, application: "Digit Lab participant-trained submission " + (evaluation?.package_name || "v1"),
    mode: state.mode, dataset: state.dataset, labels_consulted_by_app: false,
    score_scope: "Original, unscaled CNN softmax", predictions: state.records};
}

$("clear").addEventListener("click", () => {tools.clear(); resetOutput(); status("Canvas cleared.");});
$("read").addEventListener("click", () => {
  if (!state.ready || state.busy) return;
  try {
    const {record, result} = classify(canvas, "drawing"); state.records.push(record); show(record, result); controls();
    status("Drawing classified with the selected trained model.");
  } catch (error) {resetOutput(); status(String(error));}
});
// activate reports errors in the interface; event handlers consume rejections.
$("mode").addEventListener("change", () => activate($("mode").value).catch(() => {}));
$("dataset").addEventListener("change", () => activate("digits", $("dataset").value).catch(() => {}));
$("retry").addEventListener("click", () => activate().catch(() => {}));
$("files").addEventListener("change", async event => {
  if (!state.ready || state.busy) return;
  const files = Array.from(event.target.files); event.target.value = "";
  if (!files.length) return;
  state.busy = true; controls(); let failures = 0;
  try {
    for (const file of files.slice(0, 20)) if (!await upload(file)) failures++;
    status(`${Math.min(files.length, 20)} images processed; ${failures} failed.${files.length > 20 ? " Limit: 20 images per selection." : ""}`);
  } finally {state.busy = false; controls();}
});
$("export").addEventListener("click", () => downloadBlob(
  new Blob([JSON.stringify(exportRecord(), null, 2)], {type: "application/json"}), "participant-trained-predictions.json"));

window.submission = {state, activate, exportRecord, predict: input => predict(state.model, Float32Array.from(input))};
await activate().catch(() => {});
