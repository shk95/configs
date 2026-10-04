"""Original disposable Git and fake anonymous service; no actual approval/native proof."""
# INV repository/typed-production-receipt-custody
# INV repository/fixture-git-isolation
import base64
import copy
import importlib.util
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('receipt',ROOT/'release-production-receipt.py')
R=importlib.util.module_from_spec(spec);spec.loader.exec_module(R)
T=R.T

def git(root,*args):
    return subprocess.check_output(['git','-C',str(root),*args],stderr=subprocess.DEVNULL).decode().strip()

class FakeApi:
    operating='fixture/operating'
    def __init__(self,public,head):self.public=public;self.head=head
    def ref(self,ref,repo=None):return self.head
    def commit(self,head):
        raw=git(self.public,'cat-file','commit',head).splitlines()
        return {'sha':head,'tree':raw[0][5:],'parents':[r[7:] for r in raw if r.startswith('parent ')]}
    def tree(self,tree):
        rows={}
        for row in git(self.public,'ls-tree','-r',tree).splitlines():
            meta,path=row.split('\t');mode,kind,oid=meta.split();rows[path]=(mode,kind,oid)
        return rows
    def blob(self,blob):return subprocess.check_output(['git','-C',str(self.public),'cat-file','blob',blob])

class FakePublic:
    def __init__(self,source,blob,digest):
        run={'id':71,'run_attempt':1,'workflow_id':72,'head_sha':source,'head_branch':'master',
             'event':'workflow_dispatch','repository':{'id':73},'head_repository':{'id':73},
             'actor':{'id':R.REVIEWER},'triggering_actor':{'id':R.REVIEWER},
             'status':'completed','conclusion':'success','display_title':'review:'+digest}
        self.values={'/actions/runs/71':run,'/actions/runs/71/attempts/1':copy.deepcopy(run),
            '/actions/workflows/72':{'id':72,'path':R.PATH},
            '/actions/runs/71/approvals':[{'state':'approved','comment':'review:'+digest,
                'user':{'id':R.REVIEWER},'environments':[{'id':74,'name':R.ENVIRONMENT}]}],
            '/environments/'+R.ENVIRONMENT:{'id':74,'name':R.ENVIRONMENT},
            '/actions/runs/71/attempts/1/jobs?per_page=100&page=1':{'total_count':1,'jobs':[
                {'id':75,'name':R.JOB,'run_id':71,'head_sha':source,'status':'completed','conclusion':'success',
                 'html_url':'https://github.com/shk95/configs/actions/runs/71/job/75'}]}}
        self.calls=[];self.headers={}
    def request(self,path):
        self.calls.append(path)
        key=path if path in self.values else path.removeprefix('/repos/'+R.PUBLIC)
        return copy.deepcopy(self.values[key]),self.headers

class ReceiptProof(unittest.TestCase):
    # INV repository/typed-production-receipt-custody
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.public=self.root/'public';self.public.mkdir()
        git(self.public,'init');git(self.public,'config','user.name','Fixture');git(self.public,'config','user.email','fixture@example.invalid')
        def write(path,raw):
            p=self.public/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
        write(R.PATH,R.workflow(True));write(R.POLICY_PATH,T.canonical(R.POLICY))
        git(self.public,'add','.');git(self.public,'commit','-m','fixture source')
        self.source=git(self.public,'rev-parse','HEAD');blob=git(self.public,'rev-parse','HEAD:'+R.PATH)
        self.authority={'format':1,'source':self.source,'public-repository-id':73,'review-workflow-id':72,
            'review-workflow-path':R.PATH,'review-workflow-blob':blob,'review-job':R.JOB,
            'review-environment-id':74,'review-environment':R.ENVIRONMENT,'reviewer':R.REVIEWER}
        self.producers=[{'id':'prod-windows-ltsc-runtime','kind':'native','domain':'windows','lane':'native-runtime','tool':'lt-sc-profile'}]
        self.checks=[{'id':self.producers[0]['id'],'domain':'windows','lane':'native-runtime','expected_tool':'lt-sc-profile','requiredness':'required'}]
        self.package=self.root/'package';(self.package/'tool/version-control').mkdir(parents=True)
        rules=b'format\t1\nproduction\t1\nproduction-check\tprod-windows-ltsc-runtime\twindows\tnative-runtime\trequired\t-\tlt-sc-profile\nproduction-check\tprod-windows-documentation\twindows\treview\trequired\t-\tcontract-review-v1\nproduction-check\tprod-unixlike-template-pair\tunixlike\tfixtures\trequired\t-\texact-pair-v1\n'
        (self.package/'tool/version-control/release-preview.rules').write_bytes(rules)
        self.scope={'dev':self.source,'master':self.source,'tree':git(self.public,'rev-parse','HEAD^{tree}'),
            'control':self.source,'manifest':'a'*64,'rules':T.digest(rules),
            'baselines-digest':T.digest(b'format\t1\n'),'baselines':base64.b64encode(b'format\t1\n').decode(),
            'selected':['prod-windows-ltsc-runtime'],'requirements-digest':T.digest(T.canonical([]))}
        self.packet={'format':1,'scope':self.scope,'authority':{'source':self.source,'workflow-blob':blob,
            'workflow-path':R.PATH,'job':R.JOB,'environment':R.ENVIRONMENT,'public-repository-id':73,
            'workflow-id':72,'environment-id':74,'reviewer':R.REVIEWER},
            'claims':[dict(self.producers[0],source=self.source,records=['original'],statement='Reviewed original LTSC read-only result.')],
            'raw-records':[{'id':'original','kind':'native','source':self.source,'platform':'windows-ltsc-19044-x64',
                'tool':'lt-sc-profile','command':['pwsh','-NoProfile','read-only-check'],'lane':'native-runtime',
                'result':'verified','content':base64.b64encode(b'original synthetic result\n').decode(),
                'sha256':T.digest(b'original synthetic result\n')}],'template-pair':None}
        self.operating=self.root/'operating';self.operating.mkdir();git(self.operating,'init')
        git(self.operating,'config','user.name','Fixture');git(self.operating,'config','user.email','fixture@example.invalid')
        self.save()
    def save(self):
        raw=T.canonical(self.packet);self.digest=T.digest(raw)
        path=self.operating/('review/packets/'+self.digest+'.json');path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
        index={'format':1,'scope-digest':T.digest(T.canonical(self.scope)),
            'entries':[{'id':self.producers[0]['id'],'packet':self.digest,'run':71,'attempt':1,'job':75}]}
        (self.operating/'review/production-index.json').write_bytes(T.canonical(index))
        git(self.operating,'add','.');git(self.operating,'commit','--allow-empty','-m','fixture packet')
        self.head=git(self.operating,'rev-parse','HEAD');self.api=FakeApi(self.public,self.head)
        self.snapshot=SimpleNamespace(bundle=self.public,source=self.source,operating=self.operating,
            head=self.head,control=self.source,manifest='a'*64,package=self.package,requirements=[],api=self.api,
            entry=SimpleNamespace(trusted={'repository-id':73},evidence=lambda *a:[]))
        self.service=FakePublic(self.source,self.authority['review-workflow-blob'],self.digest)
        self.collector=R.Collector(T.canonical(self.authority),T.canonical(self.producers),public=self.service)
    def collect(self,historical=None):
        return self.collector.collect(self.snapshot,{k:self.scope[k] for k in ('dev','master','tree')},b'format\t1\n',self.checks,historical)
    def refuse(self,fn):
        with self.assertRaises((T.Refusal,ValueError,KeyError,TypeError,subprocess.CalledProcessError)):fn()
    def test_original_packet_custody_projection(self):
        rows,pair,binding=self.collect();self.assertIsNone(pair);self.assertEqual(rows[0]['run'],71);self.assertEqual(binding[0],self.digest)
        self.assertTrue(all(p.startswith('/repos/shk95/configs/') for p in self.service.calls))
    def test_historical_recovery_ignores_replaced_index(self):
        old=[['prod-windows-ltsc-runtime',self.source,self.source,self.scope['tree'],self.scope['rules'],'a'*64,'verified','71','1','75','lt-sc-profile']]
        (self.operating/'review/production-index.json').write_bytes(b'not an index')
        git(self.operating,'add','.');git(self.operating,'commit','-m','replacement hint')
        self.snapshot.head=self.api.head=git(self.operating,'rev-parse','HEAD')
        self.assertEqual(self.collect(old)[0][0]['job'],75)
    def test_review_scope_and_service_refusals(self):
        cases=[('/actions/runs/71',lambda v:v.update(run_attempt=2)),
          ('/actions/runs/71',lambda v:v.update(display_title='changed')),
          ('/actions/runs/71/approvals',lambda v:v[0].update(state='rejected')),
          ('/actions/runs/71/approvals',lambda v:v[0].update(comment='review:'+'b'*64)),
          ('/actions/runs/71/approvals',lambda v:v[0]['user'].update(id=1)),
          ('/actions/runs/71/approvals',lambda v:v.append(copy.deepcopy(v[0]))),
          ('/environments/'+R.ENVIRONMENT,lambda v:v.update(id=999)),
          ('/actions/workflows/72',lambda v:v.update(path='foreign.yml')),
          ('/actions/runs/71/attempts/1/jobs?per_page=100&page=1',lambda v:v['jobs'][0].update(id=999))]
        for route,change in cases:
            with self.subTest(route=route):
                old=copy.deepcopy(self.service.values[route]);change(self.service.values[route]);self.refuse(self.collect);self.service.values[route]=old
    def test_packet_claim_and_profile_refusals(self):
        for change in (lambda p:p.update(run=71),lambda p:p['authority'].update(reviewer=1),
                       lambda p:p['raw-records'][0].update(platform='windows-x64'),
                       lambda p:p['raw-records'][0].update(sha256='b'*64),
                       lambda p:p['claims'][0].update(kind='review'),
                       lambda p:p.update(**{'template-pair':{}})):
            original=copy.deepcopy(self.packet);change(self.packet);self.save();self.refuse(self.collect);self.packet=original;self.save()
    def test_schema_and_canonical_refusals(self):
        for raw in (b'{"x":1,"x":1}',b'{ "x":1}',b'{"x":NaN}',b'[]'+b' '*R.MAX):self.refuse(lambda:R.document(raw))
        a=copy.deepcopy(self.authority);a['review-environment-id']=True
        self.refuse(lambda:R.Collector(T.canonical(a),T.canonical(self.producers)))
    def test_source_workflow_disabled_refuses_approval(self):
        (self.public/R.PATH).write_bytes(R.workflow(False));git(self.public,'add','.');git(self.public,'commit','-m','disabled fixture')
        self.snapshot.source=git(self.public,'rev-parse','HEAD')
        self.authority['source']=self.snapshot.source;self.authority['review-workflow-blob']=git(self.public,'rev-parse','HEAD:'+R.PATH)
        self.collector=R.Collector(T.canonical(self.authority),T.canonical(self.producers),public=self.service)
        self.refuse(self.collect)
    def test_packet_bytes_and_mode_refusals(self):
        path=self.operating/('review/packets/'+self.digest+'.json');path.write_bytes(b'{}')
        git(self.operating,'add','.');git(self.operating,'commit','-m','corrupt original')
        self.snapshot.head=self.api.head=git(self.operating,'rev-parse','HEAD');self.refuse(self.collect)
    def test_selected_optionality_without_packet(self):
        c=R.Collector(T.canonical(self.authority),b'[]',public=self.service)
        self.assertEqual(c.collect(self.snapshot,{k:self.scope[k] for k in ('dev','master','tree')},b'format\t1\n',[]),([],None,[]))
        self.assertEqual(self.service.calls,[])
    def test_actions_runtime_is_not_metadata(self):
        p=copy.deepcopy(self.producers);p[0]['kind']='actions'
        c=R.Collector(T.canonical(self.authority),T.canonical(p),public=self.service)
        self.refuse(lambda:c.expected(self.checks))
    def test_template_original_delivery_and_override_pair(self):
        template=self.root/'template';template.mkdir();git(template,'init');git(template,'config','user.name','Fixture');git(template,'config','user.email','fixture@example.invalid')
        (template/'flake.nix').write_text('synthetic old provider pin; reviewed override pair\n')
        git(template,'add','.');git(template,'commit','-m','delivered adaptation')
        revision=git(template,'rev-parse','HEAD');tree=git(template,'rev-parse','HEAD^{tree}')
        p={'id':'prod-unixlike-template-pair','kind':'template','domain':'unixlike','lane':'fixtures','tool':'exact-pair-v1'}
        self.producers=[p];self.checks=[dict(id=p['id'],domain=p['domain'],lane=p['lane'],expected_tool=p['tool'],requiredness='required')]
        self.scope['selected']=[p['id']]
        self.packet['claims']=[dict(p,source=self.source,records=['original'],statement='Exact source-bound override pair reviewed.')]
        self.packet['raw-records'][0].update(kind='review',platform=None,command=[],tool=p['tool'],lane=p['lane'])
        self.packet['template-pair']={'repository':R.TEMPLATE,'provider':self.source,'revision':revision,'tree':tree,
            'delivery-ref':'refs/heads/main','observed-ref-head':revision,'delivery':'delivered','pair':'verified','record':'original'}
        self.save();self.collector.template=template
        self.service.values['/repos/'+R.TEMPLATE]={'id':R.TEMPLATE_ID,'full_name':R.TEMPLATE,'private':False}
        ref={'ref':'refs/heads/main','object':{'type':'commit','sha':revision}}
        self.service.values['/repos/'+R.TEMPLATE+'/git/ref/heads/main']=ref
        self.assertEqual(self.collect()[1]['provider'],self.source)
        ref['object']['sha']='b'*40;self.refuse(self.collect)
        ref['object']['sha']=revision
        (template/'.git/objects/info/alternates').write_text('/foreign/objects')
        self.refuse(self.collect)
    def test_review_claim_and_packet_retention(self):
        p={'id':'prod-windows-documentation','kind':'review','domain':'windows','lane':'review','tool':'contract-review-v1'}
        self.producers=[p];self.checks=[dict(id=p['id'],domain=p['domain'],lane=p['lane'],expected_tool=p['tool'],requiredness='required')]
        self.scope['selected']=[p['id']];self.packet['claims']=[dict(p,source=self.source,records=['original'],statement='Original contract reviewed.')]
        self.packet['raw-records'][0].update(kind='review',platform=None,command=[],tool=p['tool'],lane=p['lane'])
        self.save();self.assertEqual(self.collect()[0][0]['id'],p['id'])
        (self.operating/('review/packets/'+self.digest+'.json')).unlink()
        git(self.operating,'add','.');git(self.operating,'commit','-m','missing packet')
        self.snapshot.head=self.api.head=git(self.operating,'rev-parse','HEAD');self.refuse(self.collect)
    def test_anonymous_channel_has_no_token_or_write(self):
        from unittest.mock import patch
        calls=[]
        class Response:
            status=200
            def read(self,n):return b'{}'
            def getheader(self,k):return None
            def getheaders(self):return []
        class Connection:
            def __init__(self,*args,**kwargs):self.args=args
            def request(self,*args,**kwargs):calls.append((args,kwargs))
            def getresponse(self):return Response()
            def close(self):pass
        with patch.object(R.http.client,'HTTPSConnection',Connection):
            R.Anonymous().request('/repos/shk95/configs/actions/runs/71/approvals')
        self.assertEqual(calls[0][0][0],'GET');self.assertNotIn('Authorization',calls[0][1]['headers'])
        self.refuse(lambda:R.Anonymous().request('/repos/shk95/configs/actions/runs/71/pending_deployments'))
        self.refuse(lambda:R.Anonymous().request('/repos/foreign/repository'))
    def test_original_graph_refuses_shallow_and_replace(self):
        (self.public/'.git/shallow').write_text(self.source+'\n')
        self.refuse(lambda:self.collector.original_graph(self.public,[self.source]))
    def test_unexpected_pagination_refuses_without_following(self):
        self.service.headers={'Link':'<https://foreign.invalid/next>; rel="next"'}
        self.refuse(self.collect)
        self.assertEqual(self.service.calls,['/repos/shk95/configs/actions/runs/71'])
        self.service.headers={};self.assertEqual(self.collect()[0][0]['job'],75)
    def test_jobs_incomplete_page_and_mixed_inventory_refuse(self):
        route='/actions/runs/71/attempts/1/jobs?per_page=100&page=1'
        self.service.values[route]['total_count']=2
        self.refuse(self.collect)
        self.assertFalse(any('page=2' in p for p in self.service.calls))
        self.service.values[route]['jobs'].append(copy.deepcopy(self.service.values[route]['jobs'][0]))
        self.refuse(self.collect)

    def test_index_and_packet_strictness(self):
        for change in (lambda p:p['scope'].update(**{'baselines-digest':'b'*64}),
                       lambda p:p['claims'][0].update(records=['missing']),
                       lambda p:p['raw-records'].append(dict(p['raw-records'][0],id='unused')),
                       lambda p:p['raw-records'][0].update(command=['x'*4097])):
            original=copy.deepcopy(self.packet);change(self.packet);self.save();self.refuse(self.collect);self.packet=original;self.save()
        self.api.head='b'*40;self.refuse(self.collect)

    def test_legacy_membership_does_not_include_new_files(self):
        spec=importlib.util.spec_from_file_location('preflight',ROOT/'release-transport-preflight.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
        self.assertEqual([len(p.LEGACY_FIVE),len(p.LEGACY_SIX),len(p.LEGACY_SEVEN),len(p.LEGACY_EIGHT)],[5,6,7,8])
        self.assertTrue(all(not any('production-' in n for n in v) for v in (p.LEGACY_FIVE,p.LEGACY_SIX,p.LEGACY_SEVEN,p.LEGACY_EIGHT)))

if __name__=='__main__':unittest.main()
