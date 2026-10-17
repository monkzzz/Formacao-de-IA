"""Validate preservation, actual Issue records and scoped bootstrap evidence."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
STARTER = ROOT / 'participant-work/starter'
BASELINE = '4342c320a0f570de729f8fc517850c9cebb6767d'


def git(*args):
    return subprocess.check_output(['rtk', 'proxy', 'git', *args], cwd=ROOT)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    output = HERE / 'bootstrap-planning-validation.json'
    output.write_text(json.dumps({'status': 'RUNNING'}) + '\n', encoding='utf-8')
    fixture_record = HERE / 'bootstrap-fixture-context.json'
    if not fixture_record.exists():
        fixture = HERE / '.bootstrap-fixture/context'
        saved = {p.name: {'sha256': digest(p), 'content': p.read_bytes().decode('utf-8')}
                 for p in sorted(fixture.glob('*.md'))}
        assert len(saved) == 3
        fixture_record.write_text(json.dumps({
            'scope': 'Actual final disposable context from controlled synthetic approval; not real participant requirements',
            'files': saved}, indent=2) + '\n', encoding='utf-8')
    fixture_data = json.loads(fixture_record.read_text(encoding='utf-8'))
    for item in fixture_data['files'].values():
        assert hashlib.sha256(item['content'].encode('utf-8')).hexdigest() == item['sha256']
    versioned = [STARTER / '.github/skills/bootstrap-project/SKILL.md',
                 *sorted((STARTER / 'context').glob('*.md'))]
    version = {
        'source_baseline': BASELINE, 'skill_version': '1.0.0', 'context_version': '1.0.0',
        'context_authority': 'Participant instruction to maintain existing dia2-local development and website, after context proposal; no new technical design or publication approval',
        'files': {p.relative_to(ROOT).as_posix(): digest(p) for p in versioned},
        'generic_archive': 'starter-generic-1.0.0.json',
        'limits': ['retrospective scope confirmation, not original design approval',
                   'explicit chosen-assistant tests, not native Copilot discovery',
                   'Git history versions source; no standalone release/tag claimed'],
    }
    (HERE / 'bootstrap-context-version.json').write_text(json.dumps(version, indent=2) + '\n', encoding='utf-8')
    unchanged = [STARTER / 'AGENTS.md', STARTER / '.gitignore',
                 STARTER / '.github/copilot-instructions.md',
                 *sorted((STARTER / 'procedures').glob('*.md')),
                 STARTER / 'capabilities/README.md', STARTER / 'capabilities/cli.md',
                 STARTER / 'capabilities/mcp.md', STARTER / 'evidence/README.md',
                 STARTER / 'knowledge/README.md']
    for path in unchanged:
        assert path.read_bytes() == git('show', f'{BASELINE}:{path.relative_to(ROOT).as_posix()}'), path
    assert not git('diff', BASELINE, '--name-only', '--', 'Dia1', 'Dia2', 'dia2-local').strip()
    before = git('show', f'{BASELINE}:TASKS.md').decode('utf-8')
    after = (ROOT / 'TASKS.md').read_text(encoding='utf-8')
    old = re.findall(r'^- \[([ x])\] (.*)', before, re.M)
    new = re.findall(r'^- \[([ x])\] (.*)', after, re.M)
    pending = [i for i, (status, _) in enumerate(old) if status == ' ']
    affected = [i for i, (a, b) in enumerate(zip(old, new)) if a != b]
    assert len(old) == len(new) and affected == pending[:10], affected
    completed = [i for i in affected if new[i][0] == 'x']
    assert completed == pending[:8] + pending[9:10]
    assert new[pending[8]][0] == ' ', 'Unsent instructor request must remain incomplete'
    public = json.loads((HERE / 'github-issues-verified.json').read_text(encoding='utf-8'))
    initial = json.loads((HERE / 'github-issues-before.json').read_text(encoding='utf-8'))
    assert initial['status'] == 'PASS' and initial['issues'] == []
    plan = json.loads((HERE / 'issue-plan.json').read_text(encoding='utf-8'))
    published = {x['title']: x for x in public['issues']}
    assert len(plan) == 6 and len(published) == 6
    numbers = {}
    for item in plan:
        issue = published[item['title']]
        assert issue['state'] == 'open' and issue['url'].startswith('https://github.com/monkzzz/Formacao-de-IA/issues/')
        assert (HERE / item['body_file']).read_text(encoding='utf-8').strip() in issue['body']
        for dependency in item['depends_on']:
            assert numbers[dependency] in issue['body']
        numbers[item['key']] = issue['url']
    model = ROOT / 'dia2-local/dist/model/captcha-v3/digits'
    manifest = json.loads((model / 'manifest.json').read_text(encoding='utf-8'))
    assert digest(model / 'weights.bin') == manifest['sha256'] == 'd962c7f1aefd4f86cf9fcc621e30a1e8fbbce092c5a47ab3dd88e0f64573b42c'
    assert (model / 'weights.bin').stat().st_size == manifest['bytes'] == 1090472
    paths = [ROOT / 'TASKS.md', *sorted(STARTER.rglob('*.md')),
             *[HERE / name for name in ['bootstrap-next-ten.md', 'bootstrap-behavior.md',
                 'bootstrap-recovery.md', 'classifier-specification.md', 'issue-register.md',
                 'instructor-process-request.md']], *sorted((HERE / 'issues').glob('*.md'))]
    links = anchors = 0
    for path in paths:
        prose = re.sub(r'^```[^\n]*\n.*?^```\s*$', '', path.read_text(encoding='utf-8-sig'), flags=re.M | re.S)
        # Quoted fixture proposals use fixture-relative links, not report links.
        prose = re.sub(r'^>.*$', '', prose, flags=re.M)
        for target in re.findall(r'\]\(([^)]+)\)', prose):
            if '://' in target:
                continue
            filename, _, anchor = unquote(target).partition('#')
            dest = (path.parent / filename).resolve() if filename else path
            assert dest.exists(), (path, target)
            links += 1
            if anchor:
                headings = re.findall(r'^#+ (.*)', dest.read_text(encoding='utf-8'), re.M)
                slugs = [re.sub(r'[^\w\- ]', '', h.lower()).replace(' ', '-') for h in headings]
                assert anchor in slugs, (path, target)
                anchors += 1
    result = {
        'executed_utc': datetime.now(timezone.utc).isoformat(), 'baseline': BASELINE,
        'status': 'PASS', 'tasks_attempted': 10, 'tasks_completed': 9,
        'pending': 'Instructor request delivery/acceptance; no recipient/channel',
        'real_issues_verified': len(published), 'local_links': links, 'heading_anchors': anchors,
        'generic_files_unchanged': len(unchanged), 'versioned_files': version['files'],
        'checks': ['exact next ten checklist scope, nine complete', 'unsent request remains open',
                   'real public Issues and dependency URLs', 'generic rules/procedures unchanged',
                   'course/classifier source unchanged', 'existing weight hash and byte count',
                   'local links and anchors', 'version hashes'],
        'limits': ['does not prove Copilot discovery or instructor acceptance',
                   'behavior has separate actual-session evidence',
                   'no retraining, official evaluation or production change'],
    }
    output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
