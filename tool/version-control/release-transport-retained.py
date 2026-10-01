"""Credential-free bridge to the exact eight-file semantic package.

Driver text is trusted transport glue. It imports only the manifest-verified
package selected by the existing global-history loader; no candidate code runs.
"""
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

class Snapshot:
    """A whole-history verified, source-bound projector with no credentials."""
    def __init__(self, entry, bundle, operating, approved, head, tagger, requirements):
        self.entry, self.api = entry, entry.api
        T.need(type(entry) is T.Entry and entry.authenticated, 'missing-entry')
        self.source = entry.trusted['source']
        T.need(self.api.ref('heads/master') == self.source, 'untrusted-control-head')
        T.need(self.api.ref('heads/operations', self.api.operating) == head, 'stale-history-head')
        self.expected = T.sha(head)
        T.need(set(tagger) == {'name','email','date'} and tagger['name'] == 'Release controller'
               and tagger['email'] == 'release-controller@example.invalid'
               and __import__('re').fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ',tagger['date']), 'unfixed-record-tagger')
        self.tagger, self.requirements = dict(tagger), copy.deepcopy(requirements)
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
        T.need('config/operating.tsv' in entries and entries['config/operating.tsv'][:2] == ('100644','blob'),'missing-current-authority')
        config=L.singletons(self.api.blob(entries['config/operating.tsv'][2],self.api.operating),
               {'enabled','public-repository','repository','operating-repository','operating-ref','workflow','actors','checks','protocol'})
        T.need(config['enabled']=='1' and config['public-repository']==T.PUBLIC
               and config['operating-repository']==self.api.operating and config['operating-ref']=='operations'
               and config['repository']==str(self.entry.trusted['repository-id'])
               and config['workflow']==str(self.entry.trusted['workflow'])
               and str(self.entry.runtime['actor']) in config['actors'].split(','),'revoked-current-authority')
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
        events=sorted((self.batch/'history').iterdir())
        framing=L.singletons(events[0].read_bytes(),set()) if not events else dict((r[0],r[1]) for r in L.table(events[0].read_bytes()) if len(r)==2)
        self.boundary=framing['prior']
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

    def authorize(self, plan, entry):
        T.need(set(plan)=={'id','digest','head'} and entry is self.entry and plan['head']==self.head,'stale-plan')
        current=self.project()['state']; op=current['operations'].get(plan['id'])
        T.need(op and op['state']=='intent' and op['payload'] and plan['digest']==T.digest(T.canonical(op['payload'])),'unbound-retained-intent')
        T.need(not any(o['state'] in {'unknown','conflict'} for o in current['operations'].values()),'outstanding-unknown-effect')
        T.need(current['owner'] and int(current['owner']['run'])==entry.runtime['run']
               and int(current['owner']['attempt'])==entry.runtime['attempt']
               and int(current['owner']['job'])==entry.runtime['job'],'foreign-record-owner')
        T.need(entry.runtime['candidate']==T.digest(T.canonical(current['candidate'] or current.get('refresh'))) if current['candidate'] or current.get('refresh') else entry.runtime['candidate']=='0'*64,'stale-entry-candidate')
        payload=copy.deepcopy(op['payload']);kind=op['kind']
        if kind=='cancel':
            payload={'run':int(payload['run']),'attempt':int(payload['attempt']),'job':int(payload['jobs']),
                     'workflow':int(payload['workflow']),'source':self.owner_source}
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
            T.need(entry.owner_terminal({'run':int(owner['run']),'attempt':int(owner['attempt']),'job':int(owner['job']),
                 'workflow':entry.trusted['workflow'],'source':self.owner_source}),'old-owner-not-terminal')
        T.need(op and op['state'] in {'intent','unknown'} and plan['digest']==T.digest(T.canonical(op['payload'])),'wrong-recovery-operation')
        kind,payload=op['kind'],copy.deepcopy(op['payload'])
        if kind=='merge':payload['number']=int(payload['number'])
        if kind=='tag-object':payload['tagger']={'name':payload['tagger-name'],'email':payload['tagger-email'],'date':payload['tagger-time']}
        if kind=='cancel':payload={'run':int(payload['run']),'attempt':int(payload['attempt']),'job':int(payload['jobs']),'workflow':int(payload['workflow']),'source':self.owner_source}
        return kind,payload,{}

    def validate_stop(self,raw,head):
        fields=L.singletons(raw,{'stop','revision','reason','operator'})
        T.need(fields['stop'] in {'0','1'} and fields['revision'].isdigit(),'invalid-stop')
        # A fresh authenticated stop may advance records; it never permits writing
        # on an unrelated head. Changed non-stopped state requires complete reload.
        T.need(fields['stop']=='1' or head==self.expected,'operating-head-changed')
        return fields['stop']=='1'

    def validate_changes(self,changes):
        T.need(changes==self.pending_changes or changes=={'current/index.tsv':L.record_blob(self.operating,self.head,'current/index.tsv')[1]},'unprojected-record-changes')

    def accept_changes(self,changes,head):
        self.expected=self.head=head
        self.state=self.project()['state']
        self.pending_changes=None

    def observation(self,plan,state,remote):
        T.need(state in {'applied','absent'},'unconfirmed-observation')
        op=self.state['operations'][plan['id']];payload=op['payload'];kind=op['kind']
        if kind=='merge':target={'merged':True,'commit':remote,'parents':[payload['master'],payload['dev']],'tree':payload['tree'],'source':payload['dev']}
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
            target=({'batch':payload['batch'],'branch':payload['branch'],'head':payload['previous']} if kind=='refresh-branch' else {})
        observed={'status':'present' if state=='applied' else 'absent','target':target,'complete':True}
        transcript=T.document((self.batch/'transcript.json').read_bytes())
        transcript['observations'].setdefault(plan['id'],[]).append(observed)
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

    @staticmethod
    def encode_event(fields):
        lines=['format\t1']
        for key in sorted(fields):
            if key=='operation':lines.extend('\t'.join([key]+row) for row in fields[key])
            else:lines.append(key+'\t'+fields[key])
        return ('\n'.join(lines)+'\n').encode()

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

    def verify_merge(self,p,entry):
        candidate=self.state['candidate'];T.need(candidate and all(candidate[k]==p[k] for k in ('dev','master','tree')),'stale-merge-context')
        entry.evidence(p['dev'],p['tree'],self.requirements)
        # Exact API checks do not authenticate arbitrary job-reported tool strings.
        # Reviewed requirements bind trusted workflow/source/tool blobs; R-manual
        # must provision that trust set before this source can be used live.
        T.need(self.requirements and {r['id'] for r in self.requirements}==set(candidate['selected'].split(',')),'incomplete-public-evidence')
        approval=self.state['approval']
        if candidate['approval-required']=='1' or candidate['classification']=='major' or candidate['migrations']!='-':
            T.need(approval and int(approval['actor']) in entry.trusted['actors'],'missing-exact-approval')
            run=entry.api.run(int(approval['run']),int(approval['attempt']))
            latest=entry.api.get('/actions/runs/'+approval['run'])
            T.need(latest.get('run_attempt')==int(approval['attempt']) and run.get('event')=='workflow_dispatch'
                   and run.get('head_branch')=='master' and run.get('workflow_id')==entry.trusted['workflow']
                   and run.get('actor',{}).get('id')==int(approval['actor']),'untrusted-approval-source')

    def verify_publication(self,p,api):
        merges=[o for o in self.state['operations'].values() if o['kind']=='merge' and o['state']=='observed']
        T.need(len(merges)==1 and self.state['frozen'],'publication-before-promotion')
        op=merges[0];actual=api.commit(op['remote'])
        T.need(actual['parents']==[op['payload']['master'],op['payload']['dev']] and actual['tree']==op['payload']['tree'],'unexpected-promotion')
        source=op['payload']['dev']; releases=[r for r in self.state['releases'] if r[0]+'-v'+r[1]==p['tag']]
        T.need(len(releases)==1 and releases[0][2]==source and releases[0][5]==p['object'],'wrong-publication-source')
