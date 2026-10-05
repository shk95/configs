"""Bounded provider lock refresh. Standard library only; no Git/deployment calls.

INV unixlike/provider-input-refresh-bounded
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def nix(*arguments):
    result = subprocess.run(["nix", *arguments], text=True, stdout=subprocess.PIPE)
    if result.returncode:
        raise ValueError(f"Nix command failed ({result.returncode})")
    return result.stdout


def exclusions(data):
    value = json.loads(data)
    if (not isinstance(value, dict) or set(value) != {"formatVersion", "exclusions"}
            or type(value["formatVersion"]) is not int or value["formatVersion"] != 1
            or not isinstance(value["exclusions"], list)):
        raise ValueError("invalid exclusion configuration")
    names = set()
    for entry in value["exclusions"]:
        if (not isinstance(entry, dict) or set(entry) != {"input", "reason"}
                or not isinstance(entry["input"], str) or not entry["input"]
                or not isinstance(entry["reason"], str) or not entry["reason"].strip()
                or entry["input"] in names):
            raise ValueError("invalid or duplicate exclusion; input and reason are required")
        names.add(entry["input"])
    return names


def inputs(lock):
    if lock.get("version") != 7:
        raise ValueError("unsupported lock format")
    return lock["nodes"][lock["root"]].get("inputs", {})


def own_source(lock, name):
    edge = inputs(lock).get(name)
    if not isinstance(edge, str):
        raise ValueError(f"{name}: exclusion needs an existing independent locked source")
    return lock["nodes"][edge]["locked"]


def source_snapshot(root, ignored):
    result = {}
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if relative.parts[0] in ignored or ".git" in relative.parts:
            continue
        if path.is_symlink():
            raise ValueError(f"provider source symlink is unsupported: {relative}")
        elif path.is_file():
            result[str(relative)] = (hashlib.sha256(path.read_bytes()).hexdigest(),
                                     path.stat().st_mode & 0o777)
    return result


def refresh(root, check=False, requested=None):
    lock_path = root / "flake.lock"
    config_path = root / "flake-refresh-exclusions.json"
    # An atomic directory claim serializes cooperating invocations without a
    # persistent file or unlinking a lock inode another process has acquired.
    running = root / ".refresh-inputs-running"
    try:
        running.mkdir()
    except FileExistsError as error:
        raise ValueError("another refresh or a stale refresh claim exists; inspect before recovery") from error
    try:
        with tempfile.TemporaryDirectory(prefix=".refresh-inputs-", dir=root) as directory:
            temporary = Path(directory)
            ignored = {running.name, temporary.name}
            original = lock_path.read_bytes()
            baseline = json.loads(original)
            configuration = config_path.read_bytes()
            excluded = exclusions(configuration)
            snapshot = source_snapshot(root, ignored)
            if (snapshot["flake.lock"][0] != hashlib.sha256(original).hexdigest()
                    or snapshot["flake-refresh-exclusions.json"][0] != hashlib.sha256(configuration).hexdigest()):
                raise ValueError("provider lock/config changed during initial snapshot")
            reference = temporary / "reference.lock"
            candidate_path = temporary / "candidate.lock"
            reference.write_bytes(original)
            arguments = ["flake", "metadata", "--json", "--no-write-lock-file",
                         "--reference-lock-file", str(reference)]
            if check:
                arguments += ["--offline", "--no-update-lock-file"]
            graph = json.loads(nix(*arguments, f"path:{root}"))["locks"]
            direct = inputs(graph)
            for name in excluded:
                if name not in direct:
                    raise ValueError(f"unknown excluded input: {name}")
                if not isinstance(direct[name], str):
                    raise ValueError(f"cannot exclude a follows alias: {name}")
                own_source(baseline, name)
            independent = {name for name, edge in direct.items() if isinstance(edge, str)}
            if requested is not None:
                names = set(requested)
                if not names or len(names) != len(requested) or not names <= independent or names & excluded:
                    raise ValueError("selection must name distinct non-excluded independent inputs")
                excluded |= independent - names
                for name in excluded:
                    own_source(baseline, name)
            selected = sorted(independent - excluded)
            print(json.dumps({"independent": sorted(name for name, edge in direct.items()
                                                    if isinstance(edge, str)),
                              "follows": {name: edge for name, edge in direct.items()
                                          if isinstance(edge, list)},
                              "excluded": sorted(excluded), "selected": selected}))
            if check or not selected:
                if source_snapshot(root, ignored) != snapshot:
                    raise ValueError("provider sources changed during selection")
                return "checked" if check else "empty selection; unchanged"
            nix("flake", "update", *selected, "--flake", f"path:{root}",
                "--reference-lock-file", str(reference),
                "--output-lock-file", str(candidate_path))
            candidate_bytes = candidate_path.read_bytes()
            candidate = json.loads(candidate_bytes)
            candidate_inputs = inputs(candidate)
            if set(candidate_inputs) != set(direct):
                raise ValueError("candidate direct input set changed")
            for name, edge in direct.items():
                if isinstance(edge, list) and candidate_inputs[name] != edge:
                    raise ValueError(f"candidate changed follows alias: {name}")
            for name in excluded:
                if own_source(candidate, name) != own_source(baseline, name):
                    raise ValueError(f"candidate changed excluded source: {name}")
            # Verify the candidate is accepted by Nix, not only JSON-shaped.
            nix("flake", "metadata", "--json", "--no-update-lock-file",
                "--no-write-lock-file", "--reference-lock-file", str(candidate_path), f"path:{root}")
            if source_snapshot(root, ignored) != snapshot:
                raise ValueError("provider lock/config/source changed; stale candidate refused")
            if candidate == baseline:
                return "unchanged"
            candidate_path.chmod(lock_path.stat().st_mode & 0o777)
            with candidate_path.open("rb") as stream:
                os.fsync(stream.fileno())
            if source_snapshot(root, ignored) != snapshot:
                raise ValueError("provider lock/config/source changed; stale candidate refused")
            # Publication is the commit point. Every failure above preserves
            # original bytes; an interrupted rename leaves a complete old/new
            # file. Arbitrary noncooperating writers are not filesystem CAS.
            os.replace(candidate_path, lock_path)
            return "updated flake.lock"
    finally:
        running.rmdir()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="offline read-only current input inventory")
    parser.add_argument("--input", action="append", help="refresh only this independent input; repeat to select more")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    try:
        print(refresh(root, args.check, args.input))
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f"refresh-inputs: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
