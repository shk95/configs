"""Finite GET-only operating credential qualification, never an executor."""
# INV repository/operating-credential-qualification
import http.client
import json
import os
import re
import ssl
import sys

PUBLIC = 'shk95/configs'
PUBLIC_ID = 1330390069
ACTOR = 101378576
WORKFLOW = '.github/workflows/release-credential-check.yml'
JOB = 'validate-operating-credential'
MAX_BODY = 4 * 1024 * 1024


class Refusal(ValueError):
    pass


def need(condition, reason):
    if not condition:
        raise Refusal(reason)


def number(value):
    need(isinstance(value, str) and re.fullmatch(r'[1-9][0-9]*', value), 'invalid-runtime-number')
    return int(value)


def runtime(env):
    need(env.get('GITHUB_ACTIONS') == 'true'
         and env.get('GITHUB_SERVER_URL') == 'https://github.com'
         and env.get('GITHUB_API_URL') == 'https://api.github.com'
         and env.get('GITHUB_REPOSITORY') == PUBLIC
         and env.get('GITHUB_REF') == 'refs/heads/master'
         and env.get('GITHUB_EVENT_NAME') == 'workflow_dispatch'
         and env.get('GITHUB_JOB') == JOB, 'wrong-runtime-boundary')
    need(number(env.get('GITHUB_REPOSITORY_ID')) == PUBLIC_ID
         and number(env.get('GITHUB_ACTOR_ID')) == ACTOR, 'wrong-runtime-authority')
    source = env.get('GITHUB_SHA', '')
    need(re.fullmatch(r'[a-f0-9]{40}', source) and source != '0' * 40, 'invalid-runtime-source')
    return {'source': source, 'run': number(env.get('GITHUB_RUN_ID')),
            'attempt': number(env.get('GITHUB_RUN_ATTEMPT')),
            'actor': ACTOR, 'repository': PUBLIC_ID}


class Reads:
    """No method/body parameter, write primitive, redirects or ambient credential."""
    def __init__(self, token, operating):
        need(isinstance(token, str) and token and not any(c.isspace() for c in token), 'missing-credential')
        need(isinstance(operating, str) and re.fullmatch(r'shk95/[A-Za-z0-9_.-]+', operating)
             and operating not in {PUBLIC, 'shk95/configs-hosts', 'shk95/configs-host-template'},
             'wrong-operating-connection')
        self.__token, self.operating = token, operating

    def get(self, repository, suffix='', *, anonymous=False, denied=False):
        need(repository in {PUBLIC, self.operating}, 'foreign-read-target')
        allowed = (suffix == '' or suffix in {'/branches/master/protection', '/branches/dev/protection', '/actions/secrets'}
                   or re.fullmatch(r'/git/ref/heads/(master|dev)', suffix)
                   or re.fullmatch(r'/commits/[a-f0-9]{40}/check-runs\?per_page=100', suffix)
                   or re.fullmatch(r'/commits/[a-f0-9]{40}/status\?per_page=100', suffix)
                   or re.fullmatch(r'/actions/runs/[1-9][0-9]*(/attempts/[1-9][0-9]*(/jobs\?per_page=100)?)?', suffix)
                   or re.fullmatch(r'/actions/workflows/[1-9][0-9]*', suffix))
        need(allowed and (repository == PUBLIC or suffix == ''), 'unsupported-read-endpoint')
        need(not anonymous or (repository == PUBLIC and '/commits/' in suffix), 'foreign-anonymous-read')
        need(not denied or (repository == PUBLIC and suffix == '/actions/secrets'), 'wrong-denial-probe')
        connection = http.client.HTTPSConnection('api.github.com', timeout=30,
                                                context=ssl.create_default_context())
        headers = {'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2026-03-10',
                   'User-Agent': 'configs-operating-credential-check'}
        if not anonymous:
            headers['Authorization'] = 'Bearer ' + self.__token
        try:
            connection.request('GET', '/repos/' + repository + suffix, headers=headers)
            response = connection.getresponse()
            need(not response.getheader('Location'), 'redirect-refused')
            raw = response.read(MAX_BODY + 1)
            need(len(raw) <= MAX_BODY, 'oversize-read')
            if denied:
                need(response.status in {403, 404}, 'unexpected-secret-metadata-access')
                return None
            need(response.status == 200, 'unavailable-required-read')
            def unique(pairs):
                result = {}
                for key, value in pairs:
                    need(key not in result, 'duplicate-response-field')
                    result[key] = value
                return result
            value = json.loads(raw, object_pairs_hook=unique)
            need(isinstance(value, dict), 'invalid-read-response')
            return value
        except (OSError, http.client.HTTPException, UnicodeError, json.JSONDecodeError):
            raise Refusal('unavailable-read') from None
        finally:
            connection.close()


def protection(value, branch):
    checks = value.get('required_status_checks', {})
    need(checks.get('strict') is (branch == 'dev')
         and checks.get('contexts') == ['Required checks']
         and checks.get('checks') == [{'context': 'Required checks', 'app_id': 15368}]
         and value.get('enforce_admins', {}).get('enabled') is True
         and value.get('required_conversation_resolution', {}).get('enabled') is True
         and value.get('allow_force_pushes', {}).get('enabled') is False
         and value.get('allow_deletions', {}).get('enabled') is False, 'protection-mismatch')


def qualify(reads, current, operating_id):
    """Validate accessible identities; permission to mutate remains unproved."""
    public = reads.get(PUBLIC)
    need(public.get('id') == PUBLIC_ID and public.get('full_name') == PUBLIC
         and public.get('private') is False and public.get('default_branch') == 'master', 'wrong-public-repository')
    private = reads.get(reads.operating)
    need(private.get('id') == operating_id and private.get('full_name') == reads.operating
         and private.get('private') is True, 'wrong-private-repository')
    master = reads.get(PUBLIC, '/git/ref/heads/master')
    need(master.get('ref') == 'refs/heads/master'
         and master.get('object') == {'type': 'commit', 'sha': current['source'],
                                      'url': master.get('object', {}).get('url')}, 'moving-master-source')
    run_path = '/actions/runs/' + str(current['run'])
    attempt_path = run_path + '/attempts/' + str(current['attempt'])
    run = reads.get(PUBLIC, attempt_path)
    workflow_id = run.get('workflow_id')
    need(type(workflow_id) is int and workflow_id > 0
         and run.get('id') == current['run'] and run.get('run_attempt') == current['attempt']
         and run.get('head_sha') == current['source'] and run.get('head_branch') == 'master'
         and run.get('event') == 'workflow_dispatch' and run.get('status') == 'in_progress'
         and run.get('repository', {}).get('id') == PUBLIC_ID
         and run.get('actor', {}).get('id') == current['actor']
         and run.get('triggering_actor', {}).get('id') == current['actor'], 'wrong-actual-run')
    workflow = reads.get(PUBLIC, '/actions/workflows/' + str(workflow_id))
    need(workflow.get('id') == workflow_id and workflow.get('path') == WORKFLOW, 'wrong-actual-workflow')
    jobs = reads.get(PUBLIC, attempt_path + '/jobs?per_page=100')
    rows = jobs.get('jobs')
    need(jobs.get('total_count') == 1 and isinstance(rows, list) and len(rows) == 1, 'nonisolated-credential-job')
    job = rows[0]
    need(job.get('name') == JOB and job.get('run_id') == current['run']
         and job.get('head_sha') == current['source'] and job.get('status') == 'in_progress', 'wrong-actual-job')
    for branch in ('master', 'dev'):
        protection(reads.get(PUBLIC, '/branches/' + branch + '/protection'), branch)
    # Public check observations need no Checks grant. They are only accessibility
    # observations here, never evidence that every selected required check passed.
    checks = reads.get(PUBLIC, '/commits/' + current['source'] + '/check-runs?per_page=100', anonymous=True)
    need(type(checks.get('total_count')) is int and isinstance(checks.get('check_runs'), list), 'unavailable-public-checks')
    statuses = reads.get(PUBLIC, '/commits/' + current['source'] + '/status?per_page=100')
    need(statuses.get('sha') == current['source'] and isinstance(statuses.get('statuses'), list), 'wrong-status-source')
    reads.get(PUBLIC, '/actions/secrets', denied=True)
    latest = reads.get(PUBLIC, run_path)
    need(latest.get('id') == current['run'] and latest.get('run_attempt') == current['attempt']
         and latest.get('head_sha') == current['source'], 'moving-run-attempt')
    final = reads.get(PUBLIC, '/git/ref/heads/master')
    need(final.get('object', {}).get('sha') == current['source'], 'moving-master-source')
    return {'kind': 'operating-credential-read-check', 'source': current['source'],
            'run': current['run'], 'attempt': current['attempt'],
            'private_repository_read': True, 'protection_read': True,
            'actions_read': True, 'public_checks_read': True, 'commit_statuses_read': True,
            'secret_metadata_denied': True, 'mutation_permissions_verified': False,
            'operating_enabled': False, 'production_certification': False}


def main(env=None, factory=Reads):
    try:
        env = os.environ if env is None else env
        current = runtime(env)
        operating_id = number(env.get('CONFIGS_RELEASE_OPERATING_REPOSITORY_ID'))
        reads = factory(env.get('CONFIGS_RELEASE_TOKEN'), env.get('CONFIGS_RELEASE_OPERATING_REPOSITORY'))
        result = qualify(reads, current, operating_id)
        print(json.dumps(result, sort_keys=True))
        return 0
    except (Refusal, ValueError, TypeError, KeyError):
        # Never print endpoint bodies, private values, exceptions or token fragments.
        print('operating credential read check: refused', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
