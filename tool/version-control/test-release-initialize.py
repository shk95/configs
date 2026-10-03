"""Original disposable Git and fake metadata; never private operating proof."""
# INV repository/initializer-attempt-custody
# INV repository/fixture-git-isolation
import base64
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parent
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
I=load('initializer_proof','release-initialize.py')
F=load('initializer_fixtures','test-release-operating-history.py')
T=I.T;H=I.H;L=I.L

class InitializerProof(unittest.TestCase):
    # INV repository/initializer-attempt-custody
    # INV repository/fixture-git-isolation
    def setUp(self):
        self.fixture=F.HistoryProof();self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
        f=self.fixture
        bundle,approved,config,desired=f.desired_inputs()
        workflow=bundle/I.WORKFLOW;workflow.write_bytes((ROOT.parents[1]/I.WORKFLOW).read_bytes())
        F.F.F.run_git(bundle,'add','.');F.F.F.run_git(bundle,'commit','-qm','chore(repository): fixture initializer source')
        self.source=F.F.F.run_git(bundle,'rev-parse','HEAD');f.fake.source=self.source
        self.bundle=bundle;self.approved=F.F.F.encode(dict(L.approved(approved),master=self.source))
        self.config=config;self.desired=desired;self.fake=f.fake
        self.api=T.Api(self.fake,'fixture/operating');self.run=44;self.attempt=1;self.job=55
        self.actor=4;self.action='initialize';self.extra_jobs=[];self.writes=[];self.flags={}
        self.server=f.history.scratch/'initializer-server.git'
        L.git(f.history.scratch,'init','--bare',str(self.server));self.fake.operating=self.server
        original=self.fake.request
        def request(method,path,body):
            if path=='/repos/shk95/configs':return self.fake.response({'id':1,'full_name':T.PUBLIC,'private':False,'default_branch':'master'})
            if path.startswith('/repos/shk95/configs/actions/runs/'+str(self.run)):
                if '/jobs?' in path:
                    rows=[{'id':self.job,'name':I.JOB,'run_id':self.run,'head_sha':self.fake.source,'status':'in_progress'}]+self.extra_jobs
                    return self.fake.response({'total_count':len(rows),'jobs':rows})
                return self.fake.response({'id':self.run,'run_attempt':self.attempt,'head_sha':self.fake.source,
                    'head_branch':'master','event':'workflow_dispatch','workflow_id':6,'repository':{'id':1},
                    'actor':{'id':self.actor},'triggering_actor':{'id':self.actor},'status':'in_progress'})
            for identifier,name in ((6,I.WORKFLOW),(2,'.github/workflows/release-control-writer.yml')):
                if path in {'/repos/shk95/configs/actions/workflows/'+str(identifier),
                            '/repos/shk95/configs/actions/workflows/'+name.rsplit('/',1)[1]}:
                    return self.fake.response({'id':identifier,'path':name,'state':'active'})
            if method=='GET':return original(method,path,body)
            self.writes.append((method,path,body))
            if self.flags.get('no-effect'):raise T.Unknown('fixture-lost-write')
            if method=='PUT':
                self.assertEqual(path,'/repos/fixture/operating/contents/'+H.SEED_PATH)
                data=base64.b64decode(body['content']);blob=L.git(self.server,'hash-object','-w','--stdin',data=data).decode().strip()
                tree=L.git(self.server,'mktree',data=('100644 blob '+blob+'\t'+H.SEED_PATH+'\n').encode()).decode().strip()
                command=['git','-C',str(self.server),'commit-tree',tree]
                env=dict(f.history.base,GIT_AUTHOR_NAME='Fixture',GIT_AUTHOR_EMAIL='fixture@example.invalid',
                    GIT_COMMITTER_NAME='Fixture',GIT_COMMITTER_EMAIL='fixture@example.invalid')
                head=subprocess.check_output(command,input=body['message'].encode(),env=env).decode().strip()
                L.git(self.server,'update-ref','refs/heads/main',head)
                if self.flags.get('lose-seed'):raise T.Unknown('fixture-lost-seed')
                return self.fake.response({'commit':{'sha':head}},201)
            if path.endswith('/git/commits'):
                env=dict(f.history.base)
                for kind,key in (('AUTHOR','author'),('COMMITTER','committer')):
                    for suffix,field in (('NAME','name'),('EMAIL','email'),('DATE','date')):env['GIT_'+kind+'_'+suffix]=body[key][field]
                head=subprocess.check_output(['git','-C',str(self.server),'commit-tree',body['tree'],'-p',body['parents'][0]],
                    input=body['message'].encode(),env=env).decode().strip()
                if self.flags.get('lose-object'):raise T.Unknown('fixture-lost-object')
                return self.fake.response({'sha':head},201)
            if path.endswith('/git/refs'):
                self.assertEqual(body['ref'],'refs/heads/operations')
                L.git(self.server,'update-ref',body['ref'],body['sha'],'0'*40)
                if self.flags.get('lose-ref'):raise T.Unknown('fixture-lost-ref')
                return self.fake.response({'ref':body['ref'],'object':{'type':'commit','sha':body['sha']}},201)
            return original(method,path,body)
        self.request_patch=patch.object(self.fake,'request',request);self.request_patch.start();self.addCleanup(self.request_patch.stop)
        self.raw=I.attempt_document(bundle,self.approved,config,desired,self.run)
        self.env={'CONFIGS_RELEASE_INITIAL_ATTEMPT':self.raw.decode()}
        self.history=self.new_history()

    def new_history(self):
        runtime={'run':self.run,'attempt':self.attempt,'actor':self.actor,'repository':1}
        entry=I.InitializerEntry(self.api,self.bundle,self.source,runtime,self.action)
        history=I.InitialHistory(entry,self.env);self.addCleanup(history.close)
        original=history.run
        def local(args,env,capture=False):
            if 'CONFIGS_ACQUIRE_TOKEN' not in env:return original(args,env,capture)
            self.assertNotIn('CONFIGS_RELEASE_INITIAL_ATTEMPT',env);self.assertNotIn('CONFIGS_RELEASE_TOKEN',env)
            local_args=[str(self.server) if arg=='https://x-access-token@github.com/fixture/operating.git' else arg for arg in args]
            result=subprocess.run([history.git]+history.options+['-c','protocol.file.allow=always']+local_args,
                env=dict(history.base,GIT_ALLOW_PROTOCOL='file'),capture_output=True,timeout=30)
            T.need(result.returncode==0,'fixture-private-git-refused');return result.stdout if capture else b''
        p=patch.object(history,'run',local);p.start();self.addCleanup(p.stop)
        return history

    def test_private_pure_construction_does_not_issue_or_publish(self):
        self.assertEqual(I.attempt_document(self.bundle,self.approved,self.config,self.desired,44),self.raw)
        self.assertFalse(self.writes);self.assertIs(type(self.history.entry),I.InitializerEntry)
        self.assertNotIsInstance(self.history.entry,T.Entry)
        value=T.document(self.raw);self.assertEqual(value['desired']['authenticated'],False)
        self.assertEqual(value['authorization']['attempt'],1)

    def test_exact_finite_attempt_and_lost_seed_ref_acknowledgements(self):
        self.flags.update({'lose-seed':True,'lose-ref':True})
        self.assertEqual(self.history.initialize('fixture-token'),'initialized')
        self.assertEqual(len([x for x in self.writes if x[0]=='PUT']),1)
        self.assertEqual(len([x for x in self.writes if x[1].endswith('/git/refs')]),1)
        self.assertEqual(self.history.observe('fixture-token'),'initialized')
        before=len(self.writes)
        with self.assertRaises(T.Refusal):self.history.initialize('fixture-token')
        self.assertEqual(len(self.writes),before)

    def test_missing_changed_or_body_certificate_refuses(self):
        for env in ({},{'certificate':self.raw.decode()},{'CONFIGS_RELEASE_INITIAL_ATTEMPT':self.raw.decode()+'\n'}):
            with self.subTest(env=tuple(env)),self.assertRaises(T.Refusal):I.InitialHistory(self.history.entry,env)
        self.env['CONFIGS_RELEASE_INITIAL_ATTEMPT']=T.canonical(dict(T.document(self.raw),construction={})).decode()
        with self.assertRaises(T.Refusal):self.history.initialize('fixture-token')
        self.assertFalse(self.writes)

    def test_later_run_rerun_and_changed_role_refuse_publishing(self):
        for key,value in (('run',45),('attempt',2),('actor',3),('job',99)):
            old=getattr(self,key);setattr(self,key,value)
            with self.subTest(key=key),self.assertRaises(T.Refusal):
                if key=='job':self.history.initialize('fixture-token')
                else:self.new_history()
            setattr(self,key,old)
        self.assertFalse(self.writes)

    def test_missing_prior_run_metadata_cannot_authorize_new_publication(self):
        self.run=45
        self.fake.fail[('GET','/repos/shk95/configs/actions/runs/44')]=T.Refusal('deleted-old-run')
        with self.assertRaises(T.Refusal):self.new_history()
        self.action='observe';other=self.new_history()
        self.assertEqual(other.observe('fixture-token'),'absent')
        with self.assertRaises(T.Refusal):other.initialize('fixture-token')
        self.assertFalse(self.writes)

    def test_incomplete_original_seed_is_pending_and_never_resumed(self):
        self.history.invoked=True
        self.history.create_seed(self.history.proposal,self.history.digest,self.bundle,self.approved,self.config,'fixture-token')
        self.action='observe';self.run=45;other=self.new_history()
        self.assertEqual(other.observe('fixture-token'),'pending');before=len(self.writes)
        self.action='initialize';self.run=44;again=self.new_history()
        with self.assertRaises(T.Refusal):again.initialize('fixture-token')
        with self.assertRaises(T.Refusal):again.publish_initial(again.proposal,again.digest,self.bundle,self.approved,self.config,'fixture-token')
        self.assertEqual(len(self.writes),before)

    def test_original_complete_child_is_observed_without_old_run_or_writes(self):
        self.history.initialize('fixture-token');before=len(self.writes)
        self.run=45;self.action='observe';other=self.new_history()
        self.assertEqual(other.observe('fixture-token'),'initialized');self.assertEqual(len(self.writes),before)
        head=L.git(self.server,'rev-parse','refs/heads/operations').decode().strip()
        seed=L.git(self.server,'rev-parse','refs/heads/main').decode().strip()
        records=other.disabled_records(self.bundle,self.approved,self.config)
        records[H.SEED_PATH]=other.packet['construction']['seed'].encode()
        self.assertEqual(H.planned_initial(records,seed,other._initial_date())['head'],head)

    def test_unknown_seed_and_object_acknowledgement_fence_invocation(self):
        self.flags['no-effect']=True
        with self.assertRaises(T.Refusal):self.history.initialize('fixture-token')
        before=len(self.writes)
        with self.assertRaises(T.Refusal):self.history.initialize('fixture-token')
        self.assertEqual(len(self.writes),before)
        self.flags.clear();other=self.new_history();self.flags['lose-object']=True
        with self.assertRaises(T.Unknown):other.initialize('fixture-token')
        before=len(self.writes)
        with self.assertRaises(T.Refusal):other.publish_initial(other.proposal,other.digest,self.bundle,self.approved,self.config,'fixture-token')
        self.assertEqual(len(self.writes),before)
        self.assertFalse(any(p.endswith('/git/refs') for _,p,_ in self.writes))

    def test_actual_source_job_and_default_move_refuse_before_effect(self):
        for kind in ('source','job','default'):
            other=self.new_history()
            if kind=='source':self.fake.source='b'*40
            elif kind=='job':self.extra_jobs=[{'id':99,'name':'foreign'}]
            else:self.fake.responses[('GET','/repos/fixture/operating')]=self.fake.response(
                {'id':22,'private':True,'full_name':'fixture/operating','default_branch':'foreign'})
            with self.subTest(kind=kind),self.assertRaises(T.Refusal):other.initialize('fixture-token')
            self.fake.source=self.source;self.extra_jobs=[]
            self.fake.responses[('GET','/repos/fixture/operating')]=self.fake.response(
                {'id':22,'private':True,'full_name':'fixture/operating','default_branch':'main'})
        self.assertFalse(self.writes)

    def test_foreign_refs_and_seed_refuse_observation_and_publication(self):
        subprocess.run(['git','-c','protocol.file.allow=always','-C',str(self.server),
            'fetch',str(self.bundle),'HEAD:refs/heads/foreign'],
            env=dict(self.history.base,GIT_ALLOW_PROTOCOL='file'),capture_output=True,check=True)
        with self.assertRaises(T.Refusal):self.history.observe('fixture-token')
        with self.assertRaises(T.Refusal):self.history.initialize('fixture-token')
        self.assertFalse(self.writes)

    def test_original_prospective_replay_precedes_seed_write(self):
        with patch.object(self.history,'_replay_initial',side_effect=T.Refusal('invalid-original-history')):
            with self.assertRaises(T.Refusal):self.history.initialize('fixture-token')
        self.assertFalse(self.writes)

    def test_workflow_cli_and_legacy_transport_boundaries(self):
        raw=(ROOT.parents[1]/I.WORKFLOW).read_text()
        self.assertNotIn('schedule:',raw);self.assertIn('cancel-in-progress: false',raw)
        self.assertEqual(raw.count('    environment: release-control'),1)
        self.assertIn('fetch-depth: 0',raw);self.assertIn('persist-credentials: false',raw)
        result=subprocess.run([__import__('sys').executable,'-I','-S','-B',str(ROOT/'release-initialize.py'),
            'initialize','--action','initialize'],env=H.credential_free(__import__('os').environ),capture_output=True)
        self.assertEqual(result.returncode,1);self.assertEqual(result.stderr.splitlines(),[b'initializer: refused'])
        result=subprocess.run([__import__('sys').executable,'-I','-S','-B',str(ROOT/'release-initialize.py'),
            'initialize','--action','private-marker','--certificate','private-marker'],
            env=H.credential_free(__import__('os').environ),capture_output=True)
        self.assertEqual(result.returncode,1);self.assertEqual(result.stderr.splitlines(),[b'initializer: refused'])
        self.assertFalse(self.writes)
        channel=I.InitialHttps('fixture-token');channel.gate=self.history.entry
        with patch.object(self.api,'channel',channel),patch.object(channel,'request',side_effect=self.fake.request):
            self.assertTrue(channel.authorized_write('POST','/repos/fixture/operating/git/refs',{}))
            self.assertFalse(channel.authorized_write('POST','/repos/shk95/configs/git/refs',{}))
        self.action='observe';channel.gate=self.new_history().entry
        with self.assertRaises(T.Refusal):channel.authorized_write('POST','/repos/fixture/operating/git/refs',{})

if __name__=='__main__':unittest.main()
