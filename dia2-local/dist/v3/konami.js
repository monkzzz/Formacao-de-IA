const sequence = ["arrowup", "arrowup", "arrowdown", "arrowdown", "arrowleft", "arrowright", "arrowleft", "arrowright", "b", "a"];
let entered = [];
let lastKeyAt = 0;

const dialog = document.createElement("dialog");
dialog.className = "konami-dialog";
dialog.setAttribute("aria-label", "Congratulations! You found the secret!");
const image = document.createElement("img");
image.src = new URL("../assets/konami-congratulations.svg", import.meta.url).href;
image.alt = "Congratulations! You found the secret! Konami code unlocked. Stay curious, keep exploring. Digit Lab.";
image.width = 800;
image.height = 560;
const close = document.createElement("button");
close.type = "button";
close.textContent = "Back to the lab";
close.addEventListener("click", () => dialog.close());
dialog.append(image, close);
document.body.append(dialog);
dialog.addEventListener("click", event => {
  if (event.target === dialog) {
    const bounds = dialog.getBoundingClientRect();
    if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
  }
});

document.addEventListener("keydown", event => {
  if (event.repeat) return;
  if (dialog.open || event.ctrlKey || event.metaKey || event.altKey ||
      event.target.closest?.("input, textarea, select, [contenteditable]:not([contenteditable='false'])")) {
    entered = [];
    return;
  }
  const now = Date.now();
  if (now - lastKeyAt > 5000) entered = [];
  lastKeyAt = now;
  entered.push(event.key.toLowerCase());
  // Retain the longest suffix that is also a prefix, including overlapping starts.
  while (entered.length && !entered.every((key, index) => key === sequence[index])) entered.shift();
  if (entered.length === sequence.length) {
    entered = [];
    dialog.showModal();
  }
});
