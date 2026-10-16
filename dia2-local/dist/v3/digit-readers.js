import {prepareWord} from "./words.js?v=3.2.0";

export const DIGIT_READERS = {
  local: {name: "Digit Lab residual CNN", trained_by_project: true},
  ddddocr: {name: "DdddOCR · CAPTCHA", model: "sml2h3/ddddocr/common.onnx", engine: "ddddocr",
    revision: "c40f56f95412e10bcb9bd0bd24411e92f896d238", download_mb: 54,
    sha256: "33b5cd351ee94e73a6bf8fa18c415ed8b819b3ffd342e267c30d8ad8334e34e8",
    preprocessing: "ddddocr-browser64-v1", decoding: "greedy-full-charset-ctc", trained_by_project: false},
  "ddddocr-old": {name: "DdddOCR Legacy · CAPTCHA", model: "sml2h3/ddddocr/common_old.onnx", engine: "ddddocr",
    revision: "c40f56f95412e10bcb9bd0bd24411e92f896d238", download_mb: 14,
    sha256: "b8f2ad9cbc1f2e3922a6cb9459e30824e7e2467f3fb4fd61420640e34ea0bf68",
    preprocessing: "ddddocr-browser64-v1", decoding: "greedy-full-charset-ctc", trained_by_project: false},
  printed: {name: "TrOCR Small · printed", model: "Xenova/trocr-small-printed",
    revision: "56c1626ea0b4aab378f3228235be2e824d4256bd", trained_by_project: false},
  handwritten: {name: "TrOCR Small · handwritten", model: "Xenova/trocr-small-handwritten",
    revision: "2432e24d184b1d964d07ed04f5d9e21d31a59141", trained_by_project: false},
};

// Preserve the full CAPTCHA; this model learns to handle interference itself.
export function prepareCaptcha(source) {
  const width = Math.max(1, Math.floor(source.width * 64 / source.height));
  if (width > 2048) throw new Error("Crop the image to one character before reading it.");
  const canvas = document.createElement("canvas"); canvas.width = width; canvas.height = 64;
  const ctx = canvas.getContext("2d", {willReadFrequently: true});
  ctx.fillStyle = "white"; ctx.fillRect(0, 0, width, 64);
  ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = "high";
  ctx.drawImage(source, 0, 0, width, 64);
  const image = ctx.getImageData(0, 0, width, 64), pixels = new Float32Array(width * 64);
  let low = 255, high = 0;
  for (let i = 0; i < pixels.length; i++) {
    const offset = i * 4;
    const gray = Math.round(.299 * image.data[offset] + .587 * image.data[offset + 1] + .114 * image.data[offset + 2]);
    low = Math.min(low, gray); high = Math.max(high, gray);
    pixels[i] = (gray / 255 - .5) / .5;
    image.data[offset] = image.data[offset + 1] = image.data[offset + 2] = gray;
  }
  if (high - low < 8) throw new Error("Draw a digit or choose a non-blank image first.");
  ctx.putImageData(image, 0, 0);
  return {canvas, pixels, width};
}

// OCR text is retained verbatim. Never turn O into 0 or discard unwanted characters.
export function digitResult(text) {
  const accepted = /^[0-9]$/.test(text);
  return {ocr: true, accepted, rawText: text, label: accepted ? text : "—",
    digit: accepted ? Number(text) : null, scores: null, logits: null};
}

export function createDigitReader(announce, timeout = 240000) {
  let worker, pending, timer, sequence = 0;
  function stop(message = "Digit reading cancelled. You can try again.") {
    worker?.terminate(); worker = null;
    clearTimeout(timer);
    if (pending) {const task = pending; pending = null; task.reject(new Error(message));}
  }
  async function read(source, reader, profile) {
    if (!DIGIT_READERS[reader]?.model || !["standard", "precise"].includes(profile)) throw new Error("Unknown digit reader or quality.");
    if (pending) throw new Error("A digit reading is already running.");
    const identity = DIGIT_READERS[reader], captcha = identity.engine === "ddddocr";
    if (captcha) profile = "standard";
    let prepared, pixels, width;
    if (captcha) {const input = prepareCaptcha(source); prepared = input.canvas; pixels = input.pixels; width = input.width;}
    else {try {prepared = prepareWord(source);} catch {throw new Error("Draw a digit or choose a non-blank image first.");}}
    const image = captcha ? null : prepared.toDataURL("image/png");
    announce(`Loading ${identity.name}. First use downloads about ${identity.download_mb || (profile === "precise" ? "250" : "65")} MB plus the runtime. Your image stays on this device…`);
    const output = await new Promise((resolve, reject) => {
      const id = ++sequence;
      pending = {id, resolve, reject};
      timer = setTimeout(() => stop("Digit reading timed out. Try Standard quality or check your connection."), timeout);
      try {
        if (!worker) {
          worker = new Worker(new URL("./digit-reader-worker.js?v=2", import.meta.url), {type: "module"});
          worker.onmessage = ({data}) => {
            if (!pending || data.id !== pending.id) return;
            if (data.type === "progress") {announce(data.message); return;}
            if (data.type !== "result") {stop(data.message || "Digit reader failed. Try again."); return;}
            clearTimeout(timer);
            const task = pending; pending = null; task.resolve(data);
          };
          worker.onerror = event => {event.preventDefault(); stop("Could not start the digit reader. Check your connection and try again.");};
        }
        worker.postMessage({id, image, pixels, width, reader, profile});
      } catch (error) {stop(error.message);}
    });
    return {result: digitResult(output.text), elapsed: output.elapsed, prepared,
      identity: {...identity, reader, profile,
        precision: captcha || profile === "precise" ? "float32" : "int8",
        decoding: identity.decoding || "greedy", preprocessing: identity.preprocessing || "word-crop-display-v1"}};
  }
  return {read, stop};
}
