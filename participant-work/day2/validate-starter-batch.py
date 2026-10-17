"""Validate the scoped starter batch without executing models or course demos."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote
import zipfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
STARTER = ROOT / 'participant-work/starter'
BASELINE = 'cc349efac3aebfc26dafbb73724ca0ac85694d9c'


def git(*args):
    return subprocess.check_output(['rtk', 'proxy', 'git', *args], cwd=ROOT)


def main():
    # A failure leaves a truthful non-success record instead of a stale PASS.
    (HERE / 'starter-batch-validation.json').write_text(
        json.dumps({'status': 'RUNNING', 'baseline': BASELINE}) + '\n', encoding='utf-8')
    manifest = json.loads((HERE / 'starter-generic-1.0.0.json').read_text(encoding='utf-8'))
    archive = HERE / manifest['archive']
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == manifest['archive_sha256']
    assert manifest['source_commit'] == BASELINE
    with zipfile.ZipFile(archive) as snapshot:
        assert sorted(snapshot.namelist()) == sorted(manifest['files'])
        for name, digest in manifest['files'].items():
            data = snapshot.read(name)
            assert hashlib.sha256(data).hexdigest() == digest
            assert data == git('show', f'{BASELINE}:participant-work/starter/{name}')
        assert not any('/skills/' in name for name in snapshot.namelist())
    before = git('show', f'{BASELINE}:TASKS.md').decode('utf-8')
    after = (ROOT / 'TASKS.md').read_text(encoding='utf-8')
    old = re.findall(r'^- \[([ x])\] (.*)', before, re.M)
    new = re.findall(r'^- \[([ x])\] (.*)', after, re.M)
    changed = [i for i, (a, b) in enumerate(zip(old, new)) if a != b]
    pending = [i for i, (status, _) in enumerate(old) if status == ' ']
    assert len(old) == len(new) and changed == pending[:5], changed
    assert all(new[i][0] == 'x' for i in changed)
    paths = [ROOT / 'TASKS.md', HERE / 'starter-next-five.md',
             HERE / 'starter-reference-selection.md', HERE / 'bootstrap-research.md',
             HERE / 'starter-fresh-session.md', *sorted(STARTER.rglob('*.md'))]
    links = anchors = 0
    for path in paths:
        # Embedded experiment scripts contain fixture-relative Markdown, not report links.
        prose = re.sub(r'^```[^\n]*\n.*?^```\s*$', '',
                       path.read_text(encoding='utf-8'), flags=re.M | re.S)
        for target in re.findall(r'\]\(([^)]+)\)', prose):
            if '://' in target:
                continue
            filename, _, anchor = unquote(target).partition('#')
            dest = (path.parent / filename).resolve() if filename else path
            assert dest.exists(), (path, target)
            if path.is_relative_to(STARTER):
                assert dest.is_relative_to(STARTER), (path, target)
            links += 1
            if anchor:
                headings = re.findall(r'^#+ (.*)', dest.read_text(encoding='utf-8'), re.M)
                slugs = [re.sub(r'[^\w\- ]', '', h.lower()).replace(' ', '-') for h in headings]
                assert anchor in slugs, (path, target)
                anchors += 1
    assert not git('diff', BASELINE, '--name-only', '--', 'Dia1', 'Dia2', 'dia2-local').strip()
    result = {
        'executed_utc': datetime.now(timezone.utc).isoformat(), 'baseline': BASELINE,
        'status': 'PASS', 'tasks_completed': len(changed), 'local_links': links,
        'heading_anchors': anchors, 'archived_files': len(manifest['files']),
        'checks': ['archive hash and per-file hashes', 'archive equals actual baseline source',
                   'archive predates skill', 'exact next five tasks', 'links and anchors',
                   'starter links survive copying', 'unchanged course and classifier sources'],
        'limits': ['does not prove Copilot discovery or interview behavior',
                   'fresh-session behavior has a separate observed report'],
    }
    (HERE / 'starter-batch-validation.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
