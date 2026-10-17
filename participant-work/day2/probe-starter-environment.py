"""Read-only local capability probes; evidence stays outside the generic starter."""
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).with_name('starter-environment.json')
checks = []
for name, command in (
    ('rtk', ['rtk', '--version']),
    ('git', ['rtk', 'proxy', 'git', '--version']),
    ('ripgrep', ['rtk', 'proxy', 'rg', '--version']),
    ('powershell', ['rtk', 'proxy', 'powershell', '-NoProfile', '-Command', '$PSVersionTable.PSVersion.ToString()']),
    ('gss-python', [sys.executable, '--version']),
    ('repository-status', ['rtk', 'proxy', 'git', 'status', '--short']),
):
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=30)
    checks.append({'name': name, 'command': command, 'cwd': '.', 'exit_code': result.returncode,
                   'stdout': result.stdout, 'stderr': result.stderr,
                   'status': 'verified' if result.returncode == 0 else 'unavailable'})
record = {'executed_utc': datetime.now(timezone.utc).isoformat(),
          'scope': 'course workspace only; executable/version/status probes, not remote authentication',
          'checks': checks,
          'optional_path_discovery': {name: {'path': shutil.which(name),
                                             'status': 'present, not invoked' if shutil.which(name)
                                             else 'not found on current PATH'}
                                      for name in ('gh', 'node', 'npm')},
          'skills': {'status': 'advertised in session catalog; not invoked for this batch',
                     'project_skills': 'none; bootstrap implementation deferred'},
          'mcp': {'status': 'session tool metadata inspected; no service calls made',
                  'project_integration': 'none selected',
                  'authentication_and_writes': 'NOT RUN'}}
OUT.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
assert all(c['exit_code'] == 0 for c in checks)
print('PASS: six read-only local probes; optional capabilities remain separately labelled')
