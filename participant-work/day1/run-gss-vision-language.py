"""Record real YOLO inference and scripted Tk token/embedding lesson controls.

Requires the prepared GSS environment, YOLO cache and an interactive desktop.
Re-running overwrites only this recorder's evidence directory.
"""
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import importlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
GSS = ROOT / 'Dia1/Exercicios-GSS'
OUT = Path(__file__).with_name('gss-vision-language-evidence')
OUT.mkdir(exist_ok=True)
os.environ['FORMACAO_LMSTUDIO_OFFLINE'] = '1'
os.environ['MPLBACKEND'] = 'TkAgg'
os.environ['MPLCONFIGDIR'] = str(GSS / '.cache/matplotlib')
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.path[:0] = [str(GSS / 'modulo1'), str(GSS / 'modulo2')]

import cv2
import matplotlib.pyplot as plt
import tkinter as tk
from PIL import Image
from apoio.vision_yolo import YoloEngine, TASKS, EXAMPLE_DIRECTORY, MODEL_DIRECTORY
from apoio.vision_ui import VisionInterface


def capture(ui, name):
    """Export the lesson's own rendering; these are not desktop screenshots."""
    if hasattr(ui, 'figure'):
        ui.figure.canvas.draw()
        ui.figure.savefig(OUT / f'{name}.png')
    elif ui.rendered is not None:
        Image.fromarray(ui.rendered).save(OUT / f'{name}.png')


def settle(ui):
    deadline = time.monotonic() + 90
    while ui.future is not None or ui.pending_request is not None or ui.queued_request is not None:
        ui.root.update()
        if time.monotonic() > deadline:
            raise TimeoutError('YOLO window did not finish its request')
        time.sleep(.03)
    ui.root.update()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    record = {'executed_utc': datetime.now(timezone.utc).isoformat(),
              'python': sys.version, 'executable': str(Path(sys.executable).relative_to(ROOT)),
              'mode': 'scripted real Tk controls and real CPU YOLO; recorded language responses',
              'packages': {n: importlib.metadata.version(n) for n in
                           ('ultralytics', 'torch', 'torchvision', 'opencv-python', 'numpy', 'matplotlib', 'Pillow')},
              'provenance_sha256': sha(GSS / 'origem.json'), 'entries': [], 'vision': []}
    env = dict(os.environ, MPLBACKEND='Agg', FORMACAO_ML_NO_PAUSE='1')
    for pattern in ('modulo1/*06*.py', 'modulo2/*01*.py', 'modulo2/*02*.py'):
        path = next(GSS.glob(pattern))
        result = subprocess.run([sys.executable, str(path)], cwd=GSS, env=env,
                                capture_output=True, encoding='utf-8', timeout=180)
        log = path.stem + '.txt'
        (OUT / log).write_text(result.stdout + result.stderr, encoding='utf-8')
        record['entries'].append({'path': str(path.relative_to(ROOT)), 'sha256': sha(path),
                                  'exit_code': result.returncode, 'log': log})
        assert result.returncode == 0, result.stderr
    check = subprocess.run([sys.executable, '-m', 'pip', 'check'], capture_output=True, text=True)
    record['pip_check'] = {'exit_code': check.returncode, 'output': check.stdout + check.stderr}
    assert check.returncode == 0
    record['weights'] = {p.name: {'bytes': p.stat().st_size, 'sha256': sha(p)}
                         for p in sorted(MODEL_DIRECTORY.glob('*.pt'))}
    root = tk.Tk()
    ui = VisionInterface(root, YoloEngine())
    settle(ui)
    for task in TASKS:
        image = EXAMPLE_DIRECTORY / ('boats.jpg' if task.key == 'obb' else
                                    'dog.jpg' if task.key == 'classify' else 'bus.jpg')
        ui.task_label.set(task.label)
        ui.change_task()
        ui._set_source('image', str(image))
        settle(ui)
        ui.analyze()
        settle(ui)
        prediction = ui.last_frame.prediction
        assert prediction is not None and prediction.task.key == task.key
        record['vision'].append({'task': task.key, 'image': image.name, 'input_sha256': sha(image),
                                 'count': prediction.count, 'details': prediction.details,
                                 'items': [asdict(item) for item in prediction.items]})
        capture(ui, f'vision-{task.key}')
    # An ignored two-frame local fixture exercises real OpenCV video decoding.
    video = GSS / '.cache/yolo/lesson-video.avi'
    image = cv2.imread(str(EXAMPLE_DIRECTORY / 'bus.jpg'))
    height, width = image.shape[:2]
    writer = cv2.VideoWriter(str(video), cv2.VideoWriter_fourcc(*'MJPG'), 2, (width, height))
    assert writer.isOpened()
    writer.write(image)
    writer.write(cv2.flip(image, 1))
    writer.release()
    ui.task_label.set(TASKS[0].label)
    ui.change_task()
    ui._set_source('video', str(video))
    settle(ui)
    ui.analyze()
    settle(ui)
    first = ui.last_frame.frame_number
    ui.next_frame()
    settle(ui)
    record['video'] = {'fixture': 'two frames from attributed bus.jpg; second horizontally flipped',
                       'first_frame': first, 'next_frame': ui.last_frame.frame_number,
                       'objects': ui.last_frame.prediction.count}
    assert first == 1 and ui.last_frame.frame_number == 2
    capture(ui, 'vision-video')
    ui.close_source()
    settle(ui)
    ui.choose_camera()
    settle(ui)
    record['camera'] = {'selected': ui.source.kind, 'capture_unopened': ui.worker.capture is None,
                        'live_capture': 'NOT RUN: no classroom camera input supplied'}
    assert ui.worker.capture is None
    ui.close()

    tokens = importlib.import_module('dia1_modulo2_01_tokens_ids')
    ui = tokens.TokenInterface(tokens.load_vocabulary(), live_counts=False)
    record['tokens'] = []
    for _, sentence in tokens.EXAMPLES:
        ui.choose_example(sentence)
        ui.count_in_model()
        record['tokens'].append({'text': sentence,
                                 'tokens': [asdict(t) for t in tokens.tokenize(sentence, ui.vocabulary)],
                                 'summary': ui.summary.get_text(), 'comparison': ui.model_count})
    capture(ui, 'tokens-unknown')
    ui.toggle_vocabulary()
    capture(ui, 'tokens-vocabulary')
    ui.set_text('Unrecorded text example')
    ui.count_in_model()
    record['tokens_missing_recording'] = ui.model_count
    ui.clear()
    assert not ui.text
    plt.close(ui.figure)

    embeddings = importlib.import_module('dia1_modulo2_02_mapa_embeddings')
    ui = embeddings.EmbeddingMapInterface(embeddings.RecordedEmbeddingSource())
    ui.selected = 0
    ui.render()
    record['embeddings'] = {'shape': list(ui.vectors.shape), 'neighbours': ui.panel.get_text()}
    capture(ui, 'embeddings-neighbours')
    ui.add_suggestion()
    record['embeddings']['suggestion'] = ui.added.copy()
    ui.toggle_bank()
    record['embeddings']['bank_comparison'] = ui.panel.get_text()
    capture(ui, 'embeddings-bank')
    ui.add_phrase('Unrecorded sentence outside the prepared examples')
    record['embeddings']['missing_recording'] = ui.message
    ui.clear()
    assert not ui.added and ui.selected is None
    plt.close(ui.figure)
    record['recording_hashes'] = {p.name: sha(p) for p in
                                (GSS / 'modulo2/respostas_gravadas').glob('*.json')}
    (OUT / 'execution.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Recorded vision, tokens and embeddings successfully')


if __name__ == '__main__':
    main()
