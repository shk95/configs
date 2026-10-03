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
                       'workflow_id':2,'repository':{'id':1},'head_repository':{'id':1},'actor':{'id':3},'triggering_actor':{'id':3},
                       'status':status,'conclusion':'success' if status=='completed' else None})
        if route=='/actions/workflows/2':return self.response({'id':2,'path':'.github/workflows/release-control-writer.yml'})
        if route=='/pulls' and method=='GET':return self.response(self.pulls)
        if route=='/pulls' and method=='POST':
            p={'id':17,'number':17,'state':'open','head':{'ref':body['head'],'sha':self.dev,'repo':{'full_name':T.PUBLIC}},
               'base':{'ref':body['base'],'sha':self.master,'repo':{'full_name':T.PUBLIC}},'body':body['body']}
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

    def test_existing_pr_body_operation_is_independently_verified(self):
        self.fake.pulls=[{'id':17,'number':17,'state':'open','body':F.X,
             'head':{'ref':'dev','sha':F.D,'repo':{'full_name':T.PUBLIC}},
             'base':{'ref':'master','sha':F.H,'repo':{'full_name':T.PUBLIC}}}]
        executor,plan=self.executor()
        with self.assertRaisesRegex(T.Refusal,'wrong-pr-operation'):executor.perform(plan)
        self.assertFalse(any(method!='GET' for method,_,_ in self.fake.calls))

    def test_unrecognized_pagination_header_cannot_prove_absence(self):
        path='/repos/shk95/configs/pulls?state=all&per_page=100&page=1'
        self.fake.responses[('GET',path)]=self.fake.response([],200,{'link':"<https://foreign.invalid>; rel='next'"})
        with self.assertRaisesRegex(T.Refusal,'unknown-pagination-framing'):self.api.pages('/pulls',parameters={'state':'all'})

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

    def test_current_config_change_preserves_pinned_outstanding_context(self):
        f=self.fixture
        config=f.operating/'config/operating.tsv'
        config.write_bytes(config.read_bytes().replace(b'enabled\t1',b'enabled\t0').replace(b'actors\t3',b'actors\t99'))
        self.fake.head=f.commit(f.operating)
        restored=self.snapshot()
        self.assertEqual(restored.state['candidate'],F.CANDIDATE)
        self.assertEqual(restored.pinned_config['actors'],'3')
        self.assertEqual(restored.pinned_config['enabled'],'1')
        self.assertFalse(any(method!='GET' for method,_,_ in self.fake.calls))

    def test_later_master_owner_does_not_replace_old_semantic_context(self):
        f=self.fixture;old=f.packages['3']['master']
        (f.public/'later-master.txt').write_text('new loader; same retained semantics')
        later=f.commit(f.public);f.packages['3']=dict(f.packages['3'],master=later)
        self.fake.source=later;self.trusted['source']=later;self.runtime['source']=later
        self.entry=T.Entry(self.api,self.trusted,self.runtime)
        restored=self.snapshot()
        self.assertEqual(restored.owner_source,old)
        self.assertEqual(restored.owner_target(restored.state['owner'])['source'],later)
        plan=restored.plan(F.X)
        self.assertEqual(restored.authorize(plan,self.entry)[0],'pr')

    def test_owner_source_outside_approved_master_history_refuses(self):
        restored=self.snapshot()
        path='/repos/shk95/configs/actions/runs/4/attempts/1'
        code,headers,raw=self.fake.request('GET',path,None)
        value=T.document(raw);value['head_sha']=F.H
        self.fake.responses[('GET',path)]=self.fake.response(value)
        with self.assertRaisesRegex(T.Refusal,'unapproved-owner-source'):restored.owner_target(restored.state['owner'])

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
        # Bind this disposable fixture's public commit, never the real delivery pin.
        inputs=json.loads(template.read_text());inputs['transport-source']=source
        inputs['transport-manifest']=T.digest((f.public/'tool/version-control/release-transport.manifest.tsv').read_bytes())
        template.write_text(json.dumps(inputs))
        command=[sys.executable,'-I','-S','-B',str(f.public/'tool/version-control/release-transport-preflight.py'),
                 'preflight','--source',source,'--template',str(template)]
        result=subprocess.run(command,capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)
        value=json.loads(result.stdout);self.assertFalse(value['enabled']);self.assertFalse(value['production_certification'])
        self.assertIn('operating-repository',value['unresolved'])
        inputs=json.loads(template.read_text());inputs['transport-source']=F.H
        template.write_text(json.dumps(inputs))
        self.assertNotEqual(subprocess.run(command,capture_output=True).returncode,0)
        inputs['transport-source']='UNRESOLVED';template.write_text(json.dumps(inputs))
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

    def proposal_candidate(self):
        return dict(F.CANDIDATE,kind='candidate',**{'candidate-generation':'2'})

    def proposal_transcript(self,snapshot):
        return T.document((snapshot.batch/'transcript.json').read_bytes())

    def reconciled_proposal_snapshot(self):
        snapshot=self.snapshot();plan=snapshot.plan(F.X)
        changes=snapshot.observation(plan,'absent',None)
        T.Journal(self.api,snapshot,self.fake.head).publish(changes)
        self.fake.calls.clear()
        return self.snapshot()

    def candidate_transcript(self,snapshot):
        transcript=self.proposal_transcript(snapshot)
        candidate={k:v for k,v in self.proposal_candidate().items() if k!='kind'}
        transcript['source'].append(F.transcript('preview',candidate)['source'][0])
        return transcript

    def test_general_candidate_refuses_unreconciled_effect(self):
        snapshot=self.snapshot()
        with self.assertRaises(T.Refusal):
            snapshot.propose_event(self.proposal_candidate(),self.candidate_transcript(snapshot))
        self.assertTrue(snapshot.proposal_fenced)
        self.assertFalse(any(m!='GET' for m,_,_ in self.fake.calls))

    def test_general_candidate_projection_preserves_original_history_and_invalidates_approval(self):
        snapshot=self.reconciled_proposal_snapshot();before=copy.deepcopy(snapshot.state)
        old={p.name:p.read_bytes() for p in (self.fixture.operating/'history').iterdir()}
        changes=snapshot.propose_event(self.proposal_candidate(),self.candidate_transcript(snapshot))
        self.assertTrue(before['approval'])
        event=F.parse(next(v for p,v in changes.items() if p.startswith('history/')),'event')
        self.assertEqual(event['sequence'],str(int(before['sequence'])+1))
        self.assertEqual(event['batch'],before['batch'])
        self.assertFalse(any(m!='GET' for m,_,_ in self.fake.calls))
        journal=T.Journal(self.api,snapshot,self.fake.head);journal.publish(changes)
        restored=self.snapshot()
        self.assertEqual(restored.state['candidate']['candidate-generation'],'2')
        self.assertEqual(restored.state['stage'],'candidate')
        self.assertIsNone(restored.state['approval']);self.assertEqual(restored.state['evidence'],[])
        for name,data in old.items():self.assertEqual((self.fixture.operating/'history'/name).read_bytes(),data)

    def test_general_candidate_then_evidence_uses_original_package_and_full_global_replay(self):
        snapshot=self.reconciled_proposal_snapshot()
        changes=snapshot.propose_event(self.proposal_candidate(),self.candidate_transcript(snapshot))
        T.Journal(self.api,snapshot,self.fake.head).publish(changes)
        self.entry=T.Entry(self.api,self.trusted,dict(self.runtime,candidate=T.digest(T.canonical(snapshot.state['candidate']))))
        restored=self.snapshot()
        fields={'kind':'evidence','evidence':[F.EVIDENCE],'evidence-digest':T.digest(T.canonical([F.EVIDENCE]))}
        changes=restored.propose_event(fields,self.proposal_transcript(restored))
        T.Journal(self.api,restored,self.fake.head).publish(changes)
        final=self.snapshot();self.assertEqual(final.state['stage'],'validated');self.assertIsNone(final.state['approval'])

    def test_general_intent_is_derived_and_published_before_any_public_effect(self):
        snapshot=self.snapshot()
        payload={'repository':T.PUBLIC,'head':'dev','base':'master','dev':F.D,'master':F.H,'body-operation':'2'*64}
        event=F.effect('pr',payload,op_id='2'*64)
        fields={k:v for k,v in event.items() if k not in {'sequence','prior','batch'}}
        changes=snapshot.propose_event(fields,self.proposal_transcript(snapshot))
        T.Journal(self.api,snapshot,self.fake.head).publish(changes)
        self.assertEqual(snapshot.state['operations']['2'*64]['state'],'intent')
        self.assertFalse(any(m!='GET' and p.startswith('/repos/shk95/configs/') for m,p,_ in self.fake.calls))

    def test_general_candidate_refuses_unknown_effect(self):
        f=self.fixture;supplied=T.document((f.operating/'current/transcript.json').read_bytes())
        unknown={'status':'unknown','target':{},'complete':True}
        payload=T.document(f.events[-1]['payload'].encode())
        supplied['observations'][F.X]=[unknown]
        f.append(F.effect('pr',payload,'unknown',unknown))
        projection=F.engine.index(F.engine.reduce(f.events,F.CONFIG,supplied),F.digest(F.encode(f.events[-1])))
        f.final=dict(row.split('\t') for row in projection.decode().splitlines()[1:])
        f.ledger[-1]['projection']=F.digest(projection)
        (f.operating/'current/transcript.json').write_bytes(F.canonical(supplied))
        f.save();self.fake.head=f.head
        snapshot=self.snapshot();self.fake.calls.clear()
        self.assertEqual(snapshot.state['operations'][F.X]['state'],'unknown')
        with self.assertRaises(T.Refusal):
            snapshot.propose_event(self.proposal_candidate(),self.candidate_transcript(snapshot))
        self.assertFalse(any(m!='GET' for m,_,_ in self.fake.calls))

    def test_general_candidate_refuses_frozen_publication(self):
        snapshot=self.reconciled_proposal_snapshot()
        payload={'repository':T.PUBLIC,'number':'17','dev':F.D,'master':F.H,'tree':F.T}
        event=F.effect('merge',payload,op_id='3'*64)
        fields={k:v for k,v in event.items() if k not in {'sequence','prior','batch'}}
        changes=snapshot.propose_event(fields,self.proposal_transcript(snapshot))
        T.Journal(self.api,snapshot,self.fake.head).publish(changes)
        snapshot=self.snapshot();plan=snapshot.plan('3'*64)
        changes=snapshot.observation(plan,'applied',F.T)
        T.Journal(self.api,snapshot,self.fake.head).publish(changes)
        snapshot=self.snapshot();self.fake.calls.clear()
        self.assertTrue(snapshot.state['frozen'])
        with self.assertRaises(T.Refusal):
            snapshot.propose_event(self.proposal_candidate(),self.candidate_transcript(snapshot))
        self.assertFalse(any(m!='GET' for m,_,_ in self.fake.calls))

    def test_general_projection_rechecks_after_local_projection(self):
        snapshot=self.snapshot();original=snapshot.projected_changes
        def move(*args):
            changes=original(*args);self.fake.head='b'*40;return changes
        snapshot.projected_changes=move
        with self.assertRaises(T.Refusal):
            snapshot.propose_event({'kind':'refresh-result','payload':T.canonical({'status':'noop'}).decode()},
                                   self.proposal_transcript(snapshot))
        self.assertTrue(snapshot.proposal_fenced)
        self.assertFalse(any(m!='GET' for m,_,_ in self.fake.calls))

    def test_general_projection_uses_retained_package_after_new_source(self):
        f=self.fixture;old=f.packages['3']['master']
        (f.public/'tool/version-control/release-control-package/engine.py').write_text('raise RuntimeError("unapproved current semantics")')
        later=f.commit(f.public);f.packages['3']=dict(f.packages['3'],master=later)
        self.fake.source=later;self.trusted['source']=later;self.runtime['source']=later
        self.entry=T.Entry(self.api,self.trusted,self.runtime)
        snapshot=self.snapshot();self.assertEqual(snapshot.owner_source,old)
        fields={'kind':'refresh-result','payload':T.canonical({'status':'noop'}).decode()}
        changes=snapshot.propose_event(fields,self.proposal_transcript(snapshot))
        T.Journal(self.api,snapshot,self.fake.head).publish(changes)
        self.assertEqual(self.snapshot().state['refresh-stage'],'noop')

    def test_general_projection_refuses_framing_injection_and_specialized_authority(self):
        for change in ({'sequence':'1'},{'prior':'0'*64},{'batch':'0'*64},{'kind':'approval'},
                       {'kind':'claim'},{'kind':'observation'},{'kind':'stop-observed'},{'kind':'unknown'}):
            snapshot=self.snapshot()
            with self.subTest(change=change),self.assertRaises(T.Refusal):
                snapshot.propose_event(dict(self.proposal_candidate(),**change),self.proposal_transcript(snapshot))
            self.assertTrue(snapshot.proposal_fenced)
        self.assertFalse(any(m!='GET' for m,_,_ in self.fake.calls))

    def test_general_projection_preserves_original_transcript_bindings(self):
        for key in ('source','checks','owner','observations','protection'):
            snapshot=self.snapshot();transcript=self.proposal_transcript(snapshot)
            transcript[key]=[] if key in {'source','checks'} else {'foreign':'private'}
            with self.subTest(key=key),self.assertRaises(T.Refusal):snapshot.propose_event(self.proposal_candidate(),transcript)
        self.assertFalse(any(m!='GET' for m,_,_ in self.fake.calls))

    def test_general_projection_rechecks_actual_owner_head_job_and_stop(self):
        for failure in ('owner','source','head','job','stop','candidate'):
            snapshot=self.snapshot();old_source=self.fake.source;old_head=self.fake.head
            if failure=='owner':snapshot.entry.runtime['run']=6
            elif failure=='source':self.fake.source='b'*40
            elif failure=='head':self.fake.head='b'*40
            elif failure=='job':self.fake.jobs_extra=[{'id':99,'name':'foreign'}]
            elif failure=='stop':self.fake.stop=True
            else:snapshot.entry.runtime['candidate']='0'*64
            with self.subTest(failure=failure),self.assertRaises((T.Refusal,ValueError)):
                snapshot.propose_event(self.proposal_candidate(),self.proposal_transcript(snapshot))
            self.fake.source=old_source;self.fake.head=old_head;self.fake.jobs_extra=[];self.fake.stop=False
            snapshot.entry.runtime.update(self.runtime)
        self.assertFalse(any(m!='GET' for m,_,_ in self.fake.calls))

    def test_general_projection_fences_pending_or_failed_proposal_and_changed_bytes(self):
        snapshot=self.reconciled_proposal_snapshot();transcript=self.candidate_transcript(snapshot)
        changes=snapshot.propose_event(self.proposal_candidate(),transcript)
        with self.assertRaises(T.Refusal):snapshot.propose_event(self.proposal_candidate(),transcript)
        with self.assertRaises(T.Refusal):snapshot.claim()
        with self.assertRaises(T.Refusal):snapshot.observation(snapshot.plan(F.X),'absent',None)
        with self.assertRaises(T.Refusal):snapshot.transition({})
        changes['current/index.tsv']+=b'poisoned\n'
        with self.assertRaises(T.Refusal):T.Journal(self.api,snapshot,self.fake.head).publish(changes)
        self.assertFalse(any(m!='GET' for m,_,_ in self.fake.calls))
        snapshot=self.snapshot()
        with self.assertRaises(T.Refusal):snapshot.propose_event(dict(self.proposal_candidate(),unknown='value'),self.proposal_transcript(snapshot))
        with self.assertRaises(T.Refusal):snapshot.propose_event(self.proposal_candidate(),self.proposal_transcript(snapshot))

    def test_unknown_record_object_fences_the_same_journal_before_retry(self):
        snapshot=self.reconciled_proposal_snapshot();changes=snapshot.propose_event(self.proposal_candidate(),self.candidate_transcript(snapshot))
        journal=T.Journal(self.api,snapshot,self.fake.head)
        self.fake.fail[('POST','/repos/fixture/operating/git/blobs')]=T.Unknown('unknown-write')
        with self.assertRaises(T.Unknown):journal.publish(changes)
        self.assertTrue(journal.pending);calls=len(self.fake.calls)
        with self.assertRaises(T.Refusal):journal.publish(changes)
        self.assertEqual(len(self.fake.calls),calls)
        self.assertFalse(any(m!='GET' and p.startswith('/repos/shk95/configs/') for m,p,_ in self.fake.calls))

    def test_claim_joins_same_owner_without_a_record(self):
        snapshot=self.snapshot()
        self.assertEqual(snapshot.claim(),{})
        self.assertFalse(any(m!='GET' for m,_,_ in self.fake.calls))

    def takeover_entry(self):
        self.fake.terminal=True;self.fake.terminal_jobs=True
        runtime=dict(self.runtime,run=6)
        value={'id':6,'run_attempt':1,'head_sha':self.fake.source,'head_branch':'master','event':'workflow_dispatch',
            'workflow_id':2,'repository':{'id':1},'actor':{'id':3},'triggering_actor':{'id':3},'status':'in_progress'}
        for suffix in ('','/attempts/1'):
            self.fake.responses[('GET','/repos/shk95/configs/actions/runs/6'+suffix)]=self.fake.response(value)
        jobs={'total_count':1,'jobs':[{'id':5,'run_id':6,'name':'writer','head_sha':self.fake.source,'status':'in_progress'}]}
        self.fake.responses[('GET','/repos/shk95/configs/actions/runs/6/attempts/1/jobs?per_page=100&page=1')]=self.fake.response(jobs)
        self.entry=T.Entry(self.api,self.trusted,runtime)

    def test_claim_refuses_unreconciled_old_intent_even_after_terminal_owner(self):
        self.takeover_entry();snapshot=self.snapshot()
        with self.assertRaises(T.Refusal):snapshot.claim()
        self.assertFalse(any(m!='GET' for m,_,_ in self.fake.calls))

    def test_claim_never_cancels_or_takes_over_a_live_owner(self):
        self.takeover_entry();self.fake.terminal=False;self.fake.terminal_jobs=False
        snapshot=self.snapshot()
        with self.assertRaises(T.Refusal):snapshot.claim()
        self.assertFalse(any(m!='GET' for m,_,_ in self.fake.calls))

    def test_terminal_reconciled_owner_claim_advances_once_without_public_effect(self):
        executor,plan=self.executor();self.assertEqual(executor.perform(plan),'applied')
        self.takeover_entry();snapshot=self.snapshot()
        public_writes=sum(m!='GET' and p.startswith('/repos/shk95/configs/') for m,p,_ in self.fake.calls)
        changes=snapshot.claim();self.assertTrue(changes)
        T.Journal(self.api,snapshot,self.fake.head).publish(changes)
        self.assertEqual(snapshot.state['owner']['run'],'6')
        self.assertEqual(snapshot.state['generation'],'2')
        self.assertEqual(snapshot.claim(),{})
        self.assertEqual(public_writes,sum(m!='GET' and p.startswith('/repos/shk95/configs/') for m,p,_ in self.fake.calls))

class StartProof(unittest.TestCase):
    # INV repository/authenticated-release-transport
    # INV repository/fixture-git-isolation
    def setUp(self):
        self.fixture=F.GlobalHistoryProof();self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
        f=self.fixture
        (f.operating/'config/operating.tsv').write_bytes(F.encode(F.CONFIG))
        (f.operating/'current/transcript.json').write_bytes(F.canonical(F.transcript('preview',candidate=None)))
        (f.operating/'current/batches.tsv').write_bytes(b'format\t1\n')
        fields=dict(F.loader.singletons(F.engine.index(F.engine.initial(),F.Z),F.loader.PROJECTION_FIELDS),
                    **{'index-kind':'global-1','ledger-digest':F.digest(F.canonical([]))})
        (f.operating/'current/index.tsv').write_bytes(F.encode(fields))
        self.head=f.commit(f.operating)
        self.connect()

    def connect(self):
        f=self.fixture
        self.fake=Fake(f.public,f.operating,f.packages['3']['master'])
        self.api=T.Api(self.fake,'fixture/operating')
        self.runtime={'repository':T.PUBLIC,'ref':'refs/heads/master','event':'workflow_dispatch',
            'run':4,'attempt':1,'job':5,'actor':3,'source':self.fake.source,'environment':'fixture-controller',
            'mode':'start','candidate':F.Z}
        self.trusted={'source':self.fake.source,'workflow':2,'workflow-path':'.github/workflows/release-control-writer.yml',
            'repository-id':1,'actors':[3],'environment':'fixture-controller','job-name':'writer'}
        value={'id':4,'run_attempt':1,'head_sha':self.fake.source,'head_branch':'master','event':'workflow_dispatch',
            'workflow_id':2,'repository':{'id':1},'actor':{'id':3},'triggering_actor':{'id':3},
            'status':'in_progress','run_started_at':'2026-10-02T00:00:00Z'}
        self.fake.responses[('GET','/repos/shk95/configs/actions/runs/4/attempts/1')]=self.fake.response(value)
        self.entry=T.Entry(self.api,self.trusted,self.runtime)

    def start(self):
        f=self.fixture
        plan=B.StartPlan(self.entry,f.public,f.operating,F.encode(f.packages['3']),self.head)
        self.addCleanup(plan.close)
        return plan

    def test_empty_start_uses_original_records_and_global_projection(self):
        f=self.fixture;before=F.run_git(f.operating,'rev-parse','HEAD');plan=self.start()
        self.assertEqual(F.run_git(f.operating,'rev-parse','HEAD'),before)
        self.assertFalse(any(m!='GET' for m,_,_ in self.fake.calls))
        changes=plan.pending_changes
        first=F.parse(changes['history/000000000001.tsv'],'event')
        claim=F.parse(changes['history/000000000002.tsv'],'event')
        self.assertEqual(first['kind'],'batch-start');self.assertEqual(first['config-commit'],self.head)
        self.assertEqual(claim['operating-head'],self.head);self.assertEqual(claim['generation'],'1')
        self.assertEqual(claim['prior'],F.digest(changes['history/000000000001.tsv']))
        journal=T.Journal(self.api,plan,self.head);result=journal.publish(changes)
        snapshot=B.Snapshot(self.entry,f.public,f.operating,F.encode(f.packages['3']),result,plan.tagger,[])
        self.addCleanup(snapshot.close)
        self.assertEqual(snapshot.state['stage'],'active');self.assertEqual(snapshot.state['owner']['job'],'5')
        self.assertFalse(any(p.endswith('/pulls') for _,p,_ in self.fake.calls))

    def test_completed_old_protocols_keep_literal_history_and_original_ledgers(self):
        f=self.fixture
        f.add_batch('1',F.X,True);f.add_batch('3',F.Y,True);f.save()
        self.head=f.head
        self.connect()
        old={p.name:p.read_bytes() for p in (f.operating/'history').iterdir()}
        plan=self.start();self.assertIn('history/000000000007.tsv',plan.pending_changes)
        result=T.Journal(self.api,plan,self.head).publish(plan.pending_changes)
        snapshot=B.Snapshot(self.entry,f.public,f.operating,F.encode(f.packages['3']),result,plan.tagger,[])
        self.addCleanup(snapshot.close)
        self.assertEqual(snapshot.state['stage'],'active')
        for name,data in old.items():self.assertEqual((f.operating/'history'/name).read_bytes(),data)

    def test_outstanding_batch_never_restarts_or_adopts_current_package(self):
        f=self.fixture;(f.operating/'current/transcript.json').write_bytes(F.canonical({'source':[]}));f.commit(f.operating)
        f.add_batch('3',F.X,False);f.save();self.head=f.head;self.connect()
        with self.assertRaises(T.Refusal):self.start()
        self.assertFalse(any(m!='GET' for m,_,_ in self.fake.calls))

    def test_disabled_stopped_and_wrong_configuration_refuse_before_write(self):
        f=self.fixture
        for changed in ({'enabled':'0'},{'workflow':'99'},{'actors':'99'},{'protocol':'2'}):
            (f.operating/'config/operating.tsv').write_bytes(F.encode(dict(F.CONFIG,**changed)))
            self.head=f.commit(f.operating);self.connect()
            with self.subTest(changed=changed),self.assertRaises(T.Refusal):self.start()
            self.assertFalse(any(m!='GET' for m,_,_ in self.fake.calls))
        (f.operating/'config/operating.tsv').write_bytes(F.encode(F.CONFIG))
        (f.operating/'control/stop.tsv').write_bytes(F.encode(dict(F.STOP,stop='1')))
        self.head=f.commit(f.operating);self.connect()
        with self.assertRaises(T.Refusal):self.start()

    def test_mixed_job_and_moving_source_refuse(self):
        self.fake.jobs_extra=[{'id':99,'name':'inspector'}]
        with self.assertRaises(T.Refusal):self.start()
        self.fake.jobs_extra=[]
        self.fake.responses[('GET','/repos/shk95/configs/git/ref/heads/master')]=self.fake.response(
            {'ref':'refs/heads/master','object':{'type':'commit','sha':F.H}})
        with self.assertRaises(T.Refusal):self.start()

    def test_bad_global_index_and_unprojected_changes_refuse(self):
        plan=self.start()
        with self.assertRaises(T.Refusal):T.Journal(self.api,plan,self.head).publish({'current/index.tsv':b'invented'})
        plan.pending_changes['current/index.tsv']=b'modified through the shared proposal'
        with self.assertRaises(T.Refusal):T.Journal(self.api,plan,self.head).publish(plan.pending_changes)
        f=self.fixture;(f.operating/'current/index.tsv').write_bytes(b'format\t1\n')
        self.head=f.commit(f.operating);self.connect()
        with self.assertRaises(ValueError):self.start()
        self.assertFalse(any(m!='GET' for m,_,_ in self.fake.calls))

    def test_conflict_after_plan_and_lost_ref_response_never_duplicate_start(self):
        plan=self.start();self.fake.lose_record=True
        result=T.Journal(self.api,plan,self.head).publish(plan.pending_changes)
        self.assertEqual(result,self.fake.head)
        self.assertEqual(sum(m=='PATCH' for m,_,_ in self.fake.calls),1)
        self.assertIsNone(plan.pending_changes)
        with self.assertRaises(T.Refusal):plan.validate_changes({'current/index.tsv':b'invented'})

class ObservedEvidenceProof(unittest.TestCase):
    """Original candidate objects plus observed receipts; no HTTP or real credential."""
    snapshot=TransportProof.snapshot
    reconciled_proposal_snapshot=TransportProof.reconciled_proposal_snapshot

    def setUp(self):
        TransportProof.setUp(self)
        f=self.fixture
        workflow=f.public/'.github/workflows/ci.yml';workflow.parent.mkdir(parents=True,exist_ok=True)
        workflow.write_text('name: Fixture data only\n')
        F.run_git(f.public,'add','.github/workflows/ci.yml');F.run_git(f.public,'commit','-qm','fixture candidate')
        self.dev=F.run_git(f.public,'rev-parse','HEAD');self.tree=F.run_git(f.public,'rev-parse','HEAD^{tree}')
        self.fake.dev=self.dev
        self.requirements=[dict(self.requirements[0],source=self.dev,workflow=7,
            **{'workflow-path':'.github/workflows/ci.yml',
               'workflow-blob':F.run_git(f.public,'rev-parse','HEAD:.github/workflows/ci.yml')})]
        self.run={'id':8,'run_attempt':1,'head_sha':self.dev,'head_branch':'dev','event':'push',
            'workflow_id':7,'repository':{'id':1},'head_repository':{'id':1},'status':'completed','conclusion':'success'}
        self.job={'id':9,'run_id':8,'name':'Required checks','head_sha':self.dev,
            'status':'completed','conclusion':'success','html_url':'https://github.com/shk95/configs/actions/runs/8/job/9'}
        self.check={'id':10,'name':'Required checks','app':{'id':15368},'head_sha':self.dev,
            'status':'completed','conclusion':'success','details_url':self.job['html_url']}
        self.bind_metadata()
        base=self.reconciled_proposal_snapshot()
        self.prepare(base)
        self.fake.calls.clear()

    def bind_metadata(self):
        def response(suffix,value):self.fake.responses[('GET','/repos/shk95/configs'+suffix)]=self.fake.response(value)
        response('/actions/runs/8',self.run);response('/actions/runs/8/attempts/1',self.run)
        response('/actions/runs/8/attempts/1/jobs?per_page=100&page=1',{'total_count':1,'jobs':[self.job]})
        response('/actions/workflows/7',{'id':7,'path':'.github/workflows/ci.yml'})
        response('/commits/'+self.dev+'/check-runs?per_page=100&page=1',{'total_count':1,'check_runs':[self.check]})

    def prepare(self,snapshot=None,**change):
        snapshot=snapshot or self.snapshot()
        candidate=dict(F.CANDIDATE,dev=self.dev,master=self.fake.source,tree=self.tree,
                       **{'candidate-generation':str(int(snapshot.state['promotion-generation'])+1)})
        candidate.update(change)
        transcript=T.document((snapshot.batch/'transcript.json').read_bytes())
        transcript['source'].append(F.transcript('preview',candidate)['source'][0])
        changes=snapshot.propose_event(dict(candidate,kind='candidate'),transcript)
        T.Journal(self.api,snapshot,self.fake.head).publish(changes)
        self.runtime['candidate']=T.digest(T.canonical(candidate))
        self.entry=T.Entry(self.api,self.trusted,self.runtime)
        self.candidate=candidate
        return self.snapshot()

    def no_writes(self):self.assertFalse(any(method!='GET' for method,_,_ in self.fake.calls))

    def test_observed_rows_preserve_transcript_and_publish_original_history(self):
        snapshot=self.snapshot();old=T.document((snapshot.batch/'transcript.json').read_bytes())
        changes=snapshot.propose_evidence();new=T.document(changes['current/transcript.json'])
        self.assertEqual(new['checks'][:len(old['checks'])],old['checks'])
        self.assertEqual(new['source'],old['source']);self.assertEqual(new['observations'],old['observations'])
        row=new['checks'][-1]
        self.assertEqual(row,['gate',self.dev,self.fake.source,self.tree,F.X,F.X,'verified','8','1','9','fixture-tool'])
        self.no_writes()
        head=T.Journal(self.api,snapshot,self.fake.head).publish(changes)
        restored=self.snapshot();self.assertEqual(restored.head,head);self.assertEqual(restored.state['stage'],'validated')
        self.assertEqual(restored.state['evidence'],[row]);self.assertIsNone(snapshot.evidence_binding)

    def test_actual_clean_divergent_merge_and_conflict_refusal(self):
        f=self.fixture;master=self.fake.source;dev=self.dev
        F.run_git(f.public,'checkout','-q',master)
        (f.public/'independent.txt').write_text('separate original side\n')
        F.run_git(f.public,'add','independent.txt');F.run_git(f.public,'commit','-qm','fixture other side')
        other=F.run_git(f.public,'rev-parse','HEAD')
        expected=F.run_git(f.public,'merge-tree','--write-tree','--no-messages',other,dev)
        self.assertEqual(self.snapshot().public_merge_tree({'master':other,'dev':dev}),expected)
        F.run_git(f.public,'checkout','-q',master)
        workflow=f.public/'.github/workflows/ci.yml';workflow.parent.mkdir(parents=True,exist_ok=True)
        workflow.write_text('conflicting addition\n');F.run_git(f.public,'add','.github/workflows/ci.yml')
        F.run_git(f.public,'commit','-qm','fixture conflict');conflict=F.run_git(f.public,'rev-parse','HEAD')
        with self.assertRaises(T.Refusal):self.snapshot().public_merge_tree({'master':conflict,'dev':dev})
        self.no_writes()

    def test_wrong_tree_unavailable_original_objects_and_api_parent_mismatch(self):
        snapshot=self.prepare(tree=F.T);self.fake.calls.clear()
        with self.assertRaises(T.Refusal):snapshot.propose_evidence()
        self.no_writes()
        with self.assertRaises((T.Refusal,ValueError)):snapshot.public_merge_tree({'master':self.fake.source,'dev':F.D})
        self.fake.responses[('GET','/repos/shk95/configs/git/commits/'+self.dev)]=self.fake.response(
            {'sha':self.dev,'tree':{'sha':self.tree},'parents':[]})
        with self.assertRaises(T.Refusal):self.snapshot().public_merge_tree(self.candidate)

    def test_selected_trust_requires_exact_unique_requirements(self):
        for requirements in ([],self.requirements*2,[dict(self.requirements[0],id='foreign')]):
            self.requirements=requirements;snapshot=self.snapshot();self.fake.calls.clear()
            with self.subTest(requirements=requirements),self.assertRaises(T.Refusal):snapshot.propose_evidence()
            self.no_writes()

    def test_failed_foreign_latest_attempt_and_job_observations_refuse(self):
        original=(copy.deepcopy(self.run),copy.deepcopy(self.job),copy.deepcopy(self.check))
        for target,key,value in [('run','repository',{'id':99}),('run','head_repository',{'id':99}),
            ('run','event','pull_request_target'),('run','run_attempt',2),('run','head_sha',F.D),
            ('job','name','other-job'),('job','run_id',80),('job','conclusion','failure'),
            ('job','html_url','https://invalid.example/job'),('check','conclusion','failure')]:
            self.run,self.job,self.check=copy.deepcopy(original);getattr(self,target)[key]=value
            self.bind_metadata();snapshot=self.snapshot();self.fake.calls.clear()
            with self.subTest(target=target,key=key),self.assertRaises(T.Refusal):snapshot.propose_evidence()
            self.no_writes()

    def test_ambiguous_missing_workflow_or_wrong_tool_blobs_refuse(self):
        suffix='/commits/'+self.dev+'/check-runs?per_page=100&page=1'
        self.fake.responses[('GET','/repos/shk95/configs'+suffix)]=self.fake.response(
            {'total_count':2,'check_runs':[self.check,dict(self.check,id=11)]})
        with self.assertRaises(T.Refusal):self.snapshot().propose_evidence()
        self.bind_metadata()
        self.fake.responses[('GET','/repos/shk95/configs/actions/workflows/7')]=self.fake.response({'id':70,'path':'.github/workflows/ci.yml'})
        with self.assertRaises(T.Refusal):self.snapshot().propose_evidence()
        self.bind_metadata();self.requirements[0]['tool-blob']=F.H
        with self.assertRaises(T.Refusal):self.snapshot().propose_evidence()
        self.no_writes()

    def test_child_receives_no_credentials_ambient_git_or_merge_driver(self):
        from unittest import mock
        import os
        actual=B.subprocess.run;children=[]
        def checked(command,**kwargs):
            if 'merge-tree' in command:
                children.append(kwargs['env'])
                self.assertNotIn('CONFIGS_RELEASE_TOKEN',kwargs['env']);self.assertNotIn('GH_TOKEN',kwargs['env'])
                self.assertNotIn('GIT_CONFIG_COUNT',kwargs['env']);self.assertEqual(kwargs['env']['GIT_ALLOW_PROTOCOL'],'')
                self.assertIn('core.attributesFile='+os.devnull,command)
            return actual(command,**kwargs)
        with mock.patch.dict(os.environ,{'CONFIGS_RELEASE_TOKEN':'fixture-only','GH_TOKEN':'fixture-only',
            'GIT_CONFIG_COUNT':'1','GIT_CONFIG_KEY_0':'merge.fixture.driver','GIT_CONFIG_VALUE_0':'invalid-command'}),            mock.patch.object(B.subprocess,'run',side_effect=checked):
            self.snapshot().propose_evidence()
        self.assertTrue(children);self.no_writes()

    def test_conflicting_candidate_cannot_invoke_ambient_or_repository_merge_driver(self):
        from unittest import mock
        import os,shlex
        f=self.fixture;marker=f.public.parent/'driver-ran'
        F.run_git(f.public,'checkout','-q',self.fake.source)
        (f.public/'.gitattributes').write_text('shared.txt merge=fixture\n')
        (f.public/'shared.txt').write_text('original\n')
        F.run_git(f.public,'add','.gitattributes','shared.txt');F.run_git(f.public,'commit','-qm','fixture base')
        base=F.run_git(f.public,'rev-parse','HEAD')
        (f.public/'shared.txt').write_text('left\n');F.run_git(f.public,'add','shared.txt')
        F.run_git(f.public,'commit','-qm','fixture left');left=F.run_git(f.public,'rev-parse','HEAD')
        F.run_git(f.public,'checkout','-q',base)
        (f.public/'shared.txt').write_text('right\n');F.run_git(f.public,'add','shared.txt')
        F.run_git(f.public,'commit','-qm','fixture right');right=F.run_git(f.public,'rev-parse','HEAD')
        driver=shlex.quote(sys.executable.replace('\\','/'))+' -c '+shlex.quote(
            'from pathlib import Path; Path('+repr(str(marker))+').write_text("unexpected")')
        F.run_git(f.public,'config','merge.fixture.driver',driver)
        with mock.patch.dict(os.environ,{'GIT_CONFIG_COUNT':'1','GIT_CONFIG_KEY_0':'merge.fixture.driver','GIT_CONFIG_VALUE_0':driver}),            self.assertRaises(T.Refusal):self.snapshot().public_merge_tree({'master':left,'dev':right})
        self.assertFalse(marker.exists());self.no_writes()

    def test_corrupt_original_candidate_object_refuses_before_effect(self):
        import stat
        f=self.fixture
        snapshot=self.snapshot()
        location=Path(F.run_git(f.public,'rev-parse','--git-path','objects/'+self.dev[:2]+'/'+self.dev[2:]))
        if not location.is_absolute():location=f.public/location
        location.chmod(stat.S_IRUSR|stat.S_IWUSR);location.unlink();location.write_bytes(b'corrupt fixture object')
        self.fake.calls.clear()
        with self.assertRaises((T.Refusal,ValueError)):snapshot.propose_evidence()
        self.no_writes()

    def test_moving_receipts_fence_after_complete_collection(self):
        from unittest import mock
        for when in (2,3):
            snapshot=self.snapshot();actual=snapshot.entry.evidence;count=0
            def moving(*args):
                nonlocal count
                result=actual(*args);count+=1
                if count==when:result[0]['check']=11
                return result
            with self.subTest(when=when),mock.patch.object(snapshot.entry,'evidence',side_effect=moving),self.assertRaises(T.Refusal):snapshot.propose_evidence()
            with self.assertRaises(T.Refusal):snapshot.propose_evidence()
            self.no_writes()

    def test_fresh_publication_rechecks_failed_checks_and_source(self):
        for failure in ('checks','dev','operating-head','requirements'):
            self.bind_metadata();self.fake.dev=self.dev
            snapshot=self.snapshot();changes=snapshot.propose_evidence()
            journal=T.Journal(self.api,snapshot,self.fake.head);self.fake.calls.clear()
            old_head=self.fake.head
            if failure=='checks':
                self.check['conclusion']='failure';self.bind_metadata()
            elif failure=='dev':self.fake.dev=F.D
            elif failure=='operating-head':self.fake.head=F.D
            else:snapshot.requirements[0]['tool']='changed-tool'
            with self.subTest(failure=failure),self.assertRaises(T.Refusal):journal.publish(changes)
            self.no_writes();self.check['conclusion']='success';self.fake.head=old_head

    def test_original_remote_stop_record_refuses_collection(self):
        f=self.fixture
        (f.operating/'control/stop.tsv').write_bytes(F.encode(dict(F.STOP,stop='1')))
        f.commit(f.operating);self.fake.head=F.run_git(f.operating,'rev-parse','HEAD')
        snapshot=self.snapshot();self.fake.calls.clear()
        with self.assertRaises(T.Refusal):snapshot.propose_evidence()
        self.no_writes()

    def test_collector_refuses_outstanding_mutated_proposal_and_retained_rows(self):
        snapshot=self.snapshot();changes=snapshot.propose_evidence()
        with self.assertRaises(T.Refusal):snapshot.propose_evidence()
        changes['current/transcript.json']+=b' '
        self.fake.calls.clear()
        with self.assertRaises(T.Refusal):T.Journal(self.api,snapshot,self.fake.head).publish(changes)
        self.no_writes()


class PublicChecksBoundaryProof(unittest.TestCase):
    def test_only_public_check_reads_omit_the_dedicated_token(self):
        from unittest import mock
        connection=mock.Mock();response=connection.getresponse.return_value
        response.status=200;response.getheaders.return_value=[];response.read.return_value=b'{}'
        channel=T.Https('fixture-only-credential')
        with mock.patch.object(T.http.client,'HTTPSConnection',return_value=connection):
            for suffix in ('','?per_page=100&page=1','?per_page=100&page=20'):
                channel.request('GET','/repos/'+T.PUBLIC+'/commits/'+F.D+'/check-runs'+suffix,None)
                self.assertNotIn('Authorization',connection.request.call_args.kwargs['headers'])
            for path in ('/repos/'+T.PUBLIC+'/actions/runs/8',
                '/repos/'+T.PUBLIC+'/branches/dev/protection',
                '/repos/fixture/operating/commits/'+F.D+'/check-runs?per_page=100&page=1'):
                channel.request('GET',path,None)
                self.assertEqual(connection.request.call_args.kwargs['headers']['Authorization'],
                                 'Bearer fixture-only-credential')

if __name__=='__main__':unittest.main()
