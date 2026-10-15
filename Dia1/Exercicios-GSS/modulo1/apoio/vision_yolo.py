"""Local YOLO inference with explicit tasks, cached official weights and typed output."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from urllib.error import URLError
from urllib.request import Request, urlopen
from typing import TYPE_CHECKING
import os
import numpy as np
from numpy.typing import NDArray
from PIL import Image, ImageOps

if TYPE_CHECKING:
    from ultralytics import YOLO
    from ultralytics.engine.results import Results

PixelArray = NDArray[np.uint8]
ROOT = Path(__file__).resolve().parents[2]
MODEL_DIRECTORY = ROOT / ".cache/yolo/models"
EXAMPLE_DIRECTORY = ROOT / "recursos/visao_computacional"
DENSE_LABEL_LIMIT = 40


@dataclass(frozen=True)
class VisionTask:
    """One task requires its corresponding checkpoint and interpretation."""
    key: str
    label: str
    model_name: str
    question: str
    interpretation: str


TASKS = (
    VisionTask("detect", "Deteção", "yolo11n.pt", "Que objetos existem e onde estão?",
               "Caixas e classes por objeto. O limiar filtra deteções, sem treinar o modelo."),
    VisionTask("classify", "Classificação", "yolo11n-cls.pt", "Que categoria descreve a imagem?",
               "Top 5 classes da imagem inteira, entre as classes ImageNet do modelo. Não localiza objetos."),
    VisionTask("segment", "Segmentação", "yolo11n-seg.pt", "Que píxeis pertencem a cada objeto?",
               "Máscaras por objeto, entre as classes COCO do modelo. Não cobre todas as regiões da imagem."),
    VisionTask("pose", "Pose humana", "yolo11n-pose.pt", "Onde estão os pontos do corpo?",
               "Pontos e ligações por pessoa. O modelo estima pose, sem identificar pessoas ou reconhecer ações."),
    VisionTask("obb", "Caixas orientadas (OBB)", "yolo11n-obb.pt", "Onde estão os objetos e qual a orientação?",
               "Caixas rodadas. Modelo treinado em imagens aéreas DOTA: usar um exemplo aéreo."),
)
EXAMPLES = (("Rua e pessoas", "bus.jpg"), ("Cão", "dog.jpg"), ("Pessoas em campo", "zidane.jpg"),
            ("Vista aérea", "boats.jpg"))


@dataclass(frozen=True)
class PredictionItem:
    """A class score reported by YOLO, not a measured accuracy."""
    label: str
    score: float


@dataclass(frozen=True)
class VisionPrediction:
    """Copied RGB output and compact measurements for one inference."""
    task: VisionTask
    image: PixelArray
    items: tuple[PredictionItem, ...]
    count: int
    elapsed_ms: float
    details: str


def task_by_key(key: str) -> VisionTask:
    """Resolve only the five declared tasks."""
    for task in TASKS:
        if task.key == key:
            return task
    raise ValueError(f"Tarefa desconhecida: {key}.")


def load_image(path: Path) -> PixelArray:
    """Read an oriented RGB image; bound memory for large classroom inputs."""
    if not path.is_file():
        raise ValueError(f"Imagem não encontrada: {path}.")
    try:
        with Image.open(path) as source:
            image = ImageOps.exif_transpose(source).convert("RGB")
            image.thumbnail((1600,1600))
            return np.asarray(image,dtype=np.uint8).copy()
    except (OSError,ValueError) as error:
        raise ValueError(f"Não foi possível ler a imagem {path.name}: {error}") from error


def download_model(task: VisionTask, directory: Path = MODEL_DIRECTORY) -> Path:
    """Download only an official, whitelisted checkpoint into repository cache."""
    path = directory/task.model_name
    if path.is_file():
        return path
    directory.mkdir(parents=True,exist_ok=True)
    partial = path.with_suffix(".pt.part")
    url = "https://github.com/ultralytics/assets/releases/download/v8.3.0/"+task.model_name
    try:
        request = Request(url,headers={"User-Agent":"formacao-gss-vision/1.0"})
        with urlopen(request,timeout=30) as response, partial.open("wb") as output:
            while chunk := response.read(1024*1024):
                output.write(chunk)
        if partial.stat().st_size < 100_000:
            raise ValueError("O ficheiro recebido não tem o tamanho esperado de um modelo.")
        partial.replace(path)
    except (OSError,URLError,ValueError) as error:
        partial.unlink(missing_ok=True)
        raise RuntimeError(f"Não foi possível preparar {task.model_name}. Verifica a internet e a cache {directory}: {error}") from error
    return path


class YoloEngine:
    """Load once per task and infer on CPU; this instance belongs to one worker."""

    def __init__(self, model_directory: Path = MODEL_DIRECTORY) -> None:
        # Set before importing Ultralytics so its settings and fonts stay local.
        config_directory = ROOT/".cache/yolo/config"
        config_directory.mkdir(parents=True,exist_ok=True)
        os.environ["YOLO_CONFIG_DIR"] = str(config_directory)
        self.model_directory = model_directory
        self.models: dict[str, YOLO] = {}

    def prepare(self) -> tuple[Path, ...]:
        """Cache all checkpoints before the lesson, without accessing a camera."""
        return tuple(download_model(task,self.model_directory) for task in TASKS)

    def _model(self, task: VisionTask) -> YOLO:
        if task.key not in self.models:
            try:
                from ultralytics import YOLO, settings
                import torch
            except ImportError as error:
                raise RuntimeError("Instala as dependências com: .venv\\Scripts\\python.exe -m pip install -r requirements-visao.txt") from error
            torch.set_num_threads(1)
            settings.update({"sync":False,"weights_dir":str(self.model_directory),
                             "runs_dir":str(ROOT/".cache/yolo/runs")})
            path = download_model(task,self.model_directory)
            self.models[task.key] = YOLO(str(path),task=task.key)
        return self.models[task.key]

    def predict(self, image: PixelArray, task_key: str, threshold: float = .25,
                show_boxes: bool = True) -> VisionPrediction:
        """Run the appropriate checkpoint on an RGB frame and copy the output."""
        if image.ndim != 3 or image.shape[2] != 3 or image.dtype != np.uint8 or not image.size:
            raise ValueError("Esperada uma imagem RGB não vazia, uint8, com três canais.")
        if not np.isfinite(threshold) or not 0 <= threshold <= 1:
            raise ValueError("O limiar deve estar entre 0 e 1.")
        task = task_by_key(task_key)
        model = self._model(task)
        start = perf_counter()
        # Ultralytics' ndarray boundary expects BGR, while our GUI uses RGB.
        result = model.predict(source=image[...,::-1].copy(),device="cpu",imgsz=640,
                               conf=threshold,verbose=False,save=False)[0]
        items,count,details = summarize_result(result,task)
        if task.key == "classify":
            annotated = image.copy()
        else:
            # For aerial OBB imagery, hide dense legends while retaining the
            # rotated geometry that defines the task. Above DENSE_LABEL_LIMIT objects
            # the legends cover the whole image, so they are hidden automatically.
            show_labels = show_boxes and count <= DENSE_LABEL_LIMIT
            if show_boxes and not show_labels:
                details = f"{details} Legendas escondidas: mais de {DENSE_LABEL_LIMIT} objetos.".strip()
            annotated = np.asarray(result.plot(boxes=True if task.key=="obb" else show_boxes,labels=show_labels,
                                               conf=show_labels,probs=False),dtype=np.uint8)[...,::-1].copy()
        annotated.setflags(write=False)
        return VisionPrediction(task,annotated,items,count,(perf_counter()-start)*1000,details)


def summarize_result(result: Results, task: VisionTask) -> tuple[tuple[PredictionItem,...],int,str]:
    """Interpret each task's actual output field, including empty detections."""
    if task.key == "classify":
        probabilities = result.probs
        if probabilities is None:
            raise RuntimeError("O modelo de classificação não devolveu probabilidades.")
        items = tuple(PredictionItem(result.names[i],float(probabilities.data[i])) for i in probabilities.top5)
        return items,1,"Uma classificação global. Os cinco scores apresentados são apenas o top 5, não têm de somar 1."
    boxes = result.obb if task.key == "obb" else result.boxes
    if boxes is None:
        return (),0,"Nenhum objeto acima do limiar. Isto não prova que a imagem não contenha objetos."
    items = tuple(PredictionItem(result.names[int(cls)],float(score))
                  for cls,score in zip(boxes.cls.tolist(),boxes.conf.tolist()))
    details = f"{len(items)} {'pessoas' if task.key=='pose' else 'objetos'} acima do limiar."
    if task.key == "segment":
        details += f" {0 if result.masks is None else len(result.masks)} máscaras de instâncias."
    elif task.key == "pose":
        points = result.keypoints
        details += f" {0 if points is None else points.data.shape[1]} pontos possíveis por pessoa."
    return items,len(items),details
