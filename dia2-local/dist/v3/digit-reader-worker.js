import {DIGIT_READERS} from "./digit-readers.js?v=1";

let recognizer, loaded;
self.onmessage = async ({data}) => {
  const {id, image, reader, profile} = data;
  try {
    const identity = DIGIT_READERS[reader];
    if (!identity?.model || !["standard", "precise"].includes(profile)) throw new Error("Unknown digit reader or quality.");
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
