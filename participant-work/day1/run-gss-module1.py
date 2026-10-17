"""Run the existing five GSS lessons and record an automated Tk walkthrough.

Use an interpreter with the GSS base requirements. Downloads the UCI cache through its existing
loader. Screenshots are cropped to this process's own Tk windows. This records
assistant execution, not human mouse interaction or participant attendance.
"""
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import importlib
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
GSS = ROOT / 'Dia1/Exercicios-GSS'
OUT = Path(__file__).resolve().parent / 'gss-evidence'
OUT.mkdir(exist_ok=True)
os.environ['MPLCONFIGDIR'] = str(GSS / '.cache/matplotlib')
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ.pop('FORMACAO_ML_NO_PAUSE', None)
os.environ['MPLBACKEND'] = 'TkAgg'
sys.path.insert(0, str(GSS / 'modulo1'))

import tkinter as tk
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseEvent
import numpy as np
from PIL import ImageGrab
import torch

record = {
    'started_utc': datetime.now(timezone.utc).isoformat(),
    'python': sys.version,
    'executable': str(Path(sys.executable).relative_to(ROOT)),
    'platform': platform.platform(),
    'packages': {name: importlib.metadata.version(name)
                 for name in ('matplotlib', 'numpy', 'torch', 'Pillow')},
    'tk_version': tk.TkVersion,
    'backend': matplotlib.get_backend(),
    'mode': 'real Tk windows; scripted controls and dispatched Matplotlib mouse events',
    'lessons': {},
    'source_baseline': subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
    'provenance_manifest_sha256': hashlib.sha256((GSS / 'origem.json').read_bytes()).hexdigest(),
    'entry_script_sha256': {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                           for path in sorted((GSS / 'modulo1').glob('dia1_modulo1_0[1-5]_*.py'))},
}


def save():
    (OUT / 'execution.json').write_text(json.dumps(record, indent=2), encoding='utf-8')


def capture(ui, name):
    fig = ui.figure
    fig.canvas.draw()
    window = fig.canvas.manager.window
    window.deiconify()
    window.lift()
    window.update_idletasks()
    window.update()
    plt.pause(.25)
    x, y = window.winfo_rootx(), window.winfo_rooty()
    width, height = window.winfo_width(), window.winfo_height()
    ImageGrab.grab(bbox=(x, y, x + width, y + height)).save(OUT / f'{name}.png')
    return {'file': f'{name}.png', 'window_size': [width, height],
            'capture': 'own Tk client area, PIL ImageGrab'}


def click(fig, axis, point, kind='button_press_event'):
    x, y = axis.transData.transform(point)
    event = MouseEvent(kind, fig.canvas, x, y, button=1)
    fig.canvas.callbacks.process(kind, event)


def state_hash(model):
    digest = hashlib.sha256()
    for name, tensor in sorted(model.state_dict().items()):
        digest.update(name.encode())
        digest.update(tensor.detach().cpu().numpy().tobytes())
    return digest.hexdigest()


def main():
    torch.set_num_threads(1)
    root = tk.Tk()
    root.withdraw()
    root.update()
    record['tk_patchlevel'] = root.tk.call('info', 'patchlevel')
    root.destroy()
    if importlib.util.find_spec('pip') is not None:
        record['pip_check'] = subprocess.check_output(
            [sys.executable, '-m', 'pip', 'check'], text=True).strip()
    else:
        record['pip_check'] = 'NOT RUN: reused environment has no pip; required imports succeeded'
    installed = sorted(f'{dist.metadata["Name"]}=={dist.version}'
                       for dist in importlib.metadata.distributions())
    (OUT / 'environment.txt').write_text('\n'.join(installed) + '\n', encoding='utf-8')

    from apoio.digit_dataset import load_digit_splits, load_binary_demo_examples, DATASET_URL
    images, labels, test_images, test_labels = load_digit_splits()
    archive = GSS / '.cache/datasets/optical_digits.zip'
    record['dataset'] = {
        'url': DATASET_URL, 'cache_path': str(archive.relative_to(ROOT)),
        'sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
        'train_shape': list(images.shape), 'test_shape': list(test_images.shape),
        'train_class_counts': np.bincount(labels).tolist(),
        'test_class_counts': np.bincount(test_labels).tolist(),
        'range': [float(images.min()), float(images.max())],
        'separate_from_day2_mnist': True,
    }
    save()

    # Run the unchanged entry scripts exactly as documented for unattended use.
    for index in range(1, 6):
        script = next((GSS / 'modulo1').glob(f'dia1_modulo1_{index:02d}_*.py'))
        env = dict(os.environ, MPLBACKEND='Agg', FORMACAO_ML_NO_PAUSE='1')
        completed = subprocess.run([sys.executable, str(script)], cwd=GSS,
                                   env=env, capture_output=True, text=True,
                                   encoding='utf-8', errors='replace', timeout=180)
        log = f'entry-{index:02d}.txt'
        (OUT / log).write_text(completed.stdout + completed.stderr, encoding='utf-8')
        record['lessons'][str(index)] = {'entry_script': script.name,
            'exit_code': completed.returncode, 'log': log}
        save()
        if completed.returncode:
            raise RuntimeError(f'{script.name} failed; inspect {log}')

    one = importlib.import_module('dia1_modulo1_01_paradigmas_aprendizagem')
    ui = one.SessionLearningInterface()
    ui.train()
    ui.next_example()
    record['lessons']['1']['paradigms'] = {
        'trained': ui.is_trained, 'new_session': ui.new_session.tolist(),
        'status': ui.status.get_text(), 'screenshot': capture(ui, '01-paradigms')}
    plt.close(ui.figure)
    from apoio.flappy_bird_ui import FlappyBirdInterface
    ui = FlappyBirdInterface(animate=False)
    ui.single_step()
    first_reward = ui.learner.last_reward
    while len(ui.learner.scores) < 200:
        ui.learner.advance()
    trained = ui.learner.q_table.copy()
    scores = ui.learner.scores.copy()
    ui.toggle_learning()
    for _ in range(100):
        ui.learner.advance()
    ui.render()
    assert np.array_equal(trained, ui.learner.q_table)
    record['lessons']['1']['flappy'] = {
        'first_reward': first_reward, 'training_episodes': len(scores),
        'score_first20_mean': float(np.mean(scores[:20])),
        'score_last20_mean': float(np.mean(scores[-20:])), 'score_max': max(scores),
        'epsilon_playback': ui.learner.epsilon,
        'nonzero_q_values': int(np.count_nonzero(trained)),
        'playback_preserved_q_table': True, 'screenshot': capture(ui, '01-flappy')}
    plt.close(ui.figure)
    save()

    from apoio.forward_pass_ui import ForwardPassInterface
    ui = ForwardPassInterface(*load_binary_demo_examples(), animate=False)
    for _ in range(9):
        ui.advance()
    result = ui.demo.result
    record['lessons']['2']['forward'] = {
        'image_shape': list(ui.demo.image.shape), 'vector_size': ui.demo.vector.size,
        'selected_pixels': list(ui.demo.pixel_indices), 'inputs': result.inputs.tolist(),
        'hidden_activations': result.hidden_activations.tolist(),
        'probabilities_0_5': result.probabilities.tolist(),
        'screenshot': capture(ui, '02-forward')}
    ui.next_example()
    plt.close(ui.figure)
    save()

    from apoio.learning_ui import LearningInterface
    ui = LearningInterface(*load_binary_demo_examples(), animate=False)
    for _ in range(10):
        ui.advance()
    step = ui.demo.step
    first_loss = ui.demo.loss_history[0]
    for _ in range(20):
        ui.demo.next_iteration(advance_example=True)
        for _ in range(10):
            ui.demo.advance()
    ui.render()
    record['lessons']['3']['learning'] = {
        'sample_loss_before': step.loss_before, 'sample_loss_after': step.loss_after,
        'gradient_norm': float(np.linalg.norm(step.gradients.hidden_weights)),
        'updates': ui.demo.total_updates, 'mean_loss_initial': first_loss,
        'mean_loss_final': ui.demo.loss_history[-1],
        'screenshot': capture(ui, '03-learning')}
    plt.close(ui.figure)
    save()

    from apoio.metrics_ui import MetricsInterface
    from apoio.evaluation_metrics import roc_curve
    ui = MetricsInterface()
    results = {}
    for threshold in (.2, .5, .8):
        ui.slider.set_val(threshold)
        results[str(threshold)] = asdict(ui.metrics)
    ui.slider.set_val(.5)
    for _ in range(7):
        ui.advance()
    before = ui.is_fn_expensive
    ui.costs()
    assert ui.is_fn_expensive != before
    cost_image = capture(ui, '04-costs')
    ui.advance()
    fpr, tpr, auc = roc_curve(ui.scenario.labels, ui.scenario.scores)
    record['lessons']['4']['metrics'] = {
        'scenario': ui.scenario.name, 'thresholds': results, 'auc': auc,
        'cost_toggle_changed': True, 'cost_screenshot': cost_image,
        'roc_screenshot': capture(ui, '04-roc')}
    plt.close(ui.figure)
    save()

    five = importlib.import_module('dia1_modulo1_05_mlp_digitos')
    from apoio.digit_training_demo import DigitTrainingDemo
    from apoio.digit_training_ui import DigitTrainingInterface
    demo = DigitTrainingDemo(five)
    ui = DigitTrainingInterface(demo)
    for _ in range(7):
        ui.advance()
    ui.train()
    while ui.is_running:
        ui.tick()
    curve = capture(ui, '05-training')
    ui.evaluate()
    evaluation = capture(ui, '05-evaluation')
    confusion, accuracy, precision, recall, f1, loss = demo.test_result
    ui.use()
    frozen_before = state_hash(demo.final_model)
    ui.infer()  # Empty drawing recovery.
    empty_notice = ui.notice
    # Dispatch an actual Matplotlib event sequence for a simple vertical stroke.
    ui.figure.canvas.draw()
    click(ui.figure, ui.image_axis, (12., 4.))
    for y in range(5, 21):
        click(ui.figure, ui.image_axis, (12., float(y)), 'motion_notify_event')
    click(ui.figure, ui.image_axis, (12., 20.), 'button_release_event')
    ui.infer()
    probabilities = ui.draw_probabilities.copy()
    drawing = capture(ui, '05-drawing')
    ui.clear()
    assert not np.any(ui.drawing)
    assert frozen_before == state_hash(demo.final_model)
    record['lessons']['5']['training'] = {
        'seed': five.SEED, 'epochs': demo.epoch, 'updates': demo.updates,
        'train_size': len(demo.train_indices), 'validation_size': len(demo.validation_indices),
        'test_size': len(demo.test_labels), 'best_epoch': demo.best_epoch,
        'history': [asdict(row) for row in demo.history],
        'test': {'accuracy': accuracy, 'macro_precision': precision,
                 'macro_recall': recall, 'macro_f1': f1, 'loss': loss,
                 'confusion_matrix': confusion.tolist()},
        'drawing': {'input': 'synthetic vertical mouse stroke; not a test sample',
                    'prediction': int(probabilities.argmax()), 'scores': probabilities.tolist(),
                    'empty_notice': empty_notice, 'clear_works': True,
                    'frozen_state_sha256_before_after': frozen_before,
                    'weights_unchanged_by_inference': True},
        'screenshots': [curve, evaluation, drawing],
    }
    plt.close(ui.figure)
    record['finished_utc'] = datetime.now(timezone.utc).isoformat()
    save()
    print('PASS: five entry scripts and Tk walkthroughs; evidence:', OUT)


if __name__ == '__main__':
    main()
