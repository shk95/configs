"""Trusted finite GitHub transport. Retained semantic code never sees credentials.

This module has no CLI or enabled workflow. Its injectable API is exercised only
in isolated fixtures until a reviewed operating connection is provisioned.
"""
# INV repository/authenticated-release-transport
import base64
import hashlib
import http.client
import json
import re
import ssl
from urllib.parse import urlencode

PUBLIC = 'shk95/configs'
VERSION = '2026-03-10'
MAX_BODY = 4 * 1024 * 1024
MAX_PAGES = 20


class Refusal(ValueError):
    """A bounded reason; never include endpoint response, token or private data."""


class Unknown(Refusal):
    """A write may have happened. Reconcile; never retry from acknowledgement."""


def need(ok, reason):
    if not ok:
        raise Refusal(reason)


def sha(value):
    need(isinstance(value, str) and re.fullmatch('[a-f0-9]{40}', value), 'invalid-object')
    return value


def number(value):
    need(type(value) is int and value > 0, 'invalid-id')
    return value


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def git_object(kind, data):
    return hashlib.sha1(kind.encode() + b' ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def document(data):
    need(type(data) is bytes and len(data) <= MAX_BODY, 'oversize-response')
    def unique(pairs):
        out = {}
        for key, value in pairs:
            need(key not in out, 'duplicate-response-key')
            out[key] = value
        return out
    try:
        return json.loads(data.decode('utf-8'), object_pairs_hook=unique,
                          parse_constant=lambda _: (_ for _ in ()).throw(Refusal('nonfinite-response')))
    except (UnicodeError, json.JSONDecodeError):
        raise Refusal('invalid-response') from None


class Https:
    """Fixed TLS host, no proxy, redirects, subprocess or ambient token discovery."""
    def __init__(self, token):
        self.gate = None
        need(isinstance(token, str) and token and not any(c.isspace() for c in token), 'invalid-credential')
        self.__token = token

    def authorized_write(self, method, path, body):
        return (type(self.gate) is Entry and self.gate.authenticated
                and self.gate.api.channel is self)

    def request(self, method, path, body):
        need(method in {'GET', 'POST', 'PATCH', 'PUT'} and path.startswith('/repos/')
             and not any(c in path for c in '\r\n#') and len(path) < 2048, 'invalid-endpoint')
        need(method == 'GET' or self.authorized_write(method,path,body), 'missing-master-entry')
        connection = http.client.HTTPSConnection('api.github.com', timeout=30,
                                                context=ssl.create_default_context())
        try:
            connection.request(method, path, body=None if body is None else canonical(body), headers={
                'Authorization': 'Bearer ' + self.__token,
                'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': VERSION,
                'Content-Type': 'application/json', 'User-Agent': 'configs-release-transport'})
            response = connection.getresponse()
            data = response.read(MAX_BODY + 1)
            need(len(data) <= MAX_BODY, 'oversize-response')
            return response.status, dict((k.lower(), v) for k, v in response.getheaders()), data
        except (OSError, http.client.HTTPException):
            if method != 'GET':
                raise Unknown('unknown-write') from None
            raise Refusal('unavailable-read') from None
        finally:
            connection.close()


class Api:
    """No caller can supply an external URL or a repository outside bootstrap."""
    def __init__(self, channel, operating):
        need(isinstance(operating, str) and re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', operating)
             and operating not in {PUBLIC, 'shk95/configs-hosts', 'shk95/configs-host-template'}, 'invalid-operating-connection')
        self.channel, self.operating = channel, operating

    def call(self, repository, method, suffix, body=None, statuses=(200,)):
        need(repository in {PUBLIC, self.operating}, 'foreign-repository')
        need(isinstance(suffix, str) and (suffix.startswith('/') or (suffix=='' and method=='GET')) and not any(c in suffix for c in '\r\n#')
             and '..' not in suffix and '://' not in suffix, 'invalid-endpoint')
        code, headers, raw = self.channel.request(method, '/repos/' + repository + suffix, body)
        need(not any(k.lower() == 'location' for k in headers), 'redirect-refused')
        if code not in statuses:
            if method != 'GET':
                raise Unknown('unconfirmed-write')
            raise Refusal('unavailable-read')
        return document(raw) if raw else None, headers

    def get(self, suffix, repository=PUBLIC):
        return self.call(repository, 'GET', suffix)[0]

    def pages(self, suffix, key=None, repository=PUBLIC, parameters=None):
        need('?' not in suffix, 'invalid-pagination')
        parameters = parameters or {}
        need(parameters in ({}, {'state': 'all'}), 'unsupported-list-query')
        query = (urlencode(parameters) + '&') if parameters else ''
        result, ids, total = [], set(), None
        for page in range(1, MAX_PAGES + 1):
            path = suffix + '?' + query + 'per_page=100&page=' + str(page)
            value, headers = self.call(repository, 'GET', path)
            if key:
                need(isinstance(value, dict) and type(value.get('total_count')) is int, 'missing-total')
                if total is None:
                    total = value['total_count']
                need(value['total_count'] == total, 'moving-pagination')
                rows = value.get(key)
            else:
                rows = value
            need(isinstance(rows, list) and len(rows) <= 100, 'invalid-page')
            for row in rows:
                need(isinstance(row, dict), 'invalid-page-item')
                identifier = number(row.get('id'))
                need(identifier not in ids, 'duplicate-page-item')
                ids.add(identifier); result.append(row)
            link = headers.get('link', '')
            need(isinstance(link,str) and (not link or re.fullmatch(r'<[^<>]+>; rel="(?:next|prev|first|last)"(?:, <[^<>]+>; rel="(?:next|prev|first|last)")*',link)), 'unknown-pagination-framing')
            next_links = re.findall(r'<([^>]+)>; rel="next"', link)
            need(len(next_links) <= 1, 'ambiguous-pagination')
            if not next_links:
                need(total is None or len(result) == total, 'incomplete-pages')
                # Full last page without an explicit complete count/Link is ambiguous.
                need(total is not None or len(rows) < 100, 'unknown-page-completeness')
                return result
            expected = 'https://api.github.com/repos/' + repository + suffix + '?' + query + 'per_page=100&page=' + str(page + 1)
            need(next_links == [expected] and len(rows) == 100, 'foreign-or-truncated-pagination')
        raise Refusal('pagination-bound')

    def repository(self, repository):
        return self.get('',repository)

    def ref(self, ref, repository=PUBLIC):
        need(re.fullmatch(r'heads/(master|dev|operations|feature/unixlike-refresh-[a-f0-9]{64})|tags/(unixlike|windows)-v[1-9][0-9]*\.[0-9]+\.[0-9]+', ref), 'unsupported-ref')
        value = self.get('/git/ref/' + ref, repository)
        need(value.get('ref') == 'refs/' + ref and value.get('object', {}).get('type') in {'commit', 'tag'}, 'wrong-ref')
        return sha(value['object']['sha'])

    def commit(self, commit, repository=PUBLIC):
        value = self.get('/git/commits/' + sha(commit), repository)
        need(value.get('sha') == commit and isinstance(value.get('parents'), list), 'wrong-commit')
        return {'sha': commit, 'tree': sha(value.get('tree', {}).get('sha')),
                'parents': [sha(p.get('sha')) for p in value['parents']]}

    def blob(self, blob, repository=PUBLIC):
        value = self.get('/git/blobs/' + sha(blob), repository)
        need(value.get('sha') == blob and value.get('encoding') == 'base64', 'wrong-blob')
        try:
            data = base64.b64decode(value['content'].replace('\n', ''), validate=True)
        except (KeyError, ValueError, TypeError):
            raise Refusal('invalid-blob') from None
        need(len(data) <= MAX_BODY and git_object('blob', data) == blob, 'corrupt-blob')
        return data

    def tree(self, tree, repository=PUBLIC):
        value = self.get('/git/trees/' + sha(tree) + '?recursive=1', repository)
        need(value.get('sha') == tree and value.get('truncated') is False and isinstance(value.get('tree'), list), 'incomplete-tree')
        entries = {}
        for row in value['tree']:
            path = row.get('path')
            need(isinstance(path, str) and path and not path.startswith('/') and '..' not in path.split('/')
                 and not any(ord(c) < 32 for c in path) and path not in entries, 'unsafe-tree')
            need(row.get('mode') in {'100644', '100755', '040000'} and row.get('type') in {'blob', 'tree'}, 'unsafe-tree-mode')
            entries[path] = (row['mode'], row['type'], sha(row.get('sha')))
        return entries

    def run(self, run, attempt):
        number(run); number(attempt)
        value = self.get('/actions/runs/' + str(run) + '/attempts/' + str(attempt))
        need(value.get('id') == run and value.get('run_attempt') == attempt, 'wrong-attempt')
        return value

    def jobs(self, run, attempt):
        return self.pages('/actions/runs/' + str(number(run)) + '/attempts/' + str(number(attempt)) + '/jobs', 'jobs')


class Entry:
    """Independent trusted runtime event plus fresh API source/job verification."""
    def __init__(self, api, trusted, runtime):
        self.authenticated = False
        fields = {'source', 'workflow', 'workflow-path', 'repository-id', 'actors', 'environment', 'job-name'}
        need(set(trusted) == fields and trusted['environment'] and trusted['actors'], 'unresolved-entry')
        need(set(runtime) == {'repository', 'ref', 'event', 'run', 'attempt', 'job', 'actor', 'source', 'environment', 'mode', 'candidate'}, 'invalid-runtime')
        need(runtime['repository'] == PUBLIC and runtime['ref'] == 'refs/heads/master'
             and runtime['event'] == 'workflow_dispatch' and runtime['environment'] == trusted['environment']
             and runtime['source'] == trusted['source'] and runtime['actor'] in trusted['actors']
             and runtime['mode'] in {'start', 'approve', 'stop', 'resume', 'wake', 'inspect'}, 'wrong-entry')
        sha(trusted['source']); number(runtime['actor'])
        need(isinstance(runtime['candidate'], str) and re.fullmatch('[a-f0-9]{64}', runtime['candidate']), 'invalid-candidate')
        # Both latest run and exact attempt are fetched; a stale rerun cannot approve.
        latest = api.get('/actions/runs/' + str(number(runtime['run'])))
        run = api.run(runtime['run'], runtime['attempt'])
        need(latest.get('run_attempt') == runtime['attempt'], 'stale-runtime-attempt')
        need(run.get('head_sha') == trusted['source'] and run.get('head_branch') == 'master'
             and run.get('event') == 'workflow_dispatch' and run.get('workflow_id') == trusted['workflow']
             and run.get('repository', {}).get('id') == trusted['repository-id']
             and run.get('actor', {}).get('id') == runtime['actor']
             and run.get('triggering_actor', {}).get('id') == runtime['actor'], 'unauthenticated-run')
        workflow = api.get('/actions/workflows/' + str(number(trusted['workflow'])))
        need(workflow.get('path') == trusted['workflow-path'], 'wrong-workflow')
        jobs = api.jobs(runtime['run'], runtime['attempt'])
        selected = [j for j in jobs if j.get('id') == runtime['job']]
        need(len(selected) == 1 and selected[0].get('name') == trusted['job-name']
             and selected[0].get('head_sha') == trusted['source']
             and selected[0].get('run_id') == runtime['run']
             and selected[0].get('status') == 'in_progress', 'wrong-entry-job')
        # A provisioned wrapper supplies the Environment-bound event; request bodies
        # never supply runtime. This source does not assert that wrapper is deployed.
        self.api, self.trusted, self.runtime = api, dict(trusted), dict(runtime)
        self.authenticated = True

    def request(self, request):
        need(set(request) == {'mode', 'actor', 'run', 'attempt', 'ref', 'candidate'}, 'invalid-request')
        expected = {k: self.runtime[k] for k in request}
        need(request == expected, 'injected-request')
        return expected

    def protection(self, branch):
        need(branch in {'master', 'dev'}, 'wrong-protected-branch')
        value = self.api.get('/branches/' + branch + '/protection')
        checks = value.get('required_status_checks', {})
        need(checks.get('strict') is (branch == 'dev')
             and checks.get('contexts') == ['Required checks']
             and checks.get('checks') == [{'context': 'Required checks', 'app_id': 15368}]
             and value.get('enforce_admins', {}).get('enabled') is True
             and value.get('required_conversation_resolution', {}).get('enabled') is True
             and value.get('allow_force_pushes', {}).get('enabled') is False
             and value.get('allow_deletions', {}).get('enabled') is False, 'protection-mismatch')
        reviews = value.get('required_pull_request_reviews')
        need(isinstance(reviews, dict) and reviews.get('require_code_owner_reviews') is False
             and reviews.get('required_approving_review_count') == 0, 'unsupported-review-policy')
        return value

    def evidence(self, head, merge_tree, requirements):
        sha(head); sha(merge_tree)
        checks = self.api.pages('/commits/' + head + '/check-runs', 'check_runs')
        receipts = []
        for requirement in requirements:
            need(set(requirement) == {'id', 'name', 'app', 'workflow', 'job', 'tool', 'source', 'attempt', 'run', 'workflow-path', 'workflow-blob', 'tool-path', 'tool-blob'}, 'invalid-check-requirement')
            for key in ('app','workflow','job','attempt','run'):number(requirement[key])
            matches = [c for c in checks if c.get('name') == requirement['name'] and c.get('app', {}).get('id') == requirement['app']]
            need(len(matches) == 1, 'ambiguous-required-check')
            check = matches[0]
            need(check.get('head_sha') == head and check.get('status') == 'completed'
                 and check.get('conclusion') == 'success', 'stale-or-failed-check')
            run = self.api.run(requirement['run'], requirement['attempt'])
            latest = self.api.get('/actions/runs/' + str(requirement['run']))
            need(latest.get('id') == requirement['run'] and latest.get('run_attempt') == requirement['attempt']
                 and latest.get('head_sha') == head and run.get('head_sha') == head
                 and run.get('repository', {}).get('id') == self.trusted['repository-id']
                 and run.get('head_repository', {}).get('id') == self.trusted['repository-id']
                 and run.get('event') in {'push','pull_request','workflow_dispatch'}
                 and latest.get('workflow_id') == run.get('workflow_id') == requirement['workflow']
                 and latest.get('status') == run.get('status')
                 and latest.get('conclusion') == run.get('conclusion')
                 and latest.get('event') == run.get('event')
                 and run.get('status') == 'completed' and run.get('conclusion') == 'success', 'untrusted-check-run')
            jobs = self.api.jobs(requirement['run'], requirement['attempt'])
            matched = [j for j in jobs if j.get('id') == requirement['job']]
            need(len(matched) == 1 and matched[0].get('head_sha') == head
                 and matched[0].get('run_id') == requirement['run'] and matched[0].get('name') == requirement['name']
                 and matched[0].get('status') == 'completed' and matched[0].get('conclusion') == 'success'
                 and check.get('details_url') == matched[0].get('html_url')
                 == 'https://github.com/'+PUBLIC+'/actions/runs/'+str(requirement['run'])+'/job/'+str(requirement['job']), 'unbound-check-job')
            need(sha(requirement['source']) == head and requirement['tool'], 'unbound-tool-source')
            workflow = self.api.get('/actions/workflows/' + str(number(requirement['workflow'])))
            need(workflow.get('id') == requirement['workflow'] and workflow.get('path') == requirement['workflow-path'], 'untrusted-check-definition')
            tree = self.api.tree(self.api.commit(head)['tree'])
            for path_key, blob_key in (('workflow-path','workflow-blob'), ('tool-path','tool-blob')):
                path = requirement[path_key]; blob = sha(requirement[blob_key])
                need(path in tree and tree[path][1:] == ('blob', blob)
                     and tree[path][0] in ({'100644'} if path_key=='workflow-path' else {'100644','100755'}), 'unbound-check-tool-blob')
                self.api.blob(blob) # independently rehash actual authenticated bytes

            receipts.append(dict(requirement, head=head, tree=merge_tree, check=number(check.get('id'))))
        return receipts

    def owner_terminal(self, owner):
        need(set(owner) == {'run', 'attempt', 'job', 'workflow', 'source'}, 'invalid-owner')
        latest = self.api.get('/actions/runs/' + str(number(owner['run'])))
        run = self.api.run(owner['run'], owner['attempt'])
        need(latest.get('run_attempt') == owner['attempt'] and run.get('workflow_id') == owner['workflow']
             and run.get('head_sha') == sha(owner['source']), 'changed-owner')
        jobs = self.api.jobs(owner['run'], owner['attempt'])
        # Run-wide cancellation is safe only when the run has precisely this job.
        need(len(jobs) == 1 and jobs[0].get('id') == owner['job']
             and jobs[0].get('head_sha') == owner['source'], 'foreign-job-in-owner-run')
        return run.get('status') == 'completed' and jobs[0].get('status') == 'completed'

    def cancel(self, owner):
        need((owner.get('run'),owner.get('attempt'),owner.get('job'),owner.get('workflow'),owner.get('source')) ==
             (self.runtime['run'],self.runtime['attempt'],self.runtime['job'],self.trusted['workflow'],self.trusted['source']),
             'foreign-cancel-owner')
        if self.owner_terminal(owner):
            return 'terminal'
        # Recheck exact latest attempt and complete jobs immediately before POST.
        need(not self.owner_terminal(owner), 'owner-finished-before-cancel')
        try:
            self.api.call(PUBLIC, 'POST', '/actions/runs/' + str(owner['run']) + '/cancel', {}, (202,))
        except Unknown:
            pass
        # Acknowledgement never authorizes takeover; callers perform bounded polling.
        return 'terminal' if self.owner_terminal(owner) else 'unknown'

    def wake(self, candidate):
        need(self.runtime['mode'] == 'wake' and candidate == self.runtime['candidate'], 'unowned-wakeup')
        value, _ = self.api.call(PUBLIC, 'POST', '/actions/workflows/' + str(self.trusted['workflow']) + '/dispatches',
              {'ref': 'master', 'inputs': {'mode': 'start', 'candidate': candidate}}, (200,))
        if not (isinstance(value, dict) and type(value.get('workflow_run_id')) is int):
            raise Unknown('unknown-dispatch-receipt')
        run = self.api.run(value['workflow_run_id'], 1)
        need(run.get('head_sha') == self.trusted['source'] and run.get('workflow_id') == self.trusted['workflow']
             and run.get('event') == 'workflow_dispatch' and run.get('head_branch') == 'master', 'wrong-dispatched-run')
        return {'run': value['workflow_run_id'], 'ownership': False, 'approval': False}

    def notification(self, run, attempt):
        latest = self.api.get('/actions/runs/' + str(number(run)))
        need(latest.get('run_attempt') == attempt, 'stale-notification-attempt')
        value = self.api.run(run, attempt)
        need(value.get('workflow_id') == self.trusted['workflow'] and value.get('head_sha') == self.trusted['source']
             and value.get('status') == 'completed' and value.get('conclusion') in {'failure', 'timed_out'}, 'not-action-notification')
        # Actions failure is the transport receipt, not delivery to a user inbox.
        return {'kind': 'actions-failure', 'run': run, 'attempt': attempt, 'delivery': 'unverified'}


class Journal:
    """Immutable Git history and non-force compare-and-advance record publication."""
    def __init__(self, api, snapshot, expected):
        self.api, self.snapshot, self.expected = api, snapshot, sha(expected)
        need(api.ref('heads/operations', api.operating) == expected, 'stale-operating-head')
        self.commit = api.commit(expected, api.operating)
        self.entries = api.tree(self.commit['tree'], api.operating)
        self.pending = False

    def publish(self, changes):
        need(not self.pending, 'unreconciled-record-write')
        Entry(self.api, self.snapshot.entry.trusted, self.snapshot.entry.runtime)
        need(isinstance(changes, dict) and changes and all(type(v) is bytes for v in changes.values()), 'invalid-record-change')
        need(self.api.ref('heads/operations', self.api.operating) == self.expected, 'competing-record-writer')
        for path in changes:
            need(re.fullmatch(r'history/[0-9]{12}\.tsv|current/(index\.tsv|batches\.tsv|transcript\.json)|control/stop\.tsv', path), 'unsupported-record-path')
            if path.startswith('history/'):
                need(path not in self.entries, 'immutable-record-rewrite')
        # The verified retained projector validates full prior history and each new
        # exact event/index/context before Git objects or a ref can be published.
        self.snapshot.validate_changes(changes)
        # Any object/ref effect can become unknown. This instance cannot retry;
        # an independently reconciled original history is a separate obligation.
        self.pending = True
        tree_rows = []
        for path, data in sorted(changes.items()):
            blob = git_object('blob', data)
            response, _ = self.api.call(self.api.operating, 'POST', '/git/blobs',
                                       {'content': base64.b64encode(data).decode(), 'encoding': 'base64'}, (201,))
            need(response.get('sha') == blob, 'record-blob-mismatch')
            tree_rows.append({'path': path, 'mode': '100644', 'type': 'blob', 'sha': blob})
        response, _ = self.api.call(self.api.operating, 'POST', '/git/trees',
                                   {'base_tree': self.commit['tree'], 'tree': tree_rows}, (201,))
        tree = sha(response.get('sha'))
        observed_tree = self.api.tree(tree, self.api.operating)
        expected_leaves = {k:v for k,v in self.entries.items() if v[1] == 'blob'}
        expected_leaves.update({k:('100644', 'blob', git_object('blob', v)) for k,v in changes.items()})
        need({k:v for k,v in observed_tree.items() if v[1] == 'blob'} == expected_leaves, 'record-tree-mismatch')
        # Fixed author/time comes from trusted snapshot; payload supplied by a PR
        # cannot choose a mutable record identity or an external author.
        fields = {'message': 'release operating record\n', 'tree': tree, 'parents': [self.expected],
                  'author': self.snapshot.tagger, 'committer': self.snapshot.tagger}
        response, _ = self.api.call(self.api.operating, 'POST', '/git/commits', fields, (201,))
        commit = sha(response.get('sha'))
        actual = self.api.commit(commit, self.api.operating)
        need(actual['parents'] == [self.expected] and actual['tree'] == tree, 'wrong-record-parent')
        # Fresh expected head plus a single-parent child and force=false means a
        # competing sibling cannot fast-forward to this record. It is not API CAS.
        need(self.api.ref('heads/operations', self.api.operating) == self.expected, 'record-head-moved')
        try:
            self.api.call(self.api.operating, 'PATCH', '/git/refs/heads/operations', {'sha': commit, 'force': False})
        except Unknown:
            pass
        observed = self.api.ref('heads/operations', self.api.operating)
        if observed != commit:
            self.pending = True
            raise Unknown('unknown-or-conflicting-record-head')
        self.expected, self.commit = commit, actual
        self.entries = self.api.tree(tree, self.api.operating)
        self.snapshot.accept_changes(changes, commit)
        self.pending = False
        return commit


class Executor:
    """One durable intent and authenticated reconciliation at a time."""
    def __init__(self, entry, journal, snapshot):
        need(type(entry) is Entry and entry.authenticated, 'missing-entry')
        self.entry, self.api, self.journal, self.snapshot = entry, entry.api, journal, snapshot
        self.unknown = False

    def stopped(self):
        head = self.api.ref('heads/operations', self.api.operating)
        commit = self.api.commit(head, self.api.operating)
        entries = self.api.tree(commit['tree'], self.api.operating)
        need('control/stop.tsv' in entries and entries['control/stop.tsv'][:2] == ('100644', 'blob'), 'missing-fresh-stop')
        raw = self.api.blob(entries['control/stop.tsv'][2], self.api.operating)
        stop = self.snapshot.validate_stop(raw, head)
        need(stop in {True, False}, 'invalid-fresh-stop')
        return stop

    def pulls(self, head, base):
        values = self.api.pages('/pulls', parameters={'state': 'all'})
        # Unfiltered complete all-state inventory avoids ambiguous head-filter results.
        return [p for p in values if p.get('head', {}).get('ref') == head and p.get('base', {}).get('ref') == base]

    def verify_pr(self, value, head, base, source, base_sha):
        need(value.get('state') == 'open' and value.get('head', {}).get('ref') == head
             and value.get('base', {}).get('ref') == base
             and value.get('head', {}).get('repo', {}).get('full_name') == PUBLIC
             and value.get('base', {}).get('repo', {}).get('full_name') == PUBLIC
             and value['head'].get('sha') == source and value['base'].get('sha') == base_sha, 'wrong-pr-pair')
        return number(value.get('number'))

    def reconcile(self, kind, payload):
        if kind in {'refresh-pr', 'pr'}:
            head, base = (payload['branch'], 'dev') if kind == 'refresh-pr' else ('dev', 'master')
            values = self.pulls(head, base)
            need(len(values) <= 1, 'ambiguous-pr')
            if not values:
                return 'absent', None
            if kind == 'pr':
                need(values[0].get('body') == payload['body-operation'], 'wrong-pr-operation')
            source, target = (payload['head'], payload['base']) if kind == 'refresh-pr' else (payload['dev'], payload['master'])
            return 'applied', self.verify_pr(values[0], head, base, source, target)
        if kind == 'merge':
            value = self.api.get('/pulls/' + str(number(payload['number'])))
            if value.get('merged') is not True:
                need(value.get('state') == 'open', 'closed-unmerged-pr')
                return 'absent', None
            commit = self.api.commit(sha(value.get('merge_commit_sha')))
            need(commit['parents'] == [payload['master'], payload['dev']] and commit['tree'] == payload['tree'], 'unexpected-merge-result')
            return 'applied', commit['sha']
        if kind == 'refresh-branch':
            values = self.api.get('/git/matching-refs/heads/' + payload['branch'])
            need(isinstance(values, list) and len(values) <= 1, 'ambiguous-branch')
            if not values:
                return 'absent', None
            row = values[0]
            need(row.get('ref') == 'refs/heads/' + payload['branch'] and row.get('object', {}).get('type') == 'commit', 'wrong-branch')
            actual = sha(row['object']['sha'])
            if actual == payload['head']:
                return 'applied', actual
            need(actual == payload['previous'], 'conflicting-refresh-branch')
            return 'absent', actual
        if kind == 'tag-ref':
            values = self.api.get('/git/matching-refs/tags/' + payload['tag'])
            need(isinstance(values, list) and len(values) <= 1, 'ambiguous-tag')
            if not values:
                return 'absent', None
            need(values[0].get('ref') == 'refs/tags/' + payload['tag'] and values[0].get('object', {}).get('type') == 'tag'
                 and values[0]['object'].get('sha') == payload['object'], 'conflicting-tag')
            return 'applied', payload['object']
        if kind == 'tag-object':
            # Exact object lookup: only an explicit authenticated 404 proves absence.
            code, headers, raw = self.api.channel.request('GET', '/repos/' + PUBLIC + '/git/tags/' + sha(payload['object']), None)
            need(not any(k.lower() == 'location' for k in headers) and len(raw) <= MAX_BODY, 'ambiguous-tag-response')
            if code == 404:
                return 'absent', None
            need(code == 200, 'unknown-tag-object')
            value = document(raw)
            need(value.get('sha') == payload['object'] and value.get('tag') == payload['tag']
                 and value.get('object', {}).get('sha') == payload['source'] and value.get('object', {}).get('type') == 'commit'
                 and value.get('message') == payload['annotation'] and value.get('tagger') == payload['tagger'], 'conflicting-tag-object')
            return 'applied', payload['object']
        if kind == 'cancel':
            return ('applied', payload['run']) if self.entry.owner_terminal(payload) else ('unknown', None)
        raise Refusal('unsupported-effect')

    def perform(self, plan):
        need(not self.unknown and not self.journal.pending, 'unreconciled-effect')
        # Snapshot is independently produced by exact retained-code replay in a
        # credential-free child. A request cannot introduce arbitrary operations.
        kind, payload, intent = self.snapshot.authorize(plan, self.entry)
        need(kind in {'refresh-branch', 'refresh-pr', 'pr', 'merge', 'tag-object', 'tag-ref', 'cancel'}, 'unsupported-effect')
        sha(self.snapshot.source); need(not self.stopped(), 'fresh-stop')
        state, remote = self.reconcile(kind, payload)
        if state == 'applied':
            self.journal.publish(self.snapshot.observation(plan, state, remote))
            return state
        # Persist full immutable intent and derived index before any external effect.
        self.journal.publish(intent)
        need(not self.stopped(), 'stop-before-effect')
        Entry(self.api, self.entry.trusted, self.entry.runtime)
        try:
            if kind == 'cancel':
                result = self.entry.cancel(payload)
                need(result == 'terminal', 'unconfirmed-termination')
            else:
                method, suffix, body, statuses = self.request(kind, payload)
                try:
                    self.api.call(PUBLIC, method, suffix, body, statuses)
                except Unknown:
                    pass
        except Refusal:
            self.unknown = True
            raise Unknown('effect-fenced') from None
        try:
            state, remote = self.reconcile(kind, payload)
            need(state == 'applied', 'effect-not-confirmed')
            self.journal.publish(self.snapshot.observation(plan, state, remote))
        except Refusal:
            self.unknown = True
            raise Unknown('reconciliation-required') from None
        return state

    def request(self, kind, p):
        if kind == 'refresh-branch':
            need(re.fullmatch('feature/unixlike-refresh-[a-f0-9]{64}', p['branch']), 'wrong-refresh-branch')
            commit = self.api.commit(p['head'])
            need(commit['parents'] == [p['parent']] and commit['tree'] == p['tree'], 'wrong-refresh-commit')
            self.snapshot.verify_refresh(p, self.api)
            if p['previous'] == '-':
                return 'POST', '/git/refs', {'ref': 'refs/heads/' + p['branch'], 'sha': p['head']}, (201,)
            return 'PATCH', '/git/refs/heads/' + p['branch'], {'sha': p['head'], 'force': False}, (200,)
        if kind in {'refresh-pr', 'pr'}:
            head, base = (p['branch'], 'dev') if kind == 'refresh-pr' else ('dev', 'master')
            need(not self.pulls(head, base), 'pr-appeared-before-post')
            # Serial writer plus fresh complete absence; GitHub offers no PR-create CAS.
            return 'POST', '/pulls', {'head': head, 'base': base, 'title': 'Release control candidate',
                                    'body': p['body-operation'] if kind == 'pr' else 'operation=' + digest(canonical(p))}, (201,)
        if kind == 'merge':
            self.entry.protection('dev'); self.entry.protection('master')
            need(self.api.ref('heads/dev') == p['dev'] and self.api.ref('heads/master') == p['master'], 'stale-merge-base')
            pr = self.api.get('/pulls/' + str(number(p['number'])))
            self.verify_pr(pr, 'dev', 'master', p['dev'], p['master'])
            need(pr.get('mergeable') is True and pr.get('mergeable_state') == 'clean'
                 and pr.get('draft') is False and pr.get('auto_merge') is None, 'unmergeable-candidate')
            self.snapshot.verify_merge(p, self.entry)
            return 'PUT', '/pulls/' + str(p['number']) + '/merge', {'sha': p['dev'], 'merge_method': 'merge'}, (200,)
        if kind == 'tag-object':
            self.snapshot.verify_publication(p, self.api)
            return 'POST', '/git/tags', {'tag': p['tag'], 'message': p['annotation'], 'object': p['source'],
                                       'type': 'commit', 'tagger': p['tagger']}, (201,)
        if kind == 'tag-ref':
            self.snapshot.verify_publication(p, self.api)
            return 'POST', '/git/refs', {'ref': 'refs/tags/' + p['tag'], 'sha': p['object']}, (201,)
        raise Refusal('unsupported-effect')

    def recover(self, plan):
        # Recovery observes only. Unknown/absent never repeats a write implicitly.
        kind, payload, _ = self.snapshot.authorize_recovery(plan, self.entry)
        state, remote = self.reconcile(kind, payload)
        need(state in {'applied', 'absent'}, 'still-unreconciled')
        self.journal.publish(self.snapshot.observation(plan, state, remote))
        self.unknown = False
        return state
