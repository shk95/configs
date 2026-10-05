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
        self.master=F.H;self.dev=F.D;self.stop=False;self.refresh_heads={}

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
        if route=='':return self.response({'id':1330390069,'full_name':T.PUBLIC,'private':False})
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
        if route.startswith('/git/matching-refs/heads/'):
            name=route.split('/git/matching-refs/heads/',1)[1]
            return self.response([{'ref':'refs/heads/'+name,'object':{'type':'commit','sha':self.refresh_heads[name]}}] if name in self.refresh_heads else [])
        if route=='/git/refs' and method=='POST':
            name=body['ref'].removeprefix('refs/heads/');self.refresh_heads[name]=body['sha']
            return self.response({'ref':body['ref'],'object':{'type':'commit','sha':body['sha']}},201)
        if route=='/git/ref/heads/operations':return self.response({'ref':'refs/heads/operations','object':{'type':'commit','sha':self.head}})
        if route=='/git/ref/heads/master':return self.response({'ref':'refs/heads/master','object':{'type':'commit','sha':self.source}})
        if route=='/git/ref/heads/dev':return self.response({'ref':'refs/heads/dev','object':{'type':'commit','sha':self.dev}})
        if route.startswith('/git/commits/'):
            oid=route.rsplit('/',1)[1]
            result=subprocess.run(['git','-C',str(root),'cat-file','commit',oid],capture_output=True)
            if result.returncode:return self.response({},404)
            raw=result.stdout
            fields=B.O.commit_fields(raw)
            return self.response(dict(fields,sha=oid,tree={'sha':fields['tree']},parents=[{'sha':v} for v in fields['parents']]))
        if route.startswith('/git/trees/'):
            oid=route.rsplit('/',1)[1]
            result=subprocess.run(['git','-C',str(root),'ls-tree',*(['-r','-t'] if parts.query else []),oid],capture_output=True)
            if result.returncode:return self.response({},404)
            raw=result.stdout.decode().strip().splitlines();rows=[]
            for line in raw:
                metadata,path=line.split('\t');mode,kind,blob=metadata.split();rows.append({'path':path,'mode':mode,'type':kind,'sha':blob})
            return self.response({'sha':oid,'truncated':False,'tree':rows})
        if route.startswith('/git/blobs/'):
            oid=route.rsplit('/',1)[1];result=subprocess.run(['git','-C',str(root),'cat-file','blob',oid],capture_output=True)
            if result.returncode:return self.response({},404)
            raw=result.stdout
            return self.response({'sha':oid,'encoding':'base64','content':base64.b64encode(raw).decode(),'size':len(raw)})
        if route=='/git/blobs' and method=='POST':
            raw=base64.b64decode(body['content']);oid=F.run_git(root,'hash-object','-w','--stdin',data=raw)
            if repo==T.PUBLIC and getattr(self,'lose_object',False):raise T.Unknown('fixture lost object response')
            return self.response({'sha':oid},201)
        if route=='/git/trees' and method=='POST':
            index=root.parent/'transport.index'
            env=__import__('os').environ.copy();env['GIT_INDEX_FILE']=str(index)
            if 'base_tree' not in body:
                rows=b''.join((row['mode']+' '+row['type']+' '+row['sha']+'\t'+row['path']).encode()+b'\0' for row in body['tree'])
                oid=subprocess.check_output(['git','-C',str(root),'mktree','-z'],input=rows,env=env).decode().strip()
                return self.response({'sha':oid},201)
            subprocess.run(['git','-C',str(root),'read-tree',body['base_tree']],env=env,check=True,capture_output=True)
            for row in body['tree']:
                subprocess.run(['git','-C',str(root),'update-index','--add','--cacheinfo',row['mode'],row['sha'],row['path']],env=env,check=True,capture_output=True)
            oid=subprocess.check_output(['git','-C',str(root),'write-tree'],env=env).decode().strip()
            return self.response({'sha':oid},201)
        if route=='/git/commits' and method=='POST':
            env=__import__('os').environ.copy()
            for kind in ('author','committer'):
                for field in ('name','email','date'):env['GIT_'+kind.upper()+'_'+field.upper()]=body[kind][field]
            args=['git','-C',str(root),'commit-tree',body['tree']]
            for parent in body['parents']:args+=['-p',parent]
            oid=subprocess.check_output(args,input=body['message'].encode(),env=env).decode().strip()
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

def adopt_current4(f):
    """Copy current actual package as 4; never relabel historical 3 blobs."""
    F.run_git(f.public,'checkout','-q','dev')
    for name in sorted(B.L.FILES):
        path=f.public/name;path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes((ROOT.parents[1]/name).read_bytes())
        if name in ('tool/version-control/classify','tool/version-control/release-preview'):
            F.run_git(f.public,'add',name);F.run_git(f.public,'update-index','--chmod=+x',name)
    manifest=b'format\t1\n'+b''.join(('file\t'+name+'\t'+T.digest((f.public/name).read_bytes())+'\n').encode() for name in sorted(B.L.FILES))
    (f.public/B.L.MANIFEST).write_bytes(manifest)
    F.run_git(f.public,'add','.');F.run_git(f.public,'commit','-qm','fixture current protocol4 source')
    F.run_git(f.public,'checkout','-q','master');F.run_git(f.public,'merge','--no-ff','-qm','fixture promotion4','dev')
    source=F.run_git(f.public,'rev-parse','HEAD')
    for approval in f.packages.values():approval['master']=source
    f.packages['4']={'public-repository':T.PUBLIC,'control':source,'master':source,
        'manifest':T.digest(manifest),'approval':F.X,'protocol':'4'}

class LegacyTenProof(unittest.TestCase):
    # INV repository/authenticated-release-transport
    # INV repository/fixture-git-isolation
    def test_original_ten_file_source_preflight_remains_literal(self):
        import tempfile
        preflight=load('legacy_ten_inventory',ROOT/'release-transport-preflight.py')
        source='fc2e1abdfc64ad3f2cc8156c49bc54f256c284ef'
        with tempfile.TemporaryDirectory(prefix='original-ten-transport-') as folder:
            repo=Path(folder);F.run_git(repo,'init','-q','-b','master')
            F.run_git(repo,'config','user.name','Fixture');F.run_git(repo,'config','user.email','fixture@example.invalid')
            for name in preflight.LEGACY_TEN+('tool/version-control/release-transport.manifest.tsv',):
                path=repo/name;path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes(B.L.git(ROOT.parents[1],'show',source+':'+name))
            F.run_git(repo,'add','.');F.run_git(repo,'commit','-qm','fixture literal original ten transport')
            head=F.run_git(repo,'rev-parse','HEAD');template=repo/'inputs.json'
            value=T.document((ROOT/'release-transport-template.json').read_bytes())
            value['transport-source']=head;value['transport-manifest']=T.digest((repo/'tool/version-control/release-transport.manifest.tsv').read_bytes())
            template.write_bytes(T.canonical(value))
            result=subprocess.run([sys.executable,'-I','-S','-B',str(repo/'tool/version-control/release-transport-preflight.py'),
                'preflight','--source',head,'--template',str(template)],capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertFalse(T.document(result.stdout)['enabled'])
            self.assertFalse((repo/'tool/version-control/release-public-objects.py').exists())

class StartProof(unittest.TestCase):
    # INV repository/authenticated-release-transport
    # INV repository/fixture-git-isolation
    def setUp(self):
        self.fixture=F.GlobalHistoryProof();self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
        f=self.fixture;adopt_current4(f)
        (f.operating/'config/operating.tsv').write_bytes(F.encode(dict(F.CONFIG,protocol='4')))
        (f.operating/'current/transcript.json').write_bytes(F.canonical(F.transcript('preview',candidate=None)))
        (f.operating/'current/batches.tsv').write_bytes(b'format\t1\n')
        fields=dict(F.loader.singletons(F.current_engine.index(F.current_engine.initial(),F.Z),F.loader.PROJECTION_FIELDS),
                    **{'index-kind':'global-1','ledger-digest':F.digest(F.canonical([]))})
        (f.operating/'current/index.tsv').write_bytes(F.encode(fields))
        self.head=f.commit(f.operating)
        self.connect()

    def connect(self):
        f=self.fixture
        import tempfile
        owned=tempfile.TemporaryDirectory(prefix='start-local-original-');self.addCleanup(owned.cleanup)
        self.local=Path(owned.name)/'objects.git'
        F.run_git(f.public,'clone','--bare','--no-local',str(f.operating),str(self.local))
        self.fake=Fake(f.public,f.operating,f.packages['4']['master'])
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
        plan=B.StartPlan(self.entry,f.public,self.local,F.encode(f.packages['4']),self.head)
        self.addCleanup(plan.close)
        return plan

    def test_empty_start_uses_original_records_and_global_projection(self):
        f=self.fixture;before=F.run_git(f.operating,'rev-parse','HEAD');plan=self.start()
        self.assertEqual(F.run_git(f.operating,'rev-parse','HEAD'),before)
        self.assertFalse(any(m!='GET' for m,_,_ in self.fake.calls))
        changes=plan.pending_changes
        first=dict((r[0],r[1]) for r in B.L.table(changes['history/000000000001.tsv']) if len(r)==2)
        claim=dict((r[0],r[1]) for r in B.L.table(changes['history/000000000002.tsv']) if len(r)==2)
        self.assertEqual(first['kind'],'batch-start');self.assertEqual(first['config-commit'],self.head)
        self.assertEqual(claim['operating-head'],self.head);self.assertEqual(claim['generation'],'1')
        self.assertEqual(claim['prior'],F.digest(changes['history/000000000001.tsv']))
        journal=T.Journal(self.api,plan,self.head);result=journal.publish(changes)
        snapshot=B.Snapshot(self.entry,f.public,self.local,F.encode(f.packages['4']),result,plan.tagger,[])
        self.addCleanup(snapshot.close)
        self.assertEqual(snapshot.state['stage'],'active');self.assertEqual(snapshot.state['owner']['job'],'5')
        self.assertFalse(any(p.endswith('/pulls') for _,p,_ in self.fake.calls))

    def test_completed_old_protocols_keep_literal_history_and_original_ledgers(self):
        f=self.fixture
        f.add_batch('1',F.X,True);f.add_batch('3',F.Y,True);f.save()
        (f.operating/'config/operating.tsv').write_bytes(F.encode(dict(F.CONFIG,protocol='4')))
        self.head=f.commit(f.operating)
        self.connect()
        old={p.name:p.read_bytes() for p in (f.operating/'history').iterdir()}
        plan=self.start();self.assertIn('history/000000000007.tsv',plan.pending_changes)
        result=T.Journal(self.api,plan,self.head).publish(plan.pending_changes)
        snapshot=B.Snapshot(self.entry,f.public,self.local,F.encode(f.packages['4']),result,plan.tagger,[])
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
        for changed in ({'enabled':'0'},{'workflow':'99'},{'actors':'99'},{'protocol':'2'},{'protocol':'3'}):
            (f.operating/'config/operating.tsv').write_bytes(F.encode(dict(dict(F.CONFIG,protocol='4'),**changed)))
            self.head=f.commit(f.operating);self.connect()
            with self.subTest(changed=changed),self.assertRaises(T.Refusal):self.start()
            self.assertFalse(any(m!='GET' for m,_,_ in self.fake.calls))
        (f.operating/'config/operating.tsv').write_bytes(F.encode(dict(F.CONFIG,protocol='4')))
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

    def test_distinct_stores_deliver_before_two_publications(self):
        f=self.fixture;plan=self.start();journal=T.Journal(self.api,plan,self.head)
        self.assertNotEqual(self.local.resolve(),f.operating.resolve())
        result=journal.publish(plan.pending_changes)
        self.assertEqual(F.run_git(self.local,'cat-file','-t',result),'commit')
        snapshot=B.Snapshot(self.entry,f.public,self.local,F.encode(f.packages['4']),result,plan.tagger,[])
        self.addCleanup(snapshot.close)
        second=T.Journal(self.api,snapshot,result)
        child=second.publish({'current/index.tsv':B.L.record_blob(self.local,result,'current/index.tsv')[1]})
        self.assertNotEqual(child,result)
        self.assertEqual(F.run_git(self.local,'cat-file','-t',child),'commit')
        self.assertEqual(snapshot.head,child);self.assertFalse(second.pending)
        self.assertFalse((self.local/'objects/info/alternates').exists())

    def test_local_delivery_failure_preserves_pending_and_original_head(self):
        from unittest.mock import patch
        plan=self.start();journal=T.Journal(self.api,plan,self.head)
        with patch.object(plan,'hydrate',side_effect=OSError('fixture disk refusal')):
            with self.assertRaises(T.Unknown):journal.publish(plan.pending_changes)
        self.assertTrue(journal.pending);self.assertEqual(journal.expected,self.head)
        self.assertEqual(plan.head,self.head);self.assertIsNotNone(plan.pending_changes)
        self.assertNotEqual(self.fake.head,self.head)
        with self.assertRaises(T.Refusal):journal.publish(plan.pending_changes)

    def test_remote_metadata_mismatch_fences_before_ref(self):
        plan=self.start();prospective=plan.validate_changes(plan.pending_changes)
        raw=next(raw for kind,sha,raw in prospective['objects'] if sha==prospective['head'])
        fields=B.O.commit_fields(raw);fields['author']=dict(fields['author'],name='unexpected actor')
        self.fake.responses[('POST','/repos/fixture/operating/git/commits')]=self.fake.response({'sha':prospective['head']},201)
        self.fake.responses[('GET','/repos/fixture/operating/git/commits/'+prospective['head'])]=self.fake.response(fields)
        journal=T.Journal(self.api,plan,self.head)
        with self.assertRaises(T.Refusal):journal.publish(plan.pending_changes)
        self.assertTrue(journal.pending);self.assertEqual(plan.head,self.head)
        self.assertFalse(any(m=='PATCH' for m,_,_ in self.fake.calls))

    def test_corrupt_retained_blob_cannot_clear_pending_after_remote_delivery(self):
        from unittest.mock import patch
        plan=self.start();original=plan.validate_changes
        def corrupt(changes):
            prospective=original(changes)
            rows=list(prospective['objects'])
            for i,(kind,sha,raw) in enumerate(rows):
                if kind=='blob':rows[i]=(kind,sha,raw+b'corrupt');break
            prospective['objects']=tuple(rows);return prospective
        journal=T.Journal(self.api,plan,self.head)
        with patch.object(plan,'validate_changes',side_effect=corrupt):
            with self.assertRaises(T.Unknown):journal.publish(plan.pending_changes)
        self.assertTrue(journal.pending);self.assertEqual(plan.head,self.head)
        self.assertNotEqual(self.fake.head,self.head)

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


class ObservedCandidateProof(unittest.TestCase):
    """Original production CLI and real disposable objects; synthetic API receipts only."""
    # INV repository/authenticated-release-transport
    # INV repository/production-release-qualification
    # INV repository/fixture-git-isolation
    def setUp(self,rules_transform=None):
        self.fixture=F.GlobalHistoryProof();self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
        f=self.fixture
        F.run_git(f.public,'checkout','-q','dev')
        (f.public/'seed').rename(f.public/'README.md')
        rules=('format\t1\nproduction\t1\n'
            'production-check\tgate\trepository\tpolicy-checks\trequired\t-\tfixture-tool\n'
            'production-check\tugate\tunixlike\tfixtures\trequired\t-\tfixture-tool\n'
            'production-check\twgate\twindows\tfixtures\trequired\t-\tfixture-tool\n'
            'production-check\tnot-selected\tunixlike\tfixtures\trequired\t-\tfixture-tool\n'
            'production-domain\tunixlike\tugate\nproduction-domain\twindows\twgate\n'
            'production-template\tunixlike\tshk95/configs-host-template\tugate\tnot-selected\n'
            'production-map\texact\tREADME.md\tgate\nproduction-map\tprefix\ttool/version-control/\tgate\n'
            'production-map\tprefix\t.github/\tgate\nproduction-map\tprefix\tunixlike/\tugate\n')
        if rules_transform is not None:rules=rules_transform(rules)
        (f.public/'tool/version-control/release-preview.rules').write_text(rules)
        workflow=f.public/'.github/workflows/ci.yml';workflow.parent.mkdir(parents=True,exist_ok=True)
        workflow.write_text('name: Fixture data only\n')
        manifest=f.public/F.loader.MANIFEST
        lines=manifest.read_text().splitlines()
        manifest.write_text('\n'.join([lines[0]]+['\t'.join(row[:2]+[T.digest((f.public/row[1]).read_bytes())])
            for line in lines[1:] for row in [line.split('\t')]])+'\n')
        F.run_git(f.public,'add','.');F.run_git(f.public,'commit','-qm','fixture reviewed production rules')
        F.run_git(f.public,'checkout','-q','master');F.run_git(f.public,'merge','--no-ff','-qm','fixture reviewed control','dev')
        self.master=F.run_git(f.public,'rev-parse','HEAD')
        f.packages['3']=dict(f.packages['3'],control=self.master,master=self.master,manifest=T.digest(manifest.read_bytes()))
        self.baseline_source=F.run_git(f.public,'rev-parse',self.master+'^2')
        annotation=f'Release-Format: 1\nDomain: unixlike\nVersion: 1.0.0\nSource: {self.baseline_source}\n'
        F.run_git(f.public,'tag','-a','unixlike-v1.0.0',self.baseline_source,'-F','-',data=annotation.encode())
        self.tag=F.run_git(f.public,'rev-parse','refs/tags/unixlike-v1.0.0')
        self.baseline=f'format\t1\nsemantic\tunixlike\t1.0.0\tunixlike-v1.0.0\t{self.tag}\n'.encode()
        F.run_git(f.public,'checkout','-q','dev')
        source=f.public/'unixlike/api/contract.json';source.parent.mkdir(parents=True,exist_ok=True)
        source.write_text('Synthetic contract data; no execution.\n')
        F.run_git(f.public,'add','.');F.run_git(f.public,'commit','-qm',
            'feat(unixlike): synthetic contract change\n\nRelease-Format: 1\nRelease-Domain: unixlike\n'
            'Release-Impact: patch\nRelease-Contracts: ugate\nRelease-Compatibility: compatible\n'
            'Release-Rationale: Synthetic fixture.\nRelease-Migration: none\n')
        self.dev=F.run_git(f.public,'rev-parse','HEAD');self.tree=F.run_git(f.public,'rev-parse','HEAD^{tree}')
        config=F.CONFIG
        try:
            F.CONFIG=dict(config,checks='gate,ugate,wgate')
            f.transcript_file.write_bytes(F.canonical(F.transcript('preview',candidate=None)))
            f.add_batch('3',F.X,False);f.save()
        finally:F.CONFIG=config
        self.fake=Fake(f.public,f.operating,self.master);self.fake.dev=self.dev
        self.api=T.Api(self.fake,'fixture/operating')
        self.runtime={'repository':T.PUBLIC,'ref':'refs/heads/master','event':'workflow_dispatch','run':4,'attempt':1,
            'job':5,'actor':3,'source':self.master,'environment':'fixture-controller','mode':'start','candidate':F.Z}
        self.trusted={'source':self.master,'workflow':2,'workflow-path':'.github/workflows/release-control-writer.yml',
            'repository-id':1,'actors':[3],'environment':'fixture-controller','job-name':'writer'}
        self.entry=T.Entry(self.api,self.trusted,self.runtime)
        self.requirements=[{'id':name,'name':'Required checks','app':15368,'workflow':7,'job':9,'tool':'fixture-tool',
            'source':self.dev,'attempt':1,'run':8,'workflow-path':'.github/workflows/ci.yml',
            'workflow-blob':F.run_git(f.public,'rev-parse',self.dev+':.github/workflows/ci.yml'),
            'tool-path':'tool/version-control/release-preview',
            'tool-blob':F.run_git(f.public,'rev-parse',self.dev+':tool/version-control/release-preview')}
            for name in ['ugate']]
        self.run={'id':8,'run_attempt':1,'head_sha':self.dev,'head_branch':'dev','event':'push','workflow_id':7,
            'repository':{'id':1},'head_repository':{'id':1},'status':'completed','conclusion':'success'}
        self.job={'id':9,'run_id':8,'name':'Required checks','head_sha':self.dev,'status':'completed',
            'conclusion':'success','html_url':'https://github.com/shk95/configs/actions/runs/8/job/9'}
        self.check={'id':10,'name':'Required checks','app':{'id':15368},'head_sha':self.dev,'status':'completed',
            'conclusion':'success','details_url':self.job['html_url']}
        ObservedEvidenceProof.bind_metadata(self)
        raw=subprocess.run(['git','-C',str(f.public),'cat-file','tag',self.tag],capture_output=True,check=True).stdout.decode('utf-8')
        header,_,message=raw.partition('\n\n')
        import re
        from datetime import datetime,timezone
        tagger=re.fullmatch(r'tagger (.+) <(.+)> ([0-9]+) ([+-][0-9]{4})',header.splitlines()[3])
        value={'sha':self.tag,'tag':'unixlike-v1.0.0','object':{'sha':self.baseline_source,'type':'commit'},
            'message':message,'tagger':{'name':tagger[1],'email':tagger[2],
            'date':datetime.fromtimestamp(int(tagger[3]),timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}}
        self.fake.responses[('GET','/repos/'+T.PUBLIC+'/git/tags/'+self.tag)]=self.fake.response(value)
        self.fake.calls.clear()

    def qualification(self,**change):
        body={'format':1,'control':self.master,'manifest':self.fixture.packages['3']['manifest'],
            'baselines':base64.b64encode(self.baseline).decode(),'baselines-digest':T.digest(self.baseline),
            'requirements-digest':T.digest(T.canonical(self.requirements))}
        body.update(change)
        return T.canonical(dict(body,binding=T.digest(T.canonical(body))))

    def snapshot(self,qualification=True):
        f=self.fixture
        s=B.Snapshot(self.entry,f.public,f.operating,F.encode(f.packages['3']),self.fake.head,
            {'name':'Release controller','email':'release-controller@example.invalid','date':'2026-10-01T00:00:00Z'},
            self.requirements,qualification=self.qualification() if qualification else None)
        self.addCleanup(s.close);return s

    def no_writes(self):self.assertFalse(any(m!='GET' for m,_,_ in self.fake.calls))

    def test_original_production_candidate_then_existing_evidence_full_replay(self):
        snapshot=self.snapshot();old=T.document((snapshot.batch/'transcript.json').read_bytes())
        changes=snapshot.propose_candidate();self.no_writes()
        event=F.parse(next(v for p,v in changes.items() if p.startswith('history/')),'event')
        self.assertEqual((event['dev'],event['master'],event['tree']),(self.dev,self.master,self.tree))
        self.assertEqual(event['classification'],'patch');self.assertEqual(event['versions'],'unixlike:1.0.1')
        self.assertEqual(event['rules'],T.digest((snapshot.package/'tool/version-control/release-preview.rules').read_bytes()))
        self.assertEqual(event['tool'],self.fixture.packages['3']['manifest'])
        self.assertEqual(event['baselines'],T.digest(self.baseline));self.assertEqual(event['selected'],'ugate')
        self.assertNotIn('release',event)
        proposed=T.document(changes['current/transcript.json']);self.assertEqual(proposed['checks'],old['checks'])
        self.assertEqual(proposed['source'][:-1],old['source']);self.assertEqual(set(proposed),set(old))
        head=T.Journal(self.api,snapshot,self.fake.head).publish(changes)
        self.assertIsNone(snapshot.candidate_binding)
        candidate=snapshot.state['candidate'];self.runtime['candidate']=T.digest(T.canonical(candidate))
        self.entry=T.Entry(self.api,self.trusted,self.runtime)
        restored=self.snapshot();self.assertEqual(restored.head,head);self.assertEqual(restored.state['stage'],'candidate')
        evidence=restored.propose_evidence();T.Journal(self.api,restored,self.fake.head).publish(evidence)
        self.assertEqual(self.snapshot().state['stage'],'validated')

    def test_observed_replacement_preserves_history_and_invalidates_actual_approval(self):
        s=self.snapshot();T.Journal(self.api,s,self.fake.head).publish(s.propose_candidate())
        self.runtime['candidate']=T.digest(T.canonical(s.state['candidate']))
        self.entry=T.Entry(self.api,self.trusted,self.runtime)
        s=self.snapshot();T.Journal(self.api,s,self.fake.head).publish(s.propose_evidence())
        self.runtime['mode']='approve';self.entry=T.Entry(self.api,self.trusted,self.runtime)
        s=self.snapshot();request={k:self.runtime[k] for k in ('mode','actor','run','attempt','ref','candidate')}
        T.Journal(self.api,s,self.fake.head).publish(s.transition(request))
        self.assertIsNotNone(s.state['approval'])
        old={p.name:p.read_bytes() for p in (self.fixture.operating/'history').iterdir()}
        self.runtime['mode']='wake';self.entry=T.Entry(self.api,self.trusted,self.runtime)
        s=self.snapshot();T.Journal(self.api,s,self.fake.head).publish(s.propose_candidate())
        self.assertEqual(s.state['promotion-generation'],'2');self.assertIsNone(s.state['approval'])
        self.assertEqual(s.state['evidence'],[])
        for name,raw in old.items():self.assertEqual((self.fixture.operating/'history'/name).read_bytes(),raw)

    def test_missing_custody_bad_binding_and_changed_baseline_refuse(self):
        s=self.snapshot(False)
        with self.assertRaises(T.Refusal):s.propose_candidate()
        for change in ({'baselines-digest':F.Z},{'requirements-digest':F.Z},{'manifest':F.Z}):
            with self.subTest(change=change):
                s=self.snapshot();s.qualification=s.qualification_bytes=self.qualification(**change)
                with self.assertRaises(T.Refusal):s.propose_candidate()
        self.no_writes()

    def test_original_baseline_tag_api_mismatch_refuses(self):
        key=('GET','/repos/'+T.PUBLIC+'/git/tags/'+self.tag)
        value=T.document(self.fake.responses[key][2]);value['object']['sha']=self.dev
        self.fake.responses[key]=self.fake.response(value)
        with self.assertRaises(T.Refusal):self.snapshot().propose_candidate()
        self.no_writes()

    def test_missing_duplicate_extra_or_wrong_tool_trust_refuses(self):
        original=copy.deepcopy(self.requirements)
        for values in ([],original*2,[dict(original[0],id='foreign')],[dict(original[0],tool='foreign-tool')]):
            with self.subTest(values=values):
                self.requirements=values
                with self.assertRaises(T.Refusal):self.snapshot().propose_candidate()
        self.no_writes()

    def test_failed_or_changed_actual_receipts_refuse(self):
        for field,value in (('conclusion','failure'),('run_attempt',2),('head_sha',self.master)):
            with self.subTest(field=field):
                run=dict(self.run,**{field:value})
                self.fake.responses[('GET','/repos/'+T.PUBLIC+'/actions/runs/8')]=self.fake.response(run)
                with self.assertRaises(T.Refusal):self.snapshot().propose_candidate()
        self.no_writes()

    def test_publishing_rechecks_actual_receipts_and_fences(self):
        s=self.snapshot();changes=s.propose_candidate()
        self.run['run_attempt']=2;ObservedEvidenceProof.bind_metadata(self)
        with self.assertRaises(T.Refusal):T.Journal(self.api,s,self.fake.head).publish(changes)
        self.assertTrue(s.proposal_fenced);self.no_writes()

    def test_publication_rechecks_changed_input_and_stop(self):
        for reason in ('input','source','stop'):
            with self.subTest(reason=reason):
                s=self.snapshot();changes=s.propose_candidate()
                if reason=='input':s.qualification=b'{}'
                elif reason=='source':self.fake.dev=self.master
                else:
                    f=self.fixture;(f.operating/'control/stop.tsv').write_bytes(F.encode(dict(F.STOP,stop='1')))
                    self.fake.head=f.commit(f.operating)
                with self.assertRaises(T.Refusal):T.Journal(self.api,s,s.head).publish(changes)
                if reason!='stop':self.assertTrue(s.proposal_fenced)
                self.assertIsNotNone(s.pending_changes);self.no_writes()
                if reason=='source':self.fake.dev=self.dev
                if reason=='stop':break

    def test_source_only_impact_refuses_and_actual_noop_is_empty(self):
        self.fake.dev=self.master
        self.assertEqual(self.snapshot().propose_candidate(),{})
        self.no_writes()
        F.run_git(self.fixture.public,'checkout','-q',self.master)
        (self.fixture.public/'README.md').write_text('source-only change\n')
        F.run_git(self.fixture.public,'add','README.md');F.run_git(self.fixture.public,'commit','-qm','fixture source only')
        self.dev=self.fake.dev=F.run_git(self.fixture.public,'rev-parse','HEAD')
        self.requirements=[dict(self.requirements[0],id='gate',source=self.dev)]
        self.run['head_sha']=self.job['head_sha']=self.check['head_sha']=self.dev
        ObservedEvidenceProof.bind_metadata(self)
        with self.assertRaisesRegex(T.Refusal,'unrepresentable-candidate-impact'):self.snapshot().propose_candidate()
        self.no_writes()

    def test_mixed_structural_refusal_and_unsupported_review_cannot_qualify(self):
        for transform,reason in (
            (lambda rules:rules.replace('ugate\tnot-selected','ugate\tunknown-trigger'),'candidate-qualification-refusal'),
            (lambda rules:rules.replace('ugate\tunixlike\tfixtures','ugate\tunixlike\treview'),'unsupported-candidate-check')):
            with self.subTest(reason=reason):
                self.doCleanups();self.setUp(transform)
                with self.assertRaisesRegex(T.Refusal,reason):self.snapshot().propose_candidate()
                self.no_writes()

    def test_final_selection_or_version_change_refuses_before_projection(self):
        from unittest.mock import patch
        for field in ('checks','domains'):
            with self.subTest(field=field):
                s=self.snapshot();preview=s.candidate_preview
                def changed(*args):
                    code,value=preview(*args)
                    if code==0:
                        if field=='checks':value['checks'][0]['id']='foreign'
                        else:value['domains'][0]['next_version']='9.0.0'
                    return code,value
                with patch.object(s,'candidate_preview',changed),self.assertRaisesRegex(T.Refusal,'changed-candidate-qualification'):
                    s.propose_candidate()
                self.no_writes()

    def test_original_bootstrap_record_binding_and_corruption_refuse(self):
        f=self.fixture;record=f.public/'records/bootstrap.tsv';record.parent.mkdir()
        raw=f'format\t1\ndomain\tunixlike\nsource\t{self.dev}\nversion\t1.0.0\ncontracts\tugate\n'.encode()
        record.write_bytes(raw);F.run_git(f.public,'add','records/bootstrap.tsv')
        F.run_git(f.public,'commit','-qm','fixture separate reviewed record')
        head=F.run_git(f.public,'rev-parse','HEAD')
        self.baseline=f'format\t1\nbootstrap\tunixlike\t{self.dev}\t{head}\trecords/bootstrap.tsv\n'.encode()
        s=self.snapshot();roots=s.qualification_objects(s.qualification_input())
        self.assertIn(head,roots);self.assertIn(self.dev,roots)
        # Independent record binding works; this package supplies no bootstrap review lane.
        with self.assertRaises(T.Refusal):s.propose_candidate()
        blob=F.run_git(f.public,'rev-parse',head+':records/bootstrap.tsv')
        value={'sha':blob,'encoding':'base64','content':base64.b64encode(raw+b'foreign').decode()}
        self.fake.responses[('GET','/repos/'+T.PUBLIC+'/git/blobs/'+blob)]=self.fake.response(value)
        with self.assertRaises(T.Refusal):self.snapshot().propose_candidate()
        self.no_writes()

    def test_owned_original_preview_does_not_execute_candidate_or_inherit_credentials(self):
        s=self.snapshot();comparison={'dev':self.dev,'master':self.master,'tree':self.tree}
        baseline,roots=s.candidate_context(comparison,s.state)
        import os
        from unittest.mock import patch
        calls=[];run=B.subprocess.run
        def observed(command,**kwargs):
            if command[0]=='sh':
                env=kwargs['env'];self.assertNotIn('GH_TOKEN',env);self.assertNotIn('GIT_CONFIG_COUNT',env)
                self.assertFalse((Path(kwargs['cwd'])/'unixlike').exists())
                calls.append(command)
            return run(command,**kwargs)
        before=F.run_git(self.fixture.public,'status','--porcelain')
        with patch.dict(os.environ,{'GH_TOKEN':'synthetic-sentinel','GIT_CONFIG_COUNT':'1','GIT_CONFIG_KEY_0':'alias.foo','GIT_CONFIG_VALUE_0':'!false'}),patch.object(B.subprocess,'run',observed):
            code,value=s.candidate_preview(comparison,baseline,roots,b'format\t1\n')
        self.assertEqual(code,1);self.assertEqual(value['reasons'],['missing-required-evidence'])
        self.assertEqual(len(calls),1);self.assertEqual(F.run_git(self.fixture.public,'status','--porcelain'),before)
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

class TypedCandidateProof(unittest.TestCase):
    # INV repository/typed-production-receipt-custody
    # INV repository/authenticated-release-transport
    # INV repository/fixture-git-isolation
    def setUp(self):
        self.o=ObservedCandidateProof();self.addCleanup(self.o.doCleanups)
        def reviewed(rules):
            root=self.o.fixture.public
            (root/B.R.PATH).parent.mkdir(parents=True,exist_ok=True)
            (root/B.R.PATH).write_bytes(B.R.workflow(True))
            (root/B.R.POLICY_PATH).write_bytes(T.canonical(B.R.POLICY))
            return rules.replace('ugate\tunixlike\tfixtures','ugate\tunixlike\treview')
        self.o.setUp(reviewed);o=self.o;f=o.fixture;o.requirements=[]
        a={'format':1,'source':o.master,'public-repository-id':1,'review-workflow-id':72,
            'review-workflow-path':B.R.PATH,'review-workflow-blob':F.run_git(f.public,'rev-parse',o.master+':'+B.R.PATH),
            'review-job':B.R.JOB,'review-environment-id':74,'review-environment':B.R.ENVIRONMENT,'reviewer':B.R.REVIEWER}
        p=[{'id':'ugate','kind':'review','domain':'unixlike','lane':'review','tool':'fixture-tool'}]
        self.a=a;self.p=p
        probe=o.snapshot();_,diag=probe.candidate_preview({'dev':o.dev,'master':o.master,'tree':o.tree},o.baseline,
            probe.qualification_objects(o.baseline),b'format\t1\n')
        c=B.R.Collector(T.canonical(a),T.canonical(p),public=None)
        scope=c.scope(probe,{'dev':o.dev,'master':o.master,'tree':o.tree},o.baseline,diag['checks'])
        packet={'format':1,'scope':scope,'authority':{'source':o.master,'workflow-blob':a['review-workflow-blob'],
            'workflow-path':B.R.PATH,'job':B.R.JOB,'environment':B.R.ENVIRONMENT,'public-repository-id':1,
            'workflow-id':72,'environment-id':74,'reviewer':B.R.REVIEWER},
            'claims':[dict(p[0],source=o.dev,records=['reviewed'],statement='Reviewed synthetic public contract.')],
            'raw-records':[{'id':'reviewed','kind':'review','source':o.dev,'platform':None,'tool':'fixture-tool',
                'command':[],'lane':'review','result':'verified','content':base64.b64encode(b'synthetic original review').decode(),
                'sha256':T.digest(b'synthetic original review')}],'template-pair':None}
        digest=T.digest(T.canonical(packet));path=f.operating/('review/packets/'+digest+'.json');path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(T.canonical(packet))
        (f.operating/'review/production-index.json').write_bytes(T.canonical({'format':1,'scope-digest':T.digest(T.canonical(scope)),
            'entries':[{'id':'ugate','packet':digest,'run':71,'attempt':1,'job':75}]}))
        F.run_git(f.operating,'add','.');F.run_git(f.operating,'commit','-qm','fixture private reviewed packet')
        o.fake.head=F.run_git(f.operating,'rev-parse','HEAD');F.run_git(f.operating,'update-ref','refs/heads/operations',o.fake.head)
        helper=load('typed_fixture_helpers',ROOT/'test-production-receipt.py')
        self.public=helper.FakePublic(o.master,a['review-workflow-blob'],digest)
        for route in ('/actions/runs/71','/actions/runs/71/attempts/1'):
            self.public.values[route]['repository']['id']=1;self.public.values[route]['head_repository']['id']=1
        self.c=B.R.Collector(T.canonical(a),T.canonical(p),public=self.public)
    def snapshot(self):
        o=self.o;f=o.fixture
        s=B.Snapshot(o.entry,f.public,f.operating,F.encode(f.packages['3']),o.fake.head,
            {'name':'Release controller','email':'release-controller@example.invalid','date':'2026-10-01T00:00:00Z'},
            o.requirements,qualification=o.qualification(),receipts=self.c)
        self.addCleanup(s.close);return s
    def test_typed_candidate_evidence_original_global_replay(self):
        o=self.o;s=self.snapshot();changes=s.propose_candidate();o.no_writes()
        T.Journal(o.api,s,o.fake.head).publish(changes)
        o.runtime.update(mode='wake',candidate=T.digest(T.canonical(s.state['candidate'])))
        o.entry=T.Entry(o.api,o.trusted,o.runtime)
        s=self.snapshot();T.Journal(o.api,s,o.fake.head).publish(s.propose_evidence())
        self.assertEqual(s.state['stage'],'validated');self.assertEqual(s.state['evidence'][0][7:10],['71','1','75'])
        self.assertEqual(self.snapshot().state['stage'],'validated')
    def test_pending_custody_movement_fences_journal(self):
        o=self.o;s=self.snapshot();changes=s.propose_candidate()
        self.public.values['/actions/runs/71/approvals'][0]['comment']='review:'+'b'*64
        with self.assertRaises((T.Refusal,B.R.T.Refusal)):
            T.Journal(o.api,s,o.fake.head).publish(changes)
        o.no_writes()

class PublicObjectProof(unittest.TestCase):
    # INV repository/public-refresh-object-transport
    # INV repository/fixture-git-isolation
    connect=StartProof.connect
    start=StartProof.start
    def setUp(self):
        StartProof.setUp(self)
        self.original=F.ImmutableRefreshObjects();self.original.setUp();self.addCleanup(self.original.doCleanups)
        f=self.fixture;o=self.original
        # Transfer only disposable original fixture objects, without alternates.
        packed=subprocess.check_output(['git','-C',str(o.repo),'pack-objects','--quiet','--stdout','--revs'],input=(o.candidate['base']+'\n').encode())
        subprocess.run(['git','-C',str(f.public),'index-pack','--stdin'],input=packed,capture_output=True,check=True)
        plan=self.start();head=T.Journal(self.api,plan,self.head).publish(plan.pending_changes)
        self.snapshot=B.Snapshot(self.entry,f.public,self.local,F.encode(f.packages['4']),head,plan.tagger,[])
        self.addCleanup(self.snapshot.close)
        batch=self.snapshot.state['batch'];o.candidate['batch']=batch;o.candidate['branch']=F.current_adapter.refresh_branch(batch)
        o.context['branch']['batch']=batch;o.context['branch']['branch']=o.candidate['branch']
        o.context['construction']['inputs']['batch']=batch;o.refresh_digest()
        transcript=T.document(self.snapshot.original_transcript)
        transcript['refresh']={'revisions':[o.context],'current':o.context}
        transcript['protection']=copy.deepcopy(F.PROTECTION)
        transcript['source'].append(dict(transcript['source'][-1],candidate=T.digest(T.canonical(o.candidate)),mode='preview'))
        fields={'kind':'refresh-result','payload':T.canonical({'status':'changed','candidate':o.candidate}).decode()}
        T.Journal(self.api,self.snapshot,head).publish(self.snapshot.propose_event(fields,transcript))
        self.entry.runtime['candidate']=T.digest(T.canonical(o.candidate))
        self.plans=o.plans();self.journal=T.Journal(self.api,self.snapshot,self.snapshot.head)
        self.executor=T.Executor(self.entry,self.journal,self.snapshot,public_read=self.fake)

    def intent(self,oid,payload):
        fields={'kind':'intent','payload':T.canonical(payload).decode(),'operation':[[oid,'refresh-object',T.digest(T.canonical(payload)),
            '1','intent','-','-']]}
        self.journal.publish(self.snapshot.propose_event(fields,T.document(self.snapshot.original_transcript)))
        return self.snapshot.plan(oid)

    def test_four_original_effects_then_restart_replay(self):
        for oid,payload in self.plans:
            plan=self.intent(oid,payload)
            self.assertEqual(self.executor.perform(plan),'applied')
            raw=B.O.raw_base64(payload['raw'])
            self.assertEqual(subprocess.check_output(['git','-C',str(self.fake.public),'cat-file',payload['object-type'],payload['object']]),raw)
            self.assertEqual(self.snapshot.state['operations'][oid]['state'],'observed')
        branch=dict(self.original.candidate,repository=T.PUBLIC)
        oid=F.current_adapter.refresh_operation_id('refresh-branch',branch)
        fields={'kind':'intent','payload':T.canonical(branch).decode(),'operation':[[oid,'refresh-branch',T.digest(T.canonical(branch)),'1','intent','-','-']]}
        self.journal.publish(self.snapshot.propose_event(fields,T.document(self.snapshot.original_transcript)))
        self.fake.dev=branch['base']
        self.assertEqual(self.executor.perform(self.snapshot.plan(oid)),'applied')
        self.assertEqual(self.fake.refresh_heads[branch['branch']],branch['head'])
        f=self.fixture
        restored=B.Snapshot(self.entry,f.public,self.local,F.encode(f.packages['4']),self.snapshot.head,self.snapshot.tagger,[])
        self.addCleanup(restored.close)
        self.assertEqual(restored.state,self.snapshot.state)
        calls=[(m,p) for m,p,_ in self.fake.calls if m=='POST' and p.startswith('/repos/shk95/configs/git/')]
        self.assertEqual([p.rsplit('/',1)[1] for _,p in calls],['blobs','trees','trees','commits','refs'])
        self.assertFalse(any('recursive' in p for m,p,_ in self.fake.calls if m=='GET' and p.startswith('/repos/shk95/configs/git/trees/') and '?' not in p))

    def test_missing_prerequisite_and_unknown_read_refuse_before_public_write(self):
        with self.assertRaises(T.Refusal):self.snapshot.object_dependencies(self.plans[1][1],B.O.Reader(self.fake))
        branch=dict(self.original.candidate,repository=T.PUBLIC)
        oid=F.current_adapter.refresh_operation_id('refresh-branch',branch)
        fields={'kind':'intent','payload':T.canonical(branch).decode(),'operation':[[oid,'refresh-branch',T.digest(T.canonical(branch)),'1','intent','-','-']]}
        with self.assertRaises(T.Refusal):self.snapshot.propose_event(fields,T.document(self.snapshot.original_transcript))
        oid,payload=self.plans[1]
        with self.assertRaises(T.Refusal):self.intent(oid,payload)
        self.assertFalse(any(m=='POST' and p.startswith('/repos/shk95/configs/git/') for m,p,_ in self.fake.calls))

    def test_masked_404_fences_without_write_or_retry(self):
        oid,payload=self.plans[0];plan=self.intent(oid,payload)
        self.fake.responses[('GET','/repos/shk95/configs')]=self.fake.response({},404)
        with self.assertRaises(T.Unknown):self.executor.perform(plan)
        self.assertTrue(self.executor.unknown)
        with self.assertRaises(T.Refusal):self.executor.perform(plan)
        self.assertFalse(any(m=='POST' and p.startswith('/repos/shk95/configs/git/') for m,p,_ in self.fake.calls))

    def test_lost_post_response_is_independently_proved_once(self):
        oid,payload=self.plans[0];plan=self.intent(oid,payload);self.fake.lose_object=True
        self.assertEqual(self.executor.perform(plan),'applied')
        self.assertEqual(sum(m=='POST' and p=='/repos/shk95/configs/git/blobs' for m,p,_ in self.fake.calls),1)
        self.assertEqual(self.snapshot.state['operations'][oid]['state'],'observed')

    def test_restart_reconciles_original_intent_without_repeating_post(self):
        from unittest.mock import patch
        oid,payload=self.plans[0];plan=self.intent(oid,payload)
        with patch.object(self.snapshot,'observation',side_effect=T.Refusal('fixture interrupted observation')):
            with self.assertRaises(T.Unknown):self.executor.perform(plan)
        self.assertTrue(self.executor.unknown)
        f=self.fixture;restored=B.Snapshot(self.entry,f.public,self.local,F.encode(f.packages['4']),self.snapshot.head,self.snapshot.tagger,[])
        self.addCleanup(restored.close);journal=T.Journal(self.api,restored,restored.head)
        resumed=T.Executor(self.entry,journal,restored,public_read=self.fake)
        before=sum(m=='POST' and p.startswith('/repos/shk95/configs/git/') for m,p,_ in self.fake.calls)
        resumed.recover(restored.plan(oid))
        self.assertEqual(restored.state['operations'][oid]['state'],'observed')
        self.assertEqual(sum(m=='POST' and p.startswith('/repos/shk95/configs/git/') for m,p,_ in self.fake.calls),before)

    def test_post_ack_without_independent_object_proof_fences(self):
        oid,payload=self.plans[0];plan=self.intent(oid,payload)
        self.fake.responses[('POST','/repos/shk95/configs/git/blobs')]=self.fake.response({'sha':payload['object']},201)
        with self.assertRaises(T.Unknown):self.executor.perform(plan)
        self.assertTrue(self.executor.unknown)
        self.assertEqual(self.snapshot.state['operations'][oid]['state'],'intent')
        self.assertFalse(self.fake.refresh_heads)
        with self.assertRaises(T.Refusal):self.executor.perform(plan)

class TypedPublicProof(unittest.TestCase):
    # INV repository/public-refresh-object-transport
    # INV repository/fixture-git-isolation
    def setUp(self):
        self.fixture=F.ImmutableRefreshObjects();self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
        self.fake=Fake(self.fixture.repo,self.fixture.repo,F.H)
        self.reader=B.O.Reader(self.fake)
    def test_original_signed_commit_and_exact_direct_trees(self):
        for row in self.fixture.context['construction']['originals']:
            self.assertTrue(self.reader.prove(row['type'],row['sha'],self.fixture.raw(row)))
        self.assertTrue(all('?' not in p for _,p,_ in self.fake.calls))
    def test_generated_commit_and_strict_date_roundtrip(self):
        row=self.fixture.context['construction']['objects'][-1]
        self.assertTrue(self.reader.prove('commit',row['sha'],self.fixture.raw(row),True))
        for date in ('2026-02-30T00:00:00Z','2026-10-04T00:00:00+00:00','2026-10-04T24:00:00Z'):
            with self.subTest(date=date),self.assertRaises(B.O.Refusal):B.O.date_epoch(date)
        with self.assertRaises(B.O.Refusal):B.O.commit_fields(self.fixture.raw(row).replace(b'+0000',b'+0900'),True)
    def test_wrong_typed_complete_proof_is_not_absence(self):
        for row in self.fixture.context['construction']['originals']:
            path='/repos/shk95/configs/git/'+row['type']+'s/'+row['sha']
            _,_,raw=self.fake.request('GET',path,None);value=T.document(raw)
            variants=[dict(value,sha='f'*40)]
            if row['type']=='blob':variants+=[dict(value,size=True),dict(value,content='AA==')]
            elif row['type']=='tree':variants+=[dict(value,truncated=True),dict(value,tree=value['tree'][:-1])]
            else:variants+=[dict(value,message='wrong'),dict(value,parents=[{'sha':F.H}])]
            for changed in variants:
                self.fake.responses[('GET',path)]=self.fake.response(changed)
                with self.subTest(kind=row['type'],changed=changed),self.assertRaises(B.O.Refusal):self.reader.prove(row['type'],row['sha'],self.fixture.raw(row))
            self.fake.responses.pop(('GET',path))
    def test_status_redirect_base64_and_plumbing_bounds(self):
        row=self.fixture.context['construction']['originals'][-1];path='/repos/shk95/configs/git/blobs/'+row['sha']
        for status,headers in ((403,{}),(429,{}),(500,{}),(302,{'location':'https://foreign.invalid'}),(200,{'link':'next'})):
            self.fake.responses[('GET',path)]=(status,headers,b'{}')
            with self.assertRaises(B.O.Refusal):self.reader.prove('blob',row['sha'],self.fixture.raw(row))
        for raw in ('AA=','AB==','AA==\r\n'):
            with self.assertRaises(B.O.Refusal):B.O.raw_base64(raw)
        with self.assertRaises(B.O.Refusal):B.O.bounded_git(self.fixture.repo,['cat-file','blob',row['sha']],B.L.runtime_environment(__import__('os').environ),limit=1)

    def test_qualified_absence_and_moving_identity_are_distinct(self):
        original=self.fixture.context['construction']['originals'][-1]
        target=b'not created remote original';sha=B.O.oid('blob',target)
        reference=(original['sha'],self.fixture.raw(original))
        self.assertFalse(self.reader.qualified('blob',sha,target,reference))
        path='/repos/shk95/configs/git/blobs/'+sha
        self.fake.mutate[('GET',path)]=lambda:self.fake.responses.update({('GET','/repos/shk95/configs'):self.fake.response({'id':2,'full_name':T.PUBLIC,'private':False})})
        with self.assertRaises(B.O.Refusal):B.O.Reader(self.fake).qualified('blob',sha,target,reference)
        for method,path,body in (('POST','/repos/shk95/configs/git/blobs',{}),('GET','/repos/foreign/repo',None),('GET','/repos/shk95/configs/git/trees/'+F.H+'?recursive=0',None)):
            with self.assertRaises(B.O.Refusal):B.O.Anonymous().request(method,path,body)

if __name__=='__main__':unittest.main()
