"""Typed review custody over original data. No issuer, writes or native execution."""
# INV repository/typed-production-receipt-custody
import base64
import copy
import http.client
import importlib.util
import re
import ssl
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def module(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / file)
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value)
    return value

T = module('receipt_transport', 'release-transport.py')
L = module('receipt_loader', 'release-control-loader.py')
PUBLIC = 'shk95/configs'
TEMPLATE = 'shk95/configs-host-template'
TEMPLATE_ID = 1385102654
PATH = '.github/workflows/release-production-review.yml'
JOB = 'review-production-receipt'
ENVIRONMENT = 'release-production-review'
REVIEWER = 101378576
POLICY_PATH = 'tool/version-control/release-production-review-policy.json'
MAX = 4 * 1024 * 1024
PLATFORMS = {'x86_64-linux', 'aarch64-linux', 'aarch64-darwin', 'windows-x64',
             'windows-ltsc-19044-x64', 'windows-inbox-powershell-5.1-x64'}
POLICY = {'format': 1, 'path': PATH, 'job': JOB, 'environment': ENVIRONMENT,
          'reviewer': REVIEWER, 'template': TEMPLATE, 'template-id': TEMPLATE_ID}


def need(ok, reason):
    T.need(ok, reason)


def keys(value, names):
    need(type(value) is dict and set(value) == set(names.split()), 'receipt-schema')


def identity(value, size=64):
    need(type(value) is str and re.fullmatch('[a-f0-9]{%s}' % size, value), 'receipt-identity')
    return value


def number(value):
    need(type(value) is int and value > 0, 'receipt-numeric-identity')
    return value


def text(value, limit=8192):
    need(type(value) is str and len(value.encode('utf-8')) <= limit and '\0' not in value,
         'receipt-text-bound')


def document(raw, limit=MAX):
    need(type(raw) is bytes and 0 < len(raw) <= limit, 'receipt-byte-bound')
    value = T.document(raw)
    need(T.canonical(value) == raw, 'receipt-noncanonical')
    return value


def ordered(values, key=None):
    need(type(values) is list and len(values) <= 64, 'receipt-array-bound')
    try:
        names = [key(v) for v in values] if key else values
    except (KeyError, TypeError):
        raise T.Refusal('receipt-array-schema') from None
    need(all(type(n) is str for n in names), 'receipt-array-schema')
    need(names == sorted(set(names)), 'receipt-unordered-or-duplicate')


def decoded(value, limit):
    need(type(value) is str and len(value) <= ((limit + 2) // 3) * 4, 'receipt-base64-bound')
    try:
        raw = base64.b64decode(value, validate=True)
    except ValueError:
        raise T.Refusal('receipt-base64') from None
    need(0 < len(raw) <= limit and base64.b64encode(raw).decode('ascii') == value,
         'receipt-base64')
    return raw


def workflow(enabled=False):
    gate = "github.repository == 'shk95/configs' && github.ref == 'refs/heads/master' && github.event_name == 'workflow_dispatch' && github.actor_id == '101378576'" if enabled else 'false'
    return ('''name: Production receipt review custody
run-name: review:${{ inputs.packet_digest }}
on:
  workflow_dispatch:
    inputs:
      packet_digest:
        description: SHA256 of the independently reviewed private canonical packet
        required: true
        type: string
permissions: {}
jobs:
  review-production-receipt:
    if: ''' + gate + '''
    runs-on: ubuntu-latest
    environment: release-production-review
    timeout-minutes: 5
    steps:
      - name: Validate public digest only
        env:
          PACKET_DIGEST: ${{ inputs.packet_digest }}
        shell: bash
        run: '[[ "$PACKET_DIGEST" =~ ^[a-f0-9]{64}$ ]]'
''').encode('utf-8')


class Anonymous:
    """Fixed host GET only; never receives an operating channel or token."""
    def request(self, path):
        allowed = (r'/repos/shk95/configs/(?:actions/runs/[1-9][0-9]*(?:/attempts/1(?:/jobs)?|/approvals)?|actions/workflows/[1-9][0-9]*|environments/release-production-review)',
                   r'/repos/shk95/configs-host-template(?:/git/ref/heads/main)?')
        need(type(path) is str and any(re.fullmatch(p + r'(?:\?per_page=100&page=[1-9][0-9]*)?', path) for p in allowed), 'receipt-endpoint')
        connection = http.client.HTTPSConnection('api.github.com', timeout=30, context=ssl.create_default_context())
        try:
            connection.request('GET', path, headers={'Accept': 'application/vnd.github+json',
                'X-GitHub-Api-Version': T.VERSION, 'User-Agent': 'configs-production-receipt'})
            response = connection.getresponse(); raw = response.read(MAX + 1)
            need(response.status == 200 and len(raw) <= MAX
                 and not response.getheader('Location'), 'receipt-unavailable-read')
            return T.document(raw), dict((k.lower(), v) for k, v in response.getheaders())
        except (OSError, http.client.HTTPException):
            raise T.Refusal('receipt-unavailable-read') from None
        finally:
            connection.close()


class Collector:
    """Independently provisioned producer/authority inputs; packet grants no role."""
    def __init__(self, authority, producers, *, public=None, template=None):
        self.authority_bytes = bytes(authority)
        self.producers_bytes = bytes(producers)
        self.authority = document(authority, 16384)
        keys(self.authority, 'format source public-repository-id review-workflow-id review-workflow-path review-workflow-blob review-job review-environment-id review-environment reviewer')
        a = self.authority
        need(type(a['format']) is int and a['format'] == 1 and a['reviewer'] == REVIEWER
             and a['review-workflow-path'] == PATH and a['review-job'] == JOB
             and a['review-environment'] == ENVIRONMENT, 'receipt-foreign-authority')
        for k in ('public-repository-id', 'review-workflow-id', 'review-environment-id', 'reviewer'):
            number(a[k])
        identity(a['source'], 40); identity(a['review-workflow-blob'], 40)
        self.producers = document(producers, 65536)
        need(type(self.producers) is list and all(type(r) is dict and 'id' in r for r in self.producers), 'receipt-producer-schema')
        ordered(self.producers, lambda r: r['id'])
        for r in self.producers:
            keys(r, 'id kind domain lane tool')
            need(type(r['id']) is str and re.fullmatch('[a-z0-9][a-z0-9-]{0,127}', r['id'])
                 and r['kind'] in {'actions', 'review', 'native', 'template'}
                 and r['domain'] in {'repository', 'unixlike', 'windows'}
                 and r['lane'] in {'review','evaluation','build','native-runtime','fixtures','policy-checks'}, 'receipt-producer')
            text(r['tool'], 4096)
            need(r['tool'], 'receipt-producer-tool')
        self.public = public if public is not None else Anonymous()
        self.template = Path(template) if template is not None else None

    def get(self, suffix, *, template=False):
        repo = TEMPLATE if template else PUBLIC
        value, headers = self.public.request('/repos/' + repo + suffix)
        need(type(headers) is dict and not any(k.lower() == 'location' for k in headers), 'receipt-redirect')
        need('/attempts/1/jobs?' in suffix or not any(k.lower()=='link' for k in headers),
             'receipt-unexpected-pagination')
        return value

    def jobs(self, run):
        rows = []
        for page in range(1, 21):
            value = self.get('/actions/runs/%s/attempts/1/jobs?per_page=100&page=%s' % (run, page))
            need(type(value) is dict and set(value) >= {'total_count','jobs'}
                 and type(value['total_count']) is int and type(value['jobs']) is list, 'receipt-jobs')
            need(0 <= value['total_count'] <= 2000,'receipt-jobs-bound')
            rows.extend(value['jobs'])
            if len(rows) == value['total_count']:
                return rows
            need(len(value['jobs']) == 100 and len(rows) < value['total_count'], 'receipt-incomplete-jobs')
        raise T.Refusal('receipt-jobs-bound')

    def original_blob(self,repo,head,path,limit):
        metadata=L.git(repo,'ls-tree',head,'--',path).decode('utf-8').strip().split()
        need(len(metadata)==4 and metadata[:2]==['100644','blob'] and metadata[3]==path,'receipt-blob-mode')
        blob=identity(metadata[2],40)
        size=L.git(repo,'cat-file','-s',blob).decode('ascii').strip()
        need(size.isdecimal() and 0 < int(size) <= limit,'receipt-byte-bound')
        raw=L.git(repo,'cat-file','blob',blob)
        need(len(raw)==int(size) and T.git_object('blob',raw)==blob,'receipt-original-blob')
        return blob,raw

    def source(self, snapshot):
        a = self.authority
        need(a['public-repository-id'] == snapshot.entry.trusted['repository-id'], 'receipt-foreign-repository')
        L.verify_graphs(snapshot.bundle, [a['source']])
        _, policy = self.original_blob(snapshot.bundle, a['source'], POLICY_PATH,16384)
        need(document(policy, 16384) == POLICY and policy == T.canonical(POLICY), 'receipt-original-policy')
        blob, raw = self.original_blob(snapshot.bundle, a['source'], PATH,16384)
        need(blob == a['review-workflow-blob'] and raw == workflow(True), 'receipt-disabled-or-foreign-source')
        # The independently provisioned original review source must be accepted
        # history, not caller-selected candidate code. Current master is separately live.
        L.git(snapshot.bundle, 'merge-base', '--is-ancestor', a['source'], snapshot.source)
        actual = snapshot.api.commit(a['source']); entries = snapshot.api.tree(actual['tree'])
        need(entries.get(PATH) == ('100644','blob',blob)
             and snapshot.api.blob(blob) == raw, 'receipt-unbound-original-source')
        policy_blob = T.git_object('blob', policy)
        need(entries.get(POLICY_PATH) == ('100644','blob',policy_blob)
             and snapshot.api.blob(policy_blob) == policy, 'receipt-unbound-original-policy')

    def custody(self, snapshot, run, job=None, digest=None):
        number(run); self.source(snapshot); a = self.authority
        first = self.get('/actions/runs/%s' % run)
        attempt = self.get('/actions/runs/%s/attempts/1' % run)
        for value in (first, attempt):
            need(type(value) is dict,'receipt-run-schema')
            for k in ('id','run_attempt','workflow_id'):number(value.get(k))
            for k in ('repository','head_repository','actor','triggering_actor'):
                need(type(value.get(k)) is dict,'receipt-run-schema');number(value[k].get('id'))
            need(type(value) is dict and value.get('id') == run and value.get('run_attempt') == 1
                 and value.get('workflow_id') == a['review-workflow-id']
                 and value.get('head_sha') == a['source'] and value.get('head_branch') == 'master'
                 and value.get('event') == 'workflow_dispatch'
                 and value.get('repository',{}).get('id') == a['public-repository-id']
                 and value.get('head_repository',{}).get('id') == a['public-repository-id']
                 and value.get('actor',{}).get('id') == REVIEWER
                 and value.get('triggering_actor',{}).get('id') == REVIEWER
                 and value.get('status') == 'completed' and value.get('conclusion') == 'success', 'receipt-untrusted-run')
        definition = self.get('/actions/workflows/%s' % a['review-workflow-id'])
        number(definition.get('id'))
        need(definition.get('id') == a['review-workflow-id'] and definition.get('path') == PATH, 'receipt-workflow')
        history = self.get('/actions/runs/%s/approvals' % run)
        need(type(history) is list and len(history) == 1, 'receipt-ambiguous-review')
        approval = history[0]
        need(type(approval) is dict and type(approval.get('user')) is dict,'receipt-review-schema')
        number(approval['user'].get('id'))
        need(approval.get('state') == 'approved' and approval.get('user',{}).get('id') == REVIEWER
             and type(approval.get('environments')) is list and len(approval['environments']) == 1
             and approval['environments'][0].get('id') == a['review-environment-id']
             and approval['environments'][0].get('name') == ENVIRONMENT, 'receipt-unapproved')
        number(approval['environments'][0].get('id'))
        comment = approval.get('comment')
        need(type(comment) is str and re.fullmatch('review:[a-f0-9]{64}', comment), 'receipt-review-comment')
        observed = comment[7:]
        need(digest is None or digest == observed, 'receipt-review-hash')
        need(first.get('display_title') == attempt.get('display_title') == comment, 'receipt-title')
        environment = self.get('/environments/' + ENVIRONMENT)
        number(environment.get('id'))
        need(environment.get('id') == a['review-environment-id'] and environment.get('name') == ENVIRONMENT, 'receipt-environment')
        jobs = self.jobs(run)
        need(len(jobs) == 1, 'receipt-mixed-jobs'); row = jobs[0]; number(row.get('id'))
        need(row.get('name') == JOB and row.get('run_id') == run and row.get('head_sha') == a['source']
             and row.get('status') == 'completed' and row.get('conclusion') == 'success'
             and row.get('html_url') == 'https://github.com/'+PUBLIC+'/actions/runs/'+str(run)+'/job/'+str(row['id'])
             and (job is None or row['id'] == job), 'receipt-job')
        need(self.get('/actions/runs/%s' % run) == first, 'receipt-moving-run')
        return observed, row['id'], T.digest(T.canonical([first,attempt,definition,history,environment,jobs]))

    def blob(self, snapshot, path, limit):
        need(snapshot.api.ref('heads/operations', snapshot.api.operating) == snapshot.head, 'receipt-moving-head')
        _, raw = self.original_blob(snapshot.operating, snapshot.head, path,limit)
        need(len(raw) <= limit, 'receipt-byte-bound')
        return raw

    def scope(self, snapshot, comparison, baseline, checks):
        return dict(comparison, control=snapshot.control, manifest=snapshot.manifest,
                    rules=T.digest((snapshot.package/'tool/version-control/release-preview.rules').read_bytes()),
                    **{'baselines-digest':T.digest(baseline), 'baselines':base64.b64encode(baseline).decode('ascii'),
                       'selected':[r['id'] for r in checks], 'requirements-digest':T.digest(T.canonical(snapshot.requirements))})

    def expected(self, checks):
        need(self.producers_bytes == T.canonical(self.producers) and self.authority_bytes == T.canonical(self.authority), 'receipt-changing-contract')
        need([r['id'] for r in self.producers] == [r['id'] for r in checks], 'receipt-producer-coverage')
        for p, c in zip(self.producers, checks):
            need(c.get('requiredness') == 'required' and (p['domain'],p['lane'],p['tool'])
                 == (c.get('domain'),c.get('lane'),c.get('expected_tool')), 'receipt-qualifier-contract')
            need((p['kind'] == 'review') == (p['lane'] == 'review')
                 and (p['kind']=='template') == (p['id']=='prod-unixlike-template-pair'), 'receipt-producer-lane')
            # Exact production execution profiles cannot be proved by present
            # Actions metadata alone. Review raw execution records instead.
            need(p['kind'] != 'actions' or (not p['id'].startswith('prod-')
                 and not re.search(r'(?:^|:)(?:nix|git|python|pwsh|pester|lua)-[0-9]',p['tool'])),
                 'receipt-unresolved-actions-runtime')
        return [p for p in self.producers if p['kind'] != 'actions']

    def packet(self, snapshot, digest, scope, expected):
        raw = self.blob(snapshot, 'review/packets/'+identity(digest)+'.json', MAX)
        need(T.digest(raw) == digest, 'receipt-packet-hash'); value = document(raw)
        keys(value, 'format scope authority claims raw-records template-pair')
        need(type(value['format']) is int and value['format'] == 1, 'receipt-format')
        keys(value['scope'], 'dev master tree control manifest rules baselines-digest requirements-digest baselines selected')
        need(value['scope'] == scope, 'receipt-packet-scope')
        for k in ('dev','master','tree','control'): identity(scope[k],40)
        for k in ('manifest','rules','baselines-digest','requirements-digest'): identity(scope[k])
        need(T.digest(decoded(scope['baselines'],MAX)) == scope['baselines-digest'], 'receipt-baseline')
        a = self.authority
        required = {'source':a['source'], 'workflow-blob':a['review-workflow-blob'], 'workflow-path':PATH,
            'job':JOB, 'environment':ENVIRONMENT, 'public-repository-id':a['public-repository-id'],
            'workflow-id':a['review-workflow-id'], 'environment-id':a['review-environment-id'], 'reviewer':REVIEWER}
        keys(value['authority'],'source workflow-blob workflow-path job environment public-repository-id workflow-id environment-id reviewer')
        for k in ('public-repository-id','workflow-id','environment-id','reviewer'):number(value['authority'][k])
        need(value['authority'] == required, 'receipt-packet-authority')
        claims=value['claims']; records=value['raw-records']; ordered(claims,lambda r:r['id']); ordered(records,lambda r:r['id'])
        need([r['id'] for r in claims] == [r['id'] for r in expected], 'receipt-claim-coverage')
        by_record={r['id']:r for r in records}; used=[]; total=0
        for c,p in zip(claims,expected):
            keys(c,'id kind domain lane tool source records statement')
            need(all(c[k] == p[k] for k in ('id','kind','domain','lane','tool')) and c['source'] == scope['dev'], 'receipt-claim-binding')
            text(c['statement']); need(c['statement'], 'receipt-empty-claim'); ordered(c['records']); need(c['records'], 'receipt-no-record')
            for rid in c['records']:
                need(rid in by_record and rid not in used, 'receipt-record-reference'); used.append(rid)
                r=by_record[rid]; keys(r,'id kind source platform tool command lane result content sha256')
                need(type(rid) is str and re.fullmatch('[a-z0-9][a-z0-9-]{0,127}',rid)
                     and r['source'] == scope['dev'] and r['tool'] == c['tool'] and r['lane'] == c['lane']
                     and r['result'] == 'verified' and r['kind'] in {'review','native'}, 'receipt-record-binding')
                data=decoded(r['content'],512*1024); total+=len(data)
                need(T.digest(data) == identity(r['sha256']) and total <= 3*1024*1024, 'receipt-record-hash')
                if r['kind'] == 'review':
                    need(r['platform'] is None and r['command'] == [] and c['kind'] != 'native', 'receipt-review-profile')
                else:
                    need(r['platform'] in PLATFORMS and type(r['command']) is list and 1 <= len(r['command']) <= 64, 'receipt-native-profile')
                    for part in r['command']: text(part,4096)
                    profiles={'prod-unixlike-darwin-capture':'aarch64-darwin','prod-windows-ltsc-runtime':'windows-ltsc-19044-x64',
                        'prod-windows-bootstrap':'windows-inbox-powershell-5.1-x64',
                        'prod-unixlike-build-x86-64-linux':'x86_64-linux','prod-unixlike-build-aarch64-linux':'aarch64-linux',
                        'prod-unixlike-build-aarch64-darwin':'aarch64-darwin','prod-windows-native':'windows-x64',
                        'prod-repository-native':'windows-x64'}
                    need(c['id'] not in profiles or r['platform'] == profiles[c['id']], 'receipt-wrong-platform')
        need(sorted(used) == sorted(by_record), 'receipt-unused-record')
        pair=value['template-pair']; selected=any(p['kind']=='template' for p in expected)
        need(selected == (pair is not None), 'receipt-template-optionality')
        if selected:
            keys(pair,'repository provider revision tree delivery-ref observed-ref-head delivery pair record')
            need(pair['repository']==TEMPLATE and pair['provider']==scope['dev'] and pair['delivery-ref']=='refs/heads/main'
                 and pair['delivery']=='delivered' and pair['pair']=='verified' and pair['record'] in used
                 and any(c['kind']=='template' and c['id']=='prod-unixlike-template-pair' and pair['record'] in c['records'] for c in claims), 'receipt-template-binding')
            for k in ('revision','tree','observed-ref-head'):identity(pair[k],40)
            self.template_pair(pair)
        return value

    def original_graph(self, repo, heads):
        need(L.git(repo,'rev-parse','--show-object-format').strip()==b'sha1'
             and L.git(repo,'rev-parse','--is-shallow-repository').strip()==b'false'
             and not L.git(repo,'for-each-ref','--format=%(refname)','refs/replace').strip(),'receipt-incomplete-graph')
        common=Path(L.git(repo,'rev-parse','--path-format=absolute','--git-common-dir').decode().strip())
        for path in (common/'objects/info/alternates',common/'info/grafts',common/'shallow'):
            need(not path.is_symlink() and (not path.exists() or (path.is_file() and path.stat().st_size==0)), 'receipt-alternate-graph')
        need(not list((common/'objects/pack').glob('*.promisor')),'receipt-promisor-graph')
        count=dict(line.split(': ',1) for line in L.git(repo,'count-objects','-v').decode('ascii').splitlines())
        need(int(count['count'])+int(count['in-pack']) <= 20000,'receipt-object-bound')
        total=0;files=0
        for path in (common/'objects').rglob('*'):
            need(not path.is_symlink(),'receipt-symlink-graph')
            if path.is_file():
                total+=path.stat().st_size;files+=1
                need(total<=128*1024*1024 and files<=20000,'receipt-graph-bound')
        L.verify_graphs(repo,heads)
        L.git(repo,'fsck','--strict','--no-dangling','--no-reflogs','--no-progress',*heads)

    def template_pair(self, pair):
        need(self.template is not None, 'receipt-missing-template-objects')
        repo=self.get('',template=True); ref=self.get('/git/ref/heads/main',template=True)
        self.original_graph(self.template,[pair['observed-ref-head'],pair['revision']])
        need(repo.get('id')==TEMPLATE_ID and repo.get('full_name')==TEMPLATE and repo.get('private') is False
             and ref.get('ref')=='refs/heads/main' and ref.get('object',{}).get('type')=='commit'
             and ref['object'].get('sha')==pair['observed-ref-head'], 'receipt-template-ref')
        L.verify_graphs(self.template,[pair['observed-ref-head'],pair['revision']])
        L.git(self.template,'merge-base','--is-ancestor',pair['revision'],pair['observed-ref-head'])
        need(L.git(self.template,'rev-parse',pair['revision']+'^{tree}').decode().strip()==pair['tree'], 'receipt-template-tree')
        need(self.get('/git/ref/heads/main',template=True)==ref, 'receipt-moving-template')
        # Compatibility/provider override is the reviewed raw pair claim, not
        # a demand that a pre-release template pin already equals candidate.

    def collect(self, snapshot, comparison, baseline, checks, historical=None):
        try:
            return self._collect(snapshot,comparison,baseline,checks,historical)
        except T.Refusal:
            raise
        except (ValueError,TypeError,KeyError,IndexError,AttributeError,OSError,UnicodeError,subprocess.SubprocessError):
            raise T.Refusal('receipt-unavailable-binding') from None

    def _collect(self, snapshot, comparison, baseline, checks, historical=None):
        domains={}
        for line in (snapshot.package/'tool/version-control/release-preview.rules').read_text().splitlines():
            fields=line.replace('\\t','\t').split('\t')
            if fields[0] in {'check','production-check'}:
                need(len(fields)==7 and fields[1] not in domains,'receipt-original-check-definition')
                domains[fields[1]]=fields[2]
        checks=copy.deepcopy(checks)
        for check in checks:
            need(check['id'] in domains,'receipt-unmapped-check-domain')
            check['domain']=domains[check['id']]
        expected=self.expected(checks); actions=[r for r in snapshot.requirements if r['id'] in {p['id'] for p in self.producers if p['kind']=='actions'}]
        need(len(actions)==len([p for p in self.producers if p['kind']=='actions']), 'receipt-actions-coverage')
        receipts=snapshot.entry.evidence(comparison['dev'],comparison['tree'],actions)
        pair=None; binding=[]
        if expected:
            scope=self.scope(snapshot,comparison,baseline,checks)
            if historical is None:
                index=document(self.blob(snapshot,'review/production-index.json',256*1024),256*1024)
                keys(index,'format scope-digest entries'); need(type(index['format']) is int and index['format']==1
                    and index['scope-digest']==T.digest(T.canonical(scope)), 'receipt-index-scope')
                entries=index['entries']; ordered(entries,lambda r:r['id'])
                need([r['id'] for r in entries]==[r['id'] for r in expected], 'receipt-index-coverage')
                for row in entries:
                    keys(row,'id packet run attempt job');identity(row['packet']);number(row['run']);number(row['attempt']);number(row['job'])
                    need(row['attempt']==1, 'receipt-index-attempt')
                need(len({(r['packet'],r['run'],r['job']) for r in entries})==1,'receipt-split-review')
                digest,run,job=entries[0]['packet'],entries[0]['run'],entries[0]['job']
            else:
                need(type(historical) is list and [r[0] for r in historical]==[r['id'] for r in expected]
                     and len({(r[7],r[8],r[9]) for r in historical})==1, 'receipt-historical-coverage')
                run=int(historical[0][7]); job=int(historical[0][9]);need(historical[0][8]=='1','receipt-historical-attempt')
                digest=None
            digest,job,observation=self.custody(snapshot,run,job,digest)
            packet=self.packet(snapshot,digest,scope,expected);pair=packet['template-pair']
            for p in expected:
                receipts.append({'id':p['id'],'run':run,'attempt':1,'job':job,'tool':p['tool']})
            binding=[digest,run,job,observation]
            need(self.custody(snapshot,run,job,digest)[2]==observation,'receipt-moving-custody')
        need(snapshot.api.ref('heads/operations',snapshot.api.operating)==snapshot.head,'receipt-moving-head')
        return sorted(receipts,key=lambda r:r['id']),pair,binding
