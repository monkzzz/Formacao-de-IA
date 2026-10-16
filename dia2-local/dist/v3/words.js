const $ = id => document.getElementById(id);

// A separate, full-resolution pipeline: never squeeze a word into the CNN's 28×28 input.
export function prepareWord(source) {
  const width = source.width, height = source.height;
  const context = source.getContext("2d", {willReadFrequently: true});
  const pixels = context.getImageData(0, 0, width, height).data;
  const gray = i => {
    const alpha = pixels[i + 3] / 255;
    return (.299 * pixels[i] + .587 * pixels[i + 1] + .114 * pixels[i + 2]) * alpha + 255 * (1 - alpha);
  };
  let border = 0, count = 0;
  for (let y = 0; y < height; y++) for (let x = 0; x < width; x++) {
    if (x === 0 || y === 0 || x === width - 1 || y === height - 1) {border += gray((y * width + x) * 4); count++;}
  }
  const darkBackground = border / count < 128;
  let left = width, top = height, right = -1, bottom = -1, ink = 0;
  for (let y = 0; y < height; y++) for (let x = 0; x < width; x++) {
    const value = gray((y * width + x) * 4);
    if (darkBackground ? value > 160 : value < 150) {
      left = Math.min(left, x); right = Math.max(right, x);
      top = Math.min(top, y); bottom = Math.max(bottom, y); ink++;
    }
  }
  if (ink < 12 || right - left < 3 || bottom - top < 3) throw new Error("Write a word or choose a non-blank image first.");
  const cropWidth = right - left + 1, cropHeight = bottom - top + 1;
  const scale = Math.min(1, 1400 / cropWidth, 320 / cropHeight);
  const padding = Math.max(8, Math.round(cropHeight * scale * .15));
  const prepared = document.createElement("canvas");
  prepared.width = Math.ceil(cropWidth * scale) + 2 * padding;
  prepared.height = Math.ceil(cropHeight * scale) + 2 * padding;
  const out = prepared.getContext("2d");
  out.fillStyle = "white"; out.fillRect(0, 0, prepared.width, prepared.height);
  const crop = document.createElement("canvas"); crop.width = cropWidth; crop.height = cropHeight;
  const cropContext = crop.getContext("2d"), normalized = cropContext.createImageData(cropWidth, cropHeight);
  for (let y = 0; y < cropHeight; y++) for (let x = 0; x < cropWidth; x++) {
    const value = gray(((top + y) * width + left + x) * 4);
    const v = darkBackground ? 255 - value : value;
    normalized.data.set([v, v, v, 255], (y * cropWidth + x) * 4);
  }
  cropContext.putImageData(normalized, 0, 0);
  out.drawImage(crop, padding, padding, cropWidth * scale, cropHeight * scale);
  return prepared;
}

export function createWordsWorkspace() {
  const canvas = $("word-drawing"), context = canvas.getContext("2d", {willReadFrequently: true});
  let worker, pending, timer, sequence = 0, drawing = false, previous, busy = false, active = false;
  let originalText = "", sourceName = "Your drawing", metadata = null;
  const announce = (message, error = false) => {
    $("word-status").textContent = message; $("word-status").classList.toggle("error", error);
  };
  function controls() {
    for (const id of ["word-read", "word-clear", "word-file"]) $(id).disabled = busy;
    $("word-cancel").hidden = !busy;
    $("word-text").disabled = busy;
    for (const id of ["word-copy", "word-download"]) $(id).disabled = busy || !$("word-text").value.trim();
    $("words-workspace").setAttribute("aria-busy", String(busy));
  }
  function clearResult() {
    $("word-text").value = ""; $("word-raw").textContent = "No transcription yet.";
    $("word-timing").textContent = "READY WHEN YOU ARE";
    $("word-preview").hidden = true; $("word-preview").removeAttribute("src");
    originalText = ""; metadata = null; controls();
  }
  function clearCanvas() {
    drawing = false; previous = null;
    context.fillStyle = "white"; context.fillRect(0, 0, canvas.width, canvas.height);
    sourceName = "Your drawing";
  }
  function stopWorker(error) {
    worker?.terminate(); worker = null;
    if (pending) {const {reject} = pending; pending = null; clearTimeout(timer); reject(error);}
  }
  function recognize(image) {
    return new Promise((resolve, reject) => {
      const id = ++sequence;
      pending = {id, resolve, reject};
      timer = setTimeout(() => stopWorker(new Error("Reading timed out. Check your connection and try again, or use a shorter word.")), 240000);
      try {
        if (!worker) {
          worker = new Worker(new URL("./words-worker.js?v=words-1", import.meta.url), {type: "module"});
          worker.onmessage = ({data}) => {
            if (!pending || data.id !== pending.id) return;
            if (data.type === "progress") {announce(data.message); return;}
            clearTimeout(timer);
            const task = pending; pending = null;
            if (data.type === "result") task.resolve(data);
            else {
              worker.terminate(); worker = null;
              task.reject(new Error("Could not read the word. Check your connection to the model downloads and try again. " + data.message));
            }
          };
          worker.onerror = event => {
            event.preventDefault(); stopWorker(new Error("The word reader could not start. Check your internet connection and try again."));
          };
        }
        worker.postMessage({id, image});
      } catch (error) {stopWorker(error);}
    });
  }
  async function read() {
    if (busy) return;
    let prepared;
    try {prepared = prepareWord(canvas);} catch (error) {announce(error.message, true); return;}
    clearResult(); busy = true; drawing = false; controls();
    $("word-preview").src = prepared.toDataURL("image/png"); $("word-preview").hidden = false;
    announce("Preparing the word reader. First use downloads about 65 MB of model weights plus the runtime; this may take a minute…");
    try {
      const result = await recognize(prepared.toDataURL("image/png"));
      if (!result.text) throw new Error("No text was recognized. Try a clearer word with a little space around it.");
      originalText = result.text; metadata = {model: result.model, revision: result.revision, source: sourceName};
      $("word-text").value = result.text; $("word-raw").textContent = result.text;
      $("word-timing").textContent = `${(result.elapsed / 1000).toFixed(1)} S / READING`;
      announce("Transcription ready. Check the text, make any corrections, then copy or download it.");
    } catch (error) {announce(error.message, true);}
    finally {busy = false; controls();}
  }
  function point(event) {
    const rect = canvas.getBoundingClientRect();
    return [(event.clientX - rect.left) * canvas.width / rect.width, (event.clientY - rect.top) * canvas.height / rect.height];
  }
  canvas.addEventListener("pointerdown", event => {
    if (busy) return;
    event.preventDefault(); canvas.setPointerCapture(event.pointerId);
    if (sourceName !== "Your drawing") clearCanvas();
    clearResult(); drawing = true; previous = point(event);
    context.fillStyle = "#14251d"; context.beginPath(); context.arc(...previous, 3, 0, 2 * Math.PI); context.fill();
  });
  canvas.addEventListener("pointermove", event => {
    if (!drawing || busy) return;
    const current = point(event);
    context.strokeStyle = "#14251d"; context.lineWidth = 6; context.lineCap = "round"; context.lineJoin = "round";
    context.beginPath(); context.moveTo(...previous); context.lineTo(...current); context.stroke(); previous = current;
  });
  for (const type of ["pointerup", "pointercancel", "lostpointercapture"]) canvas.addEventListener(type, () => {drawing = false; previous = null;});
  $("word-read").addEventListener("click", read);
  $("word-clear").addEventListener("click", () => {clearCanvas(); clearResult(); announce("Canvas cleared. Write one word or a short line.");});
  $("word-cancel").addEventListener("click", () => stopWorker(new Error("Reading cancelled. You can try again or switch modes.")));
  $("word-file").addEventListener("change", async event => {
    const file = event.target.files[0]; event.target.value = "";
    if (!file || busy) return;
    busy = true; controls(); clearResult();
    try {
      if (file.size > 30 * 1024 * 1024) throw new Error("Image exceeds the 30 MB limit.");
      if (file.type && !["image/png", "image/jpeg", "image/webp"].includes(file.type)) throw new Error("Use PNG, JPEG, or WebP images.");
      const bitmap = await createImageBitmap(file);
      try {
        if (bitmap.width * bitmap.height > 16000000) throw new Error("Image exceeds 16 million pixels.");
        const source = document.createElement("canvas"); source.width = bitmap.width; source.height = bitmap.height;
        source.getContext("2d").drawImage(bitmap, 0, 0);
        const prepared = prepareWord(source);
        clearCanvas();
        const scale = Math.min((canvas.width - 32) / prepared.width, (canvas.height - 32) / prepared.height);
        context.drawImage(prepared, (canvas.width - prepared.width * scale) / 2,
          (canvas.height - prepared.height * scale) / 2, prepared.width * scale, prepared.height * scale);
        sourceName = file.name;
      } finally {bitmap.close();}
    } catch (error) {announce(error.message, true); return;}
    finally {busy = false; controls();}
    await read();
  });
  $("word-text").addEventListener("input", controls);
  $("word-copy").addEventListener("click", async () => {
    try {await navigator.clipboard.writeText($("word-text").value); announce("Text copied to your clipboard.");}
    catch {$("word-text").focus(); $("word-text").select(); announce("Select and copy the text using your keyboard or device menu.");}
  });
  $("word-download").addEventListener("click", () => {
    const url = URL.createObjectURL(new Blob([$("word-text").value], {type: "text/plain;charset=utf-8"}));
    const link = document.createElement("a"); link.href = url; link.download = "digitlab-handwriting.txt"; link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
  clearCanvas(); controls();
  return {
    activate(value) {
      active = value;
      if (!active && busy) stopWorker(new Error("Reading cancelled when leaving Words mode."));
    },
    context: () => ({predicted: $("word-text").value, originalText, metadata, busy, active}),
  };
}
