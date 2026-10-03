"""Finite private one-shot initialization. No certificate issuer or retry entry."""
# INV repository/initializer-attempt-custody
# INV repository/private-history-acquisition-isolated
import argparse
import importlib.util
import os
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('initializer_history',ROOT/'release-operating-history.py')
H=importlib.util.module_from_spec(spec);spec.loader.exec_module(H)
T=H.T;L=H.L
PUBLIC_ID=1330390069
JOB='initialize-operating-records'
WORKFLOW='.github/workflows/release-control-initialize.yml'
ENVIRONMENT='release-control'

def construction(proposal,records):
    value=T.document(proposal)
    seed=('format\t1\nproposal\t'+T.digest(proposal)+'\n').encode()
    return {'seed':seed.decode(),'tree':H.initial_tree(dict(records,**{H.SEED_PATH:seed})),
        'date':value['date'],'name':'Release controller','email':'release-controller@example.invalid',
        'message':'disabled release initial records\n','parent':'observed-original-root-seed'}

def attempt_document(bundle,approved,config,desired,run):
    """Pure private review assertion. This never issues publishing authority."""
    T.number(run)
    proposal,records=H.desired_initial(bundle,approved,config,desired)
    value=T.document(proposal)
    T.need(value['roles']['initializer']['blob'] is not None,'missing-initializer-source')
    return T.canonical({'format':1,'kind':'private-initial-attempt','desired':value,
        'desired-digest':T.digest(proposal),'approval':approved.decode(),'configuration':config.decode(),
        'authorization':{'source':value['source'],'workflow':desired['initializer-workflow'],
            'run':run,'attempt':1,'actor':desired['initializer-actor']},
        'construction':construction(proposal,records)})

def certificate(env):
    value=env.get('CONFIGS_RELEASE_INITIAL_ATTEMPT')
    T.need(isinstance(value,str) and value and len(value.encode())<=H.MAX_OUTPUT,'missing-private-certificate')
    raw=value.encode();packet=T.document(raw)
    T.need(type(packet) is dict and set(packet)=={'format','kind','desired','desired-digest',
        'approval','configuration','authorization','construction'}
        and type(packet['format']) is int and packet['format']==1
        and packet['kind']=='private-initial-attempt' and T.canonical(packet)==raw,'invalid-private-certificate')
    authorization=packet['authorization']
    T.need(type(authorization) is dict and set(authorization)=={'source','workflow','run','attempt','actor'}
        and type(authorization['attempt']) is int and authorization['attempt']==1,'invalid-private-attempt')
    T.sha(authorization['source'])
    for key in ('workflow','run','actor'):T.number(authorization[key])
    T.need(type(packet['desired']) is dict and type(packet['approval']) is str
        and type(packet['configuration']) is str,'invalid-private-certificate')
    T.need(T.digest(T.canonical(packet['desired']))==packet['desired-digest'],'changed-private-proposal')
    return raw,packet

class InitializerEntry:
    """Initializer authority observed independently; never a simulated writer Entry."""
    def __init__(self,api,bundle,source,runtime,action):
        self.authenticated=False
        T.need(action in {'initialize','observe'} and set(runtime)=={'run','attempt','actor','repository'},'invalid-initializer-runtime')
        for key in runtime:T.number(runtime[key])
        T.sha(source);H.source_transport(bundle,source,True)
        T.need(tuple(row.split('\t')[1] for row in H.source_transport(bundle,source).decode().splitlines()[1:])
               ==H.TRANSPORT_FILES,'missing-initializer-closure')
        self.api,self.bundle,self.source,self.runtime,self.action=api,Path(bundle),source,dict(runtime),action
        self.refresh();self.authenticated=True

    def refresh(self):
        api=self.api;runtime=self.runtime
        T.need(api.ref('heads/master')==self.source,'moving-initializer-source')
        public=api.repository(T.PUBLIC)
        T.need(public.get('id')==runtime['repository'] and public.get('full_name')==T.PUBLIC
            and public.get('private') is False and public.get('default_branch')=='master','wrong-initializer-public')
        latest=api.get('/actions/runs/'+str(runtime['run']))
        run=api.run(runtime['run'],runtime['attempt'])
        workflow=T.number(run.get('workflow_id'))
        self.role=H.verify_source_role(api,self.bundle,self.source,'initializer',workflow)
        T.need(self.role['path']==WORKFLOW and self.role['job']==JOB and self.role['environment']==ENVIRONMENT
            and runtime['actor'] in self.role['actors'],'wrong-initializer-role')
        T.need(latest.get('id')==runtime['run'] and latest.get('run_attempt')==runtime['attempt']
            and latest.get('head_sha')==self.source and run.get('head_sha')==self.source
            and run.get('head_branch')=='master' and run.get('event')=='workflow_dispatch'
            and run.get('repository',{}).get('id')==runtime['repository']
            and run.get('actor',{}).get('id')==runtime['actor']
            and run.get('triggering_actor',{}).get('id')==runtime['actor']
            and run.get('status')=='in_progress','unauthenticated-initializer-run')
        jobs=api.jobs(runtime['run'],runtime['attempt'])
        T.need(len(jobs)==1 and jobs[0].get('name')==JOB
            and jobs[0].get('head_sha')==self.source and jobs[0].get('run_id')==runtime['run']
            and jobs[0].get('status')=='in_progress','nonisolated-initializer-job')
        job=T.number(jobs[0].get('id'))
        T.need(not hasattr(self,'job') or self.job==job,'moving-initializer-job')
        self.job=job
        if self.action=='initialize':T.need(runtime['attempt']==1,'initializer-rerun-refused')
        T.need(api.ref('heads/master')==self.source,'moving-initializer-source')

    def bind(self,packet):
        self.refresh();auth=packet['authorization']
        value=packet['desired'];desired=value['desired']
        T.need(auth['source']==value['source']==self.source and auth['workflow']==desired['initializer-workflow']
            ==self.role['workflow'] and auth['actor']==desired['initializer-actor']
            and desired['public-repository-id']==self.runtime['repository']
            and value['roles']['initializer']==self.role,'foreign-private-attempt')
        writer=H.verify_source_role(self.api,self.bundle,self.source,'writer',desired['writer-workflow'])
        T.need(writer==value['roles']['writer'] and writer['environment'] is None,'changed-initial-writer')
        if self.action=='initialize':
            T.need(auth['run']==self.runtime['run'] and auth['attempt']==self.runtime['attempt']
                and auth['actor']==self.runtime['actor'],'foreign-publishing-certificate')

class InitialHttps(T.Https):
    def authorized_write(self,method,path,body):
        entry=self.gate
        T.need(type(entry) is InitializerEntry and entry.authenticated and entry.action=='initialize'
            and entry.api.channel is self,'missing-initializer-entry')
        entry.refresh()
        prefix='/repos/'+entry.api.operating
        allowed=(method=='PUT' and path==prefix+'/contents/'+H.SEED_PATH
                 or method=='POST' and path in {prefix+'/git/blobs',prefix+'/git/trees',prefix+'/git/commits',prefix+'/git/refs'})
        return allowed

class InitialHistory(H.GitHistory):
    """Reuse original isolated Git and fixed publication grammar with actual roles."""
    def __init__(self,entry,env):
        T.need(type(entry) is InitializerEntry and entry.authenticated,'missing-initializer-entry')
        self.entry=entry;self.env=env
        self.raw,self.packet=certificate(env);entry.bind(self.packet)
        self.bundle=entry.bundle;self.approved=self.packet['approval'].encode();self.config=self.packet['configuration'].encode()
        self.proposal=T.canonical(self.packet['desired']);self.digest=T.digest(self.proposal)
        self.repository_id=T.number(self.packet['desired']['desired']['operating-repository-id'])
        T.need(entry.api.operating==self.packet['desired']['desired']['operating-repository'],'foreign-initial-connection')
        self.private_identity();self._storage()
        try:self._initial_context(self.proposal,self.digest)
        except BaseException:self.close();raise
        self.invoked=False;self.seed_seen=False

    def _initial_context(self,proposal,digest):
        T.need(certificate(self.env)[0]==self.raw and proposal==self.proposal and digest==self.digest,
               'changed-initial-certificate')
        self.entry.bind(self.packet)
        metadata=self.private_identity();desired=self.packet['desired']['desired']
        T.need(metadata.get('default_branch')==desired['default-branch'],'moving-initial-default')
        actual,records=H.desired_initial(self.bundle,self.approved,self.config,desired)
        T.need(actual==self.proposal and construction(actual,records)==self.packet['construction'],'changed-initial-construction')
        return dict(desired,**{'seed-path':H.SEED_PATH})

    def disabled_records(self,bundle,approved,config):
        T.need(Path(bundle)==self.bundle and approved==self.approved and config==self.config,'foreign-initial-inputs')
        return H.desired_initial(bundle,approved,config,self.packet['desired']['desired'])[1]

    def _proposal(self,bundle,approved,config,token,expected_refs):
        self._initial_context(self.proposal,self.digest)
        T.need(self._initial_git(token,['ls-remote','--refs','@url'],True)==expected_refs,'moving-initial-refs')
        self.disabled_records(bundle,approved,config)
        T.need(self._initial_git(token,['ls-remote','--refs','@url'],True)==expected_refs,'moving-initial-refs')
        self._initial_context(self.proposal,self.digest)
        return self.proposal

    def review_initial(self,proposal,digest,bundle,approved,config,token):
        self._initial_context(proposal,digest)
        T.need(self.entry.action=='initialize' and self.invoked and not self.seed_seen,'no-fresh-initial-invocation')
        self._proposal(bundle,approved,config,token,b'')
        return self.packet['construction']['seed'].encode()

    def _initial_date(self):return self.packet['construction']['date']

    def create_seed(self,*args):
        T.need(self.entry.action=='initialize' and self.invoked and not self.seed_seen,'no-fresh-initial-invocation')
        result=super().create_seed(*args);self.seed_seen=True;return result

    def publish_initial(self,*args):
        T.need(self.entry.action=='initialize' and self.invoked and self.seed_seen,'foreign-seed-invocation')
        return super().publish_initial(*args)

    def observe(self,token):
        self._initial_context(self.proposal,self.digest)
        rows=self._initial_git(token,['ls-remote','--refs','@url'],True)
        if not rows:
            self._proposal(self.bundle,self.approved,self.config,token,b'')
            return 'absent'
        refs={}
        for line in rows.decode('ascii').splitlines():
            fields=line.split('\t')
            T.need(len(fields)==2 and fields[1] not in refs,'ambiguous-initial-refs')
            refs[fields[1]]=T.sha(fields[0])
        branch=self.packet['desired']['desired']['default-branch'];names={'refs/heads/'+branch}
        T.need(set(refs) in (names,names|{'refs/heads/operations'}),'conflicting-initial-refs')
        records=self.disabled_records(self.bundle,self.approved,self.config)
        records[H.SEED_PATH]=self.packet['construction']['seed'].encode()
        expected=H.planned_initial(records,refs['refs/heads/'+branch],self._initial_date())['head']
        complete='refs/heads/operations' in refs
        super().observe_initial(self.proposal,self.digest,self.bundle,self.approved,self.config,token,complete,
            expected if complete else None)
        return 'initialized' if complete else 'pending'

    def initialize(self,token):
        T.need(self.entry.action=='initialize' and not self.invoked,'initial-invocation-fenced')
        self.invoked=True
        state=self.observe(token)
        if state=='initialized':return state
        T.need(state=='absent','previous-initialization-pending')
        self.create_seed(self.proposal,self.digest,self.bundle,self.approved,self.config,token)
        self.publish_initial(self.proposal,self.digest,self.bundle,self.approved,self.config,token)
        return 'initialized'

def runtime(env):
    T.need(env.get('GITHUB_ACTIONS')=='true' and env.get('GITHUB_SERVER_URL')=='https://github.com'
        and env.get('GITHUB_API_URL')=='https://api.github.com' and env.get('GITHUB_REPOSITORY')==T.PUBLIC
        and env.get('GITHUB_REF')=='refs/heads/master' and env.get('GITHUB_EVENT_NAME')=='workflow_dispatch'
        and env.get('GITHUB_JOB')==JOB,'wrong-initializer-runtime')
    def number(key):
        value=env.get(key);T.need(isinstance(value,str) and re.fullmatch('[1-9][0-9]*',value),'invalid-runtime-number')
        return T.number(int(value))
    current={'run':number('GITHUB_RUN_ID'),'attempt':number('GITHUB_RUN_ATTEMPT'),
        'actor':number('GITHUB_ACTOR_ID'),'repository':number('GITHUB_REPOSITORY_ID')}
    T.need(current['repository']==PUBLIC_ID,'wrong-initializer-repository')
    return T.sha(env.get('GITHUB_SHA')),current

class Parser(argparse.ArgumentParser):
    def error(self,message):self.exit(1,'initializer: refused\n')

def main():
    parser=Parser(description='Finite private initializer; no retry or certificate issuer')
    parser.add_argument('mode',choices=['initialize']);parser.add_argument('--action',choices=['initialize','observe'],required=True)
    args=parser.parse_args();history=None
    try:
        source,current=runtime(os.environ);bundle=ROOT.parents[1]
        T.need(L.git(bundle,'rev-parse','HEAD').decode().strip()==source,'wrong-initializer-checkout')
        event_path=Path(os.environ['GITHUB_EVENT_PATH']);T.need(event_path.stat().st_size<=T.MAX_BODY,'oversize-runtime-event')
        event=T.document(event_path.read_bytes())
        T.need(event.get('inputs',{}).get('action')==args.action,'changed-runtime-action')
        token=os.environ['CONFIGS_RELEASE_TOKEN'];channel=InitialHttps(token)
        api=T.Api(channel,os.environ['CONFIGS_RELEASE_OPERATING_REPOSITORY'])
        entry=InitializerEntry(api,bundle,source,current,args.action);channel.gate=entry
        history=InitialHistory(entry,os.environ)
        T.need(str(history.repository_id)==os.environ['CONFIGS_RELEASE_OPERATING_REPOSITORY_ID'],'foreign-private-id')
        result=history.initialize(token) if args.action=='initialize' else history.observe(token)
        print('initializer: '+result);return 0 if result!='pending' else 1
    except Exception: # Never print private subprocess arguments or endpoint diagnostics.
        print('initializer: refused',file=sys.stderr);return 1
    finally:
        if history is not None:history.close()

if __name__=='__main__':sys.exit(main())
