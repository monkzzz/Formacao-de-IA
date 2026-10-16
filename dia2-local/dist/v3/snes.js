const input = document.getElementById("rom");
const play = document.getElementById("play");
const status = document.getElementById("status");
const reset = document.getElementById("reset");
let romUrl;
input.addEventListener("change", () => {
  const file = input.files[0];
  const valid = file && /\.(sfc|smc)$/i.test(file.name) && file.size > 0 && file.size <= 16 * 1024 * 1024;
  play.disabled = !valid;
  status.textContent = valid ? "Ready. Press Play game to start." : "Choose a non-empty .sfc or .smc ROM up to 16 MB.";
});
function startGame(url, name) {
  play.disabled = true;
  document.getElementById("picker").hidden = true;
  document.getElementById("game").hidden = false;
  reset.hidden = false;
  status.textContent = "Loading Zelda… If loading fails, stop and try again.";
  Object.assign(window, {
    EJS_player: "#game",
    EJS_core: "snes9x",
    EJS_gameUrl: url,
    EJS_gameName: name,
    EJS_pathtodata: "https://cdn.emulatorjs.org/stable/data/",
    EJS_startOnLoaded: true,
    EJS_threads: false,
    EJS_onGameStart: () => { status.textContent = "Playing. Use the emulator menu for controls and save states. Escape returns to the lab."; }
  });
  const loader = document.createElement("script");
  loader.src = window.EJS_pathtodata + "loader.js";
  loader.onerror = () => { status.textContent = "Could not load the emulator. Check your connection, then stop and try again."; };
  document.body.append(loader);
}
play.addEventListener("click", () => {
  const file = input.files[0];
  if (play.disabled || !file) return;
  romUrl = URL.createObjectURL(file);
  startGame(romUrl, file.name.replace(/\.(sfc|smc)$/i, ""));
});
reset.addEventListener("click", () => { location.search = "?choose=1"; });
window.addEventListener("pagehide", () => { if (romUrl) URL.revokeObjectURL(romUrl); });
document.addEventListener("keydown", event => {
  if (event.key === "Escape") window.parent.postMessage("snes-close", location.origin);
});
if (!new URLSearchParams(location.search).has("choose")) {
  const url = new URL("../roms/zelda.sfc", import.meta.url).href;
  fetch(url, {method: "HEAD"}).then(response => {
    if (!response.ok) throw new Error("ROM missing");
    startGame(url, "The Legend of Zelda - A Link to the Past");
  }).catch(() => { status.textContent = "Zelda ROM unavailable. Choose a local ROM to play."; });
}
