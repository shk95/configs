"""Credential-free bridge to the exact eight-file semantic package.

Driver text is trusted transport glue. It imports only the manifest-verified
package selected by the existing global-history loader; no candidate code runs.
"""
# INV repository/public-refresh-object-transport
# INV repository/authenticated-release-transport
import base64
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

# Trusted siblings are part of the separate transport source inventory, never an
# implicit addition to the retained semantic package's historical manifest.
ROOT = Path(__file__).resolve().parent

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

T = module('configs_release_transport', ROOT / 'release-transport.py')
O = T.O
R = module('configs_production_receipt', ROOT / 'release-production-receipt.py')
L = module('configs_release_loader', ROOT / 'release-control-loader.py')

DRIVER = r'''
import base64,json,sys
from pathlib import Path
sys.path.insert(0,sys.argv[1])
import records,engine,adapter
root=Path(sys.argv[2]); before=int(sys.argv[3]); boundary=sys.argv[4]
config=records.parse(records.read(root/'config/operating.tsv'),'config')
transcript=adapter.document(records.read(root/'transcript.json'))
events,prior=records.history(root/'history',before,boundary) if before else records.history(root/'history')
state=engine.reduce(events,config,transcript)
print(json.dumps({'state':state,'prior':prior,'index':base64.b64encode(engine.index(state,prior)).decode()},sort_keys=True))
'''

class StartPlan:
    """Build a new durable batch using only its verified original package.

    This is a journal proposal, not bootstrap or an external-effect executor.
    A complete authenticated history must already exist. Outstanding batches
    return to their pinned Snapshot rather than adopting current configuration.
    """
    def __init__(self, entry, bundle, operating, approved, head):
        T.need(type(entry) is T.Entry and entry.authenticated, 'missing-entry')
        T.need(entry.runtime['mode']=='start' and entry.runtime['candidate']=='0'*64,
               'wrong-new-batch-request')
        self.entry, self.api = entry, entry.api
        self.head = self.expected = T.sha(head)
        T.need(self.api.ref('heads/master')==entry.trusted['source']
               and self.api.ref('heads/operations',self.api.operating)==head,
               'moving-start-source')
        jobs=self.api.jobs(entry.runtime['run'],entry.runtime['attempt'])
        T.need(len(jobs)==1 and jobs[0].get('id')==entry.runtime['job'],
               'nonisolated-start-job')
        run=self.api.run(entry.runtime['run'],entry.runtime['attempt'])
        date=run.get('run_started_at')
        T.need(isinstance(date,str) and __import__('re').fullmatch(
               r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ',date),'missing-start-time')
        O.date_epoch(date)
        self.tagger={'name':'Release controller','email':'release-controller@example.invalid','date':date}
        self.bundle,self.operating=Path(bundle),Path(operating)
        self.temporary=tempfile.TemporaryDirectory(prefix='release-start-plan-')
        self.scratch=Path(self.temporary.name)
        try:
            self.build(approved,date)
        except BaseException:
            self.close()
            raise

    def close(self):
        self.temporary.cleanup()

    def build(self, approved, date):
        self.approved = approved
        assertion=L.approved(approved)
        T.need(assertion['master']==self.entry.trusted['source']
               and assertion['protocol']=='4','unapproved-new-batch-package')
        T.need(L.git(self.operating,'rev-parse',self.head).decode().strip()==self.head,
               'missing-operating-objects')
        actual=self.api.commit(self.head,self.api.operating)
        T.need(L.git(self.operating,'rev-parse',self.head+'^{tree}').decode().strip()==actual['tree'],
               'unbound-operating-tree')
        cfg_blob,config=L.record_blob(self.operating,self.head,'config/operating.tsv')
        cfg=L.singletons(config,{'enabled','public-repository','repository','operating-repository',
               'operating-ref','workflow','actors','checks','protocol'})
        T.need(cfg['enabled']=='1' and cfg['public-repository']==T.PUBLIC
               and cfg['repository']==str(self.entry.trusted['repository-id'])
               and cfg['workflow']==str(self.entry.trusted['workflow'])
               and cfg['operating-repository']==self.api.operating and cfg['operating-ref']=='operations'
               and str(self.entry.runtime['actor']) in cfg['actors'].split(',')
               and cfg['checks']!='-' and cfg['protocol']==assertion['protocol'],'unbound-start-configuration')
        stop=L.singletons(L.record_blob(self.operating,self.head,'control/stop.tsv')[1],
                         {'stop','revision','reason','operator'})
        T.need(stop['stop']=='0','stopped-new-batch')
        request={k:str(self.entry.runtime[k]) for k in ('mode','actor','run','attempt','ref','candidate')}
        request['mode']='preview'
        source=dict(request,repository=cfg['repository'],workflow=cfg['workflow'],event='workflow_dispatch')
        source['mode']='start'
        transcript={'source':[source],'checks':[],'owner':None,'observations':{}}
        transcript_path=self.scratch/'transcript.json';transcript_path.write_bytes(T.canonical(transcript))
        request_path=self.scratch/'request.tsv';request_path.write_bytes(L.encode_index(request))
        result=L.global_preview({'operating':self.operating,'bundle_repository':self.bundle,
               'transcript':transcript_path,'request':request_path},assertion,self.head,self.scratch)
        T.need(result and result.get('outcome')=='preview' and result.get('stage') in {'empty','complete'},
               'outstanding-batch-needs-retained-owner')
        current=L.singletons(L.record_blob(self.operating,self.head,'current/index.tsv')[1],
                             L.PROJECTION_FIELDS|{'index-kind','ledger-digest'})
        contexts=L.table(L.record_blob(self.operating,self.head,'current/batches.tsv')[1])
        ledger=[]
        for index,row in enumerate(contexts):
            context=dict(zip(L.CONTEXT_FIELDS,row[1:]))
            batch=self.scratch/('batch-'+str(index));package=self.scratch/('package-'+str(index))
            first=sorted((batch/'history').iterdir())[0]
            boundary=dict((r[0],r[1]) for r in L.table(first.read_bytes()) if len(r)==2)['prior']
            projection=L.replay_package(package,batch,context['protocol'],int(context['start'])-1,boundary)[0]
            ledger.append({'context':context,'projection':T.digest(projection)})
        self.package=self.scratch/'current-package'
        # global_preview verifies/extracts this package only without an outstanding batch.
        T.need((self.package/L.ROOT/'records.py').is_file(),'missing-verified-start-package')
        before=int(current['sequence']);prior=current['prior']
        T.need(before+2<10**12,'start-sequence-bound')
        batch_id=T.digest(T.canonical({'source':assertion['master'],'control':assertion['control'],
            'config':cfg_blob,'day':date[:10],'run':self.entry.runtime['run'],'attempt':self.entry.runtime['attempt']}))
        T.need(all(row[2]!=batch_id for row in contexts),'duplicate-start-batch')
        self.batch=self.scratch/'new-batch'
        for name in ('config','history'):(self.batch/name).mkdir(parents=True,exist_ok=True)
        (self.batch/'config/operating.tsv').write_bytes(config)
        (self.batch/'transcript.json').write_bytes(T.canonical(transcript))
        first={'sequence':str(before+1),'kind':'batch-start','prior':prior,'batch':batch_id,
            'control':assertion['control'],'manifest':assertion['manifest'],'approval-provenance':assertion['approval'],
            'config':cfg_blob,'protocol':assertion['protocol'],'day':date[:10],'run':str(self.entry.runtime['run']),
            'attempt':str(self.entry.runtime['attempt']),'time':date,'approved-master':assertion['master'],'config-commit':self.head}
        raw=self.encode_event(first)
        changes={'history/%012d.tsv'%(before+1):raw}
        claim={'sequence':str(before+2),'kind':'claim','prior':T.digest(raw),'batch':batch_id,
            'repository':cfg['repository'],'workflow':cfg['workflow'],'run':str(self.entry.runtime['run']),
            'attempt':str(self.entry.runtime['attempt']),'job':str(self.entry.runtime['job']),
            'generation':'1','operating-head':self.head}
        changes['history/%012d.tsv'%(before+2)]=self.encode_event(claim)
        for path,data in changes.items():(self.batch/path).write_bytes(data)
        result=subprocess.run([sys.executable,'-I','-S','-B','-c',DRIVER,str(self.package/L.ROOT),
            str(self.batch),str(before),prior],env=L.runtime_environment(os.environ),capture_output=True,timeout=900)
        T.need(result.returncode==0 and len(result.stdout)<=T.MAX_BODY,'retained-start-projection-refusal')
        projected=T.document(result.stdout)
        simple=base64.b64decode(projected['index'],validate=True)
        context={'start':str(before+1),'batch':batch_id,'master':assertion['master'],'control':assertion['control'],
            'manifest':assertion['manifest'],'approval':assertion['approval'],'protocol':assertion['protocol'],'config-commit':self.head,
            'config':cfg_blob,'transcript-commit':'-','transcript':'-'}
        ledger.append({'context':context,'projection':T.digest(simple)})
        fields=L.singletons(simple,L.PROJECTION_FIELDS)
        fields.update({'index-kind':'global-1','ledger-digest':T.digest(T.canonical(ledger))})
        row=['context']+[context[k] for k in L.CONTEXT_FIELDS]
        changes.update({'current/index.tsv':L.encode_index(fields),'current/transcript.json':T.canonical(transcript),
            'current/batches.tsv':('format\t1\n'+''.join('\t'.join(r)+'\n' for r in contexts+[row])).encode()})
        self.pending_changes=changes

        self.approved_changes=tuple(sorted((path,T.digest(data)) for path,data in changes.items()))

    def encode_event(self, fields):
        return Snapshot.encode_event(self,fields)

    def validate_changes(self, changes):
        T.need(self.pending_changes is not None and changes==self.pending_changes
               and tuple(sorted((path,T.digest(data)) for path,data in changes.items()))==self.approved_changes,
               'unprojected-start-changes')
        T.need(self.api.ref('heads/master')==self.entry.trusted['source']
               and self.api.ref('heads/operations',self.api.operating)==self.head,'moving-start-head')
        return self.validate_prospective(changes)

    def validate_prospective(self, changes):
        self.assertion = L.approved(self.approved)
        return Snapshot.validate_prospective(self, changes)

    def hydrate(self, prospective, changes):
        return Snapshot.hydrate(self, prospective, changes)

    def accept_changes(self, changes, head):
        self.expected=self.head=head
        self.pending_changes=None

class Snapshot:
    """A whole-history verified, source-bound projector with no credentials."""
    def __init__(self, entry, bundle, operating, approved, head, tagger, requirements, *, qualification=None, receipts=None):
        self.entry, self.api = entry, entry.api
        T.need(type(entry) is T.Entry and entry.authenticated, 'missing-entry')
        self.source = entry.trusted['source']
        T.need(self.api.ref('heads/master') == self.source, 'untrusted-control-head')
        T.need(self.api.ref('heads/operations', self.api.operating) == head, 'stale-history-head')
        self.expected = T.sha(head)
        T.need(set(tagger) == {'name','email','date'} and tagger['name'] == 'Release controller'
               and tagger['email'] == 'release-controller@example.invalid'
               and __import__('re').fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ',tagger['date']), 'unfixed-record-tagger')
        O.date_epoch(tagger['date'])
        self.tagger, self.requirements = dict(tagger), copy.deepcopy(requirements)
        self.qualification=self.qualification_bytes=qualification
        T.need(receipts is None or type(receipts) is R.Collector, 'invalid-typed-receipt-collector')
        self.receipts=receipts
        self.temporary = tempfile.TemporaryDirectory(prefix='release-transport-retained-')
        self.scratch = Path(self.temporary.name)
        self.bundle, self.operating = Path(bundle), Path(operating)
        self.approved = approved
        assertion = L.approved(approved)
        # Bootstrap is an independently reviewed deployment input. In fixtures it
        # is synthetic; a private API response cannot invent bootstrap approval.
        T.need(assertion['master'] == self.source, 'unbound-approved-master')
        self.head = head
        try:
            self.load()
        except BaseException:
            self.close()
            raise

    def close(self):
        self.temporary.cleanup()

    def load(self):
        op = self.api.commit(self.head, self.api.operating)
        entries = self.api.tree(op['tree'], self.api.operating)
        T.need('current/transcript.json' in entries and entries['current/transcript.json'][:2] == ('100644','blob'), 'missing-retained-transcript')
        transcript = self.api.blob(entries['current/transcript.json'][2],self.api.operating)
        # Local object history is checked against the independently observed remote
        # full commit identity. Git hashes and graph checks bind all retained bytes.
        T.need(L.git(self.operating,'rev-parse',self.head).decode().strip()==self.head,'missing-operating-objects')
        self.assertion = L.approved(self.approved)
        transcript_path=self.scratch/'authenticated-transcript.json'; transcript_path.write_bytes(transcript)
        approved_path=self.scratch/'approved.tsv'; approved_path.write_bytes(self.approved)
        dto=T.document(transcript)
        T.need(isinstance(dto.get('source'),list) and dto['source'],'missing-retained-request')
        source=dto['source'][-1]
        request={k:str(source[k]) for k in ('mode','actor','run','attempt','ref','candidate')}
        request['mode']='preview'
        request_path=self.scratch/'request.tsv';request_path.write_bytes(L.encode_index(request))
        summary=L.global_preview({'operating':self.operating,'bundle_repository':self.bundle,
                  'transcript':transcript_path,'request':request_path},self.assertion,self.head,self.scratch)
        T.need(summary and summary.get('stage') not in {'empty','complete'} and summary.get('outcome') in {'preview','stopped'},'no-operable-outstanding-batch')
        batches=sorted(self.scratch.glob('batch-*'),key=lambda p:int(p.name.split('-')[-1]))
        T.need(batches,'missing-selected-batch')
        self.batch=batches[-1]; self.package=self.scratch/('package-'+self.batch.name.split('-')[-1])
        contexts=L.table(L.record_blob(self.operating,self.head,'current/batches.tsv')[1])
        context=dict(zip(L.CONTEXT_FIELDS,contexts[-1][1:]));self.before=int(context['start'])-1
        self.protocol=context['protocol'];self.owner_source=context['master']
        self.control=context['control'];self.manifest=context['manifest']
        events=sorted((self.batch/'history').iterdir())
        framing=L.singletons(events[0].read_bytes(),set()) if not events else dict((r[0],r[1]) for r in L.table(events[0].read_bytes()) if len(r)==2)
        self.boundary=framing['prior']
        # Existing batches retain their original authority/configuration. Current
        # config may disable later work; only fresh stop/credential revocation is live.
        self.pinned_config=L.singletons((self.batch/'config/operating.tsv').read_bytes(),
               {'enabled','public-repository','repository','operating-repository','operating-ref','workflow','actors','checks','protocol'})
        config=self.pinned_config
        T.need(config['enabled']=='1' and config['public-repository']==T.PUBLIC
               and config['operating-repository']==self.api.operating and config['operating-ref']=='operations'
               and config['repository']==str(self.entry.trusted['repository-id'])
               and config['workflow']==str(self.entry.trusted['workflow'])
               and str(self.entry.runtime['actor']) in config['actors'].split(','),'unbound-pinned-authority')
        self.original_transcript=transcript
        self.state=self.project()['state']
        self.pending_changes=None

    def project(self):
        result=subprocess.run([sys.executable,'-I','-S','-B','-c',DRIVER,str(self.package/L.ROOT),str(self.batch),str(self.before),self.boundary],
             env=L.runtime_environment(os.environ),capture_output=True,timeout=900)
        T.need(result.returncode==0 and len(result.stdout)<=T.MAX_BODY,'retained-transport-projection-refusal')
        value=T.document(result.stdout)
        T.need(set(value)=={'state','prior','index'},'invalid-transport-projection')
        return value

    def plan(self, operation):
        T.need(operation in self.state['operations'],'unknown-retained-operation')
        op=self.state['operations'][operation]
        T.need(op['state'] in {'intent','unknown'},'completed-or-conflicting-operation')
        return {'id':operation,'digest':T.digest(T.canonical(op['payload'])),'head':self.head}

    def proposal_context(self,state):
        """Fresh actual entry/owner/head/stop; caller data supplies none of these."""
        T.Entry(self.api,self.entry.trusted,self.entry.runtime)
        runtime=self.entry.runtime
        jobs=self.api.jobs(runtime['run'],runtime['attempt'])
        T.need(len(jobs)==1 and jobs[0].get('id')==runtime['job'],'nonisolated-proposal-job')
        T.need(self.api.ref('heads/master')==self.source
               and self.api.ref('heads/operations',self.api.operating)==self.head==self.expected,'moving-proposal-head')
        owner=state['owner']
        T.need(owner and all(int(owner[k])==runtime[k] for k in ('run','attempt','job')),'foreign-proposal-owner')
        self.owner_target(owner)
        candidate=state['candidate'] or state.get('refresh')
        T.need(runtime['candidate']==(T.digest(T.canonical(candidate)) if candidate else '0'*64),'stale-proposal-candidate')
        tree=self.api.tree(self.api.commit(self.head,self.api.operating)['tree'],self.api.operating)
        T.need(tree.get('control/stop.tsv',())[:2]==('100644','blob'),'missing-proposal-stop')
        T.need(not self.validate_stop(self.api.blob(tree['control/stop.tsv'][2],self.api.operating),self.head),
               'stopped-proposal')

    def validate_prospective(self,changes):
        """Owned local copy; full replay is validation, never a remote receipt."""
        deadline=__import__('time').monotonic()+900
        with tempfile.TemporaryDirectory(dir=self.scratch,prefix='proposal-replay-') as folder:
            root=Path(folder);repo=root/'objects.git';empty=root/'empty';empty.mkdir()
            L.verify_graphs(self.operating,[self.head])
            # Local pack plumbing only. No clone/fetch/URL, alternate or hook.
            packed=O.bounded_git(self.operating,['-c','pack.threads=1','-c','pack.windowMemory=8m',
                'pack-objects','--quiet','--stdout','--revs'],L.runtime_environment(os.environ)|{
                'GIT_CONFIG_NOSYSTEM':'1','GIT_CONFIG_GLOBAL':os.devnull,'GIT_ALLOW_PROTOCOL':'',
                'GIT_NO_REPLACE_OBJECTS':'1','GIT_NO_LAZY_FETCH':'1','GIT_GRAFT_FILE':os.devnull},
                data=(self.head+'\n').encode(),limit=128*1024*1024,deadline=deadline)
            T.need(len(packed)<=128*1024*1024,'proposal-object-bound')
            L.git(root,'init','--bare','--template='+str(empty),str(repo))
            L.git(repo,'index-pack','--stdin','--strict',data=packed)
            index=root/'index'
            env=L.runtime_environment(os.environ)
            env.update(GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL=os.devnull,
                GIT_NO_REPLACE_OBJECTS='1',GIT_NO_LAZY_FETCH='1',GIT_GRAFT_FILE=os.devnull,
                GIT_ALLOW_PROTOCOL='',GIT_TERMINAL_PROMPT='0',GIT_INDEX_FILE=str(index),
                GIT_AUTHOR_NAME=self.tagger['name'],GIT_AUTHOR_EMAIL=self.tagger['email'],
                GIT_COMMITTER_NAME=self.tagger['name'],GIT_COMMITTER_EMAIL=self.tagger['email'],
                GIT_AUTHOR_DATE=self.tagger['date'],GIT_COMMITTER_DATE=self.tagger['date'])
            def raw_local(*args,data=None,limit=T.MAX_BODY):
                return O.bounded_git(repo,list(args),env,data=data,limit=limit,deadline=deadline)
            def local(*args,data=None):
                return raw_local(*args,data=data).decode('ascii').strip()
            local('read-tree',self.head)
            for path,data in sorted(changes.items()):
                oid=local('hash-object','-w','--stdin',data=data)
                T.need(oid==T.git_object('blob',data),'proposal-local-blob-mismatch')
                local('update-index','--add','--cacheinfo','100644,'+oid+','+path)
            tree=local('write-tree')
            head=local('commit-tree',tree,'-p',self.head,data=b'release operating record\n')
            transcript_bytes=changes.get('current/transcript.json',L.record_blob(self.operating,self.head,'current/transcript.json')[1])
            source=T.document(transcript_bytes)['source'][-1]
            request_fields={k:str(source[k]) for k in ('actor','run','attempt','ref','candidate')}
            request_fields['mode']='preview'
            request=root/'request.tsv';request.write_bytes(L.encode_index(request_fields))
            transcript=root/'transcript.json';transcript.write_bytes(transcript_bytes)
            replay=root/'replay';replay.mkdir()
            L.global_preview({'operating':repo,'bundle_repository':self.bundle,
                'request':request,'transcript':transcript},self.assertion,head,replay)
            names=local('rev-list','--objects',head,'^'+self.head).splitlines()
            T.need(len(names)<=20000,'prospective-object-count')
            objects=[];total=0
            for row in names:
                identity=T.sha(row.split()[0]);kind=local('cat-file','-t',identity)
                size=int(local('cat-file','-s',identity))
                T.need(kind in {'blob','tree','commit'} and 0<=size<=T.MAX_BODY,'prospective-object-size')
                total+=size;T.need(total<=128*1024*1024,'prospective-closure-bound')
                raw=raw_local('cat-file',kind,identity,limit=max(1,size))
                T.need(len(raw)==size and T.git_object(kind,raw)==identity,'prospective-object-identity')
                objects.append((kind,identity,raw))
            self.prospective={'parent':self.head,'head':head,'tree':tree,'objects':tuple(objects),
                'changes':tuple(sorted((p,T.digest(d)) for p,d in changes.items()))}
            return self.prospective

    def hydrate(self, prospective, changes):
        """Only retained hash-verified originals, no remote fetch or checkout."""
        T.need(prospective is self.prospective and prospective['parent']==self.head
            and prospective['changes']==tuple(sorted((p,T.digest(d)) for p,d in changes.items())),
            'changed-prospective-delivery')
        objects=prospective['objects'];T.need(type(objects) is tuple and 1<=len(objects)<=20000,'delivery-object-count')
        total=0;seen=set();deadline=__import__('time').monotonic()+900
        env=L.runtime_environment(os.environ)|{'GIT_CONFIG_NOSYSTEM':'1','GIT_CONFIG_GLOBAL':os.devnull,
            'GIT_ALLOW_PROTOCOL':'','GIT_NO_REPLACE_OBJECTS':'1','GIT_NO_LAZY_FETCH':'1','GIT_GRAFT_FILE':os.devnull}
        for kind,identity,raw in objects:
            T.sha(identity);T.need(kind in {'blob','tree','commit'} and type(raw) is bytes
                and len(raw)<=T.MAX_BODY and identity not in seen
                and T.git_object(kind,raw)==identity,'corrupt-retained-delivery')
            seen.add(identity);total+=len(raw);T.need(total<=128*1024*1024,'delivery-byte-bound')
        T.need(prospective['head'] in seen,'missing-retained-child')
        for kind,identity,raw in objects:
            actual=O.bounded_git(self.operating,['hash-object','-t',kind,'-w','--stdin'],env,
                data=raw,limit=128,deadline=deadline).decode().strip()
            T.need(actual==identity,'local-delivery-identity')
        L.verify_graphs(self.operating,[prospective['head']])
        raw=L.git(self.operating,'cat-file','commit',prospective['head'])
        fields=O.commit_fields(raw)
        T.need(T.git_object('commit',raw)==prospective['head'] and fields['tree']==prospective['tree']
            and fields['parents']==[self.head],'local-child-parent')
        source=T.document(changes.get('current/transcript.json',
            L.record_blob(self.operating,self.head,'current/transcript.json')[1]))['source'][-1]
        with tempfile.TemporaryDirectory(dir=self.scratch,prefix='delivery-replay-') as directory:
            root=Path(directory);request=root/'request';transcript=root/'transcript'
            request.write_bytes(L.encode_index(dict({k:str(source[k]) for k in
                ('actor','run','attempt','ref','candidate')},mode='preview')))
            transcript.write_bytes(changes.get('current/transcript.json',
                L.record_blob(self.operating,self.head,'current/transcript.json')[1]))
            L.global_preview({'operating':self.operating,'bundle_repository':self.bundle,
                'request':request,'transcript':transcript},self.assertion,prospective['head'],root)
        return prospective['head']

    def public_merge_tree(self,candidate):
        """Original object data only; merge plumbing owns a credential-free bare copy."""
        heads=[T.sha(candidate[k]) for k in ('master','dev')]
        T.need(L.git(self.bundle,'rev-parse','--show-object-format').strip()==b'sha1'
            and L.git(self.bundle,'rev-parse','--is-shallow-repository').strip()==b'false',
            'incomplete-candidate-objects')
        L.verify_graphs(self.bundle,heads)
        for head in heads:
            raw=L.git(self.bundle,'cat-file','commit',head)
            T.need(T.git_object('commit',raw)==head,'corrupt-candidate-commit')
            header=raw.split(b'\n\n',1)[0].decode('utf-8').splitlines()
            trees=[row[5:] for row in header if row.startswith('tree ')]
            parents=[row[7:] for row in header if row.startswith('parent ')]
            observed=self.api.commit(head)
            T.need(trees==[observed['tree']] and parents==observed['parents'],'unbound-candidate-commit')
        packed=L.git(self.bundle,'-c','pack.threads=1','-c','pack.windowMemory=8m',
                     'pack-objects','--quiet','--stdout','--revs',data=('\n'.join(heads)+'\n').encode())
        T.need(len(packed)<=128*1024*1024,'candidate-object-bound')
        with tempfile.TemporaryDirectory(dir=self.scratch,prefix='candidate-tree-') as folder:
            root=Path(folder);repo=root/'objects.git';empty=root/'empty';empty.mkdir()
            env=L.runtime_environment(os.environ)
            env.update(GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL=os.devnull,
                GIT_NO_REPLACE_OBJECTS='1',GIT_NO_LAZY_FETCH='1',GIT_GRAFT_FILE=os.devnull,
                GIT_ALLOW_PROTOCOL='',GIT_TERMINAL_PROMPT='0',GIT_ATTR_NOSYSTEM='1')
            def local(*args,data=None):
                result=subprocess.run(['git','--no-replace-objects','-c','core.hooksPath='+str(empty),
                    '-c','core.fsmonitor=false','-c','core.attributesFile='+os.devnull,'-c','gc.auto=0',
                    '-C',str(root),*args],input=data,env=env,capture_output=True,timeout=30)
                T.need(result.returncode==0 and len(result.stdout)<=T.MAX_BODY,'candidate-merge-refused')
                return result.stdout
            local('init','--bare','--template='+str(empty),str(repo))
            local('-C',str(repo),'index-pack','--stdin','--strict',data=packed)
            local('-C',str(repo),'fsck','--no-dangling','--no-reflogs','--no-progress',*heads)
            tree=local('-C',str(repo),'merge-tree','--write-tree','--no-messages',*heads).decode('ascii').strip()
            return T.sha(tree)

    def qualification_input(self):
        """A pinned review assertion, never proof that a maintainer adopted it."""
        raw=self.qualification
        T.need(type(raw) is bytes and raw==self.qualification_bytes,'changed-qualification-input')
        value=T.document(raw)
        T.need(type(value) is dict and set(value)=={'format','control','manifest','baselines',
            'baselines-digest','requirements-digest','binding'} and type(value['format']) is int
            and value['format']==1,'invalid-qualification-input')
        T.need(value['control']==self.control and value['manifest']==self.manifest,
            'foreign-qualification-package')
        body={k:v for k,v in value.items() if k!='binding'}
        T.need(T.digest(T.canonical(body))==value['binding'],'unbound-qualification-input')
        try:baseline=base64.b64decode(value['baselines'],validate=True)
        except (ValueError,TypeError):raise T.Refusal('invalid-qualification-baselines') from None
        T.need(0<len(baseline)<=T.MAX_BODY and T.digest(baseline)==value['baselines-digest']
            and T.digest(T.canonical(self.requirements))==value['requirements-digest'],
            'changed-qualification-bytes')
        return baseline

    def original_public_commit(self,head):
        raw=L.git(self.bundle,'cat-file','commit',T.sha(head))
        T.need(len(raw)<=T.MAX_BODY and T.git_object('commit',raw)==head,'corrupt-qualification-commit')
        headers=raw.split(b'\n\n',1)[0].decode('utf-8').splitlines()
        trees=[v[5:] for v in headers if v.startswith('tree ')]
        parents=[v[7:] for v in headers if v.startswith('parent ')]
        actual=self.api.commit(head)
        T.need(trees==[actual['tree']] and parents==actual['parents'],'unbound-qualification-commit')
        return actual

    def qualification_objects(self,baseline):
        """Original baseline and semantic bytes bound to existing finite GETs."""
        import re
        from datetime import datetime,timezone
        roots=[self.control]
        control=self.original_public_commit(self.control)
        entries=self.api.tree(control['tree'])
        for name in sorted(L.FILES|{L.MANIFEST}):
            metadata=L.git(self.bundle,'ls-tree',self.control,'--',name).decode('ascii').strip().split()
            T.need(len(metadata)==4 and metadata[:2] in (['100644','blob'],['100755','blob'])
                and metadata[3]==name and entries.get(name)==(metadata[0],'blob',metadata[2]),
                'unbound-qualification-package-blob')
            raw=L.git(self.bundle,'cat-file','blob',metadata[2])
            T.need(len(raw)<=T.MAX_BODY and T.git_object('blob',raw)==metadata[2]
                and self.api.blob(metadata[2])==raw,'corrupt-qualification-package-blob')
            if name!=L.MANIFEST:
                T.need((self.package/name).read_bytes()==raw,'changed-extracted-qualifier')
            else:T.need(T.digest(raw)==self.manifest,'changed-qualification-manifest')
        rows=L.table(baseline)
        T.need(rows,'missing-qualification-baseline')
        seen=set()
        for row in rows:
            T.need(len(row)==5 and row[1] in {'unixlike','windows'} and row[1] not in seen,
                'invalid-qualification-baseline')
            seen.add(row[1]);kind,domain,value,target,reference=row
            if kind=='semantic':
                tag=T.sha(reference);raw=L.git(self.bundle,'cat-file','tag',tag)
                T.need(len(raw)<=T.MAX_BODY and T.git_object('tag',raw)==tag,'corrupt-baseline-tag')
                header,separator,message=raw.partition(b'\n\n')
                T.need(separator,'invalid-baseline-tag')
                fields=header.decode('utf-8').splitlines()
                T.need(len(fields)==4 and fields[1]=='type commit' and fields[2]=='tag '+target,
                    'unsupported-baseline-tag')
                head=T.sha(fields[0].removeprefix('object '))
                match=re.fullmatch(r'tagger ([^<>\n]+) <([^<>\n]+)> ([0-9]+) ([+-][0-9]{4})',fields[3])
                T.need(match,'unsupported-baseline-tagger')
                date=datetime.fromtimestamp(int(match[3]),timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
                actual=self.api.get('/git/tags/'+tag)
                T.need(actual.get('sha')==tag and actual.get('tag')==target
                    and actual.get('object',{}).get('type')=='commit'
                    and actual['object'].get('sha')==head and actual.get('message')==message.decode('utf-8')
                    and actual.get('tagger')=={'name':match[1],'email':match[2],'date':date},
                    'unbound-baseline-tag')
                self.original_public_commit(head);roots.extend([head,tag])
            elif kind=='bootstrap':
                self.original_public_commit(T.sha(value))
                commit=self.original_public_commit(T.sha(target))
                tree=self.api.tree(commit['tree'])
                T.need(reference in tree and tree[reference][:2]==('100644','blob'),'unbound-bootstrap-record')
                blob=tree[reference][2];raw=L.git(self.bundle,'show',target+':'+reference)
                T.need(len(raw)<=T.MAX_BODY and T.git_object('blob',raw)==blob
                    and self.api.blob(blob)==raw,'corrupt-bootstrap-record')
                roots.extend([value,target])
            else:raise T.Refusal('unsupported-qualification-baseline')
        return sorted(set(roots))

    def candidate_context(self,comparison,before):
        baseline=self.qualification_input()
        self.proposal_context(before)
        T.need(self.api.ref('heads/master')==comparison['master']
            and self.api.ref('heads/dev')==comparison['dev'],'moving-candidate-source')
        roots=self.qualification_objects(baseline)
        T.need(self.public_merge_tree(comparison)==comparison['tree'],'moving-candidate-tree')
        T.need(self.api.ref('heads/master')==comparison['master']
            and self.api.ref('heads/dev')==comparison['dev'],'moving-candidate-source')
        self.proposal_context(before)
        return baseline,roots

    def candidate_preview(self,comparison,baseline,roots,evidence):
        """Run only verified original tools against an owned no-checkout object copy."""
        heads=sorted(set(roots+[comparison['dev'],comparison['master']]))
        L.verify_graphs(self.bundle,[h for h in heads if L.git(self.bundle,'cat-file','-t',h).strip()==b'commit'])
        packed=L.git(self.bundle,'-c','pack.threads=1','-c','pack.windowMemory=8m',
            'pack-objects','--quiet','--stdout','--revs',data=('\n'.join(heads)+'\n').encode())
        T.need(len(packed)<=128*1024*1024,'qualification-object-bound')
        with tempfile.TemporaryDirectory(dir=self.scratch,prefix='candidate-preview-') as folder:
            root=Path(folder);repo=root/'source';empty=root/'empty';empty.mkdir()
            L.git(root,'init','--template='+str(empty),str(repo))
            L.git(repo,'index-pack','--stdin','--strict',data=packed)
            baseline_path=root/'baselines.tsv';baseline_path.write_bytes(baseline)
            evidence_path=root/'evidence.tsv';evidence_path.write_bytes(evidence)
            env=L.runtime_environment(os.environ)
            env.update(GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL=os.devnull,
                GIT_NO_REPLACE_OBJECTS='1',GIT_NO_LAZY_FETCH='1',GIT_GRAFT_FILE=os.devnull,
                GIT_ALLOW_PROTOCOL='',GIT_TERMINAL_PROMPT='0',GIT_ATTR_NOSYSTEM='1',LC_ALL='C')
            result=subprocess.run(['sh',(self.package/'tool/version-control/release-preview').as_posix(),
                '--production','--master',comparison['master'],'--candidate',comparison['dev'],
                '--rules',self.control,'--baselines',baseline_path.as_posix(),
                '--evidence',evidence_path.as_posix(),'--json'],cwd=repo,env=env,
                capture_output=True,timeout=120)
            T.need(result.returncode in {0,1} and len(result.stdout)<=T.MAX_BODY,'qualification-preview-unavailable')
            value=T.document(result.stdout)
            T.need(type(value) is dict and type(value.get('format')) is int and value['format']==1
                and value.get('qualification')=='offline-production' and value.get('production_certification') is False
                and value.get('evidence_authority')=='asserted-offline'
                and value.get('master')==comparison['master'] and value.get('candidate')==comparison['dev']
                and value.get('merge_tree')==comparison['tree'] and value.get('rules')==self.control,
                'unbound-production-preview')
            rules=(self.package/'tool/version-control/release-preview.rules').read_bytes()
            engine=(self.package/'tool/version-control/release-preview').read_bytes()+(self.package/'tool/version-control/release-preview.awk').read_bytes()
            T.need(value.get('rules_digest')==T.git_object('blob',rules)
                and value.get('baselines_digest')==T.git_object('blob',baseline)
                and value.get('engine_digest')==T.git_object('blob',engine)
                and value.get('classifier_digest')==T.git_object('blob',(self.package/'tool/version-control/classify').read_bytes())
                and value.get('evidence_digest')==T.git_object('blob',evidence),'changed-production-preview-tools')
            return result.returncode,value

    def candidate_decision(self,value):
        fields={k:copy.deepcopy(v) for k,v in value.items() if k not in {'decision','reasons','evidence_digest','checks'}}
        T.need(type(value.get('checks')) is list and value['checks'],'empty-candidate-selection')
        fields['checks']=[{k:v for k,v in row.items() if k not in {'state','reference'}} for row in value['checks']]
        return T.canonical(fields)

    def typed_collect(self,comparison,baseline,checks,historical=None):
        try:
            return self.receipts.collect(self,comparison,baseline,checks,historical)
        except R.T.Refusal as error:
            raise T.Refusal(error.args[0]) from None

    def candidate_receipts(self,comparison,baseline,checks):
        if self.receipts is None:
            return self.entry.evidence(comparison['dev'],comparison['tree'],self.requirements),None,[]
        return self.typed_collect(comparison,baseline,checks)

    def propose_candidate(self):
        """Derive selection, observe receipts and qualify; accept no supplied event."""
        T.need(not getattr(self,'proposal_fenced',False) and self.pending_changes is None,'outstanding-proposal')
        try:
            before=self.project()['state'];self.proposal_context(before)
            comparison={'dev':self.api.ref('heads/dev'),'master':self.api.ref('heads/master')}
            comparison['tree']=self.public_merge_tree(comparison)
            baseline,roots=self.candidate_context(comparison,before)
            code,diagnostic=self.candidate_preview(comparison,baseline,roots,b'format\t1\n')
            if code==0 and diagnostic.get('decision')=='no-op':return {}
            T.need(code==1 and diagnostic.get('decision')=='refusal'
                and (diagnostic.get('reasons')==['missing-required-evidence'] or
                     (self.receipts is not None and set(diagnostic.get('reasons',[]))=={'missing-required-evidence','missing-template-pair'})),
                'candidate-qualification-refusal')
            decision=self.candidate_decision(diagnostic);checks=diagnostic['checks']
            ids=[r.get('id') for r in checks]
            T.need(all(isinstance(i,str) and __import__('re').fullmatch('[a-z0-9][a-z0-9-]*',i) for i in ids)
                and ids==sorted(set(ids)) and (self.receipts is not None or
                ({r['id'] for r in self.requirements}==set(ids) and len(self.requirements)==len(ids))),'incomplete-candidate-trust-set')
            required={r['id']:r for r in self.requirements}
            T.need(self.receipts is not None or all(r.get('lane')!='review' and r.get('requiredness')=='required'
                and r.get('expected_tool')==required[r['id']]['tool'] for r in checks),'unsupported-candidate-check')
            receipts,pair,binding=self.candidate_receipts(comparison,baseline,checks)
            rows=[['evidence',r['id'],comparison['dev'],comparison['master'],comparison['tree'],self.control,
                r['tool'],'verified','https://github.com/'+T.PUBLIC+'/actions/runs/'+str(r['run'])+'/job/'+str(r['job'])]
                for r in sorted(receipts,key=lambda r:r['id'])]
            evidence=b'format\t1\n'+b''.join(('\t'.join(row)+'\n').encode('utf-8') for row in rows)
            if pair is not None:
                evidence+=('\t'.join(['template-pair','unixlike',pair['repository'],pair['revision'],pair['provider'],'delivered','verified'])+'\n').encode('utf-8')
            self.candidate_context(comparison,before)
            T.need(self.candidate_receipts(comparison,baseline,checks)==(receipts,pair,binding),'moving-candidate-receipts')
            code,final=self.candidate_preview(comparison,baseline,roots,evidence)
            T.need(code==0 and final.get('decision')=='candidate' and final.get('reasons')==[]
                and self.candidate_decision(final)==decision
                and all(r.get('state')=='verified' for r in final['checks']),'changed-candidate-qualification')
            releases=[r for r in final['domains'] if r.get('next_version') is not None]
            impacts={'patch':1,'minor':2,'major':3}
            T.need(releases and all(r.get('impact') in impacts and r.get('domain') in {'unixlike','windows'}
                for r in releases),'unrepresentable-candidate-impact')
            versions=','.join(r['domain']+':'+r['next_version'] for r in sorted(releases,key=lambda r:r['domain']))
            migrations=sorted({p for r in releases for p in r['migrations']})
            candidate=dict(comparison,**{'candidate-generation':str(int(before['promotion-generation'])+1),
                'rules':T.digest((self.package/'tool/version-control/release-preview.rules').read_bytes()),
                'tool':self.manifest,'baselines':T.digest(baseline),'selected':','.join(ids),
                'classification':max((r['impact'] for r in releases),key=impacts.get),
                'versions':versions,'migrations':','.join(migrations) or '-',
                'approval-required':'1' if final['approval_reasons'] else '0'})
            transcript=T.document((self.batch/'transcript.json').read_bytes())
            runtime=self.entry.runtime
            request={k:str(runtime[k]) for k in ('actor','run','attempt','ref')}
            # Original replay request framing; actual start/wake is checked independently.
            request.update(mode='preview',candidate=T.digest(T.canonical(candidate)),
                repository=str(self.entry.trusted['repository-id']),workflow=str(self.entry.trusted['workflow']),event='workflow_dispatch')
            transcript['source'].append(request)
            changes=self.propose_event(dict(candidate,kind='candidate'),transcript)
            self.candidate_binding=(copy.deepcopy(comparison),copy.deepcopy(before),copy.deepcopy((receipts,pair,binding,checks)))
            self.validate_collected_candidate()
            return changes
        except (ValueError,TypeError,KeyError,IndexError,OSError,subprocess.SubprocessError) as error:
            self.proposal_fenced=True
            if isinstance(error,T.Refusal):raise
            raise T.Refusal('candidate-observation-unavailable') from None
        except BaseException:
            self.proposal_fenced=True
            raise

    def validate_collected_candidate(self):
        binding=getattr(self,'candidate_binding',None)
        if binding is None:return
        try:
            comparison,before,saved=binding
            receipts,pair,observation,checks=saved
            baseline,_=self.candidate_context(comparison,before)
            T.need(self.candidate_receipts(comparison,baseline,checks)==(receipts,pair,observation),
                'moving-candidate-receipts')
            self.candidate_context(comparison,before)
        except BaseException:
            self.proposal_fenced=True
            raise

    def evidence_context(self,candidate,requirements):
        T.need(T.canonical(self.requirements)==requirements,'changed-evidence-trust-set')
        state=self.project()['state']
        T.need(state['candidate']==candidate,'changed-evidence-candidate')
        self.proposal_context(state)
        T.need(self.api.ref('heads/master')==candidate['master']
            and self.api.ref('heads/dev')==candidate['dev'],'moving-evidence-source')
        T.need(self.public_merge_tree(candidate)==candidate['tree'],'wrong-candidate-merge-tree')
        T.need(self.api.ref('heads/master')==candidate['master']
            and self.api.ref('heads/dev')==candidate['dev'],'moving-evidence-source')

    def collected_evidence(self,candidate,requirements):
        self.evidence_context(candidate,requirements)
        if self.receipts is None:
            receipts=self.entry.evidence(candidate['dev'],candidate['tree'],self.requirements)
        else:
            baseline=self.qualification_input()
            T.need(T.digest(baseline)==candidate['baselines'],'changed-evidence-baseline')
            checks=self.typed_checks(candidate,baseline)
            T.need([r['id'] for r in checks]==candidate['selected'].split(','),'changed-evidence-producer-set')
            transcript=T.document((self.batch/'transcript.json').read_bytes())
            typed={p['id'] for p in self.receipts.producers if p['kind']!='actions'}
            old=[r for r in transcript['checks'] if r[0] in typed and r[1:6]==[candidate[k] for k in ('dev','master','tree','rules','tool')]]
            receipts,_,_=self.typed_collect({k:candidate[k] for k in ('dev','master','tree')},baseline,checks,old or None)
        self.evidence_context(candidate,requirements)
        return receipts

    def propose_evidence(self):
        """No supplied rows: independently acquire a reviewed candidate's exact checks."""
        T.need(not getattr(self,'proposal_fenced',False) and self.pending_changes is None,'outstanding-proposal')
        try:
            state=self.project()['state'];candidate=copy.deepcopy(state['candidate'])
            T.need(candidate and state['stage']=='candidate','no-candidate-awaiting-evidence')
            selected=candidate['selected'].split(',')
            T.need(len(set(selected))==len(selected) and (self.receipts is not None or
                (self.requirements and len(self.requirements)==len(selected) and {r['id'] for r in self.requirements}==set(selected))),'incomplete-evidence-trust-set')
            requirements=T.canonical(self.requirements)
            receipts=self.collected_evidence(candidate,requirements)
            rows=[[r['id']]+[candidate[k] for k in ('dev','master','tree','rules','tool')]
                +['verified',str(r['run']),str(r['attempt']),str(r['job']),r['tool']]
                for r in sorted(receipts,key=lambda r:r['id'])]
            transcript=T.document((self.batch/'transcript.json').read_bytes())
            for row in rows:
                count=transcript['checks'].count(row)
                T.need(count<=1,'ambiguous-retained-evidence')
                if not count:transcript['checks'].append(row)
            T.need(self.collected_evidence(candidate,requirements)==receipts,'moving-evidence-receipts')
            changes=self.propose_event({'kind':'evidence','evidence':rows,
                'evidence-digest':T.digest(T.canonical(rows))},transcript)
            self.evidence_binding=(candidate,requirements,copy.deepcopy(receipts))
            self.validate_collected_evidence()
            return changes
        except BaseException:
            self.proposal_fenced=True
            raise

    def validate_collected_evidence(self):
        binding=getattr(self,'evidence_binding',None)
        if binding is None:return
        try:
            candidate,requirements,receipts=binding
            T.need(self.collected_evidence(candidate,requirements)==receipts,'moving-evidence-receipts')
        except BaseException:
            self.proposal_fenced=True
            raise

    def propose_event(self,fields,transcript):
        """Trusted library caller only; this does not authenticate supplied data."""
        T.need(not getattr(self,'proposal_fenced',False) and self.pending_changes is None,'outstanding-proposal')
        try:
            T.need(self.entry.runtime['mode'] in {'start','wake'} and type(fields) is dict
                and fields.get('kind') in {'candidate','evidence','refresh-result','refresh-integrated',
                    'intent','retry-wait','blocker','complete'}
                and not {'sequence','prior','batch'} & set(fields),'unsupported-proposal-event')
            before=self.project();self.proposal_context(before['state'])
            old=T.document((self.batch/'transcript.json').read_bytes())
            transcript=copy.deepcopy(transcript)
            T.need(type(transcript) is dict and set(old)<=set(transcript)<=set(old)|{'refresh','protection'},'changed-transcript-shape')
            T.need(len(T.canonical(transcript))<=T.MAX_BODY,'proposal-transcript-bound')
            if 'refresh' in transcript and 'refresh' not in old:
                T.need(type(transcript['refresh']) is dict and set(transcript['refresh'])=={'revisions','current'}
                    and type(transcript['refresh']['revisions']) is list,'invalid-new-refresh-view')
            if 'protection' in transcript and 'protection' not in old:
                T.need(type(transcript['protection']) is dict,'invalid-new-protection-view')
            for key in old:
                if key in {'source','checks'}:
                    T.need(type(transcript[key]) is list and transcript[key][:len(old[key])]==old[key],
                           'rewritten-transcript-history')
                elif key=='observations':
                    T.need(type(transcript[key]) is dict and all(transcript[key].get(k)==v for k,v in old[key].items()),
                           'rewritten-transcript-observation')
                elif key=='refresh':
                    T.need(type(transcript[key]) is dict and set(transcript[key])=={'revisions','current'}
                        and type(transcript[key]['revisions']) is list
                        and transcript[key]['revisions'][:len(old[key]['revisions'])]==old[key]['revisions'],
                        'rewritten-refresh-history')
                else:T.need(transcript[key]==old[key],'rewritten-transcript-binding')
            sequence=int(before['state']['sequence'])+1
            T.need(sequence<10**12,'proposal-sequence-bound')
            event=copy.deepcopy(fields)
            event.update(sequence=str(sequence),prior=before['prior'],batch=before['state']['batch'])
            raw=self.encode_event(event);path='history/%012d.tsv'%sequence
            (self.batch/path).write_bytes(raw);(self.batch/'transcript.json').write_bytes(T.canonical(transcript))
            changes=self.projected_changes(path,raw,transcript)
            self.validate_prospective(changes);self.proposal_context(before['state'])
            self.pending_changes=changes
            self.proposal_binding=tuple(sorted((p,T.digest(d)) for p,d in changes.items()))
            self.proposal_before=before['state']
            return changes
        except BaseException:
            self.proposal_fenced=True
            raise

    def claim(self):
        """Propose one authenticated owner transition; never cancel another run."""
        T.need(not getattr(self,'proposal_fenced',False) and self.pending_changes is None,'outstanding-proposal')
        T.need(self.entry.runtime['mode']=='start','wrong-claim-entry')
        T.need(self.api.ref('heads/operations',self.api.operating)==self.head,'moving-claim-head')
        stop=L.singletons(L.record_blob(self.operating,self.head,'control/stop.tsv')[1],
                         {'stop','revision','reason','operator'})
        T.need(stop['stop']=='0','stopped-claim')
        jobs=self.api.jobs(self.entry.runtime['run'],self.entry.runtime['attempt'])
        T.need(len(jobs)==1 and jobs[0].get('id')==self.entry.runtime['job'],'nonisolated-claim-job')
        previous=self.project();state=previous['state'];owner=state['owner']
        T.need(not state['stopped'] and state['stage'] not in {'empty','complete','stopped'},'inactive-claim')
        candidate=state['candidate'] or state.get('refresh')
        expected=T.digest(T.canonical(candidate)) if candidate else '0'*64
        T.need(self.entry.runtime['candidate']==expected,'stale-claim-candidate')
        if owner and (int(owner['run']),int(owner['attempt']),int(owner['job'])) == (
                self.entry.runtime['run'],self.entry.runtime['attempt'],self.entry.runtime['job']):
            return {} # exact existing owner joins; no new generation or record
        transcript=T.document((self.batch/'transcript.json').read_bytes())
        if owner:
            T.need(self.entry.owner_terminal(self.owner_target(owner)),'old-owner-not-terminal')
            transcript['owner']={'owner':owner,'latest-attempt':owner['attempt'],
                'jobs':{owner['job']:'terminal'},'complete':True,'status':'terminal'}
        event={'sequence':str(int(state['sequence'])+1),'kind':'claim','prior':previous['prior'],'batch':state['batch'],
            'repository':str(self.entry.trusted['repository-id']),'workflow':str(self.entry.trusted['workflow']),
            'run':str(self.entry.runtime['run']),'attempt':str(self.entry.runtime['attempt']),
            'job':str(self.entry.runtime['job']),'generation':str(int(state['generation'])+1),'operating-head':self.head}
        raw=self.encode_event(event);path='history/%012d.tsv'%int(event['sequence'])
        (self.batch/path).write_bytes(raw);(self.batch/'transcript.json').write_bytes(T.canonical(transcript))
        # The original reducer, not a current helper, decides unresolved-effect
        # and old-protocol takeover compatibility before publication.
        changes=self.projected_changes(path,raw,transcript)
        self.pending_changes=changes
        return changes

    def owner_target(self, owner):
        target={k:int(owner[k]) for k in ('run','attempt','job','workflow')}
        run=self.api.run(target['run'],target['attempt'])
        T.need(run.get('repository',{}).get('id')==self.entry.trusted['repository-id']
               and run.get('workflow_id')==target['workflow']==self.entry.trusted['workflow']
               and run.get('head_branch')=='master' and run.get('event')=='workflow_dispatch'
               and str(run.get('actor',{}).get('id')) in self.pinned_config['actors'].split(',')
               and run.get('triggering_actor',{}).get('id')==run.get('actor',{}).get('id'),'untrusted-owner-source')
        source=T.sha(run.get('head_sha'))
        # A later master loader may own an old semantic package. Observe its actual
        # immutable run source separately, bounded by approved public master history.
        try:
            L.git(self.bundle,'merge-base','--is-ancestor',self.owner_source,source)
            L.git(self.bundle,'merge-base','--is-ancestor',source,self.entry.trusted['source'])
        except (ValueError,subprocess.SubprocessError):
            raise T.Refusal('unapproved-owner-source') from None
        return dict(target,source=source)

    def authorize(self, plan, entry):
        T.need(set(plan)=={'id','digest','head'} and entry is self.entry and plan['head']==self.head,'stale-plan')
        current=self.project()['state']; op=current['operations'].get(plan['id'])
        T.need(op and op['state']=='intent' and op['payload'] and plan['digest']==T.digest(T.canonical(op['payload'])),'unbound-retained-intent')
        T.need(not any(o['state'] in {'unknown','conflict'} for o in current['operations'].values()),'outstanding-unknown-effect')
        T.need(current['owner'] and int(current['owner']['run'])==entry.runtime['run']
               and int(current['owner']['attempt'])==entry.runtime['attempt']
               and int(current['owner']['job'])==entry.runtime['job'],'foreign-record-owner')
        T.need(entry.runtime['candidate']==T.digest(T.canonical(current['candidate'] or current.get('refresh'))) if current['candidate'] or current.get('refresh') else entry.runtime['candidate']=='0'*64,'stale-entry-candidate')
        self.owner_target(current['owner'])
        payload=copy.deepcopy(op['payload']);kind=op['kind']
        if kind=='cancel':
            payload=self.owner_target({'run':payload['run'],'attempt':payload['attempt'],'job':payload['jobs'],'workflow':payload['workflow']})
        if kind=='merge':payload['number']=int(payload['number'])
        if kind=='tag-object':
            payload['tagger']={'name':payload['tagger-name'],'email':payload['tagger-email'],'date':payload['tagger-time']}
        # Intent is already a complete durable semantic event. Publish a verified
        # identical index/archival transcript snapshot to bind the writer head.
        return kind,payload,{'current/index.tsv':L.record_blob(self.operating,self.head,'current/index.tsv')[1]}

    def authorize_recovery(self,plan,entry):
        T.need(entry is self.entry and set(plan)=={'id','digest','head'},'unowned-recovery')
        current=self.project()['state'];op=current['operations'].get(plan['id'])
        owner=current['owner']
        if owner and (int(owner['run']),int(owner['attempt']),int(owner['job'])) != (entry.runtime['run'],entry.runtime['attempt'],entry.runtime['job']):
            T.need(entry.owner_terminal(self.owner_target(owner)),'old-owner-not-terminal')
        T.need(op and op['state'] in {'intent','unknown'} and plan['digest']==T.digest(T.canonical(op['payload'])),'wrong-recovery-operation')
        kind,payload=op['kind'],copy.deepcopy(op['payload'])
        if kind=='merge':payload['number']=int(payload['number'])
        if kind=='tag-object':payload['tagger']={'name':payload['tagger-name'],'email':payload['tagger-email'],'date':payload['tagger-time']}
        if kind=='cancel':payload=self.owner_target({'run':payload['run'],'attempt':payload['attempt'],'job':payload['jobs'],'workflow':payload['workflow']})
        return kind,payload,{}

    def validate_stop(self,raw,head):
        fields=L.singletons(raw,{'stop','revision','reason','operator'})
        T.need(fields['stop'] in {'0','1'} and fields['revision'].isdigit(),'invalid-stop')
        # A fresh authenticated stop may advance records; it never permits writing
        # on an unrelated head. Changed non-stopped state requires complete reload.
        T.need(fields['stop']=='1' or head==self.expected,'operating-head-changed')
        return fields['stop']=='1'

    def validate_changes(self,changes):
        T.need(not getattr(self,'proposal_fenced',False),'failed-proposal')
        T.need(changes==self.pending_changes or changes=={'current/index.tsv':L.record_blob(self.operating,self.head,'current/index.tsv')[1]},'unprojected-record-changes')
        prospective=None
        if getattr(self,'proposal_binding',None) is not None:
            T.need(tuple(sorted((p,T.digest(d)) for p,d in changes.items()))==self.proposal_binding,'changed-proposal-bytes')
            self.proposal_context(self.proposal_before)
            prospective=self.validate_prospective(changes)
            self.proposal_context(self.proposal_before)
            self.validate_collected_evidence()
            self.validate_collected_candidate()

        return prospective if prospective is not None else self.validate_prospective(changes)

    def accept_changes(self,changes,head):
        state=self.project()['state']
        self.expected=self.head=head
        self.state=state
        if 'current/transcript.json' in changes:self.original_transcript=changes['current/transcript.json']
        self.pending_changes=None
        self.proposal_binding=None
        self.evidence_binding=None
        self.candidate_binding=None

    def observation(self,plan,state,remote):
        T.need(not getattr(self,'proposal_fenced',False) and self.pending_changes is None,'outstanding-proposal')
        T.need(state in {'applied','absent'},'unconfirmed-observation')
        op=self.state['operations'][plan['id']];payload=op['payload'];kind=op['kind']
        if kind=='refresh-object':target={'object-type':payload['object-type'],'object':payload['object'],
            'raw-digest':T.digest(O.raw_base64(payload['raw'])),
            'dependencies':T.document(payload['dependencies'].encode()),'construction':payload['construction']}
        elif kind=='merge':target={'merged':True,'commit':remote,'parents':[payload['master'],payload['dev']],'tree':payload['tree'],'source':payload['dev']}
        elif kind=='refresh-branch':target={'candidate':{k:v for k,v in payload.items() if k!='repository'}}
        elif kind=='refresh-pr':
            context=T.document(self.original_transcript)['refresh']['current']
            target={'matches':[{'number':str(remote),'repository':payload['repository'],'base-ref':'dev','state':'open',
                     'candidate':{k:v for k,v in payload.items() if k!='repository'},'checks':context['checks']}]}
        elif kind=='pr':target={'matches':[{'number':str(remote),'payload':payload}]}
        elif kind=='cancel':target={'run':payload['run'],'attempt':payload['attempt'],'workflow':payload['workflow'],'jobs':payload['jobs'],'latest-attempt':payload['attempt'],'terminal':True}
        elif kind=='tag-ref':target=payload
        else:target=payload
        if state=='absent':
            target=({'object-type':payload['object-type'],'object':payload['object']} if kind=='refresh-object' else {'batch':payload['batch'],'branch':payload['branch'],'head':payload['previous']} if kind=='refresh-branch' else {})
        observed={'status':'present' if state=='applied' else 'absent','target':target,'complete':True}
        transcript=T.document((self.batch/'transcript.json').read_bytes())
        transcript['observations'].setdefault(plan['id'],[]).append(observed)
        if kind=='refresh-branch' and state=='applied':
            transcript['refresh']['current']['branch']['head']=payload['head']
        (self.batch/'transcript.json').write_bytes(T.canonical(transcript))
        previous=self.project(); sequence=int(previous['state']['sequence'])+1
        event={'sequence':str(sequence),'kind':'observation','prior':previous['prior'],'batch':self.state['batch'],
               'payload':T.canonical(payload).decode(),'operation':[[plan['id'],kind,plan['digest'],self.state['generation'],
                       'observed' if state=='applied' else 'intent',str(remote) if remote is not None else '-',T.digest(T.canonical(observed))]]}
        raw=self.encode_event(event)
        path='history/%012d.tsv'%sequence
        (self.batch/path).write_bytes(raw)
        changes=self.projected_changes(path,raw,transcript)
        self.pending_changes=changes
        return changes

    def transition(self, request):
        """Authenticated approval/stop/resume; exact old reducer keeps its gates."""
        T.need(not getattr(self,'proposal_fenced',False) and self.pending_changes is None,'outstanding-proposal')
        self.entry.request(request)
        mode=request['mode'];T.need(mode in {'approve','stop','resume'},'unsupported-transition')
        previous=self.project();state=previous['state']
        candidate=state['candidate']
        expected=T.digest(T.canonical(candidate)) if candidate else '0'*64
        T.need(request['candidate']==expected,'stale-transition-candidate')
        transcript=T.document((self.batch/'transcript.json').read_bytes())
        source={'repository':str(self.entry.trusted['repository-id']),'workflow':str(self.entry.trusted['workflow']),
                'actor':str(request['actor']),'run':str(request['run']),'attempt':str(request['attempt']),
                'ref':request['ref'],'event':'workflow_dispatch','mode':mode,'candidate':expected}
        if source not in transcript['source']:transcript['source'].append(source)
        changes={}
        if mode=='stop':
            stop=L.singletons(L.record_blob(self.operating,self.head,'control/stop.tsv')[1],{'stop','revision','reason','operator'})
            revision=str(int(stop['revision'])+1)
            event={'kind':'stop-observed','revision':revision,'reason':'operator-stop'}
            changes['control/stop.tsv']=L.encode_index({'stop':'1','revision':revision,'reason':'operator-stop','operator':str(request['actor'])})
        elif mode=='resume':
            event={'kind':'resume',**{k:str(request[k]) for k in ('actor','run','attempt','ref')}}
            stop=L.singletons(L.record_blob(self.operating,self.head,'control/stop.tsv')[1],{'stop','revision','reason','operator'})
            changes['control/stop.tsv']=L.encode_index({'stop':'0','revision':str(int(stop['revision'])+1),'reason':'operator-resume','operator':str(request['actor'])})
        else:
            T.need(candidate and state['stage']=='validated','unvalidated-approval')
            event={k:candidate[k] for k in ('candidate-generation','dev','master','tree','classification','versions','migrations')}
            event.update(kind='approval',**{k:str(request[k]) for k in ('actor','run','attempt','ref')},
                         **{'evidence-digest':T.digest(T.canonical(state['evidence']))})
        event.update(sequence=str(int(state['sequence'])+1),prior=previous['prior'],batch=state['batch'])
        raw=self.encode_event(event);path='history/%012d.tsv'%int(event['sequence'])
        (self.batch/path).write_bytes(raw);(self.batch/'transcript.json').write_bytes(T.canonical(transcript))
        changes.update(self.projected_changes(path,raw,transcript))
        self.pending_changes=changes
        return changes

    def projected_changes(self,path,raw,transcript):
        simple=base64.b64decode(self.project()['index'],validate=True)
        contexts=L.table(L.record_blob(self.operating,self.head,'current/batches.tsv')[1])
        ledger=[]
        for index,row in enumerate(contexts):
            context=dict(zip(L.CONTEXT_FIELDS,row[1:]))
            batch=self.scratch/('batch-'+str(index));package=self.scratch/('package-'+str(index))
            if index==len(contexts)-1:projection=simple
            else:
                before=int(context['start'])-1;first=sorted((batch/'history').iterdir())[0]
                prior=dict((r[0],r[1]) for r in L.table(first.read_bytes()) if len(r)==2)['prior']
                projection=L.replay_package(package,batch,context['protocol'],before,prior)[0]
            ledger.append({'context':context,'projection':T.digest(projection)})
        fields=L.singletons(simple,L.PROJECTION_FIELDS)
        fields.update({'index-kind':'global-1','ledger-digest':T.digest(T.canonical(ledger))})
        return {path:raw,'current/index.tsv':L.encode_index(fields),'current/transcript.json':T.canonical(transcript)}

    def encode_event(self, fields):
        # Use this batch's manifest-verified original serializer, not a transport
        # reimplementation whose treatment of old framing might silently diverge.
        driver="import json,sys;sys.path.insert(0,sys.argv[1]);import records;sys.stdout.buffer.write(records.encode(json.load(sys.stdin)))"
        result=subprocess.run([sys.executable,'-I','-S','-B','-c',driver,str(self.package/L.ROOT)],
               input=T.canonical(fields),env=L.runtime_environment(os.environ),capture_output=True,timeout=30)
        T.need(result.returncode==0 and 0<len(result.stdout)<=T.MAX_BODY,'retained-serializer-refusal')
        return result.stdout

    def object_material(self, payload):
        T.need(self.protocol=='4','object-effect-requires-original4')
        driver="import json,sys;sys.path.insert(0,sys.argv[1]);import adapter;print(json.dumps(adapter.operation('refresh-object',json.load(sys.stdin)),sort_keys=True))"
        result=subprocess.run([sys.executable,'-I','-S','-B','-c',driver,str(self.package/L.ROOT)],
            input=T.canonical(payload),env=L.runtime_environment(os.environ),capture_output=True,timeout=30)
        T.need(result.returncode==0 and len(result.stdout)<=T.MAX_BODY,'original-object-serializer')
        request=T.document(result.stdout)
        T.need(set(request)=={'api-version','method','path','body','payload-digest'} and
            request['api-version']==T.VERSION and request['method']=='POST' and
            request['path']=='/repos/'+T.PUBLIC+'/git/'+payload['object-type']+'s' and
            request['payload-digest']==T.digest(T.canonical(payload)),'unbound-original-object-request')
        raw=O.raw_base64(payload['raw'])
        T.need(O.oid(payload['object-type'],raw)==payload['object'],'object-raw-identity')
        transcript=T.document(self.original_transcript)
        construction=transcript['refresh']['current']['construction']
        T.need(construction['digest']==payload['construction'],'foreign-object-construction')
        originals={row['type']:(row['sha'],O.raw_base64(row['raw'])) for row in construction['originals']}
        return request,raw,originals

    def object_dependencies(self, payload, reader):
        state=self.project()['state'];request,raw,originals=self.object_material(payload)
        deps=T.document(payload['dependencies'].encode())
        T.need(type(deps) is list and len(deps)<=4096,'object-dependency-bound')
        for dep in deps:
            kind,identity,operation=dep['type'],dep['sha'],dep['operation']
            if operation!='-':
                prior=state['operations'].get(operation)
                T.need(prior and prior['kind']=='refresh-object' and prior['state']=='observed'
                    and prior['payload']['object-type']==kind and prior['payload']['object']==identity,
                    'unobserved-generated-dependency')
                expected=O.raw_base64(prior['payload']['raw']);generated=kind=='commit'
            else:
                size=int(L.git(self.bundle,'cat-file','-s',identity))
                T.need(0<=size<=O.MAX_RAW,'unsupported-original-dependency')
                # Independently acquired public originals only; no API reconstruction.
                expected=L.git(self.bundle,'cat-file',kind,identity);generated=False
            T.need(reader.prove(kind,identity,expected,generated),'unavailable-object-dependency')
        return request

    def verify_refresh(self,p,api):
        T.need(api.ref('heads/dev')==p['base'],'stale-refresh-base')
        commit=api.commit(p['head']); entries=api.tree(commit['tree']);parent=api.commit(p['parent']); old=api.tree(parent['tree'])
        changed={k for k in set(old)|set(entries) if old.get(k)!=entries.get(k)}
        # Recursive directory identities legitimately change along the lock path.
        leaves={k for k in changed if (entries.get(k) or old.get(k))[1]!='tree'}
        T.need(leaves=={'unixlike/flake.lock'} and entries['unixlike/flake.lock'][0]==old['unixlike/flake.lock'][0], 'contaminated-refresh')
        T.need(T.digest(api.blob(entries['unixlike/flake.lock'][2]))==p['lock']
               and T.digest(api.blob(old['unixlike/flake.lock'][2]))==p['before-lock'],'wrong-lock-bytes')
        if p['previous']!='-':T.need(parent['parents']==[p['previous'],p['base']],'wrong-refresh-update-parents')

    def typed_checks(self,candidate,baseline):
        roots=self.qualification_objects(baseline)
        _,diagnostic=self.candidate_preview({k:candidate[k] for k in ('dev','master','tree')},baseline,roots,b'format\t1\n')
        checks=diagnostic.get('checks')
        T.need(type(checks) is list and [r['id'] for r in checks]==candidate['selected'].split(','),'changed-typed-qualifier-selection')
        return checks

    def verify_typed_evidence(self):
        candidate=self.state['candidate'];baseline=self.qualification_input()
        T.need(T.digest(baseline)==candidate['baselines'],'changed-evidence-baseline')
        checks=self.typed_checks(candidate,baseline)
        typed={p['id'] for p in self.receipts.producers if p['kind']!='actions'}
        historical=[r for r in self.state['evidence'] if r[0] in typed]
        receipts,_,_=self.typed_collect({k:candidate[k] for k in ('dev','master','tree')},baseline,checks,historical or None)
        rows=[[r['id']]+[candidate[k] for k in ('dev','master','tree','rules','tool')]+['verified',str(r['run']),str(r['attempt']),str(r['job']),r['tool']] for r in receipts]
        T.need(rows==self.state['evidence'],'changed-typed-evidence')

    def verify_merge(self,p,entry):
        candidate=self.state['candidate'];T.need(candidate and all(candidate[k]==p[k] for k in ('dev','master','tree')),'stale-merge-context')
        if self.receipts is None:
            entry.evidence(p['dev'],p['tree'],self.requirements)
        else:
            self.verify_typed_evidence()
        # Exact API checks do not authenticate arbitrary job-reported tool strings.
        # Reviewed requirements bind trusted workflow/source/tool blobs; R-manual
        # must provision that trust set before this source can be used live.
        T.need((self.receipts is not None and {p['id'] for p in self.receipts.producers}==set(candidate['selected'].split(','))) or
               (self.requirements and {r['id'] for r in self.requirements}==set(candidate['selected'].split(','))),'incomplete-public-evidence')
        approval=self.state['approval']
        if candidate['approval-required']=='1' or candidate['classification']=='major' or candidate['migrations']!='-':
            T.need(approval and int(approval['actor']) in entry.trusted['actors'],'missing-exact-approval')
            run=entry.api.run(int(approval['run']),int(approval['attempt']))
            latest=entry.api.get('/actions/runs/'+approval['run'])
            T.need(latest.get('run_attempt')==int(approval['attempt']) and run.get('event')=='workflow_dispatch'
                   and run.get('head_branch')=='master' and run.get('workflow_id')==entry.trusted['workflow']
                   and run.get('actor',{}).get('id')==int(approval['actor'])
                   and run.get('triggering_actor',{}).get('id')==int(approval['actor'])
                   and run.get('head_sha')==self.owner_source
                   and run.get('repository',{}).get('id')==entry.trusted['repository-id'],'untrusted-approval-source')

    def verify_publication(self,p,api):
        if self.receipts is not None:self.verify_typed_evidence()
        merges=[o for o in self.state['operations'].values() if o['kind']=='merge' and o['state']=='observed']
        T.need(len(merges)==1 and self.state['frozen'],'publication-before-promotion')
        op=merges[0];actual=api.commit(op['remote'])
        T.need(actual['parents']==[op['payload']['master'],op['payload']['dev']] and actual['tree']==op['payload']['tree'],'unexpected-promotion')
        source=op['payload']['dev']; releases=[r for r in self.state['releases'] if r[0]+'-v'+r[1]==p['tag']]
        T.need(len(releases)==1 and releases[0][2]==source and releases[0][5]==p['object'],'wrong-publication-source')
