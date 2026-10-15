"""Exercise06: choose a YOLO task and inspect images, video or a webcam locally."""
from __future__ import annotations
import argparse
from contextlib import redirect_stdout
import json
import os
from pathlib import Path
import sys


def main() -> int:
    """Launch the GUI, prepare weights or verify the five tasks without a window."""
    parser = argparse.ArgumentParser(description="Visão computacional com YOLO11: cinco tarefas, imagens, vídeo e webcam.")
    parser.add_argument("--tarefa",choices=("detect","classify","segment","pose","obb"),default="detect")
    parser.add_argument("--imagem",type=Path,help="Imagem inicial da GUI ou da verificação.")
    parser.add_argument("--preparar",action="store_true",help="Descarregar os cinco modelos oficiais para a cache local.")
    parser.add_argument("--verificar",action="store_true",help="Executar inferência real nas cinco tarefas, sem janela ou webcam.")
    args = parser.parse_args()
    try:
        from apoio.vision_yolo import EXAMPLE_DIRECTORY, TASKS, YoloEngine, load_image
        engine = YoloEngine()
        if args.preparar:
            print(json.dumps({"models":[str(path) for path in engine.prepare()]},ensure_ascii=False))
            return 0
        if args.verificar or os.environ.get("FORMACAO_ML_NO_PAUSE") == "1":
            records = []
            for task in TASKS:
                filename = "boats.jpg" if task.key=="obb" else ("dog.jpg" if task.key=="classify" else "bus.jpg")
                path = args.imagem or EXAMPLE_DIRECTORY/filename
                with redirect_stdout(sys.stderr):
                    result = engine.predict(load_image(path),task.key)
                records.append({"task":task.key,"image":path.name,"model":task.model_name,
                                "count":result.count,"labels":[item.label for item in result.items],
                                "scores":[item.score for item in result.items]})
            print(json.dumps({"results":records},ensure_ascii=False))
            return 0
        import tkinter as tk
        from apoio.vision_sources import VisionSource
        from apoio.vision_ui import VisionInterface
        root = tk.Tk()
        source = VisionSource("image",str(args.imagem)) if args.imagem else None
        interface = VisionInterface(root,engine,args.tarefa,source)
        root.mainloop()
        return 0
    except (ImportError,RuntimeError,ValueError,OSError) as error:
        print(f"Exercício YOLO: {error}",file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
