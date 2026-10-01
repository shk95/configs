"""Small fixed loader. Approval file is an assertion in this preview-only lane."""
# INV repository/release-control-preview-only
import argparse
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
    if result["public-repository"] != "shk95/configs" or result["protocol"] not in {"1", "2"}:
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
    args = parser.parse_args()
    try:
        paths = {k: Path(getattr(args, k)).resolve(strict=True) for k in
                 ("bundle_repository", "approved", "operating", "transcript", "request")}
        for key in ("approved", "transcript", "request"):
            if Path(getattr(args, key)).is_symlink() or not paths[key].is_file():
                raise ValueError("unsafe-input-path")
        assertion = approved(paths["approved"].read_bytes())
        with tempfile.TemporaryDirectory(prefix="release-control-") as directory:
            scratch = Path(directory)
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
                permitted = ({"outcome", "proposed"} if summary.get("outcome") == "stopped"
                             else {"outcome", "stage", "proposed"})
                if (set(summary) != permitted or summary.get("outcome") not in {"preview", "stopped"}
                    or type(summary.get("proposed")) is not int or summary["proposed"] < 0
                    or ("stage" in summary and summary["stage"] not in
                        {"empty", "active", "candidate", "validated", "approved", "promoted", "publishing", "waiting", "blocked", "complete"})):
                    raise ValueError("unsafe-package-output")
                print(json.dumps(summary, sort_keys=True))
    except (ValueError, OSError, subprocess.SubprocessError):
        # Never print raw private paths, records, digests, or exception payloads.
        print("release-control: refused", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
