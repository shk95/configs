"""Credential-free finite public run observations; never ownership or approval."""
# INV repository/authenticated-release-transport
# INV repository/release-inspection-without-authority
import http.client
import json
import os
from pathlib import Path
import re
import ssl
import subprocess
import sys
import time

PUBLIC='shk95/configs'
REPOSITORY=1330390069
ACTOR=101378576
WORKFLOW='.github/workflows/release-control-inspect.yml'
JOB='inspect-release-run'
TARGETS={'.github/workflows/release-control-writer.yml':'writer',
         '.github/workflows/release-credential-check.yml':'validate-operating-credential'}
MAX_BODY=1024*1024

class Refusal(ValueError):
    pass

def need(value):
    if not value:raise Refusal('unavailable-public-observation')

def number(value):
    need(isinstance(value,str) and re.fullmatch(r'[1-9][0-9]*',value))
    return int(value)

def identity(value):
    need(isinstance(value,str) and re.fullmatch(r'[a-f0-9]{40}',value) and value!='0'*40)
    return value

def document(raw):
    def unique(pairs):
        result={}
        for key,value in pairs:
            need(key not in result);result[key]=value
        return result
    value=json.loads(raw,object_pairs_hook=unique,parse_constant=lambda _:need(False))
    need(isinstance(value,dict));return value

class Reads:
    """No token parameter, Authorization header, private URL or write primitive."""
    def get(self,path):
        need(path=='/git/ref/heads/master'
             or re.fullmatch(r'/actions/runs/[1-9][0-9]*(/attempts/[1-9][0-9]*(/jobs\?per_page=100)?)?',path)
             or re.fullmatch(r'/actions/workflows/[1-9][0-9]*',path))
        connection=http.client.HTTPSConnection('api.github.com',timeout=5,context=ssl.create_default_context())
        try:
            connection.request('GET','/repos/'+PUBLIC+path,headers={
                'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2026-03-10',
                'User-Agent':'configs-release-inspect'})
            response=connection.getresponse()
            need(response.status==200 and not response.getheader('Location')
                 and not response.getheader('Link'))
            raw=response.read(MAX_BODY+1);need(len(raw)<=MAX_BODY)
            return document(raw)
        finally:connection.close()

def ancestor(source,approved):
    root=Path(__file__).resolve().parents[2]
    allowed={'PATH','SYSTEMROOT','SystemRoot','WINDIR','COMSPEC','ComSpec','PATHEXT',
             'TEMP','TMP','TMPDIR','LANG','LC_ALL','TZ'}
    env={k:v for k,v in os.environ.items() if k in allowed}
    env.update(GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL=os.devnull,GIT_NO_REPLACE_OBJECTS='1',
               GIT_NO_LAZY_FETCH='1',GIT_GRAFT_FILE=os.devnull,GIT_ALLOW_PROTOCOL='',GIT_TERMINAL_PROMPT='0')
    command=['git','--no-replace-objects','-C',str(root)]
    def git(*args):
        result=subprocess.run(command+list(args),env=env,capture_output=True,timeout=10)
        need(result.returncode==0);return result.stdout.strip()
    need(git('rev-parse','--is-shallow-repository')==b'false'
         and git('rev-parse','--show-object-format')==b'sha1'
         and git('rev-parse','HEAD').decode()==approved
         and not git('for-each-ref','--format=%(refname)','refs/replace'))
    git('merge-base','--is-ancestor',source,approved)

def run(api,identifier,attempt,source=None):
    latest=api.get('/actions/runs/'+str(identifier))
    value=api.get('/actions/runs/'+str(identifier)+'/attempts/'+str(attempt))
    need(latest.get('id')==identifier and latest.get('run_attempt')==attempt
         and latest.get('head_sha')==value.get('head_sha')
         and value.get('id')==identifier and value.get('run_attempt')==attempt
         and value.get('repository',{}).get('id')==REPOSITORY
         and value.get('actor',{}).get('id')==ACTOR and value.get('triggering_actor',{}).get('id')==ACTOR
         and value.get('head_branch')=='master' and value.get('event')=='workflow_dispatch')
    identity(value.get('head_sha'))
    if source is not None:need(value['head_sha']==source)
    workflow=value.get('workflow_id');need(type(workflow) is int and workflow>0)
    definition=api.get('/actions/workflows/'+str(workflow))
    need(definition.get('id')==workflow)
    path=definition.get('path')
    rows=api.get('/actions/runs/'+str(identifier)+'/attempts/'+str(attempt)+'/jobs?per_page=100')
    jobs=rows.get('jobs');need(isinstance(jobs,list) and type(rows.get('total_count')) is int
                             and rows['total_count']==len(jobs) and len(jobs)<=1)
    return value,path,jobs

def observe(env,api,ancestry=ancestor,sleep=time.sleep):
    need(env.get('GITHUB_ACTIONS')=='true' and env.get('GITHUB_SERVER_URL')=='https://github.com'
         and env.get('GITHUB_API_URL')=='https://api.github.com' and env.get('GITHUB_REPOSITORY')==PUBLIC
         and env.get('GITHUB_REF')=='refs/heads/master' and env.get('GITHUB_EVENT_NAME')=='workflow_dispatch'
         and env.get('GITHUB_JOB')==JOB and number(env.get('GITHUB_ACTOR_ID'))==ACTOR
         and number(env.get('GITHUB_REPOSITORY_ID'))==REPOSITORY)
    approved=identity(env.get('GITHUB_SHA'))
    caller=number(env.get('GITHUB_RUN_ID'));caller_attempt=number(env.get('GITHUB_RUN_ATTEMPT'))
    own,path,jobs=run(api,caller,caller_attempt,approved)
    need(path==WORKFLOW and own.get('status')=='in_progress' and len(jobs)==1
         and jobs[0].get('name')==JOB and jobs[0].get('run_id')==caller
         and jobs[0].get('head_sha')==approved and jobs[0].get('status')=='in_progress')
    target=number(env.get('CONFIGS_INSPECT_RUN'));attempt=number(env.get('CONFIGS_INSPECT_ATTEMPT'))
    need(target!=caller)
    mode=env.get('CONFIGS_INSPECT_MODE');need(mode in {'inspect','wait'})
    pinned=None;definition=None;job_id=None
    for index in range(6 if mode=='wait' else 1):
        need(api.get('/git/ref/heads/master').get('object',{}).get('sha')==approved)
        value,path,jobs=run(api,target,attempt,pinned)
        need(path in TARGETS and value.get('status') in {'queued','in_progress','completed','waiting','requested','pending'})
        need(definition is None or definition==(path,value['workflow_id']))
        definition=(path,value['workflow_id'])
        pinned=value['head_sha'];ancestry(pinned,approved)
        if jobs:
            job=jobs[0]
            need(type(job.get('id')) is int and job['id']>0 and job.get('name')==TARGETS[path]
                 and job.get('head_sha')==pinned and job.get('run_id')==target
                 and job.get('status') in {'queued','in_progress','completed','waiting','pending'})
            need(job_id is None or job_id==job['id']);job_id=job['id']
        terminal=value['status']=='completed'
        need(not terminal or (len(jobs)==1 and jobs[0]['status']=='completed'))
        latest=api.get('/actions/runs/'+str(target))
        need(latest.get('run_attempt')==attempt and latest.get('head_sha')==pinned)
        if terminal or mode=='inspect':break
        if index<5:sleep(2)
    need(api.get('/git/ref/heads/master').get('object',{}).get('sha')==approved)
    own,path,jobs=run(api,caller,caller_attempt,approved)
    need(own.get('status')=='in_progress' and path==WORKFLOW and len(jobs)==1
         and jobs[0].get('name')==JOB and jobs[0].get('status')=='in_progress'
         and jobs[0].get('head_sha')==approved and jobs[0].get('run_id')==caller)
    return {'kind':'public-release-run-observation','run':target,'attempt':attempt,'source':pinned,
            'status':value['status'],'terminal':terminal,'bounded_wait_finished':mode=='wait' and not terminal,
            'ownership':False,'approval':False,'operating_certification':False}

def main(env=None,factory=Reads,ancestry=ancestor,sleep=time.sleep):
    try:
        value=observe(os.environ if env is None else env,factory(),ancestry,sleep)
        print(json.dumps(value,sort_keys=True));return 0
    except (ValueError,TypeError,KeyError,AttributeError,OSError,http.client.HTTPException,subprocess.SubprocessError):
        print('public release inspection: refused',file=sys.stderr);return 1

if __name__=='__main__':sys.exit(main())
