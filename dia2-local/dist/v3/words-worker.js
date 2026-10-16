// Model execution stays in this worker; image pixels never leave the browser.
const MODEL = "Xenova/trocr-small-handwritten";
const REVISION = "2432e24d184b1d964d07ed04f5d9e21d31a59141";
let recognizer;

self.onmessage = async ({data}) => {
  const {id, image} = data;
  try {
    if (!recognizer) {
      const {pipeline, env} = await import("https://cdn.jsdelivr.net/npm/@xenova/transformers@2.17.2/dist/transformers.min.js");
      env.allowLocalModels = false;
      // Single-thread WASM works on ordinary static hosting without COOP/COEP.
      env.backends.onnx.wasm.numThreads = 1;
      recognizer = await pipeline("image-to-text", MODEL, {
        revision: REVISION, quantized: true,
        progress_callback: progress => {
          if (progress.status === "progress") self.postMessage({id, type: "progress",
            message: `Loading handwriting model: ${progress.file} (${Math.round(progress.progress)}%)`});
        },
      });
    }
    self.postMessage({id, type: "progress", message: "Reading your handwriting on this device…"});
    const start = performance.now();
    const output = await recognizer(image, {max_new_tokens: 64, num_beams: 1});
    self.postMessage({id, type: "result", text: output[0]?.generated_text?.trim() || "",
      elapsed: performance.now() - start, model: MODEL, revision: REVISION});
  } catch (error) {
    self.postMessage({id, type: "error", message: error.message || String(error)});
  }
};
