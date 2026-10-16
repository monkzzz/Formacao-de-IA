import {prepareWord} from "./words.js?v=3.2.0";

export const DIGIT_READERS = {
  local: {name: "Digit Lab residual CNN", trained_by_project: true},
  printed: {name: "TrOCR Small · printed", model: "Xenova/trocr-small-printed",
    revision: "56c1626ea0b4aab378f3228235be2e824d4256bd", trained_by_project: false},
  handwritten: {name: "TrOCR Small · handwritten", model: "Xenova/trocr-small-handwritten",
    revision: "2432e24d184b1d964d07ed04f5d9e21d31a59141", trained_by_project: false},
};

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
    let prepared;
    try {prepared = prepareWord(source);} catch {throw new Error("Draw a digit or choose a non-blank image first.");}
    const image = prepared.toDataURL("image/png");
    announce(`Loading ${DIGIT_READERS[reader].name}. First use downloads about ${profile === "precise" ? "250" : "65"} MB plus the runtime. Your image stays on this device…`);
    const output = await new Promise((resolve, reject) => {
      const id = ++sequence;
      pending = {id, resolve, reject};
      timer = setTimeout(() => stop("Digit reading timed out. Try Standard quality or check your connection."), timeout);
      try {
        if (!worker) {
          worker = new Worker(new URL("./digit-reader-worker.js?v=1", import.meta.url), {type: "module"});
          worker.onmessage = ({data}) => {
            if (!pending || data.id !== pending.id) return;
            if (data.type === "progress") {announce(data.message); return;}
            if (data.type !== "result") {stop(data.message || "Digit reader failed. Try again."); return;}
            clearTimeout(timer);
            const task = pending; pending = null; task.resolve(data);
          };
          worker.onerror = event => {event.preventDefault(); stop("Could not start the digit reader. Check your connection and try again.");};
        }
        worker.postMessage({id, image, reader, profile});
      } catch (error) {stop(error.message);}
    });
    return {result: digitResult(output.text), elapsed: output.elapsed, prepared,
      identity: {...DIGIT_READERS[reader], reader, profile,
        precision: profile === "precise" ? "float32" : "int8", decoding: "greedy", preprocessing: "word-crop-display-v1"}};
  }
  return {read, stop};
}
