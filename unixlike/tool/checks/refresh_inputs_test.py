"""Positive/negative actual-CLI fixtures: INV unixlike/provider-input-refresh-bounded."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


SOURCE = Path(__file__).resolve().parents[1]
NIX = shutil.which("nix")
ENV = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
ENV.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
           GIT_CONFIG_SYSTEM=os.devnull, GIT_ALLOW_PROTOCOL="file", GIT_TERMINAL_PROMPT="0")


def run(*args, env=ENV, success=True):
    result = subprocess.run(args, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if (result.returncode == 0) != success:
        raise AssertionError(f"{args}: exit {result.returncode}\n{result.stdout}\n{result.stderr}")
    return result


def commit(root):
    run("git", "-C", str(root), "add", ".")
    run("git", "-C", str(root), "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
        "commit", "-qm", "fixture")


def url(root):
    return f"git+{root.as_uri()}?ref=main"


def upstream(root, followed=None):
    root.mkdir()
    run("git", "init", "-q", "-b", "main", str(root))
    dependency = f'inputs.a.url = "{url(followed)}";' if followed else ""
    (root / "flake.nix").write_text(f'{{ {dependency} outputs = {{ ... }}: {{ }}; }}\n')
    (root / "payload").write_text("first\n")
    commit(root)


def lock(root):
    return json.loads((root / "flake.lock").read_bytes())


def own(root, name):
    value = lock(root)
    edge = value["nodes"][value["root"]]["inputs"][name]
    return value["nodes"][edge]["locked"]


def snapshot(root):
    return {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in root.rglob("*") if path.is_file()}


def invoke(root, *, env=ENV, success=True, check=False):
    before = snapshot(root)
    result = run(str(root / "tool/refresh-inputs"), *( ["--check"] if check else []),
                 env=env, success=success)
    after = snapshot(root)
    assert {key: value for key, value in before.items() if key != "flake.lock"} == {
        key: value for key, value in after.items() if key != "flake.lock"}
    assert not any(path.name.startswith(".refresh-inputs-") for path in root.iterdir())
    if not success or check:
        assert before == after, result.stderr
    return result


def config(root, entries):
    (root / "flake-refresh-exclusions.json").write_text(json.dumps({"formatVersion": 1, "exclusions": entries}))


def exclude(name):
    return {"input": name, "reason": "controlled fixture"}


with tempfile.TemporaryDirectory(prefix="refresh-fixtures-") as temporary:
    scratch = Path(temporary).resolve()
    a, b, c = (scratch / name for name in ("a", "b", "c"))
    upstream(a)
    upstream(b, a)
    upstream(c)
    root = scratch / "provider"
    (root / "tool").mkdir(parents=True)
    for name in ("refresh-inputs", "refresh_inputs.py"):
        shutil.copy2(SOURCE / name, root / "tool" / name)
    (root / "flake.nix").write_text(
        f'{{ inputs.a.url = "{url(a)}"; inputs.b.url = "{url(b)}"; '
        'inputs.b.inputs.a.follows = "a"; inputs.alias.follows = "a"; '
        'outputs = { ... }: { }; }\n')
    config(root, [])
    run(NIX, "flake", "lock", f"path:{root}")

    # All direct inputs update; a root follows alias is not an update name.
    original_a, original_b = own(root, "a"), own(root, "b")
    for path in (a, b):
        (path / "payload").write_text("second\n")
        commit(path)
    assert "updated flake.lock" in invoke(root).stdout
    assert own(root, "a") != original_a and own(root, "b") != original_b
    assert json.loads(invoke(root, check=True).stdout.splitlines()[0])["selected"] == ["a", "b"]
    print("PASS direct default refresh and read-only inventory")

    # New direct input is selected without a tool/config allowlist change.
    source = root / "flake.nix"
    source.write_text(source.read_text().replace("outputs =", f'inputs.c.url = "{url(c)}"; outputs ='))
    invoke(root)
    assert own(root, "c")["rev"] == run("git", "-C", str(c), "rev-parse", "HEAD").stdout.strip()
    print("PASS new independent direct input")

    config(root, [exclude("b")])
    previous_b, previous_a = own(root, "b"), own(root, "a")
    for path in (a, b):
        (path / "payload").write_text("third\n")
        commit(path)
    invoke(root)
    assert own(root, "b") == previous_b and own(root, "a") != previous_a
    graph = lock(root)
    bnode = graph["nodes"][graph["nodes"][graph["root"]]["inputs"]["b"]]
    assert bnode["inputs"]["a"] == ["a"]
    print("PASS exclusion preserves own source while followed owner updates")

    for entries in ([exclude("missing")], [exclude("a"), exclude("a")], [exclude("alias")],
                    [{"input": "a", "reason": " "}]):
        config(root, entries)
        invoke(root, success=False)
    (root / "flake-refresh-exclusions.json").write_text('{"formatVersion":true,"exclusions":[]}')
    invoke(root, success=False)
    print("PASS unknown duplicate alias and invalid configuration refusal")

    config(root, [exclude("a"), exclude("b"), exclude("c")])
    # Log command selection: real metadata is still run, update must not run.
    wrappers = scratch / "bin"
    wrappers.mkdir()
    log = scratch / "calls"
    wrapper = wrappers / "nix"
    wrapper.write_text(f'#!/bin/sh\nprintf "%s\\n" "$*" >> "{log}"\nexec "{NIX}" "$@"\n')
    wrapper.chmod(0o755)
    wrapped = dict(ENV, PATH=f'{wrappers}:{ENV["PATH"]}')
    before = snapshot(root)
    assert "empty selection" in invoke(root, env=wrapped).stdout
    assert before == snapshot(root) and "flake update" not in log.read_text()
    config(root, [])
    invoke(root)
    before = snapshot(root)
    assert "unchanged" in invoke(root).stdout
    assert before == snapshot(root)
    print("PASS all-excluded no update invocation and unchanged-upstream byte no-op")

    # Excluded new source has no previous lock to preserve.
    source.write_text(source.read_text().replace("outputs =", f'inputs.new.url = "{url(c)}"; outputs ='))
    config(root, [exclude("new")])
    invoke(root, success=False)
    source.write_text(source.read_text().replace(f'inputs.new.url = "{url(c)}"; ', ""))
    config(root, [])

    # Failed real CLI, candidate validation and stale source/config/lock guards.
    source.write_text(source.read_text().replace(url(c), "git+file:///nonexistent-refresh-fixture?ref=main"))
    invoke(root, success=False)
    source.write_text(source.read_text().replace("git+file:///nonexistent-refresh-fixture?ref=main", url(c)))
    print("PASS missing upstream actual Nix failure and excluded-new-source refusal")

    config(root, [exclude("b")])
    tampered = scratch / "excluded-candidate.lock"
    altered = lock(root)
    bkey = altered["nodes"][altered["root"]]["inputs"]["b"]
    altered["nodes"][bkey]["locked"]["rev"] = "0" * 40
    tampered.write_text(json.dumps(altered))
    for mutation in ("candidate", "excluded", "config", "source", "lock", "update-failure", "validation-failure"):
        saved = {name: (root / name).read_bytes() for name in (
            "flake.nix", "flake.lock", "flake-refresh-exclusions.json")}
        # Wrap only the tested boundary. Real update executes first; simulated
        # faults exercise validation/staleness, not upstream success claims.
        wrapper.write_text(f'''#!/bin/sh
if [ "$1 $2" = "flake update" ]; then
  if [ "{mutation}" = update-failure ]; then exit 37; fi
  "{NIX}" "$@" || exit $?
  previous=
  for arg do
    if [ "$previous" = --output-lock-file ]; then candidate=$arg; fi
    previous=$arg
  done
  case "{mutation}" in
    candidate) printf '{{"version":7,"root":"root","nodes":{{"root":{{"inputs":{{}}}}}}}}' > "$candidate" ;;
    excluded) cp "{tampered}" "$candidate" ;;
    config) printf ' ' >> "{root}/flake-refresh-exclusions.json" ;;
    source) printf '\\n' >> "{root}/flake.nix" ;;
    lock) printf ' ' >> "{root}/flake.lock" ;;
  esac
  exit 0
fi
if [ "{mutation}" = validation-failure ]; then
  case " $* " in *' --no-update-lock-file '*) exit 38 ;; esac
fi
exec "{NIX}" "$@"
''')
        result = run(str(root / "tool/refresh-inputs"), env=wrapped, success=False)
        # External stale edits remain; the refresh never overwrites them.
        for name, data in saved.items():
            expected = data + (b" " if mutation in ("config", "lock") and name == {
                "config": "flake-refresh-exclusions.json", "lock": "flake.lock"}[mutation] else
                               b"\n" if mutation == "source" and name == "flake.nix" else b"")
            assert (root / name).read_bytes() == expected, (mutation, name, result.stderr)
            (root / name).write_bytes(data)
        assert not any(path.name.startswith(".refresh-inputs-") for path in root.iterdir())
    print("PASS candidate/excluded-source validation update-failure validation-failure and stale lock/config/source guards")

    fake_python = wrappers / "python3"
    fake_python.write_text('#!/bin/sh\nexit 42\n')
    fake_python.chmod(0o755)
    before = snapshot(root)
    result = run(str(root / "tool/refresh-inputs"), env=wrapped, success=False)
    assert result.returncode == 69 and "functional Python" in result.stderr
    assert before == snapshot(root)
    fake_python.unlink()
    print("PASS nonfunctional interpreter prerequisite refusal")

    # Refuse links rather than guarding only their names while targets mutate.
    for name in ("flake.lock", "flake-refresh-exclusions.json"):
        target = scratch / f"external-{name}"
        original = (root / name).read_bytes()
        target.write_bytes(original)
        (root / name).unlink()
        (root / name).symlink_to(target)
        result = run(str(root / "tool/refresh-inputs"), success=False)
        assert "source symlink is unsupported" in result.stderr
        assert (root / name).is_symlink() and target.read_bytes() == original
        (root / name).unlink()
        (root / name).write_bytes(original)
    for target in (a / "payload", a):
        link = root / "external-source"
        link.symlink_to(target, target_is_directory=target.is_dir())
        result = run(str(root / "tool/refresh-inputs"), success=False)
        assert "source symlink is unsupported" in result.stderr and link.is_symlink()
        link.unlink()
    print("PASS symlink lock/config/file/directory refusal preserves targets")

    # Execute the actual public recipe only against a disposable provider.
    # This proves justfile_directory delegation and caller-CWD independence.
    just = shutil.which("just")
    if just:
        delegated = scratch / "delegated"
        delegated.mkdir()
        shutil.copytree(root, delegated / "unixlike")
        shutil.copy2(SOURCE.parents[1] / "Justfile", delegated / "Justfile")
        before = snapshot(delegated)
        run(just, "--justfile", str(delegated / "Justfile"), "up")
        assert before == snapshot(delegated)
        print("PASS disposable public Justfile up recipe and no-op")
    else:
        print("UNVERIFIED disposable Justfile recipe: just unavailable")

    (root / ".refresh-inputs-running").mkdir()
    before = snapshot(root)
    run(str(root / "tool/refresh-inputs"), success=False)
    assert before == snapshot(root)
    (root / ".refresh-inputs-running").rmdir()
    print("PASS cooperating refresh serialization refusal")

print("PASS refresh-inputs actual local Nix fixtures; only fixture flake.lock changes")
