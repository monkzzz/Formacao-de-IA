// Bounded, pixel-exact undo/redo shared by the character and word canvases.
export function createDrawingTools(canvas, {prefix, background, penWidth, eraserWidth, onRestore}) {
  const context = canvas.getContext("2d", {willReadFrequently: true});
  const button = name => document.getElementById(`${prefix}-${name}`);
  let past = [], future = [], tool = "pen", disabled = false;
  let eraseWidth = eraserWidth;
  const sizeLabel = document.createElement("label"); sizeLabel.className = "eraser-size";
  sizeLabel.append("Eraser size ");
  const size = document.createElement("input"); size.type = "range"; size.min = "8"; size.max = "100";
  size.id = `${prefix}-eraser-size`;
  size.value = String(eraseWidth); size.setAttribute("aria-label", "Eraser size");
  const sizeValue = document.createElement("output"); sizeValue.textContent = String(eraseWidth);
  sizeLabel.append(size, sizeValue); button("pen").parentElement.append(sizeLabel);
  const capture = () => context.getImageData(0, 0, canvas.width, canvas.height);
  function controls() {
    button("pen").disabled = button("eraser").disabled = disabled;
    button("undo").disabled = disabled || !past.length;
    button("redo").disabled = disabled || !future.length;
    for (const name of ["pen", "eraser"]) button(name).setAttribute("aria-pressed", String(tool === name));
    canvas.dataset.tool = tool;
    sizeLabel.hidden = tool !== "eraser"; size.disabled = disabled;
    if (tool === "eraser") {
      const side = Math.max(8, Math.min(96, Math.round(eraseWidth * canvas.getBoundingClientRect().width / canvas.width)));
      const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${side + 4}" height="${side + 4}"><rect x="1" y="1" width="${side + 2}" height="${side + 2}" fill="none" stroke="white" stroke-width="3"/><rect x="2" y="2" width="${side}" height="${side}" fill="none" stroke="black"/></svg>`;
      canvas.style.cursor = `url("data:image/svg+xml,${encodeURIComponent(svg)}") ${Math.floor((side + 4) / 2)} ${Math.floor((side + 4) / 2)}, cell`;
    } else canvas.style.cursor = "crosshair";
  }
  function remember(stack, image) {
    stack.push(image);
    if (stack.length > 20) stack.shift();
  }
  function snapshot() {
    if (disabled) return false;
    remember(past, capture()); future = []; controls(); return true;
  }
  function blank() {
    context.fillStyle = background;
    context.fillRect(0, 0, canvas.width, canvas.height);
  }
  for (const name of ["pen", "eraser"]) button(name).addEventListener("click", () => {
    if (disabled) return;
    tool = name; controls();
  });
  size.addEventListener("input", () => {eraseWidth = Number(size.value); sizeValue.textContent = size.value; controls();});
  canvas.tabIndex = 0;
  canvas.addEventListener("pointerdown", () => canvas.focus({preventScroll: true}));
  canvas.addEventListener("keydown", event => {
    if (!(event.ctrlKey || event.metaKey) || disabled) return;
    const key = event.key.toLowerCase();
    if (key === "z" || key === "y") {
      event.preventDefault(); button(key === "y" || event.shiftKey ? "redo" : "undo").click();
    }
  });
  for (const name of ["undo", "redo"]) button(name).addEventListener("click", () => {
    const from = name === "undo" ? past : future, to = name === "undo" ? future : past;
    if (disabled || !from.length) return;
    remember(to, capture()); context.putImageData(from.pop(), 0, 0);
    onRestore?.(); controls();
  });
  blank(); controls();
  return {
    snapshot,
    clear() {if (snapshot()) blank();},
    reset() {past = []; future = []; blank(); controls();},
    setDisabled(value) {disabled = value; controls();},
    get brush() {return {color: tool === "eraser" ? background : (background === "white" ? "#14251d" : "white"),
      width: tool === "eraser" ? eraseWidth : penWidth, eraser: tool === "eraser"};},
  };
}
