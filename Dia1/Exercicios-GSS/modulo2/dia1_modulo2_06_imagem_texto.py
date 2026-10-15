"""Exercise 6: ask GLM-4.6V about an image and judge what the answer can and cannot claim."""

from __future__ import annotations

import argparse
import textwrap
import threading
import time

import matplotlib.image as mpimg
from matplotlib.backend_bases import MouseEvent

from apoio_linguagem import lm_studio
from apoio_linguagem.imagem_texto import (
    REQUESTS, FallbackVisionRunner, LiveVisionRunner, RecordedVisionRunner, VisionAnswer, VisionRunner,
    available_images, image_path, record_all, request_text,
)
from apoio_linguagem.interface_base import (
    INK, MUTED, ORANGE, STATUS, TEAL, add_buttons, add_footer, create_window, is_headless, run_window,
)

CHECKS = {
    "Descrever": "Verificar: a descrição corresponde ao que se vê?",
    "Pergunta": "Verificar: separa o que observa do que supõe? Os números batem com a imagem?",
    "Limites": "Verificar: reconhece o que a imagem não mostra (material, causa, gravidade, contexto)?",
}


class VisionInterface:
    """Choose an image and a request, ask the model in the background and show the answer."""

    def __init__(self, runner: VisionRunner) -> None:
        self.runner = runner
        self.images = available_images()
        self.image = self.images[0]
        self.request = REQUESTS[0]
        self.answer: VisionAnswer | None = None
        self.message = "Escolhe a imagem e o pedido e carrega em «Perguntar»."
        self.worker: threading.Thread | None = None
        self.started_at = 0.0
        self.figure = create_window("Imagem e texto", "Imagem e texto · GLM-4.6V",
                                    "O modelo recebe a imagem e o pedido em texto e responde em texto. Avalia o que "
                                    "a resposta pode e não pode afirmar.")
        self.image_axis = self.figure.add_axes((0.04, 0.24, 0.42, 0.58))
        self.request_line = self.figure.text(0.50, 0.80, "", fontsize=13, va="top", color=TEAL, weight="bold")
        self.answer_text = self.figure.text(0.50, 0.70, "", fontsize=14, va="top", color=INK, linespacing=1.45)
        self.check_line = self.figure.text(0.50, 0.29, "", fontsize=13, va="top", color=TEAL)
        self.status = self.figure.text(0.05, 0.185, "", fontsize=13.5, color=STATUS)
        self.buttons = add_buttons(self.figure, [
            ("", self.next_image), ("", self.next_request), ("Perguntar", self.ask),
        ], width=0.2)
        add_footer(self.figure, f"Modelo {lm_studio.VISION_MODEL} no LM Studio, ou respostas gravadas do mesmo "
                                "modelo · a primeira chamada carrega o modelo e demora mais")
        self.timer = self.figure.canvas.new_timer(interval=400)
        self.timer.add_callback(self.poll)
        self.render()

    def next_image(self, event: MouseEvent | None = None) -> None:
        if self._busy():
            return
        self.image = self.images[(self.images.index(self.image) + 1) % len(self.images)]
        self.answer = None
        self.render()

    def next_request(self, event: MouseEvent | None = None) -> None:
        if self._busy():
            return
        self.request = REQUESTS[(REQUESTS.index(self.request) + 1) % len(REQUESTS)]
        self.answer = None
        self.render()

    def _busy(self) -> bool:
        return self.worker is not None and self.worker.is_alive()

    def ask(self, event: MouseEvent | None = None) -> None:
        """Start the model call; the window keeps responding while it runs."""
        if self._busy():
            return
        self.answer, self.started_at = None, time.perf_counter()
        self.message = "A pensar…"
        self.worker = threading.Thread(target=self._call_model, daemon=True)
        self.worker.start()
        if is_headless():
            self.worker.join()
            self.poll()
        else:
            self.timer.start()
        self.render()

    def _call_model(self) -> None:
        try:
            self.answer = self.runner.run(self.image, self.request)
            self.message = f"Fonte: {self.answer.source} · {self.answer.seconds:.1f} s".replace(".", ",")
        except lm_studio.LmStudioError as error:
            self.message = str(error)

    def poll(self) -> None:
        """Timer callback: show the elapsed time until the answer arrives."""
        if self._busy():
            self.message = f"A pensar… {time.perf_counter() - self.started_at:.0f} s"
        else:
            self.timer.stop()
        self.render()

    def render(self) -> None:
        """Redraw the image, the request, the answer and what to check."""
        self.image_axis.clear()
        self.image_axis.imshow(mpimg.imread(image_path(self.image)))
        self.image_axis.axis("off")
        self.image_axis.set_title(self.image.label, fontsize=14, color=MUTED)
        self.buttons[0].label.set_text(f"Imagem: {self.image.label}")
        self.buttons[1].label.set_text(f"Pedido: {self.request}")
        self.request_line.set_text("Pedido: " + textwrap.fill(request_text(self.image, self.request), width=62))
        text = textwrap.fill(f"«{self.answer.text}»", width=60) if self.answer else "(ainda sem resposta)"
        self.answer_text.set_text(text)
        self.answer_text.set_color(INK if self.answer else MUTED)
        self.check_line.set_text(textwrap.fill(CHECKS[self.request], width=66))
        self.status.set_text(self.message)
        self.status.set_color(ORANGE if "indisponível" in self.message or "Sem resposta" in self.message else STATUS)
        self.figure.canvas.draw_idle()


def create_runner() -> VisionRunner:
    """Live GLM-4.6V when available, with the recording as fallback."""
    try:
        recorded = RecordedVisionRunner()
    except lm_studio.LmStudioError:
        recorded = None
    live = LiveVisionRunner() if lm_studio.is_model_available(lm_studio.VISION_MODEL) else None
    return FallbackVisionRunner(live, recorded)


def main() -> None:
    """Open the exercise, or record every image and request with --gravar."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gravar", action="store_true", help="grava as respostas do GLM-4.6V para uso offline")
    if parser.parse_args().gravar:
        if not lm_studio.is_model_available(lm_studio.VISION_MODEL):
            raise SystemExit(f"Para gravar é preciso o LM Studio com o modelo {lm_studio.VISION_MODEL}.")
        print(f"Gravadas {record_all(LiveVisionRunner())} respostas.")
        return
    runner = RecordedVisionRunner() if lm_studio.is_offline_forced() else create_runner()
    interface = VisionInterface(runner)

    def smoke() -> None:
        interface.ask()
        print(interface.answer_text.get_text()[:120])

    run_window(interface.figure, smoke)


if __name__ == "__main__":
    main()
