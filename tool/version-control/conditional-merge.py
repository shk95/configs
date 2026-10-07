#!/usr/bin/env python3
"""Submit or execute one explicitly admitted protected pull-request merge.
INV repository/conditional-protected-merge
"""
import argparse
import datetime as dt
import io
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile

SHA = re.compile(r'[0-9a-f]{40}\Z')
REPO = re.compile(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z')
API = 'https://api.github.com'
API_VERSION = '2026-03-10'
APP_ID = 15368
WAIT_SECONDS = 3600
MAX_DEV_UPDATES = 3
SAFETY_PATHS = ('.github/', 'tool/', '.agents/', 'AGENTS.md', 'CONTRIBUTING.md', 'docs/policy/')


class GitHub:
    def __init__(self, token, repo):
        self.token, self.repo = token, repo

    def request(self, path, method='GET', data=None, binary=False):
        if path.startswith('https://'):
            url = path
        else:
            endpoint = f'{API}/repos/{self.repo}'
            route = path.lstrip('/')
            url = f'{endpoint}/{route}' if route else endpoint
        headers = {'Accept': 'application/vnd.github+json', 'Authorization': f'Bearer {self.token}',
                   'X-GitHub-Api-Version': API_VERSION, 'User-Agent': 'configs-conditional-merge'}
        payload = None if data is None else json.dumps(data).encode()
        request = urllib.request.Request(url, data=payload, headers=headers, method=method)
        opener = urllib.request.build_opener(StripCrossHostAuthorization())
        with opener.open(request, timeout=30) as response:
            body = response.read(65537) if binary else response.read()
            if binary:
                if len(body) > 65536:
                    raise ValueError('CI source artifact exceeds 64 KiB')
                return body
            return json.loads(body) if body else None

    def pages(self, path):
        url = f'{API}/repos/{self.repo}/{path.lstrip("/")}'
        values = []
        while url:
            if urllib.parse.urlparse(url).hostname != 'api.github.com':
                raise ValueError('pagination escaped the GitHub API host')
            headers = {'Accept': 'application/vnd.github+json', 'Authorization': f'Bearer {self.token}',
                       'X-GitHub-Api-Version': API_VERSION, 'User-Agent': 'configs-conditional-merge'}
            opener = urllib.request.build_opener(StripCrossHostAuthorization())
            with opener.open(urllib.request.Request(url, headers=headers), timeout=30) as response:
                page = json.loads(response.read())
                if isinstance(page, list):
                    values.extend(page)
                else:
                    for key in ('workflow_runs', 'check_runs', 'artifacts'):
                        if key in page:
                            values.extend(page[key])
                            break
                link = response.headers.get('Link', '')
            match = re.search(r'<([^>]+)>;\s*rel="next"', link)
            url = match.group(1) if match else ''
        return values


class StripCrossHostAuthorization(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        redirected = super().redirect_request(req, fp, code, msg, headers, newurl)
        if redirected and urllib.parse.urlparse(req.full_url).hostname != urllib.parse.urlparse(newurl).hostname:
            redirected.remove_header('Authorization')
        return redirected


def repo_name():
    value = os.environ.get('GITHUB_REPOSITORY')
    if not value:
        try:
            value = subprocess.check_output(['gh', 'repo', 'view', '--json', 'nameWithOwner', '--jq', '.nameWithOwner'],
                                            text=True, stderr=subprocess.DEVNULL).strip()
        except (OSError, subprocess.CalledProcessError):
            value = ''
    if not REPO.fullmatch(value):
        raise ValueError('GITHUB_REPOSITORY is missing or invalid')
    return value


def token():
    value = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if not value:
        try:
            value = subprocess.check_output(['gh', 'auth', 'token'], text=True, stderr=subprocess.DEVNULL).strip()
        except (OSError, subprocess.CalledProcessError):
            value = ''
    if not value:
        raise ValueError('GH_TOKEN is required')
    return value


def full_sha(value, field):
    if not isinstance(value, str) or not SHA.fullmatch(value):
        raise ValueError(f'{field} must be a full 40-character commit SHA')
    return value


def sha256_tree(base, head):
    for value in (base, head):
        subprocess.run(['git', 'fetch', '--quiet', '--no-tags', 'origin', value], check=True)
    result = subprocess.run(['git', 'merge-tree', '--write-tree', base, head], check=True,
                            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    tree = result.stdout.splitlines()[0].strip()
    if not re.fullmatch(r'[0-9a-f]{40}', tree):
        raise ValueError('git did not produce a merge tree')
    return tree


def source_identity(data):
    if len(data) > 65536:
        raise ValueError('CI source archive is too large')
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        item = archive.getinfo('source.json')
        if item.file_size > 4096:
            raise ValueError('CI source record is too large')
        source = json.loads(archive.read(item))
    if set(source) != {'event', 'base', 'head', 'tree'} or source['event'] != 'pull_request':
        raise ValueError('invalid CI source record')
    for field in ('base', 'head', 'tree'):
        full_sha(source[field], f'CI source {field}')
    return source


def request_identity(pr, request, allow_dev_chain=False):
    head_matches = pr['head']['sha'] == request['head']
    base_matches = pr['base']['sha'] == request['base']
    return (pr['number'] == request['pr'] and pr['base']['ref'] == request['target']
            and (head_matches or (allow_dev_chain and request['target'] == 'dev'))
            and (base_matches or (allow_dev_chain and request['target'] == 'dev'))
            and pr['head']['repo'] and pr['head']['repo']['full_name'].lower() == request['repo'].lower()
            and pr['base']['repo']['full_name'].lower() == request['repo'].lower())


def merged_request_identity(pr, request):
    return (pr['number'] == request['pr'] and pr['base']['ref'] == request['target']
            and (pr['head']['sha'] == request['head'] or request['target'] == 'dev')
            and pr['head']['repo'] and pr['base']['repo']
            and pr['head']['repo']['full_name'].lower() == request['repo'].lower()
            and pr['base']['repo']['full_name'].lower() == request['repo'].lower())


def read_pr(api, request, allow_dev_chain=False):
    pr = api.request(f"pulls/{request['pr']}")
    if pr['state'] == 'closed' and pr.get('merged_at'):
        if not merged_request_identity(pr, request):
            raise ValueError('merged pull request identity differs from the admitted request')
        if request['target'] == 'master' and pr['head']['ref'] != 'dev':
            raise ValueError('master accepts only a same-repository dev promotion')
        return pr
    if pr['state'] != 'open' or pr.get('draft'):
        raise ValueError('candidate must be an open Ready pull request')
    if not request_identity(pr, request, allow_dev_chain=allow_dev_chain):
        raise ValueError('pull request head or target identity changed; fresh admission is required')
    if pr.get('auto_merge'):
        raise ValueError('candidate already has an auto-merge request; cancel and inspect it first')
    if request['target'] == 'master' and pr['head']['ref'] != 'dev':
        raise ValueError('master accepts only a same-repository dev promotion')
    labels = {item['name'].lower() for item in pr.get('labels', [])}
    if 'blocked' in labels:
        raise ValueError('candidate is explicitly blocked')
    if 'high-risk' in labels:
        raise ValueError('high-risk candidate requires admission-specific synchronous review')
    if pr.get('mergeable') is False or pr.get('mergeable_state') == 'dirty':
        raise ValueError(f"candidate is not mergeable ({pr.get('mergeable_state')})")
    if pr.get('mergeable_state') == 'behind' and not (allow_dev_chain and request['target'] == 'dev'):
        raise ValueError('candidate is behind its target')
    if pr.get('mergeable') is not True or pr.get('mergeable_state') in ('unknown', 'blocked'):
        pr['_conditional_waiting'] = True
    check_conversations(api, request)
    check_reviews(api, request, pr, labels)
    return pr


def check_conversations(api, request):
    owner, name = request['repo'].split('/')
    query = '''query($owner:String!, $name:String!, $number:Int!, $after:String) {
      repository(owner:$owner, name:$name) {
        pullRequest(number:$number) { reviewThreads(first:100, after:$after) {
          nodes { isResolved } pageInfo { hasNextPage endCursor }
        } }
      }
    }'''
    after = None
    while True:
        result = api.request('https://api.github.com/graphql', method='POST', data={
            'query': query, 'variables': {'owner': owner, 'name': name, 'number': request['pr'], 'after': after}})
        repository = result.get('data', {}).get('repository') if isinstance(result, dict) else None
        if not isinstance(result, dict) or result.get('errors') or not repository or not repository.get('pullRequest'):
            raise ValueError('review conversation state is unavailable')
        threads = result['data']['repository']['pullRequest']['reviewThreads']
        if any(not item['isResolved'] for item in threads['nodes']):
            raise ValueError('candidate has unresolved review conversations')
        if not threads['pageInfo']['hasNextPage']:
            break
        after = threads['pageInfo']['endCursor']


def check_reviews(api, request, pr, labels):
    if 'high-risk' in labels:
        raise ValueError('high-risk candidate requires admission-specific synchronous review')
    reviews = api.pages(f"pulls/{request['pr']}/reviews?per_page=100")
    latest = {}
    for review in sorted(reviews, key=lambda r: r.get('submitted_at') or ''):
        if review.get('user') and review.get('state') in ('APPROVED', 'CHANGES_REQUESTED', 'DISMISSED'):
            latest[review['user']['login'].lower()] = review
    if any(review.get('state') == 'CHANGES_REQUESTED' for review in latest.values()):
        raise ValueError('candidate has an outstanding change request')
    protection = api.request(f"branches/{request['target']}/protection")
    requirements = protection.get('required_pull_request_reviews') or {}
    approved = [login for login, review in latest.items()
                if review.get('state') == 'APPROVED' and review.get('commit_id') == pr['head']['sha']]
    if len(approved) < requirements.get('required_approving_review_count', 0):
        raise ValueError('required pull request approvals are not satisfied')


def validate_protection(api, target):
    branch = api.request(f'branches/{target}/protection')
    checks = branch.get('required_status_checks') or {}
    declared = checks.get('checks') or []
    if (checks.get('strict') is not True
            or checks.get('contexts') != ['Required checks']
            or declared != [{'context': 'Required checks', 'app_id': APP_ID}]):
        raise ValueError(f'{target} must require strict Required checks from GitHub Actions')
    if (branch.get('enforce_admins', {}).get('enabled') is not True
            or branch.get('required_conversation_resolution', {}).get('enabled') is not True
            or branch.get('required_pull_request_reviews') is None
            or branch.get('allow_force_pushes', {}).get('enabled') is not False
            or branch.get('allow_deletions', {}).get('enabled') is not False):
        raise ValueError(f'{target} branch protection does not match the conditional-merge contract')
    repo = api.request('')
    if not (repo.get('allow_merge_commit') is True and repo.get('allow_squash_merge') is False
            and repo.get('allow_rebase_merge') is False):
        raise ValueError('repository merge settings must allow merge commits only')


def check_independent_shape(api, request):
    subprocess.run(['git', 'fetch', '--quiet', '--no-tags', 'origin', request['base'], request['head']], check=True)
    if request['target'] == 'master':
        promotions = api.pages('pulls?state=open&base=master&per_page=100')
        if len(promotions) != 1 or promotions[0]['number'] != request['pr']:
            raise ValueError('master promotion requires the single open master pull request')
        env = os.environ.copy()
        env.update({'PROMOTION_BASE_REF': 'master', 'PROMOTION_HEAD_REF': 'dev',
                    'PROMOTION_BASE_REPOSITORY': request['repo'], 'PROMOTION_HEAD_REPOSITORY': request['repo'],
                    'PROMOTION_BASE_SHA': request['base'], 'PROMOTION_HEAD_SHA': request['head']})
        subprocess.run(['tool/version-control/check-promotion'], env=env, check=True)
    else:
        open_prs = api.pages(f"pulls?state=open&base={request['target']}&per_page=100")
        for other in open_prs:
            if other['number'] == request['pr']:
                continue
            other_head = other['head']['sha']
            subprocess.run(['git', 'fetch', '--quiet', '--no-tags', 'origin', other_head], check=True)
            if subprocess.run(['git', 'merge-base', '--is-ancestor', other_head, request['head']],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
                raise ValueError(f"candidate is stacked on open pull request #{other['number']}")


def branch_sha(api, branch):
    ref = api.request(f'git/ref/heads/{urllib.parse.quote(branch, safe="/-_")}')
    return ref['object']['sha']


def is_ancestor(ancestor, descendant):
    return subprocess.run(['git', 'merge-base', '--is-ancestor', ancestor, descendant],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def validate_dev_chain(request, current_head, current_dev):
    """Accept only deterministic clean merges extending the frozen source head."""
    source_head = request.get('source_head', request['head'])
    source_base = request.get('source_base', request['base'])
    for value in (source_base, source_head, current_head, current_dev):
        subprocess.run(['git', 'fetch', '--quiet', '--no-tags', 'origin', value], check=True)
    if not is_ancestor(source_base, current_dev):
        raise ValueError('current dev is not descended from the originally admitted base')
    if not is_ancestor(source_head, current_head):
        raise ValueError('approved source head is not an ancestor of the PR head')
    chain = subprocess.check_output(['git', 'rev-list', '--first-parent', '--reverse', '--max-count=4',
                                     f'{source_head}..{current_head}'], text=True).split()
    if len(chain) > MAX_DEV_UPDATES:
        raise ValueError('dev integration chain exceeds three updates')
    previous = source_head
    for commit in chain:
        parents = subprocess.check_output(['git', 'show', '-s', '--format=%P', commit], text=True).strip().split()
        if len(parents) != 2 or parents[0] != previous:
            raise ValueError('PR head contains a source commit or malformed integration merge')
        base = parents[1]
        if not is_ancestor(source_base, base) or not is_ancestor(base, current_dev):
            raise ValueError('integration merge second parent is outside accepted dev ancestry')
        try:
            expected_tree = subprocess.check_output(['git', 'merge-tree', '--write-tree', parents[0], base],
                                                    text=True, stderr=subprocess.PIPE).splitlines()[0].strip()
        except subprocess.CalledProcessError as error:
            raise ValueError('integration merge is not conflict-free') from error
        actual_tree = subprocess.check_output(['git', 'rev-parse', f'{commit}^{{tree}}'], text=True).strip()
        if expected_tree != actual_tree:
            raise ValueError('integration merge has conflict resolution or a non-deterministic tree')
        previous = commit
    return len(chain)


def update_dev_branch(api, request, expected_head, deadline):
    """CAS the PR head, then observe and validate the asynchronous GitHub update."""
    if time.monotonic() >= deadline:
        raise ValueError('60-minute request deadline expired before branch update')
    verify_run = os.environ.get('GITHUB_RUN_ID')
    if not verify_run:
        raise ValueError('writer run identity is unavailable before branch update')
    run = verify_accepted_run(api, verify_run, target='dev')
    validate_accepted_revision(api, run, 'dev')
    validate_protection(api, 'dev')
    latest_pr = read_pr(api, request, allow_dev_chain=True)
    if latest_pr['head']['sha'] != expected_head:
        raise ValueError('PR state or expected head changed before branch update')
    if latest_pr['head'].get('ref') in ('dev', 'master'):
        raise ValueError('protected branch refs cannot be updated as topic PRs')
    current_dev = branch_sha(api, 'dev')
    chain_count = validate_dev_chain(request, expected_head, current_dev)
    if chain_count >= MAX_DEV_UPDATES and not is_ancestor(current_dev, expected_head):
        raise ValueError('three dev integration updates exhausted before current dev was included')
    sha256_tree(current_dev, expected_head)  # refuse conflicts before asking GitHub to update
    refuse_latest_ci_failure(api, expected_head)
    check_independent_shape(api, dict(request, head=expected_head, base=current_dev))
    if time.monotonic() >= deadline:
        raise ValueError('60-minute request deadline expired before branch update')
    ambiguous_error = None
    try:
        api.request(f"pulls/{request['pr']}/update-branch", method='PUT',
                    data={'expected_head_sha': expected_head})
    except urllib.error.HTTPError as error:
        if error.code == 422:
            current = read_pr(api, request, allow_dev_chain=True)
            if current['head']['sha'] != expected_head:
                validate_dev_chain(request, current['head']['sha'], branch_sha(api, 'dev'))
                return current
            raise ValueError('PR head compare-and-swap failed; re-inspect the accepted chain') from error
        ambiguous_error = error
    except (urllib.error.URLError, TimeoutError) as error:
        ambiguous_error = error
    while time.monotonic() < deadline:
        pr = read_pr(api, request, allow_dev_chain=True)
        if pr['head']['sha'] != expected_head:
            current_dev = branch_sha(api, 'dev')
            validate_dev_chain(request, pr['head']['sha'], current_dev)
            return pr
        time.sleep(min(5, max(0, deadline - time.monotonic())))
    # A final read can confirm an accepted update after the wait bound; it does
    # not authorize another write or extend the request deadline.
    pr = read_pr(api, request, allow_dev_chain=True)
    if pr['head']['sha'] != expected_head:
        validate_dev_chain(request, pr['head']['sha'], branch_sha(api, 'dev'))
        return pr
    if ambiguous_error:
        raise ValueError(f'branch update response is ambiguous ({ambiguous_error}); inspect GitHub before retrying') from ambiguous_error
    raise ValueError('branch update remains ambiguous at the request deadline; inspect GitHub before retrying')


def validate_accepted_revision(api, run, target, allow_recovery=False):
    current = branch_sha(api, 'dev')
    subprocess.run(['git', 'fetch', '--quiet', '--no-tags', 'origin', current], check=True)
    accepted = run['head_sha']
    if not is_ancestor(accepted, current):
        raise ValueError('accepted workflow revision is not an ancestor of current target')
    if target == 'master':
        if accepted != current and not (allow_recovery and is_ancestor(accepted, current)):
            raise ValueError('master promotion requires a workflow dispatched from current dev')
    elif not allow_recovery:
        changed = subprocess.run(['git', 'diff', '--quiet', accepted, current, '--', *SAFETY_PATHS]).returncode
        if changed:
            raise ValueError('accepted workflow safety paths changed on dev; request a fresh accepted revision')
    return current


def source_run(api, request, tree):
    runs = api.pages(f"actions/workflows/ci.yml/runs?head_sha={request['head']}&event=pull_request&per_page=100")
    runs = [r for r in runs if r.get('path') == '.github/workflows/ci.yml'
            and r.get('event') == 'pull_request' and r.get('head_sha') == request['head']]
    if not runs:
        return None, 'waiting'
    latest = max(runs, key=lambda r: int(r['id']))
    if latest['status'] != 'completed':
        return None, 'waiting'
    if latest.get('conclusion') != 'success':
        raise ValueError(f"newest matching CI run {latest['id']} concluded {latest.get('conclusion')}")
    checks = api.pages(f"commits/{request['head']}/check-runs?per_page=100")
    required = [c for c in checks if c.get('name') == 'Required checks' and c.get('app', {}).get('id') == APP_ID]
    if not required:
        return None, 'waiting'
    newest_check = max(required, key=lambda c: int(c['id']))
    run_match = re.search(r'/actions/runs/(\d+)(?:/|$)', newest_check.get('details_url', ''))
    if newest_check.get('status') != 'completed' or newest_check.get('conclusion') != 'success':
        if run_match and run_match.group(1) == str(latest['id']) and newest_check.get('status') == 'completed':
            raise ValueError('newest Required checks run did not pass')
        return None, 'waiting'
    if not run_match or run_match.group(1) != str(latest['id']):
        return None, 'waiting'
    artifacts = api.pages(f"actions/runs/{latest['id']}/artifacts?per_page=100")
    matches = [a for a in artifacts if a.get('name') == 'ci-source' and not a.get('expired')]
    if len(matches) != 1:
        raise ValueError('newest successful CI run must have exactly one live ci-source artifact')
    identity = source_identity(api.request(f"actions/artifacts/{matches[0]['id']}/zip", binary=True))
    expected = {'event': 'pull_request', 'base': request['base'], 'head': request['head'], 'tree': tree}
    if identity != expected:
        raise ValueError('newest successful CI source identity does not match the admitted merge tree')
    return latest, 'success'


def refuse_latest_ci_failure(api, head):
    runs = api.pages(f"actions/workflows/ci.yml/runs?head_sha={head}&event=pull_request&per_page=100")
    runs = [r for r in runs if r.get('path') == '.github/workflows/ci.yml'
            and r.get('event') == 'pull_request' and r.get('head_sha') == head]
    if runs:
        latest = max(runs, key=lambda r: int(r['id']))
        if latest.get('status') == 'completed' and latest.get('conclusion') not in ('success', None):
            raise ValueError(f"newest matching CI run {latest['id']} concluded {latest.get('conclusion')}")
    checks = api.pages(f"commits/{head}/check-runs?per_page=100")
    required = [c for c in checks if c.get('name') == 'Required checks' and c.get('app', {}).get('id') == APP_ID]
    if not required:
        return
    latest_check = max(required, key=lambda c: int(c['id']))
    if latest_check.get('status') == 'completed' and latest_check.get('conclusion') not in ('success', None):
        raise ValueError('newest Required checks run did not pass; refusing to hide failure with an update')


def validate_actor(api, request, run, require_repository_role=True):
    actors = {x.strip().lower() for x in os.environ.get('CONFIGS_MERGE_ACTORS', '').split(',') if x.strip()}
    actor = run.get('actor', {}).get('login', '').lower()
    if not actors or actor not in actors:
        raise ValueError('dispatch actor is not in CONFIGS_MERGE_ACTORS')
    if require_repository_role:
        value = api.request(f"collaborators/{urllib.parse.quote(actor, safe='')}/permission")
        if value.get('permission') != 'admin' and value.get('role_name') not in ('admin', 'maintain'):
            raise ValueError('dispatch actor must have admin or maintain repository permission')


def verify_accepted_run(api, run_id, allow_recovery=False, target='dev'):
    run = api.request(f'actions/runs/{run_id}')
    if run.get('event') != 'workflow_dispatch' or run.get('path') != '.github/workflows/conditional-merge.yml':
        raise ValueError('unsupported workflow run')
    if run.get('head_branch') != 'dev':
        raise ValueError('workflow was not dispatched from the accepted dev ref')
    validate_accepted_revision(api, run, target, allow_recovery=allow_recovery)
    allowed_status = ('in_progress', 'completed') if allow_recovery else ('in_progress',)
    if run.get('status') not in allowed_status or run.get('created_at') is None:
        raise ValueError('workflow run is not active')
    created = dt.datetime.fromisoformat(run['created_at'].replace('Z', '+00:00'))
    age = (dt.datetime.now(dt.timezone.utc) - created).total_seconds()
    if age > WAIT_SECONDS and not allow_recovery:
        raise ValueError('request exceeded the 60-minute queue and wait limit')
    return run


def preflight(args):
    repo = repo_name()
    api = GitHub(token(), repo)
    run_id = os.environ.get('GITHUB_RUN_ID')
    if not run_id or str(args.run_id) != run_id:
        raise ValueError('input run id does not match this Actions run')
    if os.environ.get('CONFIGS_MERGE_ENABLED') != '1':
        raise ValueError('conditional merges are disabled; CONFIGS_MERGE_ENABLED is not 1')
    if args.target not in ('dev', 'master') or args.pr < 1:
        raise ValueError('invalid target or pull request number')
    full_sha(args.head, 'head')
    full_sha(args.base, 'base')
    head, base = full_sha(args.head, 'head'), full_sha(args.base, 'base')
    request = {'pr': args.pr, 'target': args.target, 'head': head, 'source_head': head,
               'base': base, 'source_base': base, 'repo': repo}
    pr = api.request(f"pulls/{request['pr']}")
    if pr.get('state') == 'closed' and pr.get('merged_at'):
        if not merged_request_identity(pr, request):
            raise ValueError('merged pull request source or target differs from this request')
        recovery = True
    else:
        recovery = False
    run = verify_accepted_run(api, run_id, allow_recovery=recovery, target=args.target)
    validate_actor(api, {'repo': repo}, run)
    print(json.dumps({'state': 'authorized', 'actor': run['actor']['login'], 'accepted_sha': run['head_sha']}))


def request_from_inputs(args, repo):
    if args.target not in ('dev', 'master'):
        raise ValueError('target must be dev or master')
    if args.pr < 1:
        raise ValueError('pull request number must be positive')
    head = full_sha(args.head, 'head')
    base = full_sha(args.base, 'base')
    return {'pr': args.pr, 'target': args.target, 'head': head, 'source_head': head,
            'base': base, 'source_base': base, 'repo': repo}


def submit(args):
    if not args.confirm:
        raise ValueError('add --confirm after reviewing the exact PR number and both SHAs')
    repo = repo_name()
    request = request_from_inputs(args, repo)
    api = GitHub(token(), repo)
    pr = read_pr(api, request, allow_dev_chain=request['target'] == 'dev')
    if pr['head']['sha'] != request['head']:
        raise ValueError('PR source head changed before submission; the reviewed source SHA must match exactly')
    if pr.get('merged_at'):
        raise ValueError('candidate is already merged; inspect its recorded result instead of dispatching')
    if branch_sha(api, request['target']) != request['base']:
        raise ValueError('target moved before submission; inspect again and make a fresh admission')
    inputs = {'pr': str(request['pr']), 'target': request['target'], 'head': request['head'], 'base': request['base']}
    try:
        result = api.request('actions/workflows/conditional-merge.yml/dispatches', method='POST',
                             data={'ref': 'dev', 'inputs': inputs})
    except (urllib.error.URLError, TimeoutError) as error:
        raise ValueError(f'dispatch response is ambiguous ({error}); inspect Actions before retrying') from error
    if not isinstance(result, dict) or not all(result.get(k) for k in ('workflow_run_id', 'run_url', 'html_url')):
        raise ValueError('dispatch was accepted without a confirmed run identity; inspect Actions before retrying')
    print(json.dumps({'state': 'requested', 'run_id': result['workflow_run_id'], 'run_url': result['html_url'],
                      'pr': request['pr'], 'target': request['target'], 'base': request['base'], 'head': request['head']}))


def write_run(args):
    repo = repo_name()
    api = GitHub(token(), repo)
    run_id = os.environ.get('GITHUB_RUN_ID')
    if not run_id or str(args.run_id) != run_id:
        raise ValueError('input run id does not match this Actions run')
    admitted_head = full_sha(args.head, 'head')
    admitted_base = full_sha(args.base, 'base')
    request = {'pr': args.pr, 'target': args.target,
               'head': admitted_head, 'source_head': admitted_head,
               'base': admitted_base, 'source_base': admitted_base, 'repo': repo}
    if request['target'] not in ('dev', 'master'):
        raise ValueError('unsupported target')
    if os.environ.get('CONFIGS_MERGE_ENABLED') != '1':
        raise ValueError('conditional merges are disabled; CONFIGS_MERGE_ENABLED is not 1')
    run = verify_accepted_run(api, run_id, allow_recovery=True, target=request['target'])
    validate_actor(api, {'repo': repo}, run)
    pr = read_pr(api, request, allow_dev_chain=True)
    if pr.get('merged_at'):
        if request['target'] == 'dev':
            validate_dev_chain(request, pr['head']['sha'], branch_sha(api, 'dev'))
            request['head'] = pr['head']['sha']
        return finish(api, request, pr, 'already merged')
    run = verify_accepted_run(api, run_id, target=request['target'])
    validate_protection(api, request['target'])
    check_independent_shape(api, request)
    deadline = time.monotonic() + max(0, WAIT_SECONDS - (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(run['created_at'].replace('Z', '+00:00'))).total_seconds())
    while True:
        if time.monotonic() >= deadline:
            raise ValueError('60-minute request deadline expired; pull request is preserved')
        verify_accepted_run(api, run_id, target=request['target'])
        pr = read_pr(api, request, allow_dev_chain=request['target'] == 'dev')
        if pr.get('merged_at'):
            if request['target'] == 'dev':
                validate_dev_chain(request, pr['head']['sha'], branch_sha(api, 'dev'))
                request['head'] = pr['head']['sha']
            return finish(api, request, pr, 'already merged')
        current_base = branch_sha(api, request['target'])
        active = dict(request, head=pr['head']['sha'], base=current_base)
        if request['target'] == 'dev':
            chain_count = validate_dev_chain(request, pr['head']['sha'], current_base)
            if not is_ancestor(current_base, pr['head']['sha']):
                # Check the newest evidence for the currently observed head
                # before starting another update; a failure must not be hidden.
                refuse_latest_ci_failure(api, pr['head']['sha'])
                if chain_count >= MAX_DEV_UPDATES:
                    raise ValueError('three dev integration updates exhausted before current dev was included')
                pr = update_dev_branch(api, request, pr['head']['sha'], deadline)
                continue
        elif current_base != request['base'] or pr['head']['sha'] != request['head']:
            raise ValueError('master target or source head moved; fresh admission is required')
        tree = sha256_tree(current_base, pr['head']['sha'])
        ci, state = source_run(api, active, tree)
        if state == 'waiting':
            if time.monotonic() >= deadline:
                raise ValueError('60-minute CI wait expired; pull request is preserved')
            time.sleep(min(30, max(0, deadline - time.monotonic())))
            continue
        if pr.get('_conditional_waiting'):
            if time.monotonic() >= deadline:
                raise ValueError('60-minute protection wait expired; pull request is preserved')
            time.sleep(min(30, max(0, deadline - time.monotonic())))
            continue
        # Last inspection immediately before the protected merge API. GitHub
        # receives an atomic expected-head condition; strict protection guards
        # a target move, which has no compare-and-swap field in that API.
        verify_accepted_run(api, run_id, target=request['target'])
        pr = read_pr(api, request, allow_dev_chain=request['target'] == 'dev')
        latest_base = branch_sha(api, request['target'])
        if latest_base != active['base'] or pr['head']['sha'] != active['head']:
            if request['target'] == 'dev':
                continue
            raise ValueError('master target or source head moved before merge; fresh admission is required')
        if pr.get('_conditional_waiting'):
            raise ValueError('GitHub protection state is pending; no merge was requested')
        validate_protection(api, request['target'])
        check_independent_shape(api, active)
        if source_run(api, active, tree)[1] != 'success':
            raise ValueError('Required checks changed before merge')
        try:
            result = api.request(f"pulls/{request['pr']}/merge", method='PUT',
                                 data={'sha': active['head'], 'merge_method': 'merge'})
            if not result or result.get('merged') is not True:
                raise ValueError('protected merge API did not confirm success')
        except (urllib.error.URLError, TimeoutError, ValueError) as error:
            current = api.request(f"pulls/{request['pr']}")
            if not current.get('merged_at') or current['head']['sha'] != active['head']:
                raise ValueError(f'merge result is ambiguous or refused ({error}); inspect GitHub before retrying') from error
            pr = current
        else:
            pr = api.request(f"pulls/{request['pr']}")
        if not pr.get('merged_at') or pr['head']['sha'] != active['head']:
            raise ValueError('merge response was not confirmed by the pull request')
        return finish(api, active, pr, 'merged')


def confirmed_merge_identity(api, request):
    owner, name = request['repo'].split('/', 1)
    query = '''query($owner:String!, $name:String!, $number:Int!) {
      repository(owner:$owner, name:$name) {
        nameWithOwner
        pullRequest(number:$number) {
          number state merged mergedAt baseRefName headRefOid mergeCommit { oid }
        }
      }
    }'''
    result = api.request('https://api.github.com/graphql', method='POST', data={
        'query': query, 'variables': {'owner': owner, 'name': name, 'number': request['pr']}})
    if not isinstance(result, dict) or result.get('errors'):
        raise ValueError('GraphQL response did not confirm the merged pull request identity')
    data_result = result.get('data')
    if not isinstance(data_result, dict):
        raise ValueError('GraphQL response omitted the merged repository identity')
    repository = data_result.get('repository')
    if not isinstance(repository, dict):
        raise ValueError('GraphQL merge identity repository does not match the admitted repository')
    repository_name = repository.get('nameWithOwner')
    if not isinstance(repository_name, str) or repository_name.lower() != request['repo'].lower():
        raise ValueError('GraphQL merge identity repository does not match the admitted repository')
    pr = repository.get('pullRequest')
    if not isinstance(pr, dict):
        raise ValueError('GraphQL response omitted the merged pull request identity')
    if (pr.get('number') != request['pr'] or pr.get('state') != 'MERGED' or pr.get('merged') is not True
            or not pr.get('mergedAt') or pr.get('baseRefName') != request['target']
            or pr.get('headRefOid') != request['head']):
        raise ValueError('GraphQL merge identity does not match the admitted pull request')
    merge_commit = pr.get('mergeCommit')
    if not isinstance(merge_commit, dict):
        raise ValueError('GraphQL response omitted the merged commit identity')
    return full_sha(merge_commit.get('oid'), 'merge commit')


def finish(api, request, pr, label):
    merged = None
    try:
        merged = confirmed_merge_identity(api, request)
        subprocess.run(['git', 'fetch', '--quiet', '--no-tags', 'origin', merged], check=True)
        parents = subprocess.check_output(['git', 'show', '-s', '--format=%P', merged], text=True).strip().split()
        if request['target'] == 'dev':
            if len(parents) != 2 or parents[1] != pr['head']['sha']:
                raise ValueError('dev merge commit does not preserve the accepted PR integration head')
            if label != 'already merged' and parents[0] != request['base']:
                raise ValueError('protected merge used a base newer than the exact base CI evidence tested')
            current_dev = branch_sha(api, 'dev')
            subprocess.run(['git', 'fetch', '--quiet', '--no-tags', 'origin', current_dev], check=True)
            source_base = request.get('source_base', request['base'])
            if not is_ancestor(source_base, parents[0]) or not is_ancestor(parents[0], current_dev):
                raise ValueError('dev merge commit base is outside the admitted dev ancestry')
            validate_dev_chain(request, parents[1], current_dev)
            tree = sha256_tree(parents[0], parents[1])
            evidence_request = dict(request, base=parents[0], head=parents[1])
            if source_run(api, evidence_request, tree)[1] != 'success':
                raise ValueError('merged PR has no successful exact-base integration-head CI evidence')
        else:
            tree = sha256_tree(request['base'], request['head'])
            if source_run(api, request, tree)[1] != 'success':
                raise ValueError('merged PR has no successful exact-source CI evidence')
        actual_tree = subprocess.check_output(['git', 'rev-parse', f'{merged}^{{tree}}'], text=True).strip()
        expected_parents = [request['base'], request['head']] if request['target'] == 'master' else parents
        if parents != expected_parents or actual_tree != tree:
            raise ValueError('merged commit parents/tree differ from the approved identities')
        subprocess.run(['git', 'fetch', '--quiet', 'origin', 'dev', 'master', '--tags'], check=True)
        for command in (['tool/version-control/audit', '--history', merged],
                        ['tool/version-control/audit-remote']):
            audit = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if audit.returncode:
                raise ValueError(audit.stdout)
    except (OSError, subprocess.CalledProcessError, ValueError) as error:
        print(json.dumps({'state': 'merged-with-audit-failure', 'pr': request['pr'],
                          'merge_commit': merged, 'audit': str(error)}), file=sys.stderr)
        raise ValueError('merge completed; post-merge identity or audit failed') from error
    print(json.dumps({'state': label, 'pr': request['pr'], 'merge_commit': merged,
                      'approved_source_head': request.get('source_head', request['head']),
                      'integration_head': request['head'],
                      'tested_base': parents[0] if request['target'] == 'dev' else request['base'],
                      'parents': parents, 'tree': actual_tree, 'audit': 'passed'}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='operation', required=True)
    dispatch = sub.add_parser('submit')
    dispatch.add_argument('--pr', type=int, required=True)
    dispatch.add_argument('--target', required=True)
    dispatch.add_argument('--head', required=True)
    dispatch.add_argument('--base', required=True)
    dispatch.add_argument('--confirm', action='store_true')
    write = sub.add_parser('run')
    write.add_argument('--run-id', required=True)
    write.add_argument('--pr', type=int, required=True)
    write.add_argument('--target', required=True)
    write.add_argument('--head', required=True)
    write.add_argument('--base', required=True)
    check = sub.add_parser('preflight')
    check.add_argument('--run-id', required=True)
    check.add_argument('--pr', type=int, required=True)
    check.add_argument('--target', required=True)
    check.add_argument('--head', required=True)
    check.add_argument('--base', required=True)
    args = parser.parse_args()
    try:
        if args.operation == 'submit':
            submit(args)
        elif args.operation == 'preflight':
            preflight(args)
        else:
            write_run(args)
    except (KeyError, OSError, subprocess.CalledProcessError, urllib.error.HTTPError,
            urllib.error.URLError, ValueError, json.JSONDecodeError, zipfile.BadZipFile) as error:
        print(f'conditional-merge: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
