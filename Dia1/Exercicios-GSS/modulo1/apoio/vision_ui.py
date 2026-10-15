"""Responsive Tk GUI for images, video and explicitly activated webcams."""
from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from collections import Counter
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageOps, ImageTk
from .formato_pt import numero
from .vision_sources import VisionFrame, VisionRequest, VisionSource, VisionWorker
from .vision_yolo import EXAMPLES, EXAMPLE_DIRECTORY, TASKS, PixelArray, YoloEngine, task_by_key

BACKGROUND, TEAL, INK = "#f6fafb", "#008694", "#172b33"


class VisionInterface:
    """One serialized worker, one pending job and at most one replacement job.

    Every GUI edit gets a new version. Completion of an older inference cannot
    replace a newer task/source/threshold. Tk widgets remain on the main thread.
    """

    def __init__(self, root: tk.Tk, engine: YoloEngine | None = None,
                 task_key: str = "detect", source: VisionSource | None = None) -> None:
        self.root = root
        self.worker = VisionWorker(engine or YoloEngine())
        self.executor = ThreadPoolExecutor(max_workers=1,thread_name_prefix="vision")
        self.future: Future[VisionFrame] | None = None
        self.pending_request: VisionRequest | None = None
        self.queued_request: VisionRequest | None = None
        self.version = self.generation = 0
        self.source = source or VisionSource("image",str(EXAMPLE_DIRECTORY/"bus.jpg"))
        self.is_running = self.is_closed = False
        self.last_frame: VisionFrame | None = None
        self.original: PixelArray | None = None
        self.rendered: PixelArray | None = None
        self.photos: list[ImageTk.PhotoImage | None] = [None,None]
        self.task_label = tk.StringVar(value=task_by_key(task_key).label)
        example = next((label for label,file in EXAMPLES if self.source.kind == "image"
                        and Path(self.source.location).name == file),EXAMPLES[0][0])
        self.example_label = tk.StringVar(value=example)
        self.camera_index = tk.StringVar(value="0")
        self.threshold = tk.DoubleVar(value=.25)
        self.show_boxes = tk.BooleanVar(value=True)
        self.status = tk.StringVar(value="Escolhe uma tarefa e clica em Analisar.")
        self.source_text = tk.StringVar(value=self._source_name())
        self.question = tk.StringVar()
        self.interpretation = tk.StringVar()
        self.score_text = tk.StringVar(value="Os scores aparecerão após a inferência.")
        self._build_window()
        self._set_task_text()
        self.root.protocol("WM_DELETE_WINDOW",self.close)
        self.root.bind("<space>",lambda _: self.toggle_playback())
        self.root.bind("<Right>",lambda _: self.next_frame())
        self.root.bind("<Escape>",lambda _: self.pause())
        self.poll_id = self.root.after(60,self.poll)
        if self.source.kind != "camera":
            self.request(should_predict=False)

    @property
    def task_key(self) -> str:
        """The visible task label maps to a fixed model specification."""
        return next(task.key for task in TASKS if task.label == self.task_label.get())

    def _build_window(self) -> None:
        self.root.title("Formação IA · Visão computacional com YOLO")
        self.root.geometry("1400x900")
        self.root.minsize(1080,780)
        self.root.configure(bg=BACKGROUND)
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TFrame",background=BACKGROUND)
        style.configure("TLabel",background=BACKGROUND,foreground=INK,font=("Segoe UI",12))
        style.configure("TButton",font=("Segoe UI",11),padding=(10,7))
        style.configure("TCheckbutton",background=BACKGROUND,font=("Segoe UI",11))
        body = ttk.Frame(self.root,padding=(28,18))
        body.pack(fill="both",expand=True)
        ttk.Label(body,text="Visão computacional com YOLO",font=("Segoe UI",25,"bold"),foreground=INK).pack(anchor="w")
        ttk.Label(body,textvariable=self.question,font=("Segoe UI",15),foreground=TEAL).pack(anchor="w",pady=(5,13))
        self._source_controls(body)
        self._task_controls(body)
        self._image_views(body)
        self._output_details(body)
        ttk.Label(body,textvariable=self.status,foreground=TEAL,wraplength=1300).pack(anchor="w",pady=(6,0))
        ttk.Label(body,text="Inferência local · pesos já treinados · mudar tarefa ou limiar não treina o modelo · scores não são accuracy",
                  font=("Segoe UI",10)).pack(anchor="w",pady=(8,0))

    def _source_controls(self, body: ttk.Frame) -> None:
        row = ttk.Frame(body)
        row.pack(fill="x",pady=(0,8))
        ttk.Label(row,text="Exemplo").pack(side="left",padx=(0,8))
        examples = ttk.Combobox(row,textvariable=self.example_label,state="readonly",width=19,
                                font=("Segoe UI",11),
                                values=[name for name,_ in EXAMPLES])
        examples.pack(side="left",padx=(0,10))
        examples.bind("<<ComboboxSelected>>",lambda _: self.choose_example())
        ttk.Button(row,text="Abrir imagem",command=self.open_image).pack(side="left",padx=4)
        ttk.Button(row,text="Abrir vídeo",command=self.open_video).pack(side="left",padx=4)
        ttk.Button(row,text="Escolher webcam",command=self.choose_camera).pack(side="left",padx=(12,4))
        ttk.Spinbox(row,from_=0,to=9,textvariable=self.camera_index,width=3).pack(side="left",padx=4)
        ttk.Label(body,textvariable=self.source_text,font=("Segoe UI",10)).pack(anchor="w")

    def _task_controls(self, body: ttk.Frame) -> None:
        row = ttk.Frame(body)
        row.pack(fill="x",pady=(9,7))
        self.task_select = ttk.Combobox(row,textvariable=self.task_label,state="readonly",width=23,
                                        font=("Segoe UI",11),
                                        values=[task.label for task in TASKS])
        self.task_select.pack(side="left",padx=(0,10))
        self.task_select.bind("<<ComboboxSelected>>",lambda _: self.change_task())
        ttk.Button(row,text="Analisar",command=self.analyze).pack(side="left",padx=4)
        self.play_button = ttk.Button(row,text="Iniciar vídeo/webcam",command=self.toggle_playback)
        self.play_button.pack(side="left",padx=4)
        self.step_button = ttk.Button(row,text="Próximo frame",command=self.next_frame)
        self.step_button.pack(side="left",padx=4)
        ttk.Button(row,text="Fechar fonte",command=self.close_source).pack(side="left",padx=4)
        self.box_control = ttk.Checkbutton(row,text="Mostrar caixas/classes",variable=self.show_boxes,command=self.change_options)
        self.box_control.pack(side="left",padx=15)
        self.limit_row = ttk.Frame(body)
        self.limit_row.pack(fill="x",pady=(0,6))
        self.limit_caption = ttk.Label(self.limit_row,text="Limiar das deteções")
        self.limit_caption.pack(side="left",padx=(0,10))
        self.limit_scale = ttk.Scale(self.limit_row,from_=.05,to=.95,variable=self.threshold,
                                     command=self.change_threshold,length=360)
        self.limit_scale.pack(side="left")
        self.limit_value = ttk.Label(self.limit_row,text="0,25",width=6)
        self.limit_value.pack(side="left",padx=10)

    def _image_views(self, body: ttk.Frame) -> None:
        views = ttk.Frame(body)
        views.pack(fill="both",expand=True,pady=8)
        views.columnconfigure((0,1),weight=1,uniform="image")
        views.rowconfigure(1,weight=1)
        ttk.Label(views,text="Imagem original",font=("Segoe UI",15,"bold")).grid(row=0,column=0,sticky="w",pady=(0,7))
        self.output_title = ttk.Label(views,text="Resultado",font=("Segoe UI",15,"bold"))
        self.output_title.grid(row=0,column=1,sticky="w",padx=(15,0),pady=(0,7))
        self.canvases = []
        for column in range(2):
            canvas = tk.Canvas(views,bg="white",highlightthickness=1,highlightbackground="#d5e2e6")
            canvas.grid(row=1,column=column,sticky="nsew",padx=(0,15) if column==0 else (15,0))
            canvas.bind("<Configure>",lambda _: self._draw_images())
            self.canvases.append(canvas)

    def _output_details(self, body: ttk.Frame) -> None:
        ttk.Label(body,textvariable=self.interpretation,wraplength=1300,font=("Segoe UI",12)).pack(anchor="w",pady=(6,4))
        details = ttk.Frame(body)
        details.pack(fill="x")
        details.columnconfigure(0,weight=1)
        self.items_text = tk.Text(details,height=3,wrap="word",font=("Segoe UI",11),bg=BACKGROUND,
                                  fg=INK,relief="flat",state="disabled")
        self.items_text.grid(row=0,column=0,sticky="ew")
        ttk.Label(details,textvariable=self.score_text,wraplength=420,font=("Segoe UI",11)).grid(row=0,column=1,sticky="ne",padx=(16,0))

    def _source_name(self) -> str:
        kind = {"image":"Imagem","video":"Vídeo","camera":"Webcam"}[self.source.kind]
        name = self.source.location if self.source.kind == "camera" else Path(self.source.location).name
        return f"Fonte: {kind} · {name}"

    def _set_task_text(self) -> None:
        task = task_by_key(self.task_key)
        self.question.set(task.question)
        self.interpretation.set(task.interpretation)
        classification = task.key == "classify"
        self.limit_scale.configure(state="disabled" if classification else "normal")
        if classification:
            self.limit_scale.pack_forget()
            self.limit_value.pack_forget()
        elif not self.limit_scale.winfo_manager():
            self.limit_scale.pack(side="left")
            self.limit_value.pack(side="left",padx=10)
        self.box_control.configure(state="disabled" if classification else "normal")
        self.box_control.configure(text="Mostrar legendas" if task.key=="obb" else "Mostrar caixas/classes")
        self.limit_caption.configure(text="Classificação global · cinco classes mais prováveis" if classification else "Limiar das deteções")
        self.output_title.configure(text=f"Resultado · {task.label}")
        media = self.source.kind != "image"
        for button in (self.play_button,self.step_button):
            button.configure(state="normal" if media else "disabled")

    def _invalidate(self) -> None:
        self.version += 1
        self.queued_request = None
        self.rendered = None
        self.last_frame = None
        self._set_items("")
        self.score_text.set("Novo resultado após Analisar ou no próximo frame.")
        self._draw_images()

    def change_task(self) -> None:
        """Swap the checkpoint without showing an old task's output."""
        self._invalidate()
        self._set_task_text()
        self.status.set("Tarefa alterada. Clica em Analisar, ou continua a reprodução.")

    def change_threshold(self, _value: str) -> None:
        """Apply the new threshold only to new results, never to old annotations."""
        self.limit_value.configure(text=f"{self.threshold.get():.2f}".replace(".",","))
        if hasattr(self,"canvases"):
            self.change_options()

    def change_options(self) -> None:
        """Invalidate annotations after editing confidence or visible overlays."""
        self._invalidate()
        self.status.set("Opções alteradas. Clica em Analisar, ou observa o próximo frame.")

    def _set_source(self, kind: str, location: str) -> None:
        self.pause()
        self.generation += 1
        self.source = VisionSource(kind,location,self.generation)
        if kind == "image":
            for label,filename in EXAMPLES:
                if Path(location).name == filename:
                    self.example_label.set(label)
                    break
        self.original = None
        self._invalidate()
        self.source_text.set(self._source_name())
        self._set_task_text()
        if kind != "camera":
            self.request(should_predict=False)
        else:
            self.status.set("Webcam escolhida, ainda fechada. Clica em Analisar ou Iniciar para a abrir.")

    def choose_example(self) -> None:
        """Open a packaged example; all tasks can inspect the same input."""
        filename = next(file for label,file in EXAMPLES if label == self.example_label.get())
        self._set_source("image",str(EXAMPLE_DIRECTORY/filename))

    def open_image(self) -> None:
        """Select an image from the user's filesystem."""
        path = filedialog.askopenfilename(parent=self.root,title="Escolher imagem",filetypes=[("Imagens","*.jpg *.jpeg *.png *.webp *.bmp"),("Todos","*.*")])
        if path:
            self._set_source("image",path)

    def open_video(self) -> None:
        """Select a local video and preview its first frame, without playing."""
        path = filedialog.askopenfilename(parent=self.root,title="Escolher vídeo",filetypes=[("Vídeos","*.mp4 *.avi *.mov *.mkv"),("Todos","*.*")])
        if path:
            self._set_source("video",path)

    def choose_camera(self) -> None:
        """Configure a webcam index; choosing it does not activate capture."""
        try:
            index = int(self.camera_index.get())
            if index < 0:
                raise ValueError
        except ValueError:
            self.status.set("Escolhe um índice de webcam não negativo, por exemplo 0.")
            return
        self._set_source("camera",str(index))

    def analyze(self) -> None:
        """Infer on the current frame, preserving a paused video's position."""
        self.pause()
        self.request()

    def next_frame(self) -> None:
        """Read and analyze exactly one new media frame."""
        if self.source.kind != "image":
            self.pause()
            self.request(should_advance=True)

    def toggle_playback(self) -> None:
        """Start or pause media; images are analyzed with the dedicated button."""
        if self.source.kind == "image":
            return
        if self.is_running:
            self.pause()
        else:
            self.is_running = True
            self.play_button.configure(text="Pausar")
            self.request(should_advance=True)

    def pause(self) -> None:
        """Stop further jobs; finish any in-flight job and release the webcam."""
        self.is_running = False
        self.play_button.configure(text="Iniciar vídeo/webcam")
        self.queued_request = None
        if self.source.kind == "camera":
            self.worker.release_requested.set()
            if self.future is None:
                self.executor.submit(self.worker.close)

    def close_source(self) -> None:
        """Release the source, discard queued/stale work and keep the window open."""
        self.pause()
        self._invalidate()
        self.worker.release_requested.set()
        if self.future is None:
            self.executor.submit(self.worker.close)
        self.status.set("Fonte fechada. A próxima análise volta a abrir a fonte escolhida.")

    def request(self, should_advance: bool = False, should_predict: bool = True) -> None:
        """Keep only the newest requested replacement while one job is running."""
        request = VisionRequest(self.version,self.source,self.task_key,self.threshold.get(),
                                self.show_boxes.get(),should_advance,should_predict,
                                self.source.kind=="camera" and not self.is_running)
        if self.future is not None:
            self.queued_request = request
        else:
            self._submit(request)

    def _submit(self, request: VisionRequest) -> None:
        self.pending_request = request
        self.status.set("A analisar. Na primeira utilização, preparar o modelo pode demorar..." if request.should_predict else "A abrir a fonte...")
        self.future = self.executor.submit(self.worker.process,request)

    def poll(self) -> None:
        """Commit completed jobs only when their settings still match the GUI."""
        if self.is_closed:
            return
        if self.future is not None and self.future.done():
            self._finish_job()
            if self.queued_request is not None:
                request,self.queued_request = self.queued_request,None
                self._submit(request)
            elif self.is_running:
                self.request(should_advance=True)
        self.poll_id = self.root.after(60,self.poll)

    def _finish_job(self) -> None:
        future,request = self.future,self.pending_request
        self.future = self.pending_request = None
        try:
            frame = future.result()
        except Exception as error:
            if request.version == self.version:
                self.pause()
                self.status.set(str(error))
            return
        if request.version != self.version:
            return
        self.last_frame = frame
        self.original = frame.image
        self.rendered = None if frame.prediction is None else frame.prediction.image
        self._draw_images()
        if frame.prediction is None:
            self.status.set("Fonte pronta. Clica em Analisar ou inicia o vídeo.")
        else:
            self._show_prediction(frame)

    def _show_prediction(self, frame: VisionFrame) -> None:
        result = frame.prediction
        self.interpretation.set(result.task.interpretation)
        if result.task.key == "classify":
            lines = [f"{item.label}: {numero(item.score, '.1%')}" for item in result.items]
            self.output_title.configure(text=f"Classificação: {result.items[0].label}" if result.items else "Classificação sem resultado")
        else:
            if len(result.items)>15:
                lines = [f"{label}: {count}" for label,count in Counter(item.label for item in result.items).most_common()]
            else:
                lines = [f"{item.label} ({item.score:.0%})" for item in result.items]
        self._set_items("   ·   ".join(lines) if lines else "Nenhum objeto acima do limiar.")
        self.score_text.set(result.details)
        self.status.set(f"Frame {frame.frame_number} · {result.task.model_name} · CPU · análise {result.elapsed_ms:.0f} ms. Pesos fixos.")

    def _set_items(self, value: str) -> None:
        self.items_text.configure(state="normal")
        self.items_text.delete("1.0","end")
        self.items_text.insert("1.0",value)
        self.items_text.configure(state="disabled")

    def _draw_images(self) -> None:
        for i,(canvas,array) in enumerate(zip(self.canvases,(self.original,self.rendered))):
            canvas.delete("all")
            width,height = max(1,canvas.winfo_width()),max(1,canvas.winfo_height())
            if array is None:
                caption = "Escolhe uma fonte" if i == 0 else "Clica em Analisar para revelar o resultado"
                canvas.create_text(width/2,height/2,text=caption,font=("Segoe UI",15),fill=TEAL,width=max(1,width-30))
                self.photos[i] = None
            else:
                image = ImageOps.contain(Image.fromarray(array),(max(1,width-16),max(1,height-16)))
                self.photos[i] = ImageTk.PhotoImage(image,master=self.root)
                canvas.create_image(width/2,height/2,image=self.photos[i])

    def close(self) -> None:
        """Cancel queued work and guarantee capture release after any active job."""
        if self.is_closed:
            return
        self.is_closed = True
        self.is_running = False
        self.queued_request = None
        self.worker.release_requested.set()
        if self.future is not None:
            self.future.add_done_callback(lambda _: self.worker.close())
        else:
            self.executor.submit(self.worker.close)
        self.executor.shutdown(wait=False,cancel_futures=False)
        self.root.after_cancel(self.poll_id)
        self.root.destroy()
