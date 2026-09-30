"""Bounded original-byte records. No record text is executable."""
# INV repository/release-control-preview-only
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path


class Refusal(ValueError):
    pass


def require(ok, reason):
    if not ok:
        raise Refusal(reason)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def blob_identity(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def identity(value, size=64):
    require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{%d}" % size, value) is not None, "invalid-identity")
    return value


def decimal(value):
    require(re.fullmatch(r"0|[1-9][0-9]*", value) is not None, "invalid-decimal")
    return int(value)


def identifiers(value, numeric=False):
    if value == "-":
        return []
    values = value.split(",")
    require(values == sorted(set(values)), "invalid-identifier-list")
    for item in values:
        if numeric:
            require(decimal(item) > 0, "invalid-actor")
        else:
            require(re.fullmatch(r"[a-z][a-z0-9-]*", item) is not None, "invalid-list-item")
    return values


def rows(data):
    require(isinstance(data, bytes) and data.endswith(b"\n"), "missing-final-lf")
    try:
        text = data.decode("utf-8", "strict")
    except UnicodeError:
        raise Refusal("invalid-utf8") from None
    require(all(c in "\t\n" or (ord(c) >= 32 and ord(c) != 127
                               and not 128 <= ord(c) <= 159) for c in text),
            "invalid-control-byte")
    result = [line.split("\t") for line in text[:-1].split("\n")]
    require(result and result[0] == ["format", "1"], "unsupported-format")
    require(all(all(row) for row in result), "empty-row-or-value")
    return result[1:]


BASE = {"sequence", "kind", "prior", "batch"}
EVENT_FIELDS = {
    "batch-start": {"control", "manifest", "approval-provenance", "config", "protocol", "day", "run", "attempt", "time"},
    "claim": {"repository", "workflow", "run", "attempt", "job", "generation", "operating-head"},
    "candidate": {"candidate-generation", "dev", "master", "tree", "rules", "tool", "baselines", "selected", "classification", "versions", "migrations", "approval-required"},
    "evidence": {"evidence-digest"},
    "approval": {"actor", "run", "attempt", "ref", "candidate-generation", "dev", "master", "tree", "classification", "versions", "migrations", "evidence-digest"},
    "intent": {"payload"},
    "observation": {"payload"},
    "retry-wait": {"minutes", "transient", "reason"},
    "blocker": {"reason"},
    "stop-observed": {"revision", "reason"},
    "resume": {"actor", "run", "attempt", "ref"},
    "complete": set(),
}
CONFIG = {"enabled", "public-repository", "repository", "operating-repository", "operating-ref", "workflow", "actors", "checks", "protocol"}
STOP = {"stop", "revision", "reason", "operator"}
REQUEST = {"mode", "actor", "run", "attempt", "ref", "candidate"}
APPROVED = {"public-repository", "master", "control", "manifest", "approval", "protocol"}
INDEX = {"sequence", "prior", "batch", "generation", "stage", "state-digest"}
TUPLES = {"evidence": 12, "release": 8, "operation": 8}


def parse(data, kind):
    raw = rows(data)
    singles, repeated = {}, {name: [] for name in TUPLES}
    for row in raw:
        name = row[0]
        if name in TUPLES:
            require(kind in ("event", "index"), "unexpected-tuple")
            require(len(row) == TUPLES[name], "bad-tuple-arity")
            repeated[name].append(row[1:])
        else:
            require(len(row) == 2 and name not in singles, "bad-or-duplicate-field")
            singles[name] = row[1]
    if kind == "event":
        event = singles.get("kind")
        require(event in EVENT_FIELDS, "unknown-event-kind")
        expected = BASE | EVENT_FIELDS[event]
        allowed = {"evidence": "evidence", "intent": "operation", "observation": "operation", "candidate": "release"}.get(event)
        require(all(not values or name == allowed for name, values in repeated.items()), "unexpected-event-tuple")
    else:
        expected = {"config": CONFIG, "stop": STOP, "request": REQUEST,
                    "approved": APPROVED, "index": INDEX}.get(kind)
        require(expected is not None, "unknown-record-kind")
    require(set(singles) == expected, "missing-or-unknown-field")
    for key, value in singles.items():
        if key in {"sequence", "run", "attempt", "job", "repository", "workflow", "generation", "candidate-generation", "revision", "actor", "operator", "minutes"}:
            decimal(value)
        if key in {"dev", "master", "tree", "control", "config", "operating-head"}:
            identity(value, 40)
        if key in {"prior", "batch", "manifest", "approval-provenance", "approval", "rules", "tool", "baselines", "evidence-digest", "candidate", "state-digest"}:
            identity(value)
        if key in {"enabled", "stop", "approval-required", "transient"}:
            require(value in ("0", "1"), "invalid-boolean")
        if key == "protocol":
            require(value == "1", "unsupported-protocol")
        if key == "time":
            require(re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", value) is not None, "invalid-time")
            try:
                datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                raise Refusal("invalid-time") from None
        if key == "day":
            require(re.fullmatch(r"\d{4}-\d\d-\d\d", value) is not None, "invalid-day")
            try:
                datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                raise Refusal("invalid-day") from None
        if key in {"checks", "selected"}:
            identifiers(value)
        if key == "actors":
            identifiers(value, True)
    if kind == "config":
        require(singles["public-repository"] == "shk95/configs", "wrong-public-repository")
        require(re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", singles["operating-repository"]) is not None, "invalid-connection")
        require(singles["operating-ref"] == "operations", "unsupported-operating-ref")
    for name, tuples in repeated.items():
        require(len({row[0] for row in tuples}) == len(tuples), "duplicate-tuple-id")
        for row in tuples:
            if name == "evidence":
                identifiers(row[0]); identity(row[1], 40); identity(row[2], 40); identity(row[3], 40)
                identity(row[4]); identity(row[5])
                require(row[6] in {"verified", "failed", "unverified"}, "invalid-evidence-state")
                for value in row[7:10]:
                    decimal(value)
            elif name == "release":
                require(row[0] in {"unixlike", "windows", "common"}, "invalid-release-domain")
                require(re.fullmatch(r"[1-9][0-9]*\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", row[1]) is not None, "invalid-version")
                for value in (row[2], row[4], row[5]):
                    identity(value, 40)
                if row[3] != "-":
                    identity(row[3], 40)
                identity(row[6])
            else:
                identity(row[0]); identity(row[2]); decimal(row[3])
                require(row[1] in {"record", "pr", "merge", "tag-object", "tag-ref", "cancel"}, "unsupported-operation")
                require(row[4] in {"intent", "observed", "unknown", "conflict"}, "invalid-operation-state")
                require(row[5] == "-" or re.fullmatch(r"[0-9a-f]{40}|[1-9][0-9]*", row[5]) is not None, "invalid-remote-identity")
                if row[6] != "-":
                    identity(row[6])
    singles.update({name: values for name, values in repeated.items() if values})
    return singles


def encode(fields):
    output = ["format\t1"]
    for key in sorted(fields):
        value = fields[key]
        if key in TUPLES:
            for row in sorted(value):
                output.append("\t".join([key] + row))
        else:
            require(isinstance(value, str) and value and not any(c in value for c in "\t\n"), "invalid-serialization")
            output.append(key + "\t" + value)
    return ("\n".join(output) + "\n").encode("utf-8")


def read(path):
    path = Path(path)
    require(path.is_file() and not path.is_symlink(), "missing-or-unsafe-record")
    return path.read_bytes()


def history(directory):
    directory = Path(directory)
    require(directory.is_dir() and not directory.is_symlink(), "missing-history")
    paths = sorted(directory.iterdir())
    result, previous = [], "0" * 64
    for sequence, path in enumerate(paths, 1):
        require(sequence < 10 ** 12 and path.name == f"{sequence:012d}.tsv", "event-sequence-gap-or-path")
        data = read(path)
        event = parse(data, "event")
        require(event["sequence"] == str(sequence) and event["prior"] == previous, "event-chain-mismatch")
        result.append(event)
        previous = digest(data)
    return result, previous
