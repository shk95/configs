"""Validate live GitHub evidence; caller-supplied JSON is never proof."""
# INV repository/exact-ci-proof
import io
import json
import re
import subprocess
import zipfile
from repo_policy import load


def api(path, binary=False):
    raw = subprocess.check_output(['gh', 'api', path])
    return raw if binary else json.loads(raw)


def repository():
    value = subprocess.check_output(['gh', 'repo', 'view', '--json', 'nameWithOwner', '--jq', '.nameWithOwner'], text=True).strip()
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', value): raise ValueError('Invalid repository identity')
    return value


def source_record(raw):
    if len(raw) > 65536: raise ValueError('CI identity archive is too large')
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        if archive.namelist() != ['source.json']: raise ValueError('Unexpected CI identity archive')
        entry = archive.getinfo('source.json')
        if entry.file_size > 4096: raise ValueError('CI identity record is too large')
        value = json.loads(archive.read(entry))
    if set(value) != {'base', 'head', 'tree', 'event'}: raise ValueError('Invalid CI identity fields')
    if any(not isinstance(value[k], str) or not re.fullmatch('[0-9a-f]{40}', value[k]) for k in ('base', 'head', 'tree')):
        raise ValueError('Invalid CI source SHA')
    return value


def verify(run_id, base, head, tree):
    policy = load()
    if not re.fullmatch('[1-9][0-9]*', str(run_id)): raise ValueError('Use a numeric GitHub run ID')
    repo = repository()
    prefix = f'repos/{repo}'
    run = api(f'{prefix}/actions/runs/{run_id}')
    if run.get('repository', {}).get('full_name') != repo or run.get('path') != policy['ci']['workflow']:
        raise ValueError('CI belongs to a different repository or workflow')
    if run.get('status') != 'completed' or run.get('conclusion') != 'success' or run.get('event') not in policy['ci']['events']:
        raise ValueError('CI did not finish successfully in an admitted event')
    if run['event'] == 'workflow_dispatch':
        # Dispatch orchestration must be accepted master tooling, not a topic workflow.
        if run.get('head_branch') != policy['base_branch']: raise ValueError('Dispatch must use master tooling')
        subprocess.check_call(['git', 'merge-base', '--is-ancestor', run['head_sha'], policy['base_branch']])
    elif run.get('head_sha') != head:
        raise ValueError('CI run belongs to a different candidate')
    jobs = api(f'{prefix}/actions/runs/{run_id}/attempts/{run["run_attempt"]}/jobs?per_page=100')['jobs']
    if sum(j['name'] == policy['ci']['gate'] and j['conclusion'] == 'success' for j in jobs) != 1:
        raise ValueError('Stable CI gate did not succeed in this attempt')
    artifacts = api(f'{prefix}/actions/runs/{run_id}/artifacts?per_page=100')['artifacts']
    found = [item for item in artifacts if item['name'] == policy['ci']['artifact'] and not item['expired']]
    if len(found) != 1: raise ValueError('Missing, expired or ambiguous CI source artifact')
    value = source_record(api(f'{prefix}/actions/artifacts/{found[0]["id"]}/zip', binary=True))
    if value != dict(base=base, head=head, tree=tree, event=run['event']):
        raise ValueError('CI does not cover the exact base/head/tree/event')
    return {'run_id': str(run_id), 'url': run['html_url'], 'attempt': run['run_attempt'], **value}
