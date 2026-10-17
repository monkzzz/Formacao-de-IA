"""Validate the ten-task batch against its fixed pre-batch commit."""
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
BASELINE = 'fbf1af3'
HERE = ROOT / 'participant-work'
GSS = ROOT / 'Dia1/Exercicios-GSS'
OUT = HERE / 'day1/gss-language-final-evidence'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    evidence = json.loads((OUT / 'execution.json').read_text(encoding='utf-8'))
    assert len(evidence['entries']) == 4
    for entry in evidence['entries']:
        assert entry['exit_code'] == 0
        assert sha(ROOT / entry['path']) == entry['sha256']
        assert (OUT / entry['log']).exists()
    assert sha(GSS / 'origem.json') == evidence['provenance_sha256']
    for name, digest in evidence['recording_hashes'].items():
        assert sha(GSS / 'modulo2/respostas_gravadas' / name) == digest
    assert evidence['suite']['exit_code'] == 0
    suite = (OUT / evidence['suite']['log']).read_text(encoding='utf-8')
    assert re.search(r'Ran 125 tests in [\d.]+s\s+OK\s*$', suite), suite[-300:]
    assert evidence['attention']['matrix_click_navigation_reset'] == 'PASS'
    assert len(evidence['generation']['contexts']) == 3
    assert evidence['generation']['unrecorded_branch_message']
    assert len(evidence['prompts']) == 7 and len(evidence['image_text']) == 9
    assert evidence['prompts'][-1]['answers'][0]['finish_reason'] == 'length'
    for item in evidence['image_text']:
        directory = GSS / ('recursos/modulo2' if item['image']['is_generated'] else 'modulo2/imagens')
        assert sha(directory / item['image']['file_name']) == item['input_sha256']
    images = sorted(OUT.glob('*.png'))
    assert len(images) == 22
    from PIL import Image, ImageDraw, ImageOps, ImageStat
    for path in images:
        with Image.open(path) as source:
            assert max(ImageStat.Stat(source.convert('RGB')).stddev) > 10, path
    # Ignored contact sheets assist visual review without becoming submission artifacts.
    contacts = GSS / '.cache/language-review'
    contacts.mkdir(parents=True, exist_ok=True)
    for start in range(0, len(images), 4):
        sheet = Image.new('RGB', (1600, 1000), 'white')
        draw = ImageDraw.Draw(sheet)
        for index, path in enumerate(images[start:start + 4]):
            x, y = (index % 2) * 800, (index // 2) * 500
            with Image.open(path) as source:
                thumb = ImageOps.contain(source.convert('RGB'), (800, 470))
                sheet.paste(thumb, (x, y + 25))
            draw.text((x + 10, y + 5), path.name, fill='black')
        sheet.save(contacts / f'contact-{start // 4 + 1}.png')

    before = subprocess.check_output(['rtk', 'proxy', 'git', 'show', f'{BASELINE}:TASKS.md'], cwd=ROOT).decode('utf-8')
    after = (ROOT / 'TASKS.md').read_text(encoding='utf-8')
    old = re.findall(r'^- \[([ x])\] (.*)', before, re.M)
    new = re.findall(r'^- \[([ x])\] (.*)', after, re.M)
    changed = [i for i, (a, b) in enumerate(zip(old, new)) if a != b]
    pending = [i for i, (status, _) in enumerate(old) if status == ' ']
    assert len(old) == len(new) and changed == pending[:10], changed
    assert all(new[i][0] == 'x' for i in changed)
    paths = [ROOT / 'TASKS.md', HERE / 'day1/README.md', HERE / 'day1/gss-language-final.md',
             HERE / 'day2/starter-preparation.md', *sorted((HERE / 'starter').rglob('*.md'))]
    links = anchors = 0
    for path in paths:
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
            if '://' in target:
                continue
            filename, _, anchor = unquote(target).partition('#')
            dest = (path.parent / filename).resolve() if filename else path
            assert dest.exists(), (path, target)
            # Every internal starter link must survive copying that directory alone.
            if path.is_relative_to(HERE / 'starter'):
                assert dest.is_relative_to(HERE / 'starter'), (path, target)
            links += 1
            if anchor:
                headings = re.findall(r'^#+ (.*)', dest.read_text(encoding='utf-8'), re.M)
                slugs = [re.sub(r'[^\w\- ]', '', h.lower()).replace(' ', '-') for h in headings]
                assert anchor in slugs, (path, target)
                anchors += 1
    probes = json.loads((HERE / 'day2/starter-environment.json').read_text(encoding='utf-8'))
    assert len(probes['checks']) == 6 and all(c['exit_code'] == 0 for c in probes['checks'])
    for path in (HERE / 'day1/run-gss-language-final.py', HERE / 'day2/probe-starter-environment.py', Path(__file__)):
        ast.parse(path.read_text(encoding='utf-8'))
    assert not subprocess.check_output(['rtk', 'proxy', 'git', 'diff', '--name-only', BASELINE, '--', 'Dia1', 'Dia2', 'dia2-local'], cwd=ROOT).strip()
    result = {'executed_utc': datetime.now(timezone.utc).isoformat(), 'baseline': BASELINE,
              'status': 'PASS', 'tasks_completed': len(changed), 'local_links': links,
              'heading_anchors': anchors, 'rendered_images': len(images), 'offline_tests': 125,
              'checks': ['entry exits/hashes', 'recording/model-input/provenance hashes',
                         'suite result', 'lesson observations', 'nonblank renderings',
                         'exact next ten tasks', 'links/anchors', 'starter-contained links',
                         'six capability probes', 'Python syntax', 'unchanged course and classifier sources'],
              'limits': ['not a fresh-session behavioral test', 'renderings are not desktop screenshots']}
    (HERE / 'ten-task-validation.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
