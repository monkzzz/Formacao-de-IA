"""File and camera frame lifecycle, isolated from inference and GUI widgets."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from threading import Event
from typing import TYPE_CHECKING, Literal
import os
import numpy as np
from .vision_yolo import PixelArray, VisionPrediction, YoloEngine, load_image

if TYPE_CHECKING:
    import cv2


@dataclass(frozen=True)
class VisionSource:
    """The generation forces reloading when the same input is opened again."""
    kind: Literal["image","video","camera"]
    location: str
    generation: int = 0


@dataclass(frozen=True)
class VisionRequest:
    """One immutable job snapshot; versions prevent stale GUI results."""
    version: int
    source: VisionSource
    task_key: str
    threshold: float
    show_boxes: bool
    should_advance: bool = False
    should_predict: bool = True
    should_close_source: bool = False


@dataclass(frozen=True)
class VisionFrame:
    """The source frame and matching prediction for one displayed moment."""
    image: PixelArray
    prediction: VisionPrediction | None
    frame_number: int


class VisionWorker:
    """All capture and YOLO operations are serialized on the same worker thread."""

    def __init__(self, engine: YoloEngine) -> None:
        self.engine = engine
        self.source: VisionSource | None = None
        self.capture: cv2.VideoCapture | None = None
        self.frame: PixelArray | None = None
        self.frame_number = 0
        self.release_requested = Event()

    def close(self, clear_request: bool = True) -> None:
        """Release a camera/video handle and reset the frame cache."""
        if self.capture is not None:
            self.capture.release()
        self.capture = self.source = self.frame = None
        self.frame_number = 0
        if clear_request:
            self.release_requested.clear()

    def process(self, request: VisionRequest) -> VisionFrame:
        """Read or reuse one frame, ensuring requested release even on failure."""
        try:
            if request.source != self.source:
                self.close(clear_request=False)
                self._open(request.source)
            if self.frame is None or (request.should_advance and request.source.kind != "image"):
                self._read()
            image = self.frame.copy()
            prediction = (self.engine.predict(image,request.task_key,request.threshold,request.show_boxes)
                          if request.should_predict else None)
            return VisionFrame(image,prediction,self.frame_number)
        except Exception:
            self.close()
            raise
        finally:
            if self.release_requested.is_set() or request.should_close_source:
                self.close()

    def _open(self, source: VisionSource) -> None:
        if source.kind not in ("image","video","camera"):
            raise ValueError(f"Tipo de fonte desconhecido: {source.kind}.")
        self.source = source
        if source.kind == "image":
            self.frame = load_image(Path(source.location))
            self.frame_number = 1
            return
        import cv2
        if source.kind == "video":
            if not Path(source.location).is_file():
                raise ValueError(f"Vídeo não encontrado: {source.location}.")
            self.capture = cv2.VideoCapture(source.location)
        else:
            try:
                index = int(source.location)
            except ValueError as error:
                raise ValueError("O índice da webcam deve ser um inteiro não negativo.") from error
            if index < 0:
                raise ValueError("O índice da webcam deve ser não negativo.")
            backend = cv2.CAP_DSHOW if os.name == "nt" else cv2.CAP_ANY
            self.capture = cv2.VideoCapture(index,backend)
        if not self.capture.isOpened():
            raise RuntimeError("Não foi possível abrir a fonte. Verifica o ficheiro, o índice ou o acesso à webcam.")

    def _read(self) -> None:
        success, frame = self.capture.read()
        if not success:
            if self.source.kind == "video":
                raise EOFError("Fim do vídeo. Iniciar volta ao início.")
            raise RuntimeError("A webcam não forneceu uma imagem. Verifica se está disponível.")
        self.frame = np.asarray(frame,dtype=np.uint8)[...,::-1].copy()
        self.frame_number += 1
