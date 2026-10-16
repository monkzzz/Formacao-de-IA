// Keep in sync with digitlab/preprocess.py; browser/Python parity is tested.
export const PREPROCESS_VERSION = "border-gray-bilinear-com-v1";
export const PREPROCESS_VERSION64 = "border-gray-bilinear-com-64-v1";

export function prepareRGBA(data, width, height, side = 28) {
  if (![28, 64].includes(side)) throw new Error("Supported model input sides are 28 and 64.");
  if (width < 2 || height < 2 || data.length !== width * height * 4) {
    throw new Error("Expected an RGBA image at least 2 by 2 pixels.");
  }
  const gray = new Float64Array(width * height);
  for (let i = 0; i < gray.length; i++) {
    const p = i * 4, a = data[p + 3] / 255;
    gray[i] = (.299 * data[p] + .587 * data[p + 1] + .114 * data[p + 2]) * a + 255 * (1 - a);
  }
  let borderSum = 0, borderCount = 0;
  for (let x = 0; x < width; x++) {
    borderSum += gray[x] + gray[(height - 1) * width + x]; borderCount += 2;
  }
  for (let y = 1; y < height - 1; y++) {
    borderSum += gray[y * width] + gray[y * width + width - 1]; borderCount += 2;
  }
  const background = borderSum / borderCount, ink = new Float64Array(gray.length);
  let contrast = 0;
  for (let i = 0; i < gray.length; i++) {
    ink[i] = Math.abs(gray[i] - background) / 255;
    contrast = Math.max(contrast, ink[i]);
  }
  if (contrast < .12) throw new Error("No visible digit: image is blank or has insufficient contrast.");
  let left = width, right = -1, top = height, bottom = -1;
  for (let y = 0; y < height; y++) for (let x = 0; x < width; x++) {
    const i = y * width + x;
    ink[i] /= contrast;
    if (ink[i] < .06) ink[i] = 0;
    if (ink[i] > .20) {
      left = Math.min(left, x); right = Math.max(right, x);
      top = Math.min(top, y); bottom = Math.max(bottom, y);
    }
  }
  if (right < left) throw new Error("No visible digit.");
  const cw = right - left + 1, ch = bottom - top + 1, scale = (side === 64 ? 48 : 20) / Math.max(cw, ch);
  const rw = Math.max(1, Math.floor(cw * scale + .5)), rh = Math.max(1, Math.floor(ch * scale + .5));
  const resized = new Float64Array(rw * rh);
  let mass = 0, sumX = 0, sumY = 0;
  for (let y = 0; y < rh; y++) for (let x = 0; x < rw; x++) {
    const sy = Math.max(0, Math.min(ch - 1, (y + .5) * ch / rh - .5));
    const sx = Math.max(0, Math.min(cw - 1, (x + .5) * cw / rw - .5));
    const y0 = Math.floor(sy), x0 = Math.floor(sx);
    const y1 = Math.min(y0 + 1, ch - 1), x1 = Math.min(x0 + 1, cw - 1);
    const fy = sy - y0, fx = sx - x0;
    const at = (yy, xx) => ink[(yy + top) * width + xx + left];
    const v = (1 - fy) * ((1 - fx) * at(y0, x0) + fx * at(y0, x1))
      + fy * ((1 - fx) * at(y1, x0) + fx * at(y1, x1));
    resized[y * rw + x] = v; mass += v; sumX += v * x; sumY += v * y;
  }
  if (mass < 1) throw new Error("Too little foreground to classify.");
  const center = (side - 1) / 2;
  const ox = Math.floor(center - sumX / mass + .5), oy = Math.floor(center - sumY / mass + .5);
  const input = new Float32Array(side * side);
  for (let y = 0; y < rh; y++) for (let x = 0; x < rw; x++) {
    if (x + ox >= 0 && x + ox < side && y + oy >= 0 && y + oy < side) {
      input[(y + oy) * side + x + ox] = resized[y * rw + x];
    }
  }
  return input;
}

export function prepareCanvas(canvas, side = 28) {
  return prepareRGBA(canvas.getContext("2d", {willReadFrequently: true})
    .getImageData(0, 0, canvas.width, canvas.height).data, canvas.width, canvas.height, side);
}
