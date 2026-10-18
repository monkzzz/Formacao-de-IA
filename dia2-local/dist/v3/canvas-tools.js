// Bounded, pixel-exact undo/redo shared by the character and word canvases.
export function createDrawingTools(canvas, {prefix, background, penWidth, eraserWidth, onRestore, onDraw}) {
  const context = canvas.getContext("2d", {willReadFrequently: true});
  const button = name => document.getElementById(`${prefix}-${name}`);
  let past = [], future = [], tool = "pen", disabled = false;
  let eraseWidth = eraserWidth;
  let activePointer = null, previousPoint = null;
  const brush = () => ({color: tool === "eraser" ? background : (background === "white" ? "#14251d" : "white"),
    width: tool === "eraser" ? eraseWidth : penWidth, eraser: tool === "eraser"});
  function endStroke() {
    const pointer = activePointer;
    activePointer = null; previousPoint = null;
    if (pointer !== null && canvas.hasPointerCapture(pointer)) canvas.releasePointerCapture(pointer);
  }
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
  // Opt in so existing consumers with their own drawing handlers remain compatible.
  if (onDraw) {
    const point = event => {
      const rect = canvas.getBoundingClientRect();
      return [(event.clientX - rect.left) * canvas.width / rect.width,
        (event.clientY - rect.top) * canvas.height / rect.height];
    };
    canvas.addEventListener("pointerdown", event => {
      if (disabled || activePointer !== null || event.button !== 0) return;
      event.preventDefault(); canvas.setPointerCapture(event.pointerId);
      snapshot(); activePointer = event.pointerId; previousPoint = point(event);
      const currentBrush = brush();
      onDraw(currentBrush);
      context.fillStyle = currentBrush.color;
      if (currentBrush.eraser) {
        context.fillRect(previousPoint[0] - currentBrush.width / 2,
          previousPoint[1] - currentBrush.width / 2, currentBrush.width, currentBrush.width);
      } else {
        context.beginPath(); context.arc(...previousPoint, currentBrush.width / 2, 0, Math.PI * 2); context.fill();
      }
    });
    canvas.addEventListener("pointermove", event => {
      if (disabled || event.pointerId !== activePointer) return;
      event.preventDefault();
      const current = point(event), currentBrush = brush();
      context.strokeStyle = currentBrush.color; context.lineWidth = currentBrush.width;
      context.lineCap = currentBrush.eraser ? "square" : "round"; context.lineJoin = "round";
      context.beginPath(); context.moveTo(...previousPoint); context.lineTo(...current); context.stroke();
      previousPoint = current;
    });
    for (const name of ["pointerup", "pointercancel", "lostpointercapture"]) {
      canvas.addEventListener(name, event => {if (event.pointerId === activePointer) endStroke();});
    }
  }
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
    endStroke();
    remember(to, capture()); context.putImageData(from.pop(), 0, 0);
    onRestore?.(); controls();
  });
  blank(); controls();
  return {
    snapshot,
    clear() {endStroke(); if (snapshot()) blank();},
    reset() {endStroke(); past = []; future = []; blank(); controls();},
    setDisabled(value) {disabled = value; if (disabled) endStroke(); controls();},
    get brush() {return brush();},
  };
}
