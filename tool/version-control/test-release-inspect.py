"""Public fake reads and disposable Git; no credential or network access."""
# INV repository/authenticated-release-transport
# INV repository/release-inspection-without-authority
# INV repository/fixture-git-isolation
import contextlib
import copy
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parent
def load(path):
    spec=importlib.util.spec_from_file_location('public_inspector',path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result
M=load(ROOT/'release-inspect.py')
S='a'*40

class Fake:
    def __init__(self):
        self.calls=[];self.responses={}
        self.values={22:self.record(22,88,'in_progress'),11:self.record(11,99,'completed')}
        self.workflows={88:M.WORKFLOW,99:'.github/workflows/release-credential-check.yml'}
        self.jobs={22:[self.job(22,220,M.JOB,'in_progress')],
                   11:[self.job(11,110,'validate-operating-credential','completed')]}
        self.master=S
    def record(self,run,workflow,status):
        return {'id':run,'run_attempt':1,'head_sha':S,'head_branch':'master','event':'workflow_dispatch',
            'workflow_id':workflow,'repository':{'id':M.REPOSITORY},'actor':{'id':M.ACTOR},
            'triggering_actor':{'id':M.ACTOR},'status':status}
    def job(self,run,job,name,status):
        return {'id':job,'run_id':run,'head_sha':S,'name':name,'status':status}
    def get(self,path):
        self.calls.append(path)
        if path in self.responses:return copy.deepcopy(self.responses[path])
        if path=='/git/ref/heads/master':return {'object':{'sha':self.master}}
        if path.startswith('/actions/workflows/'):
            key=int(path.rsplit('/',1)[1]);return {'id':key,'path':self.workflows[key]}
        run=int(path.split('/')[3])
        if '/jobs?' in path:return {'total_count':len(self.jobs[run]),'jobs':copy.deepcopy(self.jobs[run])}
        return copy.deepcopy(self.values[run])

class InspectorProof(unittest.TestCase):
    # INV repository/authenticated-release-transport
    # INV repository/release-inspection-without-authority
    def setUp(self):
        self.api=Fake();self.sleeps=[];self.ancestors=[]
        self.env={'GITHUB_ACTIONS':'true','GITHUB_SERVER_URL':'https://github.com','GITHUB_API_URL':'https://api.github.com',
            'GITHUB_REPOSITORY':M.PUBLIC,'GITHUB_REF':'refs/heads/master','GITHUB_EVENT_NAME':'workflow_dispatch',
            'GITHUB_JOB':M.JOB,'GITHUB_ACTOR_ID':str(M.ACTOR),'GITHUB_REPOSITORY_ID':str(M.REPOSITORY),
            'GITHUB_SHA':S,'GITHUB_RUN_ID':'22','GITHUB_RUN_ATTEMPT':'1',
            'CONFIGS_INSPECT_RUN':'11','CONFIGS_INSPECT_ATTEMPT':'1','CONFIGS_INSPECT_MODE':'inspect'}
    def observe(self,sleep=None):
        return M.observe(self.env,self.api,lambda a,b:self.ancestors.append((a,b)),sleep or self.sleeps.append)
    def test_terminal_receipt_has_no_ownership_approval_or_private_data(self):
        self.env.update(CONFIGS_RELEASE_TOKEN='private-token',CONFIGS_RELEASE_OPERATING_REPOSITORY='private-connection')
        value=self.observe();self.assertTrue(value['terminal'])
        self.assertFalse(value['ownership']);self.assertFalse(value['approval']);self.assertFalse(value['operating_certification'])
        self.assertNotIn('private',json.dumps(value));self.assertEqual(self.ancestors,[(S,S)])
        self.assertFalse(self.sleeps)
    def test_runtime_ref_actor_repository_event_and_input_refuse_before_reads(self):
        for key,bad in [('GITHUB_REF','refs/heads/dev'),('GITHUB_ACTOR_ID','9'),('GITHUB_EVENT_NAME','pull_request'),
                        ('GITHUB_REPOSITORY','foreign/repo'),('GITHUB_SHA','0'*40)]:
            env=dict(self.env);env[key]=bad;api=Fake()
            with self.subTest(key=key),self.assertRaises(M.Refusal):M.observe(env,api)
            self.assertEqual(api.calls,[])
        for key,bad in [('CONFIGS_INSPECT_RUN','https://private.invalid'),('CONFIGS_INSPECT_ATTEMPT','0'),
                        ('CONFIGS_INSPECT_MODE','cancel')]:
            env=dict(self.env);env[key]=bad
            with self.subTest(key=key),self.assertRaises(M.Refusal):M.observe(env,Fake())
    def test_foreign_target_source_actor_event_workflow_refuses(self):
        for key,bad in [('head_branch','dev'),('event','pull_request'),('actor',{'id':9}),
                        ('triggering_actor',{'id':9}),('repository',{'id':9}),('head_sha','invalid')]:
            api=Fake();api.values[11][key]=bad
            with self.subTest(key=key),self.assertRaises(M.Refusal):M.observe(self.env,api,lambda a,b:None)
        self.api.workflows[99]='.github/workflows/ci.yml'
        with self.assertRaises(M.Refusal):self.observe()
    def test_latest_attempt_and_exact_attempt_must_match(self):
        self.api.values[11]['run_attempt']=2
        with self.assertRaises(M.Refusal):self.observe()
        self.api=Fake();self.api.responses['/actions/runs/11/attempts/1']=dict(self.api.values[11],run_attempt=2)
        with self.assertRaises(M.Refusal):self.observe()
    def test_mixed_missing_or_foreign_jobs_never_prove_terminal(self):
        for jobs in ([],[self.api.job(11,110,'foreign','completed')],
                     [self.api.job(11,110,'validate-operating-credential','in_progress')],
                     self.api.jobs[11]*2):
            self.api=Fake();self.api.jobs[11]=jobs
            with self.subTest(jobs=jobs),self.assertRaises(M.Refusal):self.observe()
    def test_queued_run_without_jobs_is_nonterminal_observation(self):
        self.api.values[11]['status']='queued';self.api.jobs[11]=[]
        value=self.observe();self.assertFalse(value['terminal']);self.assertEqual(value['status'],'queued')
    def test_wait_is_finite_and_timeout_grants_no_authority(self):
        self.env['CONFIGS_INSPECT_MODE']='wait';self.api.values[11]['status']='in_progress'
        self.api.jobs[11][0]['status']='in_progress'
        value=self.observe();self.assertEqual(self.sleeps,[2]*5)
        self.assertFalse(value['terminal']);self.assertTrue(value['bounded_wait_finished']);self.assertFalse(value['ownership'])
        self.assertEqual(len(self.ancestors),6);self.assertLess(len(self.api.calls),50)
    def test_wait_observes_actual_completion_and_refuses_moving_attempt_source_or_job(self):
        self.env['CONFIGS_INSPECT_MODE']='wait'
        def active():
            self.api=Fake();self.api.values[11]['status']='in_progress';self.api.jobs[11][0]['status']='in_progress'
        active()
        def finish(_):self.api.values[11]['status']='completed';self.api.jobs[11][0]['status']='completed'
        self.assertTrue(self.observe(finish)['terminal'])
        for change in ('attempt','source','job','workflow','master'):
            active()
            def mutate(_,change=change):
                if change=='attempt':self.api.values[11]['run_attempt']=2
                elif change=='source':self.api.values[11]['head_sha']='b'*40
                elif change=='job':self.api.jobs[11][0]['id']=999
                elif change=='workflow':self.api.workflows[99]='.github/workflows/release-control-writer.yml';self.api.jobs[11][0]['name']='writer'
                else:self.api.master='b'*40
            with self.subTest(change=change),self.assertRaises(M.Refusal):self.observe(mutate)
    def test_unapproved_source_ancestry_and_private_errors_are_generic(self):
        def refuse(a,b):raise M.Refusal('private source detail')
        out=io.StringIO();err=io.StringIO()
        with contextlib.redirect_stdout(out),contextlib.redirect_stderr(err):
            self.assertEqual(M.main(self.env,lambda:self.api,refuse),1)
        self.assertEqual(out.getvalue(),'');self.assertEqual(err.getvalue(),'public release inspection: refused\n')
    def test_http_only_public_get_no_authorization_redirect_or_body(self):
        calls=[]
        class Response:
            status=200
            def getheader(self,key):return None
            def read(self,bound):return b'{"id":11}'
        class Connection:
            def __init__(self,*a,**kw):calls.append((a,kw))
            def request(self,*a,**kw):calls.append((a,kw))
            def getresponse(self):return Response()
            def close(self):pass
        with patch.object(M.http.client,'HTTPSConnection',Connection):
            self.assertEqual(M.Reads().get('/actions/runs/11'),{'id':11})
            with self.assertRaises(M.Refusal):M.Reads().get('/actions/secrets')
            with self.assertRaises(M.Refusal):M.Reads().get('https://private.invalid')
            with patch.object(Response,'getheader',lambda s,k:'foreign' if k=='Location' else None):
                with self.assertRaises(M.Refusal):M.Reads().get('/actions/runs/11')
            with patch.object(Response,'getheader',lambda s,k:'incomplete' if k=='Link' else None):
                with self.assertRaises(M.Refusal):M.Reads().get('/actions/runs/11')
            with patch.object(Response,'read',lambda s,b:b'x'*(M.MAX_BODY+1)):
                with self.assertRaises(M.Refusal):M.Reads().get('/actions/runs/11')
            with patch.object(Response,'status',403):
                with self.assertRaises(M.Refusal):M.Reads().get('/actions/runs/11')
        self.assertEqual(calls[1][0],('GET','/repos/shk95/configs/actions/runs/11'))
        self.assertNotIn('Authorization',calls[1][1]['headers']);self.assertNotIn('body',calls[1][1])
    def test_duplicate_nonobject_and_nonfinite_json_responses_refuse(self):
        for raw in (b'{"id":1,"id":2}',b'[]',b'{"id":NaN}'):
            with self.subTest(raw=raw),self.assertRaises(ValueError):M.document(raw)
    def test_workflow_has_no_environment_operating_secret_writer_lock_or_candidate_execution(self):
        source=(ROOT.parents[1]/'.github/workflows/release-control-inspect.yml').read_text()
        for forbidden in ('environment:','secrets.','concurrency:','schedule:','upload-artifact','download-artifact','cache@'):
            self.assertNotIn(forbidden,source)
        self.assertIn('ref: ${{ github.sha }}',source);self.assertIn('fetch-depth: 0',source)
        self.assertIn('persist-credentials: false',source);self.assertIn('python3 -I -S -B',source)

class AncestryProof(unittest.TestCase):
    # INV repository/authenticated-release-transport
    # INV repository/release-inspection-without-authority
    # INV repository/fixture-git-isolation
    def test_full_original_public_git_history_is_required(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)/'repo';root.mkdir()
            def git(*args):return subprocess.check_output(['git','-C',str(root),*args],stderr=subprocess.DEVNULL).decode().strip()
            git('init','-q','-b','master');git('config','user.name','Fixture');git('config','user.email','fixture@example.invalid')
            git('config','core.hooksPath',str(Path(directory)/'no-hooks'))
            (root/'README.md').write_text('fixture\n');git('add','.');git('commit','-qm','fixture root');first=git('rev-parse','HEAD')
            script=root/'tool/version-control/release-inspect.py';script.parent.mkdir(parents=True);script.write_bytes((ROOT/'release-inspect.py').read_bytes())
            git('add','.');git('commit','-qm','fixture inspector');head=git('rev-parse','HEAD')
            module=load(script);module.ancestor(first,head)
            with self.assertRaises(module.Refusal):module.ancestor(head,first)
            (root/'.git/shallow').write_text(head+'\n')
            with self.assertRaises(module.Refusal):module.ancestor(first,head)
            (root/'.git/shallow').unlink();git('update-ref','refs/replace/'+first,head)
            with self.assertRaises(module.Refusal):module.ancestor(first,head)

if __name__=='__main__':unittest.main()
