import {answerQuestion} from "./helper-knowledge.js?v=3.12.0";
import {openArcade} from "./konami.js?v=5";

const launcher = document.getElementById("helper-launcher");
const panel = document.getElementById("scopedog");
const input = document.getElementById("helper-question");
const messages = document.getElementById("helper-messages");
const actions = {
  workspace: ["Go to the workspace", "workspace"],
  network: ["Explore the real feature maps", "network"],
  model: ["See model details", "model"],
  uploads: ["Go to image results", "uploads-section"],
  wordMetrics: ["See word test details", "word-benchmark-details"],
};

function setOpen(open) {
  panel.hidden = !open;
  launcher.setAttribute("aria-expanded", String(open));
  if (open) {input.focus(); messages.scrollTop = messages.scrollHeight;}
  else launcher.focus();
}

function appendMessage(speaker, text, suggestions = []) {
  // Use text nodes, including for user input: never render question text as HTML.
  const message = document.createElement("div");
  message.className = "helper-message" + (speaker === "You" ? " is-user" : "");
  const label = document.createElement("span"); label.className = "helper-speaker"; label.textContent = speaker;
  const body = document.createElement("p"); body.textContent = text;
  message.append(label, body);
  if (suggestions.length) {
    const links = document.createElement("div"); links.className = "helper-actions";
    for (const action of suggestions) {
      const [title, id] = actions[action];
      const button = document.createElement("button"); button.type = "button"; button.textContent = title;
      button.addEventListener("click", () => {
        const target = document.getElementById(id);
        if (!target) {appendMessage("Scopedog", "Refresh this page to see the latest benchmark details."); return;}
        if (target.hidden) {
          appendMessage("Scopedog", id === "network" || id === "model"
            ? "Switch to Digits or Letters to inspect the CNN models and their real activations. Words has its own model details below the writing workspace."
            : "Choose an image first to start your collection.");
          return;
        }
        if (target instanceof HTMLDetailsElement) target.open = true;
        setOpen(false);
        target.scrollIntoView({block: "start", behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth"});
        if (!target.hasAttribute("tabindex")) target.setAttribute("tabindex", "-1");
        target.focus({preventScroll: true});
      });
      links.append(button);
    }
    message.append(links);
  }
  messages.append(message);
  // Bound the live session so extended use does not grow the page indefinitely.
  while (messages.children.length > 60) messages.firstElementChild.remove();
  messages.scrollTop = messages.scrollHeight;
}

function ask(question) {
  question = question.trim().slice(0, 400);
  if (!question) return;
  appendMessage("You", question);
  if (question.toLowerCase().replace(/\s+/g, " ") === "up up down down left right left right b a") {
    appendMessage("Scopedog", "Secret unlocked! Tap the game to play. Use the emulator menu for touch controls.");
    input.blur();
    setOpen(false);
    openArcade();
    return true;
  }
  const state = window.digitLab?.state;
  const benchmark = document.getElementById("benchmark-words");
  const response = answerQuestion(question, {
    mode: state?.mode || "digits",
    digitReader: document.getElementById("digit-reader")?.value || "local",
    predicted: state?.mode === "words" ? window.digitLab.wordsContext().predicted : document.getElementById("predicted").textContent.trim(),
    confidence: document.getElementById("confidence").textContent.trim(),
    wordBenchmark: benchmark ? {score: document.getElementById("word-accuracy").textContent.trim(),
      lines: benchmark.dataset.lines, words: benchmark.dataset.words, wer: benchmark.dataset.wer,
      cer: benchmark.dataset.cer, exact: benchmark.dataset.exact} : null,
  });
  appendMessage("Scopedog", response.text, response.actions);
}

launcher.hidden = false;
launcher.addEventListener("click", () => setOpen(panel.hidden));
document.getElementById("helper-close").addEventListener("click", () => setOpen(false));
document.addEventListener("keydown", event => {
  if (event.key === "Escape" && !panel.hidden) {event.preventDefault(); setOpen(false);}
});
document.getElementById("helper-form").addEventListener("submit", event => {
  event.preventDefault();
  const question = input.value;
  input.value = "";
  if (!ask(question)) input.focus();
});
for (const [label, question] of [["Get started", "How do I use the page?"], ["How it works", "How does it work?"],
  ["My prediction", "Explain this prediction"], ["Model scores", "What do model scores mean?"]]) {
  const button = document.createElement("button"); button.type = "button"; button.textContent = label;
  button.addEventListener("click", () => ask(question)); document.getElementById("helper-topics").append(button);
}
appendMessage("Scopedog", "Hi, I’m Scopedog. Need a hand with the lab? Ask how to draw or upload a character, what a prediction means, or how the neural network learns. Choose a topic below or type a question.");
