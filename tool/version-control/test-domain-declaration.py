"""Original disposable source objects and synthetic GETs; no actual approval."""
# INV repository/domain-declaration-observation
# INV repository/fixture-git-isolation
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('domain', ROOT/'release-domain-declaration.py')
D = importlib.util.module_from_spec(spec); spec.loader.exec_module(D)
RULES = b'format\t1\ncheck\ta\tunixlike\tfixtures\trequired\t-\ttest\ncheck\tb\tunixlike\tfixtures\trequired\t-\ttest\ncheck\tw\twindows\tfixtures\trequired\t-\ttest\n'
SCOPE = {'source': '1'*40, 'rules-digest': D.sha(RULES), 'protocol': '4', 'manifest': 'c'*64}


def git(path, *arguments):
    return subprocess.check_output(['git', '-C', str(path), *arguments], stderr=subprocess.DEVNULL)


def envelope():
    body = {'format': 1, 'preparation': 'a'*64, 'source': '2'*40, 'base': '3'*40,
        'before-lock': 'b'*64, 'after-lock': 'd'*64, 'utility-source': '4'*40,
        'utility-manifest': 'e'*64, 'source-fingerprint': 'f'*64,
        'rules-source': SCOPE['source'], 'rules-digest': SCOPE['rules-digest'],
        'semantic-protocol': '4', 'semantic-manifest': SCOPE['manifest'],
        'declarations': {'Release-Format': '1', 'Release-Domain': 'unixlike',
            'Release-Impact': 'patch', 'Release-Contracts': 'b,a',
            'Release-Compatibility': 'compatible', 'Release-Rationale': 'Literal original data',
            'Release-Migration': 'none'}}
    return {'format': 1, 'body': body, 'body-digest': D.sha(D.canonical(body)),
        'staging': {'controller-source': SCOPE['source'], 'workflow': 11, 'actor': 17,
            'run': 21, 'attempt': 1, 'job': 25, 'batch': '9'*64, 'generation': '3',
            'operating-parent': '5'*40}}


def parsed(value=None, scope=None):
    value = copy.deepcopy(value if value is not None else envelope())
    if 'body-digest' in value and type(value.get('body')) is dict:
        value['body-digest'] = D.sha(D.canonical(value['body']))
    raw = D.canonical(value)
    return D.parse_full_d1(raw, D.sha(raw), scope or SCOPE, RULES)


class Service:
    def __init__(self, authority, digest):
        a = authority
        run = {'id': 71, 'run_attempt': 1, 'workflow_id': 72, 'head_sha': a['source'],
            'head_branch': 'master', 'event': 'workflow_dispatch', 'repository': {'id': D.PUBLIC_ID},
            'head_repository': {'id': D.PUBLIC_ID}, 'actor': {'id': 17},
            'triggering_actor': {'id': 17}, 'status': 'completed', 'conclusion': 'success',
            'display_title': 'release-declaration:' + digest, 'path': D.WORKFLOW_PATH}
        self.rows = {'/actions/runs/71': run, '/actions/runs/71/attempts/1': copy.deepcopy(run),
            '/actions/workflows/72': {'id': 72, 'path': D.WORKFLOW_PATH},
            '/actions/runs/71/approvals': [{'state': 'approved', 'user': {'id': 19},
                'comment': 'declaration:' + digest, 'environments': [{'id': 74, 'name': D.ENVIRONMENT}]}],
            '/environments/'+D.ENVIRONMENT: {'id': 74, 'name': D.ENVIRONMENT},
            '/actions/runs/71/attempts/1/jobs?per_page=100&page=1': {'total_count': 1,
                'jobs': [{'id': 75, 'run_id': 71, 'head_sha': a['source'], 'name': D.JOB,
                    'status': 'completed', 'conclusion': 'success',
                    'html_url': 'https://github.com/'+D.PUBLIC+'/actions/runs/71/job/75'}]}}
        self.calls = []; self.headers = {}; self.change = None
    def request(self, path, timeout=30):
        self.calls.append((path, timeout)); suffix = path.removeprefix('/repos/'+D.PUBLIC)
        value = copy.deepcopy(self.rows[suffix]); headers = copy.deepcopy(self.headers.get(suffix, {}))
        if self.change:
            self.change(suffix, sum(p == path for p, _ in self.calls), value, headers)
        return value, headers


class Declaration(unittest.TestCase):
    # INV repository/domain-declaration-observation
    # INV repository/fixture-git-isolation
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        git(self.root, 'init', '--initial-branch=main')
        git(self.root, 'config', 'user.name', 'Fixture')
        git(self.root, 'config', 'user.email', 'fixture@example.invalid')
        self.a = dict(D.POLICY, source='6'*40, **{'role-policy-path': D.POLICY_PATH,
            'role-policy-blob': D.oid('blob', D.canonical(D.POLICY)), 'review-workflow-blob': '7'*40,
            'review-workflow-id': 72, 'review-environment-id': 74, 'dispatch-actors': [17], 'reviewers': [19]})
        workflow = D.render_review_workflow(D.canonical(self.a))
        self.a['review-workflow-blob'] = D.oid('blob', workflow)
        for name, raw in ((D.POLICY_PATH, D.canonical(D.POLICY)), (D.WORKFLOW_PATH, workflow)):
            path = self.root/name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
        git(self.root, 'add', '.'); git(self.root, 'commit', '-m', 'original fixture source')
        self.a['source'] = git(self.root, 'rev-parse', 'HEAD').strip().decode()
        git(self.root, 'commit', '--allow-empty', '-m', 'accepted descendant')
        self.anchor = {'public-repository': D.PUBLIC, 'public-repository-id': D.PUBLIC_ID,
            'source': self.a['source'], 'master': git(self.root, 'rev-parse', 'HEAD').strip().decode(),
            'source-approval': '8'*64}
        self.objects = {}
        for row in git(self.root, 'rev-list', '--objects', 'HEAD').decode().splitlines():
            identity = row.split()[0]; kind = git(self.root, 'cat-file', '-t', identity).strip().decode()
            self.objects[(kind, identity)] = git(self.root, 'cat-file', kind, identity)
        self.source = D.OriginalSource(self.anchor, self.read)
        self.p = parsed(); self.service = Service(self.a, self.p.digest)
        self.lookup = {'format': 1, 'domain': 'unixlike', 'source': self.a['source'],
            'workflow': 72, 'run': 71, 'attempt': 1, 'job': 75}
    def read(self, kind, identity, limit):
        return self.objects.get((kind, identity), b'missing')[:limit+1]
    def observe(self, p=None, a=None, lookup=None, source=None, service=None):
        return D.observe_domain_declaration(p or self.p, D.canonical(lookup or self.lookup),
            D.canonical(a or self.a), source or self.source, service or self.service)
    def test_original_full_data_and_run_scoped_observation(self):
        result = self.observe()
        self.assertEqual(self.p.envelope['body']['declarations']['Release-Contracts'], 'b,a')
        self.assertEqual(self.p.envelope['staging']['generation'], '3')
        self.assertNotEqual(self.p.envelope['staging']['controller-source'], result['source'])
        self.assertEqual(set(result), {'format','kind','domain','declaration','source','workflow','run',
            'attempt','job','reviewer','environment','observation-digest','binding'})
        self.assertEqual(result['binding'], 'run-scoped-environment-approval')
        self.assertEqual(result['reviewer'], 19); self.assertEqual(result['declaration'], self.p.digest)
        self.assertEqual(len(self.service.calls), 9)
        self.assertTrue(all(0 < timeout <= 30 for _, timeout in self.service.calls))
        with self.assertRaises(TypeError): result['environment']['id'] = 0
        with self.assertRaises(TypeError): self.p.envelope['staging']['generation'] = '4'
    def test_protocol4_unsorted_and_protocol5_sorted_are_distinct(self):
        value = envelope(); value['body']['semantic-protocol'] = '5'
        scope = dict(SCOPE, protocol='5')
        with self.assertRaises(D.Refusal): parsed(value, scope)
        value['body']['declarations']['Release-Contracts'] = 'a,b'
        self.assertEqual(parsed(value, scope).envelope['body']['semantic-protocol'], '5')
        value['body']['semantic-protocol'] = '4'
        self.assertEqual(parsed(value).envelope['body']['declarations']['Release-Contracts'], 'a,b')
    def test_every_nested_keyset_refuses_missing_unknown_and_wrong_shape(self):
        for path in ((), ('body',), ('staging',), ('body','declarations')):
            original = envelope()
            target = original
            for name in path: target = target[name]
            for name in tuple(target):
                value = copy.deepcopy(original); row = value
                for key in path: row = row[key]
                del row[name]
                with self.subTest(path=path, missing=name), self.assertRaises(D.Refusal): parsed(value)
            value = copy.deepcopy(original); row = value
            for name in path: row = row[name]
            row['approved'] = True
            with self.subTest(path=path), self.assertRaises(D.Refusal): parsed(value)
        for path in ('body', 'staging'):
            value = envelope(); value[path] = []
            with self.assertRaises(D.Refusal): parsed(value)
    def test_format_numeric_identity_and_historical_scope_refusals(self):
        for target, key, bad in [('top','format',True), ('body','format',True), ('staging','attempt',True),
            ('staging','attempt',2), ('staging','job',True), ('staging','workflow',0),
            ('staging','generation','03'), ('staging','generation','-1'), ('staging','batch','a'*40),
            ('staging','controller-source','f'*40), ('body','rules-source','f'*40),
            ('body','rules-digest','f'*64), ('body','semantic-manifest','f'*64),
            ('body','semantic-protocol','3'), ('body','base','A'*40)]:
            value = envelope(); row = value if target == 'top' else value[target]; row[key] = bad
            with self.subTest(target=target,key=key,bad=bad), self.assertRaises(D.Refusal): parsed(value)
        with self.assertRaises(D.Refusal): D.parse_full_d1(self.p.raw, self.p.digest, dict(SCOPE, approved=True), RULES)
        with self.assertRaises(D.Refusal): D.parse_full_d1(self.p.raw, self.p.digest, SCOPE, RULES+b'\n')
    def test_declaration_grammar_and_literal_string_boundaries(self):
        value = envelope(); d = value['body']['declarations']; d['Release-Rationale'] = 'x'*4096
        self.assertEqual(len(parsed(value).envelope['body']['declarations']['Release-Rationale']), 4096)
        for name, bad in [('Release-Rationale','x'*4097), ('Release-Rationale',''),
            ('Release-Rationale','injected\ntrailer'), ('Release-Rationale','x\u0085y'),
            ('Release-Rationale','x\u2028y'), ('Release-Rationale','x\u2029y'), ('Release-Rationale','\ud800'),
            ('Release-Domain','windows'), ('Release-Format','2'), ('Release-Impact','unknown'),
            ('Release-Compatibility','unknown'), ('Release-Contracts','a,a'), ('Release-Contracts','a,w'),
            ('Release-Contracts','unknown'), ('Release-Contracts','A'), ('Release-Contracts','a,,b'),
            ('Release-Contracts',' a'), ('Release-Migration','/docs/a'), ('Release-Migration','docs/../a'),
            ('Release-Migration','docs/./a'), ('Release-Migration','docs//a'), ('Release-Migration','docs/a/')]:
            value = envelope(); value['body']['declarations'][name] = bad
            with self.subTest(name=name,bad=bad), self.assertRaises(D.Refusal): parsed(value)
        for migration in ('docs/notes/colon:name.md', r'docs/notes/back\slash.md'):
            value = envelope(); value['body']['declarations']['Release-Migration'] = migration
            self.assertEqual(parsed(value).envelope['body']['declarations']['Release-Migration'], migration)
        value = envelope(); value['body']['declarations'].update({'Release-Compatibility':'breaking'})
        with self.assertRaises(D.Refusal): parsed(value)
        value['body']['declarations'].update({'Release-Impact':'major', 'Release-Migration':'docs/policy/change.md'})
        self.assertEqual(parsed(value).envelope['body']['declarations']['Release-Compatibility'], 'breaking')
    def test_digest_duplicate_encoding_recursion_and_byte_refusals(self):
        for raw in (self.p.raw+b'\n', self.p.raw.replace(b'"format":1', b'"format":1,"format":1', 1),
                    b'\xff', b'\xef\xbb\xbf'+self.p.raw, b'x'*65537,
                    b'{"x":NaN}', b'{"x":'+b'1'*5000+b'}', b'['*1000+b'0'+b']'*1000):
            with self.subTest(raw=raw[:20]), self.assertRaises(D.Refusal): D.parse_full_d1(raw, D.sha(raw), SCOPE, RULES)
        with self.assertRaises(D.Refusal): D.parse_full_d1(self.p.raw, 'f'*64, SCOPE, RULES)
        value = json.loads(self.p.raw); value['body-digest'] = 'f'*64; raw = D.canonical(value)
        with self.assertRaises(D.Refusal): D.parse_full_d1(raw, D.sha(raw), SCOPE, RULES)
        self.assertEqual(len(D.json_document(b'"'+b'x'*65534+b'"',65536)),65534)
        with self.assertRaises(D.Refusal): D.json_document(b'"'+b'x'*65535+b'"',65536)
    def test_fixed_authority_and_lookup_have_no_defaults(self):
        for key in self.a:
            value = copy.deepcopy(self.a); del value[key]
            with self.subTest(missing=key), self.assertRaises(D.Refusal): self.observe(a=value)
        for name,bad in [('format',True), ('public-repository-id',True), ('domain','windows'),
            ('dispatch-actors',[]), ('dispatch-actors',[17,17]), ('dispatch-actors',[True]),
            ('reviewers',[19,17]), ('reviewers',list(range(1,18))), ('reviewer-policy','all'),
            ('role-policy-path','foreign.json'), ('review-workflow-path','foreign.yml'),
            ('source','f'*40), ('role-policy-blob','f'*40), ('review-workflow-blob','f'*40)]:
            value = copy.deepcopy(self.a); value[name] = bad
            with self.subTest(name=name), self.assertRaises(D.Refusal): self.observe(a=value)
        for key in self.lookup:
            value = dict(self.lookup); del value[key]
            with self.subTest(missing=key), self.assertRaises(D.Refusal): self.observe(lookup=value)
        for name,bad in [('attempt',True), ('format',True), ('attempt',2), ('workflow',73), ('job',True),
                         ('source','f'*40), ('domain','windows')]:
            value = dict(self.lookup); value[name] = bad
            with self.subTest(name=name), self.assertRaises(D.Refusal): self.observe(lookup=value)
    def test_wrong_moving_and_ambiguous_api_observations_refuse(self):
        cases = [('/actions/runs/71', lambda v:v.update(run_attempt=2)),
            ('/actions/runs/71', lambda v:v.update(display_title='declaration:'+self.p.digest)),
            ('/actions/runs/71/attempts/1', lambda v:v.update(head_sha='f'*40)),
            ('/actions/runs/71', lambda v:v['actor'].update(id=19)),
            ('/actions/runs/71', lambda v:v['repository'].update(id=True)),
            ('/actions/runs/71', lambda v:v.update(event='push')),
            ('/actions/workflows/72', lambda v:v.update(path='foreign.yml')),
            ('/actions/runs/71/approvals', lambda v:v[0].update(state='rejected')),
            ('/actions/runs/71/approvals', lambda v:v[0].update(comment='release-declaration:'+self.p.digest)),
            ('/actions/runs/71/approvals', lambda v:v[0]['user'].update(id=17)),
            ('/actions/runs/71/approvals', lambda v:v.append(copy.deepcopy(v[0]))),
            ('/environments/'+D.ENVIRONMENT, lambda v:v.update(id=999)),
            ('/actions/runs/71/attempts/1/jobs?per_page=100&page=1', lambda v:v['jobs'][0].update(name='foreign')),
            ('/actions/runs/71/attempts/1/jobs?per_page=100&page=1', lambda v:v['jobs'][0].update(id=76)),
            ('/actions/runs/71/attempts/1/jobs?per_page=100&page=1', lambda v:v.update(total_count=2))]
        for route, mutate in cases:
            service = Service(self.a,self.p.digest); mutate(service.rows[route])
            with self.subTest(route=route), self.assertRaises(D.Refusal): self.observe(service=service)
        for route in ('/actions/runs/71', '/actions/runs/71/approvals', '/environments/'+D.ENVIRONMENT):
            service = Service(self.a,self.p.digest)
            def change(suffix, count, value, headers):
                if suffix == route and count == 2:
                    if isinstance(value,list): value[0]['comment'] = 'moving'
                    else: value['moving'] = True
            service.change = change
            with self.subTest(moving=route), self.assertRaises(D.Refusal): self.observe(service=service)
    def test_job_bounds_pagination_and_foreign_headers_refuse(self):
        route = '/actions/runs/71/attempts/1/jobs?per_page=100&page=1'
        for count in (True, -1, 2001):
            service = Service(self.a,self.p.digest); service.rows[route]['total_count'] = count
            with self.assertRaises(D.Refusal): self.observe(service=service)
        for header in ({'Location':'https://else.invalid'}, {'Link':'<https://else.invalid/x>; rel="next"'},
                       {'Link':'<https://api.github.com/repos/shk95/configs/actions/runs/71/attempts/1/jobs?per_page=100&page=2>; rel="next"'},
                       {'Link':'<https://api.github.com/repos/shk95/configs/actions/runs/999/attempts/1/jobs?per_page=100&page=2>; rel="next"'}):
            service=Service(self.a,self.p.digest); service.headers[route]=header
            with self.assertRaises(D.Refusal): self.observe(service=service)
        service=Service(self.a,self.p.digest); service.headers['/actions/runs/71']={'Link':'unexpected'}
        with self.assertRaises(D.Refusal): self.observe(service=service)
        service=Service(self.a,self.p.digest); sample=service.rows[route]['jobs'][0]
        service.rows[route]={'total_count':101,'jobs':[dict(sample,id=n+100) for n in range(100)]}
        service.rows[route[:-1]+'2']={'total_count':102,'jobs':[dict(sample,id=999)]}
        with self.assertRaises(D.Refusal): self.observe(service=service)
        self.assertTrue(any('page=2' in p for p,_ in service.calls))
    def test_original_git_hash_membership_ancestry_and_disabled_source_refuse(self):
        for kind, identity in (('commit',self.a['source']), ('blob',self.a['role-policy-blob']),
                               ('blob',self.a['review-workflow-blob'])):
            original = self.objects[(kind,identity)]; self.objects[(kind,identity)] = b'corrupt'
            with self.subTest(kind=kind), self.assertRaises(D.Refusal): self.observe()
            self.objects[(kind,identity)] = original
        source = D.OriginalSource(dict(self.anchor, master='f'*40),self.read)
        with self.assertRaises(D.Refusal): self.observe(source=source)
        with self.assertRaises(D.Refusal): self.observe(source=dict(self.anchor,accepted=True))
        disabled = D.render_review_workflow(D.canonical(self.a),enabled=False)
        path=self.root/D.WORKFLOW_PATH;path.write_bytes(disabled)
        git(self.root,'add','.');git(self.root,'commit','-m','disabled original source')
        source_oid=git(self.root,'rev-parse','HEAD').strip().decode()
        def reader(kind,identity,limit): return git(self.root,'cat-file',kind,identity)
        a=dict(self.a,source=source_oid,**{'review-workflow-blob':D.oid('blob',disabled)})
        source=D.OriginalSource(dict(self.anchor,master=source_oid,source=source_oid),reader)
        with self.assertRaises(D.Refusal): self.observe(a=a,source=source,lookup=dict(self.lookup,source=source_oid))
    def test_signed_raw_headers_and_unsupported_paths_are_data_only(self):
        raw=b'tree '+b'a'*40+b'\nauthor F <f@example.invalid> 1 +0000\ncommitter F <f@example.invalid> 1 +0000\ngpgsig signed\n continuation\n\nmessage\n'
        self.assertEqual(D.commit(raw),('a'*40,[]))
        for bad in (raw.replace(b' continuation',b'unknown'),raw.replace(b'tree ',b'parent ',1),raw+b'x'*65536):
            with self.assertRaises(D.Refusal):D.commit(bad)
        for mode,name in ((b'120000',b'link'),(b'160000',b'gitlink'),(b'100644',b'..'),(b'100644',b'x/y')):
            with self.assertRaises(D.Refusal):D.tree(mode+b' '+name+b'\0'+bytes.fromhex('a'*40))
    def test_service_count_and_deadline_refuse_without_extra_request(self):
        class Boundary(D.Budget):
            def __init__(self):super().__init__();self.requests=23
        with patch.object(D,'Budget',Boundary):self.assertEqual(self.observe()['job'],75)
        self.assertEqual(len(self.service.calls),9)
        self.service.calls.clear()
        class Count(D.Budget):
            def __init__(self):super().__init__();self.requests=32
        with patch.object(D,'Budget',Count),self.assertRaises(D.Refusal):self.observe()
        self.assertEqual(self.service.calls,[])
        class Expired(D.Budget):
            def __init__(self):super().__init__();self.deadline=self.clock()-1
        with patch.object(D,'Budget',Expired),self.assertRaises(D.Refusal):self.observe()
        self.assertEqual(self.service.calls,[])
        for name in ('approved','qualified','accepted','effect-permission','current-generation'):
            self.assertNotIn(name,self.observe())
        with self.assertRaises(D.Refusal):self.observe(p={'digest':self.p.digest,'approved':True})

    def test_shared_deadline_includes_original_source_and_service_reads(self):
        now=[0]
        class Clock(D.Budget):
            def __init__(self):super().__init__(clock=lambda:now[0])
        parse = D.parse_full_d1
        def slow_parse(*args):
            value = parse(*args); now[0] = 900; return value
        with patch.object(D,'Budget',Clock), patch.object(D,'parse_full_d1',slow_parse), self.assertRaises(D.Refusal):
            self.observe()
        self.assertEqual(self.service.calls,[])
        now[0]=0
        def slow_source(kind,identity,limit):now[0]=900;return self.read(kind,identity,limit)
        source=D.OriginalSource(self.anchor,slow_source)
        with patch.object(D,'Budget',Clock),self.assertRaises(D.Refusal):self.observe(source=source)
        self.assertEqual(self.service.calls,[])
        now[0]=0
        def slow_service(*args):now[0]+=30
        self.service.change=slow_service
        with patch.object(D,'Budget',Clock),self.assertRaises(D.Refusal):self.observe()
        self.assertEqual(len(self.service.calls),1)

    def test_source_reader_unavailability_and_complete_ancestry_count_bound(self):
        def unavailable(*args):raise FileNotFoundError('fixture unavailable')
        with self.assertRaisesRegex(D.Refusal,'original object unavailable'):
            self.observe(source=D.OriginalSource(self.anchor,unavailable))
        objects={};prior=None;source_oid=None
        for n in range(4097):
            raw=(b'tree '+b'a'*40+b'\n'+(b'parent '+prior.encode()+b'\n' if prior else b'')+
                b'author F <f@example.invalid> 1 +0000\ncommitter F <f@example.invalid> 1 +0000\n\n'+str(n).encode()+b'\n')
            current=D.oid('commit',raw);objects[current]=raw
            if source_oid is None:source_oid=current
            if n==4095:boundary=current
            prior=current
        reader=lambda kind,identity,limit:objects[identity]
        anchor=dict(self.anchor,source=source_oid,master=boundary)
        source=D.OriginalSource(anchor,reader);source._budget=D.Budget()
        self.assertEqual(len(source.ancestry(source_oid,boundary)['commits']),4096)
        source=D.OriginalSource(dict(anchor,master=prior),reader);source._budget=D.Budget()
        with self.assertRaisesRegex(D.Refusal,'ancestry bound'):source.ancestry(source_oid,prior)

    def test_response_bound_and_missing_source_membership_refuse(self):
        service=Service(self.a,self.p.digest);service.rows['/actions/runs/71']['extra']='x'*D.MAX_RESPONSE
        with self.assertRaisesRegex(D.Refusal,'document byte bound'):self.observe(service=service)
        source_tree,_=D.commit(self.objects[('commit',self.a['source'])])
        original=self.objects[('tree',source_tree)];self.objects[('tree',source_tree)]=b''
        with self.assertRaises(D.Refusal):self.observe()
        self.objects[('tree',source_tree)]=original
        forged=self.p._replace(raw=self.p.raw+b'\n')
        with self.assertRaises(D.Refusal):self.observe(p=forged)


class Anonymous(unittest.TestCase):
    # INV repository/domain-declaration-observation
    def test_exact_endpoint_allowlist(self):
        for suffix in ('/actions/runs/71','/actions/runs/71/attempts/1','/actions/runs/71/approvals',
            '/actions/workflows/72','/environments/'+D.ENVIRONMENT,
            '/actions/runs/71/attempts/1/jobs?per_page=100&page=20'):
            D.endpoint('/repos/'+D.PUBLIC+suffix)
        for path in ('https://api.github.com/repos/'+D.PUBLIC+'/actions/runs/71',
            '/repos/foreign/repo/actions/runs/71','/repos/'+D.PUBLIC+'/actions/runs/71/attempts/2',
            '/repos/'+D.PUBLIC+'/actions/runs/71/attempts/1/jobs?per_page=100&page=21',
            '/repos/'+D.PUBLIC+'/actions/runs/71?token=secret'):
            with patch.object(D.http.client,'HTTPSConnection') as connection,self.assertRaises(D.Refusal):
                D.Anonymous().request(path)
            connection.assert_not_called()
    def test_anonymous_streamed_get_and_no_fallback_on_refusal(self):
        class Socket:
            def settimeout(self,value):pass
        class Response:
            status=200
            def __init__(self,raw=b'{"id":1}',location=None):self.raw=raw;self.location=location
            def getheader(self,name):return self.location
            def getheaders(self):return []
            def read1(self,n):value=self.raw[:n];self.raw=self.raw[n:];return value
        class Connection:
            def __init__(self,response):self.response=response;self.sock=Socket();self.calls=[];self.closed=False
            def request(self,*args,**kwargs):self.calls.append((args,kwargs))
            def getresponse(self):return self.response
            def close(self):self.closed=True
        for response,success in ((Response(),True),(Response(location='https://else.invalid'),False),
                                  (Response(b'x'*(D.MAX_RESPONSE+1)),False),(Response(b'{"x":NaN}'),False)):
            connection=Connection(response)
            with patch.dict(os.environ,{'HTTPS_PROXY':'https://foreign.invalid','GH_TOKEN':'fixture-only'}),\
                 patch.object(D.http.client,'HTTPSConnection',return_value=connection) as constructor:
                if success:self.assertEqual(D.Anonymous().request('/repos/'+D.PUBLIC+'/actions/runs/71')[0],{'id':1})
                else:
                    with self.assertRaises(D.Refusal):D.Anonymous().request('/repos/'+D.PUBLIC+'/actions/runs/71')
                self.assertEqual(constructor.call_args.args[0],'api.github.com')
                headers=connection.calls[0][1]['headers']
                self.assertNotIn('Authorization',headers);self.assertNotIn('Cookie',headers)
                self.assertEqual(connection.calls[0][0][0],'GET');self.assertEqual(len(connection.calls),1)
                self.assertTrue(connection.closed)


if __name__ == '__main__': unittest.main()
