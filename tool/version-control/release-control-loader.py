"""Small fixed loader. Approval file is an assertion in this preview-only lane."""
# INV repository/release-control-preview-only
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = "tool/version-control/release-control-package"
FILES = {ROOT + "/" + name for name in ("main.py", "records.py", "engine.py", "adapter.py")}
FILES |= {"tool/version-control/" + name for name in
          ("release-preview", "release-preview.awk", "release-preview.rules", "classify")}
MANIFEST = ROOT + "/manifest.tsv"


def runtime_environment(source):
    # Read only runtime keys: never forward ambient credentials to retained code.
    names = {"PATH", "SYSTEMROOT", "SystemRoot", "WINDIR", "COMSPEC", "ComSpec",
             "PATHEXT", "TEMP", "TMP", "TMPDIR", "LANG", "LC_ALL", "TZ"}
    return {key: source[key] for key in names if key in source}


def git(repo, *args, data=None):
    env = runtime_environment(os.environ)
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
               GIT_NO_REPLACE_OBJECTS="1", GIT_NO_LAZY_FETCH="1",
               GIT_ALLOW_PROTOCOL="", GIT_TERMINAL_PROMPT="0")
    result = subprocess.run(["git", "--no-replace-objects", "-C", str(repo), *args],
                            input=data, env=env, capture_output=True, timeout=30)
    if result.returncode:
        raise ValueError("unavailable-public-object")
    return result.stdout


def approved(data):
    # Independent bounded parser: never import an unverified current engine.
    try:
        text = data.decode("utf-8", "strict")
    except UnicodeError:
        raise ValueError("invalid-approval-assertion") from None
    if not text.endswith("\n") or any(c not in "\n\t" and (ord(c) < 32 or ord(c) == 127) for c in text):
        raise ValueError("invalid-approval-assertion")
    lines = [line.split("\t") for line in text[:-1].split("\n")]
    if not lines or lines[0] != ["format", "1"] or any(len(row) != 2 for row in lines):
        raise ValueError("invalid-approval-assertion")
    result = dict(lines[1:])
    if len(result) != len(lines) - 1 or set(result) != {"public-repository", "master", "control", "manifest", "approval", "protocol"}:
        raise ValueError("invalid-approval-assertion")
    if result["public-repository"] != "shk95/configs" or result["protocol"] not in {"1", "2", "3"}:
        raise ValueError("unsupported-approval-protocol")
    for key, size in (("master", 40), ("control", 40), ("manifest", 64), ("approval", 64)):
        if not re.fullmatch(r"[0-9a-f]{%d}" % size, result[key]) or result[key] == "0" * size:
            raise ValueError("invalid-approved-identity")
    return result


def extract(repo, assertion, target):
    control = assertion["control"]
    # Full identities and absence of replacement objects; no arbitrary URL/ref/path.
    if git(repo, "rev-parse", "--show-object-format").strip() != b"sha1":
        raise ValueError("unsupported-object-format")
    if git(repo, "rev-parse", "--is-shallow-repository").strip() != b"false":
        raise ValueError("incomplete-public-history")
    git(repo, "merge-base", "--is-ancestor", control, assertion["master"])
    commit = git(repo, "cat-file", "-p", control)
    if sum(line.startswith(b"parent ") for line in commit.split(b"\n\n", 1)[0].splitlines()) != 2:
        raise ValueError("unapproved-master-provenance")
    metadata = git(repo, "ls-tree", control, "--", MANIFEST).decode("ascii").strip().split()
    if len(metadata) != 4 or metadata[0:2] != ["100644", "blob"] or metadata[3] != MANIFEST:
        raise ValueError("unsafe-manifest-object")
    manifest = git(repo, "show", control + ":" + MANIFEST)
    if hashlib.sha256(manifest).hexdigest() != assertion["manifest"]:
        raise ValueError("manifest-identity-mismatch")
    try:
        lines = manifest.decode("ascii").splitlines()
        if not manifest.endswith(b"\n") or not lines or lines.pop(0) != "format\t1":
            raise ValueError("invalid-manifest")
        tuples = [line.split("\t") for line in lines]
        if any(len(row) != 3 or row[0] != "file" for row in tuples):
            raise ValueError("invalid-manifest")
        names = [row[1] for row in tuples]
        if names != sorted(FILES):
            raise ValueError("incomplete-package-closure")
        for _, name, expected in tuples:
            if not re.fullmatch(r"[0-9a-f]{64}", expected):
                raise ValueError("invalid-file-digest")
            metadata = git(repo, "ls-tree", control, "--", name).decode("ascii").strip().split()
            if len(metadata) != 4 or metadata[0] not in {"100644", "100755"} or metadata[1] != "blob":
                raise ValueError("unsafe-package-object")
            data = git(repo, "show", control + ":" + name)
            if hashlib.sha256(data).hexdigest() != expected:
                raise ValueError("package-digest-mismatch")
            path = target / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            if metadata[0] == "100755":
                path.chmod(0o755)
    except UnicodeError:
        raise ValueError("invalid-manifest") from None


CONTEXT_FIELDS = ("start", "batch", "master", "control", "manifest", "approval", "protocol",
                  "config-commit", "config", "transcript-commit", "transcript")
PROJECTION_FIELDS = {"sequence", "prior", "batch", "generation", "stage", "state-digest"}
STAGES = {"empty", "active", "candidate", "validated", "approved", "promoted", "publishing", "waiting", "blocked", "complete"}


def table(data):
    value = data.decode("utf-8", "strict")
    if (not value.endswith("\n") or any(c not in "\n\t" and
            (ord(c) < 32 or ord(c) == 127 or 128 <= ord(c) <= 159) for c in value)):
        raise ValueError("invalid-global-record")
    rows = [line.split("\t") for line in value[:-1].split("\n")]
    if not rows or rows[0] != ["format", "1"] or any(not all(row) for row in rows):
        raise ValueError("invalid-global-record")
    return rows[1:]


def singletons(data, expected):
    rows = table(data)
    if any(len(row) != 2 for row in rows):
        raise ValueError("invalid-global-singletons")
    result = dict(rows)
    if len(result) != len(rows) or set(result) != expected:
        raise ValueError("invalid-global-singletons")
    return result


def identity(value, width=40):
    if not re.fullmatch(r"[0-9a-f]{%d}" % width, value):
        raise ValueError("invalid-global-identity")
    return value


def record_blob(repo, commit, path):
    identity(commit)
    row = git(repo, "ls-tree", commit, "--", path).decode("utf-8").strip().split()
    if len(row) != 4 or row[0:2] != ["100644", "blob"] or row[3] != path:
        raise ValueError("missing-or-unsafe-operating-object")
    return row[2], git(repo, "cat-file", "blob", row[2])


def encode_index(fields):
    return ("format\t1\n" + "".join(key + "\t" + fields[key] + "\n" for key in sorted(fields))).encode()


# Current glue selects a finite verified callable interface, not current semantics.
REPLAY_DRIVER = r"""
import base64,json,sys
from pathlib import Path
sys.path.insert(0,sys.argv[1])
import records,engine
root=Path(sys.argv[2]); protocol=sys.argv[3]; before=int(sys.argv[4]); prior=sys.argv[5]
assert protocol in {'1','2','3'}
config=records.parse(records.read(root/'config/operating.tsv'),'config')
approved=records.parse(records.read(root/'approved.tsv'),'approved')
from adapter import document
transcript=document(records.read(root/'transcript.json'))
assert config['protocol']==protocol and approved['protocol']==protocol
assert config['enabled']!='1' or (config['actors']!='-' and config['checks']!='-')
if protocol=='3':
 import main
 result=main.replay(root,transcript,approved,before,prior)
else:
 assert before==0 and prior=='0'*64
 events,last=records.history(root/'history')
 assert not events or config['enabled']=='1'
 if events:
  start=events[0]
  assert start['kind']=='batch-start' and start['control']==approved['control'] and start['manifest']==approved['manifest'] and start['approval-provenance']==approved['approval'] and start['config']==records.blob_identity(records.read(root/'config/operating.tsv'))
 state=engine.reduce(events,config,transcript)
 result={'projection':base64.b64encode(engine.index(state,last)).decode('ascii'),'stage':state['stage'],'proposed':sum(o['state']=='intent' for o in state['operations'].values())}
print(json.dumps(result,sort_keys=True))
"""


def replay_package(package, batch, protocol, before, prior):
    if protocol in {"1", "2"} and (before != 0 or prior != "0" * 64):
        raise ValueError("unsupported-retained-offset")
    process = subprocess.run([sys.executable, "-I", "-S", "-B", "-c", REPLAY_DRIVER,
                              str(package / ROOT), str(batch), protocol, str(before), prior],
                             capture_output=True, timeout=15 * 60, env=runtime_environment(os.environ))
    if process.returncode or len(process.stdout) > 4096:
        raise ValueError("retained-replay-refusal")
    result = json.loads(process.stdout)
    if (not isinstance(result, dict) or set(result) != {"projection", "stage", "proposed"}
            or result["stage"] not in STAGES or type(result["proposed"]) is not int or result["proposed"] < 0):
        raise ValueError("invalid-retained-projection")
    projection = base64.b64decode(result["projection"], validate=True)
    fields = singletons(projection, PROJECTION_FIELDS)
    if fields["stage"] != result["stage"]:
        raise ValueError("inconsistent-retained-stage")
    identity(fields["prior"], 64); identity(fields["batch"], 64); identity(fields["state-digest"], 64)
    if any(not re.fullmatch(r"0|[1-9][0-9]*", fields[key]) for key in ("sequence", "generation")):
        raise ValueError("invalid-retained-count")
    return projection, fields, result


def global_preview(paths, assertion, head, scratch):
    repo = paths["operating"]
    identity(head)
    for source in (repo, paths["bundle_repository"]):
        if git(source, "for-each-ref", "--format=%(refname)", "refs/replace").strip():
            raise ValueError("replaced-history-refused")
    request = singletons(paths["request"].read_bytes(), {"mode", "actor", "run", "attempt", "ref", "candidate"})
    identity(request["candidate"], 64)
    if request["mode"] != "preview" or any(not re.fullmatch(r"0|[1-9][0-9]*", request[k]) for k in ("actor", "run", "attempt")):
        raise ValueError("invalid-global-request")
    if git(repo, "rev-parse", "--show-object-format").strip() != b"sha1" or git(repo, "rev-parse", "--is-shallow-repository").strip() != b"false":
        raise ValueError("incomplete-operating-history")
    git(repo, "cat-file", "commit", head)
    _, current_config = record_blob(repo, head, "config/operating.tsv")
    _, stop = record_blob(repo, head, "control/stop.tsv")
    stop_fields = singletons(stop, {"stop", "revision", "reason", "operator"})
    if stop_fields["stop"] not in {"0", "1"} or any(not re.fullmatch(r"0|[1-9][0-9]*", stop_fields[k]) for k in ("revision", "operator")):
        raise ValueError("invalid-fresh-stop")
    _, actual_index = record_blob(repo, head, "current/index.tsv")
    _, raw_contexts = record_blob(repo, head, "current/batches.tsv")
    contexts = []
    for row in table(raw_contexts):
        if len(row) != 12 or row[0] != "context":
            raise ValueError("invalid-batch-context")
        c = dict(zip(CONTEXT_FIELDS, row[1:]))
        if not re.fullmatch(r"[1-9][0-9]*", c["start"]) or int(c["start"]) >= 10 ** 12:
            raise ValueError("invalid-context-sequence")
        for key in ("master", "control", "config-commit", "config"):
            identity(c[key])
        for key in ("batch", "manifest", "approval"):
            identity(c[key], 64)
        if c["protocol"] not in {"1", "2", "3"}:
            raise ValueError("unsupported-context-protocol")
        if (c["transcript-commit"] == "-") != (c["transcript"] == "-"):
            raise ValueError("partial-transcript-context")
        if c["transcript"] != "-":
            identity(c["transcript-commit"]); identity(c["transcript"])
        contexts.append(c)
    starts = [int(c["start"]) for c in contexts]
    if starts != sorted(set(starts)) or len({c["batch"] for c in contexts}) != len(contexts):
        raise ValueError("duplicate-or-unordered-context")
    names = git(repo, "ls-tree", "-r", "--name-only", "-z", head, "--", "history/").split(b"\0")
    names = sorted(name.decode("utf-8") for name in names if name)
    envelopes, active, prior, before = [], [], "0" * 64, 0
    for number, name in enumerate(names, 1):
        if number >= 10 ** 12 or name != "history/%012d.tsv" % number:
            raise ValueError("history-gap-or-path")
        _, data = record_blob(repo, head, name)
        rows = table(data)
        framing = {}
        for row in rows:
            if row[0] in {"sequence", "kind", "prior", "batch", "control", "manifest", "approval-provenance", "config", "protocol", "approved-master", "config-commit"}:
                if len(row) != 2 or row[0] in framing:
                    raise ValueError("ambiguous-event-framing")
                framing[row[0]] = row[1]
        if framing.get("sequence") != str(number) or framing.get("prior") != prior:
            raise ValueError("original-event-chain-mismatch")
        identity(framing.get("batch", ""), 64)
        if not active:
            if framing.get("kind") != "batch-start":
                raise ValueError("event-outside-envelope")
            before = number - 1
        elif framing.get("kind") == "batch-start" or framing["batch"] != active[0][2]["batch"]:
            raise ValueError("overlapping-batches")
        active.append((name, data, framing))
        prior = hashlib.sha256(data).hexdigest()
        if framing.get("kind") == "complete":
            envelopes.append((before, active, True)); active = []
    if active:
        envelopes.append((before, active, False))
    if len(envelopes) != len(contexts):
        raise ValueError("missing-or-surplus-context")
    ledger, final_fields, last_result, selected = [], None, None, None
    for ordinal, ((before, events, completed), context) in enumerate(zip(envelopes, contexts)):
        first = events[0][2]
        if context["start"] != str(before + 1) or any(first.get(k) != context[v] for k, v in
                (("batch", "batch"), ("control", "control"), ("manifest", "manifest"),
                 ("approval-provenance", "approval"), ("config", "config"), ("protocol", "protocol"))):
            raise ValueError("retained-context-binding-mismatch")
        if context["protocol"] == "3" and (first.get("approved-master") != context["master"] or first.get("config-commit") != context["config-commit"]):
            raise ValueError("missing-protocol-three-bindings")
        git(repo, "merge-base", "--is-ancestor", context["config-commit"], head)
        cfg_blob, config = record_blob(repo, context["config-commit"], "config/operating.tsv")
        if cfg_blob != context["config"]:
            raise ValueError("changed-retained-config")
        if completed:
            if context["transcript"] == "-":
                raise ValueError("missing-completed-replay-input")
            git(repo, "merge-base", "--is-ancestor", context["transcript-commit"], head)
            tid, transcript = record_blob(repo, context["transcript-commit"], "current/transcript.json")
            if tid != context["transcript"]:
                raise ValueError("changed-retained-transcript")
        else:
            if context["transcript"] != "-" or ordinal != len(envelopes) - 1:
                raise ValueError("invalid-outstanding-context")
            transcript = paths["transcript"].read_bytes()
        approval = {k: context[k] for k in ("master", "control", "manifest", "approval", "protocol")}
        approval["public-repository"] = "shk95/configs"
        approval = approved(encode_index(approval))
        package = scratch / ("package-%d" % ordinal)
        extract(paths["bundle_repository"], approval, package)
        batch = scratch / ("batch-%d" % ordinal)
        for folder in ("config", "control", "current", "history"):
            (batch / folder).mkdir(parents=True, exist_ok=True)
        (batch / "config/operating.tsv").write_bytes(config)
        (batch / "control/stop.tsv").write_bytes(stop)
        (batch / "approved.tsv").write_bytes(encode_index(approval))
        (batch / "transcript.json").write_bytes(transcript)
        for name, data, framing in events:
            (batch / "history" / name.split("/")[1]).write_bytes(data)
        boundary_prior = events[0][2]["prior"]
        projection, fields, result = replay_package(package, batch, context["protocol"], before, boundary_prior)
        if fields["sequence"] != str(before + len(events)) or fields["prior"] != hashlib.sha256(events[-1][1]).hexdigest() or fields["batch"] != context["batch"]:
            raise ValueError("wrong-global-semantic-projection")
        if completed and (result["stage"] != "complete" or result["proposed"] != 0):
            raise ValueError("structural-completion-not-semantic")
        ledger.append({"context": context, "projection": hashlib.sha256(projection).hexdigest()})
        final_fields, last_result = fields, result
        if not completed:
            (batch / "current/index.tsv").write_bytes(projection)
            selected = (package, batch, approval, before, boundary_prior)
    current_package = None
    if selected is None:
        current_package = scratch / "current-package"
        extract(paths["bundle_repository"], assertion, current_package)
        empty = scratch / "empty"
        for folder in ("config", "history"):
            (empty / folder).mkdir(parents=True, exist_ok=True)
        (empty / "config/operating.tsv").write_bytes(current_config)
        (empty / "approved.tsv").write_bytes(encode_index(assertion))
        (empty / "transcript.json").write_bytes(paths["transcript"].read_bytes())
        projection, empty_fields, empty_result = replay_package(current_package, empty, assertion["protocol"], 0, "0" * 64)
        if final_fields is None:
            final_fields, last_result = empty_fields, empty_result
    expected = dict(final_fields, **{"index-kind": "global-1", "ledger-digest": hashlib.sha256(json.dumps(ledger, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()})
    if actual_index != encode_index(expected):
        raise ValueError("global-index-mismatch")
    if stop_fields["stop"] == "1":
        return {"outcome": "stopped", "proposed": 0}
    if selected is None:
        if singletons(current_config, {"enabled", "public-repository", "repository", "operating-repository", "operating-ref", "workflow", "actors", "checks", "protocol"})["enabled"] == "0":
            return None
        return {"outcome": "preview", "stage": last_result["stage"], "proposed": 0}
    package, batch, approval, before, boundary_prior = selected
    (batch / "request.tsv").write_bytes(paths["request"].read_bytes())
    arguments = [str(batch), str(batch / "transcript.json"), str(batch / "request.tsv"), str(batch / "approved.tsv")]
    if approval["protocol"] == "3":
        arguments = ["--preview-range"] + arguments + [str(before), boundary_prior]
    result = subprocess.run([sys.executable, "-I", "-S", "-B", str(package / ROOT / "main.py")] + arguments,
                            timeout=15 * 60, capture_output=True, env=runtime_environment(os.environ))
    if result.returncode or len(result.stdout) > 512:
        raise ValueError("selected-retained-preview-refusal")
    return json.loads(result.stdout) if result.stdout else None


def validate_summary(summary):
    if not isinstance(summary, dict):
        raise ValueError("unsafe-package-output")
    permitted = ({"outcome", "proposed"} if summary.get("outcome") == "stopped"
                 else {"outcome", "stage", "proposed"})
    if (set(summary) != permitted or summary.get("outcome") not in {"preview", "stopped"}
            or type(summary.get("proposed")) is not int or summary["proposed"] < 0
            or ("stage" in summary and summary["stage"] not in STAGES)):
        raise ValueError("unsafe-package-output")


def main():
    class Parser(argparse.ArgumentParser):
        def error(self, message):
            self.exit(64, "release-control: invalid arguments\n")
    parser = Parser(description="Inert release control with explicit synthetic trust/transcript inputs")
    parser.add_argument("mode", choices=["preview"])
    parser.add_argument("--fixture-inputs", action="store_true", required=True)
    parser.add_argument("--bundle-repository", required=True)
    parser.add_argument("--approved", required=True)
    parser.add_argument("--operating", required=True)
    parser.add_argument("--transcript", required=True)
    parser.add_argument("--request", required=True)
    parser.add_argument("--global-history", action="store_true")
    parser.add_argument("--operating-head")
    args = parser.parse_args()
    try:
        paths = {k: Path(getattr(args, k)).resolve(strict=True) for k in
                 ("bundle_repository", "approved", "operating", "transcript", "request")}
        for key in ("approved", "transcript", "request"):
            if Path(getattr(args, key)).is_symlink() or not paths[key].is_file():
                raise ValueError("unsafe-input-path")
        if args.global_history != (args.operating_head is not None):
            raise ValueError("missing-global-snapshot-head")
        if Path(args.operating).is_symlink():
            raise ValueError("unsafe-operating-root")
        assertion = approved(paths["approved"].read_bytes())
        with tempfile.TemporaryDirectory(prefix="release-control-") as directory:
            scratch = Path(directory)
            if args.global_history:
                summary = global_preview(paths, assertion, args.operating_head, scratch)
                if summary is not None:
                    validate_summary(summary)
                    print(json.dumps(summary, sort_keys=True))
                return 0
            extract(paths["bundle_repository"], assertion, scratch)
            # Only verified retained package imports its verified adjacent modules.
            result = subprocess.run([sys.executable, "-I", "-S", "-B", str(scratch / ROOT / "main.py"),
                                     str(paths["operating"]), str(paths["transcript"]),
                                     str(paths["request"]), str(paths["approved"])],
                                    timeout=15 * 60, capture_output=True,
                                    env=runtime_environment(os.environ))
            # Package output is bounded public summary; never echo subprocess stderr.
            if result.returncode:
                raise ValueError("retained-package-refusal")
            if result.stdout:
                if len(result.stdout) > 512:
                    raise ValueError("unsafe-package-output")
                summary = json.loads(result.stdout)
                if not isinstance(summary, dict):
                    raise ValueError("unsafe-package-output")
                validate_summary(summary)
                print(json.dumps(summary, sort_keys=True))
    except (ValueError, OSError, subprocess.SubprocessError, KeyError, TypeError):
        # Never print raw private paths, records, digests, or exception payloads.
        print("release-control: refused", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
