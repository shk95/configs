"""Approved, exact-source history maintenance; never changes branch protection."""
# INV repository/approved-history-rewrite
import json
import os
from pathlib import Path
import re
import subprocess
from github_proof import api, repository
from repo_policy import load
from recovery import validate_bundle

APP_PERMISSIONS = {'contents': 'write', 'administration': 'read', 'actions': 'read', 'variables': 'read'}


def git(*args):
    return subprocess.check_output(['git', *args], text=True).strip()


def full_sha(value):
    if not re.fullmatch('[0-9a-f]{40}', value): raise ValueError('Full old/new SHA required')
    return git('rev-parse', '--verify', value + '^{commit}')


def variable(repo, name):
    try: return api(f'repos/{repo}/actions/variables/{name}')['value']
    except subprocess.CalledProcessError: return None


def paginated(path):
    values = []
    for page in range(1, 101):
        separator = '&' if '?' in path else '?'
        items = api(f'{path}{separator}per_page=100&page={page}')
        if not isinstance(items, list): raise ValueError('Invalid ruleset inventory')
        values.extend(items)
        if len(items) < 100: return values
    raise ValueError('Ruleset inventory exceeds the supported inspection bound')


def audit_force_actor(repo, protection, require_enabled=True):
    policy = load()
    rules = policy['history_rewrite']
    listed = paginated(f'repos/{repo}/rulesets?includes_parents=true')
    if any(item.get('enforcement') not in ('active', 'disabled', 'evaluate') for item in listed):
        raise ValueError('Unknown ruleset enforcement state')
    active = [item for item in listed if item['enforcement'] == 'active']
    effective = paginated(f'repos/{repo}/rules/branches/{policy["base_branch"]}')
    classic_enabled = protection['allow_force_pushes']['enabled']
    if not active and not effective and not classic_enabled:
        if require_enabled: raise ValueError('Approved maintenance actor has not been adopted; force remains disabled')
        return {'enabled': False}
    if len(active) != 1 or active[0].get('source_type') != 'Repository' or active[0].get('source') != repo:
        raise ValueError('Only the declared repository maintenance ruleset is supported; inherited or additional active rulesets refuse')
    summary = active[0]
    identity = summary.get('id')
    if type(identity) is not int or identity <= 0 or summary.get('name') != rules['ruleset']:
        raise ValueError('Unknown active ruleset')
    detail = api(f'repos/{repo}/rulesets/{identity}?includes_parents=true')
    expected = dict(id=identity, name=rules['ruleset'], source_type='Repository', source=repo,
                    target='branch', enforcement='active',
                    conditions={'ref_name': {'include': ['refs/heads/' + policy['base_branch']], 'exclude': []}},
                    rules=[{'type': 'non_fast_forward'}])
    if any(detail.get(key) != value for key, value in expected.items()):
        raise ValueError('Maintenance ruleset must actively protect only exact master against non-fast-forward updates')
    node = variable(repo, rules['app_node_variable'])
    app_id = variable(repo, rules['app_id_variable'])
    if not node or not app_id or not re.fullmatch('[1-9][0-9]*', app_id):
        raise ValueError('Missing declared maintenance App identities')
    actors = [{'actor_type': 'Integration', 'actor_id': int(app_id), 'bypass_mode': 'always'}]
    if detail.get('bypass_actors') != actors:
        raise ValueError('Visible ruleset bypass actors must name only the isolated maintenance App; hidden actors are not proof')
    expected_effective = [dict(type='non_fast_forward', ruleset_source_type='Repository',
                               ruleset_source=repo, ruleset_id=identity)]
    if effective != expected_effective:
        raise ValueError('Effective master rules differ from the declared maintenance rule')
    if not classic_enabled:
        raise ValueError('Maintenance ruleset is present but classic protection still blocks the approved App')
    return {'enabled': True, 'actor': node, 'app_id': int(app_id), 'ruleset_id': identity}


def app_identity(actor, slug):
    if not re.fullmatch('[a-z0-9-]+', slug): raise ValueError('Missing isolated writer App identity')
    app = api('apps/' + slug)
    if app.get('node_id') != actor['actor'] or app.get('id') != actor['app_id']:
        raise ValueError('Writer App differs from the declared maintenance capability')
    permissions = app.get('permissions', {})
    expected = dict(APP_PERMISSIONS)
    if isinstance(permissions, dict) and 'metadata' in permissions:
        expected['metadata'] = 'read'  # Implicit GitHub App repository access.
    if permissions != expected:
        raise ValueError('Maintenance App must grant only the declared exact permissions and implicit metadata:read')
    return app


def preflight(slug):
    repo = repository()
    policy = load()
    protection = api(f'repos/{repo}/branches/{policy["base_branch"]}/protection')
    if not protection['enforce_admins']['enabled'] or protection['allow_deletions']['enabled']:
        raise ValueError('Safe-history protection is not active')
    actor = audit_force_actor(repo, protection)
    app_identity(actor, slug)
    approval_environment(repo)
    return dict(repository=repo, history_rewrite=actor, app=slug, required_permissions=APP_PERMISSIONS,
                reader='current caller; workflow token grants are requested separately', writes='none', approval='not granted')


def plan(old, new, reason):
    policy = load()
    old, new = full_sha(old), full_sha(new)
    if old == new or not reason.strip(): raise ValueError('A changed target and explicit reason are required')
    repo = repository()
    if api(f'repos/{repo}/git/ref/heads/{policy["base_branch"]}')['object']['sha'] != old:
        raise ValueError('Remote master differs from the proposed old SHA')
    # Never silently strand immutable domain publications.
    for tag in git('tag', '--list').splitlines():
        if tag in ('unixlike-v2026.08.31', 'windows-v2026.08.31'): continue
        if re.fullmatch(r'(unixlike|windows|common)-v[0-9]+\.[0-9]+\.[0-9]+', tag):
            subprocess.check_call(['git', 'merge-base', '--is-ancestor', tag + '^{}', new])
    return dict(schema=1, repository=repo, branch=policy['base_branch'], old=old, new=new,
                reason=reason, removed_commits=git('rev-list', old, '--not', new).splitlines())


def approval_environment(repo):
    policy = load()
    name = policy['history_rewrite']['environment']
    environment = api(f'repos/{repo}/environments/{name}')
    reviewers = [r for r in environment['protection_rules'] if r['type'] == 'required_reviewers']
    if environment.get('can_admins_bypass') is not False or len(reviewers) != 1 or not reviewers[0]['reviewers']:
        raise ValueError('Environment must require human review without administrator bypass')
    if environment.get('deployment_branch_policy') != {'protected_branches': False, 'custom_branch_policies': True}:
        raise ValueError('Maintenance credentials must be restricted to the selected master branch')
    branches = api(f'repos/{repo}/environments/{name}/deployment-branch-policies')['branch_policies']
    if [(item['name'], item['type']) for item in branches] != [(policy['base_branch'], 'branch')]:
        raise ValueError('Maintenance environment must admit only master, not tags or other branches')
    users = [r['reviewer']['id'] for r in reviewers[0]['reviewers'] if r['type'] == 'User']
    if not users: raise ValueError('Individual human approval reviewers are required')
    return environment, users


def authorization(value):
    policy = load()
    rules = policy['history_rewrite']
    repo = value['repository']
    if os.environ.get('GITHUB_ACTIONS') != 'true' or os.environ.get('GITHUB_EVENT_NAME') != 'workflow_dispatch':
        raise ValueError('History execution is available only in the protected manual workflow')
    if os.environ.get('GITHUB_REPOSITORY') != repo or os.environ.get('GITHUB_REF') != 'refs/heads/' + policy['base_branch']:
        raise ValueError('Wrong workflow repository/ref')
    if os.environ.get('GITHUB_WORKFLOW_REF') != f'{repo}/{rules["workflow"]}@refs/heads/{policy["base_branch"]}':
        raise ValueError('Wrong maintenance workflow')
    if os.environ.get('GITHUB_RUN_ATTEMPT') != str(rules['attempts']):
        raise ValueError('Reruns cannot reuse approval; dispatch a new reviewed operation')
    if os.environ.get('GITHUB_SHA') != value['old'] or os.environ.get('GITHUB_WORKFLOW_SHA') != value['old']:
        raise ValueError('Maintenance tooling is not the selected accepted master source')
    event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text())
    if event['inputs'] != {key: value[key] for key in ('old', 'new', 'reason')}:
        raise ValueError('Approved dispatch inputs differ from the operation')
    run_id = os.environ.get('GITHUB_RUN_ID', '')
    if not re.fullmatch('[1-9][0-9]*', run_id): raise ValueError('Invalid workflow run')
    run = api(f'repos/{repo}/actions/runs/{run_id}')
    if (run['path'] != rules['workflow'] or run['head_sha'] != value['old'] or run['run_attempt'] != rules['attempts']
            or run.get('event') != 'workflow_dispatch' or run.get('head_branch') != policy['base_branch']
            or run.get('status') != 'in_progress' or run.get('conclusion') is not None):
        raise ValueError('Live maintenance run identity differs')
    environment, approved_users = approval_environment(repo)
    reviews = api(f'repos/{repo}/actions/runs/{run_id}/approvals')
    matching = [r for r in reviews if any(e['id'] == environment['id'] for e in r['environments'])]
    if not matching or any(r['state'] != 'approved' or r['user']['id'] not in approved_users for r in matching):
        raise ValueError('No explicit human approval for this environment/run')
    protection = api(f'repos/{repo}/branches/{value["branch"]}/protection')
    if not protection['enforce_admins']['enabled'] or protection['allow_deletions']['enabled']:
        raise ValueError('Safe-history protection is not active')
    actor = audit_force_actor(repo, protection)
    app_identity(actor, os.environ.get('CONFIGS_HISTORY_APP_SLUG', ''))
    return {'run': run_id, 'reviewer_id': matching[-1]['user']['id'], 'environment': environment['id']}


def prepare(directory, old, new, reason):
    value = plan(old, new, reason)
    destination = Path(directory)
    destination.mkdir(mode=0o700)  # refuse existing/symlink destinations
    bundle = destination / 'recovery.bundle'
    if git('rev-parse', 'refs/remotes/origin/' + value['branch']) != value['old']:
        raise ValueError('Recovery source differs from selected remote history')
    subprocess.check_call(['git', 'bundle', 'create', str(bundle), 'refs/remotes/origin/' + value['branch'], '--tags'])
    value['bundle_sha256'] = validate_bundle(bundle, value['old'])
    (destination / 'plan.json').write_text(json.dumps(value, indent=2) + '\n')
    return value


def execute(directory):
    directory = Path(directory)
    value = json.loads((directory / 'plan.json').read_text())
    approval = authorization(value)
    current = plan(value['old'], value['new'], value['reason'])
    if any(current[k] != value[k] for k in current): raise ValueError('Reviewed recovery plan changed')
    bundle = directory / 'recovery.bundle'
    digest = validate_bundle(bundle, value['old'])
    if digest != value['bundle_sha256']:
        raise ValueError('Recovery bundle changed')
    artifacts = api(f'repos/{value["repository"]}/actions/runs/{approval["run"]}/artifacts')['artifacts']
    if not any(a['name'] == 'history-recovery' and not a['expired'] for a in artifacts):
        raise ValueError('Recovery must be uploaded before execution')
    # No raw --force, ref deletion, tag rewrite or branch-protection mutation.
    command = ['git', '-c', 'credential.helper=!gh auth git-credential', 'push', '--no-mirror', '--no-follow-tags', '--recurse-submodules=no', 'origin',
               value['new'] + ':refs/heads/' + value['branch'],
               '--force-with-lease=refs/heads/' + value['branch'] + ':' + value['old']]
    error = None
    try: subprocess.check_call(command)
    except subprocess.CalledProcessError as caught: error = caught
    actual = api(f'repos/{value["repository"]}/git/ref/heads/{value["branch"]}')['object']['sha']
    audit_force_actor(value['repository'], api(f'repos/{value["repository"]}/branches/{value["branch"]}/protection'))
    if actual != value['new']:
        raise ValueError(f'Push not confirmed; remote={actual}; preserve recovery and inspect before retry') from error
    return dict(approval=approval, old=value['old'], new=actual, protection='unchanged', recovery='history-recovery')
