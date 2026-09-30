"""Finite Darwin settings projection and caller-reviewed document capture.

INV unixlike/host-written-payload-projected
The proposal is a consistency guard, never a signature or author authentication.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import uuid


class Refusal(Exception):
    pass


class Unavailable(Refusal):
    pass


HERE = Path(__file__).resolve().parent
CONCERN = Path(os.environ.get("CONFIGS_CAPTURE_CONCERN", HERE.parent.parent / "modules/programs/karabiner"))


def pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise Refusal("duplicate JSON object key")
        result[key] = value
    return result


def decode(raw):
    try:
        result = json.loads(raw.decode("utf-8", errors="strict"), object_pairs_hook=pairs,
                          parse_constant=lambda _: (_ for _ in ()).throw(Refusal("nonfinite JSON number")))
        # JSON escape sequences must also decode to representable UTF-8.
        encoded(result)
        return result
    except (UnicodeError, ValueError) as error:
        raise Refusal("invalid UTF-8/JSON") from error


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


CONTRACT = decode((CONCERN / "units.json").read_bytes())


def exact(value, keys):
    return isinstance(value, dict) and set(value) == set(keys)


def validate_settings(unit, settings):
    u = CONTRACT["units"][unit]
    valid = False
    if unit == "karabiner":
        valid = (exact(settings, u["parents"]) and isinstance(settings["global"], dict)
                 and not any(k in settings["global"] for k in u["obsoleteGlobalKeys"])
                 and all(k not in settings["global"] or type(settings["global"][k]) is bool for k in u["globalBooleanKeys"])
                 and isinstance(settings["profiles"], list) and len(settings["profiles"]) >= u["profilesMinimum"]
                 and all(isinstance(p, dict) for p in settings["profiles"]))
        if valid:
            valid = all(bool(settings[k]) for k in u["requiredNonemptyObjects"])
            for profile in settings["profiles"]:
                valid = valid and bool(profile)
                for field, kind in [("profileStringKeys", str), ("profileBooleanKeys", bool),
                                    ("profileArrayKeys", list), ("profileObjectKeys", dict)]:
                    valid = valid and all(k not in profile or type(profile[k]) is kind for k in u[field])
                valid = valid and all(k not in profile or bool(profile[k]) for k in u["unstableEmptyProfileKeys"])
                if "complex_modifications" in profile:
                    complex_settings = profile["complex_modifications"]
                    valid = valid and isinstance(complex_settings, dict)
                    if isinstance(complex_settings, dict) and "rules" in complex_settings:
                        rules = complex_settings["rules"]
                        valid = valid and isinstance(rules, list) and len(rules) >= u["complexRulesMinimum"] and all(isinstance(r, dict) for r in rules)
    else:
        if exact(settings, [u["parent"]]) and exact(settings[u["parent"]], u["entries"]):
            valid = True
            for e in settings[u["parent"]].values():
                valid = valid and (exact(e, u["entryKeys"]) and type(e["enabled"]) is bool
                                  and exact(e["value"], u["valueKeys"]) and e["value"]["type"] == u["valueType"]
                                  and isinstance(e["value"]["parameters"], list)
                                  and len(e["value"]["parameters"]) == u["parameterCount"]
                                  and all(type(n) is int and u["parameterMinimum"] <= n <= u["parameterMaximum"]
                                          for n in e["value"]["parameters"]))
    if not valid:
        raise Refusal("unsupported " + unit + " settings shape")
    return settings


def document(unit, raw):
    d = decode(raw)
    if (not exact(d, ["formatVersion", "source", "settings"])
            or type(d["formatVersion"]) is not int or d["formatVersion"] != CONTRACT["formatVersion"]
            or d["source"] not in ["host", "configs"] or not isinstance(d["settings"], dict)):
        raise Refusal("unsupported settings document envelope")
    if d["source"] == "host":
        validate_settings(unit, d["settings"])
    return d


def project(unit, value):
    u = CONTRACT["units"][unit]
    if not isinstance(value, dict):
        raise Refusal("reader did not return an object")
    if unit == "karabiner":
        result = {k: value[k] for k in u["parents"] if k in value}
    else:
        parent = value.get(u["parent"])
        if not isinstance(parent, dict):
            raise Refusal("required hotkey parent absent")
        result = {u["parent"]: {k: parent[k] for k in u["entries"] if k in parent}}
    return validate_settings(unit, result)


def defaults(unit):
    filename = "karabiner.json" if unit == "karabiner" else "symbolic-hotkeys.json"
    return validate_settings(unit, decode((CONCERN / filename).read_bytes()))


def tool_identity():
    return {"engine": digest(Path(__file__).read_bytes()), "contract": digest((CONCERN / "units.json").read_bytes()),
            "defaults": {u: digest(encoded(defaults(u))) for u in CONTRACT["units"]},
            "runtime": digest(Path(sys.executable).read_bytes())}


def reader_for(unit, args):
    if unit == "karabiner":
        return {"kind": "file", "path": str(Path(args.host or Path.home() / ".config/karabiner/karabiner.json").absolute())}
    if args.hotkeys_host:
        return {"kind": "file", "path": str(Path(args.hotkeys_host).absolute())}
    return {"kind": "defaults", "domain": "com.apple.symbolichotkeys", "defaults": "/usr/bin/defaults", "plutil": "/usr/bin/plutil"}


def read_reader(reader):
    if reader.get("kind") == "file" and exact(reader, ["kind", "path"]):
        try:
            raw = Path(reader["path"]).read_bytes()
            s = Path(reader["path"]).stat()
        except OSError as error:
            raise Unavailable("reader unavailable") from error
        identity = {"device": s.st_dev, "inode": s.st_ino, "content": digest(raw)}
    elif reader == {"kind": "defaults", "domain": "com.apple.symbolichotkeys", "defaults": "/usr/bin/defaults", "plutil": "/usr/bin/plutil"}:
        if sys.platform != "darwin":
            raise Unavailable("native Darwin reader unavailable")
        try:
            raw_plist = subprocess.run([reader["defaults"], "export", reader["domain"], "-"], check=True, capture_output=True).stdout
            raw = subprocess.run([reader["plutil"], "-convert", "json", "-o", "-", "-"], input=raw_plist, check=True, capture_output=True).stdout
        except (OSError, subprocess.CalledProcessError) as error:
            raise Unavailable("native defaults/plutil reader unavailable") from error
        identity = {"content": digest(raw), "executables": {p: digest(Path(p).read_bytes()) for p in [reader["defaults"], reader["plutil"]]}}
    else:
        raise Refusal("invalid reader binding")
    return decode(raw), identity


def protected_paths(readers):
    roots = [Path("/nix/store"), Path.home() / ".config/karabiner", Path.home() / "Library/Preferences",
             Path("/Applications"), Path.home() / "Applications",
             Path("/Library/Application Support/org.pqrs"), CONCERN]
    # A source checkout's parent repository is also protected. A packaged store
    # source has no checkout and is already excluded by the store boundary.
    for ancestor in [*HERE.parents, *CONCERN.parents]:
        if (ancestor / ".git").exists():
            roots.append(ancestor)
            break
    originals = [Path(r["path"]).resolve() for r in readers if r["kind"] == "file"]
    return roots, originals


def guard_path(path, readers):
    p = Path(os.path.abspath(path))
    roots, originals = protected_paths(readers)
    resolved = p.resolve()
    if any(part.suffix.casefold() == ".app" for part in [resolved, *resolved.parents]):
        raise Refusal("application bundle destination")
    if p != resolved:
        raise Refusal("symlink or noncanonical destination")
    if any(resolved == r.resolve() or r.resolve() in resolved.parents for r in roots) or resolved in originals:
        raise Refusal("provider, store, app or observed original destination")
    if not p.parent.is_dir():
        raise Refusal("prospective destination parent must already exist")
    for component in [p.parent, *p.parent.parents]:
        if component.is_symlink():
            raise Refusal("symlink parent")
    if p.exists():
        s = p.lstat()
        if not stat.S_ISREG(s.st_mode) or s.st_nlink != 1:
            raise Refusal("destination must be a single-link regular file")
    return p


def target_snapshot(path, readers):
    p = guard_path(path, readers)
    parent = p.parent.stat()
    result = {"path": str(p), "parent": {"device": parent.st_dev, "inode": parent.st_ino}, "exists": p.exists()}
    if result["exists"]:
        s = p.stat()
        result.update({"device": s.st_dev, "inode": s.st_ino, "content": digest(p.read_bytes()), "mode": stat.S_IMODE(s.st_mode)})
    return result


def atomic_replace(path, raw, expected, readers):
    p = guard_path(path, readers)
    # Keep the validated directory open and address both names through it.
    fd = os.open(p.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    temporary = ".darwin-capture-" + uuid.uuid4().hex
    try:
        s = os.fstat(fd)
        if {"device": s.st_dev, "inode": s.st_ino} != expected["parent"]:
            raise Refusal("destination parent changed")
        out = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=fd)
        with os.fdopen(out, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        if target_snapshot(path, readers) != expected:
            raise Refusal("destination changed before replacement")
        os.replace(temporary, p.name, src_dir_fd=fd, dst_dir_fd=fd)
    finally:
        try:
            os.unlink(temporary, dir_fd=fd)
        except FileNotFoundError:
            pass
        os.close(fd)


def prepare(units, targets, readers):
    if not units or len(units) != len(targets) or len(set(units)) != len(units) or any(u not in CONTRACT["units"] for u in units):
        raise Refusal("explicit unique unit/document pairs required")
    paths = [guard_path(t, readers) for t in targets]
    if len(set(paths)) != len(paths):
        raise Refusal("aliased destinations")
    entries = []
    for unit, path, reader in zip(units, paths, readers):
        value, input_identity = read_reader(reader)
        snapshot = target_snapshot(path, readers)
        prior = document(unit, path.read_bytes()) if snapshot["exists"] else None
        entries.append({"unit": unit, "reader": reader, "input": input_identity, "target": snapshot,
                        "priorSource": prior["source"] if prior else None,
                        "document": {"formatVersion": CONTRACT["formatVersion"], "source": "host", "settings": project(unit, value)}})
    return entries


def preview(args):
    units = args.unit or []
    readers = [reader_for(u, args) for u in units]
    entries = prepare(units, args.document or [], readers)
    output = guard_path(args.output, readers)
    if str(output) in [e["target"]["path"] for e in entries]:
        raise Refusal("proposal aliases destination")
    # Never overwrite an existing proposal; another preview uses another path.
    if output.exists():
        raise Refusal("proposal output already exists")
    proposal = {"formatVersion": 1, "tool": tool_identity(), "entries": entries}
    atomic_replace(str(output), encoded(proposal), target_snapshot(str(output), readers), readers)
    print(encoded(proposal).decode(), end="")


def save(args):
    proposal_path = Path(args.preview)
    proposal = decode(proposal_path.read_bytes())
    if not exact(proposal, ["formatVersion", "tool", "entries"]) or type(proposal["formatVersion"]) is not int or proposal["formatVersion"] != 1 or proposal["tool"] != tool_identity():
        raise Refusal("invalid or stale proposal/tool binding")
    entries = proposal["entries"]
    if not isinstance(entries, list) or not entries:
        raise Refusal("empty proposal")
    for e in entries:
        if not exact(e, ["unit", "reader", "input", "target", "priorSource", "document"]):
            raise Refusal("invalid proposal entry")
    readers = [e["reader"] for e in entries]
    units = [e["unit"] for e in entries]
    targets = [e["target"]["path"] for e in entries]
    guard_path(str(proposal_path), readers)
    if stat.S_IMODE(proposal_path.stat().st_mode) != 0o600:
        raise Refusal("proposal must remain private at mode 600")
    if str(proposal_path.resolve()) in targets:
        raise Refusal("proposal aliases destination")
    current = prepare(units, targets, readers)
    if current != entries:
        raise Refusal("stale input/target or inconsistent projected proposal")
    # Prepare-all is followed by a second complete observation before any write.
    if prepare(units, targets, readers) != entries:
        raise Refusal("inputs changed during preparation")
    results = []
    for index, e in enumerate(entries):
        try:
            if target_snapshot(e["target"]["path"], readers) != e["target"]:
                raise Refusal("target changed before its replacement")
            raw = encoded(e["document"])
            if e["target"]["exists"] and Path(e["target"]["path"]).read_bytes() == raw:
                state = "unchanged"
            else:
                atomic_replace(e["target"]["path"], raw, e["target"], readers)
                state = "completed"
            results.append({"unit": e["unit"], "state": state})
        except (OSError, Refusal) as error:
            results.append({"unit": e["unit"], "state": "refused" if isinstance(error, Refusal) else "incomplete"})
            results.extend({"unit": later["unit"], "state": "incomplete"} for later in entries[index + 1:])
            print(encoded({"results": results, "error": str(error)}).decode(), end="")
            return 1
    print(encoded({"results": results}).decode(), end="")
    return 0


def adapter_replace(path, raw):
    # Application is separately invoked by Home Manager. Unlike capture Save,
    # its destination is the app target. Fixtures pass disposable explicit paths.
    p = Path(path)
    if p.is_symlink() or (p.exists() and (not p.is_file() or p.stat().st_nlink != 1)):
        raise Refusal("adapter target must be an unaliased regular file")
    p.parent.mkdir(parents=True, exist_ok=True)
    p = p.absolute()
    if p.parent.resolve() != p.parent:
        raise Refusal("adapter target parent must be canonical")
    fd = os.open(p.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    temporary = ".darwin-apply-" + uuid.uuid4().hex
    try:
        out = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=fd)
        with os.fdopen(out, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, p.name, src_dir_fd=fd, dst_dir_fd=fd)
    finally:
        try:
            os.unlink(temporary, dir_fd=fd)
        except FileNotFoundError:
            pass
        os.close(fd)


def adapt(args):
    if len(args.unit) != len(args.settings) or len(set(args.unit)) != len(args.unit):
        raise Refusal("unique unit/settings pairs required")
    if not args.unit:
        return 0
    prepared = []
    for unit, settings_path in zip(args.unit, args.settings):
        wanted = validate_settings(unit, decode(Path(settings_path).read_bytes()))
        reader = reader_for(unit, args)
        if unit == "karabiner" and not Path(reader["path"]).exists():
            observed = {}
        else:
            observed, _ = read_reader(reader)
        if not isinstance(observed, dict):
            raise Refusal("adapter input must be an object")
        try:
            matches = project(unit, observed) == wanted
        except Refusal:
            matches = False
        prepared.append((unit, wanted, observed, reader, matches))
    if args.command == "check":
        for unit, _, _, _, matches in prepared:
            print(unit + (": matches" if matches else ": drift"))
        return 0 if all(p[4] for p in prepared) else 1
    results = []
    hotkeys_written = False
    for index, (unit, wanted, observed, reader, matches) in enumerate(prepared):
        try:
            if matches:
                results.append({"unit": unit, "state": "unchanged"})
                continue
            if unit == "karabiner":
                merged = {**observed, **wanted}
                adapter_replace(args.target or reader["path"], encoded(merged))
            elif args.hotkeys_host:
                if not args.hotkeys_target:
                    raise Refusal("synthetic hotkey reader requires explicit synthetic target")
                parent = CONTRACT["units"][unit]["parent"]
                existing = observed.get(parent, {})
                if not isinstance(existing, dict):
                    raise Refusal("hotkey parent must be an object")
                merged = {**observed, parent: {**existing, **wanted[parent]}}
                adapter_replace(args.hotkeys_target, encoded(merged))
            else:
                parent = CONTRACT["units"][unit]["parent"]
                existing = observed.get(parent, {})
                if not isinstance(existing, dict):
                    raise Refusal("hotkey parent must be an object")
                for entry in CONTRACT["units"][unit]["entries"]:
                    value = wanted[parent][entry]
                    if existing.get(entry) == value:
                        continue
                    plist = subprocess.run(["/usr/bin/plutil", "-convert", "xml1", "-o", "-", "-"], input=encoded(value), capture_output=True, check=True).stdout
                    subprocess.run(["/usr/bin/defaults", "write", "com.apple.symbolichotkeys", parent, "-dict-add", entry, plist.decode("utf-8")], check=True, capture_output=True)
                    hotkeys_written = True
            results.append({"unit": unit, "state": "completed"})
        except (Refusal, OSError, subprocess.CalledProcessError) as error:
            results.append({"unit": unit, "state": "incomplete"})
            results.extend({"unit": later[0], "state": "incomplete"} for later in prepared[index + 1:])
            print(encoded({"results": results, "error": str(error)}).decode(), end="")
            return 1
    if hotkeys_written:
        activate = "/System/Library/PrivateFrameworks/SystemAdministration.framework/Resources/activateSettings"
        try:
            subprocess.run([activate, "-u"], capture_output=True, check=True)
        except (OSError, subprocess.CalledProcessError):
            print("warning: preferences written; reload unavailable, logout applies them", file=sys.stderr)
    print(encoded({"results": results}).decode(), end="")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Preview and save explicitly selected host settings documents")
    commands = parser.add_subparsers(dest="command", required=True)
    p = commands.add_parser("preview")
    p.add_argument("--unit", action="append", choices=list(CONTRACT["units"]), required=True)
    p.add_argument("--document", action="append", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--host")
    p.add_argument("--hotkeys-host")
    s = commands.add_parser("save")
    s.add_argument("--preview", required=True)
    args = parser.parse_args()
    try:
        return preview(args) if args.command == "preview" else save(args)
    except Unavailable as error:
        print("unavailable: " + str(error), file=sys.stderr)
        return 69
    except (Refusal, OSError, KeyError, TypeError) as error:
        print("refused: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
