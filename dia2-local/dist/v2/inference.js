import {PREPROCESS_VERSION} from "./preprocess.js";

const SHAPES = {
  "conv1.weight": [16, 1, 3, 3], "conv1.bias": [16],
  "conv2.weight": [32, 16, 3, 3], "conv2.bias": [32],
  "fc1.weight": [128, 1568], "fc1.bias": [128],
};

export async function loadModel(mode = "digits") {
  if (!["digits", "letters"].includes(mode)) throw new Error("Unknown recognition mode.");
  if (!globalThis.crypto?.subtle) throw new Error("Open the HTTPS version of this page to load the verified model.");
  const labels = mode === "letters" ? Array.from("ABCDEFGHIJKLMNOPQRSTUVWXYZ") : Array.from("0123456789");
  const base = mode === "letters" ? "./model/letters/" : "./model/";
  const response = await fetch(base + "manifest.json?v=letters-1", {cache: "no-store"});
  if (!response.ok) throw new Error(`Cannot load the ${mode} model. Check that its model folder was uploaded.`);
  const manifest = await response.json();
  if (manifest.schema !== 1 || manifest.architecture !== "cnn16-32-128"
      || manifest.preprocessing !== PREPROCESS_VERSION || manifest.dtype !== "float32-le") {
    throw new Error("Model and application contracts do not match.");
  }
  if ((mode === "letters" && manifest.task !== "letters") ||
      (manifest.labels && JSON.stringify(manifest.labels) !== JSON.stringify(labels))) {
    throw new Error("Model labels do not match the selected recognition mode.");
  }
  const weightResponse = await fetch(base + "weights.bin?sha256=" + manifest.sha256, {cache: "no-store"});
  if (!weightResponse.ok) throw new Error("Cannot load the trained weights.");
  const bytes = await weightResponse.arrayBuffer();
  const hash = Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256", bytes)),
    b => b.toString(16).padStart(2, "0")).join("");
  if (bytes.byteLength !== manifest.bytes || hash !== manifest.sha256) {
    throw new Error("Model integrity check failed.");
  }
  const weights = {};
  let expectedOffset = 0;
  const shapes = {...SHAPES, "fc2.weight": [labels.length, 128], "fc2.bias": [labels.length]};
  for (const [name, shape] of Object.entries(shapes)) {
    const tensor = manifest.tensors.find(t => t.name === name);
    const length = shape.reduce((a, b) => a * b, 1);
    if (!tensor || JSON.stringify(tensor.shape) !== JSON.stringify(shape)
        || tensor.length !== length || tensor.offset !== expectedOffset) {
      throw new Error(`Invalid model tensor: ${name}`);
    }
    weights[name] = new Float32Array(bytes, tensor.offset * 4, length);
    if (!weights[name].every(Number.isFinite)) throw new Error("Non-finite model weights.");
    expectedOffset += length;
  }
  if (expectedOffset * 4 !== bytes.byteLength) throw new Error("Unexpected model data.");
  return {manifest, weights, labels, mode};
}

function convRelu(input, side, channels, outChannels, weights, bias) {
  const area = side * side, output = new Float32Array(area * outChannels);
  for (let oc = 0; oc < outChannels; oc++) for (let y = 0; y < side; y++) for (let x = 0; x < side; x++) {
    let sum = bias[oc];
    for (let ic = 0; ic < channels; ic++) for (let ky = 0; ky < 3; ky++) {
      const iy = y + ky - 1;
      if (iy < 0 || iy >= side) continue;
      for (let kx = 0; kx < 3; kx++) {
        const ix = x + kx - 1;
        if (ix >= 0 && ix < side) sum += input[ic * area + iy * side + ix]
          * weights[((oc * channels + ic) * 3 + ky) * 3 + kx];
      }
    }
    output[oc * area + y * side + x] = Math.max(0, sum);
  }
  return output;
}

function pool(input, side, channels) {
  const half = side / 2, output = new Float32Array(channels * half * half);
  for (let c = 0; c < channels; c++) for (let y = 0; y < half; y++) for (let x = 0; x < half; x++) {
    const at = c * side * side + y * 2 * side + x * 2;
    output[c * half * half + y * half + x] = Math.max(input[at], input[at + 1], input[at + side], input[at + side + 1]);
  }
  return output;
}

function dense(input, count, weights, bias, relu) {
  const output = new Float32Array(count);
  for (let o = 0; o < count; o++) {
    let sum = bias[o];
    for (let i = 0; i < input.length; i++) sum += input[i] * weights[o * input.length + i];
    output[o] = relu ? Math.max(0, sum) : sum;
  }
  return output;
}

export function predict(model, input) {
  if (input.length !== 784 || !input.every(v => Number.isFinite(v) && v >= 0 && v <= 1)) {
    throw new Error("Expected 784 finite input pixels in [0, 1].");
  }
  const w = model.weights;
  const first = pool(convRelu(input, 28, 1, 16, w["conv1.weight"], w["conv1.bias"]), 28, 16);
  const second = pool(convRelu(first, 14, 16, 32, w["conv2.weight"], w["conv2.bias"]), 14, 32);
  const hidden = dense(second, 128, w["fc1.weight"], w["fc1.bias"], true);
  const logits = dense(hidden, model.labels.length, w["fc2.weight"], w["fc2.bias"], false);
  const maximum = Math.max(...logits), scores = Array.from(logits, v => Math.exp(v - maximum));
  const total = scores.reduce((a, b) => a + b, 0);
  for (let i = 0; i < scores.length; i++) scores[i] /= total;
  const digit = scores.indexOf(Math.max(...scores));
  return {digit, label: model.labels[digit], scores, logits: Array.from(logits), first, second, hidden};
}
