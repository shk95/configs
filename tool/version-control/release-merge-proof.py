"""Bounded raw Git computation. No acquisition, publication or runtime admission."""
# INV repository/raw-merge-computation-read-only
import hashlib
import json
import os
from pathlib import Path
import queue
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time

LIMITS = {'commits':4096, 'parents':32, 'commit-bytes':65536, 'depth':4096,
          'trees':4096, 'blobs':4096, 'blob-bytes':1048576, 'raw-bytes':16777216,
          'manifest-bytes':262144, 'chunk-bytes':1048576, 'chunks':24,
          'carrier-bytes':25165824, 'scratch-bytes':268435456,
          'proof-seconds':120, 'command-output-bytes':1048576}
EXPANDED_INPUT_BYTES = 16777216
HEX40 = re.compile(r'[0-9a-f]{40}\Z')
HEX64 = re.compile(r'[0-9a-f]{64}\Z')
RESERVED = {'con','prn','aux','nul'} | {prefix+str(n) for prefix in ('com','lpt') for n in range(1,10)}

class Refusal(ValueError):
    def __init__(self, reason, retained_scratch=None):
        super().__init__(reason)
        self.retained_scratch = retained_scratch

def require(condition, reason):
    if not condition:
        raise Refusal(reason)

def integer(value, minimum=0):
    return type(value) is int and value >= minimum

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode('utf-8')

def oid(kind, raw):
    return hashlib.sha1(kind.encode('ascii') + b' ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()

def fields(value, keys, label):
    require(type(value) is dict and set(value) == set(keys), label + ' fields')

def digest(value, pattern, label):
    require(type(value) is str and pattern.fullmatch(value), label)

def _json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    try:
        value = json.loads(raw.decode('utf-8'), object_pairs_hook=pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(Refusal('nonfinite JSON')))
        stack = [(value,0)]
        while stack:
            item, depth = stack.pop()
            require(depth <= 8,'JSON structure depth')
            if type(item) is dict:
                stack.extend((child,depth+1) for child in item.values())
            elif type(item) is list:
                stack.extend((child,depth+1) for child in item)
        require(canonical(value) == raw, 'noncanonical JSON')
        return value
    except (UnicodeError, json.JSONDecodeError, OverflowError, TypeError, RecursionError) as exc:
        raise Refusal('invalid JSON') from exc

class Backend:
    """Programmer-owned capability; callers must independently provision custody.

    profile is the digest of that caller's immutable runtime profile, not a
    self-asserted manifest selection. This class does not qualify a runtime.
    """
    def __init__(self, executable, profile):
        self.executable = str(Path(executable).resolve(strict=True))
        require(Path(self.executable).is_file(), 'backend executable')
        digest(profile, HEX64, 'backend profile')
        self.profile = profile

class Budget:
    def __init__(self):
        self.deadline = time.monotonic() + LIMITS['proof-seconds']
    def check(self):
        require(time.monotonic() < self.deadline, 'proof deadline')
    def remaining(self):
        self.check()
        remaining = self.deadline - time.monotonic()
        require(remaining > 0,'proof deadline')
        return remaining

class Native:
    """Fresh owned bare ODB; streaming stdout/stderr, bounded input and deadline."""
    def __init__(self, backend, budget, directory):
        self.backend, self.budget = backend, budget
        self.cleanup_failed = False
        self.next_scratch_check = 0
        self.directory = Path(directory)
        self.home = self.directory / 'home'
        self.home.mkdir()
        self.odb = self.directory / 'odb'
        self.env = {'HOME':str(self.home), 'USERPROFILE':str(self.home),
                    'TMPDIR':str(self.directory), 'TMP':str(self.directory), 'TEMP':str(self.directory),
                    'GIT_CONFIG_NOSYSTEM':'1', 'GIT_CONFIG_GLOBAL':os.devnull,
                    'GIT_ATTR_NOSYSTEM':'1', 'GIT_TERMINAL_PROMPT':'0',
                    'GIT_ALLOW_PROTOCOL':'', 'GIT_NO_REPLACE_OBJECTS':'1',
                    'GIT_OPTIONAL_LOCKS':'0', 'LC_ALL':'C', 'LANG':'C',
                    'GIT_CONFIG_COUNT':'0'}
        # Windows process loading uses these OS locations; no caller PATH or Git config.
        for name in ('SystemRoot', 'WINDIR'):
            if name in os.environ:
                self.env[name] = os.environ[name]
        self.run(['init', '--bare', '--object-format=sha1', '--template=', str(self.odb)])
        version = self.run(['--version']).strip()
        expected = b'git version 2.55.0.windows.5' if os.name == 'nt' else b'git version 2.55.0'
        require(version == expected, 'unsupported native Git version')

    def kill(self, process):
        failed = False
        if os.name == 'nt':
            system = self.env.get('SystemRoot')
            require(system is not None, 'Windows process-group runtime unavailable')
            try:
                receipt = subprocess.run([str(Path(system)/'System32'/'taskkill.exe'),
                    '/PID',str(process.pid),'/T','/F'], stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,timeout=5,env=self.env)
                failed = receipt.returncode != 0
            except (OSError, subprocess.TimeoutExpired):
                failed = True
        else:
            try:
                os.killpg(process.pid,signal.SIGKILL)
            except ProcessLookupError:
                pass
            except PermissionError:
                # Reap a vanished parent before checking group absence; its exit
                # alone says nothing about still-owned descendants.
                failed = process.poll() is None
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()  # Best effort only: never successful group cleanup.
            process.wait(timeout=5)
            failed = True
        if os.name != 'nt':
            stop = time.monotonic()+2
            while True:
                try:
                    os.killpg(process.pid,0)
                except ProcessLookupError:
                    break
                except PermissionError:
                    failed = True
                    break
                if time.monotonic() >= stop:
                    failed = True
                    break
                time.sleep(.02)
        if failed:
            self.cleanup_failed = True
            raise Refusal('owned group absence unverified; scratch retained',str(self.directory))

    def run(self, arguments, raw=None, attribute_source=None):
        self.budget.check()
        self.scratch_check()
        require(raw is None or type(raw) is bytes and len(raw) <= LIMITS['chunk-bytes'], 'command input bound')
        env = dict(self.env)
        if attribute_source is not None:
            digest(attribute_source, HEX40, 'attribute source')
            env['GIT_ATTR_SOURCE'] = attribute_source
        argv = [self.backend.executable, '-c', 'core.hooksPath=' + str(self.home),
                '-c', 'core.attributesFile=' + os.devnull, '-c', 'merge.renormalize=false',
                '-c', 'core.commitGraph=false', '-c', 'gc.auto=0',
                '-c', 'maintenance.auto=false']
        if self.odb.exists():
            argv += ['--git-dir=' + str(self.odb)]
        argv += arguments
        options = {'start_new_session':True} if os.name != 'nt' else {'creationflags':subprocess.CREATE_NEW_PROCESS_GROUP}
        try:
            process = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, env=env, cwd=self.home, **options)
        except OSError as exc:
            raise Refusal('native launch unavailable') from exc
        events = queue.Queue(maxsize=8)
        stop = threading.Event()
        def emit(event):
            while not stop.is_set():
                try:
                    events.put(event, timeout=.05)
                    return
                except queue.Full:
                    pass
        def read(pipe, channel):
            try:
                while True:
                    block = pipe.read(16384)
                    if not block:
                        break
                    emit((channel, block))
            except OSError:
                emit(('error', b''))
            finally:
                pipe.close()
                emit((channel, None))
        def write():
            try:
                if raw:
                    process.stdin.write(raw)
                process.stdin.close()
            except (OSError, BrokenPipeError):
                emit(('error', b''))
        threads = [threading.Thread(target=read, args=(process.stdout,'out'), daemon=True),
                   threading.Thread(target=read, args=(process.stderr,'err'), daemon=True),
                   threading.Thread(target=write, daemon=True)]
        for thread in threads:
            thread.start()
        output, errors, total, ended = bytearray(), bytearray(), 0, set()
        try:
            while len(ended) < 2:
                remaining = self.budget.remaining()
                if time.monotonic() >= self.next_scratch_check:
                    self.scratch_check()
                    self.next_scratch_check = time.monotonic()+.05
                try:
                    channel, block = events.get(timeout=min(.05, remaining))
                except queue.Empty:
                    continue
                require(channel != 'error', 'native pipe failed')
                if block is None:
                    ended.add(channel)
                    continue
                total += len(block)
                require(total <= LIMITS['command-output-bytes'], 'command output bound')
                (output if channel == 'out' else errors).extend(block)
            status = process.wait(timeout=self.budget.remaining())
            require(status == 0, 'native command refused: ' + arguments[0])
            self.budget.check()
            self.scratch_check()
            return bytes(output)
        except (subprocess.TimeoutExpired, Refusal):
            self.kill(process)
            raise Refusal('native failure or bound: ' + arguments[0])
        finally:
            stop.set()
            for thread in threads:
                thread.join(timeout=.2)

    def scratch_check(self, force=False):
        self.budget.check()
        if not force and time.monotonic() < self.next_scratch_check:
            return
        total = 0
        def inaccessible(error):
            raise Refusal('scratch accounting unavailable') from error
        for parent, directories, names in os.walk(self.directory,onerror=inaccessible):
            require(not any((Path(parent)/name).is_symlink() for name in directories),'unexpected scratch directory symlink')
            for name in names:
                self.budget.check()
                path = Path(parent) / name
                require(not path.is_symlink(), 'unexpected scratch symlink')
                try:
                    total += path.stat().st_size
                except FileNotFoundError:
                    # Git can atomically retire its own temporary object file.
                    continue
                except OSError as exc:
                    raise Refusal('scratch accounting unavailable') from exc
                require(total <= LIMITS['scratch-bytes'], 'scratch bound')
        self.next_scratch_check = time.monotonic()+.05


def read_carrier(manifest_bytes, chunks, backend, budget):
    require(type(manifest_bytes) is bytes and len(manifest_bytes) <= LIMITS['manifest-bytes'], 'manifest bound')
    manifest = _json(manifest_bytes)
    fields(manifest, ('format','kind','roots','runtime-profile','objects','chunks','raw-bytes'), 'manifest')
    require(type(manifest['format']) is int and manifest['format'] == 1 and
            manifest['kind'] == 'required-refresh-merge', 'carrier format')
    fields(manifest['roots'], ('previous','base','merge-base'), 'roots')
    for value in manifest['roots'].values():
        digest(value, HEX40, 'root')
    digest(manifest['runtime-profile'], HEX64, 'runtime profile')
    require(manifest['runtime-profile'] == backend.profile, 'backend profile mismatch')
    rows, descriptors = manifest['chunks'], manifest['objects']
    require(type(rows) is list and 0 < len(rows) <= LIMITS['chunks'], 'chunk count')
    require(type(chunks) is tuple and len(chunks) == len(rows), 'literal chunk tuple')
    require(type(descriptors) is list and len(descriptors) <= sum(LIMITS[x] for x in ('commits','trees','blobs')), 'object count')
    total_carrier = len(manifest_bytes)
    for number, (row, raw) in enumerate(zip(rows,chunks),1):
        budget.check()
        fields(row, ('number','size','sha256','git-blob'), 'chunk')
        require(type(raw) is bytes and 0 < len(raw) <= LIMITS['chunk-bytes'], 'chunk size')
        require(type(row['number']) is int and row['number'] == number and
                type(row['size']) is int and row['size'] == len(raw), 'chunk number/size')
        digest(row['sha256'], HEX64, 'chunk sha256'); digest(row['git-blob'], HEX40, 'chunk blob')
        require(hashlib.sha256(raw).hexdigest() == row['sha256'] and oid('blob',raw) == row['git-blob'], 'chunk identity')
        total_carrier += len(raw)
    require(total_carrier <= LIMITS['carrier-bytes'], 'carrier bound')
    objects, counts, raw_total, chunk_no, offset, prior = {}, {'commit':0,'tree':0,'blob':0}, 0, 1, 0, ''
    for row in descriptors:
        budget.check()
        fields(row, ('oid','type','size','chunk','offset'), 'object')
        identity, kind, size = row['oid'], row['type'], row['size']
        digest(identity, HEX40, 'object oid')
        require(identity > prior, 'object OID order/uniqueness'); prior = identity
        require(type(kind) is str and kind in counts and integer(size), 'object type/size')
        counts[kind] += 1
        require(counts[kind] <= LIMITS[kind+'s'], 'object type count')
        require(size <= LIMITS['commit-bytes'] if kind == 'commit' else size <= LIMITS['blob-bytes'], 'payload type bound')
        header = (kind + ' ' + str(size) + ' ' + identity + '\n').encode('ascii')
        length = len(header) + size
        require(length <= LIMITS['chunk-bytes'], 'frame bound')
        if offset + length > LIMITS['chunk-bytes']:
            require(offset == len(chunks[chunk_no-1]), 'canonical chunk boundary')
            chunk_no += 1; offset = 0
        require(integer(row['chunk'],1) and row['chunk'] == chunk_no and
                integer(row['offset']) and row['offset'] == offset and chunk_no <= len(chunks), 'canonical frame placement')
        block = chunks[chunk_no-1]
        require(block[offset:offset+len(header)] == header and offset+length <= len(block), 'frame header/length')
        raw = block[offset+len(header):offset+length]
        require(oid(kind,raw) == identity, 'raw object identity')
        objects[identity] = (kind,raw)
        offset += length; raw_total += size
        require(raw_total <= LIMITS['raw-bytes'], 'raw bound')
    require(chunk_no == len(chunks) and offset == len(chunks[-1]), 'unused chunk bytes')
    require(integer(manifest['raw-bytes']) and manifest['raw-bytes'] == raw_total, 'raw byte total')
    return manifest, objects


def parse_commit(raw):
    require(len(raw) <= LIMITS['commit-bytes'] and b'\n\n' in raw, 'commit framing')
    header = raw.split(b'\n\n',1)[0]
    records = []
    for line in header.split(b'\n'):
        require(b'\0' not in line and b'\r' not in line, 'commit header encoding')
        if line.startswith(b' '):
            require(records and records[-1][0] in (b'gpgsig',b'gpgsig-sha256',b'mergetag'), 'commit continuation')
            continue
        require(b' ' in line, 'commit header')
        key, value = line.split(b' ',1)
        require(re.fullmatch(b'[a-z][a-z0-9-]*',key) and value, 'commit key/value')
        records.append((key,value))
    require(records and records[0][0] == b'tree', 'commit tree position')
    known = {b'tree',b'parent',b'author',b'committer',b'encoding',b'gpgsig',b'gpgsig-sha256',b'mergetag'}
    require(all(key in known for key,_ in records), 'unsupported commit header')
    for key in (b'tree',b'author',b'committer'):
        require(sum(k == key for k,_ in records) == 1, 'commit mandatory header')
    for key in (b'encoding',b'gpgsig',b'gpgsig-sha256'):
        require(sum(k == key for k,_ in records) <= 1, 'duplicate commit header')
    for key,value in records:
        if key in (b'author',b'committer'):
            require(re.fullmatch(rb'[^<>\x00-\x1f\x7f]+ <[^<> \x00-\x1f\x7f]+> (0|[1-9][0-9]{0,11}) [+-][0-2][0-9][0-5][0-9]',value) and int(value[-4:-2]) <= 23,
                    'unsupported commit identity/timestamp')
    require(all(value.lower() in (b'utf-8',b'utf8') for key,value in records if key == b'encoding'), 'unsupported commit encoding')
    tree = records[0][1].decode('ascii',errors='replace')
    digest(tree, HEX40, 'commit tree')
    parents = [v.decode('ascii',errors='replace') for k,v in records if k == b'parent']
    require(len(parents) <= LIMITS['parents'] and len(set(parents)) == len(parents), 'commit parents bound/duplicate')
    for parent in parents:
        digest(parent,HEX40,'commit parent')
    require([k for k,_ in records[1:1+len(parents)]] == [b'parent']*len(parents), 'parent header position')
    return tree, parents


def verify_graph(objects, roots, budget):
    commits = {identity:parse_commit(raw) for identity,(kind,raw) in objects.items() if kind == 'commit'}
    visited, active, depth = set(), set(), {}
    for root in (roots['previous'],roots['base']):
        require(root in commits,'missing root commit')
        stack = [(root,False)]
        while stack:
            budget.check(); node, done = stack.pop()
            if done:
                active.remove(node); visited.add(node)
                depth[node] = 1 + max((depth[p] for p in commits[node][1]),default=0)
                require(depth[node] <= LIMITS['depth'],'DAG depth bound')
            elif node not in visited:
                require(node in commits and node not in active,'missing/cyclic DAG')
                active.add(node); stack.append((node,True))
                stack.extend((parent,False) for parent in reversed(commits[node][1]))
    require(visited == set(commits),'unused commit')
    def ancestors(root):
        found, stack = set(), [root]
        while stack:
            budget.check(); node = stack.pop()
            if node not in found:
                found.add(node); stack.extend(commits[node][1])
        return found
    common = ancestors(roots['previous']) & ancestors(roots['base'])
    nonbest = {parent for node in common for parent in commits[node][1]}
    best = common - nonbest
    require(len(best) == 1 and best == {roots['merge-base']},'nonunique/incorrect best base')
    return commits


def tree_entries(raw):
    rows, position, prior, names = [], 0, None, set()
    while position < len(raw):
        space, zero = raw.find(b' ',position), raw.find(b'\0',position)
        require(position < space < zero and zero+21 <= len(raw),'tree framing')
        mode, name = raw[position:space], raw[space+1:zero]
        require(mode in (b'40000',b'100644',b'100755'),'unsupported tree mode')
        try:
            text = name.decode('utf-8')
        except UnicodeError as exc:
            raise Refusal('unsupported path encoding') from exc
        require(name and b'/' not in name and b'\\' not in name and
                text not in ('.','..') and text.lower() != '.git' and
                not any(ord(c)<32 or ord(c)==127 for c in text) and
                not any(c in text for c in ':*?"<>|') and not text.endswith((' ','.')) and
                text.split('.',1)[0].lower() not in RESERVED,
                'unsafe tree name')
        require(name not in names,'duplicate tree name'); names.add(name)
        sort = name + (b'/' if mode == b'40000' else b'\0')
        require(prior is None or prior < sort,'tree sort'); prior = sort
        rows.append((mode.decode(),text,raw[zero+1:zero+21].hex()))
        position = zero+21
    return rows


def snapshots(objects, commits, roots, budget):
    used, result, attrs = set(), {}, {}
    for label, root in roots.items():
        inventory, attributes, stack, expanded = {}, {}, [(commits[root][0],'',0)], 1
        while stack:
            budget.check(); identity, prefix, level = stack.pop()
            require(level <= 256 and len(prefix.encode('utf-8')) <= 4096,'snapshot path bound')
            require(identity in objects and objects[identity][0] == 'tree','missing snapshot tree')
            used.add(identity)
            rows = tree_entries(objects[identity][1])
            expanded += len(rows)
            require(expanded <= 8192,'snapshot expanded-entry bound')
            inventory[prefix] = ('40000',identity)
            require(len(inventory) <= 8192,'snapshot inventory bound')
            for mode,name,child in rows:
                path = prefix+name
                require(len(path.encode('utf-8')) <= 4096,'snapshot path bytes bound')
                if mode == '40000':
                    stack.append((child,path+'/',level+1))
                else:
                    require(child in objects and objects[child][0] == 'blob','missing snapshot blob')
                    used.add(child); inventory[path] = (mode,child)
                    require(len(inventory) <= 8192,'snapshot inventory bound')
                    if name == '.gitattributes':
                        require(mode == '100644','attribute executable mode')
                        attributes[path] = (mode,child)
        result[label], attrs[label] = inventory, attributes
    require(used == {x for x,(kind,_) in objects.items() if kind != 'commit'},'unused snapshot objects')
    require(attrs['previous'] == attrs['base'] == attrs['merge-base'],'attribute evolution')
    for _,identity in attrs['previous'].values():
        parse_attributes(objects[identity][1])
    return result


def parse_attributes(raw):
    require(len(raw) <= 65536,'attribute bytes bound')
    try:
        text = raw.decode('utf-8')
    except UnicodeError as exc:
        raise Refusal('attribute encoding') from exc
    for line in text.splitlines():
        require(len(line.encode('utf-8')) <= 4096,'attribute line bound')
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        words = line.split()
        require(len(words) >= 2 and not words[0].startswith(('!','[attr]')) and
                not any(c in words[0] for c in ('"','\\','\0')),'attribute pattern subset')
        values = words[1:]
        require(all(x in ('text','-text','text=auto','eol=lf','eol=crlf','binary') for x in values), 'attribute unsupported value')
        require(len(values) == len(set(values)),'duplicate attribute')
        require(sum(x in values for x in ('text','-text','text=auto','binary')) <= 1 and
                sum(x in values for x in ('eol=lf','eol=crlf')) <= 1 and
                not (any(x in values for x in ('binary','-text')) and any(x.startswith('eol=') for x in values)),
                'attribute conflicting values')


def novel_result(native, tree, objects, budget):
    novel, inventory, stack = {}, {}, [(tree,'',0)]
    total, expanded = 0, 1
    while stack:
        budget.check(); identity, prefix, level = stack.pop()
        require(level <= 256 and len(prefix.encode('utf-8')) <= 4096,'result path bound')
        require(identity not in objects or objects[identity][0] == 'tree','computed directory type')
        raw = native.run(['cat-file','tree',identity])
        require(oid('tree',raw) == identity,'computed tree identity')
        inventory[prefix] = ('40000',identity)
        if identity not in objects and identity not in novel:
            require(len(novel)+1 <= 8 and total+len(raw) <= 524288,'complete novel closure bound')
            novel[identity] = ('tree',raw); total += len(raw)
        rows = tree_entries(raw)
        expanded += len(rows)
        require(expanded <= 8192,'result expanded-entry bound')
        for mode,name,child in rows:
            path = prefix+name
            require(len(path.encode('utf-8')) <= 4096,'result path bytes bound')
            if mode == '40000':
                stack.append((child,path+'/',level+1))
            else:
                inventory[path] = (mode,child)
                require(child not in objects or objects[child][0] == 'blob','computed leaf type')
                if child not in objects and child not in novel:
                    require(len(novel)+1 <= 8,'complete novel closure bound')
                    body = native.run(['cat-file','blob',child])
                    require(oid('blob',body) == child,'computed blob identity')
                    require(total+len(body) <= 524288,'complete novel closure bound')
                    novel[child] = ('blob',body); total += len(body)
            require(len(inventory) <= 8192,'result inventory bound')
        require(len(novel) <= 8 and total <= 524288,'complete novel closure bound')
    # Child-first ordering, shared children emitted once; no arbitrary pack.
    ordered, emitted = [], set()
    stack = [(tree,False)]
    while stack:
        budget.check(); identity, done = stack.pop()
        if identity in emitted or identity not in novel:
            continue
        kind, raw = novel[identity]
        if done or kind == 'blob':
            emitted.add(identity); ordered.append({'oid':identity,'type':kind,'raw':raw})
        else:
            stack.append((identity,True))
            stack.extend((child,False) for _,_,child in reversed(tree_entries(raw)) if child in novel)
    require(emitted == set(novel),'novel closure dependency order')
    return inventory, ordered


def verify_merge(manifest_bytes, chunks, trusted_backend):
    require(type(trusted_backend) is Backend,'programmer-owned backend capability required')
    budget = Budget()
    manifest, objects = read_carrier(manifest_bytes,chunks,trusted_backend,budget)
    roots = manifest['roots']
    commits = verify_graph(objects,roots,budget)
    inventories = snapshots(objects,commits,roots,budget)
    # Bound expanded input work independently of unique-object carrier size.
    # This is not an allocation proof for Git or a hard filesystem quota.
    expanded_bytes = sum(len(objects[identity][1]) for inventory in inventories.values()
                         for _,identity in inventory.values())
    require(expanded_bytes <= EXPANDED_INPUT_BYTES,'expanded input bytes bound')
    directory = tempfile.mkdtemp(prefix='configs-raw-merge-')
    native = None
    try:
        native = Native(trusted_backend,budget,directory)
        for identity,(kind,raw) in objects.items():
            result = native.run(['hash-object','-w','-t',kind,'--stdin'],raw)
            require(result == (identity+'\n').encode('ascii'),'materialized object identity')
        crosscheck = native.run(['merge-base','--all',roots['previous'],roots['base']])
        require(crosscheck == (roots['merge-base']+'\n').encode('ascii'),'native merge-base mismatch')
        output = native.run(['merge-tree','--write-tree','--no-messages',
                             '--merge-base='+roots['merge-base'],roots['previous'],roots['base']],
                            attribute_source=roots['previous'])
        require(re.fullmatch(b'[0-9a-f]{40}\n',output),'native merge output')
        tree = output[:-1].decode('ascii')
        inventory, novel = novel_result(native,tree,objects,budget)
        native.scratch_check(force=True)
        budget.check()
        return {'roots':dict(roots), 'merge-base':roots['merge-base'], 'tree':tree,
                'inventory':inventory, 'objects':novel}
    finally:
        if getattr(sys.exc_info()[1],'retained_scratch',None) != directory and (native is None or not native.cleanup_failed):
            try:
                shutil.rmtree(directory)
            except OSError as exc:
                raise Refusal('owned scratch cleanup unavailable',directory) from exc
