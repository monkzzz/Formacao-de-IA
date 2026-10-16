const sequence = ["arrowup", "arrowup", "arrowdown", "arrowdown", "arrowleft", "arrowright", "arrowleft", "arrowright", "b", "a"];
let entered = [];
let lastKeyAt = 0;
let previousFocus;

export function openArcade() {
  if (dialog.open) return;
  entered = [];
  previousFocus = document.activeElement;
  setExpanded(matchMedia("(max-width: 700px), (max-height: 500px)").matches);
  dialog.showModal();
  frame.src = new URL("./snes.html", import.meta.url).href;
}

const dialog = document.createElement("dialog");
dialog.className = "konami-dialog";
dialog.setAttribute("aria-label", "Secret SNES arcade");
const heading = document.createElement("h2");
heading.textContent = "You found the secret SNES arcade!";
const frame = document.createElement("iframe");
frame.title = "SNES emulator and local ROM picker";
frame.allow = "autoplay; fullscreen; gamepad";
frame.setAttribute("allowfullscreen", "");
const close = document.createElement("button");
const expand = document.createElement("button");
expand.type = "button";
function setExpanded(expanded) {
  dialog.classList.toggle("is-expanded", expanded);
  expand.textContent = expanded ? "Exit expanded view" : "Expand game";
  expand.setAttribute("aria-pressed", String(expanded));
}
setExpanded(false);
expand.addEventListener("click", async () => {
  const expanded = !dialog.classList.contains("is-expanded");
  setExpanded(expanded);
  if (expanded && document.fullscreenEnabled && dialog.requestFullscreen) {
    try { await dialog.requestFullscreen(); } catch { /* Browser-sized view remains available. */ }
  } else if (!expanded && document.fullscreenElement === dialog) {
    try { await document.exitFullscreen(); } catch { /* Preserve the usable dialog. */ }
  }
});
close.type = "button";
close.textContent = "Back to the lab";
close.addEventListener("click", () => dialog.close());
const toolbar = document.createElement("div");
toolbar.className = "konami-toolbar";
toolbar.append(expand, close);
dialog.append(heading, toolbar, frame);
dialog.addEventListener("close", () => {
  // Destroy the frame to stop CPU use, audio and game input on exit.
  frame.src = "about:blank";
  frame.blur();
  previousFocus?.focus({preventScroll: true});
  if (document.fullscreenElement === dialog) document.exitFullscreen().catch(() => {});
});
window.addEventListener("message", event => {
  if (event.origin !== location.origin || event.source !== frame.contentWindow) return;
  if (event.data === "snes-close") dialog.close();
  if (event.data === "snes-focus" && dialog.open) {
    frame.focus({preventScroll: true});
    frame.contentDocument?.querySelector("#game canvas")?.focus({preventScroll: true});
  }
});
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
    openArcade();
  }
});
