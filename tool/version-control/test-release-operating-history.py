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
                target.parent.mkdir(exist_ok=True)
                # Windows refuses unlink of Git's read-only loose objects. This
                # receiver is an owned fixture copy; detach it before corruption.
                if target.exists():target.chmod(0o600)
                target.unlink(missing_ok=True);target.write_bytes(zlib.compress(b'commit 1\0x'))
        for kind in ('shallow','alternate','promisor','graft','replace','corrupt'):
            self.history=H.GitHistory(self.entry,22);self.addCleanup(self.history.close)
            with self.subTest(kind=kind),self.assertRaises((H.T.Refusal,ValueError)):
                self.acquire(lambda:poison(kind))
    def test_read_only_preflight_accepts_exact_five_six_seven_and_eight_file_history(self):
        import hashlib,json,shutil,sys
        preflight=load('history_preflight','release-transport-preflight.py')
        public=self.fixture.fixture.public
        for name in preflight.FILES:
            target=public/name;target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT.parents[1]/name,target)
        manifest=public/'tool/version-control/release-transport.manifest.tsv'
        for names in (preflight.FILES,preflight.LEGACY_SEVEN,preflight.LEGACY_SIX,preflight.LEGACY_FIVE):
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

    def proposal_inputs(self):
        import hashlib,shutil
        f=self.fixture.fixture
        for name in H.TRANSPORT_FILES:
            target=f.public/name;target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT.parents[1]/name,target)
        manifest=f.public/'tool/version-control/release-transport.manifest.tsv'
        manifest.write_text('format\t1\n'+''.join('file\t'+name+'\t'+hashlib.sha256((f.public/name).read_bytes()).hexdigest()+'\n' for name in H.TRANSPORT_FILES))
        F.F.run_git(f.public,'add','.')
        F.F.run_git(f.public,'commit','-qm','chore(repository): fixture initial proposal source')
        source=F.F.run_git(f.public,'rev-parse','HEAD')
        self.fake.source=source;self.fixture.trusted['source']=source;self.fixture.runtime['source']=source
        entry=H.T.Entry(self.api,self.fixture.trusted,self.fixture.runtime)
        self.history=H.GitHistory(entry,22);self.addCleanup(self.history.close)
        self.fake.responses[('GET','/repos/fixture/operating')]=self.fake.response(
            {'id':22,'private':True,'full_name':'fixture/operating','default_branch':'main'})
        return (f.public,F.F.encode(dict(f.packages['3'],master=source)),H.L.encode_index(dict(F.F.CONFIG,enabled='0')),'fixture-token')

    def desired_inputs(self):
        import hashlib,json
        bundle,approved,config,_=self.proposal_inputs()
        roles=json.loads((bundle/H.ROLE_PATH).read_bytes())
        roles['roles']['initializer']['actors']=[4]
        roles['roles']['writer']['actors']=[3]
        (bundle/H.ROLE_PATH).write_bytes(H.T.canonical(roles))
        writer=bundle/'.github/workflows/release-control-writer.yml'
        writer.parent.mkdir(parents=True,exist_ok=True)
        writer.write_text('name: Fixture disabled writer\non: workflow_dispatch\npermissions: {}\njobs:\n  writer-preflight:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo disabled\n')
        manifest=bundle/'tool/version-control/release-transport.manifest.tsv'
        manifest.write_text('format\t1\n'+''.join('file\t'+name+'\t'+hashlib.sha256((bundle/name).read_bytes()).hexdigest()+'\n' for name in H.TRANSPORT_FILES))
        F.F.run_git(bundle,'add','.')
        F.F.run_git(bundle,'commit','-qm','chore(repository): fixture distinct source roles')
        source=F.F.run_git(bundle,'rev-parse','HEAD')
        self.fake.source=source
        approved=F.F.encode(dict(H.L.approved(approved),master=source))
        desired={'operating-repository':'fixture/operating','operating-repository-id':22,
            'public-repository-id':1,'default-branch':'main','initializer-workflow':6,
            'initializer-actor':4,'writer-workflow':2}
        return bundle,approved,config,desired

    def test_desired_projection_has_no_entry_or_credentials_and_distinct_stop_actor(self):
        inputs=self.desired_inputs()
        calls=len(self.fake.calls)
        with patch.object(H.T,'Entry',side_effect=AssertionError('no runtime entry')):
            proposal,records=H.desired_initial(*inputs)
        value=H.T.document(proposal)
        self.assertEqual(len(self.fake.calls),calls)
        self.assertFalse(value['authenticated']);self.assertFalse(value['enabled'])
        self.assertIsNone(value['semantic-baseline'])
        self.assertIsNone(value['roles']['initializer']['blob'])
        self.assertEqual(value['roles']['writer']['actors'],[3])
        self.assertEqual(H.L.singletons(records['control/stop.tsv'],{'stop','revision','reason','operator'})['operator'],'4')
        self.assertEqual(H.desired_initial(*inputs),(proposal,records))
        # Format-2 desired assertions cannot enter the legacy authenticated writer.
        with self.assertRaises(H.T.Refusal):self.history._initial_context(proposal,H.T.digest(proposal))

    def test_desired_roles_and_configuration_cannot_widen_each_other(self):
        bundle,approved,config,desired=self.desired_inputs()
        for change in ({'initializer-actor':3},{'writer-workflow':7},{'operating-repository':H.T.PUBLIC},
                       {'default-branch':'operations'},{'public-repository-id':True}):
            with self.subTest(change=change),self.assertRaises(H.T.Refusal):
                H.desired_initial(bundle,approved,config,dict(desired,**change))
        fields=H.L.singletons(config,{'enabled','public-repository','repository','operating-repository',
            'operating-ref','workflow','actors','checks','protocol'})
        for change in ({'actors':'3,4'},{'enabled':'1'},{'operating-repository':'foreign/private'}):
            with self.subTest(change=change),self.assertRaises(H.T.Refusal):
                H.desired_initial(bundle,approved,H.L.encode_index(dict(fields,**change)),desired)

    def test_desired_original_source_and_complete_closure_refuse_poisoning(self):
        inputs=self.desired_inputs();bundle,approved,config,desired=inputs
        path=bundle/H.ROLE_PATH
        path.write_bytes(path.read_bytes()+b' ')
        # Working bytes do not replace original committed bytes.
        H.desired_initial(*inputs)
        bad=dict(H.L.approved(approved),manifest='0'*64)
        with self.assertRaises(ValueError):H.desired_initial(bundle,F.F.encode(bad),config,desired)
        with patch.object(H,'TRANSPORT_FILES',H.TRANSPORT_FILES+('tool/version-control/missing.py',)),self.assertRaises(H.T.Refusal):
            H.desired_initial(*inputs)

    def test_role_observation_binds_current_numeric_identity_and_original_workflow(self):
        bundle,approved,_,_=self.desired_inputs();source=H.L.approved(approved)['master']
        path='.github/workflows/release-control-writer.yml'
        value={'id':2,'path':path,'state':'active'}
        for suffix in ('2','release-control-writer.yml'):
            self.fake.responses[('GET','/repos/shk95/configs/actions/workflows/'+suffix)]=self.fake.response(value)
        actual=H.verify_source_role(self.api,bundle,source,'writer',2)
        self.assertEqual(actual['blob'],F.F.run_git(bundle,'rev-parse',source+':'+path))
        self.assertEqual(actual['job'],'writer-preflight');self.assertIsNone(actual['environment'])
        for change in ({'id':7},{'state':'disabled_manually'},{'path':'.github/workflows/foreign.yml'}):
            self.fake.responses[('GET','/repos/shk95/configs/actions/workflows/release-control-writer.yml')]=self.fake.response(dict(value,**change))
            with self.subTest(change=change),self.assertRaises(H.T.Refusal):H.verify_source_role(self.api,bundle,source,'writer',2)

    def test_missing_original_initializer_is_never_authenticated_by_a_declaration(self):
        bundle,approved,_,_=self.desired_inputs();source=H.L.approved(approved)['master']
        value={'id':6,'path':'.github/workflows/release-control-initialize.yml','state':'active'}
        for suffix in ('6','release-control-initialize.yml'):
            self.fake.responses[('GET','/repos/shk95/configs/actions/workflows/'+suffix)]=self.fake.response(value)
        with self.assertRaises(H.T.Refusal):H.verify_source_role(self.api,bundle,source,'initializer',6)
        with self.assertRaises(H.T.Refusal):H.verify_source_role(self.api,bundle,source,'foreign',6)

    def test_role_declaration_refuses_job_environment_and_actor_poisoning(self):
        import hashlib
        bundle,approved,_,_=self.desired_inputs()
        original=H.T.document((bundle/H.ROLE_PATH).read_bytes())
        for change in ({'job':'writer'},{'environment':'release-control'},{'actors':[True]},
                       {'actors':[3,3]},{'actors':['private']},{'path':'.github/workflows/foreign.yml'}):
            value=H.T.document(H.T.canonical(original))
            value['roles']['writer'].update(change)
            (bundle/H.ROLE_PATH).write_bytes(H.T.canonical(value))
            manifest=bundle/'tool/version-control/release-transport.manifest.tsv'
            manifest.write_text('format\t1\n'+''.join('file\t'+name+'\t'+hashlib.sha256((bundle/name).read_bytes()).hexdigest()+'\n' for name in H.TRANSPORT_FILES))
            F.F.run_git(bundle,'add','.')
            F.F.run_git(bundle,'commit','-qm','chore(repository): fixture invalid source role')
            source=F.F.run_git(bundle,'rev-parse','HEAD')
            with self.subTest(change=change),self.assertRaises(H.T.Refusal):H.source_roles(bundle,source)

    def test_role_data_requires_a_regular_original_blob(self):
        bundle,_,_,_=self.desired_inputs()
        F.F.run_git(bundle,'update-index','--chmod=+x',H.ROLE_PATH)
        F.F.run_git(bundle,'commit','-qm','chore(repository): fixture unsafe role mode')
        source=F.F.run_git(bundle,'rev-parse','HEAD')
        with self.assertRaises(ValueError):H.source_roles(bundle,source)

    def test_role_source_movement_and_source_time_poisoning_refuse(self):
        bundle,approved,_,_=self.desired_inputs();source=H.L.approved(approved)['master']
        self.fake.source='b'*40
        with self.assertRaises(H.T.Refusal):H.verify_source_role(self.api,bundle,source,'writer',2)
        original=H.L.git
        for raw in (b'committer person <email> private +0000\n\nmessage',
                    b'committer person <email> 999999999999 +0000\n\nmessage',
                    b'committer person <email> 1 +0000\ncommitter other <email> 2 +0000\n\nmessage'):
            def poison(repo,*args,**kw):
                return raw if args==('cat-file','commit',source) else original(repo,*args,**kw)
            with self.subTest(raw=raw),patch.object(H.L,'git',poison),self.assertRaises(H.T.Refusal):H.source_date(bundle,source)

    def test_source_date_rebuilds_the_exact_git_child_across_instances(self):
        inputs=self.desired_inputs();proposal,records=H.desired_initial(*inputs)
        value=H.T.document(proposal);date=value['date']
        records=dict(records);records[H.SEED_PATH]=('format\t1\nproposal\t'+H.T.digest(proposal)+'\n').encode()
        _,seed,_=self.history._local_initial(records,None,date)
        expected=H.planned_initial(records,seed,date)
        tree,head,_=self.history._local_initial(records,seed,date)
        self.assertEqual(expected,{'tree':tree,'head':head,'date':date})
        again,again_records=H.desired_initial(*inputs)
        again_records[H.SEED_PATH]=records[H.SEED_PATH]
        self.assertEqual(H.planned_initial(again_records,seed,H.T.document(again)['date']),expected)
        self.fake.attempt=2
        self.assertEqual(H.planned_initial(records,seed,date),expected)
        for bad in ('2026-02-30T00:00:00Z','1969-12-31T23:59:59Z','private-time',None):
            with self.subTest(date=bad),self.assertRaises(H.T.Refusal):H.planned_initial(records,seed,bad)

    def test_initial_proposal_binds_original_source_records_and_private_review_digest(self):
        import json
        inputs=self.proposal_inputs();calls=[]
        original=self.history.run
        def absent(args,env,capture=False):
            if 'CONFIGS_ACQUIRE_TOKEN' not in env:return original(args,env,capture)
            self.assertEqual(args,['ls-remote','--refs','https://x-access-token@github.com/fixture/operating.git'])
            calls.append(args);return b''
        with patch.object(self.history,'run',absent):
            proposal=self.history.initial_proposal(*inputs)
            seed=self.history.review_initial(proposal,H.T.digest(proposal),*inputs)
        value=json.loads(proposal)
        self.assertEqual(seed,('format\t1\nproposal\t'+H.T.digest(proposal)+'\n').encode())
        self.assertEqual(value['default-branch'],'main');self.assertFalse(value['enabled'])
        self.assertIsNone(value['semantic-baseline']);self.assertEqual(len(value['records']),5)
        self.assertEqual(value['source'],self.fixture.trusted['source'])
        self.assertEqual(len(calls),4)
        self.assertFalse(any(method!='GET' for method,_,_ in self.fake.calls))
        self.assertNotIn(b'fixture-token',proposal)

    def test_initial_ref_absence_never_follows_a_404_or_foreign_ref(self):
        inputs=self.proposal_inputs()
        for output in (b'a'*40+b'\trefs/tags/foreign\n',b'unknown',b'\n'):
            with patch.object(self.history,'run',return_value=output),self.assertRaises(H.T.Refusal):
                self.history.initial_proposal(*inputs)
        with patch.object(self.history,'run',side_effect=H.T.Refusal('private-git-refused')),self.assertRaises(H.T.Refusal):
            self.history.initial_proposal(*inputs)
        self.fake.responses[('GET','/repos/fixture/operating')]=self.fake.response({},404)
        with patch.object(self.history,'run') as run,self.assertRaises(H.T.Refusal):
            self.history.initial_proposal(*inputs)
        run.assert_not_called()

    def test_initial_moving_refs_default_branch_and_runtime_refuse(self):
        inputs=self.proposal_inputs()
        with patch.object(self.history,'run',side_effect=[b'',b'a'*40+b'\trefs/heads/main\n']),self.assertRaises(H.T.Refusal):
            self.history.initial_proposal(*inputs)
        def moving(args,env,capture=False):
            self.fake.responses[('GET','/repos/fixture/operating')]=self.fake.response(
                {'id':22,'private':True,'full_name':'fixture/operating','default_branch':'other'})
            return b''
        with patch.object(self.history,'run',moving),self.assertRaises(H.T.Refusal):
            self.history.initial_proposal(*inputs)
        self.fake.attempt=2
        with patch.object(self.history,'run') as run,self.assertRaises(H.T.Refusal):self.history.initial_proposal(*inputs)
        run.assert_not_called()

    def test_review_recomputes_config_actor_source_and_exact_bytes(self):
        import json
        inputs=self.proposal_inputs()
        with patch.object(self.history,'run',return_value=b''):
            proposal=self.history.initial_proposal(*inputs)
            with self.assertRaises(H.T.Refusal):self.history.review_initial(proposal,'0'*64,*inputs)
            value=json.loads(proposal);value['actor']=99
            changed=H.T.canonical(value)
            for altered in (changed,proposal+b'\n'):
                with self.assertRaises(H.T.Refusal):self.history.review_initial(altered,H.T.digest(altered),*inputs)
            changed_config=inputs[2].replace(b'checks\t',b'checks\tforeign-')
            with self.assertRaises(H.T.Refusal):
                self.history.review_initial(proposal,H.T.digest(proposal),inputs[0],inputs[1],changed_config,inputs[3])
            for key,value in (('workflow','99'),('actors','3,99')):
                fields=dict(F.F.CONFIG,enabled='0');fields[key]=value
                with self.subTest(key=key),self.assertRaises(H.T.Refusal):
                    self.history.initial_proposal(inputs[0],inputs[1],H.L.encode_index(fields),inputs[3])

    def test_incomplete_transport_and_unsupported_default_refuse_before_git_transport(self):
        inputs=self.proposal_inputs()
        for branch in ('operations','feature/other','main..other',''):
            self.fake.responses[('GET','/repos/fixture/operating')]=self.fake.response(
                {'id':22,'private':True,'full_name':'fixture/operating','default_branch':branch})
            with patch.object(self.history,'run') as run,self.assertRaises(H.T.Refusal):self.history.initial_proposal(*inputs)
            run.assert_not_called()
        self.fake.responses[('GET','/repos/fixture/operating')]=self.fake.response(
            {'id':22,'private':True,'full_name':'fixture/operating','default_branch':'main'})
        public=inputs[0];manifest=public/'tool/version-control/release-transport.manifest.tsv'
        manifest.write_bytes(b'\n'.join(manifest.read_bytes().splitlines()[:-1])+b'\n')
        F.F.run_git(public,'add','.');F.F.run_git(public,'commit','-qm','chore(repository): fixture incomplete closure')
        source=F.F.run_git(public,'rev-parse','HEAD')
        self.fake.source=source;self.fixture.trusted['source']=source;self.fixture.runtime['source']=source
        self.history.entry=H.T.Entry(self.api,self.fixture.trusted,self.fixture.runtime)
        with patch.object(self.history,'run') as run,self.assertRaises(H.T.Refusal):self.history.initial_proposal(*inputs)
        run.assert_not_called()

    def test_native_full_ref_advertisement_distinguishes_empty_from_any_ref(self):
        repo=self.history.scratch/'empty-advertisement.git'
        self.history.run(['init','--bare','--template='+str(self.history.empty),str(repo)],self.history.base)
        env=dict(self.history.base,GIT_ALLOW_PROTOCOL='file')
        command=[self.history.git]+self.history.options+['-c','protocol.file.allow=always']
        result=subprocess.run(command+['ls-remote','--refs',str(repo)],env=env,capture_output=True,timeout=30)
        self.assertEqual(result.returncode,0);self.assertEqual(result.stdout,b'')
        subprocess.run(command+['-C',str(repo),'fetch','--no-tags',str(self.fixture.fixture.operating),
            self.head+':refs/tags/foreign'],env=env,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=30)
        result=subprocess.run(command+['ls-remote','--refs',str(repo)],env=env,capture_output=True,timeout=30)
        self.assertEqual(result.returncode,0)
        self.assertEqual(result.stdout,(self.head+'\trefs/tags/foreign\n').encode())

    def provisioning_receiver(self):
        import base64
        inputs=self.proposal_inputs()
        server=self.history.scratch/'provisioning-server.git'
        self.history.run(['init','--bare','--template='+str(self.history.empty),str(server)],self.history.base)
        self.fake.operating=server
        original_run=self.history.run;original_request=self.fake.request
        self.provision_flags={};self.provision_calls=[]
        def run(args,env,capture=False):
            if 'CONFIGS_ACQUIRE_TOKEN' not in env:return original_run(args,env,capture)
            local=[str(server) if arg=='https://x-access-token@github.com/fixture/operating.git' else arg for arg in args]
            result=subprocess.run([self.history.git]+self.history.options+['-c','protocol.file.allow=always']+local,
                env=dict(self.history.base,GIT_ALLOW_PROTOCOL='file'),capture_output=True,timeout=30)
            H.T.need(result.returncode==0,'fixture-private-git-refused')
            return result.stdout if capture else b''
        def request(method,path,body):
            if method=='GET':
                result=original_request(method,path,body)
                if path=='/repos/shk95/configs/actions/runs/4/attempts/1':
                    value=H.T.document(result[2]);value['run_started_at']='2026-10-02T00:00:00Z'
                    return self.fake.response(value)
                return result
            self.provision_calls.append((method,path,body))
            if self.provision_flags.get('no-effect'):raise H.T.Unknown('fixture-lost-write')
            if method=='PUT':
                self.assertEqual(path,'/repos/fixture/operating/contents/'+H.SEED_PATH)
                self.assertEqual(set(body),{'message','branch','content'});self.assertEqual(body['branch'],'main')
                data=base64.b64decode(body['content'])
                blob=H.L.git(server,'hash-object','-w','--stdin',data=data).decode().strip()
                tree=H.L.git(server,'mktree',data=('100644 blob '+blob+'\t'+H.SEED_PATH+'\n').encode()).decode().strip()
                env=dict(self.history.base,GIT_AUTHOR_NAME='Fixture',GIT_AUTHOR_EMAIL='fixture@example.invalid',
                    GIT_COMMITTER_NAME='Fixture',GIT_COMMITTER_EMAIL='fixture@example.invalid')
                result=subprocess.run([self.history.git,'-C',str(server),'commit-tree',tree],
                    input=body['message'].encode(),env=env,capture_output=True,check=True)
                head=result.stdout.decode().strip()
                H.L.git(server,'update-ref','refs/heads/main',head)
                result=self.fake.response({'commit':{'sha':head}},201)
                if self.provision_flags.get('lose-seed'):raise H.T.Unknown('fixture-lost-seed')
                return result
            if path=='/repos/fixture/operating/git/commits':
                env=dict(self.history.base)
                for kind,field in (('AUTHOR','author'),('COMMITTER','committer')):
                    for suffix,key in (('NAME','name'),('EMAIL','email'),('DATE','date')):
                        env['GIT_'+kind+'_'+suffix]=body[field][key]
                result=subprocess.run([self.history.git,'-C',str(server),'commit-tree',body['tree'],'-p',body['parents'][0]],
                    input=body['message'].encode(),env=env,capture_output=True,check=True)
                return self.fake.response({'sha':result.stdout.decode().strip()},201)
            if path=='/repos/fixture/operating/git/refs':
                self.assertEqual(body['ref'],'refs/heads/operations')
                H.L.git(server,'update-ref','refs/heads/operations',body['sha'],'0'*40)
                self.fake.head=body['sha']
                if self.provision_flags.get('lose-ref'):raise H.T.Unknown('fixture-lost-ref')
                return self.fake.response({'ref':body['ref'],'object':{'type':'commit','sha':body['sha']}},201)
            return original_request(method,path,body)
        self.run_patch=patch.object(self.history,'run',run);self.run_patch.start();self.addCleanup(self.run_patch.stop)
        self.request_patch=patch.object(self.fake,'request',request);self.request_patch.start();self.addCleanup(self.request_patch.stop)
        proposal=self.history.initial_proposal(*inputs)
        return proposal,H.T.digest(proposal),inputs,server

    def test_initial_seed_and_operations_are_original_verified_disabled_and_replayed(self):
        proposal,digest,inputs,server=self.provisioning_receiver()
        seed=self.history.create_seed(proposal,digest,*inputs)
        self.assertIsNone(seed['head'])
        result=self.history.publish_initial(proposal,digest,*inputs)
        self.assertNotEqual(result['head'],result['seed'])
        self.assertFalse(self.history.initial_pending)
        self.assertEqual(H.L.git(server,'rev-list','--count',result['head']).strip(),b'2')
        self.assertEqual(len([x for x in self.provision_calls if x[0]=='PUT']),1)
        before=len(self.provision_calls)
        self.history.observe_initial(proposal,digest,*inputs,complete=True,expected_head=result['head'])
        self.assertEqual(len(self.provision_calls),before)
        with self.assertRaises(H.T.Refusal):self.history.publish_initial(proposal,digest,*inputs)
        self.assertEqual(len(self.provision_calls),before)

    def test_lost_seed_and_ref_acknowledgements_reconcile_without_repeated_writes(self):
        proposal,digest,inputs,server=self.provisioning_receiver()
        self.provision_flags.update({'lose-seed':True,'lose-ref':True})
        self.history.create_seed(proposal,digest,*inputs)
        self.history.publish_initial(proposal,digest,*inputs)
        self.assertEqual(len([x for x in self.provision_calls if x[0]=='PUT']),1)
        self.assertEqual(len([x for x in self.provision_calls if x[1].endswith('/git/refs')]),1)

    def test_unknown_unobserved_seed_fences_and_never_retries(self):
        proposal,digest,inputs,server=self.provisioning_receiver()
        self.provision_flags['no-effect']=True
        with self.assertRaises(H.T.Refusal):self.history.create_seed(proposal,digest,*inputs)
        self.assertTrue(self.history.initial_pending);self.assertEqual(len(self.provision_calls),1)
        with self.assertRaises(H.T.Refusal):self.history.create_seed(proposal,digest,*inputs)
        with self.assertRaises(H.T.Refusal):self.history.publish_initial(proposal,digest,*inputs)
        self.assertEqual(len(self.provision_calls),1)

    def test_foreign_seed_objects_refs_and_changed_review_refuse_without_followup_writes(self):
        proposal,digest,inputs,server=self.provisioning_receiver()
        seed=self.history.create_seed(proposal,digest,*inputs)['seed']
        before=len(self.provision_calls)
        H.L.git(server,'update-ref','refs/tags/foreign',seed)
        with self.assertRaises(H.T.Refusal):self.history.observe_initial(proposal,digest,*inputs)
        H.L.git(server,'update-ref','-d','refs/tags/foreign')
        with self.assertRaises(H.T.Refusal):self.history.observe_initial(proposal+b'\n',digest,*inputs)
        env=dict(self.history.base,GIT_AUTHOR_NAME='Fixture',GIT_AUTHOR_EMAIL='fixture@example.invalid',
            GIT_COMMITTER_NAME='Fixture',GIT_COMMITTER_EMAIL='fixture@example.invalid')
        tree=H.L.git(server,'rev-parse',seed+'^{tree}').decode().strip()
        child=subprocess.run([self.history.git,'-C',str(server),'commit-tree',tree,'-p',seed],
            input=b'foreign\n',env=env,capture_output=True,check=True).stdout.decode().strip()
        H.L.git(server,'update-ref','refs/heads/main',child)
        with self.assertRaises(H.T.Refusal):self.history.observe_initial(proposal,digest,*inputs)
        self.assertEqual(len(self.provision_calls),before)

    def test_invalid_original_local_replay_prevents_all_operations_writes(self):
        proposal,digest,inputs,server=self.provisioning_receiver()
        self.history.create_seed(proposal,digest,*inputs)
        before=len(self.provision_calls)
        original=self.history.disabled_records
        def invalid(*args):
            records=original(*args);records['current/index.tsv']=b'format\t1\n';return records
        # Preserve proposal regeneration; corrupt only the subsequent local child.
        calls=[0]
        def late(*args):
            calls[0]+=1
            return original(*args) if calls[0]==1 else invalid(*args)
        with patch.object(self.history,'disabled_records',late),self.assertRaises(ValueError):
            self.history.publish_initial(proposal,digest,*inputs)
        self.assertEqual(len(self.provision_calls),before)

    def test_complete_tree_rejects_hidden_empty_subtree(self):
        proposal,digest,inputs,server=self.provisioning_receiver()
        seed=self.history.create_seed(proposal,digest,*inputs)['seed']
        empty=H.L.git(server,'mktree',data=b'').decode().strip()
        original=H.L.git(server,'ls-tree',seed)
        tree=H.L.git(server,'mktree',data=b'040000 tree '+empty.encode()+b'\tforeign\n'+original).decode().strip()
        env=dict(self.history.base,GIT_AUTHOR_NAME='Fixture',GIT_AUTHOR_EMAIL='fixture@example.invalid',
            GIT_COMMITTER_NAME='Fixture',GIT_COMMITTER_EMAIL='fixture@example.invalid')
        root=subprocess.run([self.history.git,'-C',str(server),'commit-tree',tree],input=b'foreign root\n',
            env=env,capture_output=True,check=True).stdout.decode().strip()
        H.L.git(server,'update-ref','refs/heads/main',root)
        H.L.git(self.history.repo,'update-ref','-d','refs/heads/initial-seed')
        before=len(self.provision_calls)
        with self.assertRaisesRegex(H.T.Refusal,'foreign-initial-seed'):
            self.history.observe_initial(proposal,digest,*inputs)
        self.assertEqual(len(self.provision_calls),before)

    def test_complete_observation_requires_preserved_exact_head(self):
        proposal,digest,inputs,server=self.provisioning_receiver()
        self.history.create_seed(proposal,digest,*inputs)
        result=self.history.publish_initial(proposal,digest,*inputs)
        before=len(self.provision_calls)
        with self.assertRaises(H.T.Refusal):self.history.observe_initial(proposal,digest,*inputs,complete=True)
        with self.assertRaisesRegex(H.T.Refusal,'conflicting-initial-head'):
            self.history.observe_initial(proposal,digest,*inputs,complete=True,expected_head='a'*40)
        self.assertEqual(len(self.provision_calls),before)

    def test_unknown_object_write_fences_ref_creation_and_retry(self):
        proposal,digest,inputs,server=self.provisioning_receiver()
        self.history.create_seed(proposal,digest,*inputs)
        self.provision_flags['no-effect']=True
        with self.assertRaises(H.T.Unknown):self.history.publish_initial(proposal,digest,*inputs)
        count=len(self.provision_calls)
        self.assertTrue(self.history.initial_pending)
        self.assertFalse(any(x[1].endswith('/git/refs') for x in self.provision_calls))
        with self.assertRaises(H.T.Refusal):self.history.publish_initial(proposal,digest,*inputs)
        self.assertEqual(len(self.provision_calls),count)

    def test_invalid_original_replay_prevents_seed_write_too(self):
        proposal,digest,inputs,server=self.provisioning_receiver()
        original=self.history.disabled_records;calls=[0]
        def late(*args):
            records=original(*args);calls[0]+=1
            if calls[0]==2:records['current/index.tsv']=b'format\t1\n'
            return records
        with patch.object(self.history,'disabled_records',late),self.assertRaises(ValueError):
            self.history.create_seed(proposal,digest,*inputs)
        self.assertEqual(self.provision_calls,[])
        self.assertFalse(getattr(self.history,'initial_pending',False))

if __name__=='__main__':unittest.main()
