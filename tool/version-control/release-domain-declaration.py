"""Bounded declaration syntax and independent review observations; DATA only."""
# INV repository/domain-declaration-observation
import collections
import hashlib
import http.client
import json
import re
import ssl
import time
from types import MappingProxyType

PUBLIC = 'shk95/configs'
PUBLIC_ID = 1330390069
POLICY_PATH = 'tool/version-control/release-refresh-role-policy.json'
WORKFLOW_PATH = '.github/workflows/release-declaration-review.yml'
JOB = 'review-refresh-declaration'
ENVIRONMENT = 'release-declaration-review'
VERSION = '2026-03-10'
POLICY = {'format': 1, 'domain': 'unixlike', 'public-repository': PUBLIC,
          'public-repository-id': PUBLIC_ID, 'review-workflow-path': WORKFLOW_PATH,
          'review-job-name': JOB, 'review-environment-name': ENVIRONMENT,
          'reviewer-policy': 'any-one'}
AUTHORITY = set(POLICY) | {'source', 'role-policy-path', 'role-policy-blob',
    'review-workflow-blob', 'review-workflow-id', 'review-environment-id',
    'dispatch-actors', 'reviewers'}
DECLARATIONS = {'Release-' + name for name in
    ('Format', 'Domain', 'Impact', 'Contracts', 'Compatibility', 'Rationale', 'Migration')}
BODY = {'format', 'preparation', 'source', 'base', 'before-lock', 'after-lock',
        'utility-source', 'utility-manifest', 'source-fingerprint', 'rules-source',
        'rules-digest', 'semantic-protocol', 'semantic-manifest', 'declarations'}
STAGING = {'controller-source', 'workflow', 'actor', 'run', 'attempt', 'job',
           'batch', 'generation', 'operating-parent'}
MAX_RESPONSE = 4194304
ParsedDeclaration = collections.namedtuple('ParsedDeclaration', 'raw digest envelope scope rules')


class Refusal(ValueError):
    pass


def need(condition, reason):
    if not condition:
        raise Refusal(reason)


def keys(value, expected, reason):
    need(type(value) is dict and set(value) == set(expected), reason)


def number(value):
    need(type(value) is int and value > 0, 'numeric identity')
    return value


def identity(value, size=64):
    need(type(value) is str and re.fullmatch(r'[a-f0-9]{%s}' % size, value), 'identity')
    return value


def canonical(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(',', ':'),
                          ensure_ascii=False, allow_nan=False).encode('utf-8')
    except (ValueError, TypeError, UnicodeError, RecursionError, OverflowError) as exc:
        raise Refusal('JSON encoding') from exc


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def oid(kind, raw):
    return hashlib.sha1(kind.encode() + b' ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def json_document(raw, limit, exact=True):
    need(type(raw) is bytes and 0 < len(raw) <= limit, 'document byte bound')
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    try:
        value = json.loads(raw.decode('utf-8'), object_pairs_hook=pairs,
            parse_constant=lambda _: (_ for _ in ()).throw(Refusal('nonfinite JSON')))
        stack = [(value, 0)]
        while stack:
            child, depth = stack.pop()
            need(depth <= 16, 'JSON depth')
            if type(child) is dict:
                stack.extend((v, depth + 1) for v in child.values())
            elif type(child) is list:
                stack.extend((v, depth + 1) for v in child)
        encoded = canonical(value)
        need(not exact or encoded == raw, 'noncanonical JSON')
        return value
    except Refusal:
        raise
    except (ValueError, TypeError, UnicodeError, RecursionError, OverflowError) as exc:
        raise Refusal('invalid JSON') from exc


def freeze(value):
    if type(value) is dict:
        return MappingProxyType({k: freeze(v) for k, v in value.items()})
    if type(value) is list:
        return tuple(freeze(v) for v in value)
    return value


def checked_text(value):
    need(type(value) is str, 'string required')
    try:
        need(len(value.encode('utf-8')) <= 4096 and
             not any(ord(c) < 32 or 127 <= ord(c) <= 159 or c in '\u2028\u2029' for c in value), 'string bound/control')
    except UnicodeError as exc:
        raise Refusal('string encoding') from exc


def parse_full_d1(raw, expected_digest, original_scope, original_rules):
    identity(expected_digest)
    keys(original_scope, {'source', 'rules-digest', 'protocol', 'manifest'}, 'original scope')
    identity(original_scope['source'], 40)
    for name in ('rules-digest', 'manifest'):
        identity(original_scope[name])
    need(original_scope['protocol'] in ('4', '5'), 'original protocol')
    need(type(original_rules) is bytes and 0 < len(original_rules) <= 1048576 and
         sha(original_rules) == original_scope['rules-digest'], 'original rules binding')
    envelope = json_document(raw, 65536)
    keys(envelope, {'format', 'body', 'body-digest', 'staging'}, 'envelope fields')
    body, stage = envelope['body'], envelope['staging']
    keys(body, BODY, 'body fields'); keys(stage, STAGING, 'staging fields')
    for value in (envelope['format'], body['format']):
        need(type(value) is int and value == 1, 'declaration format')
    stack = [envelope]
    while stack:
        item = stack.pop()
        if type(item) is dict:
            stack.extend(item.values())
        elif type(item) is str:
            checked_text(item)
    for name in ('source', 'base', 'utility-source', 'rules-source'):
        identity(body[name], 40)
    for name in ('preparation', 'before-lock', 'after-lock', 'utility-manifest',
                 'source-fingerprint', 'rules-digest', 'semantic-manifest'):
        identity(body[name])
    for name in ('controller-source', 'operating-parent'):
        identity(stage[name], 40)
    identity(stage['batch'])
    for name in ('workflow', 'actor', 'run', 'job'):
        number(stage[name])
    need(type(stage['attempt']) is int and stage['attempt'] == 1, 'staging attempt')
    need(type(stage['generation']) is str and
         re.fullmatch(r'0|[1-9][0-9]*', stage['generation']), 'staging generation')
    need(body['rules-source'] == stage['controller-source'] == original_scope['source'] and
         body['rules-digest'] == original_scope['rules-digest'] and
         body['semantic-protocol'] == original_scope['protocol'] and
         body['semantic-manifest'] == original_scope['manifest'], 'original package binding')
    d = body['declarations']; keys(d, DECLARATIONS, 'declaration fields')
    for value in d.values():
        checked_text(value)
    need(d['Release-Format'] == '1' and d['Release-Domain'] == 'unixlike' and
         d['Release-Impact'] in ('none', 'patch', 'minor', 'major') and
         d['Release-Compatibility'] in ('compatible', 'breaking'), 'declaration values')
    migration = d['Release-Migration']
    need(migration == 'none' or (migration.startswith('docs/') and
         all(part not in ('', '.', '..') for part in migration.split('/'))), 'migration path')
    need(d['Release-Rationale'] and (d['Release-Compatibility'] != 'breaking' or
         (d['Release-Impact'] == 'major' and migration != 'none')), 'breaking/rationale')
    contracts = d['Release-Contracts'].split(',')
    need(contracts and all(re.fullmatch(r'[a-z0-9][a-z0-9-]*', c) for c in contracts)
         and len(contracts) == len(set(contracts)), 'contract list')
    need(body['semantic-protocol'] != '5' or contracts == sorted(contracts), 'protocol5 contract order')
    try:
        lines = original_rules.decode('utf-8').splitlines()
    except UnicodeError as exc:
        raise Refusal('rules encoding') from exc
    need(lines and lines[0] == 'format\t1', 'rules format')
    catalog = {}
    for line in lines:
        row = line.split('\t')
        if row[0] in ('check', 'production-check'):
            need(len(row) == 7 and row[1] not in catalog and
                 re.fullmatch(r'[a-z0-9][a-z0-9-]*', row[1]), 'rules catalog')
            catalog[row[1]] = row[2]
    need(all(catalog.get(c) == 'unixlike' for c in contracts), 'foreign/unknown contract')
    identity(envelope['body-digest'])
    need(sha(canonical(body)) == envelope['body-digest'] and sha(raw) == expected_digest,
         'declaration digest')
    return ParsedDeclaration(raw, expected_digest, freeze(envelope),
                             freeze(dict(original_scope)), original_rules)


def authority_document(raw):
    value = json_document(raw, 16384)
    keys(value, AUTHORITY, 'authority fields')
    for key, expected in POLICY.items():
        need(type(value[key]) is type(expected) and value[key] == expected, 'fixed authority')
    need(value['role-policy-path'] == POLICY_PATH, 'fixed policy path')
    for name in ('source', 'role-policy-blob', 'review-workflow-blob'):
        identity(value[name], 40)
    for name in ('review-workflow-id', 'review-environment-id'):
        number(value[name])
    for name in ('dispatch-actors', 'reviewers'):
        rows = value[name]
        need(type(rows) is list and 1 <= len(rows) <= 16, 'provisioned actors/reviewers')
        for row in rows:
            number(row)
        need(rows == sorted(set(rows)), 'actor/reviewer order')
    return value


def render_review_workflow(authority, enabled=True):
    a = authority_document(authority)
    need(type(enabled) is bool, 'renderer flag')
    actors = json.dumps([str(n) for n in a['dispatch-actors']], separators=(',', ':'))
    gate = "${{ github.ref == 'refs/heads/master' && contains(fromJSON('" + actors + "'), github.actor_id) }}" if enabled else 'false'
    raw = ('''name: Unix-like declaration review custody
run-name: release-declaration:${{ inputs.declaration_digest }}
on:
  workflow_dispatch:
    inputs:
      declaration_digest:
        description: SHA256 of the original full declaration envelope
        required: true
        type: string
permissions: {}
jobs:
  review-refresh-declaration:
    if: ''' + gate + '''
    runs-on: ubuntu-latest
    environment: release-declaration-review
    permissions: {}
    steps:
      - name: Validate declaration digest
        env:
          DECLARATION_DIGEST: ${{ inputs.declaration_digest }}
        shell: bash
        run: '[[ "$DECLARATION_DIGEST" =~ ^[a-f0-9]{64}$ ]]'
''').encode('utf-8')
    need(len(raw) <= 16384, 'workflow byte bound')
    return raw


class Budget:
    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self.deadline = clock() + 900
        self.requests = 0
    def remaining(self):
        remaining = self.deadline - self.clock()
        need(remaining > 0, 'observation deadline')
        return remaining


def endpoint(path):
    root = '/repos/' + PUBLIC
    ordinary = root + r'/(?:actions/runs/[1-9][0-9]*(?:/attempts/1|/approvals)?|actions/workflows/[1-9][0-9]*|environments/' + ENVIRONMENT + ')'
    jobs = root + r'/actions/runs/[1-9][0-9]*/attempts/1/jobs\?per_page=100&page=([1-9]|1[0-9]|20)'
    need(type(path) is str and (re.fullmatch(ordinary, path) or re.fullmatch(jobs, path)), 'fixed GET endpoint')


class Anonymous:
    """Fixed-host TLS GET, without environment proxy/auth/cookie/netrc fallback."""
    def request(self, path, timeout=30):
        endpoint(path)
        need(type(timeout) in (int, float) and 0 < timeout <= 30, 'request deadline')
        stop = time.monotonic() + timeout
        connection = http.client.HTTPSConnection('api.github.com', timeout=timeout,
                                                context=ssl.create_default_context())
        def remaining():
            value = stop - time.monotonic()
            need(value > 0, 'request deadline')
            if connection.sock is not None:
                connection.sock.settimeout(value)
            return value
        try:
            connection.request('GET', path, headers={'Accept': 'application/vnd.github+json',
                'X-GitHub-Api-Version': VERSION, 'User-Agent': 'configs-domain-declaration'})
            remaining(); response = connection.getresponse()
            need(response.status == 200 and not response.getheader('Location'), 'unavailable GET')
            raw = bytearray()
            while True:
                remaining()
                block = response.read1(min(16384, MAX_RESPONSE + 1 - len(raw)))
                if not block:
                    break
                raw.extend(block)
                need(len(raw) <= MAX_RESPONSE, 'response byte bound')
            remaining()
            return json_document(bytes(raw), MAX_RESPONSE, exact=False), {
                k.lower(): v for k, v in response.getheaders()}
        except (OSError, http.client.HTTPException) as exc:
            raise Refusal('unavailable GET') from exc
        finally:
            connection.close()


def commit(raw):
    need(type(raw) is bytes and 0 < len(raw) <= 65536 and b'\n\n' in raw, 'commit framing')
    records = []
    for line in raw.split(b'\n\n', 1)[0].split(b'\n'):
        need(b'\0' not in line and b'\r' not in line, 'commit encoding')
        if line.startswith(b' '):
            need(records and records[-1][0] in (b'gpgsig', b'gpgsig-sha256', b'mergetag'), 'commit continuation')
            continue
        need(b' ' in line, 'commit header')
        key, value = line.split(b' ', 1)
        need(key in (b'tree', b'parent', b'author', b'committer', b'encoding',
                     b'gpgsig', b'gpgsig-sha256', b'mergetag') and value, 'commit field')
        records.append((key, value))
    need(records and records[0][0] == b'tree', 'commit tree position')
    for key in (b'tree', b'author', b'committer'):
        need(sum(k == key for k, _ in records) == 1, 'commit mandatory field')
    for key in (b'encoding', b'gpgsig', b'gpgsig-sha256'):
        need(sum(k == key for k, _ in records) <= 1, 'commit duplicate field')
    for key, value in records:
        if key in (b'author', b'committer'):
            need(re.fullmatch(rb'[^<>\x00-\x1f\x7f]+ <[^<> \x00-\x1f\x7f]+> (0|[1-9][0-9]{0,11}) [+-][0-2][0-9][0-5][0-9]', value)
                 and int(value[-4:-2]) <= 23, 'commit identity')
        if key == b'encoding':
            need(value.lower() in (b'utf-8', b'utf8'), 'commit encoding')
    try:
        tree = identity(records[0][1].decode('ascii'), 40)
        parents = [identity(v.decode('ascii'), 40) for k, v in records if k == b'parent']
    except UnicodeError as exc:
        raise Refusal('commit OID encoding') from exc
    need(len(parents) <= 32 and len(parents) == len(set(parents)) and
         [k for k, _ in records[1:1+len(parents)]] == [b'parent'] * len(parents), 'commit parents')
    return tree, parents


def tree(raw):
    need(type(raw) is bytes, 'tree bytes')
    result, cursor, previous = {}, 0, None
    while cursor < len(raw):
        space, zero = raw.find(b' ', cursor), raw.find(b'\0', cursor)
        need(cursor < space < zero and zero + 21 <= len(raw), 'tree framing')
        mode, name = raw[cursor:space], raw[space+1:zero]
        need(mode in (b'40000', b'100644', b'100755') and name and
             b'/' not in name and b'\\' not in name and name not in (b'.', b'..') and
             name.lower() != b'.git' and not any(c < 32 or c == 127 for c in name), 'tree member')
        order = name + (b'/' if mode == b'40000' else b'\0')
        need(previous is None or previous < order, 'tree order'); previous = order
        try:
            text = name.decode('utf-8')
        except UnicodeError as exc:
            raise Refusal('tree path encoding') from exc
        need(text not in result, 'duplicate tree member')
        result[text] = (mode.decode(), raw[zero+1:zero+21].hex())
        cursor = zero + 21
    return result


class OriginalSource:
    """Host-selected original object reader, not a serialized source approval.

    The programmer/provisioner independently authenticates anchor origin and the
    read_object capability. Hash/membership checks cannot supply that premise.
    The reader must enforce its supplied byte limit before returning content.
    No Git command, network, discovery, packet code or private credential is used.
    """
    def __init__(self, anchor, read_object):
        keys(anchor, {'public-repository', 'public-repository-id', 'master', 'source', 'source-approval'}, 'source anchor')
        need(anchor['public-repository'] == PUBLIC and type(anchor['public-repository-id']) is int and
             anchor['public-repository-id'] == PUBLIC_ID, 'source repository')
        identity(anchor['master'], 40); identity(anchor['source'], 40); identity(anchor['source-approval'])
        need(callable(read_object), 'programmer-owned original reader')
        self._anchor = dict(anchor)
        self._read = read_object
        self._budget = None
    def _object(self, kind, identity_value, limit):
        identity(identity_value, 40)
        need(self._budget is not None, 'source observation budget')
        self._budget.remaining()
        try:
            raw = self._read(kind, identity_value, limit)
        except Refusal:
            raise
        except (OSError, LookupError, ValueError, TypeError) as exc:
            raise Refusal('original object unavailable') from exc
        self._budget.remaining()
        need(type(raw) is bytes and len(raw) <= limit and oid(kind, raw) == identity_value, 'original object identity/bound')
        return raw
    def anchor(self):
        return dict(self._anchor)
    def ancestry(self, source, master):
        need(source == self._anchor['source'] and master == self._anchor['master'], 'pinned ancestry')
        queue = collections.deque([master]); found = {master: None}; records = {}; total = 0
        while queue:
            self._budget.remaining()
            current = queue.popleft()
            raw = self._object('commit', current, 65536)
            total += len(raw)
            need(total <= 16777216 and len(records) < 4096, 'ancestry bound')
            _, parents = commit(raw); records[current] = raw
            if current == source:
                path = []
                while current is not None:
                    path.append({'oid': current, 'raw': records[current]})
                    current = found[current]
                return {'source': source, 'master': master, 'commits': list(reversed(path))}
            for parent in parents:
                if parent not in found:
                    need(len(found) < 4096, 'ancestry bound')
                    found[parent] = current; queue.append(parent)
        raise Refusal('source not in accepted ancestry')
    def blob(self, source, path, limit):
        need(source == self._anchor['source'] and path in (POLICY_PATH, WORKFLOW_PATH) and
             type(limit) is int and 0 < limit <= 16384, 'pinned blob request')
        parts = path.split('/'); need(len(parts) <= 64, 'membership depth')
        identity_value, _ = commit(self._object('commit', source, 65536))
        total = 0
        for n, name in enumerate(parts):
            raw = self._object('tree', identity_value, 1048576 - total)
            total += len(raw); need(total <= 1048576, 'membership tree bytes')
            entries = tree(raw); need(name in entries, 'missing original member')
            mode, identity_value = entries[name]
            need(mode == ('100644' if n == len(parts) - 1 else '40000'), 'original member mode')
        return {'source': source, 'path': path, 'mode': mode, 'oid': identity_value,
                'raw': self._object('blob', identity_value, limit)}


def observe_domain_declaration(parsed, lookup, authority, original_source, readonly_api):
    need(type(parsed) is ParsedDeclaration and type(original_source) is OriginalSource,
         'programmer-owned parsed/source boundary')
    budget = Budget()
    parsed = parse_full_d1(parsed.raw, parsed.digest, dict(parsed.scope), parsed.rules)
    budget.remaining()
    a = authority_document(authority)
    lookup = json_document(lookup, 2048)
    keys(lookup, {'format', 'domain', 'source', 'workflow', 'run', 'attempt', 'job'}, 'lookup fields')
    need(type(lookup['format']) is int and lookup['format'] == 1 and lookup['domain'] == 'unixlike'
         and type(lookup['attempt']) is int and lookup['attempt'] == 1, 'lookup format')
    identity(lookup['source'], 40)
    for name in ('workflow', 'run', 'job'):
        number(lookup[name])
    need(lookup['source'] == a['source'] and lookup['workflow'] == a['review-workflow-id'], 'lookup authority')
    # Each invocation owns its budget even when the host reuses a reader.
    original_source = OriginalSource(original_source.anchor(), original_source._read)
    budget.remaining(); original_source._budget = budget
    anchor = original_source.anchor()
    need(anchor['source'] == a['source'], 'independent source anchor')
    witness = original_source.ancestry(a['source'], anchor['master'])
    keys(witness, {'source', 'master', 'commits'}, 'source witness')
    rows = witness['commits']
    need(type(rows) is list and 1 <= len(rows) <= 4096 and
         witness['source'] == a['source'] and witness['master'] == anchor['master'], 'source witness bound')
    prior_parents = None; seen = set(); total = 0
    for n, row in enumerate(rows):
        budget.remaining(); keys(row, {'oid', 'raw'}, 'source commit row')
        identity(row['oid'], 40)
        need(type(row['raw']) is bytes and oid('commit', row['raw']) == row['oid'] and
             row['oid'] not in seen, 'source commit identity')
        total += len(row['raw']); need(total <= 16777216, 'source witness byte bound')
        _, parents = commit(row['raw']); seen.add(row['oid'])
        need((n != 0 or row['oid'] == anchor['master']) and
             (n != len(rows)-1 or row['oid'] == a['source']) and
             (prior_parents is None or row['oid'] in prior_parents), 'source witness path')
        prior_parents = parents
    for path, expected_blob, expected_raw in (
        (POLICY_PATH, a['role-policy-blob'], canonical(POLICY)),
        (WORKFLOW_PATH, a['review-workflow-blob'], render_review_workflow(authority))):
        row = original_source.blob(a['source'], path, 16384)
        keys(row, {'source', 'path', 'mode', 'oid', 'raw'}, 'source blob row')
        need(row['source'] == a['source'] and row['path'] == path and row['mode'] == '100644' and
             row['oid'] == expected_blob and row['raw'] == expected_raw and
             oid('blob', row['raw']) == row['oid'], 'source policy/workflow binding')
    budget.remaining()
    captured, pagination = [], {}
    def get(suffix):
        path = '/repos/' + PUBLIC + suffix; endpoint(path)
        budget.requests += 1; need(budget.requests <= 32, 'service request count')
        timeout = min(30, budget.remaining())
        start = budget.clock()
        value, headers = readonly_api.request(path, timeout=timeout)
        need(budget.clock() - start < timeout, 'service request deadline')
        budget.remaining()
        need(type(headers) is dict and all(type(k) is str and type(v) is str for k, v in headers.items()), 'response headers')
        need(not any(k.lower() == 'location' for k in headers), 'redirect')
        links = [v for k, v in headers.items() if k.lower() == 'link']
        need(not links or '/attempts/1/jobs?' in suffix, 'unexpected pagination')
        relations = {}
        for link in links:
            for item in link.split(','):
                match = re.fullmatch(r'\s*<https://api\.github\.com([^>]+)>;\s*rel="(next|last|prev|first)"\s*', item)
                need(match is not None, 'pagination link')
                endpoint(match[1])
                need(match[1].split('?')[0] == path.split('?')[0], 'foreign pagination')
                need(match[2] not in relations, 'duplicate pagination relation')
                relations[match[2]] = int(match[1].rsplit('=', 1)[1])
        pagination[suffix] = relations
        raw = canonical(value)
        value = json_document(raw, MAX_RESPONSE)
        captured.append(value)
        return value
    run = lookup['run']; suffix = '/actions/runs/' + str(run)
    first = get(suffix); attempt = get(suffix + '/attempts/1')
    for value in (first, attempt):
        need(type(value) is dict, 'run response')
        for key in ('id', 'run_attempt', 'workflow_id'):
            number(value.get(key))
        for key in ('repository', 'head_repository', 'actor', 'triggering_actor'):
            need(type(value.get(key)) is dict, 'run identity'); number(value[key].get('id'))
        need(value['id'] == run and value['run_attempt'] == 1 and
             value['workflow_id'] == a['review-workflow-id'] and value.get('head_sha') == a['source'] and
             value.get('head_branch') == 'master' and value.get('event') == 'workflow_dispatch' and
             value['repository']['id'] == value['head_repository']['id'] == PUBLIC_ID and
             value['actor']['id'] in a['dispatch-actors'] and value['triggering_actor']['id'] in a['dispatch-actors'] and
             value.get('status') == 'completed' and value.get('conclusion') == 'success' and
             value.get('display_title') == 'release-declaration:' + parsed.digest and
             ('path' not in value or value['path'] == WORKFLOW_PATH), 'untrusted run')
    workflow = get('/actions/workflows/' + str(a['review-workflow-id']))
    need(type(workflow) is dict, 'workflow response'); number(workflow.get('id'))
    need(workflow['id'] == a['review-workflow-id'] and workflow.get('path') == WORKFLOW_PATH, 'workflow identity')
    approvals = get(suffix + '/approvals')
    need(type(approvals) is list and len(approvals) == 1 and type(approvals[0]) is dict, 'one review required')
    review = approvals[0]
    need(type(review.get('user')) is dict, 'review user'); number(review['user'].get('id'))
    environments = review.get('environments')
    need(type(environments) is list and len(environments) == 1 and type(environments[0]) is dict, 'review environment')
    number(environments[0].get('id'))
    need(review.get('state') == 'approved' and review['user']['id'] in a['reviewers'] and
         review.get('comment') == 'declaration:' + parsed.digest and
         environments[0]['id'] == a['review-environment-id'] and
         environments[0].get('name') == ENVIRONMENT, 'untrusted review')
    environment = get('/environments/' + ENVIRONMENT)
    need(type(environment) is dict, 'environment response'); number(environment.get('id'))
    need(environment['id'] == a['review-environment-id'] and environment.get('name') == ENVIRONMENT, 'environment identity')
    jobs, count, job_ids = [], None, set()
    for page in range(1, 21):
        job_suffix = suffix + '/attempts/1/jobs?per_page=100&page=' + str(page)
        value = get(job_suffix)
        need(type(value) is dict and type(value.get('total_count')) is int and
             0 <= value['total_count'] <= 2000 and type(value.get('jobs')) is list and
             len(value['jobs']) <= 100, 'job response bound')
        need(count is None or count == value['total_count'], 'moving job count'); count = value['total_count']
        for row in value['jobs']:
            need(type(row) is dict, 'job row'); number(row.get('id'))
            need(row['id'] not in job_ids, 'duplicate job'); job_ids.add(row['id'])
        jobs.extend(value['jobs'])
        need(len(jobs) <= count, 'job count mismatch')
        relations = pagination[job_suffix]
        need('first' not in relations or relations['first'] == 1, 'pagination first')
        need('prev' not in relations or page > 1 and relations['prev'] == page - 1, 'pagination previous')
        need('last' not in relations or relations['last'] == max(1, (count + 99)//100), 'pagination last')
        if len(jobs) == count:
            need('next' not in relations, 'contradictory next page')
            break
        need('next' not in relations or relations['next'] == page + 1, 'pagination next')
        need(len(value['jobs']) == 100 and page < 20, 'incomplete jobs')
    need(len(jobs) == 1, 'sole job required'); job = jobs[0]
    number(job.get('run_id')); identity(job.get('head_sha'), 40)
    need(job['id'] == lookup['job'] and job['run_id'] == run and job['head_sha'] == a['source'] and
         job.get('name') == JOB and job.get('status') == 'completed' and job.get('conclusion') == 'success' and
         job.get('html_url') == 'https://github.com/' + PUBLIC + '/actions/runs/' + str(run) + '/job/' + str(job['id']), 'job identity')
    need(get(suffix) == first and get(suffix + '/approvals') == approvals and
         get('/environments/' + ENVIRONMENT) == environment, 'moving observations')
    budget.remaining()
    output = {'format': 1, 'kind': 'domain-declaration', 'domain': 'unixlike',
        'declaration': parsed.digest, 'source': a['source'], 'workflow': lookup['workflow'],
        'run': run, 'attempt': 1, 'job': job['id'], 'reviewer': review['user']['id'],
        'environment': {'id': environment['id'], 'name': ENVIRONMENT},
        'observation-digest': sha(canonical(captured)), 'binding': 'run-scoped-environment-approval'}
    need(len(canonical(output)) <= 16384, 'observation byte bound')
    return freeze(output)
