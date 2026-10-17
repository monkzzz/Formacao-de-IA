"""Validate this batch's evidence, local links, and checklist changes."""
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).parent
OUT = HERE / 'gss-vision-language-evidence'
GSS = ROOT / 'Dia1/Exercicios-GSS'
record = json.loads((OUT / 'execution.json').read_text(encoding='utf-8'))
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
assert record['pip_check']['exit_code'] == 0
assert len(record['entries']) == 3
for entry in record['entries']:
    assert entry['exit_code'] == 0
    assert sha(ROOT / entry['path']) == entry['sha256']
assert sha(GSS / 'origem.json') == record['provenance_sha256']
for name, digest in record['recording_hashes'].items():
    assert sha(GSS / 'modulo2/respostas_gravadas' / name) == digest
assert len(record['weights']) == 5
for name, info in record['weights'].items():
    assert sha(GSS / '.cache/yolo/models' / name) == info['sha256']
assert {p['task'] for p in record['vision']} == {'detect', 'classify', 'segment', 'pose', 'obb'}
assert record['video']['first_frame'] == 1 and record['video']['next_frame'] == 2
assert record['camera']['capture_unopened']
assert len(record['tokens']) == 4 and record['embeddings']['shape'] == [16, 1024]
assert len(list(OUT.glob('*.png'))) == 10
ast.parse((HERE / 'run-gss-vision-language.py').read_text(encoding='utf-8'))
before = subprocess.check_output(['rtk', 'proxy', 'git', 'show', 'HEAD:TASKS.md'], cwd=ROOT).decode('utf-8')
after = (ROOT / 'TASKS.md').read_text(encoding='utf-8')
old_tasks = re.findall(r'^- \[([ x])\] (.*)', before, re.M)
new_tasks = re.findall(r'^- \[([ x])\] (.*)', after, re.M)
changed = [i for i, (a, b) in enumerate(zip(old_tasks, new_tasks)) if a != b]
pending = [i for i, (status, _) in enumerate(old_tasks) if status == ' ']
assert len(old_tasks) == len(new_tasks) and changed == pending[:5]
assert all(new_tasks[i][0] == 'x' for i in changed)
links = anchors = 0
for path in (ROOT / 'TASKS.md', HERE / 'README.md', HERE / 'gss-vision-language.md'):
    for target in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
        if '://' in target:
            continue
        filename, _, anchor = unquote(target).partition('#')
        dest = path.parent / filename if filename else path
        assert dest.exists(), (path, target)
        links += 1
        if anchor:
            headings = re.findall(r'^#+ (.*)', dest.read_text(encoding='utf-8'), re.M)
            slugs = [re.sub(r'[^\w\- ]', '', h.lower()).replace(' ', '-') for h in headings]
            assert anchor in slugs, (path, target, slugs)
            anchors += 1
print(f'PASS: exactly next five tasks, {links} local links, {anchors} anchors, all evidence hashes, 10 renderings')
