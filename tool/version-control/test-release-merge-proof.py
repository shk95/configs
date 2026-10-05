"""Real disposable Git computation and refusal fixtures; no remote transport."""
# INV repository/raw-merge-computation-read-only
# INV repository/fixture-git-isolation
import copy
import hashlib
import importlib.util
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('raw_merge',ROOT/'release-merge-proof.py')
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
PROFILE = hashlib.sha256(b'fixture backend; no operating admission').hexdigest()
GIT = str(Path(shutil.which('git')).resolve())

def git(repository,*arguments,raw=None):
    result = subprocess.run([GIT,'-C',str(repository),*arguments],input=raw,
                            stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    return result.stdout

def carrier(objects,roots):
    chunks, rows, current = [], [], bytearray()
    for identity,(kind,raw) in sorted(objects.items()):
        frame = (kind+' '+str(len(raw))+' '+identity+'\n').encode()+raw
        if len(current)+len(frame) > M.LIMITS['chunk-bytes']:
            chunks.append(bytes(current)); current = bytearray()
        rows.append({'oid':identity,'type':kind,'size':len(raw),'chunk':len(chunks)+1,'offset':len(current)})
        current.extend(frame)
    if current: chunks.append(bytes(current))
    manifest = {'format':1,'kind':'required-refresh-merge','roots':roots,'runtime-profile':PROFILE,
                'objects':rows,'chunks':[{'number':n,'size':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),
                                        'git-blob':M.oid('blob',raw)} for n,raw in enumerate(chunks,1)],
                'raw-bytes':sum(len(raw) for _,raw in objects.values())}
    return M.canonical(manifest),tuple(chunks)

class Repository:
    def __init__(self,path,attributes=None):
        self.path = Path(path); self.path.mkdir()
        git(self.path,'init','--initial-branch=main')
        git(self.path,'config','user.name','Fixture'); git(self.path,'config','user.email','fixture@example.invalid')
        # Git object expectations bind literal LF bytes on every native host.
        (self.path/'shared').write_bytes(b'first\nsecond\nthird\n')
        (self.path/'lock').write_bytes(b'old lock\n')
        if attributes is not None:
            (self.path/'.gitattributes').write_bytes(attributes)
            (self.path/'sample.dat').write_bytes(b'first\nsecond\nthird\n')
        self.ancestor = self.commit('ancestor')
        git(self.path,'checkout','-b','previous')
        (self.path/'lock').write_bytes(b'new lock\n')
        self.previous = self.commit('previous')
        git(self.path,'checkout','main')
        (self.path/'base-only').write_bytes(b'base addition\n')
        self.base = self.commit('base')
    def commit(self,message):
        git(self.path,'add','--all');git(self.path,'commit','-m',message)
        return git(self.path,'rev-parse','HEAD').strip().decode()
    def roots(self):return {'previous':self.previous,'base':self.base,'merge-base':self.ancestor}
    def objects(self):
        identities = set(git(self.path,'rev-list',self.previous,self.base).decode().splitlines())
        for root in self.roots().values():
            tree = git(self.path,'rev-parse',root+'^{tree}').strip().decode()
            identities.add(tree)
            for row in git(self.path,'ls-tree','-r','-t','-z',root).split(b'\0'):
                if row: identities.add(row.split(b'\t',1)[0].split()[2].decode())
        return {identity:(git(self.path,'cat-file','-t',identity).strip().decode(),
                          git(self.path,'cat-file',git(self.path,'cat-file','-t',identity).strip().decode(),identity))
                for identity in identities}
    def expected(self):return git(self.path,'merge-tree','--write-tree','--no-messages',
                                   '--merge-base='+self.ancestor,self.previous,self.base).strip().decode()

class Computation(unittest.TestCase):
    # INV repository/raw-merge-computation-read-only
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.repository = Repository(Path(self.tmp.name)/'source')
        self.backend = M.Backend(GIT,PROFILE)
    def proof(self,objects=None,roots=None):
        raw,chunks = carrier(objects or self.repository.objects(),roots or self.repository.roots())
        return M.verify_merge(raw,chunks,self.backend)
    def test_clean_complete_closure_and_unchanged_source(self):
        before = git(self.repository.path,'rev-parse','HEAD')
        original = self.repository.objects(); result = self.proof(original)
        self.assertEqual(result['tree'],self.repository.expected())
        self.assertEqual(result['merge-base'],self.repository.ancestor)
        self.assertEqual(before,git(self.repository.path,'rev-parse','HEAD'))
        self.assertEqual(set(result),{'roots','merge-base','tree','inventory','objects'})
        available = set(original)
        for row in result['objects']:
            self.assertEqual(M.oid(row['type'],row['raw']),row['oid'])
            self.assertNotIn(row['oid'],original)
            if row['type']=='tree':
                self.assertTrue(all(child in available for _,_,child in M.tree_entries(row['raw'])))
            available.add(row['oid'])
        self.assertIn(result['tree'],available)
        self.assertEqual(result['inventory']['lock'][1],M.oid('blob',b'new lock\n'))
        self.assertIn('base-only',result['inventory'])
    def test_text_merge_rename_mode_and_empty_tree(self):
        repo=self.repository
        git(repo.path,'checkout','previous');(repo.path/'shared').write_bytes(b'FIRST\nsecond\nthird\n')
        git(repo.path,'add','--all');git(repo.path,'update-index','--chmod=+x','shared')
        git(repo.path,'commit','-m','previous edit');repo.previous=git(repo.path,'rev-parse','HEAD').strip().decode()
        git(repo.path,'checkout','--force','main');(repo.path/'shared').write_bytes(b'first\nsecond\nTHIRD\n')
        git(repo.path,'mv','base-only','renamed');repo.base=repo.commit('base edit')
        result=self.proof();self.assertEqual(result['tree'],repo.expected())
        self.assertEqual(result['inventory']['shared'][0],'100755')
        self.assertIn('renamed',result['inventory'])
        self.assertIn(M.oid('blob',b'FIRST\nsecond\nTHIRD\n'),[x['oid'] for x in result['objects']])
        self.assertEqual(M.tree_entries(b''),[])
    def test_binary_and_text_eol_attributes_preserved_and_conflict_refuses(self):
        repo=Repository(Path(self.tmp.name)/'attrs',b'*.dat binary\nshared text eol=lf\nbase-only text=auto eol=crlf\n')
        raw,chunks=carrier(repo.objects(),repo.roots())
        self.assertEqual(M.verify_merge(raw,chunks,self.backend)['tree'],repo.expected())
        git(repo.path,'checkout','previous');(repo.path/'sample.dat').write_bytes(b'FIRST\nsecond\nthird\n');repo.previous=repo.commit('binary one')
        git(repo.path,'checkout','main');(repo.path/'sample.dat').write_bytes(b'first\nsecond\nTHIRD\n');repo.base=repo.commit('binary two')
        raw,chunks=carrier(repo.objects(),repo.roots())
        with self.assertRaises(M.Refusal):M.verify_merge(raw,chunks,self.backend)
    def test_real_empty_snapshot_and_result_closure(self):
        empty=git(self.repository.path,'hash-object','-w','-t','tree','--stdin',raw=b'').strip().decode()
        repo=self.repository
        repo.ancestor=git(repo.path,'commit-tree',empty,raw=b'empty ancestor\n').strip().decode()
        repo.previous=git(repo.path,'commit-tree',empty,'-p',repo.ancestor,raw=b'empty previous\n').strip().decode()
        repo.base=git(repo.path,'commit-tree',empty,'-p',repo.ancestor,raw=b'empty base\n').strip().decode()
        result=self.proof()
        self.assertEqual(result['tree'],empty)
        self.assertEqual(result['inventory'],{'':('40000',empty)})
        self.assertEqual(result['objects'],[])

    def test_raw_headers_signed_and_unsupported_finite_refusal(self):
        tree=M.oid('tree',b'')
        raw=('tree '+tree+'\nauthor Fixture <fixture@example.invalid> 1 +0000\ncommitter Fixture <fixture@example.invalid> 1 +0000\ngpgsig -----BEGIN SIGNATURE-----\n continuation\n -----END SIGNATURE-----\n\nmessage\n').encode()
        self.assertEqual(M.parse_commit(raw),(tree,[]))
        for bad in (raw.replace(b'tree ',b'unknown ',1),raw.replace(b'\ngpgsig ',b'\nencoding latin1\ngpgsig '),
                    raw.replace(b' continuation',b'not-a-continuation')):
            with self.assertRaises(M.Refusal):M.parse_commit(bad)
    def test_manifest_frame_identity_and_canonical_corruption(self):
        raw,chunks=carrier(self.repository.objects(),self.repository.roots())
        with self.assertRaises(M.Refusal):M.verify_merge(raw+b'\n',chunks,self.backend)
        with self.assertRaises(M.Refusal):M.verify_merge(raw,chunks[:-1]+(chunks[-1]+b'x',),self.backend)
        value=M._json(raw)
        for key,bad in [('format',True),('runtime-profile','f'*64),('raw-bytes',0),('kind','raw-refresh-merge')]:
            changed=copy.deepcopy(value);changed[key]=bad
            with self.subTest(key=key),self.assertRaises(M.Refusal):M.verify_merge(M.canonical(changed),chunks,self.backend)
        for key,bad in [('offset',1),('size',True),('chunk',0),('oid','0'*40),('type','tag')]:
            changed=copy.deepcopy(value);changed['objects'][0][key]=bad
            with self.subTest(key=key),self.assertRaises(M.Refusal):M.verify_merge(M.canonical(changed),chunks,self.backend)
        with self.assertRaises(M.Refusal):M._json(b'{"format":1,"format":1}')
        with self.assertRaises(M.Refusal):M._json(b'{"x":NaN}')
        # Valid-size JSON still needs finite refusal for Python's digit guard
        # and overflow-to-infinity before exact manifest-field validation.
        with self.assertRaises(M.Refusal):M._json(b'{"raw-bytes":'+b'1'*5000+b'}')
        with self.assertRaises(M.Refusal):M._json(b'{"raw-bytes":1e999}')
        with self.assertRaises(M.Refusal):M._json(b'['*2000+b'0'+b']'*2000)
    def test_missing_unused_incorrect_and_multiple_base_graphs(self):
        objects=self.repository.objects();del objects[self.repository.ancestor]
        with self.assertRaises(M.Refusal):self.proof(objects)
        objects=self.repository.objects();objects[M.oid('blob',b'unused')]=('blob',b'unused')
        with self.assertRaises(M.Refusal):self.proof(objects)
        roots=self.repository.roots();roots['merge-base']=roots['base']
        with self.assertRaises(M.Refusal):self.proof(roots=roots)
        # Hand-built parsed graph exercises cycle/multiple-base refusal without
        # pretending a self-referential SHA1 cycle can be a genuine raw carrier.
        identities=[str(n)*40 for n in range(1,6)]
        tree=M.oid('tree',b'')
        def commit(parents):
            return ('tree '+tree+'\n'+''.join('parent '+p+'\n' for p in parents)+
                    'author F <f@example.invalid> 1 +0000\ncommitter F <f@example.invalid> 1 +0000\n\nx\n').encode()
        a,b,c,p,q=identities
        graph={a:('commit',commit([])),b:('commit',commit([a])),c:('commit',commit([a])),
               p:('commit',commit([b,c])),q:('commit',commit([c,b]))}
        with self.assertRaises(M.Refusal):M.verify_graph(graph,{'previous':p,'base':q,'merge-base':a},M.Budget())
        graph[a]=('commit',commit([p]))
        with self.assertRaises(M.Refusal):M.verify_graph(graph,{'previous':p,'base':q,'merge-base':a},M.Budget())
    def test_unsupported_modes_attrs_and_evolution_refuse(self):
        for name in (b'.',b'..',b'.GIT',b'con.txt',b'COM1',b'lpt9.log',b'x:y',b'x\\y',b'x/',b'x ',b'x.',b'\x01'):
            with self.subTest(name=name),self.assertRaises(M.Refusal):M.tree_entries(b'100644 '+name+b'\0'+bytes.fromhex('1'*40))
        for mode in (b'120000',b'160000',b'040000',b'100664'):
            with self.assertRaises(M.Refusal):M.tree_entries(mode+b' x\0'+bytes.fromhex('1'*40))
        for raw in (b'*.x merge=evil\n',b'[attr]macro text\n',b'*.x filter=x\n',
                    b'*.x working-tree-encoding=UTF-16\n',b'*.x text -text\n',b'*.x binary eol=lf\n'):
            with self.assertRaises(M.Refusal):M.parse_attributes(raw)
        repo=Repository(Path(self.tmp.name)/'evolution',b'* text\n')
        git(repo.path,'checkout','main');(repo.path/'.gitattributes').write_bytes(b'* binary\n');repo.base=repo.commit('changed attrs')
        raw,chunks=carrier(repo.objects(),repo.roots())
        with self.assertRaises(M.Refusal):M.verify_merge(raw,chunks,self.backend)
    def test_every_declared_bound_has_finite_excess(self):
        raw,chunks=carrier(self.repository.objects(),self.repository.roots())
        cases={'commits':0,'parents':0,'commit-bytes':1,'depth':1,'trees':0,'blobs':0,
               'blob-bytes':0,'raw-bytes':0,'manifest-bytes':1,'chunk-bytes':1,'chunks':0,
               'carrier-bytes':1,'scratch-bytes':0,'proof-seconds':0,'command-output-bytes':0}
        for name,value in cases.items():
            with self.subTest(bound=name),patch.dict(M.LIMITS,{name:value}),self.assertRaises(M.Refusal):
                M.verify_merge(raw,chunks,self.backend)
    def test_header_inclusive_chunk_boundary(self):
        raw=b'x'*1048576;objects={M.oid('blob',raw):('blob',raw)}
        manifest,chunks=carrier(objects,self.repository.roots())
        with self.assertRaises(M.Refusal):M.read_carrier(manifest,chunks,self.backend,M.Budget())
        raw=b'x'*(1048576-54);identity=M.oid('blob',raw)
        manifest,chunks=carrier({identity:('blob',raw)},self.repository.roots())
        _,values=M.read_carrier(manifest,chunks,self.backend,M.Budget())
        self.assertEqual(values[identity][1],raw)
    def test_expanded_path_bounds_refuse_before_native_materialization(self):
        def graph(levels,name='a',branch=False):
            objects={};identity=M.oid('tree',b'');objects[identity]=('tree',b'')
            for _ in range(levels):
                names=('a','b') if branch else (name,)
                raw=b''.join(b'40000 '+n.encode()+b'\0'+bytes.fromhex(identity) for n in names)
                identity=M.oid('tree',raw);objects[identity]=('tree',raw)
            body=('tree '+identity+'\nauthor F <f@example.invalid> 1 +0000\ncommitter F <f@example.invalid> 1 +0000\n\nx\n').encode()
            root=M.oid('commit',body);objects[root]=('commit',body)
            return objects,{'previous':root,'base':root,'merge-base':root}
        for levels,name,branch in ((257,'a',False),(64,'a'*64,False),(13,'a',True)):
            objects,roots=graph(levels,name,branch);raw,chunks=carrier(objects,roots)
            with self.subTest(levels=levels,branch=branch),patch.object(M,'Native') as native,self.assertRaises(M.Refusal):
                M.verify_merge(raw,chunks,self.backend)
            native.assert_not_called()
        for levels,name,branch in ((256,'a',False),(63,'a'*64,False),(12,'a',True)):
            objects,roots=graph(levels,name,branch);budget=M.Budget()
            commits=M.verify_graph(objects,roots,budget)
            self.assertTrue(M.snapshots(objects,commits,roots,budget))
    def test_complete_novel_raw_bytes_over_budget_refuses(self):
        repo=self.repository
        git(repo.path,'checkout','main');(repo.path/'shared').write_bytes(b'start\n'+b'm'*525000+b'\nend\n')
        repo.ancestor=repo.commit('large ancestor')
        git(repo.path,'checkout','-B','previous',repo.ancestor)
        (repo.path/'shared').write_bytes(b'START\n'+b'm'*525000+b'\nend\n');repo.previous=repo.commit('large previous')
        git(repo.path,'checkout','main');(repo.path/'shared').write_bytes(b'start\n'+b'm'*525000+b'\nEND\n');repo.base=repo.commit('large base')
        with self.assertRaises(M.Refusal):self.proof()

    def test_expanded_input_bytes_boundary_and_excess_precede_native(self):
        def data(count):
            body=b'x'*262144;blob=M.oid('blob',body)
            tree_raw=b''.join(b'100644 file'+str(n).zfill(2).encode()+b'\0'+bytes.fromhex(blob) for n in range(count))
            tree=M.oid('tree',tree_raw)
            commit=('tree '+tree+'\nauthor F <f@example.invalid> 1 +0000\ncommitter F <f@example.invalid> 1 +0000\n\nx\n').encode()
            root=M.oid('commit',commit)
            return {blob:('blob',body),tree:('tree',tree_raw),root:('commit',commit)}, {'previous':root,'base':root,'merge-base':root}
        objects,roots=data(21);raw,chunks=carrier(objects,roots)
        measured=3*(21*262144+len(objects[next(identity for identity,(kind,_) in objects.items() if kind=='tree')][1]))
        with patch.object(M,'EXPANDED_INPUT_BYTES',measured):
            self.assertEqual(M.verify_merge(raw,chunks,self.backend)['tree'],next(identity for identity,(kind,_) in objects.items() if kind=='tree'))
        with patch.object(M,'EXPANDED_INPUT_BYTES',measured-1),patch.object(M,'Native') as native,self.assertRaises(M.Refusal):
            M.verify_merge(raw,chunks,self.backend)
        native.assert_not_called()
        objects,roots=data(22);raw,chunks=carrier(objects,roots)
        with patch.object(M,'Native') as native,self.assertRaises(M.Refusal):
            M.verify_merge(raw,chunks,self.backend)
        native.assert_not_called()

    def test_complete_novel_closure_over_budget_refuses(self):
        repo=self.repository
        for branch in ('previous','main'):
            git(repo.path,'checkout',branch)
            for n in range(9):
                directory=repo.path/('dir'+str(n));directory.mkdir();(directory/branch).write_text(branch+str(n))
            head=repo.commit('many directories')
            if branch=='previous':repo.previous=head
            else:repo.base=head
        with self.assertRaises(M.Refusal):self.proof()

class Cleanup(unittest.TestCase):
    # INV repository/raw-merge-computation-read-only
    def leaf(self,root):
        path=Path(root)/'odb'/'objects'/'ab'/('c'*38)
        path.parent.mkdir(parents=True);path.write_bytes(b'owned object')
        return path
    def denial(self):
        error=PermissionError('Windows readonly object');error.winerror=5
        return error
    def test_owned_readonly_object_one_retry(self):
        with tempfile.TemporaryDirectory() as root:
            leaf=self.leaf(root);leaf.chmod(stat.S_IREAD)
            with patch.object(M.sys,'platform','win32'):
                M._readonly_object_retry(root,os.unlink,str(leaf),self.denial())
            self.assertFalse(leaf.exists())
        # Native Windows rmtree must actually encounter and remove readonly files.
        root=tempfile.mkdtemp();leaf=self.leaf(root);leaf.chmod(stat.S_IREAD)
        try:
            M._remove_scratch(root)
            self.assertFalse(Path(root).exists())
        finally:
            if leaf.exists():leaf.chmod(stat.S_IREAD | stat.S_IWRITE)
            shutil.rmtree(root,ignore_errors=True)
    def test_foreign_writable_and_symlink_objects_never_retry(self):
        with tempfile.TemporaryDirectory() as root,tempfile.TemporaryDirectory() as foreign:
            leaf=self.leaf(root);outside=Path(foreign)/'object';outside.write_bytes(b'foreign')
            outside.chmod(stat.S_IREAD)
            try:
                with patch.object(M.sys,'platform','win32'),patch.object(M.os,'chmod') as chmod:
                    for target in (outside,leaf,leaf.parent/'..'/leaf.parent.name/leaf.name):
                        with self.subTest(path=str(target)),self.assertRaises(PermissionError):
                            M._readonly_object_retry(root,os.unlink,str(target),self.denial())
                    chmod.assert_not_called()
                leaf.chmod(stat.S_IREAD)
                original=Path.lstat
                def symlink_metadata(path):
                    value=original(path)
                    if path==symlink_target:
                        values=list(value);values[0]=stat.S_IFLNK | stat.S_IREAD
                        return os.stat_result(values)
                    return value
                for symlink_target in (leaf,leaf.parent):
                    with patch.object(M.sys,'platform','win32'),patch.object(Path,'lstat',symlink_metadata),patch.object(M.os,'chmod') as chmod,self.assertRaises(PermissionError):
                        M._readonly_object_retry(root,os.unlink,str(leaf),self.denial())
                    chmod.assert_not_called()
                self.assertEqual(outside.read_bytes(),b'foreign')
                alias=Path(foreign)/'alias';os.link(leaf,alias)
                with patch.object(M.sys,'platform','win32'),patch.object(M.os,'chmod') as chmod,self.assertRaises(PermissionError):
                    M._readonly_object_retry(root,os.unlink,str(leaf),self.denial())
                chmod.assert_not_called();self.assertEqual(leaf.stat().st_nlink,2)
                if os.name!='nt':alias.unlink()
            finally:
                outside.chmod(stat.S_IREAD | stat.S_IWRITE);leaf.chmod(stat.S_IREAD | stat.S_IWRITE)
    def test_retry_denial_is_not_success_or_unbounded_retry(self):
        with tempfile.TemporaryDirectory() as root:
            leaf=self.leaf(root);leaf.chmod(stat.S_IREAD)
            original=M.os.chmod
            with patch.object(M.sys,'platform','win32'),patch.object(M.os,'chmod',wraps=original) as chmod,patch.object(M.os,'unlink',side_effect=PermissionError('still denied')) as unlink,self.assertRaises(PermissionError):
                M._readonly_object_retry(root,unlink,str(leaf),self.denial())
            self.assertEqual(chmod.call_count,1);self.assertEqual(unlink.call_count,1)
            self.assertTrue(leaf.exists())
    def test_unknown_cleanup_retains_scratch_and_original_refusal(self):
        with tempfile.TemporaryDirectory() as root:
            primary=M.Refusal('original computation refusal')
            with patch.object(M.shutil,'rmtree',side_effect=PermissionError('unknown cleanup')),self.assertRaises(M.Refusal) as caught:
                M._remove_scratch(root,primary)
            self.assertEqual(caught.exception.retained_scratch,root)
            self.assertIs(caught.exception.__cause__,primary);self.assertTrue(Path(root).exists())

class Isolation(unittest.TestCase):
    # INV repository/fixture-git-isolation
    # INV repository/raw-merge-computation-read-only
    def test_ambient_configuration_and_credentials_never_reach_backend(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp);repo=Repository(path/'source');canary=path/'canary'
            config=path/'config';config.write_text('[core]\n hooksPath = '+str(path/'hooks')+'\n[merge "evil"]\n driver = touch '+str(canary)+'\n')
            with patch.dict(os.environ,{'GIT_CONFIG_GLOBAL':str(config),'GIT_CONFIG_COUNT':'1',
                    'GIT_CONFIG_KEY_0':'core.hooksPath','GIT_CONFIG_VALUE_0':str(path/'hooks'),
                    'GIT_DIR':str(repo.path/'.git'),'GIT_OBJECT_DIRECTORY':str(repo.path/'.git/objects'),
                    'GIT_ALTERNATE_OBJECT_DIRECTORIES':str(path/'foreign'),'GITHUB_TOKEN':'credential-canary',
                    'HTTPS_PROXY':'https://invalid.invalid','GIT_ATTR_SOURCE':'0'*40}):
                # Acquire fixture data before introducing caller Git routing context.
                with tempfile.TemporaryDirectory() as scratch:
                    native=M.Native(M.Backend(GIT,PROFILE),M.Budget(),scratch)
                    self.assertNotIn('GITHUB_TOKEN',native.env);self.assertNotIn('HTTPS_PROXY',native.env)
                    self.assertNotIn('GIT_DIR',native.env);self.assertNotIn('GIT_OBJECT_DIRECTORY',native.env)
                    self.assertEqual(native.run(['rev-parse','--is-bare-repository']),b'true\n')
                    with self.assertRaises(M.Refusal):native.run(['ls-remote','https://invalid.invalid/repo'])
            self.assertFalse(canary.exists())
    def test_native_streaming_output_and_deadline_kill_owned_group(self):
        with tempfile.TemporaryDirectory() as tmp:
            native=M.Native(M.Backend(GIT,PROFILE),M.Budget(),tmp)
            with patch.dict(M.LIMITS,{'command-output-bytes':1}),self.assertRaises(M.Refusal):
                native.run(['--version'])
            native.budget.deadline=time.monotonic()-1
            with self.assertRaises(M.Refusal):native.run(['--version'])


    def test_live_deadline_terminates_parent_and_descendant_before_canary(self):
        # INV repository/raw-merge-computation-read-only
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp);owned=path/'owned';owned.mkdir()
            native=M.Native(M.Backend(GIT,PROFILE),M.Budget(),owned)
            canary=path/'descendant-effect';started=path/'started'
            child="import time,pathlib; time.sleep(1); pathlib.Path("+repr(str(canary))+").write_text('alive')"
            parent="import subprocess,sys,time,pathlib; subprocess.Popen([sys.executable,'-I','-S','-c',"+repr(child)+"]); pathlib.Path("+repr(str(started))+").write_text('started'); time.sleep(10)"
            original=subprocess.Popen
            def fixture_process(argv,**kwargs):
                return original([sys.executable,'-I','-S','-c',parent] if argv[0]==GIT else argv,**kwargs)
            native.budget.deadline=time.monotonic()+.3
            with patch.object(M.subprocess,'Popen',side_effect=fixture_process),self.assertRaises(M.Refusal):
                native.run(['--version'])
            self.assertTrue(started.exists())
            time.sleep(1.1)
            self.assertFalse(canary.exists())
    def test_streaming_refuses_while_child_is_still_producing(self):
        # INV repository/raw-merge-computation-read-only
        with tempfile.TemporaryDirectory() as tmp:
            native=M.Native(M.Backend(GIT,PROFILE),M.Budget(),tmp)
            original=subprocess.Popen
            def fixture_process(argv,**kwargs):
                return original([sys.executable,'-I','-S','-c',
                    "import os,time; os.write(1,b'x'*100000); time.sleep(10)"] if argv[0]==GIT else argv,**kwargs)
            start=time.monotonic()
            with patch.object(M.subprocess,'Popen',side_effect=fixture_process),patch.dict(M.LIMITS,{'command-output-bytes':1000}),self.assertRaises(M.Refusal):
                native.run(['--version'])
            self.assertLess(time.monotonic()-start,3)


    def test_scratch_is_observed_during_active_native_process(self):
        # INV repository/raw-merge-computation-read-only
        with tempfile.TemporaryDirectory() as tmp:
            native=M.Native(M.Backend(GIT,PROFILE),M.Budget(),tmp)
            original=subprocess.Popen
            script="import pathlib,time; pathlib.Path('large').write_bytes(b'x'*200000); time.sleep(10)"
            def fixture_process(argv,**kwargs):
                return original([sys.executable,'-I','-S','-c',script] if argv[0]==GIT else argv,**kwargs)
            start=time.monotonic()
            with patch.object(M.subprocess,'Popen',side_effect=fixture_process),patch.dict(M.LIMITS,{'scratch-bytes':100000}),self.assertRaises(M.Refusal):
                native.run(['--version'])
            self.assertLess(time.monotonic()-start,3)
    def test_missing_group_termination_receipt_is_refusal_and_retains_custody(self):
        # INV repository/raw-merge-computation-read-only
        with tempfile.TemporaryDirectory() as tmp:
            native=M.Native(M.Backend(GIT,PROFILE),M.Budget(),tmp)
            class Process:
                pid=999999999
                def poll(self):return 0
                def wait(self,timeout=None):return 0
            if os.name=='nt':
                class Receipt:returncode=1
                boundary=patch.object(M.subprocess,'run',return_value=Receipt())
            else:
                boundary=patch.object(M.os,'killpg',side_effect=PermissionError())
            with boundary,self.assertRaises(M.Refusal) as caught:native.kill(Process())
            self.assertTrue(native.cleanup_failed)
            self.assertEqual(caught.exception.retained_scratch,str(Path(tmp)))

if __name__=='__main__':unittest.main()
