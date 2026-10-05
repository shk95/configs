#!/usr/bin/env python3
"""Bounded GitHub release operations. No host deployment or operating database.
INV repository/bounded-release-automation
INV repository/release-tag-contract
"""
import argparse
import datetime as dt
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import zipfile
from zoneinfo import ZoneInfo

DOMAINS = ('unixlike', 'windows')
FIELDS = {'previous', 'version', 'summary', 'compatibility', 'migration'}
VERSION = re.compile(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\Z')
SHA = re.compile(r'[0-9a-f]{40}\Z')
REFRESH_SUMMARY = 'Refresh permitted Unix-like inputs.'
LEGACY = {
    'unixlike-v2026.08.31': 'a844c146b5e966a42a3a3bb7d8245e24af4c8dcd',
    'windows-v2026.08.31': '05dcfcefe69cc4f01a394364f8d68b06d5abbd5b',
}


def command(*args):
    return subprocess.check_output(args).decode().strip()


def git(*args):
    return command('git', *args)


def repository():
    value = os.environ.get('GITHUB_REPOSITORY') or command('gh', 'repo', 'view', '--json', 'nameWithOwner', '--jq', '.nameWithOwner')
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', value):
        raise ValueError('invalid repository identity')
    return value


def api(path, data=None, binary=False):
    args = ['gh', 'api', f'repos/{repository()}/{path}']
    payload = None
    if data is not None:
        args += ['--method', 'POST', '--input', '-']
        payload = json.dumps(data).encode()
    output = subprocess.check_output(args, input=payload)
    return output if binary else json.loads(output)


def request(path, method, data):
    output = subprocess.check_output(['gh', 'api', f'repos/{repository()}/{path}', '--method', method, '--input', '-'], input=json.dumps(data).encode())
    return json.loads(output) if output.strip() else None


def source_json(source, path):
    return json.loads(git('show', f'{source}:{path}'))


def declaration(source, domain):
    value = source_json(source, f'{domain}/release.json')
    if not isinstance(value, dict) or set(value) != FIELDS or not all(isinstance(v, str) for v in value.values()):
        raise ValueError(f'{domain}: invalid release declaration')
    if not VERSION.fullmatch(value['version']) or value['compatibility'] not in ('patch', 'minor', 'breaking'):
        raise ValueError(f'{domain}: invalid version/compatibility')
    if not value['summary'].strip() or any('\n' in v or '\r' in v for v in value.values()):
        raise ValueError(f'{domain}: release fields must be single-line text')
    previous = value['previous']
    if not SHA.fullmatch(previous) and not re.fullmatch(re.escape(domain) + r'-v[0-9]+(?:\.[0-9]+){2}', previous):
        raise ValueError(f'{domain}: invalid previous release basis')
    git('rev-parse', '--verify', f'{previous}^{{commit}}')
    return value


def tag_name(domain, declaration):
    return f"{domain}-v{declaration['version']}"


def latest(domain):
    names = [name for name in git('tag', '--list', f'{domain}-v*').splitlines() if VERSION.fullmatch(name[len(domain) + 2:])]
    # The calendar tags are outside the SemVer transition, including 2026.08.31.
    names = [name for name in names if name not in LEGACY]
    return max(names, key=lambda name: tuple(map(int, name[len(domain) + 2:].split('.')))) if names else None


def tag_state(domain, source, value):
    name = tag_name(domain, value)
    found = api(f'git/matching-refs/tags/{name}')
    exact = [ref for ref in found if ref['ref'] == f'refs/tags/{name}']
    if not exact:
        return 'missing'
    obj = exact[0]['object']
    if obj['type'] != 'tag':
        raise ValueError(f'{name}: remote tag is not annotated')
    tag = api(f"git/tags/{obj['sha']}")
    required = annotation_fields(domain, source, value)
    if tag['tag'] != name or tag['object']['type'] != 'commit' or tag['object']['sha'] != source:
        raise ValueError(f'{name}: conflicting remote target')
    lines = tag['message'].splitlines()
    if not all(line in lines for line in required):
        raise ValueError(f'{name}: conflicting required annotation')
    return 'done'


def annotation_fields(domain, source, value):
    lines = [f'Domain: {domain}', f"Version: {value['version']}", f'Source: {source}',
             f"Previous: {value['previous']}", f"Summary: {value['summary']}",
             f"Compatibility: {value['compatibility']}", f"Migration: {value['migration']}"]
    if domain == 'windows':
        lines += ['Host: windows-ci', 'Evaluation: passed; native Windows CI',
                  'Build: not applicable; desired-state provider',
                  'Native runtime: passed; native Windows CI fixtures']
    else:
        lines += ['Evaluation: passed; provider CI',
                  'Build: passed; selected matching-system provider fixtures',
                  'Native runtime: passed; provider CI fixtures']
    return lines + ['Deployment: not performed by release', f'Evidence: https://github.com/{repository()}/commit/{source}']


def planned(source):
    parents = git('show', '-s', '--format=%P', source).split()
    if len(parents) != 2:
        return []
    names = set(git('diff', '--name-only', parents[0], source).splitlines())
    return [domain for domain in DOMAINS if f'{domain}/release.json' in names]


def identity_from_zip(data):
    if len(data) > 65536:
        raise ValueError('CI source record archive is too large')
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        item = archive.getinfo('source.json')
        if item.file_size > 4096:
            raise ValueError('CI source record is too large')
        value = json.loads(archive.read(item))
    if set(value) != {'event', 'base', 'head', 'tree'} or value['event'] not in ('push', 'pull_request'):
        raise ValueError('invalid CI source record')
    if not all(isinstance(value[k], str) and SHA.fullmatch(value[k]) for k in ('base', 'head', 'tree')):
        raise ValueError('invalid CI source identities')
    return value


def checked(base, head, tree, event):
    checks = api(f'commits/{head}/check-runs?per_page=100')['check_runs']
    for check in sorted(checks, key=lambda value: value['id'], reverse=True):
        if check['name'] != 'Required checks' or check['app']['id'] != 15368 or check['conclusion'] != 'success':
            continue
        match = re.fullmatch(re.escape(f'https://github.com/{repository()}/actions/runs/') + r'([0-9]+)/job/[0-9]+', check['details_url'])
        if not match:
            continue
        run_id = match[1]
        run = api(f'actions/runs/{run_id}')
        if run['path'] != '.github/workflows/ci.yml' or run['event'] != event or run['conclusion'] != 'success':
            continue
        for artifact in api(f'actions/runs/{run_id}/artifacts')['artifacts']:
            if artifact['name'] == 'ci-source' and not artifact['expired']:
                value = identity_from_zip(api(f"actions/artifacts/{artifact['id']}/zip", binary=True))
                if value == {'event': event, 'base': base, 'head': head, 'tree': tree}:
                    return True
    return False


def merge_tree(base, head):
    return git('merge-tree', '--write-tree', base, head).splitlines()[0]


def validate_versions(base, head):
    paths = set(git('diff', '--name-only', base, head).splitlines())
    domains = [domain for domain in DOMAINS if any(p.startswith(domain + '/') for p in paths)]
    for domain in domains:
        value = declaration(head, domain)
        previous = latest(domain)
        if previous is None or value['previous'] != previous:
            raise ValueError(f'{domain}: refresh declaration against the latest published release')
        before = tuple(map(int, previous[len(domain) + 2:].split('.')))
        after = tuple(map(int, value['version'].split('.')))
        if after <= before or f'{domain}/release.json' not in paths:
            raise ValueError(f'{domain}: changed source requires a new release declaration')
    return domains


def validate_lock(before, after, allowed):
    if before.get('version') != 7 or after.get('version') != 7:
        raise ValueError('unsupported lock format')
    left = before['nodes'][before['root']]['inputs']
    right = after['nodes'][after['root']]['inputs']
    if set(left) != set(right) or not allowed <= set(left):
        raise ValueError('lock input boundary changed')
    seen = set()

    def compare(old_key, new_key, mutable):
        identity = (old_key, new_key, mutable)
        if identity in seen:
            return
        seen.add(identity)
        old, new = before['nodes'][old_key], after['nodes'][new_key]
        if {k: v for k, v in old.items() if k not in ('locked', 'inputs')} != {k: v for k, v in new.items() if k not in ('locked', 'inputs')}:
            raise ValueError('input source declaration changed')
        changing = {'rev', 'narHash', 'lastModified', 'revCount'} if mutable else set()
        if {k: v for k, v in old['locked'].items() if k not in changing} != {k: v for k, v in new['locked'].items() if k not in changing}:
            raise ValueError('non-permitted dependency or source identity changed')
        old_inputs, new_inputs = old.get('inputs', {}), new.get('inputs', {})
        if set(old_inputs) != set(new_inputs):
            raise ValueError('dependency topology changed; use manual review')
        for name, edge in old_inputs.items():
            compare_edge(edge, new_inputs[name], mutable)

    def compare_edge(old, new, mutable):
        if isinstance(old, list):
            if new != old:
                raise ValueError('follows alias changed')
        elif isinstance(old, str) and isinstance(new, str):
            compare(old, new, mutable)
        else:
            raise ValueError('invalid dependency edge')

    for name, edge in left.items():
        compare_edge(edge, right[name], name in allowed)


def automatic(base, head):
    paths = set(git('diff', '--name-only', base, head).splitlines())
    if not paths or not paths <= {'unixlike/flake.lock', 'unixlike/release.json'}:
        return False
    value = declaration(head, 'unixlike')
    prior = latest('unixlike')
    if not prior or value != {'previous': prior, 'version': patch_version(prior), 'summary': REFRESH_SUMMARY, 'compatibility': 'patch', 'migration': ''}:
        return False
    allowed = set(source_json('HEAD', 'unixlike/automatic-refresh-inputs.json'))
    validate_lock(source_json(base, 'unixlike/flake.lock'), source_json(head, 'unixlike/flake.lock'), allowed)
    # Admission also covers all pending domain changes since its previous release.
    cumulative = set(git('diff', '--name-only', f'{prior}^{{commit}}', head, '--', 'unixlike').splitlines())
    return cumulative <= {'unixlike/flake.lock', 'unixlike/release.json'}


def patch_version(previous):
    major, minor, patch = map(int, previous.split('-v', 1)[1].split('.'))
    return f'{major}.{minor}.{patch + 1}'


def inspect(now=None):
    master, dev = git('rev-parse', 'origin/master'), git('rev-parse', 'origin/dev')
    bootstrap = os.environ.get('CONFIGS_RELEASE_BOOTSTRAP_SOURCE', '')
    if bootstrap:
        if not SHA.fullmatch(bootstrap):
            raise ValueError('invalid bootstrap source')
        pending = [d for d in DOMAINS if tag_state(d, bootstrap, declaration(bootstrap, d)) == 'missing']
        if pending:
            return {'action': 'publish', 'source': bootstrap, 'base': master, 'head': bootstrap, 'approval': True}
    for domain in DOMAINS:
        if latest(domain) is None:
            raise ValueError('initial publication needs an explicit bootstrap source')
    pending = [d for d in planned(master) if tag_state(d, master, declaration(master, d)) == 'missing']
    if pending:
        return {'action': 'publish', 'source': master, 'base': master, 'head': master, 'approval': False}
    for domain in DOMAINS:
        value = declaration(master, domain)
        refs = api(f"git/matching-refs/tags/{tag_name(domain, value)}")
        exact = [ref for ref in refs if ref['ref'] == f'refs/tags/{tag_name(domain, value)}']
        if not exact:
            raise ValueError('publication source is ambiguous; specify its original SHA')
        obj = exact[0]['object']
        if obj['type'] != 'tag':
            raise ValueError('published release must be annotated')
        target = api(f"git/tags/{obj['sha']}")['object']['sha']
        tag_state(domain, target, value)
    current = now or dt.datetime.now(ZoneInfo('Asia/Seoul'))
    refresh = [pr for pr in api('pulls?state=open&base=dev&per_page=100') if pr['head']['ref'] == 'feature/unixlike-automatic-refresh' and pr['head']['repo']['full_name'] == repository()]
    if len(refresh) > 1:
        raise ValueError('multiple managed refresh PRs')
    if current.hour < 6:
        if current.hour == 5 and not refresh:
            return {'action': 'refresh', 'base': dev, 'head': dev, 'approval': False}
        return {'action': 'wait', 'reason': 'promotion opens at 06:00 Asia/Seoul'}
    # A single normal promotion per local day; recovery above is independent.
    for pr in api('pulls?state=closed&base=master&sort=updated&direction=desc&per_page=20'):
        if pr['head']['ref'] == 'dev' and pr['head']['repo']['full_name'] == repository() and pr['merged_at'] and dt.datetime.fromisoformat(pr['merged_at'].replace('Z', '+00:00')).astimezone(ZoneInfo('Asia/Seoul')).date() == current.date():
            return {'action': 'wait', 'reason': 'this cycle already promoted'}
    if refresh:
        pr = refresh[0]
        head = pr['head']['sha']
        common = git('merge-base', dev, head)
        if not automatic(common, head):
            raise ValueError('managed refresh includes unpermitted content')
        current_base = subprocess.call(['git', 'merge-base', '--is-ancestor', dev, head], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0
        if not current_base and current.hour < 7:
            return {'action': 'refresh', 'base': dev, 'head': dev, 'approval': False}
        if current_base:
            tree = merge_tree(dev, head)
            if checked(dev, head, tree, 'pull_request'):
                return {'action': 'refresh-merge', 'number': pr['number'], 'base': dev, 'head': head, 'tree': tree, 'approval': False}
        if current.hour < 7:
            return {'action': 'wait', 'reason': 'refresh pending; runner is released'}
    if git('rev-parse', f'{master}^{{tree}}') == git('rev-parse', f'{dev}^{{tree}}'):
        return {'action': 'none'}
    validate_versions(master, dev)
    tree = merge_tree(master, dev)
    promotions = api('pulls?state=open&base=master&per_page=100')
    if promotions:
        if len(promotions) != 1 or promotions[0]['head']['ref'] != 'dev' or promotions[0]['head']['repo']['full_name'] != repository():
            raise ValueError('unexpected promotion PR')
        pr = promotions[0]
        if not checked(master, dev, tree, 'pull_request'):
            return {'action': 'wait', 'reason': 'promotion Required checks pending'}
        return {'action': 'promote', 'number': pr['number'], 'base': master, 'head': dev, 'tree': tree, 'approval': not automatic(master, dev)}
    return {'action': 'promotion-pr', 'base': master, 'head': dev, 'tree': tree, 'approval': False}


def write_guard():
    if os.environ.get('CONFIGS_RELEASE_ENABLED') != '1' or not os.environ.get('GH_TOKEN'):
        raise ValueError('release writes need explicit enablement and writer credentials')
    git('fetch', '--quiet', 'origin', '+refs/heads/dev:refs/remotes/origin/dev', '+refs/heads/master:refs/remotes/origin/master', '--tags')
    if subprocess.call(['git', 'merge-base', '--is-ancestor', 'HEAD', 'origin/master'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL):
        raise ValueError('writer implementation is not accepted master source')


def publish(source):
    source = git('rev-parse', '--verify', f'{source}^{{commit}}')
    git('merge-base', '--is-ancestor', source, 'origin/master')
    bootstrap = source == os.environ.get('CONFIGS_RELEASE_BOOTSTRAP_SOURCE')
    domains = list(DOMAINS) if bootstrap else planned(source)
    if not domains:
        raise ValueError('source is not an identified promotion publication')
    missing = [d for d in domains if tag_state(d, source, declaration(source, d)) == 'missing']
    if not missing:
        return
    parents = git('show', '-s', '--format=%P', source).split()
    tree = git('rev-parse', f'{source}^{{tree}}')
    if bootstrap:
        base = os.environ.get('CONFIGS_RECONSTRUCTION_BASE', 'a886934736f701e85ab5c79fba58b155218d99d1')
        verified = checked(base, source, tree, 'push')
    else:
        prs = api(f'commits/{source}/pulls')
        verified = len(parents) == 2 and any(pr['merged_at'] and pr['base']['ref'] == 'master' and pr['head']['ref'] == 'dev' and pr['head']['repo']['full_name'] == repository() and pr['merge_commit_sha'] == source for pr in prs) and checked(parents[0], parents[1], tree, 'pull_request')
    if not verified:
        raise ValueError('publication lacks matching Required checks for its actual source tree')
    for domain in missing:
        value = declaration(source, domain)
        lines = annotation_fields(domain, source, value)
        obj = api('git/tags', {'tag': tag_name(domain, value), 'message': '\n'.join(lines), 'object': source, 'type': 'commit'})
        try:
            api('git/refs', {'ref': f'refs/tags/{tag_name(domain, value)}', 'sha': obj['sha']})
        except subprocess.CalledProcessError:
            if tag_state(domain, source, value) != 'done':
                raise
        if tag_state(domain, source, value) != 'done':
            raise ValueError('remote publication not confirmed')


def advance(expected_head, expected_base, approved=False):
    action = inspect()
    if action['action'] in ('wait', 'none'):
        return action
    if action.get('head') != expected_head or action.get('base') != expected_base:
        raise ValueError('candidate changed after preparation/approval')
    if action['approval'] and not approved:
        raise ValueError('this candidate requires Environment review')
    if action['action'] == 'publish':
        publish(action['source'])
    elif action['action'] == 'promotion-pr':
        ensure_pr('dev', 'master', 'Promote accepted dev source', 'Source promotion only; domain publication is handled separately.')
    else:
        try:
            result = request(f"pulls/{action['number']}/merge", 'PUT', {'sha': action['head'], 'merge_method': 'merge'})
            if not result['merged']:
                raise ValueError('protected merge did not complete')
        except subprocess.CalledProcessError:
            pass  # A lost response is resolved by the remote PR, never a blind retry.
        remote = api(f"pulls/{action['number']}")
        if not remote['merged'] or remote['head']['sha'] != action['head']:
            raise ValueError('remote merge is not confirmed')
        merged = remote['merge_commit_sha']
        git('fetch', '--quiet', 'origin')
        if git('show', '-s', '--format=%P', merged).split() != [action['base'], action['head']] or git('rev-parse', f'{merged}^{{tree}}') != action['tree']:
            raise ValueError('actual merge changed; no tags published')
        if action['action'] == 'promote' and planned(merged):
            publish(merged)
    return action


def ensure_pr(head, base, title, body):
    existing = [pr for pr in api(f'pulls?state=open&base={base}&per_page=100')
                if pr['head']['ref'] == head and pr['head']['repo']['full_name'] == repository()]
    if len(existing) > 1:
        raise ValueError('multiple matching pull requests')
    if existing:
        return existing[0]
    try:
        return api('pulls', {'head': head, 'base': base, 'title': title, 'body': body})
    except subprocess.CalledProcessError:
        existing = [pr for pr in api(f'pulls?state=open&base={base}&per_page=100')
                    if pr['head']['ref'] == head and pr['head']['repo']['full_name'] == repository()]
        if len(existing) != 1:
            raise ValueError('remote PR creation is not confirmed')
        return existing[0]


def refresh_pr(base, lock_path):
    if not SHA.fullmatch(base) or git('rev-parse', 'origin/dev') != base:
        raise ValueError('refresh base changed')
    if any(tag_state(d, git('rev-parse', f'{latest(d)}^{{commit}}'), declaration('origin/master', d)) != 'done' for d in DOMAINS):
        raise ValueError('complete previous publication before refreshing')
    path = Path(lock_path)
    if path.is_symlink() or path.stat().st_size > 1024 * 1024:
        raise ValueError('invalid refresh lock artifact')
    data = path.read_text()
    lock = json.loads(data)
    before = source_json(base, 'unixlike/flake.lock')
    allowed = set(source_json('HEAD', 'unixlike/automatic-refresh-inputs.json'))
    validate_lock(before, lock, allowed)
    if before == lock:
        return {'action': 'none'}
    # A patch cannot silently relabel pending human Unix-like changes.
    prior = latest('unixlike')
    changed = set(git('diff', '--name-only', f'{prior}^{{commit}}', base, '--', 'unixlike').splitlines())
    if not changed <= {'unixlike/flake.lock', 'unixlike/release.json'}:
        raise ValueError('pending human Unix-like changes require a source-owned declaration')
    value = {'previous': prior, 'version': patch_version(prior), 'summary': REFRESH_SUMMARY,
             'compatibility': 'patch', 'migration': ''}
    branch = 'feature/unixlike-automatic-refresh'
    matching = api(f'git/matching-refs/heads/{branch}')
    exact = [ref for ref in matching if ref['ref'] == f'refs/heads/{branch}']
    parent = base
    if exact:
        parent = exact[0]['object']['sha']
        git('fetch', '--quiet', 'origin', f'refs/heads/{branch}:refs/remotes/origin/{branch}')
        if git('rev-parse', f'{base}^{{tree}}') != git('rev-parse', f'{parent}^{{tree}}') and not automatic(git('merge-base', base, parent), parent):
            # A branch already merged into dev is a valid previous cycle.
            if subprocess.call(['git', 'merge-base', '--is-ancestor', parent, base], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL):
                raise ValueError('managed branch contains unpermitted changes')
        if subprocess.call(['git', 'merge-base', '--is-ancestor', base, parent], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0 and source_json(parent, 'unixlike/flake.lock') == lock and source_json(parent, 'unixlike/release.json') == value:
            return ensure_pr(branch, 'dev', 'Refresh permitted Unix-like inputs', 'Automatic patch: four permitted inputs only.')
    # Base the new tree on current dev and append history without force pushes.
    entries = []
    for name, content in [('unixlike/flake.lock', data), ('unixlike/release.json', json.dumps(value, indent=2) + '\n')]:
        blob = api('git/blobs', {'content': content, 'encoding': 'utf-8'})
        entries.append({'path': name, 'mode': '100644', 'type': 'blob', 'sha': blob['sha']})
    tree = api('git/trees', {'base_tree': git('rev-parse', f'{base}^{{tree}}'), 'tree': entries})
    if parent != base and subprocess.call(['git', 'merge-base', '--is-ancestor', parent, base], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL):
        # Preserve existing refresh content in a normal synchronization merge.
        sync_entries = [{'path': name, 'mode': '100644', 'type': 'blob', 'sha': git('rev-parse', f'{parent}:{name}')}
                        for name in ('unixlike/flake.lock', 'unixlike/release.json')]
        sync_tree = api('git/trees', {'base_tree': git('rev-parse', f'{base}^{{tree}}'), 'tree': sync_entries})
        if sync_tree['sha'] != merge_tree(parent, base):
            raise ValueError('refresh synchronization differs from the normal merge result')
        sync = api('git/commits', {'message': 'Merge dev into managed refresh', 'tree': sync_tree['sha'], 'parents': [parent, base]})
        parent = sync['sha']
        commit = sync if tree['sha'] == sync_tree['sha'] else None
    else:
        parent = base
        commit = None
    if commit is None:
        commit = api('git/commits', {'message': 'chore(unixlike-deps): refresh permitted inputs', 'tree': tree['sha'], 'parents': [parent]})
    try:
        if exact:
            request(f'git/refs/heads/{branch}', 'PATCH', {'sha': commit['sha'], 'force': False})
        else:
            api('git/refs', {'ref': f'refs/heads/{branch}', 'sha': commit['sha']})
    except subprocess.CalledProcessError:
        pass
    remote = api(f'git/ref/heads/{branch}')
    if remote['object']['sha'] != commit['sha']:
        raise ValueError('remote refresh branch write is not confirmed')
    return ensure_pr(branch, 'dev', 'Refresh permitted Unix-like inputs', 'Automatic patch: four permitted inputs only.')


def pending_review(action):
    if not action.get('approval'):
        return False
    name = f"Approve {action['head']} on {action['base']}"
    for run in api('actions/workflows/release.yml/runs?status=waiting&per_page=100')['workflow_runs']:
        if str(run['id']) == os.environ.get('GITHUB_RUN_ID'):
            continue
        jobs = api(f"actions/runs/{run['id']}/jobs?per_page=100")['jobs']
        if any(job['name'] == name and job['conclusion'] is None for job in jobs):
            return True
    return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='operation', required=True)
    diagnosis = sub.add_parser('inspect')
    diagnosis.add_argument('--source')
    step = sub.add_parser('advance')
    step.add_argument('--head', required=True)
    step.add_argument('--base', required=True)
    step.add_argument('--approved', action='store_true')
    publication = sub.add_parser('publish')
    publication.add_argument('--source', required=True)
    publication.add_argument('--approved', action='store_true')
    refresh = sub.add_parser('refresh-pr')
    refresh.add_argument('--base', required=True)
    refresh.add_argument('--lock', required=True)
    args = parser.parse_args()
    try:
        if args.operation == 'inspect':
            if os.environ.get('CONFIGS_RELEASE_ENABLED') != '1':
                result = {'action': 'disabled'}
            else:
                git('fetch', '--quiet', 'origin', '--tags')
                if args.source:
                    if not SHA.fullmatch(args.source):
                        raise ValueError('recovery source must be a full commit SHA')
                    git('merge-base', '--is-ancestor', args.source, 'origin/master')
                    result = {'action': 'recover', 'head': args.source, 'base': args.source, 'approval': True}
                else:
                    result = inspect()
                if pending_review(result):
                    result = {'action': 'wait', 'reason': 'same candidate already awaits Environment review'}
            print(json.dumps(result))
        else:
            write_guard()
            if args.operation == 'publish':
                if not args.approved:
                    raise ValueError('explicit source recovery/bootstrap requires Environment review')
                publish(args.source)
            elif args.operation == 'refresh-pr':
                print(json.dumps(refresh_pr(args.base, args.lock)))
            else:
                print(json.dumps(advance(args.head, args.base, args.approved)))
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError, json.JSONDecodeError) as error:
        print(f'release: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
