#!/usr/bin/env python3
"""Bounded GitHub release operations. No host deployment or operating database.
INV repository/bounded-release-automation
INV repository/release-tag-contract
"""
import argparse
from itertools import count
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

sys.dont_write_bytecode = True
from github_proof import find_pr
from release_version import VERSION

PATCH_BRANCH = 'feature/unixlike-input-patch-'
FIELDS = {'previous', 'version', 'summary', 'compatibility', 'migration'}
SHA = re.compile(r'[0-9a-f]{40}\Z')
REFRESH_SUMMARY = 'Refresh permitted Unix-like inputs.'
LEGACY = {
    'unixlike-v2026.08.31': 'a844c146b5e966a42a3a3bb7d8245e24af4c8dcd',
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


def tag_state(domain, source, value, *, generated=True, allow_legacy_generated=False, proof=None):
    name = tag_name(domain, value)
    found = api(f'git/matching-refs/tags/{name}')
    exact = [ref for ref in found if ref['ref'] == f'refs/tags/{name}']
    if not exact:
        return 'missing'
    obj = exact[0]['object']
    if obj['type'] != 'tag':
        raise ValueError(f'{name}: remote tag is not annotated')
    tag = api(f"git/tags/{obj['sha']}")
    if tag['tag'] != name or tag['object']['type'] != 'commit' or tag['object']['sha'] != source:
        raise ValueError(f'{name}: conflicting remote target')
    if generated:
        # Writer confirmation binds the exact evidence it generated, including
        # retries after an ambiguous write. A baseline may be developer-authored.
        lines = tag['message'].splitlines()
        expected = annotation_fields(domain, source, value, proof)
        forms = [expected]
        if allow_legacy_generated:
            # Recognize the one previously published writer format only while
            # discovering an existing immutable publication. Never use this
            # compatibility path to confirm a new remote write.
            forms.append([
                'Build: passed; selected matching-system provider fixtures'
                if line.startswith('Build:') else
                'Native runtime: passed; provider CI fixtures'
                if line.startswith('Native runtime:') else line
                for line in expected
            ])
        valid = not any(line.lstrip().startswith('Host:') for line in lines) and any(
            all(lines.count(line) == 1 and
                sum(item.lstrip().startswith(line.split(':', 1)[0] + ':') for item in lines) == 1
                for line in form)
            for form in forms)

    else:
        # INV repository/release-tag-contract: the Unix-like baseline follows
        # audit's domain-level evidence form, not the writer's evidence wording.
        lines = [line.strip() for line in tag['message'].splitlines()]
        valid = domain == 'unixlike' and f'Domain: {domain}' in lines
        valid = valid and not any(line.startswith('Host:') for line in lines)
        for lane in ('Evaluation', 'Build', 'Native runtime'):
            evidence = [line.split(':', 1)[1].strip() for line in lines if line.startswith(f'{lane}:')]
            valid = valid and len(evidence) == 1 and re.fullmatch(
                r'(passed|unavailable|not applicable)([ \t]*;.*)?', evidence[0]) is not None
    if not valid:
        raise ValueError(f'{name}: conflicting required annotation')
    return 'done'


def annotation_fields(domain, source, value, proof=None):
    lines = [f'Domain: {domain}', f"Version: {value['version']}", f'Source: {source}',
             f"Previous: {value['previous']}", f"Summary: {value['summary']}",
             f"Compatibility: {value['compatibility']}", f"Migration: {value['migration']}"]
    lines += ['Evaluation: passed; provider CI',
              'Build: passed; provider-owned artifact checks on CI system',
              'Native runtime: not applicable; host runtime belongs to consumers']
    if proof:
        lines.append(f"CI run: {proof['url']} (attempt {proof['attempt']})")
    return lines + ['Deployment: not performed by release', f'Evidence: https://github.com/{repository()}/commit/{source}']


def checked(base, head, tree, pull):
    return find_pr(base, head, tree, pull=pull, repo=repository(), read=api)


def merge_tree(base, head):
    return git('merge-tree', '--write-tree', base, head).splitlines()[0]


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
    """Static admission proof, also usable for historical patch audits.
    INV repository/topic-source
    """
    if git('show', '-s', '--format=%P', head).split() != [base]:
        return False
    paths = set(git('diff', '--name-only', base, head).splitlines())
    if paths != {'unixlike/flake.lock', 'unixlike/release.json'}:
        return False
    prior = tag_name('unixlike', declaration(base, 'unixlike'))
    value = declaration(head, 'unixlike')
    if value != {'previous': prior, 'version': patch_version(prior),
                 'summary': REFRESH_SUMMARY, 'compatibility': 'patch', 'migration': ''}:
        return False
    allowed = set(source_json(base, 'unixlike/automatic-refresh-inputs.json'))
    validate_lock(source_json(base, 'unixlike/flake.lock'), source_json(head, 'unixlike/flake.lock'), allowed)
    return True


def patch_merge(source):
    parents = git('show', '-s', '--format=%P', source).split()
    return (len(parents) == 2 and automatic(*parents)
            and git('rev-parse', f'{source}^{{tree}}') == merge_tree(*parents))


def patch_version(previous):
    major, minor, patch = map(int, previous.split('-v', 1)[1].split('.'))
    return f'{major}.{minor}.{patch + 1}'


def release_active(workflow):
    # Filter on the server so completed runs cannot hide a live writer.
    return any(api(f'actions/workflows/{workflow}/runs?status={status}&per_page=1')['workflow_runs']
               for status in ('queued', 'in_progress', 'waiting', 'pending', 'requested'))


def manual_active():
    return release_active('manual-release.yml')


def declaration_origin(master):
    return git('log', '-1', '--first-parent', '--format=%H', master, '--', 'unixlike/release.json')


def open_prs(base='master'):
    pulls = []
    for page in count(1):
        batch = api(f'pulls?state=open&base={base}&per_page=100&page={page}')
        if not isinstance(batch, list):
            raise ValueError('invalid open pull request inventory')
        pulls.extend(batch)
        if len(batch) < 100:
            return pulls


def same_repo_head(pr):
    head_repo = pr['head'].get('repo') or {}
    return head_repo.get('full_name') == repository()


def managed_patch(pr):
    return pr['head']['ref'].startswith(PATCH_BRANCH) and same_repo_head(pr)


def upgrade_readiness():
    """Read-only cutover check before deploying a new proof format."""
    master = git('rev-parse', 'origin/master')
    blockers = []
    if api('actions/variables/CONFIGS_RELEASE_ENABLED')['value'] != '0':
        blockers.append('Pause the input patch writer before changing proof formats.')
    for workflow in ('release.yml', 'manual-release.yml'):
        if release_active(workflow):
            blockers.append(f'{workflow} still has an active run.')
    for pr in open_prs():
        if managed_patch(pr):
            blockers.append(f'Input patch pull request #{pr["number"]} is still open.')
    origin = declaration_origin(master)
    if origin and patch_merge(origin):
        value = declaration(origin, 'unixlike')
        if tag_state('unixlike', origin, value, allow_legacy_generated=True) == 'missing':
            blockers.append(f'Complete {tag_name("unixlike", value)} using accepted pre-upgrade tooling first.')
    require_remote_head('master', master)
    return {'master': master, 'ready': not blockers, 'blockers': blockers}


def require_published_base(base):
    value = declaration(base, 'unixlike')
    prior = tag_name('unixlike', value)
    if prior != latest('unixlike'):
        raise ValueError('finish the current Unix-like publication before refreshing')
    target = git('rev-parse', f'{prior}^{{commit}}')
    if tag_state('unixlike', target, value, generated=False) != 'done':
        raise ValueError('finish the current Unix-like publication before refreshing')
    git('merge-base', '--is-ancestor', target, base)
    if subprocess.call(['git', 'diff', '--quiet', target, base, '--', 'unixlike', '.envrc', 'Justfile']):
        raise ValueError('master has unpublished Unix-like source; publish its development release first')
    return prior


def competing_prs():
    return [pr for pr in open_prs() if not pr.get('draft') or managed_patch(pr)]


def inspect(manual=False, start=False):
    if not manual and manual_active():
        return {'action': 'wait', 'reason': 'manual input patch is active'}
    master = git('rev-parse', 'origin/master')
    value = declaration(master, 'unixlike')
    if latest('unixlike') is None:
        raise ValueError('initial Unix-like release must exist')
    if tag_name('unixlike', value) not in git('tag', '--list').splitlines():
        source = declaration_origin(master)
        if not source or not patch_merge(source) or subprocess.call([
                'git', 'diff', '--quiet', source, master, '--', 'unixlike', '.envrc', 'Justfile']):
            return {'action': 'wait', 'reason': 'general Unix-like publication belongs to the developer'}
        return {'action': 'publish', 'source': source, 'base': master, 'head': source}
    require_published_base(master)
    prs = competing_prs()
    patches = [pr for pr in prs if managed_patch(pr)]
    if len(patches) > 1:
        raise ValueError('multiple input patch PRs')
    if len(prs) != len(patches):
        if manual:
            raise ValueError('a master topic PR is open; finish it before input patching')
        return {'action': 'wait', 'reason': 'a master topic PR is open'}
    if patches:
        pr = patches[0]
        if pr.get('draft'):
            return {'action': 'wait', 'reason': 'the input patch PR is a draft'}
        head = pr['head']['sha']
        if not SHA.fullmatch(head):
            raise ValueError('invalid input patch head')
        if subprocess.call(['git', 'cat-file', '-e', f'{head}^{{commit}}'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL):
            git('fetch', '--quiet', 'origin', head)
        if not automatic(master, head):
            raise ValueError('stale or unpermitted input patch; close it and rerun against current master')
        tree = merge_tree(master, head)
        if checked(master, head, tree, pr['number']):
            return {'action': 'patch-merge', 'number': pr['number'], 'base': master, 'head': head, 'tree': tree}
        return {'action': 'wait', 'reason': 'input patch Required checks pending', 'base': master, 'head': head}
    if start:
        return {'action': 'refresh', 'base': master, 'head': master}
    return {'action': 'none'}


def write_guard():
    if os.environ.get('CONFIGS_RELEASE_ENABLED') != '1' or not os.environ.get('GH_TOKEN'):
        raise ValueError('release writes need explicit enablement and writer credentials')
    git('fetch', '--quiet', 'origin', '+refs/heads/master:refs/remotes/origin/master', '--tags')
    if subprocess.call(['git', 'merge-base', '--is-ancestor', 'HEAD', 'origin/master'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL):
        raise ValueError('writer implementation is not accepted master source')
    if git('status', '--porcelain', '--untracked-files=all', '--', '.githooks', 'tool/version-control'):
        raise ValueError('writer tools and hooks must match the accepted checkout')


def require_remote_head(branch, expected):
    if api(f'git/ref/heads/{branch}')['object']['sha'] != expected:
        raise ValueError(f'remote {branch} changed before publication')


def guard_patch_merge(action):
    pr = api(f"pulls/{action['number']}")
    if (pr['state'] != 'open' or pr.get('draft') or not managed_patch(pr) or pr['head']['sha'] != action['head']
            or pr['base']['ref'] != 'master' or pr['base']['sha'] != action['base']):
        raise ValueError('current pull request does not match the reviewed patch')
    if [item['number'] for item in competing_prs()] != [action['number']]:
        raise ValueError('master pull request set changed before the merge')
    subprocess.run(['tool/version-control/closing-keywords', '--text', '-'],
                   input=pr['body'] or '', text=True, stdout=subprocess.DEVNULL, check=True)
    require_remote_head('master', action['base'])


def push_target():
    return f'https://github.com/{repository()}.git'


def push_patch_merge(base, source):
    # Only this process supplies the existing writer credential to Git. The
    # tracked hook compares the old ref advertised on this same connection.
    if not os.access('.githooks/pre-push', os.X_OK):
        raise ValueError('bounded release requires its executable pre-push hook')
    env = dict(os.environ, CONFIGS_PATCH_BASE=base, CONFIGS_PATCH_MERGE=source, GIT_TERMINAL_PROMPT='0')
    subprocess.run(['git', '-c', 'credential.helper=', '-c', 'credential.helper=!gh auth git-credential',
                    '-c', 'core.hooksPath=.githooks', 'push', '--no-follow-tags', '--recurse-submodules=no',
                    push_target(), f'{source}:refs/heads/master'], env=env, check=True)


def publish(source):
    source = git('rev-parse', '--verify', f'{source}^{{commit}}')
    master = git('rev-parse', 'origin/master')
    git('merge-base', '--is-ancestor', source, master)
    if not patch_merge(source):
        raise ValueError('source is not a bounded Unix-like input patch merge')
    domains = ['unixlike']
    missing = [d for d in domains if tag_state(d, source, declaration(source, d), allow_legacy_generated=True) == 'missing']
    if not missing:
        return
    parents = git('show', '-s', '--format=%P', source).split()
    tree = git('rev-parse', f'{source}^{{tree}}')
    # GitHub's commit-to-PR association can lag its successful merge response.
    # Retry read-only proof briefly; never relax source/check agreement.
    proof = None
    for attempt in range(3):
        prs = api(f'commits/{source}/pulls')
        for pr in prs:
            if (pr['merged_at'] and pr['base']['ref'] == 'master' and managed_patch(pr)
                    and pr['merge_commit_sha'] == source):
                proof = checked(parents[0], parents[1], tree, pr['number'])
                if proof:
                    break
        if proof:
            break
        if attempt < 2:
            time.sleep(5)
    if not proof:
        raise ValueError('publication lacks matching Required checks for its actual source tree')
    for domain in missing:
        value = declaration(source, domain)
        require_remote_head('master', master)
        lines = annotation_fields(domain, source, value, proof)
        message = '\n'.join(lines)
        subprocess.run(['tool/version-control/scan-secrets', '--text'], input=message, text=True, check=True)
        obj = api('git/tags', {'tag': tag_name(domain, value), 'message': message, 'object': source, 'type': 'commit'})
        require_remote_head('master', master)
        try:
            api('git/refs', {'ref': f'refs/tags/{tag_name(domain, value)}', 'sha': obj['sha']})
        except subprocess.CalledProcessError:
            if tag_state(domain, source, value, proof=proof) != 'done':
                raise
        if tag_state(domain, source, value, proof=proof) != 'done':
            raise ValueError('remote publication not confirmed')


def advance(expected_head, expected_base, manual=False):
    action = inspect(manual=manual)
    if action['action'] == 'none' or (not manual and action['action'] == 'wait' and not action.get('head')):
        return action
    if action.get('head') != expected_head or action.get('base') != expected_base:
        raise ValueError('candidate changed; rerun against current master')
    if action['action'] == 'wait':
        return action
    if action['action'] == 'publish':
        publish(action['source'])
    elif action['action'] == 'patch-merge':
        source = git('-c', 'user.name=configs release', '-c', 'user.email=configs-release@users.noreply.github.com',
                     'commit-tree', action['tree'], '-p', action['base'], '-p', action['head'],
                     '-m', f"Merge verified Unix-like input patch (#{action['number']})")
        guard_patch_merge(action)
        try:
            push_patch_merge(action['base'], source)
        except subprocess.CalledProcessError:
            # A lost response may still have delivered this exact commit.
            require_remote_head('master', source)
        git('fetch', '--quiet', 'origin', '+refs/heads/master:refs/remotes/origin/master')
        if git('rev-parse', 'origin/master') != source:
            raise ValueError('remote merge is not confirmed at the reviewed commit')
        publish(source)
    else:
        raise ValueError('unexpected input patch action')
    return action


def prepare_manual(timeout=3600, interval=30):
    """Wait for the one input patch PR and finish immutable publication."""
    deadline = time.monotonic() + timeout
    waiting = None
    while True:
        write_guard()
        action = inspect(manual=True)
        identity = (action.get('base'), action.get('head'))
        if waiting is not None and identity != waiting:
            raise ValueError('candidate changed while waiting; rerun the manual workflow')
        print(json.dumps(action), file=sys.stderr, flush=True)
        if action['action'] == 'none':
            return action
        if action['action'] == 'wait':
            if not action.get('head'):
                raise ValueError(action['reason'])
            checks = api(f"commits/{action['head']}/check-runs?per_page=100")['check_runs']
            required = [c for c in checks if c['name'] == 'Required checks' and c['app']['id'] == 15368]
            newest = max(required, key=lambda c: c['id']) if required else None
            if newest and newest['conclusion'] in ('failure', 'cancelled', 'timed_out', 'action_required', 'stale'):
                raise ValueError('Required checks failed; repair or rerun CI before retrying')
            if time.monotonic() >= deadline:
                raise ValueError('manual input patch wait expired; remote PR is preserved')
            waiting = identity
            time.sleep(min(interval, max(0, deadline - time.monotonic())))
            continue
        advance(action['head'], action['base'], manual=True)
        waiting = None
        if time.monotonic() >= deadline:
            raise ValueError('manual input patch wait expired; remote work is preserved')


def ensure_pr(head, base, title, body, *, expected_base, expected_head):
    def matches():
        return [pr for pr in open_prs(base) if pr['head']['ref'] == head and same_repo_head(pr)]

    existing = matches()
    if len(existing) > 1:
        raise ValueError('multiple matching pull requests')
    if existing:
        return existing[0]
    require_remote_head(head, expected_head)
    require_remote_head(base, expected_base)
    try:
        return api('pulls', {'head': head, 'base': base, 'title': title, 'body': body})
    except subprocess.CalledProcessError:
        existing = matches()
        if len(existing) != 1:
            raise ValueError('remote PR creation is not confirmed')
        return existing[0]


def refresh_pr(base, lock_path):
    if not SHA.fullmatch(base) or git('rev-parse', 'origin/master') != base:
        raise ValueError('refresh master base changed')
    prior = require_published_base(base)
    path = Path(lock_path)
    if path.is_symlink() or path.stat().st_size > 1024 * 1024:
        raise ValueError('invalid refresh lock artifact')
    data = path.read_text()
    lock = json.loads(data)
    before = source_json(base, 'unixlike/flake.lock')
    allowed = set(source_json(base, 'unixlike/automatic-refresh-inputs.json'))
    validate_lock(before, lock, allowed)
    if before == lock:
        return {'action': 'none'}
    if competing_prs():
        raise ValueError('a master PR opened during refresh; rerun after it completes')
    value = {'previous': prior, 'version': patch_version(prior), 'summary': REFRESH_SUMMARY,
             'compatibility': 'patch', 'migration': ''}
    branch = PATCH_BRANCH + base[:12]
    existing = api(f'git/matching-refs/heads/{branch}')
    exact = [ref for ref in existing if ref['ref'] == 'refs/heads/' + branch]
    if exact:
        head = exact[0]['object']['sha']
        git('fetch', '--quiet', 'origin', head)
        if not automatic(base, head) or source_json(head, 'unixlike/flake.lock') != lock:
            raise ValueError('input patch branch conflicts; inspect it before retrying')
        return ensure_pr(branch, 'master', 'Patch permitted Unix-like inputs', 'Automatic Unix-like patch: four permitted inputs only; no host deployment.',
                         expected_base=base, expected_head=head)
    files = {'unixlike/flake.lock': data, 'unixlike/release.json': json.dumps(value, indent=2) + '\n'}
    message = 'chore(unixlike-deps): refresh permitted inputs'
    # GitHub API writes bypass the pre-push hook. Inspect the exact text
    # that will leave the runner before even creating a remote blob.
    subprocess.run(['tool/version-control/scan-secrets', '--text'],
                   input='\n'.join([*files.values(), message]), text=True, check=True)
    entries = []
    for name, content in files.items():
        blob = api('git/blobs', {'content': content, 'encoding': 'utf-8'})
        entries.append({'path': name, 'mode': '100644', 'type': 'blob', 'sha': blob['sha']})
    tree = api('git/trees', {'base_tree': git('rev-parse', f'{base}^{{tree}}'), 'tree': entries})
    commit = api('git/commits', {'message': message, 'tree': tree['sha'], 'parents': [base]})
    require_remote_head('master', base)
    try:
        api('git/refs', {'ref': 'refs/heads/' + branch, 'sha': commit['sha']})
    except subprocess.CalledProcessError:
        pass
    if api('git/ref/heads/' + branch)['object']['sha'] != commit['sha']:
        raise ValueError('input patch branch conflicts; inspect it before retrying')
    return ensure_pr(branch, 'master', 'Patch permitted Unix-like inputs', 'Automatic Unix-like patch: four permitted inputs only; no host deployment.',
                     expected_base=base, expected_head=commit['sha'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='operation', required=True)
    diagnosis = sub.add_parser('inspect')
    modes = diagnosis.add_mutually_exclusive_group()
    modes.add_argument('--manual-start', action='store_true')
    modes.add_argument('--scheduled-start', action='store_true')
    modes.add_argument('--upgrade-readiness', action='store_true')
    modes.add_argument('--source')
    proof = sub.add_parser('verify-patch')
    proof.add_argument('--base')
    proof.add_argument('--head')
    proof.add_argument('--merge')
    step = sub.add_parser('advance')
    step.add_argument('--head', required=True)
    step.add_argument('--base', required=True)
    step.add_argument('--manual', action='store_true')
    sub.add_parser('prepare-manual')
    publication = sub.add_parser('publish')
    publication.add_argument('--source', required=True)
    refresh = sub.add_parser('refresh-pr')
    refresh.add_argument('--base', required=True)
    refresh.add_argument('--lock', required=True)
    args = parser.parse_args()
    try:
        os.environ['GIT_NO_REPLACE_OBJECTS'] = '1'
        os.chdir(git('rev-parse', '--show-toplevel'))
        if args.operation == 'verify-patch':
            valid = patch_merge(args.merge) if args.merge and not args.base and not args.head else automatic(args.base, args.head) if args.base and args.head and not args.merge else False
            if not valid:
                raise ValueError('not a single-commit permitted Unix-like input patch')
            print('Unix-like input patch boundary passed')
        elif args.operation == 'inspect':
            if args.upgrade_readiness:
                git('fetch', '--quiet', 'origin', '+refs/heads/master:refs/remotes/origin/master', '--tags')
                readiness = upgrade_readiness()
                print(json.dumps(readiness))
                return 0 if readiness['ready'] else 1
            if os.environ.get('CONFIGS_RELEASE_ENABLED') != '1':
                result = {'action': 'disabled'}
            else:
                git('fetch', '--quiet', 'origin', '--tags')
                if args.source:
                    if not SHA.fullmatch(args.source):
                        raise ValueError('recovery source must be a full commit SHA')
                    git('merge-base', '--is-ancestor', args.source, 'origin/master')
                    if not patch_merge(args.source):
                        raise ValueError('recovery source is not a Unix-like input patch merge')
                    result = {'action': 'publish', 'head': args.source, 'base': args.source}
                else:
                    result = inspect(manual=args.manual_start, start=args.manual_start or args.scheduled_start)
            print(json.dumps(result))
        else:
            write_guard()
            if args.operation == 'prepare-manual':
                print(json.dumps(prepare_manual()))
            elif args.operation == 'publish':
                publish(args.source)
            elif args.operation == 'refresh-pr':
                print(json.dumps(refresh_pr(args.base, args.lock)))
            else:
                result = advance(args.head, args.base, manual=args.manual)
                if args.manual and result['action'] == 'wait':
                    raise ValueError('Required checks changed; rerun the manual workflow')
                print(json.dumps(result))
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError, json.JSONDecodeError) as error:
        print(f'release: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
