"""Actual trusted CLI/local Git fixtures, never a production preparation command.

INV repository/release-control-preview-only
INV repository/fixture-git-isolation
INV repository/flake-lock-isolated
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time

TOOLS = Path(__file__).resolve().parent
REPOSITORY = TOOLS.parent.parent
TRUSTED_SOURCE = "21532ddf5b6f98cd7ade1163ffa43a44b16dd339"
UTILITY = {"unixlike/tool/refresh-inputs": ("100755", "103f607f59c392a728414cffc0be8d85e63dba1e660bf4259bdb9fd7677b639a"),
           "unixlike/tool/refresh_inputs.py": ("100644", "83b1e83a73d6eb29770b7c222b3e3cfe23df3576f76e2ac1e2b98a17490b0d08")}
spec = importlib.util.spec_from_file_location("control_fixture", TOOLS / "test-release-control.py")
c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
NIX = shutil.which("nix")
GIT = shutil.which("git")


def run(*args, env, okay=True, **kw):
    result = subprocess.run(args, env=env, capture_output=True, **kw)
    if okay and result.returncode:
        raise AssertionError("controlled fixture command failed: " + str(result.returncode))
    return result


def git(repo, *args, env, okay=True):
    return run(GIT, "--no-replace-objects", "-C", str(repo), *args, env=env, okay=okay).stdout


def environment(work):
    runtime = work / "runtime"; runtime.mkdir()
    for name, executable in (("python3", sys.executable), ("nix", NIX), ("git", GIT)):
        (runtime / name).symlink_to(Path(executable).resolve())
    home = work / "home"; home.mkdir()
    return {"PATH": str(runtime) + ":/usr/bin:/bin", "HOME": str(home), "TMPDIR": str(work),
            "LANG": "C.UTF-8", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_SYSTEM": os.devnull,
            "GIT_CONFIG_GLOBAL": os.devnull, "GIT_TEMPLATE_DIR": "", "GIT_ALLOW_PROTOCOL": "file",
            "GIT_PROTOCOL_FROM_USER": "0", "GIT_TERMINAL_PROMPT": "0", "GIT_NO_REPLACE_OBJECTS": "1",
            "GIT_NO_LAZY_FETCH": "1", "NIX_CONFIG": "experimental-features = nix-command flakes\nsubstituters =\n"}


def initialize(repo, env):
    repo.mkdir()
    git(repo, "init", "-q", "-b", "dev", env=env)
    git(repo, "config", "user.name", "Fixture", env=env)
    git(repo, "config", "user.email", "fixture@example.invalid", env=env)
    git(repo, "config", "core.hooksPath", str(repo.parent / "no-hooks"), env=env)


def commit(repo, env, message="fixture"):
    git(repo, "add", ".", env=env)
    git(repo, "commit", "-qm", message, env=env)
    return git(repo, "rev-parse", "HEAD", env=env).decode().strip()


def snapshot(root):
    result = {}
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if ".git" in relative.parts:
            continue
        if path.is_symlink():
            raise ValueError("fixture source symlink refused")
        if path.is_file():
            result[relative.as_posix()] = (path.read_bytes(), path.stat().st_mode & 0o777)
    return result


def fingerprint(files):
    return c.digest(c.canonical({name: [c.digest(data), mode] for name, (data, mode) in files.items()}))


def state(repo, env):
    return (snapshot(repo), git(repo, "show-ref", env=env), git(repo, "rev-list", "--all", "--count", env=env),
            git(repo, "rev-parse", "HEAD", env=env), git(repo, "status", "--porcelain=v1", env=env))


def trusted_utility(repo, env):
    for name, (mode, expected) in UTILITY.items():
        data = git(REPOSITORY, "show", TRUSTED_SOURCE + ":" + name, env=env)
        metadata = git(REPOSITORY, "ls-tree", TRUSTED_SOURCE, "--", name, env=env).decode().split()
        assert metadata[:2] == [mode, "blob"] and c.digest(data) == expected
        path = repo / name; path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data); path.chmod(0o755 if mode == "100755" else 0o644)


def copy_tree(repo, tree, target, env):
    target.mkdir()
    for item in git(repo, "ls-tree", "-rz", tree, env=env).split(b"\0"):
        if not item:
            continue
        meta, name = item.split(b"\t", 1); mode, kind, object_id = meta.decode().split()
        relative = Path(name.decode())
        assert mode in {"100644", "100755"} and kind == "blob" and not relative.is_absolute() and ".." not in relative.parts
        path = target / relative; path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(git(repo, "cat-file", "blob", object_id, env=env)); path.chmod(0o755 if mode == "100755" else 0o644)


def prepare(repo, batch, base, env, *, previous=None, timeout=60, fault=None):
    """Owns disposable fixture roots only. No caller-provided script or transport."""
    assert repo.parent.name.startswith("refresh-candidate-fixture-")
    assert git(repo, "rev-parse", "dev", env=env).decode().strip() == base
    assert not git(repo, "status", "--porcelain=v1", env=env)
    assert not git(repo, "remote", env=env)
    branch = c.adapter.refresh_branch(batch)
    registry = repo / ".git/refresh-fixture-owner.json"
    owned = json.loads(registry.read_text()) if registry.exists() else None
    existing = git(repo, "rev-parse", "--verify", "refs/heads/" + branch, env=env, okay=False).decode().strip()
    if existing:
        assert owned and owned["candidate"]["batch"] == batch and owned["candidate"]["branch"] == branch
        assert existing == owned["candidate"]["head"]
        if previous is None and owned["candidate"]["base"] == base:
            return {"status": "changed", "candidate": owned["candidate"]}, owned["proof"], "duplicate join"
        assert previous == existing and owned["candidate"]["base"] != base
        old_base = owned["candidate"]["base"]
        assert git(repo, "diff", "--name-only", old_base, existing, env=env).decode().splitlines() == ["unixlike/flake.lock"] or owned["candidate"]["previous"] != "-"
        merged = run(GIT, "--no-replace-objects", "-C", str(repo), "merge-tree", "--write-tree", previous, base, env=env, okay=False)
        if merged.returncode:
            raise ValueError("required fixture merge conflict")
        tree = merged.stdout.decode().splitlines()[0]
    else:
        assert previous is None and owned is None
        tree = git(repo, "rev-parse", base + "^{tree}", env=env).decode().strip()
    before_state = state(repo, env)
    with tempfile.TemporaryDirectory(prefix="candidate-data-", dir=repo.parent) as directory:
        workspace = Path(directory)
        source = workspace / "source"
        copy_tree(repo, tree, source, env)
        provider = source / "unixlike"
        for name, (_, expected) in UTILITY.items():
            assert c.digest((source / name).read_bytes()) == expected
        before = snapshot(source)
        original = (provider / "flake.lock").read_bytes()
        assert json.loads(original)["version"] == 7
        process_env = dict(env)
        process_env["TMPDIR"] = str(workspace)
        if fault:
            fault_runtime = workspace / "fault-runtime"; fault_runtime.mkdir()
            script = fault_runtime / "nix"
            if fault == "timeout":
                script.write_text("#!/bin/sh\nexec /bin/sleep 30\n")
            elif fault == "failure":
                script.write_text("#!/bin/sh\nexit 42\n")
            elif fault == "source":
                script.write_text("#!/bin/sh\nprintf 'contamination\\n' > '" + str(provider / "foreign") + "'\nexec '" + str(NIX) + "' \"$@\"\n")
            else:
                raise ValueError("unknown controlled fault")
            script.chmod(0o755)
            process_env["PATH"] = str(fault_runtime) + ":" + env["PATH"]
        child = subprocess.Popen([str(provider / "tool/refresh-inputs")], cwd=workspace, env=process_env,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        timed_out = False
        try:
            stdout, _ = child.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(child.pid, signal.SIGKILL)
            stdout, _ = child.communicate(timeout=5)
            assert child.poll() is not None
            # The known timeout wrapper execs sleep: verify no live group member.
            group_gone = False
            for _ in range(50):
                try:
                    os.killpg(child.pid, 0)
                except ProcessLookupError:
                    group_gone = True; break
                time.sleep(0.02)
            assert group_gone, "unconfirmed fixture termination"
        if timed_out or child.returncode:
            assert state(repo, env) == before_state
            return {"status": "terminated-timeout" if timed_out else "failed"}, None, "controlled failure"
        after = snapshot(source)
        assert {k: v for k, v in before.items() if k != "unixlike/flake.lock"} == {k: v for k, v in after.items() if k != "unixlike/flake.lock"}
        lock = (provider / "flake.lock").read_bytes()
        assert json.loads(lock)["version"] == 7 and before["unixlike/flake.lock"][1] == after["unixlike/flake.lock"][1]
        run(NIX, "flake", "metadata", "--json", "--no-write-lock-file", "--no-update-lock-file", "--reference-lock-file", str(provider / "flake.lock"), "path:" + str(provider), env=env)
        if lock == original:
            assert state(repo, env) == before_state
            return {"status": "noop"}, None, stdout.decode()
        # No source/ref commit was made by the CLI or merge-tree preflight.
        assert state(repo, env) == before_state
        if previous:
            git(repo, "checkout", "-q", branch, env=env)
            git(repo, "merge", "--no-ff", "-qm", "chore(unixlike): merge required fixture base", base, env=env)
            parent = git(repo, "rev-parse", "HEAD", env=env).decode().strip()
            merge_parents = git(repo, "show", "-s", "--format=%P", parent, env=env).decode().strip().split()
            assert merge_parents == [previous, base]
            assert git(repo, "rev-parse", parent + "^{tree}", env=env).decode().strip() == tree
        else:
            git(repo, "checkout", "-qb", branch, base, env=env)
            parent = base; merge_parents = []
        assert snapshot(repo) == before
        (repo / "unixlike/flake.lock").write_bytes(lock)
        (repo / "unixlike/flake.lock").chmod(after["unixlike/flake.lock"][1])
        git(repo, "add", "--", "unixlike/flake.lock", env=env)
        assert git(repo, "diff", "--cached", "--name-only", env=env).decode().splitlines() == ["unixlike/flake.lock"]
        git(repo, "commit", "-qm", "chore(unixlike-deps): refresh controlled fixture inputs", env=env)
        head = git(repo, "rev-parse", "HEAD", env=env).decode().strip()
        parents = git(repo, "show", "-s", "--format=%P", head, env=env).decode().strip().split()
        changed = git(repo, "diff", "--name-only", parent, head, env=env).decode().splitlines()
        assert parents == [parent] and changed == ["unixlike/flake.lock"]
        assert git(repo, "rev-parse", "dev", env=env).decode().strip() == base
        assert not git(repo, "status", "--porcelain=v1", env=env)
        assert snapshot(repo) == after
        assert git(repo, "show", head + ":unixlike/flake.lock", env=env) == lock
        assert git(repo, "log", "-1", "--format=%s", head, env=env).decode().strip().startswith("chore(unixlike-deps):")
        candidate = {"batch": batch, "branch": branch, "source": parent, "parent": parent,
                     "base": base, "head": head, "tree": git(repo, "rev-parse", head + "^{tree}", env=env).decode().strip(),
                     "before-lock": c.digest(original), "lock": c.digest(lock), "previous": previous or "-",
                     "utility-source": TRUSTED_SOURCE, "utility-manifest": c.digest(c.canonical(UTILITY)), "source-fingerprint": fingerprint(before)}
        proof = {"head-parents": parents, "merge-parents": merge_parents, "changed": changed,
                 "before-lock": c.digest(original), "lock": c.digest(lock), "before-mode": before["unixlike/flake.lock"][1], "mode": after["unixlike/flake.lock"][1]}
        c.adapter.refresh_candidate(candidate)
        registry.write_text(json.dumps({"candidate": candidate, "proof": proof}))
        return {"status": "changed", "candidate": candidate}, proof, stdout.decode()


def upstream(repo, env):
    initialize(repo, env)
    (repo / "flake.nix").write_text('{ outputs = { ... }: {}; }\n')
    (repo / "payload").write_text("first\n")
    commit(repo, env)


def url(repo):
    return "git+" + repo.as_uri() + "?ref=dev"


def integration():
    with tempfile.TemporaryDirectory(prefix="refresh-candidate-fixture-") as directory:
        workspace = Path(directory).resolve(); env = environment(workspace)
        assert not any("TOKEN" in k or k.startswith("AWS") or k.startswith("PYTHON") for k in env)
        a, b, added = (workspace / n for n in ("a", "b", "added"))
        for repo in (a, b, added):
            upstream(repo, env)
        repo = workspace / "provider"; initialize(repo, env); trusted_utility(repo, env)
        provider = repo / "unixlike"
        (provider / "flake.nix").write_text('{ inputs.a.url = "' + url(a) + '"; inputs.b.url = "' + url(b) + '"; inputs.alias.follows = "a"; outputs = { ... }: {}; }\n')
        (provider / "flake-refresh-exclusions.json").write_text(json.dumps({"formatVersion": 1, "exclusions": [{"input": "b", "reason": "controlled fixture"}]}))
        run(NIX, "flake", "lock", "path:" + str(provider), env=env)
        base = commit(repo, env)
        initial = state(repo, env)
        result, proof, _ = prepare(repo, c.X, base, env)
        assert result == {"status": "noop"} and proof is None and state(repo, env) == initial
        for fault in ("failure", "source", "timeout"):
            result, proof, _ = prepare(repo, c.X, base, env, fault=fault, timeout=0.2 if fault == "timeout" else 60)
            assert result["status"] in {"failed", "terminated-timeout"} and proof is None and state(repo, env) == initial
        print("PASS actual CLI no-op/failure/source-fault/confirmed timeout: bytes/modes/refs/commit count unchanged")
        (a / "payload").write_text("second\n"); commit(a, env)
        result, proof, output = prepare(repo, c.X, base, env)
        candidate = result["candidate"]
        selection = json.loads(output.splitlines()[0])
        assert selection["selected"] == ["a"] and selection["excluded"] == ["b"] and selection["follows"] == {"alias": ["a"]}
        events, transcript, payload, branch, pr, _, _ = c.refresh_flow(candidate, proof)
        state_one = c.engine.reduce(c.sequence(events), c.CONFIG, transcript)
        assert state_one["refresh-stage"] == "ready" and state_one["operations"][branch]["remote"] == candidate["head"]
        prior = state(repo, env)
        duplicate, duplicate_proof, _ = prepare(repo, c.X, base, env)
        assert duplicate == result and duplicate_proof == proof and state(repo, env) == prior
        print("PASS actual trusted selection/exclusion/follows → isolated lock commit → production parser/reducer → fake branch/PR; duplicate joins")
        continuation = workspace / "continuation"
        shutil.copytree(repo, continuation)
        # Human commit on the occupied automation branch cannot be treated as ours.
        (repo / "human").write_text("unrelated\n"); human = commit(repo, env)
        contaminated = state(repo, env)
        try:
            prepare(repo, c.X, base, env, previous=human)
        except AssertionError:
            pass
        else:
            raise AssertionError("occupied human branch accepted")
        assert state(repo, env) == contaminated
        # This discarded human fixture is preserved; continue in a separate copy.
        git(continuation, "checkout", "-q", "dev", env=env)
        provider_two = continuation / "unixlike"
        (continuation / "base-source").write_text("required source update\n")
        no_op_base = commit(continuation, env)
        required_before = state(continuation, env)
        no_op, no_op_proof, _ = prepare(continuation, c.X, no_op_base, env, previous=candidate["head"])
        assert no_op == {"status": "noop"} and no_op_proof is None and state(continuation, env) == required_before
        print("PASS required base-update preflight no-op creates no merge/dependency commit and changes no owned refs/source")
        content = (provider_two / "flake.nix").read_text().replace("outputs =", 'inputs.new.url = "' + url(added) + '"; outputs =')
        (provider_two / "flake.nix").write_text(content)
        new_base = commit(continuation, env)
        second, second_proof, output = prepare(continuation, c.X, new_base, env, previous=candidate["head"])
        newer = second["candidate"]
        assert newer["branch"] == candidate["branch"] and newer["previous"] == candidate["head"]
        assert second_proof["merge-parents"] == [candidate["head"], new_base]
        assert json.loads(output.splitlines()[0])["selected"] == ["a", "new"]
        events_two, proof_two, payload_two, branch_two, pr_two, _, _ = c.refresh_flow(newer, second_proof, prefix=events)
        proof_two["refresh"]["revisions"].insert(0, transcript["refresh"]["revisions"][0])
        proof_two["observations"].update(transcript["observations"])
        state_two = c.engine.reduce(c.sequence(events_two), c.CONFIG, proof_two)
        assert state_two["refresh-stage"] == "ready" and branch != branch_two and pr != pr_two
        assert state_two["operations"][branch]["remote"] == candidate["head"] and state_two["operations"][pr]["remote"] == "17"
        assert state_two["operations"][pr_two]["remote"] == "17"
        assert git(continuation, "merge-base", "--is-ancestor", candidate["head"], newer["head"], env=env) == b""
        protected_before = state(continuation, env)
        try:
            prepare(continuation, c.X, base, env, previous=candidate["head"])
        except AssertionError:
            pass
        else:
            raise AssertionError("wrong current base accepted")
        assert state(continuation, env) == protected_before
        print("PASS required normal merge/new-input local lock commit preserves same branch/history and old observed identities; existing PR joins new exact revision")
        print("Runtime:", run(NIX, "--version", env=env).stdout.decode().strip(), run(GIT, "--version", env=env).stdout.decode().strip(), sys.version.split()[0])


if __name__ == "__main__":
    integration()
