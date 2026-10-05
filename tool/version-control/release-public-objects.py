"""Fixed anonymous original object proof; no ref or publication capability."""
# INV repository/public-refresh-object-transport
import base64
import datetime
import hashlib
import http.client
import json
import re
import ssl
import time

PUBLIC = 'shk95/configs'
PUBLIC_ID = 1330390069
MAX_RAW = 256 * 1024
MAX_RESPONSE = 4 * 1024 * 1024

class Refusal(ValueError):
    pass

def need(value, reason):
    if not value:
        raise Refusal(reason)

def oid(kind, raw):
    return hashlib.sha1(kind.encode() + b' ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()

def identity(value):
    need(type(value) is str and re.fullmatch('[a-f0-9]{40}', value), 'object identity')
    return value

def decode(raw):
    need(type(raw) is bytes and len(raw) <= MAX_RESPONSE, 'response bound')
    def unique(rows):
        result = {}
        for key, value in rows:
            need(key not in result, 'duplicate key')
            result[key] = value
        return result
    try:
        return json.loads(raw.decode('utf-8'), object_pairs_hook=unique,
            parse_constant=lambda _: (_ for _ in ()).throw(Refusal('nonfinite response')))
    except (ValueError, UnicodeError, RecursionError, OverflowError) as exc:
        raise Refusal('invalid response') from exc

def raw_base64(value):
    need(type(value) is str and len(value) <= MAX_RESPONSE, 'base64 bound')
    try:
        text = value.replace('\n', '')
        raw = base64.b64decode(text, validate=True)
        need(base64.b64encode(raw).decode() == text and len(raw) <= MAX_RAW, 'canonical base64')
        return raw
    except (ValueError, UnicodeError) as exc:
        raise Refusal('base64') from exc

def entries(raw):
    need(type(raw) is bytes and len(raw) <= MAX_RAW, 'raw tree bound')
    result, cursor, prior = [], 0, None
    while cursor < len(raw):
        space, zero = raw.find(b' ', cursor), raw.find(b'\0', cursor)
        need(cursor < space < zero and zero + 21 <= len(raw), 'tree framing')
        mode, name = raw[cursor:space], raw[space+1:zero]
        need(mode in (b'40000', b'100644', b'100755', b'120000', b'160000') and
             name and len(name)<=255 and name not in (b'.', b'..') and b'/' not in name and
             not any(c < 32 or c == 127 for c in name), 'tree member')
        order = name + (b'/' if mode == b'40000' else b'\0')
        need(prior is None or prior < order, 'tree order'); prior = order
        try:
            text = name.decode('utf-8')
        except UnicodeError as exc:
            raise Refusal('tree encoding') from exc
        result.append({'path': text, 'mode': mode.decode().zfill(6),
            'type': 'tree' if mode == b'40000' else 'commit' if mode == b'160000' else 'blob',
            'sha': raw[zero+1:zero+21].hex()})
        cursor = zero + 21
        need(len(result) <= 4096, 'tree entry bound')
    return result

def date_epoch(value):
    need(type(value) is str and re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z', value), 'UTC date')
    try:
        parsed = datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=datetime.timezone.utc)
        epoch = int(parsed.timestamp())
        need(epoch >= 0 and datetime.datetime.fromtimestamp(epoch, datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ') == value, 'UTC round trip')
        return epoch
    except (ValueError, OverflowError, OSError) as exc:
        raise Refusal('unsupported date') from exc

def commit_fields(raw, generated=False):
    need(type(raw) is bytes and 0 < len(raw) <= MAX_RAW and b'\n\n' in raw, 'commit framing')
    header, message = raw.split(b'\n\n', 1)
    rows = []
    for line in header.split(b'\n'):
        need(b'\r' not in line and b'\0' not in line, 'commit controls')
        if line.startswith(b' '):
            need(rows and rows[-1][0] in (b'gpgsig', b'gpgsig-sha256', b'mergetag'), 'commit continuation')
            continue
        need(b' ' in line, 'commit header')
        key, value = line.split(b' ', 1)
        need(key in (b'tree', b'parent', b'author', b'committer', b'encoding', b'gpgsig', b'gpgsig-sha256', b'mergetag') and value, 'commit field')
        rows.append((key, value))
    need(rows and rows[0][0] == b'tree', 'commit tree')
    for key in (b'encoding', b'gpgsig', b'gpgsig-sha256'):
        need(sum(k == key for k,_ in rows)<=1, 'duplicate optional header')
    for key in (b'tree', b'author', b'committer'):
        need(sum(k == key for k, _ in rows) == 1, 'commit mandatory field')
    try:
        parents = [identity(v.decode('ascii')) for k, v in rows if k == b'parent']
        result = {'tree': identity(rows[0][1].decode('ascii')), 'parents': parents, 'message': message.decode('utf-8')}
    except UnicodeError as exc:
        raise Refusal('unsupported commit encoding') from exc
    need(len(parents) <= 32 and len(parents) == len(set(parents)) and
         [k for k, _ in rows[1:1+len(parents)]] == [b'parent'] * len(parents), 'commit parents')
    for kind in ('author', 'committer'):
        value = next(v for k, v in rows if k == kind.encode())
        match = re.fullmatch(rb'([^<>\x00-\x1f\x7f]+) <([^<> \x00-\x1f\x7f]+)> ([0-9]{1,12}) ([+-][0-2][0-9][0-5][0-9])', value)
        need(match and int(match[4][1:3]) <= 23, 'commit actor')
        try:
            zone = match[4].decode(); seconds = (int(zone[1:3])*60 + int(zone[3:]))*60
            if zone[0] == '-': seconds = -seconds
            instant = datetime.datetime.fromtimestamp(int(match[3]), datetime.timezone.utc)
            local = instant.astimezone(datetime.timezone(datetime.timedelta(seconds=seconds)))
            result[kind] = {'name': match[1].decode('utf-8'), 'email': match[2].decode('utf-8'),
                'date': instant.isoformat().replace('+00:00', 'Z')}
        except (ValueError, UnicodeError, OverflowError, OSError) as exc:
            raise Refusal('commit date') from exc
    if generated:
        need([k for k, _ in rows] == [b'tree', b'parent', b'author', b'committer'] and len(parents) == 1,
             'unsigned generated headers')
        for kind in ('author', 'committer'):
            actor = result[kind]
            need(actor['name'] == 'Release controller' and actor['email'] == 'release-controller@example.invalid', 'generated actor')
            need(next(v for k,v in rows if k == kind.encode()).endswith(b' +0000'), 'generated UTC offset')
            date_epoch(actor['date'])
        need(result['author'] == result['committer'], 'generated metadata')
    return result

class Anonymous:
    """Only fixed anonymous GETs; no credential, redirect, proxy or fallback."""
    def request(self, method, path, body, timeout=30):
        need(method == 'GET' and body is None and (path == '/repos/'+PUBLIC or
             re.fullmatch('/repos/'+PUBLIC+r'/git/(blobs|trees|commits)/[a-f0-9]{40}', path)), 'fixed endpoint')
        need(0 < timeout <= 30, 'request timeout')
        stop = time.monotonic() + timeout
        connection = http.client.HTTPSConnection('api.github.com', timeout=timeout, context=ssl.create_default_context())
        def remaining():
            seconds = stop - time.monotonic(); need(seconds > 0, 'request deadline')
            if connection.sock is not None: connection.sock.settimeout(seconds)
        try:
            connection.request('GET', path, headers={'Accept': 'application/vnd.github+json',
                'X-GitHub-Api-Version': '2026-03-10', 'User-Agent': 'configs-public-object-proof'})
            remaining(); response = connection.getresponse(); raw = bytearray()
            while True:
                remaining(); block = response.read1(min(16384, MAX_RESPONSE + 1 - len(raw)))
                if not block: break
                raw.extend(block); need(len(raw) <= MAX_RESPONSE, 'response bound')
            remaining()
            return response.status, {k.lower(): v for k,v in response.getheaders()}, bytes(raw)
        except (OSError, http.client.HTTPException) as exc:
            raise Refusal('unavailable read') from exc
        finally: connection.close()

class Reader:
    def __init__(self, channel=None):
        self.channel = channel if channel is not None else Anonymous()
        self.deadline=time.monotonic()+900
        self.requests=0;self.response_bytes=0
    def get(self, kind, sha):
        need(kind in ('blob','tree','commit'), 'object type'); identity(sha)
        return self.call('/git/'+kind+'s/'+sha)
    def call(self, suffix):
        need(suffix == '' or re.fullmatch(r'/git/(blobs|trees|commits)/[a-f0-9]{40}', suffix), 'fixed suffix')
        self.requests+=1
        need(self.requests<=32768 and time.monotonic()<self.deadline,'read aggregate bound')
        try:
            if type(self.channel) is Anonymous:
                code,headers,raw=self.channel.request('GET','/repos/'+PUBLIC+suffix,None,timeout=min(30,self.deadline-time.monotonic()))
            else:
                code, headers, raw = self.channel.request('GET', '/repos/'+PUBLIC+suffix, None)
        except (OSError, ValueError) as exc:
            raise Refusal('unavailable read') from exc
        need(time.monotonic()<self.deadline,'read deadline')
        self.response_bytes+=len(raw) if type(raw) is bytes else MAX_RESPONSE+1
        need(self.response_bytes<=128*1024*1024,'read total bytes')
        need(type(headers) is dict and not any(k.lower() in ('location','link') for k in headers), 'redirect or pagination')
        need(type(raw) is bytes and len(raw) <= MAX_RESPONSE and code in (200,404), 'unknown object read')
        return code, decode(raw) if code == 200 else None
    def prove(self, kind, sha, raw, generated=False):
        need(type(raw) is bytes and len(raw) <= MAX_RAW and oid(kind, raw) == sha, 'original raw identity')
        code, value = self.get(kind, sha)
        if code == 404: return False
        need(type(value) is dict and value.get('sha') == sha, 'typed identity')
        if kind == 'blob':
            need(value.get('encoding') == 'base64' and type(value.get('size')) is int and
                 value['size'] == len(raw) and raw_base64(value.get('content')) == raw, 'blob proof')
        elif kind == 'tree':
            expected = entries(raw); rows = value.get('tree')
            need(value.get('truncated') is False and type(rows) is list and len(rows) <= 4096, 'complete direct tree')
            actual=[]
            for row in rows:
                need(type(row) is dict and all(k in row for k in ('path','mode','type','sha')), 'tree fields')
                if 'size' in row:
                    need(type(row['size']) is int and 0 <= row['size'] <= MAX_RAW, 'tree size')
                actual.append({k:row[k] for k in ('path','mode','type','sha')})
            need(actual == expected, 'literal direct tree')
        else:
            expected=commit_fields(raw, generated)
            need(type(value.get('tree')) is dict and type(value.get('parents')) is list, 'commit shape')
            need(value['tree'].get('sha') == expected['tree'] and
                 [row.get('sha') for row in value['parents'] if type(row) is dict] == expected['parents'] and
                 len(value['parents']) == len(expected['parents']), 'commit structure')
            for name in ('message','author','committer'):
                actual=value.get(name)
                if name != 'message':
                    need(type(actual) is dict, 'commit actor'); actual={k:actual.get(k) for k in ('name','email','date')}
                need(actual == expected[name], 'commit metadata')
            if generated:
                verification=value.get('verification')
                need(verification is None or type(verification) is dict and
                     verification.get('signature') is None and verification.get('payload') is None,
                     'generated signature')
        return True
    def repository(self):
        code,value=self.call('')
        need(code==200 and type(value) is dict and type(value.get('id')) is int and
            value['id']==PUBLIC_ID and value.get('full_name')==PUBLIC and value.get('private') is False,
            'public repository identity')
        return value['id'],value['full_name'],value['private']
    def qualified(self, kind, sha, raw, reference, generated=False):
        reference_sha, reference_raw = reference
        need(reference_sha != sha and oid(kind, reference_raw) == reference_sha, 'known same-type reference')
        before=self.repository()
        need(self.prove(kind,reference_sha,reference_raw), 'reference unavailable')
        present=self.prove(kind,sha,raw,generated)
        need(self.prove(kind,reference_sha,reference_raw) and self.repository() == before, 'moving qualification')
        return present

def bounded_git(repo, args, environment, *, data=None, limit=MAX_RESPONSE, deadline=None):
    """Owned fixed plumbing, finite streamed output, no checkout or acquisition."""
    import os
    import signal
    import subprocess
    import threading
    need(type(limit) is int and 0 < limit <= 128*1024*1024, 'plumbing output bound')
    need(data is None or type(data) is bytes and len(data)<=128*1024*1024, 'plumbing input bound')
    stop=min(time.monotonic()+30,deadline if deadline is not None else time.monotonic()+30)
    need(stop>time.monotonic(), 'plumbing deadline')
    command=['git','--no-replace-objects','-c','core.hooksPath='+os.devnull,
        '-c','core.fsmonitor=false','-c','gc.auto=0','-C',str(repo),*args]
    process=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,env=environment,start_new_session=os.name!='nt')
    raw=bytearray();errors=bytearray();excess=threading.Event();finished=threading.Event();errors_finished=threading.Event()
    def output(stream,sink,bound,done):
        try:
            while True:
                block=stream.read(16384)
                if not block:break
                if len(sink)+len(block)>bound:excess.set();break
                sink.extend(block)
        finally:done.set()
    def feed():
        try:
            if data:process.stdin.write(data)
        except (BrokenPipeError,OSError):pass
        finally:
            try:process.stdin.close()
            except OSError:pass
    reader=threading.Thread(target=output,args=(process.stdout,raw,limit,finished),daemon=True)
    error_reader=threading.Thread(target=output,args=(process.stderr,errors,MAX_RESPONSE,errors_finished),daemon=True)
    writer=threading.Thread(target=feed,daemon=True)
    reader.start();error_reader.start();writer.start()
    try:
        while process.poll() is None or not finished.is_set() or not errors_finished.is_set():
            need(not excess.is_set() and time.monotonic()<stop, 'plumbing time/output refusal')
            time.sleep(min(0.005,max(0,stop-time.monotonic())))
        reader.join(timeout=max(0,stop-time.monotonic()));error_reader.join(timeout=max(0,stop-time.monotonic()));writer.join(timeout=max(0,stop-time.monotonic()))
        need(not excess.is_set() and process.returncode==0 and time.monotonic()<stop,'plumbing refused')
        return bytes(raw)
    finally:
        if process.poll() is None:
            if os.name!='nt':
                try:os.killpg(process.pid,signal.SIGKILL)
                except ProcessLookupError:pass
            else:process.kill()
            process.wait(timeout=5)
        process.stdout.close();process.stderr.close()
