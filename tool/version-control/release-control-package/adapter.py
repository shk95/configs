"""Pure API contract: construct requests and interpret supplied observations only."""
# INV repository/release-control-preview-only
import json
import hashlib
import re
import base64
from datetime import datetime, timezone
from records import Refusal, canonical, digest, identity, require

# INV repository/immutable-refresh-object-semantics
OBJECT_FIELDS = {'repository', 'batch', 'refresh', 'construction', 'object-type',
                 'object', 'raw', 'dependencies'}
RAW_LIMIT = 256 * 1024


def raw_object(value):
    require(isinstance(value, dict) and set(value) == {'type', 'sha', 'raw'}, 'invalid-raw-object')
    require(value['type'] in {'blob', 'tree', 'commit'} and isinstance(value['raw'], str), 'invalid-object-type')
    identity(value['sha'], 40)
    try:
        raw = base64.b64decode(value['raw'], validate=True)
    except (ValueError, TypeError):
        raise Refusal('invalid-object-base64') from None
    require(len(raw) <= RAW_LIMIT and base64.b64encode(raw).decode('ascii') == value['raw'], 'noncanonical-or-large-object')
    require(hashlib.sha1(value['type'].encode() + b' ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == value['sha'], 'wrong-original-object-hash')
    return raw


def tree_entries(raw):
    entries = []; offset = 0
    while offset < len(raw):
        end = raw.find(b'\0', offset)
        require(end > offset and end + 21 <= len(raw), 'malformed-raw-tree')
        mode, sep, name = raw[offset:end].partition(b' ')
        require(sep and mode in {b'40000', b'100644', b'100755', b'120000', b'160000'}
                and name and len(name) <= 255 and b'/' not in name
                and name not in {b'.', b'..'} and not any(c < 32 or c == 127 for c in name), 'invalid-tree-entry')
        entries.append((mode, name, raw[end+1:end+21].hex()))
        offset = end + 21
    require(len(entries) <= 4096 and len({e[1] for e in entries}) == len(entries), 'duplicate-or-large-tree')
    require(entries == sorted(entries, key=lambda e:e[1] + (b'/' if e[0] == b'40000' else b'')), 'noncanonical-tree-order')
    return entries


def encode_tree(entries):
    return b''.join(mode + b' ' + name + b'\0' + bytes.fromhex(sha) for mode,name,sha in entries)


def commit_headers(raw):
    header, sep, message = raw.partition(b'\n\n')
    require(sep and b'\0' not in raw and b'\r' not in header, 'invalid-commit-framing')
    rows = []; previous = None
    for row in header.split(b'\n'):
        if row.startswith(b' '):
            require(previous is not None and previous not in {b'tree', b'parent'}, 'orphan-commit-continuation')
            continue
        key, space, value = row.partition(b' ')
        require(space and re.fullmatch(b'[a-z][a-z0-9-]*',key) and value, 'invalid-commit-header')
        rows.append((key,value)); previous=key
    trees=[v for k,v in rows if k==b'tree']; parents=[v for k,v in rows if k==b'parent']
    require(len(trees)==1 and len(set(parents))==len(parents), 'ambiguous-commit-graph')
    for item in trees + parents: require(re.fullmatch(b'[a-f0-9]{40}',item), 'invalid-commit-object-id')
    return rows, trees[0].decode(), [p.decode() for p in parents], message


def generated_commit(raw, tree, parent):
    rows, actual_tree, parents, message=commit_headers(raw)
    require([k for k,v in rows]==[b'tree',b'parent',b'author',b'committer']
            and actual_tree==tree and parents==[parent], 'wrong-generated-commit-headers')
    expected=b'Release controller <release-controller@example.invalid> '
    require(rows[2][1]==rows[3][1] and re.fullmatch(re.escape(expected)+b'(0|[1-9][0-9]*) \\+0000', rows[2][1]), 'wrong-generated-identity')
    require(raw.split(b'\n\n',1)[0] == b'\n'.join(k+b' '+v for k,v in rows), 'noncanonical-generated-header')
    require(len(message)<=16384 and message.endswith(b'\n'), 'invalid-generated-message')
    try: text=message.decode('utf-8')
    except UnicodeError: raise Refusal('invalid-generated-message') from None
    lines=text.splitlines()
    names=['Format','Domain','Impact','Contracts','Compatibility','Rationale','Migration']
    require(len(lines)==9 and lines[:2]==['chore(unixlike-deps): refresh reviewed inputs',''], 'wrong-generated-subject')
    values=[]
    for line,name in zip(lines[2:],names):
        prefix='Release-'+name+': '
        require(line.startswith(prefix), 'wrong-release-trailer-order')
        value=line[len(prefix):]
        require(value and value==value.strip() and not any(ord(c)<32 or ord(c)==127 for c in value), 'invalid-release-trailer-value')
        values.append(value)
    fmt,domain,impact,contracts,compatibility,rationale,migration=values
    require(fmt=='1' and domain=='unixlike' and impact in {'none','patch','minor','major'}
            and compatibility in {'compatible','breaking'}, 'unsupported-generated-declaration')
    ids=contracts.split(',')
    require(ids==sorted(set(ids)) and all(re.fullmatch('[a-z0-9][a-z0-9-]*',i) for i in ids), 'invalid-generated-contracts')
    require(migration=='none' or (migration.startswith('docs/') and all(p and p not in {'.','..'} for p in migration.split('/'))), 'invalid-generated-migration')
    require(compatibility!='breaking' or (impact=='major' and migration!='none'), 'incompatible-generated-declaration')
    require(message==('\n'.join(lines)+'\n').encode(), 'noncanonical-generated-message')


def refresh_construction(context, candidate):
    c=context.get('construction')
    require(isinstance(c,dict) and set(c)=={'format','inputs','originals','objects','digest'} and type(c['format']) is int and c['format']==1, 'invalid-refresh-construction')
    require(len(canonical(c))<=1024*1024, 'large-refresh-construction')
    inputs=c['inputs']; keys={'batch','source','base','previous','before-lock','lock','utility-source','utility-manifest','source-fingerprint','preparation'}
    require(isinstance(inputs,dict) and set(inputs)==keys and all(inputs[k]==candidate[k] for k in keys-{'preparation'}), 'wrong-construction-inputs')
    identity(inputs['preparation'])
    require(candidate['previous']=='-' and candidate['parent']==candidate['base'], 'unsupported-refresh-base-update')
    require(c['digest']==digest(canonical({k:c[k] for k in ('format','inputs','originals','objects')})), 'wrong-construction-digest')
    require(isinstance(c['originals'],list) and 1<=len(c['originals'])<=8 and isinstance(c['objects'],list) and 1<=len(c['objects'])<=8, 'invalid-object-count')
    originals={}; total=0
    for obj in c['originals']:
        raw=raw_object(obj); total+=len(raw)
        require(obj['sha'] not in originals, 'duplicate-original-object'); originals[obj['sha']]=(obj['type'],raw)
    used=set()
    def original(sha,kind):
        require(sha in originals and originals[sha][0]==kind, 'missing-original-object')
        used.add(sha); return originals[sha][1]
    rows,root,parents,message=commit_headers(original(candidate['base'],'commit'))
    old_root=tree_entries(original(root,'tree'))
    unix=[e for e in old_root if e[1]==b'unixlike']
    require(len(unix)==1 and unix[0][0]==b'40000', 'missing-original-unixlike-tree')
    old_unix=tree_entries(original(unix[0][2],'tree'))
    locks=[e for e in old_unix if e[1]==b'flake.lock']
    require(len(locks)==1 and locks[0][0] in {b'100644',b'100755'}, 'missing-original-lock')
    require(digest(original(locks[0][2],'blob'))==candidate['before-lock'], 'wrong-original-lock')
    require(context['proof']['before-mode']==context['proof']['mode']==int(locks[0][0],8)&0o777, 'wrong-original-lock-mode')
    require(used==set(originals), 'unused-original-object')
    require(len(c['objects'])==4, 'wrong-generated-object-closure')
    decoded=[]
    for obj in c['objects']:
        require(isinstance(obj,dict) and set(obj)=={'type','sha','raw','dependencies'}, 'invalid-construction-object')
        raw=raw_object({k:obj[k] for k in ('type','sha','raw')}); total+=len(raw); decoded.append(raw)
    require(total<=512*1024 and len({o['sha'] for o in c['objects']})==4, 'large-or-duplicate-construction')
    blob,subtree,tree,commit=c['objects']
    require([o['type'] for o in c['objects']]==['blob','tree','tree','commit'] and digest(decoded[0])==candidate['lock'], 'wrong-generated-lock')
    lock=document(decoded[0])
    require(isinstance(lock,dict) and lock.get('version')==7 and isinstance(lock.get('nodes'),dict)
            and isinstance(lock.get('root'),str) and lock['root'] in lock['nodes'], 'invalid-generated-lock-data')
    require(decoded[1]==encode_tree([(m,n,blob['sha'] if n==b'flake.lock' else s) for m,n,s in old_unix]), 'contaminated-generated-subtree')
    require(decoded[2]==encode_tree([(m,n,subtree['sha'] if n==b'unixlike' else s) for m,n,s in old_root]), 'contaminated-generated-root')
    require(tree['sha']==candidate['tree'] and commit['sha']==candidate['head'], 'wrong-generated-head')
    generated_commit(decoded[3],candidate['tree'],candidate['base'])
    payloads=[]; generated={}
    for obj,raw in zip(c['objects'],decoded):
        if obj['type']=='blob': deps=[]
        elif obj['type']=='tree': deps=[{'type': 'tree' if m==b'40000' else 'commit' if m==b'160000' else 'blob','sha':s} for m,n,s in tree_entries(raw)]
        else: deps=[{'type':'tree','sha':tree['sha']},{'type':'commit','sha':candidate['base']}]
        deps=sorted({(d['type'],d['sha']) for d in deps})
        expected=[{'type':kind,'sha':sha} for kind,sha in deps]
        require(obj['dependencies']==expected and len(expected)<=4096, 'wrong-construction-dependencies')
        descriptor=[dict(d,operation=generated.get(d['sha'],'-')) for d in expected]
        payload={'repository':'shk95/configs','batch':candidate['batch'],'refresh':digest(canonical(candidate)),
                 'construction':c['digest'],'object-type':obj['type'],'object':obj['sha'],'raw':obj['raw'],'dependencies':canonical(descriptor).decode()}
        oid=digest(canonical({'kind':'refresh-object','payload':payload}))
        generated[obj['sha']]=oid; payloads.append((oid,payload))
    return payloads

API_VERSION = "2026-03-10"
BOUNDS = {"writer_minutes": 15, "api_seconds": 30, "cancel_seconds": 30,
          "cancel_limit_seconds": 300, "retry_minutes": [5, 15, 30],
          "wait_job_minutes": [6, 16, 31]}


def document(data):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "duplicate-json-key")
            result[key] = value
        return result
    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=unique,
                          parse_constant=lambda _: (_ for _ in ()).throw(Refusal("nonfinite-json")))
    except (UnicodeError, json.JSONDecodeError):
        raise Refusal("invalid-transcript-json") from None


PAYLOADS = {
    "refresh-object": OBJECT_FIELDS,
    "record": {"repository", "parent", "commit", "event", "index"},
    "pr": {"repository", "head", "base", "dev", "master", "body-operation"},
    "merge": {"repository", "number", "dev", "master", "tree"},
    "tag-object": {"repository", "tag", "source", "annotation", "tagger-time", "tagger-name", "tagger-email", "initial-run", "object"},
    "tag-ref": {"repository", "tag", "object"},
    "cancel": {"repository", "run", "attempt", "workflow", "jobs"},
}

REFRESH_FIELDS = {"batch", "source", "base", "parent", "head", "tree", "before-lock",
                  "lock", "utility-source", "utility-manifest", "source-fingerprint",
                  "previous", "branch"}
for refresh_kind in ("refresh-branch", "refresh-pr"):
    PAYLOADS[refresh_kind] = REFRESH_FIELDS | {"repository"}


def refresh_branch(batch):
    identity(batch)
    return "feature/unixlike-refresh-" + batch


def refresh_candidate(value):
    require(isinstance(value, dict) and set(value) == REFRESH_FIELDS, "invalid-refresh-candidate")
    require(all(isinstance(v, str) for v in value.values()), "invalid-refresh-value")
    for name in ("source", "base", "parent", "head", "tree", "utility-source"):
        identity(value[name], 40)
    for name in ("batch", "before-lock", "lock", "utility-manifest", "source-fingerprint"):
        identity(value[name])
    require(value["previous"] == "-" or identity(value["previous"], 40), "invalid-refresh-previous")
    require(value["branch"] == refresh_branch(value["batch"]), "wrong-refresh-branch")
    require(value["head"] != value["parent"] and value["before-lock"] != value["lock"], "unchanged-refresh-candidate")
    require(value["source"] == value["parent"], "wrong-refresh-source")
    require(value["previous"] != "-" or value["parent"] == value["base"], "wrong-initial-refresh-parent")
    return value


def refresh_operation_id(kind, payload):
    require(kind in {"refresh-branch", "refresh-pr"}, "wrong-refresh-kind")
    refresh_candidate({k: payload[k] for k in REFRESH_FIELDS})
    return digest(canonical({"kind": kind, "payload": payload}))


def refresh_context(transcript, candidate, *, checks=False, current=False, current_dev=None):
    supplied = transcript.get("refresh")
    require(isinstance(supplied, dict) and set(supplied) == {"revisions", "current"}
            and isinstance(supplied["revisions"], list), "invalid-refresh-transcript")
    if current:
        context = supplied["current"]
    else:
        matches = [c for c in supplied["revisions"] if isinstance(c, dict) and c.get("prepared") == candidate]
        require(len(matches) == 1, "ambiguous-refresh-provenance")
        context = matches[0]
    require(isinstance(context, dict) and set(context) == {"prepared", "proof", "current-dev", "branch", "checks", "integration", "construction"}, "missing-refresh-context")
    refresh_construction(context, candidate)
    require(context["prepared"] == candidate and context["current-dev"] == (current_dev or candidate["base"]), "stale-refresh-source-or-base")
    proof = context["proof"]
    require(isinstance(proof, dict) and set(proof) == {"head-parents", "merge-parents", "changed", "before-lock", "lock", "before-mode", "mode"}, "missing-refresh-preparation-proof")
    require(proof["head-parents"] == [candidate["parent"]] and proof["changed"] == ["unixlike/flake.lock"]
            and proof["before-lock"] == candidate["before-lock"] and proof["lock"] == candidate["lock"]
            and type(proof["mode"]) is int and type(proof["before-mode"]) is int
            and proof["mode"] == proof["before-mode"] and 0 <= proof["mode"] <= 0o777, "contaminated-refresh-preparation")
    expected_merge = [] if candidate["previous"] == "-" else [candidate["previous"], candidate["base"]]
    require(proof["merge-parents"] == expected_merge, "wrong-refresh-update-parents")
    observed_branch = context["branch"]
    require(isinstance(observed_branch, dict) and set(observed_branch) == {"batch", "branch", "head"}
            and observed_branch["batch"] == candidate["batch"] and observed_branch["branch"] == candidate["branch"], "wrong-refresh-branch-owner")
    require(observed_branch["head"] in {candidate["previous"], candidate["head"]}, "stale-refresh-branch-head")
    expected = {"head": candidate["head"], "base": candidate["base"], "tree": candidate["tree"],
                "lock": candidate["lock"], "name": "Required checks", "app": "15368"}
    supplied_checks = context["checks"]
    if supplied_checks is not None:
        require(isinstance(supplied_checks, dict) and set(supplied_checks) == set(expected) | {"status"}
                and all(supplied_checks[k] == v for k, v in expected.items())
                and supplied_checks["status"] in {"success", "failure", "pending", "unknown"}, "invalid-current-refresh-checks")
    if checks:
        require(supplied_checks is not None and supplied_checks["status"] == "success", "missing-current-refresh-checks")
    return context


def tag_identity(payload):
    """Canonical synthetic annotation object; actual API byte behavior needs rollout proof."""
    date = datetime.strptime(payload["tagger-time"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    require(not any(c in payload["tagger-name"] + payload["tagger-email"] for c in "<>\n\r\t"), "invalid-tagger-identity")
    raw = ("object " + payload["source"] + "\ntype commit\ntag " + payload["tag"]
           + "\ntagger " + payload["tagger-name"] + " <" + payload["tagger-email"]
           + "> " + str(int(date.timestamp())) + " +0000\n\n" + payload["annotation"]).encode("utf-8")
    return hashlib.sha1(b"tag " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def operation(kind, payload):
    require(kind in PAYLOADS and isinstance(payload, dict) and set(payload) == PAYLOADS[kind], "invalid-operation-payload")
    require(all(isinstance(v, str) and v and not any(c in v for c in ("\r\t\0" if k == "annotation" else "\r\n\t\0")) for k, v in payload.items()), "invalid-payload-value")
    require(payload["repository"] == "shk95/configs" or kind == "record", "wrong-target-repository")
    require(re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", payload["repository"]) is not None, "invalid-target-connection")
    if kind == 'refresh-object':
        for key in ('batch','refresh','construction'): identity(payload[key])
        raw=raw_object({'type':payload['object-type'],'sha':payload['object'],'raw':payload['raw']})
        deps=document(payload['dependencies'].encode())
        require(isinstance(deps,list) and len(deps)<=4096 and canonical(deps).decode()==payload['dependencies'], 'invalid-object-dependencies')
        for dep in deps:
            require(isinstance(dep,dict) and set(dep)=={'type','sha','operation'} and dep['type'] in {'blob','tree','commit'}, 'invalid-object-dependency')
            identity(dep['sha'],40)
            require(dep['operation']=='-' or identity(dep['operation']), 'invalid-dependency-operation')
        if payload['object-type']=='blob': body={'content':payload['raw'],'encoding':'base64'}; suffix='blobs'
        elif payload['object-type']=='tree':
            body={'tree':[{'path':name.decode('utf-8'),'mode':mode.decode().zfill(6),'type':'tree' if mode==b'40000' else 'commit' if mode==b'160000' else 'blob','sha':sha} for mode,name,sha in tree_entries(raw)]}; suffix='trees'
        else:
            rows,tree,parents,message=commit_headers(raw)
            require(len(parents)==1, 'invalid-object-commit')
            generated_commit(raw,tree,parents[0])
            epoch=int(rows[2][1].rsplit(b' ',2)[1])
            try: date=datetime.fromtimestamp(epoch,timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            except (OverflowError,ValueError,OSError): raise Refusal('unsupported-generated-date') from None
            actor={'name':'Release controller','email':'release-controller@example.invalid','date':date}
            body={'tree':tree,'parents':parents,'message':message.decode('utf-8'),'author':actor,'committer':dict(actor)}; suffix='commits'
        return {'api-version':API_VERSION,'method':'POST','path':'/repos/shk95/configs/git/'+suffix,'body':body,'payload-digest':digest(canonical(payload))}
    if kind in {"refresh-branch", "refresh-pr"}:
        refresh_candidate({k: payload[k] for k in REFRESH_FIELDS})
        prefix = "/repos/" + payload["repository"]
        if kind == "refresh-branch":
            creating = payload["previous"] == "-"
            method = "POST" if creating else "PATCH"
            path = prefix + ("/git/refs" if creating else "/git/refs/heads/" + payload["branch"])
            body = {"ref": "refs/heads/" + payload["branch"], "sha": payload["head"]} if creating else {"sha": payload["head"], "force": False}
        else:
            method, path = "POST", prefix + "/pulls"
            body = {"head": payload["branch"], "base": "dev", "title": "Refresh Unix-like dependencies",
                    "body": "refresh-operation=" + refresh_operation_id(kind, payload)}
        return {"api-version": API_VERSION, "method": method, "path": path, "body": body,
                "payload-digest": digest(canonical(payload))}
    for key in {"parent", "commit", "dev", "master", "tree", "source", "object"} & set(payload):
        identity(payload[key], 40)
    for key in {"event", "index", "body-operation"} & set(payload):
        identity(payload[key])
    if kind == "pr":
        require(payload["head"] == "dev" and payload["base"] == "master", "wrong-promotion-source")
    if kind.startswith("tag"):
        require(re.fullmatch(r"(unixlike|windows|common)-v[1-9][0-9]*\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", payload["tag"]) is not None, "invalid-tag-name")
    for key in {"number", "run", "attempt", "workflow", "initial-run"} & set(payload):
        require(re.fullmatch(r"[1-9][0-9]*", payload[key]) is not None, "invalid-endpoint-id")
    if kind == "tag-object":
        require(re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", payload["tagger-time"]) is not None, "noncanonical-tagger-time")
        try:
            datetime.strptime(payload["tagger-time"], "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            raise Refusal("invalid-tagger-time") from None
        require(payload["object"] == tag_identity(payload), "tag-object-byte-identity-mismatch")
    prefix = "/repos/" + payload["repository"]
    method, path, body = {
        "record": ("PATCH", prefix + "/git/refs/heads/operations", {"sha": payload.get("commit"), "force": False}),
        "pr": ("POST", prefix + "/pulls", {"head": "dev", "base": "master", "body": payload.get("body-operation")}),
        "merge": ("PUT", prefix + "/pulls/" + payload.get("number", "-") + "/merge", {"sha": payload.get("dev"), "merge_method": "merge"}),
        "tag-object": ("POST", prefix + "/git/tags", {"tag": payload.get("tag"), "message": payload.get("annotation"), "object": payload.get("source"), "type": "commit", "tagger": {"name": payload.get("tagger-name"), "email": payload.get("tagger-email"), "date": payload.get("tagger-time")}}),
        "tag-ref": ("POST", prefix + "/git/refs", {"ref": "refs/tags/" + payload.get("tag", "-"), "sha": payload.get("object")}),
        "cancel": ("POST", prefix + "/actions/runs/" + payload.get("run", "-") + "/cancel", {}),
    }[kind]
    return {"api-version": API_VERSION, "method": method, "path": path,
            "body": body, "payload-digest": digest(canonical(payload))}


def reconcile(kind, payload, observation):
    """Unknown responses are decided by target observation, never acknowledgement."""
    operation(kind, payload)
    require(isinstance(observation, dict) and set(observation) == {"status", "target", "complete"}, "invalid-observation-schema")
    require(type(observation["complete"]) is bool and observation["complete"], "incomplete-observation")
    status, target = observation["status"], observation["target"]
    require(status in {"present", "absent", "unknown"}, "invalid-observation-status")
    require(isinstance(target, dict), "invalid-observation-target")
    if status == "unknown":
        return "unknown"
    if status == "absent":
        expected = ({'object-type':payload['object-type'],'object':payload['object']} if kind=='refresh-object' else {"parent": payload["parent"]} if kind == "record" else
                    {"batch": payload["batch"], "branch": payload["branch"], "head": payload["previous"]}
                    if kind == "refresh-branch" else {})
        require(target == expected, "unconfirmed-absence")
        return "absent"
    if kind=='refresh-object':
        expected={'object-type':payload['object-type'],'object':payload['object'],
                  'raw-digest':digest(raw_object({'type':payload['object-type'],'sha':payload['object'],'raw':payload['raw']})),
                  'dependencies':document(payload['dependencies'].encode()),'construction':payload['construction']}
        require(set(target)==set(expected), 'invalid-object-observation')
        return 'applied' if target==expected else 'conflict'
    if kind in {"refresh-branch", "refresh-pr"}:
        candidate = {k: payload[k] for k in REFRESH_FIELDS}
        if kind == "refresh-branch":
            require(set(target) == {"candidate"}, "invalid-refresh-branch-observation")
            return "applied" if target["candidate"] == candidate else "conflict"
        require(set(target) == {"matches"} and isinstance(target["matches"], list), "invalid-refresh-pr-observation")
        if len(target["matches"]) != 1:
            return "conflict"
        match = target["matches"][0]
        require(isinstance(match, dict) and set(match) == {"number", "repository", "base-ref", "state", "candidate", "checks"}, "invalid-refresh-pr-match")
        require(isinstance(match["number"], str) and re.fullmatch(r"[1-9][0-9]*", match["number"]), "missing-refresh-pr-number")
        expected_checks = {"head": payload["head"], "base": payload["base"], "tree": payload["tree"], "lock": payload["lock"], "name": "Required checks", "app": "15368", "status": "success"}
        return "applied" if (match["repository"] == payload["repository"] and match["base-ref"] == "dev"
                             and match["state"] in {"open", "merged"} and match["candidate"] == candidate
                             and match["checks"] == expected_checks) else "conflict"
    if kind == "record":
        require(set(target) == {"history", "head"} and isinstance(target["history"], list), "incomplete-record-history")
        identity(target["head"], 40)
        commits, events, matches, previous = set(), set(), [], None
        for item in target["history"]:
            require(isinstance(item, dict) and set(item) == {"parent", "commit", "event", "index"}, "invalid-history-observation")
            identity(item["parent"], 40); identity(item["commit"], 40)
            identity(item["event"]); identity(item["index"])
            require(item["commit"] not in commits and item["event"] not in events
                    and (previous is None or item["parent"] == previous), "contradictory-record-history")
            commits.add(item["commit"]); events.add(item["event"]); previous = item["commit"]
            if item["event"] == payload["event"]:
                matches.append(item)
        require(previous == target["head"], "incomplete-record-head-history")
        return "applied" if matches == [{k: payload[k] for k in ("parent", "commit", "event", "index")}] else "conflict"
    if kind == "pr":
        require(set(target) == {"matches"} and isinstance(target["matches"], list), "invalid-pr-observation")
        if len(target["matches"]) != 1:
            return "conflict"
        match = target["matches"][0]
        require(isinstance(match, dict) and set(match) == {"number", "payload"}
                and isinstance(match["number"], str) and re.fullmatch(r"[1-9][0-9]*", match["number"]), "missing-pr-identity")
        return "applied" if match["payload"] == payload else "conflict"
    if kind == "merge":
        require(set(target) == {"merged", "commit", "parents", "tree", "source"}, "invalid-merge-observation")
        require(type(target["merged"]) is bool, "invalid-merged-status")
        identity(target["commit"], 40)
        return "applied" if target == {"merged": True, "commit": target["commit"], "parents": [payload["master"], payload["dev"]], "tree": payload["tree"], "source": payload["dev"]} else "conflict"
    if kind == "cancel":
        require(set(target) == {"run", "attempt", "workflow", "jobs", "latest-attempt", "terminal"}, "invalid-cancel-observation")
        return "applied" if target == {"run": payload["run"], "attempt": payload["attempt"], "workflow": payload["workflow"], "jobs": payload["jobs"], "latest-attempt": payload["attempt"], "terminal": True} else "unknown"
    return "applied" if target == payload else "conflict"


def remote_identity(kind, payload, observation):
    if kind == 'refresh-object': return payload['object']
    require(observation["status"] == "present", "missing-remote-identity")
    target = observation["target"]
    if kind == "refresh-branch":
        return payload["head"]
    if kind == "refresh-pr":
        return target["matches"][0]["number"]
    if kind == "record":
        return payload["commit"]
    if kind == "merge":
        return target["commit"]
    if kind == "pr":
        return target["matches"][0]["number"]
    if kind == "cancel":
        return target["run"]
    return target["object"]


def authenticate(transcript, config, request, candidate_digest):
    require(set(transcript) in ({"source", "checks", "owner", "observations", "protection"},
                              {"source", "checks", "owner", "observations", "protection", "refresh"}), "unknown-transcript-field")
    sources = transcript["source"]
    expected = {"repository": config["repository"], "workflow": config["workflow"],
                "actor": request["actor"], "run": request["run"], "attempt": request["attempt"],
                "ref": "refs/heads/master", "event": "workflow_dispatch",
                "mode": request["mode"], "candidate": candidate_digest}
    require(isinstance(sources, list) and all(isinstance(s, dict) and set(s) == set(expected) for s in sources), "invalid-source-observations")
    require(sum(s == expected for s in sources) == 1 and request["ref"] == "refs/heads/master", "unauthenticated-request")
    require(request["actor"] in config["actors"].split(","), "unauthorized-actor")
    require(request["candidate"] == candidate_digest, "stale-request-candidate")
    protection = transcript["protection"]
    expected_protection = {"required": "Required checks", "app": "15368", "administrators": True,
                           "conversations": True, "force": False, "deletion": False,
                           "dev-strict": True, "master-strict": False}
    require(isinstance(protection, dict) and protection == expected_protection
            and all(type(protection[k]) is type(v) for k, v in expected_protection.items()), "missing-or-mismatched-protection")


def takeover(owner, observed):
    require(isinstance(observed, dict) and set(observed) == {"owner", "latest-attempt", "jobs", "complete", "status"}, "incomplete-owner-observation")
    require(observed["owner"] == owner and observed["latest-attempt"] == owner["attempt"], "changed-owner-attempt")
    require(observed["complete"] is True and observed["status"] == "terminal", "unconfirmed-termination")
    require(observed["jobs"] == {owner["job"]: "terminal"}, "unconfirmed-writer-jobs")
    return True


def opportunity(hour, refresh):
    require(type(hour) is int and 0 <= hour <= 23, "invalid-opportunity-hour")
    require(refresh in {"ready", "waiting", "failed", "absent"}, "invalid-refresh-state")
    if hour < 6:
        return "not-due"
    if refresh == "waiting" and hour < 7:
        return "wait"
    # Cutoff never means canceling the refresh. It changes opportunity selection.
    return "reconcile"


def refresh_window(day, hour, seen, *, manual=False, refresh="absent", promoted=False):
    """Supplied synthetic calendar observation; never reads a clock or schedules."""
    require(isinstance(day, str) and re.fullmatch(r"\d{4}-\d\d-\d\d", day), "invalid-refresh-day")
    try:
        datetime.strptime(day, "%Y-%m-%d")
    except ValueError:
        raise Refusal("invalid-refresh-day") from None
    require(isinstance(seen, list) and all(isinstance(d, str) for d in seen)
            and len(set(seen)) == len(seen), "invalid-refresh-days")
    require(type(manual) is bool and type(promoted) is bool, "invalid-opportunity-flag")
    selection = opportunity(hour, refresh)
    action = "join" if day in seen else "start" if manual or hour == 5 else "missed" if hour > 5 else "not-due"
    return {"refresh": action, "promotion": selection,
            "integration": "next-opportunity" if promoted else "invalidate"}
