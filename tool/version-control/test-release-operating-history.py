"""Fake private API and local disposable Git; no network or real credentials."""
# INV repository/private-history-acquisition-isolated
# INV repository/authenticated-release-transport
# INV repository/fixture-git-isolation
import importlib.util
import os
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parent

def load(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/file)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
H=load('history_acquisition','release-operating-history.py')
F=load('history_acquisition_fixtures','test-release-transport.py')

class HistoryProof(unittest.TestCase):
    # INV repository/private-history-acquisition-isolated
    # INV repository/authenticated-release-transport
    # INV repository/fixture-git-isolation
    def setUp(self):
        self.fixture=F.TransportProof();self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
        f=self.fixture
        self.api=H.T.Api(f.fake,'fixture/operating')
        self.fake=f.fake
        self.fake.responses[('GET','/repos/fixture/operating')]=self.fake.response(
            {'id':22,'private':True,'full_name':'fixture/operating'})
        self.entry=H.T.Entry(self.api,f.trusted,f.runtime)
        self.history=H.GitHistory(self.entry,22);self.addCleanup(self.history.close)
        self.head=f.fake.head;self.calls=[]
    def acquire(self,after_fetch=None):
        original=self.history.run
        def local(args,env,capture=False):
            if 'CONFIGS_ACQUIRE_TOKEN' not in env:return original(args,env,capture)
            self.calls.append((list(args),dict(env)))
            self.assertEqual(env['CONFIGS_ACQUIRE_TOKEN'],'fixture-token')
            self.assertEqual(env['GIT_ALLOW_PROTOCOL'],'https')
            self.assertEqual(env['GIT_TERMINAL_PROMPT'],'0')
            self.assertNotIn('GIT_CONFIG_COUNT',env);self.assertNotIn('HTTPS_PROXY',env)
            self.assertNotIn('GIT_TRACE',env)
            url='https://x-access-token@github.com/fixture/operating.git'
            self.assertIn(url,args)
            if args[0]=='ls-remote':return (self.head+'\trefs/heads/operations\n').encode()
            # Only this fixture substitutes its owned local file receiver. There is
            # no production protocol/URL/executable override.
            command=[self.history.git,'-c','protocol.file.allow=always','-C',str(self.history.repo),
                'fetch','--no-tags',str(self.fixture.fixture.operating),self.head+':refs/heads/operations']
            subprocess.run(command,env=dict(self.history.base,GIT_ALLOW_PROTOCOL='file'),check=True,
                           stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            if after_fetch:after_fetch()
            return b''
        with patch.object(self.history,'run',local):return self.history.acquire('fixture-token',self.head)
    def test_original_full_objects_are_returned_without_credential_files_or_checkout(self):
        repo=self.acquire()
        self.assertEqual(H.L.git(repo,'rev-parse','refs/heads/operations').strip(),self.head.encode())
        H.L.verify_graphs(repo,[self.head]);H.L.verify_append_only_snapshot(repo,self.head)
        f=self.fixture.fixture
        snapshot=H.B.Snapshot(self.entry,f.public,repo,F.F.encode(f.packages['3']),self.head,
            {'name':'Release controller','email':'release-controller@example.invalid','date':'2026-10-01T00:00:00Z'},self.fixture.requirements)
        self.addCleanup(snapshot.close)
        self.assertEqual(snapshot.state['candidate'],F.F.CANDIDATE)
        self.assertEqual(snapshot.plan(F.F.X)['head'],self.head)
        self.assertEqual(len(self.calls),2)
        self.assertFalse((repo/'index').exists())
        for path in self.history.scratch.rglob('*'):
            if path.is_file():self.assertNotIn(b'fixture-token',path.read_bytes())
        self.assertNotIn('CONFIGS_ACQUIRE_TOKEN',H.credential_free(self.calls[0][1]))
    def test_ambient_routing_config_trace_and_credentials_do_not_reach_git(self):
        with patch.dict(os.environ,{'GIT_CONFIG_COUNT':'1','GIT_CONFIG_KEY_0':'url.https://foreign.invalid/.insteadOf',
                'GIT_CONFIG_VALUE_0':'https://github.com/','HTTPS_PROXY':'https://foreign.invalid',
                'GIT_TRACE':'1','CONFIGS_RELEASE_TOKEN':'ambient-private'}):
            other=H.GitHistory(self.entry,22);self.addCleanup(other.close);self.history=other;self.acquire()
        for _,env in self.calls:
            self.assertNotIn('CONFIGS_RELEASE_TOKEN',env);self.assertNotIn('GIT_CONFIG_COUNT',env)
    def test_private_repository_id_visibility_and_name_must_match(self):
        for field,value in [('id',23),('private',False),('full_name','foreign/operating')]:
            obj={'id':22,'private':True,'full_name':'fixture/operating'};obj[field]=value
            self.fake.responses[('GET','/repos/fixture/operating')]=self.fake.response(obj)
            with self.subTest(field=field),self.assertRaises(H.T.Refusal):H.GitHistory(self.entry,22)
    def test_mixed_job_entry_refuses_before_credential_acquisition(self):
        self.fake.jobs_extra=[{'id':99,'name':'foreign'}]
        with self.assertRaises(H.T.Refusal):H.GitHistory(self.entry,22)

    def test_unauthenticated_entry_and_invalid_token_refuse(self):
        with self.assertRaises(H.T.Refusal):H.GitHistory(object(),22)
        inspector=H.T.Entry(self.api,self.fixture.trusted,dict(self.fixture.runtime,mode='inspect'))
        with self.assertRaises(H.T.Refusal):H.GitHistory(inspector,22)
        for token in ('','token\n','token with spaces','非ascii'):
            with self.subTest(token=token),self.assertRaises(H.T.Refusal):self.history.acquire(token,self.head)
    def test_moving_or_wrong_advertised_head_refuses_without_fetch(self):
        with patch.object(self.history,'run',return_value=b'') as run:
            with self.assertRaises(H.T.Refusal):self.history.acquire('fixture-token',self.head)
            self.assertEqual(run.call_count,1)
        path='/repos/fixture/operating/git/ref/heads/operations'
        self.fake.responses[('GET',path)]=self.fake.response(
            {'ref':'refs/heads/operations','object':{'type':'commit','sha':'b'*40}})
        with patch.object(self.history,'run') as run:
            with self.assertRaises(H.T.Refusal):self.history.acquire('fixture-token',self.head)
            run.assert_not_called()
    def test_askpass_answers_only_its_exact_private_password_prompt(self):
        helper=self.history.scratch/'fixture-askpass.py';helper.write_text(H.ASKPASS)
        url='https://x-access-token@github.com/fixture/operating.git'
        env=dict(self.history.base,CONFIGS_ACQUIRE_TOKEN='fixture-token',CONFIGS_ACQUIRE_URL=url)
        import sys
        for prompt,ok in [("Password for '"+url+"': ",True),("Username for '"+url+"': ",False),
                           ("Password for 'https://foreign.invalid': ",False)]:
            result=subprocess.run([sys.executable,'-I','-S','-B',str(helper),prompt],env=env,capture_output=True)
            self.assertEqual(result.returncode==0,ok)
            self.assertEqual(result.stdout,b'fixture-token\n' if ok else b'')
    def test_time_disk_and_output_bounds_refuse_before_returning_a_repo(self):
        import sys
        with patch.object(self.history,'git',sys.executable),patch.object(self.history,'options',[]),patch.object(H,'TIMEOUT',0),self.assertRaises(H.T.Refusal):
            self.history.run(['-I','-S','-B','-c','import time; time.sleep(10)'],self.history.base,capture=True)
        (self.history.scratch/'oversize').write_bytes(b'xx')
        with patch.object(H,'MAX_DISK',1),self.assertRaises(H.T.Refusal):self.history.size()
        with patch.object(H,'MAX_OUTPUT',1),self.assertRaises(H.T.Refusal):
            self.history.run(['--version'],self.history.base,capture=True)
    def test_disabled_initial_projection_uses_original_package_and_selects_no_baseline(self):
        f=self.fixture.fixture
        config=H.L.encode_index(dict(F.F.CONFIG,enabled='0'))
        records=self.history.disabled_records(f.public,F.F.encode(f.packages['3']),config)
        self.assertEqual(H.L.singletons(records['control/stop.tsv'],{'stop','revision','reason','operator'})['stop'],'1')
        index=H.L.singletons(records['current/index.tsv'],H.L.PROJECTION_FIELDS|{'index-kind','ledger-digest'})
        self.assertEqual(index['sequence'],'0');self.assertEqual(index['stage'],'empty')
        self.assertEqual(records['current/batches.tsv'],b'format\t1\n')
        self.assertFalse(any('baseline' in path or path.startswith('history/') for path in records))
        self.assertFalse(any(method!='GET' for method,_,_ in self.fake.calls))
        with self.assertRaises(H.T.Refusal):
            self.history.disabled_records(f.public,F.F.encode(f.packages['3']),F.F.encode(F.F.CONFIG))
    def test_actual_git_askpass_binding_is_native_and_refuses_foreign_paths(self):
        self.acquire()
        env=dict(self.history.base,GIT_ASKPASS=str(self.history.scratch/'askpass.sh'),
            CONFIGS_ACQUIRE_TOKEN='fixture-token',
            CONFIGS_ACQUIRE_URL='https://x-access-token@github.com/fixture/operating.git')
        command=[self.history.git]+self.history.options+['credential','fill']
        for path,ok in [('fixture/operating.git',True),('foreign/repository.git',False)]:
            request=('protocol=https\nhost=github.com\npath='+path+'\nusername=x-access-token\n\n').encode()
            result=subprocess.run(command,input=request,env=env,capture_output=True,timeout=10)
            self.assertEqual(result.returncode==0,ok)
            if ok:self.assertIn(b'password=fixture-token\n',result.stdout)
            else:self.assertNotIn(b'fixture-token',result.stdout+result.stderr)
    def test_partial_override_or_corrupt_original_graph_refuses(self):
        def poison(kind):
            repo=self.history.repo
            if kind=='shallow':(repo/'shallow').write_text(self.head+'\n')
            elif kind=='alternate':(repo/'objects/info/alternates').write_text('')
            elif kind=='promisor':(repo/'objects/pack/fixture.promisor').write_text('')
            elif kind=='graft':
                (repo/'info').mkdir(exist_ok=True);(repo/'info/grafts').write_text(self.head+'\n')
            elif kind=='replace':
                subprocess.run([self.history.git,'-C',str(repo),'update-ref','refs/replace/'+self.head,self.head],
                    env=self.history.base,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            else:
                import zlib
                target=repo/'objects'/self.head[:2]/self.head[2:]
                target.parent.mkdir(exist_ok=True);target.unlink(missing_ok=True);target.write_bytes(zlib.compress(b'commit 1\0x'))
        for kind in ('shallow','alternate','promisor','graft','replace','corrupt'):
            self.history=H.GitHistory(self.entry,22);self.addCleanup(self.history.close)
            with self.subTest(kind=kind),self.assertRaises((H.T.Refusal,ValueError)):
                self.acquire(lambda:poison(kind))
    def test_read_only_preflight_accepts_exact_five_and_six_file_history(self):
        import hashlib,json,shutil,sys
        preflight=load('history_preflight','release-transport-preflight.py')
        public=self.fixture.fixture.public
        for name in preflight.FILES:
            target=public/name;target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT.parents[1]/name,target)
        manifest=public/'tool/version-control/release-transport.manifest.tsv'
        for names in (preflight.FILES,tuple(n for n in preflight.FILES if not n.endswith('/release-operating-history.py'))):
            manifest.write_text('format\t1\n'+''.join('file\t'+name+'\t'+hashlib.sha256((public/name).read_bytes()).hexdigest()+'\n' for name in sorted(names)))
            if len(names)==5:(public/'tool/version-control/release-operating-history.py').unlink()
            F.F.run_git(public,'add','.')
            F.F.run_git(public,'commit','-qm','chore(repository): fixture transport inventory')
            source=F.F.run_git(public,'rev-parse','HEAD')
            template=json.loads((ROOT/'release-transport-template.json').read_text())
            template.update({'transport-source':source,'transport-manifest':H.T.digest(manifest.read_bytes())})
            inputs=self.history.scratch/'source-template.json';inputs.write_text(json.dumps(template))
            result=subprocess.run([sys.executable,'-I','-S','-B',str(public/'tool/version-control/release-transport-preflight.py'),
                'preflight','--source',source,'--template',str(inputs)],env=self.history.base,capture_output=True,timeout=30)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertFalse(json.loads(result.stdout)['enabled'])
            self.assertFalse(json.loads(result.stdout)['production_certification'])

    def test_remote_head_movement_after_transfer_refuses(self):
        with self.assertRaises(H.T.Refusal):self.acquire(lambda:setattr(self.fake,'head','b'*40))
        self.fake.head=self.head
        with self.assertRaises(H.T.Refusal):self.acquire(lambda:setattr(self.fake,'attempt',2))

if __name__=='__main__':unittest.main()
