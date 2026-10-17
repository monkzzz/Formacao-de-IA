"""Preserve the actual pre-skill starter and create an isolated reuse fixture."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'participant-work/starter'
OUT = Path(__file__).resolve().parent
ARCHIVE = OUT / 'starter-generic-1.0.0.zip'
FIXTURE = OUT / '.starter-reuse-fixture'


def main():
    if ARCHIVE.exists() or FIXTURE.exists():
        raise SystemExit('Refusing to replace preserved snapshot or experiment')
    baseline = subprocess.check_output(
        ['rtk', 'proxy', 'git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    files = sorted(p for p in SOURCE.rglob('*') if p.is_file())
    entries = {}
    with zipfile.ZipFile(ARCHIVE, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            name = path.relative_to(SOURCE).as_posix()
            data = path.read_bytes()
            archive.writestr(name, data)
            entries[name] = hashlib.sha256(data).hexdigest()
    shutil.copytree(SOURCE, FIXTURE)
    record = {
        'version': 'starter-generic-1.0.0', 'source_commit': baseline,
        'sequence': 'Captured existing generic source before bootstrap skill creation; not a reconstruction of an earlier course sequence.',
        'archive': ARCHIVE.name,
        'archive_sha256': hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),
        'files': entries,
        'limits': ['local archive, not standalone publication', 'no classifier context',
                   'README describes historical pre-test status at capture time'],
    }
    (OUT / 'starter-generic-1.0.0.json').write_text(
        json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'archive': str(ARCHIVE), 'files': len(entries), 'fixture': str(FIXTURE)}))


if __name__ == '__main__':
    main()
