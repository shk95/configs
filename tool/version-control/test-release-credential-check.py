"""GET-only credential boundary fixtures; no real credential or HTTP access."""
# INV repository/operating-credential-qualification
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('credential_check', TOOLS / 'release-credential-check.py')
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
SOURCE = 'a' * 40
PRIVATE_ID = 99
ENV = {'GITHUB_ACTIONS': 'true', 'GITHUB_SERVER_URL': 'https://github.com',
       'GITHUB_API_URL': 'https://api.github.com', 'GITHUB_REPOSITORY': C.PUBLIC,
       'GITHUB_REPOSITORY_ID': str(C.PUBLIC_ID), 'GITHUB_ACTOR_ID': str(C.ACTOR),
       'GITHUB_REF': 'refs/heads/master', 'GITHUB_EVENT_NAME': 'workflow_dispatch',
       'GITHUB_JOB': C.JOB, 'GITHUB_SHA': SOURCE, 'GITHUB_RUN_ID': '4',
       'GITHUB_RUN_ATTEMPT': '1', 'CONFIGS_RELEASE_TOKEN': 'fixture-private-value',
       'CONFIGS_RELEASE_OPERATING_REPOSITORY': 'shk95/fixture-operating',
       'CONFIGS_RELEASE_OPERATING_REPOSITORY_ID': str(PRIVATE_ID)}


def protected(branch):
    return {'required_status_checks': {'strict': branch == 'dev', 'contexts': ['Required checks'],
            'checks': [{'context': 'Required checks', 'app_id': 15368}]},
            'enforce_admins': {'enabled': True}, 'required_conversation_resolution': {'enabled': True},
            'allow_force_pushes': {'enabled': False}, 'allow_deletions': {'enabled': False}}


class FakeReads:
    def __init__(self):
        self.operating = ENV['CONFIGS_RELEASE_OPERATING_REPOSITORY']
        self.calls, self.master_reads = [], 0
        self.overrides = {}

    def get(self, repository, suffix='', **options):
        self.calls.append((repository, suffix, options))
        if (repository, suffix) in self.overrides:
            return copy.deepcopy(self.overrides[(repository, suffix)])
        if repository == self.operating:
            return {'id': PRIVATE_ID, 'full_name': self.operating, 'private': True}
        if suffix == '':
            return {'id': C.PUBLIC_ID, 'full_name': C.PUBLIC, 'private': False, 'default_branch': 'master'}
        if suffix == '/git/ref/heads/master':
            self.master_reads += 1
            return {'ref': 'refs/heads/master', 'object': {'type': 'commit', 'sha': SOURCE, 'url': 'fixture'}}
        if suffix == '/actions/runs/4/attempts/1':
            return {'id': 4, 'run_attempt': 1, 'workflow_id': 2, 'head_sha': SOURCE,
                    'head_branch': 'master', 'event': 'workflow_dispatch', 'status': 'in_progress',
                    'repository': {'id': C.PUBLIC_ID}, 'actor': {'id': C.ACTOR},
                    'triggering_actor': {'id': C.ACTOR}}
        if suffix == '/actions/runs/4':
            return {'id': 4, 'run_attempt': 1, 'head_sha': SOURCE}
        if suffix == '/actions/workflows/2':
            return {'id': 2, 'path': C.WORKFLOW}
        if suffix == '/actions/runs/4/attempts/1/jobs?per_page=100':
            return {'total_count': 1, 'jobs': [{'id': 5, 'name': C.JOB, 'run_id': 4,
                    'head_sha': SOURCE, 'status': 'in_progress'}]}
        if suffix.startswith('/branches/'):
            return protected(suffix.split('/')[2])
        if suffix.endswith('/check-runs?per_page=100'):
            return {'total_count': 0, 'check_runs': []}
        if suffix.endswith('/status?per_page=100'):
            return {'sha': SOURCE, 'statuses': []}
        if suffix == '/actions/secrets':
            assert options == {'denied': True}
            return None
        raise AssertionError('unplanned endpoint')


class Proof(unittest.TestCase):
    def setUp(self):
        self.reads = FakeReads()
        self.current = C.runtime(ENV)

    def qualify(self):
        return C.qualify(self.reads, self.current, PRIVATE_ID)

    def test_public_summary_is_read_only_noncertifying_and_private_free(self):
        result = self.qualify()
        self.assertTrue(result['private_repository_read'])
        self.assertFalse(result['operating_enabled'])
        self.assertFalse(result['mutation_permissions_verified'])
        self.assertFalse(result['production_certification'])
        rendered = json.dumps(result)
        self.assertNotIn(ENV['CONFIGS_RELEASE_TOKEN'], rendered)
        self.assertNotIn(self.reads.operating, rendered)

    def test_untrusted_runtime_refuses_before_credential_factory(self):
        for field, value in [('GITHUB_REF', 'refs/heads/dev'), ('GITHUB_EVENT_NAME', 'pull_request'),
                             ('GITHUB_REPOSITORY', 'foreign/repository'), ('GITHUB_ACTOR_ID', '77'),
                             ('GITHUB_JOB', 'candidate'), ('GITHUB_SHA', 'moving'),
                             ('GITHUB_API_URL', 'https://foreign.invalid'), ('GITHUB_RUN_ATTEMPT', None)]:
            with self.subTest(field=field):
                env = dict(ENV, **{field: value})
                def forbidden(*args):
                    self.fail('credential consumed before runtime refusal')
                with contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(C.main(env, forbidden), 1)

    def test_private_numeric_identity_and_visibility_are_required(self):
        for value in ({'id': 100, 'full_name': self.reads.operating, 'private': True},
                      {'id': PRIVATE_ID, 'full_name': self.reads.operating, 'private': False}):
            self.reads.overrides[(self.reads.operating, '')] = value
            with self.assertRaises(C.Refusal):
                self.qualify()

    def test_actual_run_cannot_substitute_event_actor_or_source(self):
        path = '/actions/runs/4/attempts/1'
        original = self.reads.get(C.PUBLIC, path)
        for field, value in [('event', 'push'), ('head_sha', 'b' * 40),
                             ('triggering_actor', {'id': 77}), ('run_attempt', 2)]:
            self.reads.overrides[(C.PUBLIC, path)] = dict(original, **{field: value})
            with self.assertRaises(C.Refusal):
                self.qualify()

    def test_actual_workflow_path_is_bound(self):
        self.reads.overrides[(C.PUBLIC, '/actions/workflows/2')] = {'id': 2, 'path': '.github/workflows/candidate.yml'}
        with self.assertRaises(C.Refusal):
            self.qualify()

    def test_mixed_job_and_incomplete_inventory_refuse(self):
        path = '/actions/runs/4/attempts/1/jobs?per_page=100'
        original = self.reads.get(C.PUBLIC, path)
        for value in (dict(original, total_count=2), {'total_count': 1, 'jobs': []}):
            self.reads.overrides[(C.PUBLIC, path)] = value
            with self.assertRaises(C.Refusal):
                self.qualify()

    def test_wrong_job_or_attempt_does_not_qualify(self):
        path = '/actions/runs/4/attempts/1/jobs?per_page=100'
        original = self.reads.get(C.PUBLIC, path)
        for field, value in [('status', 'completed'), ('head_sha', 'b' * 40), ('name', 'candidate')]:
            self.reads.overrides[(C.PUBLIC, path)] = {'total_count': 1, 'jobs': [dict(original['jobs'][0], **{field: value})]}
            with self.assertRaises(C.Refusal):
                self.qualify()

    def test_protection_policy_changes_refuse(self):
        for field, value in [('enforce_admins', {'enabled': False}), ('allow_force_pushes', {'enabled': True}),
                             ('required_status_checks', {'strict': False, 'contexts': ['other']})]:
            self.reads.overrides[(C.PUBLIC, '/branches/dev/protection')] = dict(protected('dev'), **{field: value})
            with self.assertRaises(C.Refusal):
                self.qualify()

    def test_late_attempt_change_refuses(self):
        self.reads.overrides[(C.PUBLIC, '/actions/runs/4')] = {'id': 4, 'run_attempt': 2, 'head_sha': SOURCE}
        with self.assertRaises(C.Refusal):
            self.qualify()

    def test_late_master_change_refuses(self):
        original = self.reads.get
        def moved(repository, suffix='', **options):
            result = original(repository, suffix, **options)
            if suffix == '/git/ref/heads/master' and self.reads.master_reads == 2:
                result['object']['sha'] = 'b' * 40
            return result
        self.reads.get = moved
        with self.assertRaises(C.Refusal):
            self.qualify()

    def test_checks_use_anonymous_public_read_without_checks_grant(self):
        self.qualify()
        calls = [call for call in self.reads.calls if '/check-runs?' in call[1]]
        self.assertEqual(calls, [(C.PUBLIC, '/commits/' + SOURCE + '/check-runs?per_page=100', {'anonymous': True})])

    def test_refusal_output_does_not_leak_private_exception(self):
        def denied(*args):
            raise C.Refusal(ENV['CONFIGS_RELEASE_TOKEN'] + ' ' + self.reads.operating)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.assertEqual(C.main(ENV, denied), 1)
        self.assertEqual(out.getvalue(), '')
        self.assertEqual(err.getvalue(), 'operating credential read check: refused\n')

    def test_foreign_connection_and_endpoints_refuse(self):
        for name in ('foreign/operating', C.PUBLIC, 'shk95/configs-hosts', 'shk95/configs-host-template'):
            with self.assertRaises(C.Refusal):
                C.Reads('fixture-private-value', name)
        reads = C.Reads('fixture-private-value', self.reads.operating)
        for repo, suffix, kwargs in [('foreign/operating', '', {}), (C.PUBLIC, '/git/refs', {}),
                                    (self.reads.operating, '/actions/secrets', {}),
                                    (self.reads.operating, '', {'anonymous': True})]:
            with self.assertRaises(C.Refusal):
                reads.get(repo, suffix, **kwargs)

    def test_only_get_and_anonymous_checks_omit_authorization(self):
        calls = []
        class Connection:
            def __init__(self, host, **kwargs):
                self.assertions = host, kwargs
            def request(self, method, path, **kwargs):
                calls.append((method, path, kwargs))
            def getresponse(self):
                class Response:
                    status = 200
                    def getheader(self, name): return None
                    def read(self, bound): return b'{}'
                return Response()
            def close(self): pass
        reads = C.Reads('fixture-private-value', self.reads.operating)
        with patch.object(C.http.client, 'HTTPSConnection', Connection):
            reads.get(self.reads.operating)
            reads.get(C.PUBLIC, '/commits/' + SOURCE + '/check-runs?per_page=100', anonymous=True)
        self.assertEqual([row[0] for row in calls], ['GET', 'GET'])
        self.assertIn('Authorization', calls[0][2]['headers'])
        self.assertNotIn('Authorization', calls[1][2]['headers'])
        self.assertTrue(all('body' not in row[2] for row in calls))

    def test_redirect_duplicate_oversize_and_readable_secrets_refuse(self):
        class Connection:
            def __init__(self, *args, **kwargs): pass
            def request(self, *args, **kwargs): pass
            def getresponse(self): return response
            def close(self): pass
        class Response:
            status = 200
            location = None
            data = b'{}'
            def getheader(self, name): return self.location
            def read(self, bound): return self.data
        reads = C.Reads('fixture-private-value', self.reads.operating)
        for location, data in [('https://foreign.invalid', b'{}'), (None, b'{"x":1,"x":2}'),
                               (None, b'x' * (C.MAX_BODY + 1))]:
            response = Response(); response.location, response.data = location, data
            with patch.object(C.http.client, 'HTTPSConnection', Connection), self.assertRaises(C.Refusal):
                reads.get(C.PUBLIC)
        response = Response()
        with patch.object(C.http.client, 'HTTPSConnection', Connection), self.assertRaises(C.Refusal):
            reads.get(C.PUBLIC, '/actions/secrets', denied=True)
        for status in (403, 404):
            response.status = status
            with patch.object(C.http.client, 'HTTPSConnection', Connection):
                self.assertIsNone(reads.get(C.PUBLIC, '/actions/secrets', denied=True))

    def test_workflow_separates_secret_step_from_pinned_checkout(self):
        text = (TOOLS.parents[1] / C.WORKFLOW).read_text()
        self.assertIn("github.ref == 'refs/heads/master'", text)
        self.assertIn("github.actor_id == '101378576'", text)
        self.assertIn('environment: release-control', text)
        self.assertIn('ref: ${{ github.sha }}', text)
        self.assertIn('persist-credentials: false', text)
        self.assertEqual(text.count('CONFIGS_RELEASE_TOKEN:'), 1)
        self.assertNotIn('schedule:', text)
        self.assertNotIn('workflow_run:', text)
        self.assertNotIn('upload-artifact', text)
        self.assertNotIn('GH_TOKEN:', text)
        self.assertLess(text.index('persist-credentials: false'), text.index('CONFIGS_RELEASE_TOKEN:'))


if __name__ == '__main__':
    unittest.main()
