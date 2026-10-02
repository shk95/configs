"""Trusted private Git acquisition and disabled proposals; no deployed writer CLI."""
# INV repository/authenticated-release-transport
# INV repository/private-history-acquisition-isolated
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
    'release-transport-retained.py','release-transport-preflight.py','release-operating-history.py')))
SEED_PATH='release-initial-proposal.tsv'

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
        L.verify_graphs(bundle,[source])
        manifest=L.git(bundle,'show',source+':tool/version-control/release-transport.manifest.tsv')
        rows=manifest.decode('ascii').splitlines()
        T.need(manifest.endswith(b'\n') and rows and rows[0]=='format\t1','invalid-initial-transport')
        names=[]
        for row in rows[1:]:
            fields=row.split('\t')
            T.need(len(fields)==3 and fields[0]=='file' and fields[1] in TRANSPORT_FILES
                   and re.fullmatch('[a-f0-9]{64}',fields[2]),'invalid-initial-transport')
            names.append(fields[1])
            T.need(T.digest(L.git(bundle,'show',source+':'+fields[1]))==fields[2],'initial-transport-mismatch')
        T.need(tuple(names)==TRANSPORT_FILES,'incomplete-initial-transport')
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
            T.need(self.run(['ls-remote','--refs',url],env,capture=True)==b'','existing-initial-refs')
            records=self.disabled_records(bundle,approved,config)
            fields=L.singletons(config,{'enabled','public-repository','repository','operating-repository',
                'operating-ref','workflow','actors','checks','protocol'})
            T.need(fields['workflow']==str(self.entry.trusted['workflow'])
                   and sorted(map(int,fields['actors'].split(',')))==sorted(self.entry.trusted['actors']),
                   'foreign-initial-configuration')
            # Detect refs appearing while the original package is projected.
            T.need(self.run(['ls-remote','--refs',url],env,capture=True)==b'','moving-initial-refs')
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
        """Original-package empty projection only; no seed/ref or baseline adoption."""
        assertion=L.approved(approved)
        T.need(assertion['master']==self.entry.trusted['source'] and assertion['protocol']=='3',
               'unbound-initial-package')
        fields=L.singletons(config,{'enabled','public-repository','repository','operating-repository',
            'operating-ref','workflow','actors','checks','protocol'})
        T.need(fields['enabled']=='0' and fields['protocol']=='3' and fields['public-repository']==T.PUBLIC
               and fields['repository']==str(self.entry.trusted['repository-id'])
               and fields['operating-repository']==self.entry.api.operating and fields['operating-ref']=='operations'
               and re.fullmatch(r'[1-9][0-9]*',fields['workflow'])
               and re.fullmatch(r'[1-9][0-9]*(,[1-9][0-9]*)*',fields['actors'])
               and len(fields['actors'].split(','))==len(set(fields['actors'].split(',')))
               and str(self.entry.runtime['actor']) in fields['actors'].split(',') and fields['checks']!='-',
               'unsafe-initial-configuration')
        package=self.scratch/'initial-package';package.mkdir(exist_ok=True)
        L.extract(bundle,assertion,package)
        driver="import sys;sys.path.insert(0,sys.argv[1]);import engine;sys.stdout.buffer.write(engine.index(engine.initial(),'0'*64))"
        result=subprocess.run([sys.executable,'-I','-S','-B','-c',driver,str(package/L.ROOT)],
            env=L.runtime_environment(os.environ),capture_output=True,timeout=30)
        T.need(result.returncode==0 and len(result.stdout)<=MAX_OUTPUT,'initial-projection-refused')
        fields=L.singletons(result.stdout,L.PROJECTION_FIELDS)
        fields.update({'index-kind':'global-1','ledger-digest':T.digest(T.canonical([]))})
        return {'config/operating.tsv':config,'control/stop.tsv':L.encode_index({
            'stop':'1','revision':'0','reason':'initial-provisioning','operator':str(self.entry.runtime['actor'])}),
            'current/index.tsv':L.encode_index(fields),'current/batches.tsv':b'format\t1\n',
            'current/transcript.json':T.canonical({'source':[],'checks':[],'owner':None,'observations':{}})}
