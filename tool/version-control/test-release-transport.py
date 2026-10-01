"""Actual disposable Git plus finite authenticated-response fixtures. No HTTP."""
# INV repository/authenticated-release-transport
# INV repository/fixture-git-isolation
import base64
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
from urllib.parse import parse_qs, urlsplit

ROOT=Path(__file__).resolve().parent

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result

B=load('transport_bridge',ROOT/'release-transport-retained.py');T=B.T
F=load('controller_fixtures',ROOT/'test-release-control.py')

class Fake:
    """One private disposable repository; no caller Git or external transport."""
    def __init__(self,public,operating,source):
        self.public,self.operating,self.source=public,operating,source
        self.head=F.run_git(operating,'rev-parse','HEAD') if (operating/'.git').exists() else None
        self.calls=[];self.pulls=[];self.fail={};self.mutate={};self.responses={};self.jobs_extra=[];self.attempt=1
        self.master=F.H;self.dev=F.D;self.stop=False

    def response(self,value,status=200,headers=None):return status,headers or {},T.canonical(value)

    def request(self,method,path,body):
        self.calls.append((method,path,copy.deepcopy(body)))
        key=(method,path)
        if key in self.responses:return self.responses[key]
        if key in self.fail:raise self.fail[key]
        if key in self.mutate:self.mutate.pop(key)()
        repo='fixture/operating' if path.startswith('/repos/fixture/operating/') else T.PUBLIC
        suffix=path.split('/repos/'+repo,1)[1];parts=urlsplit(suffix);route=parts.path
        if route.startswith('/actions/runs/'):
            run=int(route.split('/')[3])
            attempt=int(route.split('/')[5]) if '/attempts/' in route else self.attempt
            head=self.source if run==4 else F.D
            if route.endswith('/jobs'):
                rows=[{'id':5 if run==4 else 9,'name':'writer' if run==4 else 'Required checks',
                       'run_id':run,'head_sha':head,'status':'in_progress' if run==4 and not getattr(self,'terminal_jobs',False) else 'completed',
                       'conclusion':None if run==4 else 'success','html_url':'https://github.com/shk95/configs/actions/runs/%s/job/9'%run}]+self.jobs_extra
                return self.response({'total_count':len(rows),'jobs':rows})
            if route.endswith('/cancel'):
                self.terminal=True;self.terminal_jobs=getattr(self,'confirm_cancel',False)
                return self.response({},202)
            status='completed' if getattr(self,'terminal',False) or run!=4 else 'in_progress'
            return self.response({'id':run,'run_attempt':attempt,'head_sha':head,'head_branch':'master','event':'workflow_dispatch',
                       'workflow_id':2,'repository':{'id':1},'actor':{'id':3},'triggering_actor':{'id':3},
                       'status':status,'conclusion':'success' if status=='completed' else None})
        if route=='/actions/workflows/2':return self.response({'id':2,'path':'.github/workflows/release-control-writer.yml'})
        if route=='/pulls' and method=='GET':return self.response(self.pulls)
        if route=='/pulls' and method=='POST':
            p={'id':17,'number':17,'state':'open','head':{'ref':body['head'],'sha':self.dev,'repo':{'full_name':T.PUBLIC}},
               'base':{'ref':body['base'],'sha':self.master,'repo':{'full_name':T.PUBLIC}}}
            self.pulls.append(p)
            if getattr(self,'lose_pr',False):raise T.Unknown('unknown-write')
            return self.response(p,201)
        if route.startswith('/branches/'):
            branch=route.split('/')[2]
            return self.response({'required_status_checks':{'strict':branch=='dev','contexts':['Required checks'],'checks':[{'context':'Required checks','app_id':15368}]},
                     'enforce_admins':{'enabled':True},'required_conversation_resolution':{'enabled':True},
                     'allow_force_pushes':{'enabled':False},'allow_deletions':{'enabled':False},
                     'required_pull_request_reviews':{'require_code_owner_reviews':False,'required_approving_review_count':0}})
        if route.endswith('/check-runs'):
            return self.response({'total_count':1,'check_runs':[{'id':10,'name':'Required checks','app':{'id':15368},'head_sha':F.D,
                'status':'completed','conclusion':'success','details_url':'https://github.com/shk95/configs/actions/runs/8/job/9'}]})
        root=self.operating if repo=='fixture/operating' else self.public
        if route=='/git/ref/heads/operations':return self.response({'ref':'refs/heads/operations','object':{'type':'commit','sha':self.head}})
        if route=='/git/ref/heads/master':return self.response({'ref':'refs/heads/master','object':{'type':'commit','sha':self.source}})
        if route=='/git/ref/heads/dev':return self.response({'ref':'refs/heads/dev','object':{'type':'commit','sha':self.dev}})
        if route.startswith('/git/commits/'):
            oid=route.rsplit('/',1)[1]
            raw=F.run_git(root,'cat-file','-p',oid).splitlines()
            return self.response({'sha':oid,'tree':{'sha':raw[0][5:]},'parents':[{'sha':v[7:]} for v in raw if v.startswith('parent ')]})
        if route.startswith('/git/trees/'):
            oid=route.rsplit('/',1)[1]
            raw=F.run_git(root,'ls-tree','-r','-t',oid).splitlines();rows=[]
            for line in raw:
                metadata,path=line.split('\t');mode,kind,blob=metadata.split();rows.append({'path':path,'mode':mode,'type':kind,'sha':blob})
            return self.response({'sha':oid,'truncated':False,'tree':rows})
        if route.startswith('/git/blobs/'):
            oid=route.rsplit('/',1)[1];raw=subprocess.run(['git','-C',str(root),'cat-file','blob',oid],capture_output=True,check=True).stdout
            return self.response({'sha':oid,'encoding':'base64','content':base64.b64encode(raw).decode()})
        if route=='/git/blobs' and method=='POST':
            raw=base64.b64decode(body['content']);oid=F.run_git(root,'hash-object','-w','--stdin',data=raw)
            return self.response({'sha':oid},201)
        if route=='/git/trees' and method=='POST':
            index=root.parent/'transport.index'
            env=__import__('os').environ.copy();env['GIT_INDEX_FILE']=str(index)
            subprocess.run(['git','-C',str(root),'read-tree',body['base_tree']],env=env,check=True,capture_output=True)
            for row in body['tree']:
                subprocess.run(['git','-C',str(root),'update-index','--add','--cacheinfo',row['mode'],row['sha'],row['path']],env=env,check=True,capture_output=True)
            oid=subprocess.check_output(['git','-C',str(root),'write-tree'],env=env).decode().strip()
            return self.response({'sha':oid},201)
        if route=='/git/commits' and method=='POST':
            oid=F.run_git(root,'commit-tree',body['tree'],'-p',body['parents'][0],data=body['message'].encode())
            return self.response({'sha':oid},201)
        if route=='/git/refs/heads/operations' and method=='PATCH':
            if body['force'] is not False:return self.response({},422)
            parent=F.run_git(root,'rev-parse',body['sha']+'^')
            if parent!=self.head:return self.response({},422)
            self.head=body['sha'];F.run_git(root,'update-ref','refs/heads/operations',self.head)
            if getattr(self,'lose_record',False):raise T.Unknown('unknown-write')
            return self.response({'ref':'refs/heads/operations','object':{'sha':self.head,'type':'commit'}})
        raise AssertionError((method,path,body))

class TransportProof(unittest.TestCase):
    def setUp(self):
        self.fixture=F.GlobalHistoryProof();self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
        f=self.fixture
        supplied=F.transcript('preview');supplied['source'].append(F.transcript('approve')['source'][0])
        f.transcript_file.write_bytes(F.canonical(supplied))
        f.add_batch('3',F.X,False)
        events=F.base_events()[2:]
        for e in events:f.append(e)
        p={'repository':T.PUBLIC,'head':'dev','base':'master','dev':F.D,'master':F.H,'body-operation':F.Y}
        f.append(F.effect('pr',p))
        config=F.CONFIG;state=F.engine.reduce(f.events,config,supplied)
        projection=F.engine.index(state,F.digest(F.encode(f.events[-1])))
        f.final=dict(row.split('\t') for row in projection.decode().splitlines()[1:])
        f.ledger[-1]['projection']=F.digest(projection);f.save()
        self.fake=Fake(f.public,f.operating,f.packages['3']['master']);self.api=T.Api(self.fake,'fixture/operating')
        self.runtime={'repository':T.PUBLIC,'ref':'refs/heads/master','event':'workflow_dispatch','run':4,'attempt':1,'job':5,'actor':3,
                   'source':self.fake.source,'environment':'fixture-controller','mode':'start','candidate':F.engine.candidate_digest(F.CANDIDATE)}
        self.trusted={'source':self.fake.source,'workflow':2,'workflow-path':'.github/workflows/release-control-writer.yml','repository-id':1,
                      'actors':[3],'environment':'fixture-controller','job-name':'writer'}
        self.entry=T.Entry(self.api,self.trusted,self.runtime)
        workflow_blob=F.run_git(f.public,'rev-parse','HEAD:tool/version-control/release-control-package/main.py')
        tool_blob=F.run_git(f.public,'rev-parse','HEAD:tool/version-control/release-preview')
        self.fake.responses[('GET','/repos/shk95/configs/git/commits/'+F.D)]=self.fake.response({'sha':F.D,'tree':{'sha':F.T},'parents':[{'sha':F.H}]})
        self.fake.responses[('GET','/repos/shk95/configs/git/trees/'+F.T+'?recursive=1')]=self.fake.response({'sha':F.T,'truncated':False,'tree':[
           {'path':'.github/workflows/release-control-writer.yml','mode':'100644','type':'blob','sha':workflow_blob},
           {'path':'tool/version-control/release-preview','mode':'100755','type':'blob','sha':tool_blob}]})
        self.requirements=[{'id':'gate','name':'Required checks','app':15368,'workflow':2,'job':9,'tool':'fixture-tool',
                            'source':F.D,'attempt':1,'run':8,'workflow-path':'.github/workflows/release-control-writer.yml',
             'workflow-blob':workflow_blob,'tool-path':'tool/version-control/release-preview','tool-blob':tool_blob}]

    def snapshot(self):
        f=self.fixture
        s=B.Snapshot(self.entry,f.public,f.operating,F.encode(f.packages['3']),self.fake.head,
                     {'name':'Release controller','email':'release-controller@example.invalid','date':'2026-10-01T00:00:00Z'},self.requirements)
        self.addCleanup(s.close);return s

    def executor(self):
        s=self.snapshot();j=T.Journal(self.api,s,self.fake.head);return T.Executor(self.entry,j,s),s.plan(F.X)

    def test_authenticated_entry_ref_event_actor_attempt_job(self):
        self.entry.request({k:self.runtime[k] for k in ('mode','actor','run','attempt','ref','candidate')})
        for key,bad in [('actor',30),('ref','refs/heads/dev'),('source',F.H),('environment','foreign')]:
            value=dict(self.runtime);value[key]=bad
            with self.subTest(key=key),self.assertRaises(T.Refusal):T.Entry(self.api,self.trusted,value)
        self.fake.attempt=2
        with self.assertRaises(T.Refusal):T.Entry(self.api,self.trusted,self.runtime)

    def test_request_body_cannot_authenticate_itself(self):
        request={k:self.runtime[k] for k in ('mode','actor','run','attempt','ref','candidate')}
        request['candidate']='0'*64
        with self.assertRaises(T.Refusal):self.entry.request(request)

    def test_authenticated_check_protection_and_wrong_receipt(self):
        self.entry.protection('dev');self.entry.protection('master')
        receipts=self.entry.evidence(F.D,F.T,self.requirements);self.assertEqual(receipts[0]['check'],10)
        self.fake.responses[('GET','/repos/shk95/configs/commits/'+F.D+'/check-runs?per_page=100&page=1')]=self.fake.response({'total_count':2,'check_runs':[]})
        with self.assertRaises(T.Refusal):self.entry.evidence(F.D,F.T,self.requirements)

    def test_exact_retained_snapshot_and_read_only_projection(self):
        before=F.run_git(self.fixture.public,'show-ref');s=self.snapshot()
        self.assertEqual(s.state['candidate'],F.CANDIDATE);self.assertEqual(s.plan(F.X)['head'],self.fake.head)
        self.assertEqual(before,F.run_git(self.fixture.public,'show-ref'))
        self.assertFalse(any(method!='GET' for method,_,_ in self.fake.calls))

    def test_complete_lookup_durable_intent_post_observation(self):
        executor,plan=self.executor();self.assertEqual(executor.perform(plan),'applied')
        writes=[(method,path) for method,path,_ in self.fake.calls if method!='GET']
        first_pr=writes.index(('POST','/repos/shk95/configs/pulls'))
        self.assertIn(('PATCH','/repos/fixture/operating/git/refs/heads/operations'),writes[:first_pr])
        self.assertEqual(len(self.fake.pulls),1)
        self.assertEqual(executor.snapshot.state['operations'][F.X]['state'],'observed')
        with self.assertRaises(T.Refusal):executor.perform(executor.snapshot.plan(F.X))

    def test_lost_post_response_joins_exact_pr(self):
        self.fake.lose_pr=True
        executor,plan=self.executor();self.assertEqual(executor.perform(plan),'applied')
        self.assertEqual(sum(m=='POST' and p.endswith('/pulls') for m,p,_ in self.fake.calls),1)

    def test_lost_record_response_reconciles_exact_commit(self):
        self.fake.lose_record=True
        executor,plan=self.executor();self.assertEqual(executor.perform(plan),'applied')
        self.assertFalse(executor.journal.pending)

    def test_unknown_post_fences_next_effect_and_recovery_observes_only(self):
        self.fake.fail[('POST','/repos/shk95/configs/pulls')]=T.Unknown('timeout')
        executor,plan=self.executor()
        with self.assertRaises(T.Unknown):executor.perform(plan)
        self.assertTrue(executor.unknown)
        with self.assertRaises(T.Refusal):executor.perform(plan)
        self.assertEqual(executor.recover(plan),'absent')
        self.assertFalse(executor.unknown)
        self.assertEqual(sum(m=='POST' and p.endswith('/pulls') for m,p,_ in self.fake.calls),1)

    def test_missing_or_incomplete_pr_pages_refuse_before_write(self):
        self.fake.responses[('GET','/repos/shk95/configs/pulls?state=all&per_page=100&page=1')]=self.fake.response([{'id':i+1} for i in range(100)])
        executor,plan=self.executor()
        with self.assertRaises(T.Refusal):executor.perform(plan)
        self.assertFalse(any(method!='GET' for method,_,_ in self.fake.calls))

    def test_foreign_page_redirect_duplicate_and_bound_refuse(self):
        path='/repos/shk95/configs/pulls?per_page=100&page=1'
        for response in [self.fake.response([],headers={'link':'<https://foreign.invalid>; rel="next"'}),
                         self.fake.response([],headers={'location':'https://foreign.invalid'}),
                         self.fake.response([{'id':1},{'id':1}])]:
            self.fake.responses[('GET',path)]=response
            with self.assertRaises(T.Refusal):self.api.pages('/pulls')

    def test_conflicting_pr_or_wrong_pair_never_posts(self):
        self.fake.pulls=[{'id':17,'number':17,'state':'open','head':{'ref':'dev','sha':F.H,'repo':{'full_name':T.PUBLIC}},
                         'base':{'ref':'master','sha':F.H,'repo':{'full_name':T.PUBLIC}}}]
        executor,plan=self.executor()
        with self.assertRaises(T.Refusal):executor.perform(plan)
        self.assertFalse(any(method!='GET' for method,_,_ in self.fake.calls))

    def test_cancel_single_owned_job_only_and_ack_not_termination(self):
        owner={'run':4,'attempt':1,'job':5,'workflow':2,'source':self.fake.source}
        self.fake.jobs_extra=[{'id':6,'head_sha':self.fake.source,'status':'in_progress'}]
        with self.assertRaises(T.Refusal):self.entry.cancel(owner)
        self.assertFalse(any(p.endswith('/cancel') for _,p,_ in self.fake.calls))
        self.fake.jobs_extra=[]
        # Fake returns completed run but a still-running writer: acknowledgement
        # remains unknown and never permits takeover.
        self.assertEqual(self.entry.cancel(owner),'unknown')

    def test_confirmed_single_writer_termination_and_attempt_race(self):
        owner={'run':4,'attempt':1,'job':5,'workflow':2,'source':self.fake.source}
        self.fake.confirm_cancel=True
        self.assertEqual(self.entry.cancel(owner),'terminal')
        self.fake.attempt=2
        with self.assertRaises(T.Refusal):self.entry.owner_terminal(owner)

    def test_tool_blob_mismatch_and_failed_check_refuse(self):
        wrong=copy.deepcopy(self.requirements);wrong[0]['tool-blob']=F.D
        with self.assertRaises(T.Refusal):self.entry.evidence(F.D,F.T,wrong)
        path='/repos/shk95/configs/commits/'+F.D+'/check-runs?per_page=100&page=1'
        self.fake.responses[('GET',path)]=self.fake.response({'total_count':1,'check_runs':[{'id':10,'name':'Required checks','app':{'id':15368},'head_sha':F.D,'status':'completed','conclusion':'failure'}]})
        with self.assertRaises(T.Refusal):self.entry.evidence(F.D,F.T,self.requirements)

    def test_writer_conflict_and_immutable_history_refusal(self):
        s=self.snapshot();j=T.Journal(self.api,s,self.fake.head)
        with self.assertRaises(T.Refusal):j.publish({'history/000000000001.tsv':b'changed'})
        self.fake.head=F.H
        with self.assertRaises(T.Refusal):j.publish({'current/index.tsv':b'changed'})
        self.assertFalse(any(method!='GET' for method,_,_ in self.fake.calls))

    def test_authenticated_stop_and_resume_keep_whole_history(self):
        executor,plan=self.executor();executor.perform(plan)
        self.runtime['mode']='stop';self.entry=T.Entry(self.api,self.trusted,self.runtime)
        s=self.snapshot();j=T.Journal(self.api,s,self.fake.head)
        request={k:self.runtime[k] for k in ('mode','actor','run','attempt','ref','candidate')}
        j.publish(s.transition(request))
        self.assertTrue(s.state['stopped'])
        self.runtime['mode']='resume';self.entry=T.Entry(self.api,self.trusted,self.runtime)
        restored=self.snapshot();journal=T.Journal(self.api,restored,self.fake.head)
        request['mode']='resume';journal.publish(restored.transition(request))
        self.assertFalse(restored.state['stopped'])
        self.assertEqual(restored.state['stage'],'candidate')
        # Resume clears old approval/evidence; it never reuses them for a merge.
        self.assertIsNone(restored.state['approval'])
        self.assertEqual(restored.state['evidence'],[])

    def test_republished_observation_replays_complete_remote_snapshot(self):
        executor,plan=self.executor();executor.perform(plan)
        restored=self.snapshot()
        self.assertEqual(restored.state['operations'][F.X]['state'],'observed')
        with self.assertRaises(T.Refusal):restored.plan(F.X)

    def test_immutable_history_tampering_refuses(self):
        f=self.fixture
        original=f.operating/'history/000000000001.tsv'
        original.write_bytes(original.read_bytes()+b'bad\tfield\n')
        self.fake.head=f.commit(f.operating)
        with self.assertRaises((T.Refusal,ValueError)):self.snapshot()

    def test_merge_current_checks_and_actual_post_merge_tree(self):
        executor,_=self.executor();payload={'repository':T.PUBLIC,'number':17,'dev':F.D,'master':F.H,'tree':F.T}
        self.fake.responses[('GET','/repos/shk95/configs/git/ref/heads/master')]=self.fake.response({'ref':'refs/heads/master','object':{'type':'commit','sha':F.H}})
        pr={'id':17,'number':17,'state':'open','draft':False,'auto_merge':None,'mergeable':True,'mergeable_state':'clean',
            'head':{'ref':'dev','sha':F.D,'repo':{'full_name':T.PUBLIC}},'base':{'ref':'master','sha':F.H,'repo':{'full_name':T.PUBLIC}}}
        self.fake.responses[('GET','/repos/shk95/configs/pulls/17')]=self.fake.response(pr)
        method,path,body,statuses=executor.request('merge',payload)
        self.assertEqual((method,body),('PUT',{'sha':F.D,'merge_method':'merge'}))
        merged=dict(pr,merged=True,merge_commit_sha=F.T)
        self.fake.responses[('GET','/repos/shk95/configs/pulls/17')]=self.fake.response(merged)
        self.fake.responses[('GET','/repos/shk95/configs/git/commits/'+F.T)]=self.fake.response({'sha':F.T,'tree':{'sha':F.T},'parents':[{'sha':F.H},{'sha':F.D}]})
        self.assertEqual(executor.reconcile('merge',payload),('applied',F.T))
        wrong={'sha':F.T,'tree':{'sha':F.D},'parents':[{'sha':F.H},{'sha':F.D}]}
        self.fake.responses[('GET','/repos/shk95/configs/git/commits/'+F.T)]=self.fake.response(wrong)
        with self.assertRaises(T.Refusal):executor.reconcile('merge',payload)

    def test_immutable_tag_conflict_and_unknown_object_never_retry(self):
        executor,_=self.executor();payload={'repository':T.PUBLIC,'tag':'unixlike-v1.0.1','object':F.T}
        path='/repos/shk95/configs/git/matching-refs/tags/unixlike-v1.0.1'
        self.fake.responses[('GET',path)]=self.fake.response([])
        self.assertEqual(executor.reconcile('tag-ref',payload),('absent',None))
        self.fake.responses[('GET',path)]=self.fake.response([{'ref':'refs/tags/unixlike-v1.0.1','object':{'type':'tag','sha':F.T}}])
        self.assertEqual(executor.reconcile('tag-ref',payload),('applied',F.T))
        self.fake.responses[('GET',path)]=self.fake.response([{'ref':'refs/tags/unixlike-v1.0.1','object':{'type':'tag','sha':F.D}}])
        with self.assertRaises(T.Refusal):executor.reconcile('tag-ref',payload)

    def test_closed_prior_pr_cannot_be_mistaken_for_absence(self):
        self.fake.pulls=[{'id':17,'number':17,'state':'closed','head':{'ref':'dev'},'base':{'ref':'master'}}]
        executor,plan=self.executor()
        with self.assertRaises(T.Refusal):executor.perform(plan)
        self.assertFalse(any(method!='GET' for method,_,_ in self.fake.calls))

    def test_disabled_entry_no_https_or_ambient_credentials(self):
        client=T.Https('fixture-token')
        with self.assertRaises(T.Refusal):client.request('POST','/repos/shk95/configs/pulls',{})
        self.assertFalse(hasattr(client,'token'))
        self.assertNotIn('TOKEN',B.L.runtime_environment({'TOKEN':'secret'}))

    def test_foreign_cancel_owner_refuses_before_endpoint(self):
        owner={'run':7,'attempt':1,'job':5,'workflow':2,'source':self.fake.source}
        count=len(self.fake.calls)
        with self.assertRaisesRegex(T.Refusal,'foreign-cancel-owner'):self.entry.cancel(owner)
        self.assertEqual(len(self.fake.calls),count)

    def test_approval_from_wrong_actual_source_refuses_merge(self):
        executor,_=self.executor()
        key=('GET','/repos/shk95/configs/actions/runs/4/attempts/1')
        code,headers,raw=self.fake.request(*key,None)
        value=T.document(raw);value['head_sha']=F.H
        self.fake.responses[key]=self.fake.response(value)
        with self.assertRaisesRegex(T.Refusal,'untrusted-approval-source'):
            executor.snapshot.verify_merge({'dev':F.D,'master':F.H,'tree':F.T},self.entry)

    def test_actual_lock_only_refresh_commit_and_contamination_refusal(self):
        executor,_=self.executor();f=self.fixture
        lock=f.public/'unixlike/flake.lock';lock.parent.mkdir(parents=True,exist_ok=True)
        lock.write_bytes(b'before');base=f.commit(f.public)
        lock.write_bytes(b'after');head=f.commit(f.public);self.fake.dev=base
        p={'branch':'feature/unixlike-refresh-'+F.X,'base':base,'parent':base,'head':head,
           'tree':F.run_git(f.public,'rev-parse',head+'^{tree}'),'lock':T.digest(b'after'),
           'before-lock':T.digest(b'before'),'previous':'-'}
        method,path,body,statuses=executor.request('refresh-branch',p)
        self.assertEqual((method,path,body['sha']),('POST','/git/refs',head))
        # A correctly parented commit with another changed leaf cannot qualify.
        extra=f.public/'foreign.txt';extra.write_text('contamination')
        bad=f.commit(f.public)
        p.update(parent=head,head=bad,tree=F.run_git(f.public,'rev-parse',bad+'^{tree}'),**{'before-lock':T.digest(b'after')})
        with self.assertRaisesRegex(T.Refusal,'contaminated-refresh'):executor.request('refresh-branch',p)

    def test_current_config_revocation_refuses_live_projection(self):
        f=self.fixture
        config=f.operating/'config/operating.tsv'
        config.write_bytes(config.read_bytes().replace(b'enabled\t1',b'enabled\t0'))
        self.fake.head=f.commit(f.operating)
        with self.assertRaises(T.Refusal):self.snapshot()
        self.assertFalse(any(method!='GET' for method,_,_ in self.fake.calls))

    def test_operator_preflight_is_source_bound_and_always_disabled(self):
        import shutil
        f=self.fixture
        preflight=load('transport_preflight',ROOT/'release-transport-preflight.py')
        for name in preflight.FILES+('tool/version-control/release-transport.manifest.tsv',):
            target=f.public/name;target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT.parents[1]/name,target)
        source=f.commit(f.public)
        template=f.operating.parent/'manual.json'
        shutil.copyfile(ROOT/'release-transport-template.json',template)
        command=[sys.executable,'-I','-S','-B',str(f.public/'tool/version-control/release-transport-preflight.py'),
                 'preflight','--source',source,'--template',str(template)]
        result=subprocess.run(command,capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)
        value=json.loads(result.stdout);self.assertFalse(value['enabled']);self.assertFalse(value['production_certification'])
        self.assertIn('operating-repository',value['unresolved'])
        result=subprocess.run(command[:-3]+['not-a-sha','--template',str(template)],capture_output=True)
        self.assertNotEqual(result.returncode,0)

    def test_wakeup_has_no_owner_or_approval_and_unknown_ack_fences(self):
        runtime=dict(self.runtime,mode='wake');entry=T.Entry(self.api,self.trusted,runtime)
        path='/repos/shk95/configs/actions/workflows/2/dispatches'
        self.fake.responses[('POST',path)]=self.fake.response({'workflow_run_id':4})
        result=entry.wake(runtime['candidate'])
        self.assertFalse(result['ownership']);self.assertFalse(result['approval'])
        self.fake.responses[('POST',path)]=self.fake.response({})
        with self.assertRaises(T.Unknown):entry.wake(runtime['candidate'])
        with self.assertRaises(T.Refusal):entry.wake('0'*64)

    def test_fresh_attempt_change_before_effect_refuses(self):
        executor,plan=self.executor()
        original=executor.journal.publish
        def advance(changes):
            result=original(changes);self.fake.attempt=2;return result
        executor.journal.publish=advance
        with self.assertRaises(T.Refusal):executor.perform(plan)
        self.assertFalse(any(method=='POST' and path.endswith('/pulls') for method,path,_ in self.fake.calls))

    def test_tag_absence_redirect_is_not_authenticated_absence(self):
        executor,_=self.executor()
        payload={'object':F.T}
        path='/repos/shk95/configs/git/tags/'+F.T
        self.fake.responses[('GET',path)]=self.fake.response({},404,{'Location':'https://foreign.invalid'})
        with self.assertRaises(T.Refusal):executor.reconcile('tag-object',payload)

    def test_notification_receipt_never_claims_inbox_delivery(self):
        path='/repos/shk95/configs/actions/runs/4/attempts/1'
        value={'id':4,'run_attempt':1,'workflow_id':2,'head_sha':self.fake.source,'status':'completed','conclusion':'failure'}
        self.fake.responses[('GET',path)]=self.fake.response(value)
        self.assertEqual(self.entry.notification(4,1)['delivery'],'unverified')

if __name__=='__main__':unittest.main()
