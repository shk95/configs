"""Trusted original history and disabled provisioning; no deployed writer CLI."""
# INV repository/authenticated-release-transport
# INV repository/private-history-acquisition-isolated
import base64
import datetime
import importlib.util
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time

ROOT=Path(__file__).resolve().parent

def load(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/file)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

B=load('operating_history_bridge','release-transport-retained.py')
T=B.T
L=B.L
MAX_OUTPUT=1024*1024
MAX_DISK=128*1024*1024
MAX_FILES=20000
TIMEOUT=120
TRANSPORT_FILES=tuple(sorted('tool/version-control/'+name for name in (
    'release-control-loader.py','release-transport','release-transport.py',
    'release-transport-retained.py','release-transport-preflight.py','release-operating-history.py',
    'release-operating-roles.json')))
LEGACY_TRANSPORT_FILES=tuple(name for name in TRANSPORT_FILES if not name.endswith('/release-operating-roles.json'))
ROLE_PATH='tool/version-control/release-operating-roles.json'
SEED_PATH='release-initial-proposal.tsv'

def source_transport(bundle,source,roles_required=False):
    """Original bytes only. No claim that a supplied source is current master."""
    T.sha(source);L.verify_graphs(bundle,[source])
    _,manifest=L.record_blob(bundle,source,'tool/version-control/release-transport.manifest.tsv')
    rows=manifest.decode('ascii').splitlines()
    T.need(manifest.endswith(b'\n') and rows and rows[0]=='format\t1','invalid-initial-transport')
    names=[]
    for row in rows[1:]:
        fields=row.split('\t')
        T.need(len(fields)==3 and fields[0]=='file' and fields[1] in TRANSPORT_FILES
               and re.fullmatch('[a-f0-9]{64}',fields[2]),'invalid-initial-transport')
        names.append(fields[1])
        T.need(T.digest(L.git(bundle,'show',source+':'+fields[1]))==fields[2],'initial-transport-mismatch')
    inventories=(TRANSPORT_FILES,) if roles_required else (TRANSPORT_FILES,LEGACY_TRANSPORT_FILES)
    T.need(tuple(names) in inventories,'incomplete-initial-transport')
    return manifest

def source_roles(bundle,source):
    """Source declarations are not deployed topology or Environment proof."""
    source_transport(bundle,source,True)
    _,raw=L.record_blob(bundle,source,ROLE_PATH);value=T.document(raw)
    T.need(type(value) is dict and T.canonical(value)==raw and set(value)=={'format','roles'}
           and type(value['format']) is int and value['format']==1
           and type(value['roles']) is dict and set(value['roles'])=={'initializer','writer'},'invalid-source-roles')
    fixed={'initializer':('.github/workflows/release-control-initialize.yml','initialize-operating-records','release-control'),
           'writer':('.github/workflows/release-control-writer.yml','writer-preflight',None)}
    for role,(path,job,environment) in fixed.items():
        entry=value['roles'][role]
        T.need(type(entry) is dict and set(entry)=={'path','job','environment','actors'}
               and (entry['path'],entry['job'],entry['environment'])==(path,job,environment)
               and type(entry['actors']) is list and entry['actors']
               and all(type(actor) is int and actor>0 for actor in entry['actors'])
               and entry['actors']==sorted(set(entry['actors'])),'invalid-source-role')
        for actor in entry['actors']:T.number(actor)
    return value['roles']

def source_date(bundle,source):
    """Stable UTC date from an original source commit, never a rerun clock."""
    T.sha(source);L.verify_graphs(bundle,[source])
    headers=L.git(bundle,'cat-file','commit',source).split(b'\n\n',1)[0].splitlines()
    rows=[row for row in headers if row.startswith(b'committer ')]
    T.need(len(rows)==1,'invalid-source-time')
    match=re.fullmatch(rb'committer [^\n]+ <[^\n<>]+> ([0-9]{1,12}) [+-][0-9]{4}',rows[0])
    T.need(match is not None,'invalid-source-time')
    try:date=datetime.datetime.fromtimestamp(int(match[1]),datetime.timezone.utc)
    except (ValueError,OverflowError,OSError):raise T.Refusal('invalid-source-time') from None
    T.need(1970<=date.year<=9999,'invalid-source-time')
    return date.strftime('%Y-%m-%dT%H:%M:%SZ')

def planned_initial(records,seed,date):
    """Pure prospective Git identity; no objects, refs or receipts are written."""
    T.sha(seed)
    T.need(isinstance(date,str) and re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ',date),'invalid-initial-time')
    try:stamp=datetime.datetime.strptime(date,'%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=datetime.timezone.utc)
    except (TypeError,ValueError):raise T.Refusal('invalid-initial-time') from None
    T.need(stamp.year>=1970,'invalid-initial-time')
    epoch=int(stamp.timestamp())
    tree=initial_tree(records)
    identity='Release controller <release-controller@example.invalid> '+str(epoch)+' +0000'
    raw=('tree '+tree+'\nparent '+seed+'\nauthor '+identity+'\ncommitter '+identity+
         '\n\ndisabled release initial records\n').encode('ascii')
    return {'tree':tree,'head':T.git_object('commit',raw),'date':date}

def desired_initial(bundle,approved,config,desired):
    """Credential-free desired review. Assertions cannot authorize publication."""
    T.need(type(desired) is dict and set(desired)=={'operating-repository','operating-repository-id',
        'public-repository-id','default-branch','initializer-workflow','initializer-actor','writer-workflow'},
        'invalid-desired-input')
    for field in ('operating-repository-id','public-repository-id','initializer-workflow','initializer-actor','writer-workflow'):
        T.number(desired[field])
    operating=desired['operating-repository'];branch=desired['default-branch']
    T.need(isinstance(operating,str) and re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',operating)
           and operating!=T.PUBLIC and isinstance(branch,str)
           and re.fullmatch(r'[A-Za-z0-9_-][A-Za-z0-9_-]{0,99}',branch) and branch!='operations',
           'invalid-desired-private')
    assertion=L.approved(approved);source=assertion['master']
    roles=source_roles(bundle,source)
    T.need(desired['initializer-actor'] in roles['initializer']['actors'],'foreign-desired-initializer')
    fields=L.singletons(config,{'enabled','public-repository','repository','operating-repository',
        'operating-ref','workflow','actors','checks','protocol'})
    T.need(fields['workflow']==str(desired['writer-workflow'])
           and fields['actors']==','.join(map(str,roles['writer']['actors'])),'foreign-desired-writer')
    with tempfile.TemporaryDirectory(prefix='release-desired-initial-') as folder:
        records=disabled_projection(bundle,approved,config,source,desired['public-repository-id'],
            operating,desired['initializer-actor'],Path(folder))
    bindings={}
    for role,entry in roles.items():
        rows=L.git(bundle,'ls-tree',source,'--',entry['path']).decode('ascii').splitlines()
        if not rows:
            T.need(role=='initializer','missing-source-writer')
            blob=None
        else:
            T.need(len(rows)==1 and rows[0].startswith('100644 blob '),'unsafe-source-workflow')
            blob=T.sha(rows[0].split()[2])
        bindings[role]=dict(entry,workflow=desired[role+'-workflow'],blob=blob)
    value={'kind':'desired-disabled-initial-proposal','format':2,'authenticated':False,
        'source':source,'transport-manifest':T.digest(source_transport(bundle,source,True)),
        'approval-bytes':T.digest(approved),'approved':assertion,'desired':dict(desired),
        'roles':bindings,'roles-digest':T.digest(L.git(bundle,'show',source+':'+ROLE_PATH)),
        'date':source_date(bundle,source),'seed-path':SEED_PATH,'operations-ref':'refs/heads/operations',
        'records':{name:{'digest':T.digest(data),'blob':T.git_object('blob',data),'size':len(data)}
                   for name,data in sorted(records.items())},'enabled':False,'semantic-baseline':None}
    proposal=T.canonical(value);T.need(len(proposal)<=MAX_OUTPUT,'initial-proposal-bound')
    return proposal,records

def verify_source_role(api,bundle,source,role,workflow):
    """Metadata plus original blob; never job/credential/isolation certification."""
    roles=source_roles(bundle,source);T.need(role in roles,'unknown-source-role')
    entry=roles[role];T.number(workflow)
    T.need(api.ref('heads/master')==source,'moving-role-source')
    by_id=api.get('/actions/workflows/'+str(workflow))
    by_path=api.get('/actions/workflows/'+entry['path'].rsplit('/',1)[1])
    T.need(by_id.get('id')==workflow and by_path.get('id')==workflow
           and by_id.get('path')==entry['path'] and by_path.get('path')==entry['path']
           and by_id.get('state')==by_path.get('state')=='active','wrong-source-workflow')
    rows=L.git(bundle,'ls-tree',source,'--',entry['path']).decode('ascii').splitlines()
    T.need(len(rows)==1 and rows[0].startswith('100644 blob '),'missing-source-workflow')
    blob=T.sha(rows[0].split()[2]);raw=L.git(bundle,'show',source+':'+entry['path'])
    T.need(T.git_object('blob',raw)==blob and api.ref('heads/master')==source,'wrong-source-workflow-blob')
    return dict(entry,workflow=workflow,blob=blob)

ASKPASS='''import os,sys
prompt=sys.argv[1] if len(sys.argv)==2 else ''
expected="Password for '"+os.environ['CONFIGS_ACQUIRE_URL']+"': "
if prompt!=expected:sys.exit(1)
sys.stdout.buffer.write((os.environ['CONFIGS_ACQUIRE_TOKEN']+'\\n').encode('ascii'))
'''

def credential_free(source):
    env=L.runtime_environment(source)
    env.update(GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL=os.devnull,
               GIT_NO_REPLACE_OBJECTS='1',GIT_NO_LAZY_FETCH='1',GIT_GRAFT_FILE=os.devnull,
               GIT_TERMINAL_PROMPT='0',LC_ALL='C',LANG='C')
    return env

def initial_tree(records):
    """Exact full tree identity, including directory objects and modes."""
    root={}
    for path,data in records.items():
        node=root;parts=path.split('/')
        for name in parts[:-1]:node=node.setdefault(name,{})
        node[parts[-1]]=T.git_object('blob',data)
    def tree(node):
        raw=b''
        for name,value in sorted(node.items(),key=lambda item:item[0]+('/' if isinstance(item[1],dict) else '')):
            directory=isinstance(value,dict)
            oid=tree(value) if directory else value
            raw+=('40000' if directory else '100644').encode()+b' '+name.encode()+b'\0'+bytes.fromhex(oid)
        return T.git_object('tree',raw)
    return tree(root)

def disabled_projection(bundle,approved,config,source,repository_id,operating,operator,scratch):
    """Pure original projection; caller owns role and observed-identity validation."""
    T.number(operator);T.number(repository_id)
    assertion=L.approved(approved)
    T.need(assertion['master']==source and assertion['protocol']=='3',
           'unbound-initial-package')
    fields=L.singletons(config,{'enabled','public-repository','repository','operating-repository',
        'operating-ref','workflow','actors','checks','protocol'})
    T.need(fields['enabled']=='0' and fields['protocol']=='3' and fields['public-repository']==T.PUBLIC
           and fields['repository']==str(repository_id)
           and fields['operating-repository']==operating and fields['operating-ref']=='operations'
           and re.fullmatch(r'[1-9][0-9]*',fields['workflow'])
           and re.fullmatch(r'[1-9][0-9]*(,[1-9][0-9]*)*',fields['actors'])
           and len(fields['actors'].split(','))==len(set(fields['actors'].split(',')))
           and fields['checks']!='-',
           'unsafe-initial-configuration')
    package=scratch/'initial-package';package.mkdir(exist_ok=True)
    L.extract(bundle,assertion,package)
    driver="import sys;sys.path.insert(0,sys.argv[1]);import engine;sys.stdout.buffer.write(engine.index(engine.initial(),'0'*64))"
    result=subprocess.run([sys.executable,'-I','-S','-B','-c',driver,str(package/L.ROOT)],
        env=L.runtime_environment(os.environ),capture_output=True,timeout=30)
    T.need(result.returncode==0 and len(result.stdout)<=MAX_OUTPUT,'initial-projection-refused')
    fields=L.singletons(result.stdout,L.PROJECTION_FIELDS)
    fields.update({'index-kind':'global-1','ledger-digest':T.digest(T.canonical([]))})
    return {'config/operating.tsv':config,'control/stop.tsv':L.encode_index({
        'stop':'1','revision':'0','reason':'initial-provisioning','operator':str(operator)}),
        'current/index.tsv':L.encode_index(fields),'current/batches.tsv':b'format\t1\n',
        'current/transcript.json':T.canonical({'source':[],'checks':[],'owner':None,'observations':{}})}


class GitHistory:
    """Own fresh private objects. Caller must close after retained replay."""
    def __init__(self,entry,repository_id):
        T.need(type(entry) is T.Entry and entry.authenticated,'missing-acquisition-entry')
        T.need(entry.runtime['mode'] in {'start','approve','stop','resume','wake'},'nonwriter-acquisition-mode')
        self.entry=entry
        self.repository_id=T.number(repository_id)
        self.private_identity()
        jobs=entry.api.jobs(entry.runtime['run'],entry.runtime['attempt'])
        T.need(len(jobs)==1 and jobs[0].get('id')==entry.runtime['job'],'nonisolated-acquisition-job')
        self.temporary=tempfile.TemporaryDirectory(prefix='release-private-history-')
        self.scratch=Path(self.temporary.name)
        self.scratch.chmod(0o700)
        self.repo=self.scratch/'objects.git'
        self.home=self.scratch/'home';self.home.mkdir()
        self.empty=self.scratch/'empty';self.empty.mkdir()
        executable=shutil.which('git');T.need(executable,'missing-git')
        self.git=str(Path(executable).resolve())
        self.base=credential_free(os.environ)
        self.base.update(HOME=str(self.home),USERPROFILE=str(self.home),XDG_CONFIG_HOME=str(self.home),
                         GIT_CONFIG_GLOBAL=str(self.empty/'config'),GIT_TEMPLATE_DIR=str(self.empty),GIT_ALLOW_PROTOCOL='')
        self.options=['-c','core.hooksPath='+str(self.empty),'-c','core.fsmonitor=false',
            '-c','credential.helper=','-c','credential.useHttpPath=true',
            '-c','http.proxy=','-c','http.followRedirects=false','-c','http.sslVerify=true',
            '-c','protocol.allow=never','-c','protocol.https.allow=always',
            '-c','fetch.recurseSubmodules=false','-c','maintenance.auto=false','-c','gc.auto=0']
        try:
            version=self.run(['--version'],self.base,capture=True).decode().strip()
            match=re.fullmatch(r'git version (\d+)\.(\d+)\.\d+(?:\.[A-Za-z0-9.]+)?',version)
            T.need(match and tuple(map(int,match.groups()))>=(2,38),'unsupported-git')
            self.run(['init','--bare','--template='+str(self.empty),str(self.repo)],self.base)
        except BaseException:
            self.close();raise

    def private_identity(self):
        value=self.entry.api.repository(self.entry.api.operating)
        T.need(type(value.get('id')) is int and value.get('id')==self.repository_id and value.get('private') is True
               and value.get('full_name')==self.entry.api.operating,'wrong-private-repository')
        return value

    def close(self):
        self.temporary.cleanup()

    def size(self):
        total=files=0
        for path in self.scratch.rglob('*'):
            T.need(not path.is_symlink(),'unsafe-acquisition-file')
            if path.is_file():
                try:info=path.stat()
                except FileNotFoundError:continue # Git may atomically rename a temporary pack.
                total+=info.st_size;files+=1
                T.need(total<=MAX_DISK and files<=MAX_FILES,'acquisition-size-bound')

    def terminate(self,process):
        if process.poll() is not None:return
        if os.name=='nt':
            system=Path(os.environ['SystemRoot'])/'System32/taskkill.exe'
            subprocess.run([str(system),'/PID',str(process.pid),'/T','/F'],
                env=credential_free(os.environ),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=15)
        else:
            try:os.killpg(process.pid,signal.SIGKILL)
            except ProcessLookupError:pass
        if process.poll() is None:process.kill()
        process.wait(timeout=15)

    def run(self,args,env,capture=False):
        output=bytearray();oversize=threading.Event()
        kwargs={'start_new_session':True} if os.name!='nt' else {'creationflags':subprocess.CREATE_NEW_PROCESS_GROUP}
        process=subprocess.Popen([self.git]+self.options+args,env=env,cwd=self.scratch,
            stdin=subprocess.DEVNULL,stdout=subprocess.PIPE if capture else subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,**kwargs)
        reader=None
        if capture:
            def read():
                while True:
                    chunk=process.stdout.read(65536)
                    if not chunk:return
                    if len(output)+len(chunk)>MAX_OUTPUT:oversize.set();return
                    output.extend(chunk)
            reader=threading.Thread(target=read,daemon=True);reader.start()
        try:
            deadline=time.monotonic()+TIMEOUT
            while process.poll() is None:
                self.size()
                T.need(not oversize.is_set() and time.monotonic()<deadline,'acquisition-execution-bound')
                time.sleep(0.05)
            if reader:
                reader.join(timeout=2)
                T.need(not reader.is_alive() and not oversize.is_set(),'acquisition-output-bound')
            self.size();T.need(process.returncode==0,'private-git-refused')
            return bytes(output)
        finally:
            self.terminate(process)
            if reader:
                reader.join(timeout=2)
                process.stdout.close()

    def acquire(self,token,head):
        """Fixed HTTPS ref only. No remote/candidate input chooses executable code."""
        T.sha(head)
        T.need(isinstance(token,str) and token and token.isascii()
               and not any(c.isspace() or ord(c)<33 or ord(c)==127 for c in token),'invalid-acquisition-credential')
        api=self.entry.api
        T.Entry(api,self.entry.trusted,self.entry.runtime)
        self.private_identity()
        jobs=api.jobs(self.entry.runtime['run'],self.entry.runtime['attempt'])
        T.need(len(jobs)==1 and jobs[0].get('id')==self.entry.runtime['job'],'nonisolated-acquisition-job')
        T.need(api.ref('heads/master')==self.entry.trusted['source']
               and api.ref('heads/operations',api.operating)==head,'moving-acquisition-head')
        helper=self.scratch/'askpass.py';helper.write_text(ASKPASS)
        launcher=self.scratch/'askpass.sh'
        def quote(value):return "'"+value.replace("'","'\\''")+"'"
        launcher.write_text('#!/bin/sh\nexec '+quote(sys.executable)+' -I -S -B '+quote(str(helper))+' "$@"\n')
        launcher.chmod(0o700)
        url='https://x-access-token@github.com/'+api.operating+'.git'
        env=dict(self.base,GIT_ALLOW_PROTOCOL='https',GIT_ASKPASS=str(launcher),
                 CONFIGS_ACQUIRE_TOKEN=token,CONFIGS_ACQUIRE_URL=url)
        try:
            rows=self.run(['ls-remote','--refs',url,'refs/heads/operations'],env,capture=True)
            T.need(rows== (head+'\trefs/heads/operations\n').encode(),'unbound-acquisition-ref')
            self.run(['-C',str(self.repo),'fetch','--no-tags','--no-recurse-submodules',
                      url,'refs/heads/operations:refs/heads/operations'],env)
        finally:
            env.pop('CONFIGS_ACQUIRE_TOKEN',None)
        self.private_identity()
        T.need(api.ref('heads/operations',api.operating)==head
               and api.ref('heads/master')==self.entry.trusted['source'],'moving-acquisition-head')
        T.need(L.git(self.repo,'rev-parse','--is-shallow-repository').strip()==b'false'
               and L.git(self.repo,'rev-parse','--show-object-format').strip()==b'sha1'
               and L.git(self.repo,'rev-parse','refs/heads/operations').strip()==head.encode()
               and not L.git(self.repo,'for-each-ref','--format=%(refname)','refs/replace').strip(),
               'unsafe-private-graph')
        T.need(not (self.repo/'objects/info/alternates').exists()
               and not list((self.repo/'objects').rglob('*.promisor')),'partial-private-objects')
        self.run(['-C',str(self.repo),'fsck','--full','--strict','--no-dangling','--no-reflogs'],self.base)
        L.verify_graphs(self.repo,[head]);L.verify_append_only_snapshot(self.repo,head)
        self.size()
        T.Entry(api,self.entry.trusted,self.entry.runtime)
        self.private_identity()
        jobs=api.jobs(self.entry.runtime['run'],self.entry.runtime['attempt'])
        T.need(len(jobs)==1 and jobs[0].get('id')==self.entry.runtime['job']
               and api.ref('heads/operations',api.operating)==head
               and api.ref('heads/master')==self.entry.trusted['source'],'moving-acquisition-context')
        return self.repo

    def initial_proposal(self,bundle,approved,config,token):
        """Private review bytes only. No seed, ref, bootstrap or approval effect."""
        return self._proposal(bundle,approved,config,token,b'')

    def _proposal(self,bundle,approved,config,token,expected_refs):
        """Internal regeneration with exactly observed provisioning refs."""
        T.need(isinstance(token,str) and token and token.isascii()
               and not any(c.isspace() or ord(c)<33 or ord(c)==127 for c in token),'invalid-acquisition-credential')
        api=self.entry.api
        def context():
            T.Entry(api,self.entry.trusted,self.entry.runtime)
            metadata=self.private_identity()
            jobs=api.jobs(self.entry.runtime['run'],self.entry.runtime['attempt'])
            T.need(len(jobs)==1 and jobs[0].get('id')==self.entry.runtime['job']
                   and api.ref('heads/master')==self.entry.trusted['source'],'moving-proposal-context')
            branch=metadata.get('default_branch')
            # A conservative supported subset; an unsupported default requires
            # replanning, never a request-supplied branch or URL.
            T.need(isinstance(branch,str) and re.fullmatch(r'[A-Za-z0-9_-][A-Za-z0-9_-]{0,99}',branch)
                   and branch!='operations','unsupported-initial-default')
            return branch
        branch=context()
        source=self.entry.trusted['source']
        manifest=source_transport(bundle,source)
        # Full refs advertisement, not an API 404, establishes this observation.
        # Git owns the same isolated credential boundary as original acquisition.
        helper=self.scratch/'askpass.py';helper.write_text(ASKPASS)
        launcher=self.scratch/'askpass.sh'
        def quote(value):return "'"+value.replace("'","'\\''")+"'"
        launcher.write_text('#!/bin/sh\nexec '+quote(sys.executable)+' -I -S -B '+quote(str(helper))+' "$@"\n')
        launcher.chmod(0o700)
        url='https://x-access-token@github.com/'+api.operating+'.git'
        env=dict(self.base,GIT_ALLOW_PROTOCOL='https',GIT_ASKPASS=str(launcher),
                 CONFIGS_ACQUIRE_TOKEN=token,CONFIGS_ACQUIRE_URL=url)
        try:
            T.need(self.run(['ls-remote','--refs',url],env,capture=True)==expected_refs,'existing-initial-refs')
            records=self.disabled_records(bundle,approved,config)
            fields=L.singletons(config,{'enabled','public-repository','repository','operating-repository',
                'operating-ref','workflow','actors','checks','protocol'})
            T.need(fields['workflow']==str(self.entry.trusted['workflow'])
                   and sorted(map(int,fields['actors'].split(',')))==sorted(self.entry.trusted['actors']),
                   'foreign-initial-configuration')
            # Detect refs appearing while the original package is projected.
            T.need(self.run(['ls-remote','--refs',url],env,capture=True)==expected_refs,'moving-initial-refs')
        finally:
            env.pop('CONFIGS_ACQUIRE_TOKEN',None)
        T.need(context()==branch,'moving-initial-default')
        value={'kind':'disabled-initial-proposal','format':1,'source':source,
            'transport-manifest':T.digest(manifest),'approved':L.approved(approved),
            'approval-bytes':T.digest(approved),'public-repository':T.PUBLIC,
            'public-repository-id':self.entry.trusted['repository-id'],
            'operating-repository':api.operating,'operating-repository-id':self.repository_id,
            'default-branch':branch,'operations-ref':'refs/heads/operations',
            'environment':self.entry.trusted['environment'],'workflow':self.entry.trusted['workflow'],
            'workflow-path':self.entry.trusted['workflow-path'],'job-name':self.entry.trusted['job-name'],
            'actor':self.entry.runtime['actor'],'seed-path':SEED_PATH,
            'actors':sorted(self.entry.trusted['actors']),
            'records':{name:{'digest':T.digest(data),'blob':T.git_object('blob',data),
                             'size':len(data)} for name,data in sorted(records.items())},
            'enabled':False,'semantic-baseline':None}
        proposal=T.canonical(value)
        T.need(len(proposal)<=MAX_OUTPUT,'initial-proposal-bound')
        return proposal

    def review_initial(self,proposal,requested_digest,bundle,approved,config,token):
        """Recompute every binding. Digest matching is not maintainer approval."""
        T.need(type(proposal) is bytes and len(proposal)<=MAX_OUTPUT
               and isinstance(requested_digest,str) and re.fullmatch('[a-f0-9]{64}',requested_digest)
               and T.digest(proposal)==requested_digest,'wrong-initial-review-digest')
        actual=self.initial_proposal(bundle,approved,config,token)
        T.need(actual==proposal,'changed-initial-proposal')
        # Only the digest grammar can be handed to a future fixed-path seed writer.
        return ('format\t1\nproposal\t'+requested_digest+'\n').encode('ascii')

    def disabled_records(self,bundle,approved,config):
        """Legacy same-entry projection preserves its original actor restriction."""
        fields=L.singletons(config,{'enabled','public-repository','repository','operating-repository',
            'operating-ref','workflow','actors','checks','protocol'})
        T.need(str(self.entry.runtime['actor']) in fields['actors'].split(','),'unsafe-initial-configuration')
        return disabled_projection(bundle,approved,config,self.entry.trusted['source'],
            self.entry.trusted['repository-id'],self.entry.api.operating,self.entry.runtime['actor'],self.scratch)

    def _initial_context(self,proposal,requested_digest):
        T.need(type(proposal) is bytes and len(proposal)<=MAX_OUTPUT
               and isinstance(requested_digest,str) and re.fullmatch('[a-f0-9]{64}',requested_digest)
               and T.digest(proposal)==requested_digest,'wrong-initial-review-digest')
        value=T.document(proposal)
        T.need(isinstance(value,dict) and T.canonical(value)==proposal and value.get('kind')=='disabled-initial-proposal'
               and value.get('format')==1 and value.get('enabled') is False
               and value.get('semantic-baseline') is None,'invalid-initial-proposal')
        T.Entry(self.entry.api,self.entry.trusted,self.entry.runtime)
        metadata=self.private_identity()
        T.need(value.get('source')==self.entry.trusted['source']
               and self.entry.api.ref('heads/master')==value['source']
               and value.get('operating-repository')==self.entry.api.operating
               and value.get('operating-repository-id')==self.repository_id
               and value.get('default-branch')==metadata.get('default_branch')
               and isinstance(value.get('default-branch'),str)
               and re.fullmatch(r'[A-Za-z0-9_-][A-Za-z0-9_-]{0,99}',value['default-branch'])
               and value['default-branch']!='operations'
               and value.get('seed-path')==SEED_PATH,'moving-initial-context')
        jobs=self.entry.api.jobs(self.entry.runtime['run'],self.entry.runtime['attempt'])
        T.need(len(jobs)==1 and jobs[0].get('id')==self.entry.runtime['job'],'nonisolated-initial-job')
        return value

    def _initial_git(self,token,args,capture=False):
        T.need(isinstance(token,str) and token and token.isascii()
               and not any(c.isspace() or ord(c)<33 or ord(c)==127 for c in token),'invalid-acquisition-credential')
        helper=self.scratch/'askpass.py';helper.write_text(ASKPASS)
        launcher=self.scratch/'askpass.sh'
        def quote(value):return "'"+value.replace("'","'\\''")+"'"
        launcher.write_text('#!/bin/sh\nexec '+quote(sys.executable)+' -I -S -B '+quote(str(helper))+' "$@"\n')
        launcher.chmod(0o700)
        url='https://x-access-token@github.com/'+self.entry.api.operating+'.git'
        env=dict(self.base,GIT_ALLOW_PROTOCOL='https',GIT_ASKPASS=str(launcher),
                 CONFIGS_ACQUIRE_TOKEN=token,CONFIGS_ACQUIRE_URL=url)
        try:return self.run([url if arg=='@url' else arg for arg in args],env,capture)
        finally:env.pop('CONFIGS_ACQUIRE_TOKEN',None)

    def observe_initial(self,proposal,requested_digest,bundle,approved,config,token,complete=False,expected_head=None):
        """Observe only. A missing or conflicting acknowledgement never retries."""
        if complete:T.sha(expected_head)
        value=self._initial_context(proposal,requested_digest)
        branch=value['default-branch']
        rows=self._initial_git(token,['ls-remote','--refs','@url'],True)
        expected_names=['refs/heads/'+branch]+(['refs/heads/operations'] if complete else [])
        refs={}
        for row in rows.decode('ascii').splitlines():
            fields=row.split('\t')
            T.need(len(fields)==2 and fields[1] not in refs,'ambiguous-initial-refs')
            refs[fields[1]]=T.sha(fields[0])
        T.need(set(refs)==set(expected_names) and rows==''.join(
            refs[name]+'\t'+name+'\n' for name in sorted(refs)).encode(),'unknown-or-conflicting-initial-refs')
        seed=refs['refs/heads/'+branch]
        self._initial_git(token,['-C',str(self.repo),'fetch','--no-tags','--no-recurse-submodules',
            '@url','refs/heads/'+branch+':refs/heads/initial-seed']+
            (['refs/heads/operations:refs/heads/operations'] if complete else []))
        T.need(self._initial_git(token,['ls-remote','--refs','@url'],True)==rows,'moving-initial-refs')
        T.need(L.git(self.repo,'rev-parse','--is-shallow-repository').strip()==b'false'
               and L.git(self.repo,'rev-parse','--show-object-format').strip()==b'sha1'
               and not L.git(self.repo,'for-each-ref','--format=%(refname)','refs/replace').strip()
               and not (self.repo/'objects/info/alternates').exists()
               and not list((self.repo/'objects').rglob('*.promisor')),'unsafe-initial-graph')
        self.run(['-C',str(self.repo),'fsck','--full','--strict','--no-dangling','--no-reflogs'],self.base)
        L.verify_graphs(self.repo,list(refs.values()))
        seed_bytes=('format\t1\nproposal\t'+requested_digest+'\n').encode()
        T.need(L.git(self.repo,'rev-list','--parents','-n','1',seed).strip()==seed.encode(),
               'nonroot-initial-seed')
        blob=T.git_object('blob',seed_bytes)
        T.need(L.git(self.repo,'ls-tree','-z',seed)==
               ('100644 blob '+blob+'\t'+SEED_PATH+'\0').encode()
               and L.record_blob(self.repo,seed,SEED_PATH)==(blob,seed_bytes),'foreign-initial-seed')
        T.need(self._proposal(bundle,approved,config,token,rows)==proposal,'changed-initial-proposal')
        head=refs.get('refs/heads/operations')
        if complete:
            T.need(L.git(self.repo,'rev-list','--parents','-n','1',head).strip()==(head+' '+seed).encode(),
                   'wrong-initial-parent')
            records=self.disabled_records(bundle,approved,config)
            records[SEED_PATH]=seed_bytes
            T.need(head==expected_head,'conflicting-initial-head')
            T.need(L.git(self.repo,'rev-parse',head+'^{tree}').decode().strip()==initial_tree(records),
                   'foreign-initial-records')
            for path,data in records.items():
                T.need(L.record_blob(self.repo,head,path)==(T.git_object('blob',data),data),'changed-initial-record')
            self._replay_initial(bundle,approved,head)
        self._initial_context(proposal,requested_digest)
        T.need(self._initial_git(token,['ls-remote','--refs','@url'],True)==rows,'moving-initial-refs')
        return {'seed':seed,'head':head,'refs':rows}

    def _replay_initial(self,bundle,approved,head):
        """Use the full original loader and its original retained reducer."""
        with tempfile.TemporaryDirectory(dir=self.scratch,prefix='initial-replay-') as folder:
            scratch=Path(folder)
            request=scratch/'request.tsv';request.write_bytes(L.encode_index({
                'mode':'preview','actor':'0','run':'0','attempt':'0','ref':'master','candidate':'0'*64}))
            transcript=scratch/'transcript.json';transcript.write_bytes(
                L.record_blob(self.repo,head,'current/transcript.json')[1])
            result=L.global_preview({'operating':self.repo,'bundle_repository':Path(bundle),
                'request':request,'transcript':transcript},L.approved(approved),head,scratch)
            T.need(result=={'outcome':'stopped','proposed':0},'unsafe-initial-replay')

    def _initial_date(self):
        date=self.entry.api.run(self.entry.runtime['run'],self.entry.runtime['attempt']).get('run_started_at')
        T.need(isinstance(date,str) and re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ',date),'missing-initial-time')
        return date

    def _local_initial(self,records,parent,date):
        """Prospective local bytes only; never substitute these for remote proof."""
        index=self.scratch/'initial.index'
        env=dict(self.base,GIT_INDEX_FILE=str(index),GIT_AUTHOR_NAME='Release controller',
            GIT_AUTHOR_EMAIL='release-controller@example.invalid',GIT_COMMITTER_NAME='Release controller',
            GIT_COMMITTER_EMAIL='release-controller@example.invalid')
        env.update(GIT_AUTHOR_DATE=date,GIT_COMMITTER_DATE=date)
        self.run(['-C',str(self.repo),'read-tree']+([parent] if parent else ['--empty']),env)
        rows=[]
        for path,data in sorted(records.items()):
            # Local stdin is bounded original data, never a credential.
            result=subprocess.run([self.git]+self.options+['-C',str(self.repo),'hash-object','-w','--stdin'],
                input=data,env=self.base,capture_output=True,timeout=30)
            T.need(result.returncode==0,'initial-local-blob-refused')
            blob=result.stdout.decode().strip();T.need(blob==T.git_object('blob',data),'initial-local-blob-mismatch')
            self.run(['-C',str(self.repo),'update-index','--add','--cacheinfo','100644',blob,path],env)
            rows.append({'path':path,'mode':'100644','type':'blob','sha':blob})
        tree=self.run(['-C',str(self.repo),'write-tree'],env,True).decode().strip();T.sha(tree)
        message=b'disabled release initial records\n'
        result=subprocess.run([self.git]+self.options+['-C',str(self.repo),'commit-tree',tree]+(['-p',parent] if parent else []),
            input=message,env=env,capture_output=True,timeout=30)
        T.need(result.returncode==0,'initial-local-commit-refused')
        planned=result.stdout.decode().strip();T.sha(planned)
        T.need(tree==initial_tree(records),'initial-local-tree-mismatch')
        return tree,planned,rows

    def create_seed(self,proposal,requested_digest,bundle,approved,config,token):
        """One creation attempt. Library caller must supply independent approval."""
        T.need(not getattr(self,'initial_pending',False),'initial-write-fenced')
        seed=self.review_initial(proposal,requested_digest,bundle,approved,config,token)
        value=self._initial_context(proposal,requested_digest)
        records=self.disabled_records(bundle,approved,config)
        records[SEED_PATH]=seed
        _,prospective,_=self._local_initial(records,None,self._initial_date())
        self._replay_initial(bundle,approved,prospective)
        # Rebind all review/absence observations after full prospective replay.
        self.review_initial(proposal,requested_digest,bundle,approved,config,token)
        # Mark pending before the call. A failed observation keeps this object
        # fenced; a later execution may only use observe_initial to reconcile.
        self.initial_pending=True
        try:
            self.entry.api.call(self.entry.api.operating,'PUT','/contents/'+SEED_PATH,
                {'message':'disabled release initial proposal\n','branch':value['default-branch'],
                 'content':base64.b64encode(seed).decode('ascii')},(201,))
        except T.Unknown:pass
        result=self.observe_initial(proposal,requested_digest,bundle,approved,config,token)
        self.initial_pending=False
        return result

    def publish_initial(self,proposal,requested_digest,bundle,approved,config,token):
        """Seed already verified; create only disabled/stopped operations history."""
        T.need(not getattr(self,'initial_pending',False),'initial-write-fenced')
        observed=self.observe_initial(proposal,requested_digest,bundle,approved,config,token)
        seed=observed['seed'];records=self.disabled_records(bundle,approved,config)
        date=self._initial_date()
        local_records=dict(records)
        local_records[SEED_PATH]=('format\t1\nproposal\t'+requested_digest+'\n').encode()
        tree,planned,rows=self._local_initial(local_records,seed,date)
        rows=[row for row in rows if row['path']!=SEED_PATH]
        self._replay_initial(bundle,approved,planned)
        self._initial_context(proposal,requested_digest)
        T.need(self._initial_git(token,['ls-remote','--refs','@url'],True)==observed['refs'],'moving-initial-refs')
        # Private recovery identity. A future wrapper must preserve it in its
        # independently reviewed private attempt receipt before calling effects.
        self.initial_expected=planned
        self.initial_pending=True
        api=self.entry.api
        def write(suffix,body):
            self._initial_context(proposal,requested_digest)
            T.need(self._initial_git(token,['ls-remote','--refs','@url'],True)==observed['refs'],'moving-initial-refs')
            return api.call(api.operating,'POST',suffix,body,(201,))
        for row in rows:
            data=records[row['path']]
            response,_=write('/git/blobs',{'content':base64.b64encode(data).decode(),'encoding':'base64'})
            T.need(response.get('sha')==row['sha'],'initial-blob-mismatch')
        response,_=write('/git/trees',{'base_tree':L.git(self.repo,'rev-parse',seed+'^{tree}').decode().strip(),'tree':rows})
        T.need(response.get('sha')==tree,'initial-tree-mismatch')
        tagger={'name':'Release controller','email':'release-controller@example.invalid','date':date}
        response,_=write('/git/commits',{'message':'disabled release initial records\n','tree':tree,'parents':[seed],'author':tagger,'committer':tagger})
        T.need(response.get('sha')==planned,'initial-commit-mismatch')
        self._initial_context(proposal,requested_digest)
        T.need(self._initial_git(token,['ls-remote','--refs','@url'],True)==observed['refs'],'moving-initial-refs')
        try:api.call(api.operating,'POST','/git/refs',{'ref':'refs/heads/operations','sha':planned},(201,))
        except T.Unknown:pass
        actual=self.observe_initial(proposal,requested_digest,bundle,approved,config,token,True,planned)
        T.need(actual['head']==planned,'conflicting-initial-head')
        self.initial_pending=False
        return actual
