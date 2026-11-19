"""Read attempt-bound GitHub Actions evidence for a reviewed source."""
# INV repository/exact-ci-proof
import io
import json
from pathlib import Path
import re
import subprocess
import zipfile

from git_workflow import git
from repo_policy import load

SHA = re.compile(r'[0-9a-f]{40}')
# Names are the stable Actions job/step interface. The workflow definition is
# checked separately, so a similarly named job from other wiring cannot count.
UNITS = {
    'repository:fixtures': ('Version-control policy (Linux)', 'ubuntu-latest',
                            ('Run tool/version-control/test',)),
    'repository:windows-git': ('Version-control policy (Windows Git)', 'windows-latest',
                               ('Retired capture guard on native Git for Windows',)),
    'unixlike:suite': ('Unix-like provider contract', 'ubuntu-latest',
                       ('Verify upstream Nix baseline', 'Run unixlike/tool/checks/format',
                        'Run unixlike/tool/checks/lint', 'Run unixlike/tool/checks/test')),
    'windows:suite': ('Windows desired state', 'windows-latest',
                      ('Acquire declared Windows management runtime', 'Validate and test Windows desired state')),
    'windows:runtime': ('Windows desired state', 'windows-latest',
                        ('Acquire declared Windows management runtime', 'Verify Windows CI runtime fixtures')),
}
POLICY_JOB = 'Incoming history and repository policy'
POLICY_STEPS = ('Audit incoming commits and merges', 'Scan incoming patches for secrets',
                'Run tool/version-control/hygiene', 'Run tool/version-control/domain-reads',
                'Run tool/version-control/design-citations', 'Run tool/version-control/records',
                'Check the work items', 'Run tool/version-control/invariants', 'Check the provisional registry')
TOPIC_JOB = 'Topic source policy'
TOPIC_STEPS = ('Require a same-repository topic or bounded Unix-like input patch',
               'Refuse closing keywords in the topic body')
REUSABLE = {'unixlike:suite', 'windows:suite'}


def api(path, binary=False):
    raw = subprocess.check_output(['gh', 'api', path])
    return raw if binary else json.loads(raw)


def repository():
    return subprocess.check_output(['gh', 'repo', 'view', '--json', 'nameWithOwner',
                                    '--jq', '.nameWithOwner'], text=True).strip()


def selected_units(base, source_tree, root=Path('.')):
    changes = git('diff', '--no-renames', '--name-status', base, source_tree, cwd=root)
    units = subprocess.run([str(root.resolve() / 'tool/dispatch/select'), 'ci'],
                           input=changes + '\n', text=True, cwd=root,
                           stdout=subprocess.PIPE, check=True).stdout.splitlines()
    if len(units) != len(set(units)) or any(unit not in UNITS for unit in units):
        raise ValueError('Unknown or duplicate selected check')
    return units


def source_record(raw):
    if len(raw) > 65536:
        raise ValueError('CI identity archive is too large')
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            if archive.namelist() != ['source.json']:
                raise ValueError('Unexpected CI identity archive')
            entry = archive.getinfo('source.json')
            if entry.file_size > 4096:
                raise ValueError('CI identity record is too large')
            value = json.loads(archive.read(entry))
    except (zipfile.BadZipFile, UnicodeError, RuntimeError, NotImplementedError) as error:
        raise ValueError('Unreadable CI identity archive') from error
    fields = {'schema', 'event', 'base', 'head', 'tree', 'checkout', 'workflow_sha',
              'workflow_blob', 'run_id', 'attempt', 'pull', 'units', 'reuse'}
    if not isinstance(value, dict) or set(value) != fields or value['schema'] != 2:
        raise ValueError('Unsupported CI identity fields; run the current workflow')
    for field in ('base', 'head', 'tree', 'checkout', 'workflow_sha', 'workflow_blob'):
        if not isinstance(value[field], str) or not SHA.fullmatch(value[field]):
            raise ValueError('Invalid CI source SHA: ' + field)
    for field in ('run_id', 'attempt'):
        if type(value[field]) is not int or value[field] < 1:
            raise ValueError('Invalid CI identity: ' + field)
    if value['event'] == 'pull_request':
        if type(value['pull']) is not int or value['pull'] < 1:
            raise ValueError('CI pull request identity missing')
    elif value['pull'] is not None:
        raise ValueError('Unexpected CI pull request identity')
    units = value['units']
    if (not isinstance(units, list) or any(not isinstance(unit, str) or unit not in UNITS for unit in units)
            or len(units) != len(set(units))):
        raise ValueError('Invalid CI check coverage')
    reused = value['reuse']
    if reused is not None and (value['event'] != 'push' or not isinstance(reused, dict)
            or set(reused) != {'run_id', 'attempt', 'units'}
            or any(type(reused[key]) is not int or reused[key] < 1 for key in ('run_id', 'attempt'))
            or not isinstance(reused['units'], list) or not reused['units']
            or any(not isinstance(unit, str) or unit not in REUSABLE or unit not in units
                   for unit in reused['units']) or len(reused['units']) != len(set(reused['units']))):
        raise ValueError('Invalid proof reuse identity')
    return value


def verify_jobs(jobs, run, units, ci):
    selected = {
        'Classify change': ('ubuntu-latest', {'Resolve owning scopes and CI effects'}),
        POLICY_JOB: ('ubuntu-latest', set(POLICY_STEPS)),
        ci['gate']: ('ubuntu-latest', {'Enforce scoped results', 'Record the tested source'}),
    }
    optional = {name for name, _, _ in UNITS.values()} | {TOPIC_JOB}
    if run['event'] == 'pull_request':
        selected[TOPIC_JOB] = ('ubuntu-latest', set(TOPIC_STEPS))
    if run['event'] == 'push':
        selected['Classify change'][1].add('Resolve previous provider evidence')
    for unit in units:
        name, runner, steps = UNITS[unit]
        selected.setdefault(name, (runner, set()))[1].update(steps)
    expected = set(selected) | optional
    if len(jobs) != len(expected) or {job.get('name') for job in jobs} != expected:
        raise ValueError('Missing, unexpected or duplicate CI jobs')
    for job in jobs:
        name = job['name']
        if (job.get('run_attempt'), job.get('run_id'), job.get('head_sha')) != (
                run['run_attempt'], run['id'], run['head_sha']):
            raise ValueError('CI job belongs to another attempt or source: ' + name)
        if name not in selected:
            if job.get('conclusion') != 'skipped':
                raise ValueError('Unexpected CI job execution: ' + name)
            continue
        runner, steps = selected[name]
        if job.get('conclusion') != 'success' or job.get('labels') != [runner]:
            raise ValueError('Required CI job or runner did not match: ' + name)
        witnesses = [step.get('name') for step in job.get('steps', []) if step.get('conclusion') == 'success']
        if any(witnesses.count(step) != 1 for step in steps):
            raise ValueError('Required CI step did not run successfully: ' + name)
        # The shared Windows job can run either or both checks.
        optional_steps = {step for group, _, checks in UNITS.values() if group == name for step in checks} - steps
        if any(step.get('name') in optional_steps and step.get('conclusion') != 'skipped'
               for step in job.get('steps', [])):
            raise ValueError('Unexpected CI unit execution: ' + name)


def verify(run_id, base, head, tree, *, event=None, pull=None, repo=None, read=None):
    """Validate the latest successful attempt using live run, job and artifact data."""
    policy = load()
    ci = policy['ci']
    if not re.fullmatch('[1-9][0-9]*', str(run_id)):
        raise ValueError('Use a numeric GitHub run ID')
    run_id = int(run_id)
    repo = repo or repository()
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo):
        raise ValueError('Invalid repository identity')
    if read is None:
        def read(path, binary=False):
            return api(f'repos/{repo}/{path}', binary=binary)

    path = f'actions/runs/{run_id}'
    run = read(path)
    if (run.get('id') != run_id or run.get('repository', {}).get('full_name') != repo
            or (run.get('head_repository') or {}).get('full_name') != repo or run.get('path') != ci['workflow']):
        raise ValueError('CI belongs to a different repository or workflow')
    triggered = run.get('event')
    attempt = run.get('run_attempt')
    if (run.get('status') != 'completed' or run.get('conclusion') != 'success'
            or triggered not in ci['events'] or (event is not None and triggered != event)
            or type(attempt) is not int or attempt < 1):
        raise ValueError('CI did not finish successfully in an admitted event')
    dispatch = triggered == 'workflow_dispatch'
    if (run.get('head_sha') != (base if dispatch else head)
            or (triggered != 'pull_request' and run.get('head_branch') != policy['base_branch'])):
        raise ValueError('CI run belongs to a different candidate or master revision')

    results = read(f'{path}/artifacts?per_page=100')
    if results['total_count'] != len(results['artifacts']):
        raise ValueError('CI artifact inventory is incomplete')
    artifacts = [item for item in results['artifacts'] if item.get('name') == f"{ci['artifact']}-{attempt}"]
    if (len(artifacts) != 1 or artifacts[0].get('expired') is not False
            or artifacts[0].get('workflow_run', {}).get('id') != run_id):
        raise ValueError('Missing, expired or ambiguous CI artifact for this attempt')
    value = source_record(read(f"actions/artifacts/{artifacts[0]['id']}/zip", binary=True))
    if ((value['base'], value['head'], value['tree'], value['event'], value['run_id'], value['attempt'])
            != (base, head, tree, triggered, run_id, attempt) or (pull is not None and value['pull'] != pull)):
        raise ValueError('CI artifact belongs to a different source, event or attempt')

    checkout = value['checkout']
    if triggered == 'pull_request':
        inspected = read(f'git/commits/{checkout}')
        if (inspected.get('sha') != checkout or inspected.get('tree', {}).get('sha') != tree
                or [parent['sha'] for parent in inspected.get('parents', [])] != [base, head]):
            raise ValueError('CI checkout is not the reviewed PR merge')
    elif checkout != head:
        raise ValueError('CI checkout is not the reviewed candidate')
    if value['workflow_sha'] != (base if dispatch else checkout):
        raise ValueError('CI ran a workflow from a different revision')
    blob = git('rev-parse', '--verify', f"{tree}:{ci['workflow']}")
    if value['workflow_blob'] != blob or (dispatch and git('rev-parse', '--verify', f"{base}:{ci['workflow']}") != blob):
        raise ValueError('CI workflow definition differs from the reviewed tree')

    units = selected_units(base, tree)
    if value['units'] != units:
        raise ValueError('CI did not cover the required check units')
    jobs = read(f'{path}/attempts/{attempt}/jobs?per_page=100')
    if jobs['total_count'] != len(jobs['jobs']):
        raise ValueError('CI job inventory is incomplete')
    reused = value['reuse']
    executed = units
    if reused:
        parent = merged_head(base, head)
        if parent is None:
            raise ValueError('Provider reuse requires an exact two-parent master merge')
        previous = verify(reused['run_id'], base, parent, tree, event='pull_request', repo=repo, read=read)
        if (previous['attempt'] != reused['attempt']
                or not set(reused['units']).issubset(previous['units'])):
            raise ValueError('Previous CI attempt did not prove the reused units')
        executed = [unit for unit in units if unit not in reused['units']]
    verify_jobs(jobs['jobs'], run, executed, ci)
    current = read(path)
    if (current.get('status'), current.get('conclusion'), current.get('run_attempt')) != ('completed', 'success', attempt):
        raise ValueError('CI attempt changed while reading its evidence')
    return {**value, 'url': run['html_url']}


def merged_head(base, head):
    parents = git('show', '-s', '--format=%P', head).split()
    return parents[1] if len(parents) == 2 and parents[0] == base else None


def find_pr(base, head, tree, *, pull=None, repo, read):
    ci = load()['ci']
    checks = read(f'commits/{head}/check-runs?per_page=100')['check_runs']
    run_url = re.escape(f'https://github.com/{repo}/actions/runs/') + r'([0-9]+)/job/[0-9]+'
    tried = set()
    for check in sorted(checks, key=lambda value: value['id'], reverse=True):
        if check['name'] != ci['gate'] or check['app']['id'] != 15368 or check['conclusion'] != 'success':
            continue
        match = re.fullmatch(run_url, check['details_url'])
        if match and match[1] not in tried:
            tried.add(match[1])
            try:
                return verify(match[1], base, head, tree, event='pull_request', pull=pull, repo=repo, read=read)
            except ValueError:
                continue
    return None


def reusable_provider_units(base, head, units, *, repo, read):
    if set(units).isdisjoint(REUSABLE):
        return None
    candidate = merged_head(base, head)
    if candidate is None:
        return None
    previous = find_pr(base, candidate, git('rev-parse', head + '^{tree}'), repo=repo, read=read)
    if previous:
        reused = [unit for unit in units if unit in REUSABLE and unit in previous['units']]
        if reused:
            return {'run_id': previous['run_id'], 'attempt': previous['attempt'], 'units': reused}
    return None
