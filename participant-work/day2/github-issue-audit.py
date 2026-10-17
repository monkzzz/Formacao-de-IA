"""Read public issue history; optionally publish reviewed local issue bodies.

Authentication stays in memory via Git's configured credential helper.
No credential values are emitted or persisted by this script.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import urllib.error
import urllib.request

HERE = Path(__file__).resolve().parent
REPO = 'monkzzz/Formacao-de-IA'
BASE = f'https://api.github.com/repos/{REPO}'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish', action='store_true')
    parser.add_argument('--enable-issues', action='store_true')
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    headers = {'User-Agent': 'course-task-evidence', 'Accept': 'application/vnd.github+json',
               'X-GitHub-Api-Version': '2022-11-28'}
    if args.publish or args.enable_issues:
        result = subprocess.run(['rtk', 'proxy', 'git', 'credential', 'fill'],
                                input='protocol=https\nhost=github.com\n\n',
                                text=True, capture_output=True, timeout=30,
                                env=__import__('os').environ | {'GIT_TERMINAL_PROMPT': '0'})
        values = dict(line.split('=', 1) for line in result.stdout.splitlines() if '=' in line)
        if result.returncode or not values.get('password'):
            raise SystemExit('Git credential helper did not provide authentication; no secrets logged')
        headers['Authorization'] = 'Bearer ' + values['password']

    def request(url, data=None, method=None):
        payload = json.dumps(data).encode() if data is not None else None
        req = urllib.request.Request(url, data=payload, headers=headers, method=method)
        if payload:
            req.add_header('Content-Type', 'application/json')
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.load(response)

    try:
        if args.enable_issues:
            repository = request(BASE)
            before_enabled = repository['has_issues']
            if not before_enabled:
                repository = request(BASE, {'has_issues': True}, method='PATCH')
            assert repository['has_issues']
            (HERE / 'github-issues-enabled.json').write_text(json.dumps({
                'executed_utc': datetime.now(timezone.utc).isoformat(),
                'repository': REPO, 'has_issues_before': before_enabled,
                'has_issues_after': repository['has_issues'],
                'scope': 'Enable Issues only; no website, branch or deployment settings changed'
            }, indent=2) + '\n', encoding='utf-8')
        issues = []
        page = 1
        while True:
            batch = request(f'{BASE}/issues?state=all&per_page=100&page={page}')
            issues.extend(x for x in batch if 'pull_request' not in x)
            if len(batch) < 100:
                break
            page += 1
        if args.publish:
            plan = json.loads((HERE / 'issue-plan.json').read_text(encoding='utf-8'))
            published = {}
            for item in plan:
                matching = [x for x in issues if x['title'] == item['title']]
                if matching:
                    published[item['key']] = matching[0]
                    continue
                body = (HERE / item['body_file']).read_text(encoding='utf-8')
                if item['depends_on']:
                    body += '\n\nPublished dependencies:\n' + '\n'.join(
                        '- ' + published[key]['html_url'] for key in item['depends_on']) + '\n'
                issue = request(f'{BASE}/issues', {'title': item['title'], 'body': body})
                issues.append(issue)
                published[item['key']] = issue
                # Preserve successful writes even if a later write fails.
                (HERE / 'github-issue-publication.json').write_text(json.dumps({
                    'executed_utc': datetime.now(timezone.utc).isoformat(),
                    'issues': [{'number': x['number'], 'title': x['title'], 'url': x['html_url']}
                               for x in issues]}, indent=2) + '\n', encoding='utf-8')
        record = {'executed_utc': datetime.now(timezone.utc).isoformat(), 'repository': REPO,
                  'status': 'PASS', 'operation': 'publish-and-list' if args.publish else 'public-read',
                  'issues': [{'number': x['number'], 'title': x['title'], 'url': x['html_url'],
                              'state': x['state'], 'created_at': x['created_at'],
                              'body': x.get('body'), 'comments': x['comments']}
                             for x in issues],
                  'limits': ['Issue bodies and counts do not prove original approval',
                             'Comment contents are not fetched by this operation']}
        destination = ('github-issues-verified.json' if args.verify_only else
                       'github-issues-after.json' if args.publish else 'github-issues-before.json')
        (HERE / destination).write_text(
            json.dumps(record, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({'status': record['status'], 'issues': len(issues), 'operation': record['operation']}))
    except urllib.error.HTTPError as error:
        raise SystemExit(f'GitHub HTTP {error.code}; no response body or credentials logged') from None


if __name__ == '__main__':
    main()
