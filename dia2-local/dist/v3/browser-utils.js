// Browser I/O shared by the development site and participant-trained submission.
export async function imageCanvas(file, {
  maxBytes = 30 * 1024 * 1024, maxPixels = 16000000, maxSide = Infinity,
  allowUnknownType = true,
  sizeError = "Image exceeds the 30 MB limit.",
  dimensionsError = "Image exceeds 16 million pixels.",
  typeError = "Use PNG, JPEG, or WebP images.",
} = {}) {
  if (file.size > maxBytes) throw new Error(sizeError);
  if ((!file.type && !allowUnknownType) ||
      (file.type && !["image/png", "image/jpeg", "image/webp"].includes(file.type))) throw new Error(typeError);
  const bitmap = await createImageBitmap(file);
  try {
    if (bitmap.width * bitmap.height > maxPixels || bitmap.width > maxSide || bitmap.height > maxSide) {
      throw new Error(dimensionsError);
    }
    const canvas = document.createElement("canvas");
    canvas.width = bitmap.width; canvas.height = bitmap.height;
    canvas.getContext("2d").drawImage(bitmap, 0, 0);
    return canvas;
  } finally {bitmap.close();}
}

export function imagePreview(file, alt) {
  const image = document.createElement("img"), url = URL.createObjectURL(file);
  const release = () => URL.revokeObjectURL(url);
  image.addEventListener("load", release, {once: true});
  image.addEventListener("error", release, {once: true});
  image.alt = alt; image.src = url;
  return image;
}

export function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob), link = document.createElement("a");
  try {link.href = url; link.download = filename; link.click();}
  finally {setTimeout(() => URL.revokeObjectURL(url), 1000);}
}
