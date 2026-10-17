"""Execute remaining language lessons, scripted Tk controls, and the offline suite.

Run with the GSS Python environment from the repository root. Re-running overwrites
only gss-language-final-evidence. Exports are figure renderings, not desktop captures.
"""
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import importlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
GSS = ROOT / 'Dia1/Exercicios-GSS'
OUT = Path(__file__).with_name('gss-language-final-evidence')
OUT.mkdir(exist_ok=True)
os.environ.update(FORMACAO_LMSTUDIO_OFFLINE='1', MPLBACKEND='TkAgg',
                  MPLCONFIGDIR=str(GSS / '.cache/matplotlib'), PYTHONIOENCODING='utf-8')
os.environ.pop('FORMACAO_ML_NO_PAUSE', None)
sys.path.insert(0, str(GSS / 'modulo2'))

import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseEvent
import numpy as np


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(number):
    return importlib.import_module(next((GSS / 'modulo2').glob(f'*_0{number}_*.py')).stem)


def render(ui, name):
    ui.figure.canvas.draw()
    ui.figure.canvas.flush_events()
    ui.figure.savefig(OUT / f'{name}.png')


def click(ui, axis, point):
    ui.figure.canvas.draw()
    x, y = axis.transData.transform(point)
    event = MouseEvent('button_press_event', ui.figure.canvas, x, y, button=1)
    ui.figure.canvas.callbacks.process('button_press_event', event)


def run(command, name, env, timeout=300):
    result = subprocess.run(command, cwd=GSS, env=env, capture_output=True,
                            encoding='utf-8', errors='replace', timeout=timeout)
    (OUT / name).write_text(result.stdout + result.stderr, encoding='utf-8')
    return {'command': [str(c) for c in command], 'cwd': str(GSS.relative_to(ROOT)),
            'exit_code': result.returncode, 'log': name}


def run_suite(record, env):
    directory = GSS / '.cache/test-temp'
    directory.mkdir(parents=True, exist_ok=True)
    suite_env = dict(env, TMP=str(directory), TEMP=str(directory))
    suite_env.pop('FORMACAO_ML_NO_PAUSE', None)
    record['suite_environment'] = {key: suite_env[key] for key in
                                   ('MPLBACKEND', 'FORMACAO_LMSTUDIO_OFFLINE', 'MPLCONFIGDIR', 'TMP', 'TEMP')}
    record['suite'] = run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-t', '.'],
                           'offline-suite.txt', suite_env)
    record['finished_utc'] = datetime.now(timezone.utc).isoformat()
    (OUT / 'execution.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    assert record['suite']['exit_code'] == 0, record['suite']


def main():
    if '--suite-only' in sys.argv:
        record = json.loads((OUT / 'execution.json').read_text(encoding='utf-8'))
        if record['suite']['exit_code']:
            previous = dict(record['suite'])
            previous['environment'] = record.get('suite_environment', {})
            previous['log'] = f'offline-suite-failed-attempt-{len(record.get("suite_attempts", [])) + 1}.txt'
            (OUT / record['suite']['log']).replace(OUT / previous['log'])
            record.setdefault('suite_attempts', []).append(previous)
        record['suite_execution_context'] = ('reviewed sandbox escalation' if '--reviewed-escalation' in sys.argv
                                              else 'default sandbox')
        run_suite(record, dict(os.environ, MPLBACKEND='Agg'))
        print('PASS: offline suite with workspace temporary storage')
        return
    record = {'started_utc': datetime.now(timezone.utc).isoformat(), 'python': sys.version,
              'executable': str(Path(sys.executable).relative_to(ROOT)), 'platform': platform.platform(),
              'backend': plt.get_backend(),
              'mode': 'real Tk windows; scripted callbacks and dispatched mouse events; figure exports',
              'language_outputs': 'recorded responses; attention is hand-authored didactic data',
              'packages': {n: importlib.metadata.version(n) for n in
                           ('numpy', 'matplotlib', 'Pillow', 'torch', 'ultralytics')},
              'provenance_sha256': sha(GSS / 'origem.json'), 'entries': []}
    env = dict(os.environ, MPLBACKEND='Agg', FORMACAO_ML_NO_PAUSE='1')
    for number in range(3, 7):
        path = next((GSS / 'modulo2').glob(f'*_0{number}_*.py'))
        result = run([sys.executable, path], f'entry-{number:02}.txt', env)
        result.update(path=str(path.relative_to(ROOT)), sha256=sha(path))
        record['entries'].append(result)
        assert result['exit_code'] == 0, result

    module = load(3)
    ui = module.AttentionInterface()
    ui.toggle_matrix()
    masked = module.attention_matrix(True)
    unmasked = module.attention_matrix(False)
    assert np.allclose(masked.sum(axis=1), 1) and np.allclose(unmasked.sum(axis=1), 1)
    assert np.count_nonzero(np.triu(masked, 1)) == 0
    record['attention'] = {'tokens': list(module.TOKENS), 'causal_matrix': masked.tolist(),
                           'bidirectional_matrix': unmasked.tolist(),
                           'initial_query': ui.query, 'causal_explanation': ui.explanation.get_text()}
    render(ui, '03-causal')
    ui.toggle_mask()
    record['attention']['bidirectional_explanation'] = ui.explanation.get_text()
    render(ui, '03-bidirectional')
    click(ui, ui.matrix_axis, (0, 1))
    assert ui.query == 1
    ui.previous_word()
    assert ui.query == 0
    ui.next_word()
    ui.reset()
    assert ui.query == module.QUERY_A and ui.causal
    record['attention']['matrix_click_navigation_reset'] = 'PASS'
    plt.close(ui.figure)

    module = load(4)
    ui = module.NextTokenInterface(module.RecordedNextTokenSource())
    record['generation'] = {'initial_step': asdict(ui.step), 'settings': [], 'contexts': []}
    for temperature, top_p in ((.1, 1), (1, 1), (2, 1), (1, .5)):
        ui.temperature.set_val(temperature)
        ui.top_p.set_val(top_p)
        probabilities, kept = module.selection_distribution(ui.step, temperature, top_p)
        record['generation']['settings'].append({'temperature': temperature, 'top_p': top_p,
                                                 'distribution': probabilities.tolist(),
                                                 'kept': kept.tolist()})
        assert np.isclose(probabilities.sum(), 1)
    render(ui, '04-sampling-settings')
    for _ in module.CONTEXTS:
        start = ui.context
        for _ in range(3):
            ui.choose_greedy()
        greedy = ui.context
        ui.undo()
        undone = ui.context
        ui.restart()
        ui.choose_sample()
        sampled = ui.context
        ui.restart()
        ui.choose_sample()
        assert ui.context == sampled, 'seeded restart must repeat the sampled choice'
        record['generation']['contexts'].append({'start': start, 'greedy_three_steps': greedy,
                                                 'undo': undone, 'sampled': sampled,
                                                 'sample_message': ui.message})
        render(ui, f'04-context-{ui.context_index}')
        ui.next_context()
    # Exercise the recording boundary honestly; an unavailable continuation is rolled back.
    missing = None
    for index in range(len(ui.step.options)):
        ui.restart()
        ui._append(index, 'scripted candidate')
        if not ui.generated:
            missing = ui.message
            break
    record['generation']['unrecorded_branch_message'] = missing
    ui.restart()
    for _ in range(module.MAX_NEW_TOKENS + 1):
        ui.choose_greedy()
    record['generation']['ending'] = {'context': ui.context, 'message': ui.message,
                                      'new_tokens': len(ui.generated), 'is_end': ui.step.is_end}
    plt.close(ui.figure)

    module = load(5)
    ui = module.PromptLabInterface(module.RecordedPromptRunner())
    record['prompts'] = []
    def save_prompt(label):
        assert ui.answers
        record['prompts'].append({'label': label, 'setup': asdict(ui.setup),
                                  'temperature': ui.temperature, 'max_tokens': ui.max_tokens,
                                  'prompt': module.build_prompt(ui.setup),
                                  'reference': module.reference_for(ui.setup),
                                  'answers': [asdict(a) for a in ui.answers]})
        render(ui, '05-' + label)
    ui.send_repeated()
    save_prompt('classification-baseline')
    ui.toggle_rule()
    ui.send_repeated()
    save_prompt('classification-rule')
    ui.cycle_examples()
    ui.cycle_examples()
    ui.send_once()
    save_prompt('classification-examples')
    ui.cycle_temperature()
    ui.send_repeated()
    save_prompt('classification-temperature')
    ui.cycle_task()
    ui.send_once()
    save_prompt('summary')
    ui.cycle_task()
    ui.send_once()
    save_prompt('extraction')
    ui.cycle_max_tokens()
    ui.send_once()
    save_prompt('extraction-short')
    ui.clear_answers()
    assert not ui.answers
    plt.close(ui.figure)

    module = load(6)
    ui = module.VisionInterface(module.RecordedVisionRunner())
    record['image_text'] = []
    for _ in ui.images:
        for _ in module.REQUESTS:
            ui.ask()
            deadline = time.monotonic() + 30
            while ui._busy():
                ui.figure.canvas.flush_events()
                assert time.monotonic() < deadline
                time.sleep(.01)
            ui.poll()
            assert ui.answer is not None, ui.message
            record['image_text'].append({'image': asdict(ui.image),
                                         'input_sha256': sha(module.image_path(ui.image)),
                                         'request': ui.request,
                                         'prompt': module.request_text(ui.image, ui.request),
                                         'answer': asdict(ui.answer)})
            render(ui, f'06-{ui.image.key}-{module.REQUESTS.index(ui.request)}')
            ui.next_request()
        ui.next_image()
    plt.close(ui.figure)
    record['recording_hashes'] = {p.name: sha(p) for p in
                                (GSS / 'modulo2/respostas_gravadas').glob('*.json')}
    run_suite(record, env)
    print('PASS: four language entries, scripted Tk walkthroughs, and offline unit suite')


if __name__ == '__main__':
    main()
