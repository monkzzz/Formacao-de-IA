import {DIGIT_READERS} from "./digit-readers.js?v=3";
import {singleDigitScores} from "./ctc-digits.js?v=1";

let recognizer, loaded;
let captchaSession, ort, captchaReader, charsets;

export function decodeCTC(data, dimensions, charset) {
  if (dimensions.length !== 3 || dimensions[2] !== charset.length ||
      !(dimensions[0] === 1 || dimensions[1] === 1)) throw new Error("Unexpected CAPTCHA model output.");
  const steps = dimensions[0] === 1 ? dimensions[1] : dimensions[0], classes = charset.length;
  let previous = 0, text = "";
  for (let t = 0; t < steps; t++) {
    let best = 0;
    for (let k = 1; k < classes; k++) if (data[t * classes + k] > data[t * classes + best]) best = k;
    if (best !== previous && best !== 0) text += charset[best];
    previous = best;
  }
  return text;
}

async function captcha(data, identity) {
  const {id, reader, pixels, width} = data;
  const sourceReader = identity.charset_reader || reader;
  if (!ort) {
    ort = await import("https://cdn.jsdelivr.net/npm/onnxruntime-web@1.20.1/dist/ort.wasm.min.mjs");
    ort.env.wasm.numThreads = 1;
    ort.env.wasm.wasmPaths = "https://cdn.jsdelivr.net/npm/onnxruntime-web@1.20.1/dist/";
  }
  if (!charsets) {
    const response = await fetch(new URL("./ddddocr-charsets.json?v=1", import.meta.url));
    if (!response.ok) throw new Error("Cannot load the CAPTCHA character table.");
    charsets = await response.json();
  }
  if (!captchaSession || captchaReader !== reader) {
    if (captchaSession) await captchaSession.release();
    captchaSession = null;
    self.postMessage({id, type: "progress", message: `Downloading ${identity.name} (${identity.download_mb} MB)…`});
    const response = await fetch(`https://raw.githubusercontent.com/sml2h3/ddddocr/${identity.revision}/ddddocr/${sourceReader === "ddddocr" ? "common.onnx" : "common_old.onnx"}`);
    if (!response.ok) throw new Error("Could not download the CAPTCHA model. Check your connection and try again.");
    const bytes = await response.arrayBuffer();
    const hash = Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256", bytes)), b => b.toString(16).padStart(2, "0")).join("");
    if (hash !== identity.sha256) throw new Error("CAPTCHA model integrity check failed.");
    self.postMessage({id, type: "progress", message: "Preparing the CAPTCHA model on this device…"});
    captchaSession = await ort.InferenceSession.create(bytes, {executionProviders: ["wasm"], logSeverityLevel: 3});
    captchaReader = reader;
  }
  if (!(pixels instanceof Float32Array) || pixels.length !== width * 64 || !pixels.every(v => Number.isFinite(v) && v >= -1 && v <= 1)) throw new Error("Invalid CAPTCHA pixels.");
  const start = performance.now();
  const outputs = await captchaSession.run({[captchaSession.inputNames[0]]: new ort.Tensor("float32", pixels, [1, 1, 64, width])});
  const output = outputs[captchaSession.outputNames[0]];
  const raw_text = decodeCTC(output.data, output.dims, charsets[sourceReader]);
  if (identity.single_digit) {
    const scores = singleDigitScores(output.data, output.dims, charsets[sourceReader]);
    return {text: String(scores.indexOf(Math.max(...scores))), raw_text, scores, elapsed: performance.now() - start};
  }
  return {text: raw_text, elapsed: performance.now() - start};
}
self.onmessage = async ({data}) => {
  const {id, image, reader, profile} = data;
  try {
    const identity = DIGIT_READERS[reader];
    if (!identity?.model || !["standard", "precise"].includes(profile)) throw new Error("Unknown digit reader or quality.");
    if (identity.engine === "ddddocr") {
      const output = await captcha(data, identity);
      self.postMessage({id, type: "result", ...output});
      return;
    }
    const key = reader + ":" + profile;
    if (recognizer && loaded !== key) {await recognizer.dispose(); recognizer = null;}
    if (!recognizer) {
      const {pipeline, env} = await import("https://cdn.jsdelivr.net/npm/@xenova/transformers@2.17.2/dist/transformers.min.js");
      env.allowLocalModels = false;
      env.backends.onnx.wasm.numThreads = 1;
      recognizer = await pipeline("image-to-text", identity.model, {
        revision: identity.revision, quantized: profile === "standard",
        progress_callback: progress => {
          if (progress.status === "progress") self.postMessage({id, type: "progress",
            message: `Loading digit reader: ${progress.file} (${Math.round(progress.progress)}%)`});
        },
      });
      loaded = key;
    }
    self.postMessage({id, type: "progress", message: "Reading the digit on this device…"});
    const start = performance.now();
    const output = await recognizer(image, {max_new_tokens: 16, num_beams: 1});
    self.postMessage({id, type: "result", text: output[0]?.generated_text ?? "", elapsed: performance.now() - start});
  } catch (error) {self.postMessage({id, type: "error", message: error.message || String(error)});}
};
