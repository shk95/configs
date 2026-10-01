"""Seven synthetic proof families; no production authentication or HTTP calls."""
# INV repository/release-control-preview-only
# INV repository/fixture-git-isolation
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zlib

TOOLS = Path(__file__).resolve().parent
WRAPPER = (TOOLS / "release-control").as_posix()
sys.path.insert(0, str(TOOLS / "release-control-package"))
from records import Refusal, blob_identity, canonical, digest, encode, history, parse, require
import engine
import adapter

spec = importlib.util.spec_from_file_location("loader", TOOLS / "release-control-loader.py")
loader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loader)

H = "a" * 40
D = "b" * 40
T = "c" * 40
Z = "0" * 64
X = "a" * 64
Y = "b" * 64
CONFIG = {"enabled": "1", "public-repository": "shk95/configs", "repository": "1",
          "operating-repository": "fixture/operating", "operating-ref": "operations",
          "workflow": "2", "actors": "3", "checks": "gate", "protocol": "3"}
STOP = {"stop": "0", "revision": "0", "reason": "none", "operator": "3"}
OWNER = {"repository": "1", "workflow": "2", "run": "4", "attempt": "1",
         "job": "5", "generation": "1", "operating-head": H}
CANDIDATE = {"candidate-generation": "1", "dev": D, "master": H, "tree": T,
             "rules": X, "tool": X, "baselines": X, "selected": "gate",
             "classification": "patch", "versions": "unixlike:1.0.1",
             "migrations": "-", "approval-required": "1"}
EVIDENCE = ["gate", D, H, T, X, X, "verified", "8", "1", "9", "fixture-check"]
PROTECTION = {"required": "Required checks", "app": "15368", "administrators": True,
              "conversations": True, "force": False, "deletion": False,
              "dev-strict": True, "master-strict": False}


def transcript(mode="approve", candidate=CANDIDATE):
    return {"source": [{"repository": "1", "workflow": "2", "actor": "3", "run": "4",
                       "attempt": "1", "ref": "refs/heads/master", "event": "workflow_dispatch", "mode": mode,
                       "candidate": engine.candidate_digest(candidate)}],
            "checks": [EVIDENCE], "owner": None,
            "observations": {}, "protection": PROTECTION}


def request(mode="preview", candidate=CANDIDATE):
    return {"mode": mode, "actor": "3", "run": "4", "attempt": "1",
            "ref": "refs/heads/master", "candidate": engine.candidate_digest(candidate)}


def event(kind, **values):
    result = {"sequence": "1", "kind": kind, "prior": Z, "batch": X}
    result.update(values)
    return result


def sequence(events):
    previous = Z
    for number, item in enumerate(events, 1):
        item["sequence"], item["prior"] = str(number), previous
        previous = digest(encode(item))
        # Fixture events use the production record grammar before reduction.
        parse(encode(item), "event")
    return events


def start(control=H, manifest=X, approval=X, config=H):
    return event("batch-start", control=control, manifest=manifest,
                 **{"approval-provenance": approval, "config": config, "protocol": "3",
                    "day": "2026-09-30", "run": "4", "attempt": "1", "time": "2026-09-30T00:00:00Z", "approved-master": control, "config-commit": H})


def base_events(approved=True):
    result = [start(), event("claim", **OWNER), event("candidate", **CANDIDATE),
              event("evidence", evidence=[EVIDENCE], **{"evidence-digest": digest(canonical([EVIDENCE]))})]
    if approved:
        fields = {k: CANDIDATE[k] for k in ("candidate-generation", "dev", "master", "tree", "classification", "versions", "migrations")}
        fields.update(actor="3", run="4", attempt="1", ref="refs/heads/master",
                      **{"evidence-digest": digest(canonical([EVIDENCE]))})
        result.append(event("approval", **fields))
    return sequence(copy.deepcopy(result))


def effect(kind, payload, status="intent", observation=None, op_id=X, generation="1"):
    obs = digest(canonical(observation)) if observation is not None else "-"
    remote = adapter.remote_identity(kind, payload, observation) if status == "observed" else "-"
    return event("intent" if status == "intent" and observation is None else "observation",
                 operation=[[op_id, kind, digest(canonical(payload)), generation, status, remote, obs]],
                 payload=canonical(payload).decode("utf-8"))


def run_git(root, *args, data=None):
    result = subprocess.run(["git", "-C", str(root), *args], input=data,
                            capture_output=True, check=True)
    return result.stdout.decode().strip()


def refresh_fixture(**changes):
    value = {"batch": X, "source": D, "base": D, "parent": D, "head": T, "tree": H,
             "before-lock": Y, "lock": X, "utility-source": H, "utility-manifest": X,
             "source-fingerprint": Y, "previous": "-", "branch": adapter.refresh_branch(X)}
    value.update(changes)
    return value


def refresh_checks(candidate):
    return {"head": candidate["head"], "base": candidate["base"], "tree": candidate["tree"],
            "lock": candidate["lock"], "name": "Required checks", "app": "15368", "status": "success"}


def refresh_context_fixture(candidate, proof=None):
    context = {"prepared": candidate, "current-dev": candidate["base"], "checks": refresh_checks(candidate),
               "branch": {"batch": candidate["batch"], "branch": candidate["branch"], "head": candidate["head"]},
               "integration": None,
               "proof": {"head-parents": [candidate["parent"]], "merge-parents": [] if candidate["previous"] == "-" else [candidate["previous"], candidate["base"]],
                         "changed": ["unixlike/flake.lock"], "before-lock": candidate["before-lock"], "lock": candidate["lock"], "before-mode": 0o644, "mode": 0o644}}
    if proof is not None:
        context["proof"] = proof
    return context


def refresh_event(candidate):
    return event("refresh-result", payload=canonical({"status": "changed", "candidate": candidate}).decode())


def refresh_flow(candidate=None, proof=None, prefix=None):
    candidate = candidate or refresh_fixture()
    context = refresh_context_fixture(candidate, proof)
    supplied = transcript()
    supplied["refresh"] = {"revisions": [context], "current": copy.deepcopy(context)}
    events = copy.deepcopy(prefix) if prefix is not None else [start(), event("claim", **OWNER)]
    events.append(refresh_event(candidate))
    payload = dict(candidate, repository="shk95/configs")
    branch = adapter.refresh_operation_id("refresh-branch", payload)
    pr = adapter.refresh_operation_id("refresh-pr", payload)
    branch_observed = {"status": "present", "complete": True, "target": {"candidate": candidate}}
    pr_observed = {"status": "present", "complete": True, "target": {"matches": [{"number": "17", "repository": "shk95/configs", "base-ref": "dev", "state": "open", "candidate": candidate, "checks": refresh_checks(candidate)}]}}
    events += [effect("refresh-branch", payload, op_id=branch), effect("refresh-branch", payload, "observed", branch_observed, branch),
               effect("refresh-pr", payload, op_id=pr), effect("refresh-pr", payload, "observed", pr_observed, pr)]
    supplied["observations"] = {branch: [branch_observed], pr: [pr_observed]}
    return events, supplied, payload, branch, pr, branch_observed, pr_observed


class ControllerProof(unittest.TestCase):
    def refuse(self, callback, *args):
        with self.assertRaises((Refusal, ValueError)):
            callback(*args)

    # INV repository/release-control-preview-only
    def test_ac1_retained_full_bundle_and_old_gate(self):
        actual_manifest = b"format\t1\n" + b"".join(("file\t" + name + "\t" + digest((TOOLS.parent.parent / name).read_bytes()) + "\n").encode() for name in sorted(loader.FILES))
        self.assertEqual((TOOLS.parent.parent / loader.MANIFEST).read_bytes(), actual_manifest)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "public"
            root.mkdir()
            run_git(root, "init", "-q", "-b", "master")
            run_git(root, "config", "user.name", "Fixture")
            run_git(root, "config", "user.email", "fixture@example.invalid")
            run_git(root, "config", "core.hooksPath", str(Path(directory) / "no-hooks"))
            for name in loader.FILES:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(TOOLS.parent.parent / name, path)
                if (TOOLS.parent.parent / name).stat().st_mode & 0o111:
                    path.chmod(0o755)
            def manifest():
                data = b"format\t1\n" + b"".join(("file\t" + name + "\t" + digest((root / name).read_bytes()) + "\n").encode() for name in sorted(loader.FILES))
                (root / loader.MANIFEST).write_bytes(data)
                return digest(data)
            m = manifest()
            run_git(root, "add", ".")
            for name in ("release-preview", "classify"):
                run_git(root, "update-index", "--chmod=+x", "tool/version-control/" + name)
            run_git(root, "commit", "-qm", "fixture base")
            original = run_git(root, "rev-parse", "HEAD")
            # Approved package enters master only via a synthetic two-parent merge.
            run_git(root, "checkout", "-qb", "dev")
            (root / "marker").write_text("old\n")
            run_git(root, "add", ".")
            run_git(root, "commit", "-qm", "fixture old dev")
            run_git(root, "checkout", "-q", "master")
            run_git(root, "merge", "--no-ff", "-qm", "fixture old promotion", "dev")
            old = run_git(root, "rev-parse", "HEAD")
            approved = {"public-repository": "shk95/configs", "control": old,
                        "master": old, "manifest": m, "approval": X, "protocol": "3"}
            scratch = Path(directory) / "old-extract"
            loader.extract(root, approved, scratch)
            for name in loader.FILES:
                self.assertEqual((scratch / name).read_bytes(), (root / name).read_bytes())
            # Invoke the verified retained preview and classifier, not current tools.
            baselines, evidence = Path(directory) / "baselines.tsv", Path(directory) / "evidence.tsv"
            baselines.write_bytes(b"format\t1\n"); evidence.write_bytes(b"format\t1\n")
            sys.path.insert(0, str(scratch / loader.ROOT))
            retained_spec = importlib.util.spec_from_file_location("retained_engine", scratch / loader.ROOT / "engine.py")
            retained_engine = importlib.util.module_from_spec(retained_spec)
            retained_spec.loader.exec_module(retained_engine)
            replay = retained_engine.retained_replay(root, old, old, old, baselines, evidence)
            self.assertEqual(replay["decision"], "no-op")
            sys.path.pop(0)
            # New approved package weakens both the engine entry and its preview rules.
            run_git(root, "checkout", "-q", "dev")
            (root / loader.ROOT / "main.py").write_bytes(b"import sys\nsys.stdout.buffer.write(b'new gate waived\\n')\n")
            (root / "tool/version-control/release-preview.rules").write_text("format\t1\n")
            newer_manifest = manifest()
            run_git(root, "add", ".")
            run_git(root, "commit", "-qm", "fixture gate waiver")
            run_git(root, "checkout", "-q", "master")
            run_git(root, "merge", "--no-ff", "-qm", "fixture new promotion", "dev")
            newer = run_git(root, "rev-parse", "HEAD")
            approved["master"] = newer
            retained = Path(directory) / "retained"
            loader.extract(root, approved, retained)
            self.assertEqual((retained / "tool/version-control/release-preview.rules").read_bytes(), (scratch / "tool/version-control/release-preview.rules").read_bytes())
            self.assertEqual((retained / loader.ROOT / "main.py").read_bytes(), (scratch / loader.ROOT / "main.py").read_bytes())
            new_assertion = dict(approved, control=newer, manifest=newer_manifest)
            fresh = Path(directory) / "fresh"
            loader.extract(root, new_assertion, fresh)
            weakened = subprocess.run([sys.executable, "-I", str(fresh / loader.ROOT / "main.py")], capture_output=True, check=True)
            self.assertEqual(weakened.stdout, b"new gate waived\n")
            # Same valid record grammar requests unvalidated promotion: old gate refuses.
            operating = Path(directory) / "operating"
            for folder in ("config", "control", "history", "current"):
                (operating / folder).mkdir(parents=True)
            config_data = encode(CONFIG)
            (operating / "config/operating.tsv").write_bytes(config_data)
            (operating / "control/stop.tsv").write_bytes(encode(STOP))
            merge = {"repository": "shk95/configs", "number": "7", "dev": D, "master": H, "tree": T}
            invalid_gate = sequence([start(old, m, X, blob_identity(config_data)), event("claim", **OWNER), event("candidate", **CANDIDATE), effect("merge", merge)])
            for n, item in enumerate(invalid_gate, 1):
                (operating / "history" / f"{n:012d}.tsv").write_bytes(encode(item))
            assertion_file = Path(directory) / "approved.tsv"; assertion_file.write_bytes(encode(approved))
            request_file = Path(directory) / "request.tsv"; request_file.write_bytes(encode(request()))
            transcript_file = Path(directory) / "transcript.json"; transcript_file.write_bytes(canonical(transcript("preview")))
            old_result = subprocess.run([sys.executable, "-I", str(retained / loader.ROOT / "main.py"), str(operating), str(transcript_file), str(request_file), str(assertion_file)], capture_output=True)
            self.assertNotEqual(old_result.returncode, 0)
            self.refuse(engine.reduce, invalid_gate, CONFIG, transcript())
            # Required evidence present does not let newer rules waive old approval.
            missing_approval = base_events(False)
            missing_approval[0] = start(old, m, X, blob_identity(config_data))
            missing_approval.append(effect("merge", merge))
            missing_approval = sequence(missing_approval)
            with self.assertRaisesRegex(Refusal, "missing-exact-approval"):
                retained_engine.reduce(missing_approval, CONFIG, transcript())
            for path in (operating / "history").iterdir():
                path.unlink()
            for n, item in enumerate(missing_approval, 1):
                (operating / "history" / f"{n:012d}.tsv").write_bytes(encode(item))
            old_approval_result = subprocess.run([sys.executable, "-I", str(retained / loader.ROOT / "main.py"), str(operating), str(transcript_file), str(request_file), str(assertion_file)], capture_output=True)
            self.assertNotEqual(old_approval_result.returncode, 0)
            # Identical missing gate inputs accepted by the newer deliberately weak engine.
            new_result = subprocess.run([sys.executable, "-I", str(fresh / loader.ROOT / "main.py"), str(operating), str(transcript_file), str(request_file), str(assertion_file)], capture_output=True)
            self.assertEqual(new_result.returncode, 0)
            # Full operator/loader path preserves old refusal after newer master exists.
            command = [WRAPPER, "preview", "--fixture-inputs", "--bundle-repository", str(root), "--approved", str(assertion_file), "--operating", str(operating), "--transcript", str(transcript_file), "--request", str(request_file)]
            refused = subprocess.run(["sh"] + command, capture_output=True)
            self.assertNotEqual(refused.returncode, 0)
            self.assertEqual(refused.stderr, b"release-control: refused" + os.linesep.encode("ascii"))
            # Remove invalid events to demonstrate the complete quiet safe preview path.
            for path in (operating / "history").iterdir():
                path.unlink()
            (operating / "current/index.tsv").write_bytes(engine.index(engine.initial(), Z))
            request_file.write_bytes(encode(request(candidate=None)))
            success = subprocess.run(["sh"] + command, capture_output=True)
            self.assertEqual(success.returncode, 0, success.stderr)
            self.assertEqual(json.loads(success.stdout)["proposed"], 0)
            self.assertEqual(run_git(root, "rev-parse", "HEAD"), newer)
            self.refuse(loader.extract, root, dict(approved, control=original), Path(directory) / "ancestor")
            self.refuse(loader.extract, root, dict(approved, manifest=Y), Path(directory) / "tamper")
            self.refuse(loader.approved, encode(dict(approved, protocol="4")))
            self.refuse(loader.approved, encode(dict(approved, **{"public-repository": "fixture/other"})))
            # Missing closure entry, even with its newly asserted manifest digest, refuses.
            raw = (root / loader.MANIFEST).read_bytes().splitlines(keepends=True)
            (root / loader.MANIFEST).write_bytes(b"".join(raw[:-1]))
            run_git(root, "checkout", "-q", "dev")
            run_git(root, "add", ".")
            run_git(root, "commit", "-qm", "fixture incomplete manifest")
            run_git(root, "checkout", "-q", "master")
            run_git(root, "merge", "--no-ff", "-qm", "fixture incomplete promotion", "dev")
            incomplete = run_git(root, "rev-parse", "HEAD")
            self.refuse(loader.extract, root, dict(approved, master=incomplete, control=incomplete,
                        manifest=digest((root / loader.MANIFEST).read_bytes())), Path(directory) / "incomplete")

    # INV repository/release-control-preview-only
    def test_ac2_original_bytes_and_projection(self):
        literal = dict(STOP, reason='유니코드 \\" literal $(never) `never`')
        self.assertEqual(parse(encode(literal), "stop"), literal)
        good = encode(STOP)
        for bad in [good[:-1], good + b"\n", good.replace(b"none", b"\xff"),
                    good.replace(b"none", b"\x00"), good.replace(b"none", b"\r"),
                    good.replace(b"none", b"\x1b"), good + b"reason\tduplicate\n",
                    good + b"unknown\tvalue\n", good.replace(b"format\t1", b"format\t2"),
                    good.replace(b"revision\t0", b"revision\t00")]:
            self.refuse(parse, bad, "stop")
        self.refuse(parse, encode(event("unknown")), "event")
        bad_tuple = base_events()[3]
        bad_tuple["evidence"] = [EVIDENCE[:-1]]
        self.refuse(parse, encode(bad_tuple), "event")
        initial_release = event("candidate", **CANDIDATE)
        initial_release["release"] = [["unixlike", "1.0.0", D, "-", H, H, X]]
        parse(encode(initial_release), "event")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            events = sequence(base_events())
            for n, item in enumerate(events, 1):
                (root / f"{n:012d}.tsv").write_bytes(encode(item))
            actual, prior = history(root)
            state = engine.reduce(actual, CONFIG, transcript())
            projected = engine.index(state, prior)
            parse(projected, "index")
            self.assertEqual(projected, engine.index(engine.reduce(actual, CONFIG, transcript()), prior))
            (root / "000000000002.tsv").rename(root / "000000000009.tsv")
            self.refuse(history, root)
        self.refuse(engine.reduce, sequence([event("complete")]), CONFIG, transcript())
        second = start(); second["batch"] = Y
        self.refuse(engine.reduce, sequence([start(), event("complete"), second]), CONFIG, transcript())

    # INV repository/release-control-preview-only
    def test_ac3_requests_evidence_and_invalidation(self):
        self.assertEqual(engine.reduce(base_events(), CONFIG, transcript())["stage"], "approved")
        for key, value in [("actor", "99"), ("attempt", "2"), ("ref", "refs/heads/dev"),
                           ("run", "99"), ("workflow", "99"), ("event", "push")]:
            forged = transcript(); forged["source"][0][key] = value
            self.refuse(engine.reduce, base_events(), CONFIG, forged)
        for status in ("unverified", "failed"):
            events = base_events(); events[3]["evidence"][0][6] = status
            self.refuse(engine.reduce, sequence(events), CONFIG, transcript())
        events = base_events(); events[3]["evidence"] = []
        self.refuse(engine.reduce, sequence(events), CONFIG, transcript())
        events = base_events(); events.append(event("candidate", **dict(CANDIDATE, dev=T, **{"candidate-generation": "2"})))
        state = engine.reduce(sequence(events), CONFIG, transcript())
        self.assertEqual(state["evidence"], []); self.assertIsNone(state["approval"])
        self.refuse(adapter.authenticate, dict(transcript(), source={}), CONFIG, request("approve"), engine.candidate_digest(CANDIDATE))
        self.refuse(parse, encode({k: v for k, v in request().items() if k != "candidate"}), "request")
        self.refuse(adapter.authenticate, dict(transcript(), source={"status": "canceled"}), CONFIG, request("approve"), engine.candidate_digest(CANDIDATE))
        major = dict(CANDIDATE, classification="major", **{"approval-required": "0"})
        events = base_events(False); events[2].update(major)
        merge = {"repository": "shk95/configs", "number": "7", "dev": D, "master": H, "tree": T}
        with self.assertRaisesRegex(Refusal, "missing-exact-approval"):
            engine.reduce(sequence(events + [effect("merge", merge)]), CONFIG, transcript(candidate=major))
        for classification in ("major-unknown", "", "no-op"):
            unsupported = base_events(False); unsupported[2]["classification"] = classification
            self.refuse(sequence, unsupported)
        migration = dict(CANDIDATE, migrations="data", **{"approval-required": "0"})
        migrating = base_events(False); migrating[2].update(migration)
        self.refuse(engine.reduce, sequence(migrating + [effect("merge", merge)]), CONFIG, transcript(candidate=migration))
        approved_migration = base_events(); approved_migration[2].update(migration)
        approved_migration[4]["migrations"] = "data"
        self.assertEqual(engine.reduce(sequence(approved_migration + [effect("merge", merge)]), CONFIG, transcript(candidate=migration))["stage"], "approved")

    # INV repository/release-control-preview-only
    def test_ac4_writer_wait_termination_stop(self):
        observed = {"owner": OWNER, "latest-attempt": "1", "jobs": {"5": "terminal"}, "complete": True, "status": "terminal"}
        self.assertTrue(adapter.takeover(OWNER, observed))
        for altered in [dict(observed, complete=False), dict(observed, status="202"),
                        dict(observed, **{"latest-attempt": "2"}), dict(observed, jobs={}),
                        dict(observed, status="timeout")]:
            self.refuse(adapter.takeover, OWNER, altered)
        events = base_events(); events.append(event("claim", **dict(OWNER, generation="2", run="10")))
        self.assertEqual(engine.reduce(sequence(events), CONFIG, dict(transcript(), owner=observed))["generation"], "2")
        events = base_events(); events.append(event("retry-wait", minutes="5", transient="1", reason="transient"))
        self.assertEqual(engine.reduce(sequence(events), CONFIG, transcript())["stage"], "waiting")
        events.append(event("stop-observed", revision="1", reason="operator"))
        events.append(event("claim", **dict(OWNER, generation="2")))
        self.refuse(engine.reduce, sequence(events), CONFIG, dict(transcript(), owner=observed))
        # An accepted intent can finish after stop; retain observation, forbid next intent.
        merge = {"repository": "shk95/configs", "number": "7", "dev": D, "master": H, "tree": T}
        applied = {"status": "present", "target": {"merged": True, "commit": "d" * 40, "parents": [H, D], "tree": T, "source": D}, "complete": True}
        events = base_events() + [effect("merge", merge), event("stop-observed", revision="1", reason="operator"), effect("merge", merge, "observed", applied)]
        proof = transcript(); proof["observations"][X] = [applied]
        stopped = engine.reduce(sequence(events), CONFIG, proof)
        self.assertEqual(stopped["stage"], "stopped")
        self.assertEqual(stopped["operations"][X]["state"], "observed")
        self.refuse(engine.reduce, sequence(copy.deepcopy(events) + [effect("merge", merge, op_id=Y)]), CONFIG, proof)
        # Current preview and historical approval observations coexist without guessing inputs.
        proof["source"] += transcript("preview")["source"]
        adapter.authenticate(proof, CONFIG, request(), engine.candidate_digest(CANDIDATE))
        cancel = {"repository": "shk95/configs", "run": OWNER["run"], "attempt": OWNER["attempt"], "workflow": OWNER["workflow"], "jobs": OWNER["job"]}
        self.assertEqual(engine.reduce(sequence(base_events() + [effect("cancel", cancel, op_id=Y)]), CONFIG, transcript())["operations"][Y]["state"], "intent")
        for field in ("run", "attempt", "workflow", "jobs"):
            self.refuse(engine.reduce, sequence(base_events() + [effect("cancel", dict(cancel, **{field: "999"}), op_id=Y)]), CONFIG, transcript())
        terminal_cancel = {"status": "present", "complete": True, "target": {**{k: v for k, v in cancel.items() if k != "repository"}, "latest-attempt": cancel["attempt"], "terminal": True}}
        cancel_proof = transcript(); cancel_proof["observations"][Y] = [terminal_cancel]
        self.assertEqual(engine.reduce(sequence(base_events() + [effect("cancel", cancel, op_id=Y), effect("cancel", cancel, "observed", terminal_cancel, Y)]), CONFIG, cancel_proof)["operations"][Y]["state"], "observed")

    # INV repository/release-control-preview-only
    def test_ac5_endpoint_reconciliation_gaps(self):
        record = {"repository": "fixture/operating", "parent": H, "commit": D, "event": X, "index": Y}
        observed = {"status": "present", "complete": True, "target": {"history": [{k: v for k, v in record.items() if k != "repository"}, {"parent": D, "commit": T, "event": "c" * 64, "index": "d" * 64}], "head": T}}
        self.assertEqual(adapter.reconcile("record", record, observed), "applied")
        self.assertEqual(adapter.reconcile("record", record, {"status": "absent", "target": {"parent": H}, "complete": True}), "absent")
        self.refuse(adapter.reconcile, "record", record, {"status": "absent", "target": {"parent": T}, "complete": True})
        self.refuse(adapter.reconcile, "record", record, dict(observed, complete=False))
        conflict = copy.deepcopy(observed); conflict["target"]["history"][0]["index"] = X
        self.assertEqual(adapter.reconcile("record", record, conflict), "conflict")
        # A matching first row cannot hide contradictory later history or a stale head.
        duplicate = copy.deepcopy(observed); duplicate["target"]["history"].append(duplicate["target"]["history"][0])
        self.refuse(adapter.reconcile, "record", record, duplicate)
        wrong_chain = copy.deepcopy(observed); wrong_chain["target"]["history"][1]["parent"] = H
        self.refuse(adapter.reconcile, "record", record, wrong_chain)
        stale_head = copy.deepcopy(observed); stale_head["target"]["head"] = H
        self.refuse(adapter.reconcile, "record", record, stale_head)
        pr = {"repository": "shk95/configs", "head": "dev", "base": "master", "dev": D, "master": H, "body-operation": X}
        self.assertEqual(adapter.reconcile("pr", pr, {"status": "present", "target": {"matches": [{"number": "7", "payload": pr}]}, "complete": True}), "applied")
        self.assertEqual(adapter.reconcile("pr", pr, {"status": "present", "target": {"matches": [pr, pr]}, "complete": True}), "conflict")
        merge = {"repository": "shk95/configs", "number": "7", "dev": D, "master": H, "tree": T}
        matching = {"status": "present", "target": {"merged": True, "commit": "d" * 40, "parents": [H, D], "tree": T, "source": D}, "complete": True}
        self.assertEqual(adapter.reconcile("merge", merge, matching), "applied")
        wrong = copy.deepcopy(matching); wrong["target"]["parents"] = [T, D]
        self.assertEqual(adapter.reconcile("merge", merge, wrong), "conflict")
        missing_sha = copy.deepcopy(matching); del missing_sha["target"]["commit"]
        self.refuse(adapter.reconcile, "merge", merge, missing_sha)
        wrong_remote = effect("merge", merge, "observed", matching)
        wrong_remote["operation"][0][5] = "unsafe remote identity"
        self.refuse(parse, encode(wrong_remote), "event")
        events = base_events(); intent = effect("merge", merge); events.append(intent)
        events.append(effect("merge", merge, "observed", matching))
        proof = transcript(); proof["observations"][X] = [matching]
        self.assertEqual(engine.reduce(sequence(events), CONFIG, proof)["stage"], "promoted")
        changed = dict(merge, tree=H)
        events.append(effect("merge", changed))
        self.refuse(engine.reduce, sequence(events), CONFIG, proof)
        # Replay both a timed-out observation and its later exact target reconciliation.
        unknown = {"status": "unknown", "target": {}, "complete": True}
        events = base_events() + [effect("merge", merge), effect("merge", merge, "unknown", unknown)]
        proof = transcript(); proof["observations"][X] = [unknown, matching]
        self.assertEqual(engine.reduce(sequence(events), CONFIG, proof)["stage"], "blocked")
        self.refuse(engine.reduce, sequence(copy.deepcopy(events) + [effect("merge", merge, op_id=Y)]), CONFIG, proof)
        events.append(effect("merge", merge, "observed", matching))
        self.assertEqual(engine.reduce(sequence(events), CONFIG, proof)["stage"], "promoted")
        other_commit = copy.deepcopy(matching); other_commit["target"]["commit"] = "e" * 40
        changed_identity = copy.deepcopy(proof); changed_identity["observations"][X].append(other_commit)
        self.refuse(engine.reduce, sequence(copy.deepcopy(events) + [effect("merge", merge, "observed", other_commit)]), CONFIG, changed_identity)
        replacement = dict(CANDIDATE, dev=T, versions="unixlike:1.0.2", **{"candidate-generation": "2"})
        unresolved = base_events() + [effect("merge", merge), effect("merge", merge, "unknown", unknown)]
        self.refuse(engine.reduce, sequence(copy.deepcopy(unresolved) + [event("candidate", **replacement)]), CONFIG, proof)
        no_merge = {"status": "absent", "target": {}, "complete": True}
        changed_candidate = copy.deepcopy(unresolved) + [effect("merge", merge, "intent", no_merge), event("candidate", **replacement)]
        replacement_proof = transcript(); replacement_proof["observations"][X] = [unknown, no_merge, matching]
        changed_state = engine.reduce(sequence(copy.deepcopy(changed_candidate)), CONFIG, replacement_proof)
        self.assertEqual(changed_state["operations"][X]["state"], "superseded")
        self.assertFalse([o for o in changed_state["operations"].values() if o["state"] == "intent"])
        self.refuse(engine.reduce, sequence(copy.deepcopy(changed_candidate) + [effect("merge", merge, "observed", matching)]), CONFIG, replacement_proof)
        self.refuse(engine.reduce, sequence(copy.deepcopy(changed_candidate) + [effect("merge", merge)]), CONFIG, replacement_proof)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for folder in ("config", "control", "history", "current"):
                (root / folder).mkdir()
            data = encode(CONFIG); changed_candidate[0]["config"] = blob_identity(data)
            packet = sequence(copy.deepcopy(changed_candidate)); state = engine.reduce(packet, CONFIG, replacement_proof)
            (root / "config/operating.tsv").write_bytes(data)
            (root / "control/stop.tsv").write_bytes(encode(STOP))
            for n, item in enumerate(packet, 1):
                (root / "history" / f"{n:012d}.tsv").write_bytes(encode(item))
            (root / "current/index.tsv").write_bytes(engine.index(state, digest(encode(packet[-1]))))
            replacement_proof["source"] += transcript("preview", replacement)["source"]
            self.assertEqual(engine.preview(root, replacement_proof, request(candidate=replacement), {"control": H, "manifest": X, "approval": X, "master": H})["proposed"], 0)
        # Lost operating update confirmed absent at the exact old parent can reload/retry.
        absent = {"status": "absent", "target": {"parent": H}, "complete": True}
        events = base_events() + [effect("record", record), effect("record", record, "unknown", unknown), effect("record", record, "intent", absent)]
        proof = transcript(); proof["observations"][X] = [unknown, absent]
        state = engine.reduce(sequence(events), CONFIG, proof)
        self.assertEqual(state["stage"], "approved")
        self.assertEqual(state["operations"][X]["state"], "intent")
        # Applied operating advancement reloads the parent for the next proposal.
        events = base_events() + [effect("record", record), effect("record", record, "observed", observed)]
        proof = transcript(); proof["observations"][X] = [observed]
        state = engine.reduce(sequence(events), CONFIG, proof)
        self.assertEqual(state["owner"]["operating-head"], T)
        self.refuse(engine.reduce, sequence(copy.deepcopy(events) + [effect("record", record, op_id=Y)]), CONFIG, proof)
        advanced = dict(record, parent=T, commit="e" * 40, event=Y)
        state = engine.reduce(sequence(copy.deepcopy(events) + [effect("record", advanced, op_id=Y)]), CONFIG, proof)
        self.assertEqual(state["operations"][Y]["state"], "intent")
        advanced_observation = {"status": "present", "complete": True, "target": {"history": observed["target"]["history"] + [{k: v for k, v in advanced.items() if k != "repository"}], "head": advanced["commit"]}}
        proof["observations"][Y] = [advanced_observation]
        advanced_events = copy.deepcopy(events) + [effect("record", advanced, op_id=Y), effect("record", advanced, "observed", advanced_observation, Y)]
        preserved = engine.reduce(sequence(copy.deepcopy(advanced_events)), CONFIG, proof)
        self.assertEqual(preserved["owner"]["operating-head"], advanced["commit"])
        snapshot = copy.deepcopy(preserved)
        self.refuse(engine.reduce, sequence(copy.deepcopy(advanced_events) + [effect("record", record, "observed", observed)]), CONFIG, proof)
        self.assertEqual(preserved, snapshot)
        self.assertEqual(preserved["operations"][X]["state"], "observed")
        self.assertEqual(preserved["operations"][Y]["state"], "observed")
        # A same-identity later read may advance along the complete known chain.
        later = copy.deepcopy(advanced_observation)
        later["target"]["history"].append({"parent": advanced["commit"], "commit": "f" * 40, "event": "f" * 64, "index": "e" * 64})
        later["target"]["head"] = "f" * 40
        forked = copy.deepcopy(observed)
        forked["target"]["history"].append({"parent": T, "commit": "f" * 40, "event": "f" * 64, "index": "e" * 64})
        forked["target"]["head"] = "f" * 40
        proof["observations"][X] += [later, forked]
        self.refuse(engine.reduce, sequence(copy.deepcopy(advanced_events) + [effect("record", record, "observed", forked)]), CONFIG, proof)
        self.assertEqual(engine.reduce(sequence(copy.deepcopy(advanced_events) + [effect("record", record, "observed", later)]), CONFIG, proof)["owner"]["operating-head"], "f" * 40)

    # INV repository/release-control-preview-only
    def test_ac6_immutable_publication_and_conflicts(self):
        annotation = "Fixed-Annotation: fixture\nSecond-Line: immutable\n"
        tag = {"repository": "shk95/configs", "tag": "unixlike-v1.0.1", "source": D,
               "annotation": annotation, "tagger-time": "2026-09-30T00:00:00Z", "tagger-name": "Fixture", "tagger-email": "fixture@example.invalid", "initial-run": "4", "object": H}
        tag["object"] = adapter.tag_identity(tag)
        for kind, payload in [("tag-object", tag), ("tag-ref", {k: tag[k] for k in ("repository", "tag", "object")})]:
            matching = {"status": "present", "target": payload, "complete": True}
            self.assertEqual(adapter.reconcile(kind, payload, matching), "applied")
            for key in payload:
                changed = dict(payload); changed[key] += "changed"
                self.assertEqual(adapter.reconcile(kind, payload, dict(matching, target=changed)), "conflict")
            self.assertEqual(adapter.reconcile(kind, payload, {"status": "absent", "target": {}, "complete": True}), "absent")
        merge = {"repository": "shk95/configs", "number": "7", "dev": D, "master": H, "tree": T}
        matching = {"status": "present", "target": {"merged": True, "commit": "d" * 40, "parents": [H, D], "tree": T, "source": D}, "complete": True}
        events = base_events(); events[2]["release"] = [["unixlike", "1.0.1", D, H, H, H, Y]]
        events.extend([effect("merge", merge), effect("merge", merge, "observed", matching)])
        proof = transcript(); proof["observations"][X] = [matching]
        events.append(event("candidate", **dict(CANDIDATE, **{"candidate-generation": "2"})))
        self.refuse(engine.reduce, sequence(events), CONFIG, proof)
        # Two domains: Unix-like tag is immutable success, Windows ref is missing.
        windows = dict(tag, tag="windows-v1.0.1")
        windows["object"] = adapter.tag_identity(windows)
        release_rows = [["unixlike", "1.0.1", D, H, blob_identity(annotation.encode()), tag["object"], Y],
                        ["windows", "1.0.1", D, H, blob_identity(annotation.encode()), windows["object"], "d" * 64]]
        unix_ref_id, windows_ref_id = map(engine.publication_ref_id, release_rows)
        events = base_events(); events[2]["release"] = release_rows
        publication_candidate = dict(CANDIDATE, versions="unixlike:1.0.1,windows:1.0.1")
        events[2]["versions"] = publication_candidate["versions"]
        events[4]["versions"] = publication_candidate["versions"]
        events.extend([effect("merge", merge), effect("merge", merge, "observed", matching)])
        proof = transcript(candidate=publication_candidate); proof["observations"][X] = [matching]
        for payload, object_id, ref_id in [(tag, Y, unix_ref_id), (windows, "d" * 64, windows_ref_id)]:
            observed = {"status": "present", "complete": True, "target": payload}
            events.extend([effect("tag-object", payload, op_id=object_id), effect("tag-object", payload, "observed", observed, object_id)])
            proof["observations"][object_id] = [observed]
            ref = {k: payload[k] for k in ("repository", "tag", "object")}
            events.append(effect("tag-ref", ref, op_id=ref_id))
            if payload == tag:
                present = {"status": "present", "complete": True, "target": ref}
                events.append(effect("tag-ref", ref, "observed", present, ref_id))
                proof["observations"][ref_id] = [present]
        state = engine.reduce(sequence(events), CONFIG, proof)
        self.assertEqual(state["operations"][unix_ref_id]["state"], "observed")
        self.assertEqual([k for k, op in state["operations"].items() if op["state"] == "intent"], [windows_ref_id])
        # Repeating success or changing any fixed publication bytes refuses.
        fixed_ref = {k: tag[k] for k in ("repository", "tag", "object")}
        self.refuse(engine.reduce, sequence(copy.deepcopy(events) + [effect("tag-ref", fixed_ref, op_id=unix_ref_id)]), CONFIG, proof)
        self.refuse(engine.reduce, sequence(copy.deepcopy(events) + [effect("tag-ref", fixed_ref, op_id="f" * 64)]), CONFIG, proof)
        absent_ref = {"status": "absent", "target": {}, "complete": True}
        unknown_ref = {"status": "unknown", "target": {}, "complete": True}
        conflict_ref = {"status": "present", "target": dict(fixed_ref, object=H), "complete": True}
        immutable_proof = copy.deepcopy(proof)
        immutable_proof["observations"][unix_ref_id] += [absent_ref, unknown_ref, conflict_ref]
        for status, observation in [("intent", absent_ref), ("unknown", unknown_ref), ("conflict", conflict_ref)]:
            self.refuse(engine.reduce, sequence(copy.deepcopy(events) + [effect("tag-ref", fixed_ref, status, observation, unix_ref_id)]), CONFIG, immutable_proof)
        repeated = engine.reduce(sequence(copy.deepcopy(events) + [effect("tag-ref", fixed_ref, "observed", proof["observations"][unix_ref_id][0], unix_ref_id)]), CONFIG, proof)
        self.assertEqual(repeated["operations"][unix_ref_id]["state"], "observed")
        self.assertEqual(repeated["stage"], "publishing")
        early = base_events(); early[2]["release"] = [release_rows[0]]
        early += [effect("merge", merge), effect("merge", merge, "observed", matching), effect("tag-object", tag, op_id=Y)]
        early_proof = transcript(); early_proof["observations"][X] = [matching]
        self.refuse(engine.reduce, sequence(early + [effect("tag-ref", fixed_ref, op_id=unix_ref_id)]), CONFIG, early_proof)
        for key, value in [("source", T), ("annotation", "changed"), ("tagger-time", "2026-10-01T00:00:00Z"), ("initial-run", "10"), ("tag", "unixlike-v1.0.2")]:
            changed = dict(tag, **{key: value})
            self.refuse(engine.reduce, sequence(copy.deepcopy(events) + [effect("tag-object", changed, op_id=Y)]), CONFIG, proof)
        self.refuse(engine.reduce, sequence(copy.deepcopy(events) + [event("complete")]), CONFIG, proof)
        missing = {k: windows[k] for k in ("repository", "tag", "object")}
        observed = {"status": "present", "complete": True, "target": missing}
        proof["observations"][windows_ref_id] = [observed]
        events.extend([effect("tag-ref", missing, "observed", observed, windows_ref_id), event("complete")])
        completed = engine.reduce(sequence(events), CONFIG, proof)
        self.assertEqual(completed["stage"], "complete")
        handover = copy.deepcopy(events[:-1]) + [event("claim", **dict(OWNER, generation="2", run="10"))]
        handover_proof = copy.deepcopy(proof)
        handover_proof["owner"] = {"owner": OWNER, "latest-attempt": "1", "jobs": {OWNER["job"]: "terminal"}, "complete": True, "status": "terminal"}
        self.assertEqual(engine.reduce(sequence(copy.deepcopy(handover)), CONFIG, handover_proof)["owner"]["run"], "10")
        for replay_id in (unix_ref_id, "f" * 64):
            self.refuse(engine.reduce, sequence(copy.deepcopy(handover) + [effect("tag-ref", fixed_ref, op_id=replay_id, generation="2")]), CONFIG, handover_proof)
        mismatched = base_events(); mismatched[2]["release"] = [["unixlike", "1.0.2", D, H, H, H, X]]
        self.refuse(engine.reduce, sequence(mismatched), CONFIG, transcript())
        # Stop/resume after promotion cannot reopen selection or lose partial success.
        merge_only = base_events() + [effect("merge", merge), effect("merge", merge, "observed", matching), event("stop-observed", revision="1", reason="operator"), event("resume", actor="3", run="4", attempt="1", ref="refs/heads/master")]
        proof = transcript(); proof["source"] += transcript("resume")["source"]
        proof["observations"][X] = [matching]
        resumed = engine.reduce(sequence(merge_only), CONFIG, proof)
        self.assertEqual(resumed["stage"], "promoted")
        self.assertTrue(resumed["frozen"])
        self.refuse(engine.reduce, sequence(copy.deepcopy(merge_only) + [event("candidate", **dict(CANDIDATE, **{"candidate-generation": "2"}))]), CONFIG, proof)
        self.refuse(engine.reduce, sequence(copy.deepcopy(merge_only) + [effect("merge", merge, op_id=Y)]), CONFIG, proof)

    # INV repository/release-control-preview-only
    # INV repository/fixture-git-isolation
    def test_ac7_inert_runtime_isolation_and_timing(self):
        self.assertEqual(loader.runtime_environment({"PATH": "fixture-tools", "GH_TOKEN": "fixture-private-value", "GITHUB_TOKEN": "fixture-private-value", "PYTHONPATH": "candidate-code", "GIT_DIR": "candidate-repo"}), {"PATH": "fixture-tools"})
        for native, expected in [("0", 69), ("1", 1)]:
            env = dict(os.environ, CONFIGS_CONTROLLER_PYTHON="fixture-missing-python-runtime", REQUIRE_NATIVE=native)
            absent = subprocess.run(["sh", WRAPPER, "--help"], env=env, capture_output=True)
            self.assertEqual(absent.returncode, expected)
        invalid = subprocess.run(["sh", WRAPPER, "private-unrecognized-value"], capture_output=True)
        self.assertEqual(invalid.returncode, 64)
        self.assertNotIn(b"private-unrecognized-value", invalid.stderr)
        self.assertEqual(adapter.opportunity(5, "ready"), "not-due")
        self.assertEqual(adapter.opportunity(6, "waiting"), "wait")
        self.assertEqual(adapter.opportunity(7, "waiting"), "reconcile")
        events = base_events()
        for minutes in ("5", "15", "30"):
            events.append(event("retry-wait", minutes=minutes, transient="1", reason="transient"))
        self.assertEqual(engine.reduce(sequence(events), CONFIG, transcript())["retry"], 3)
        events.append(event("retry-wait", minutes="30", transient="1", reason="transient"))
        self.refuse(engine.reduce, sequence(events), CONFIG, transcript())
        self.refuse(engine.reduce, sequence(base_events() + [event("retry-wait", minutes="5", transient="0", reason="permanent")]), CONFIG, transcript())
        with tempfile.TemporaryDirectory(prefix="space fixture ") as directory:
            root = Path(directory)
            for name in ("config", "control", "history", "current"):
                (root / name).mkdir()
            (root / "config/operating.tsv").write_bytes(encode(dict(CONFIG, enabled="0")))
            self.assertIsNone(engine.preview(root, {}, request(), {}))
            (root / "config/operating.tsv").write_bytes(encode(dict(CONFIG, actors="-")))
            self.refuse(engine.preview, root, {}, request(), {})
            (root / "config/operating.tsv").write_bytes(encode(CONFIG))
            (root / "control/stop.tsv").write_bytes(encode(STOP))
            initial = engine.initial()
            (root / "current/index.tsv").write_bytes(engine.index(initial, Z))
            summary = engine.preview(root, {}, request(candidate=None), {})
            self.assertEqual(summary, {"outcome": "preview", "stage": "empty", "proposed": 0})
            self.assertNotIn("fixture/operating", json.dumps(summary))
            # Identical duplicate signals leave the same index and public summary.
            original_index = (root / "current/index.tsv").read_bytes()
            self.assertEqual(engine.preview(root, {}, request(candidate=None), {}), summary)
            self.assertEqual((root / "current/index.tsv").read_bytes(), original_index)
            (root / "current/index.tsv").write_bytes(engine.index(dict(initial, stage="wrong"), Z))
            self.refuse(engine.preview, root, {}, request(candidate=None), {})
            run_git(root, "init", "-q", "-b", "fixture")
            # File-only transport succeeds; inherited external routing is refused.
            receiver = root / "receiver.git"
            run_git(root, "init", "--bare", "-q", str(receiver))
            clone = root / "local-clone"
            subprocess.run(["git", "clone", "-q", str(receiver), str(clone)], check=True, capture_output=True)
            denied = subprocess.run(["git", "ls-remote", "https://fixture.invalid/never"], capture_output=True)
            self.assertNotEqual(denied.returncode, 0)
            self.assertIn(b"not allowed", denied.stderr)
        workflow = (TOOLS.parent.parent / ".github/workflows/release-control.yml").read_text()
        for forbidden in ("schedule:", "secrets.", "environment:", "workflow_run:"):
            self.assertNotIn(forbidden, workflow)
        self.assertIn("cancel-in-progress: false", workflow)
        self.assertIn("timeout-minutes: 15", workflow)
        self.assertIn("options: [preview]", workflow)
        self.assertIn("github.ref == 'refs/heads/master'", workflow)
        self.assertIn("permissions: {}", workflow)
        # Source-level no HTTP transport is backed by fake-only adapter execution.
        for path in (TOOLS / "release-control-package").glob("*.py"):
            for forbidden in ("urllib", "requests.", "http.client", "socket.", "eval(", "exec("):
                self.assertNotIn(forbidden, path.read_text())


    # INV repository/release-control-preview-only
    def test_refresh_fixed_branch_revision_recovery_and_proof(self):
        events, proof, payload, branch, pr, bo, po = refresh_flow()
        candidate = {k: payload[k] for k in adapter.REFRESH_FIELDS}
        state = engine.reduce(sequence(copy.deepcopy(events)), CONFIG, proof)
        self.assertEqual(state["refresh-stage"], "ready")
        self.assertEqual(adapter.operation("refresh-pr", payload)["body"]["title"], "Refresh Unix-like dependencies")
        self.assertEqual(adapter.operation("refresh-pr", payload)["body"]["base"], "dev")
        self.assertEqual(adapter.operation("pr", {"repository": "shk95/configs", "head": "dev", "base": "master", "dev": D, "master": H, "body-operation": X})["body"]["base"], "master")
        for status in ("noop", "failed", "terminated-timeout"):
            plain = event("refresh-result", payload=canonical({"status": status}).decode())
            empty = engine.reduce(sequence([start(), event("claim", **OWNER), plain]), CONFIG, transcript())
            self.assertIsNone(empty["refresh"])
            self.refuse(engine.reduce, sequence(copy.deepcopy(events) + [plain]), CONFIG, proof)
            bad = event("refresh-result", payload=canonical({"status": status, "head": T}).decode())
            self.refuse(engine.reduce, sequence([start(), event("claim", **OWNER), bad]), CONFIG, transcript())
        joined = engine.reduce(sequence(copy.deepcopy(events) + [refresh_event(candidate)]), CONFIG, proof)
        self.assertEqual(joined["refresh-stage"], "ready")
        self.assertEqual(sum(o["state"] == "intent" for o in joined["operations"].values()), 0)
        new = refresh_fixture(source="d" * 40, parent="d" * 40, base=H, head="e" * 40, previous=T, lock="c" * 64)
        self.assertEqual(new["branch"], candidate["branch"])
        new_context = refresh_context_fixture(new)
        proof["refresh"]["revisions"].append(new_context)
        proof["refresh"]["current"] = copy.deepcopy(new_context)
        updated = copy.deepcopy(events) + [refresh_event(new)]
        # Old completed observations cannot advance the new prepared revision.
        updated += [effect("refresh-branch", payload, "observed", bo, branch), effect("refresh-pr", payload, "observed", po, pr)]
        state = engine.reduce(sequence(updated), CONFIG, proof)
        self.assertEqual(state["refresh-stage"], "prepared")
        self.assertEqual(state["operations"][branch]["remote"], T)
        self.assertEqual(state["operations"][pr]["remote"], "17")
        new_payload = dict(new, repository="shk95/configs")
        self.assertNotEqual(adapter.refresh_operation_id("refresh-branch", new_payload), branch)
        request_update = adapter.operation("refresh-branch", new_payload)
        self.assertEqual(request_update["method"], "PATCH")
        self.assertIs(request_update["body"]["force"], False)
        self.refuse(engine.reduce, sequence(copy.deepcopy(updated) + [effect("refresh-branch", new_payload, op_id=branch)]), CONFIG, proof)
        for name, bad in [("head-parents", [H]), ("merge-parents", [H, T]), ("changed", ["unixlike/flake.lock", "README.md"]), ("mode", 0o755)]:
            forged = copy.deepcopy(proof)
            forged["refresh"]["revisions"][-1]["proof"][name] = bad
            self.refuse(engine.reduce, sequence(copy.deepcopy(events) + [refresh_event(new)]), CONFIG, forged)
        # Unknown response fences new revision; confirmed absence supersedes old PR intent.
        unknown = {"status": "unknown", "target": {}, "complete": True}
        uncertain = copy.deepcopy(events[:-1]) + [effect("refresh-pr", payload, "unknown", unknown, pr)]
        proof["observations"][pr].append(unknown)
        self.refuse(engine.reduce, sequence(uncertain + [refresh_event(new)]), CONFIG, proof)
        absent = {"status": "absent", "target": {}, "complete": True}
        proof["observations"][pr].append(absent)
        recovered = copy.deepcopy(uncertain) + [effect("refresh-pr", payload, "intent", absent, pr), refresh_event(new)]
        recovered_state = engine.reduce(sequence(copy.deepcopy(recovered)), CONFIG, proof)
        self.assertEqual(recovered_state["operations"][pr]["state"], "superseded")
        self.assertEqual(sum(o["state"] == "intent" for o in recovered_state["operations"].values()), 0)
        for suffix in [effect("refresh-pr", payload, op_id=pr), effect("refresh-pr", payload, "observed", po, pr)]:
            self.refuse(engine.reduce, sequence(copy.deepcopy(recovered) + [suffix]), CONFIG, proof)
        for suffix in [effect("refresh-pr", payload, "intent", absent, pr), effect("refresh-pr", payload, "unknown", unknown, pr)]:
            self.refuse(engine.reduce, sequence(copy.deepcopy(events) + [suffix]), CONFIG, proof)
        self.refuse(engine.reduce, sequence(copy.deepcopy(events[:3]) + [effect("refresh-pr", payload, op_id=pr)]), CONFIG, proof)
        # Observations require exact head/base/lock/checks and one PR, never its body.
        for changed in ("head", "base", "lock"):
            wrong = copy.deepcopy(po); wrong["target"]["matches"][0]["candidate"][changed] = H if changed != "lock" else Y
            self.assertEqual(adapter.reconcile("refresh-pr", payload, wrong), "conflict")
        wrong = copy.deepcopy(po); wrong["target"]["matches"][0]["checks"]["status"] = "pending"
        self.assertEqual(adapter.reconcile("refresh-pr", payload, wrong), "conflict")
        wrong = copy.deepcopy(po); wrong["target"]["matches"] *= 2
        self.assertEqual(adapter.reconcile("refresh-pr", payload, wrong), "conflict")
        merged = copy.deepcopy(po); merged["target"]["matches"][0]["state"] = "merged"
        self.assertEqual(adapter.reconcile("refresh-pr", payload, merged), "applied")
        stopped = copy.deepcopy(events[:3]) + [event("stop-observed", revision="1", reason="operator"), effect("refresh-branch", payload, op_id=branch)]
        self.refuse(engine.reduce, sequence(stopped), CONFIG, proof)

    # INV repository/release-control-preview-only
    def test_refresh_integration_generation_freeze_and_opportunities(self):
        merge = {"repository": "shk95/configs", "number": "7", "dev": D, "master": H, "tree": T}
        applied = {"status": "present", "target": {"merged": True, "commit": "d" * 40, "parents": [H, D], "tree": T, "source": D}, "complete": True}
        for frozen in (False, True):
            prefix = base_events()
            if frozen:
                prefix += [effect("merge", merge), effect("merge", merge, "observed", applied)]
            events, proof, payload, _, _, _, _ = refresh_flow(prefix=prefix)
            if frozen:
                proof["observations"][X] = [applied]
            integrated = {"base": payload["base"], "head": payload["head"], "commit": "f" * 40, "parents": [payload["base"], payload["head"]], "tree": payload["tree"]}
            proof["refresh"]["current"].update(integration=integrated, **{"current-dev": integrated["commit"]})
            events.append(event("refresh-integrated", payload=canonical(integrated).decode()))
            state = engine.reduce(sequence(copy.deepcopy(events)), CONFIG, proof)
            self.assertEqual(state["frozen"], frozen)
            self.assertEqual(state["refresh-stage"], "next-opportunity" if frozen else "integrated")
            if frozen:
                self.assertIsNotNone(state["approval"])
                self.assertEqual(state["candidate"]["dev"], D)
                self.refuse(engine.reduce, sequence(events + [event("candidate", **dict(CANDIDATE, **{"candidate-generation": "2"}))]), CONFIG, proof)
            else:
                self.assertIsNone(state["candidate"]); self.assertIsNone(state["approval"]); self.assertEqual(state["evidence"], [])
                self.assertEqual(state["promotion-generation"], "1")
                self.refuse(engine.reduce, sequence(copy.deepcopy(events) + [event("candidate", **CANDIDATE)]), CONFIG, proof)
                new = dict(CANDIDATE, dev=integrated["commit"], **{"candidate-generation": "2"})
                state = engine.reduce(sequence(copy.deepcopy(events) + [event("candidate", **new)]), CONFIG, proof)
                self.assertEqual(state["promotion-generation"], "2")
                self.refuse(engine.reduce, sequence(copy.deepcopy(events) + [effect("merge", merge)]), CONFIG, proof)
        self.assertEqual(adapter.refresh_window("2026-10-01", 5, [])["refresh"], "start")
        self.assertEqual(adapter.refresh_window("2026-10-01", 5, ["2026-10-01"], manual=True)["refresh"], "join")
        self.assertEqual(adapter.refresh_window("2026-10-01", 6, [], refresh="waiting")["promotion"], "wait")
        self.assertEqual(adapter.refresh_window("2026-10-01", 7, [], refresh="waiting"), {"refresh": "missed", "promotion": "reconcile", "integration": "invalidate"})
        self.assertEqual(adapter.refresh_window("2026-10-01", 8, [], promoted=True)["integration"], "next-opportunity")
        self.refuse(adapter.refresh_window, "2026-02-30", 5, [])
        for malformed in ([[]], [{}], [1], ["2026-10-01", "2026-10-01"], {}):
            with self.assertRaises(Refusal):
                adapter.refresh_window("2026-10-01", 5, malformed)


    # INV repository/release-control-preview-only
    def test_refresh_protocol_one_two_actual_old_blobs_and_three_real_loader(self):
        source = "24cf09b5efbb4db821210632da8b44dcb822a337"
        with tempfile.TemporaryDirectory() as directory:
            scratch = Path(directory)
            repo = scratch / "public"; repo.mkdir()
            run_git(repo, "init", "-q", "-b", "master")
            run_git(repo, "config", "user.name", "Fixture")
            run_git(repo, "config", "user.email", "fixture@example.invalid")
            run_git(repo, "config", "core.hooksPath", str(scratch / "no-hooks"))
            # Actual historical eight blobs, not current modules relabeled protocol 1.
            executable_names = []
            for name in sorted(loader.FILES):
                data = subprocess.run(["git", "-C", str(TOOLS.parent.parent), "show", source + ":" + name], check=True, capture_output=True).stdout
                path = repo / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(data)
                mode = run_git(TOOLS.parent.parent, "ls-tree", source, "--", name).split()[0]
                if mode == "100755":
                    path.chmod(0o755)
                    executable_names.append(name)
            raw = subprocess.run(["git", "-C", str(TOOLS.parent.parent), "show", source + ":" + loader.MANIFEST], check=True, capture_output=True).stdout
            (repo / loader.MANIFEST).write_bytes(raw)
            old_manifest = digest(raw)
            run_git(repo, "add", ".")
            # Native Git for Windows cannot infer executable index mode from chmod.
            for name in executable_names:
                run_git(repo, "update-index", "--chmod=+x", name)
            run_git(repo, "commit", "-qm", "fixture historical package")
            run_git(repo, "checkout", "-qb", "dev")
            (repo / "marker").write_text("old\n"); run_git(repo, "add", "."); run_git(repo, "commit", "-qm", "fixture historical dev")
            run_git(repo, "checkout", "-q", "master"); run_git(repo, "merge", "--no-ff", "-qm", "fixture historical promotion", "dev")
            old = run_git(repo, "rev-parse", "HEAD")
            run_git(repo, "checkout", "-q", "dev")
            protocol_two_source = "7f43ec3b49243d10b0ea3d75272d8cd4c6ff3d7f"
            for name in loader.FILES | {loader.MANIFEST}:
                data = subprocess.run(["git", "-C", str(TOOLS.parent.parent), "show", protocol_two_source + ":" + name], check=True, capture_output=True).stdout
                (repo / name).write_bytes(data)
            middle_manifest = digest((repo / loader.MANIFEST).read_bytes())
            run_git(repo, "add", "."); run_git(repo, "commit", "-qm", "fixture actual protocol two")
            run_git(repo, "checkout", "-q", "master"); run_git(repo, "merge", "--no-ff", "-qm", "fixture protocol two promotion", "dev")
            middle = run_git(repo, "rev-parse", "HEAD")
            run_git(repo, "checkout", "-q", "dev")
            for name in loader.FILES:
                shutil.copyfile(TOOLS.parent.parent / name, repo / name)
            shutil.copyfile(TOOLS.parent.parent / loader.MANIFEST, repo / loader.MANIFEST)
            new_manifest = digest((repo / loader.MANIFEST).read_bytes())
            run_git(repo, "add", "."); run_git(repo, "commit", "-qm", "fixture protocol two")
            run_git(repo, "checkout", "-q", "master"); run_git(repo, "merge", "--no-ff", "-qm", "fixture protocol two promotion", "dev")
            newer = run_git(repo, "rev-parse", "HEAD")
            for protocol, control, manifest_hash in [("1", old, old_manifest), ("2", middle, middle_manifest), ("3", newer, new_manifest)]:
                approval = {"public-repository": "shk95/configs", "control": control, "master": newer,
                            "manifest": manifest_hash, "approval": X, "protocol": protocol}
                retained = scratch / ("retained-" + protocol)
                loader.extract(repo, approval, retained)
                self.assertEqual(len(list(retained.rglob("*"))) > 8, True)
                for name in loader.FILES:
                    actual = subprocess.run(["git", "-C", str(repo), "show", control + ":" + name], check=True, capture_output=True).stdout
                    self.assertEqual((retained / name).read_bytes(), actual)
                # Build the original index using that exact package, isolated process.
                code = "import sys;sys.path.insert(0,sys.argv[1]);import engine;sys.stdout.buffer.write(engine.index(engine.initial(),'0'*64))"
                initial_index = subprocess.run([sys.executable, "-I", "-S", "-B", "-c", code, str(retained / loader.ROOT)], check=True, capture_output=True).stdout
                operating = scratch / ("operating-" + protocol)
                for folder in ("config", "control", "history", "current"):
                    (operating / folder).mkdir(parents=True)
                (operating / "config/operating.tsv").write_bytes(encode(dict(CONFIG, protocol=protocol)))
                (operating / "control/stop.tsv").write_bytes(encode(STOP))
                (operating / "current/index.tsv").write_bytes(initial_index)
                approved_file = scratch / "approved.tsv"; approved_file.write_bytes(encode(approval))
                request_file = scratch / "request.tsv"; request_file.write_bytes(encode(request(candidate=None)))
                transcript_file = scratch / "transcript.json"; transcript_file.write_bytes(canonical(transcript("preview")))
                command = ["sh", WRAPPER, "preview", "--fixture-inputs", "--bundle-repository", repo.as_posix(), "--approved", approved_file.as_posix(), "--operating", operating.as_posix(), "--transcript", transcript_file.as_posix(), "--request", request_file.as_posix()]
                result = subprocess.run(command, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout), {"outcome": "preview", "stage": "empty", "proposed": 0})
                # Original retained modules serialize and project a nonempty history.
                if protocol == "1":
                    supplied_events = base_events()
                    payload = {"repository": "shk95/configs", "head": "dev", "base": "master", "dev": D, "master": H, "body-operation": X}
                    supplied_transcript = transcript(); supplied_transcript["source"] += transcript("preview")["source"]
                    bound_request = request()
                else:
                    supplied_events, supplied_transcript, _, _, _, _, _ = refresh_flow()
                    supplied_events = supplied_events[:-1]
                    supplied_transcript["source"] = transcript("preview", candidate=refresh_fixture())["source"]
                    payload = None
                    bound_request = request(candidate=refresh_fixture())
                generate = '''import sys,json
from pathlib import Path
sys.path.insert(0,sys.argv[1])
import records,engine,adapter
value=json.loads(sys.stdin.buffer.read())
root=Path(sys.argv[2])
config=records.encode(value['config'])
(root/'config/operating.tsv').write_bytes(config)
events=value['events']
events[0].update(control=value['approved']['control'],manifest=value['approved']['manifest'],**{'approval-provenance':value['approved']['approval'],'config':records.blob_identity(config),'protocol':value['config']['protocol']})
if value['config']['protocol']=='3':
 events[0]['approved-master']=value['approved']['master']
else:
 events[0].pop('approved-master',None);events[0].pop('config-commit',None)
if value['pr']:
 p=value['pr'];request=adapter.operation('pr',p)
 events.append({'sequence':'1','kind':'intent','prior':'0'*64,'batch':events[0]['batch'],'payload':records.canonical(p).decode(),'operation':[['c'*64,'pr',request['payload-digest'],'1','intent','-','-']]})
previous='0'*64
for n,event in enumerate(events,1):
 event.update(sequence=str(n),prior=previous)
 data=records.encode(event);records.parse(data,'event')
 (root/'history'/f'{n:012d}.tsv').write_bytes(data)
 previous=records.digest(data)
state=engine.reduce(events,value['config'],value['transcript'])
(root/'current/index.tsv').write_bytes(engine.index(state,previous))
'''
                supplied = {"events": supplied_events, "config": dict(CONFIG, protocol=protocol), "approved": approval,
                            "transcript": supplied_transcript, "pr": payload}
                subprocess.run([sys.executable, "-I", "-S", "-B", "-c", generate, str(retained / loader.ROOT), str(operating)], input=canonical(supplied), check=True, capture_output=True)
                request_file.write_bytes(encode(bound_request)); transcript_file.write_bytes(canonical(supplied_transcript))
                nonempty = subprocess.run(command, capture_output=True)
                self.assertEqual(nonempty.returncode, 0, nonempty.stderr)
                self.assertEqual(json.loads(nonempty.stdout), {"outcome": "preview", "stage": "approved" if protocol == "1" else "active", "proposed": 1})
                # Mislabeled semantic package cannot consume a different protocol.
                (operating / "config/operating.tsv").write_bytes(encode(dict(CONFIG, protocol="3" if protocol == "1" else "1")))
                self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
                approved_file.write_bytes(encode(dict(approval, protocol="4")))
                self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
                self.refuse(loader.approved, encode(dict(approval, protocol="4")))
            self.assertEqual(run_git(repo, "rev-parse", "HEAD"), newer)


    # INV repository/release-control-preview-only
    def test_refresh_current_dto_gate_real_preview(self):
        events, proof, payload, _, _, _, _ = refresh_flow()
        events = events[:-1]  # Historical good checks with a pending PR effect.
        candidate = {k: payload[k] for k in adapter.REFRESH_FIELDS}
        proof["source"] = transcript("preview", candidate=candidate)["source"]
        def view(supplied, supplied_events=None):
            records = copy.deepcopy(supplied_events or events)
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for name in ("config", "control", "history", "current"):
                    (root / name).mkdir()
                config_data = encode(CONFIG)
                records[0]["config"] = blob_identity(config_data)
                records = sequence(records)
                projected = engine.reduce(records, CONFIG, supplied)
                for n, record in enumerate(records, 1):
                    (root / "history" / f"{n:012d}.tsv").write_bytes(encode(record))
                (root / "config/operating.tsv").write_bytes(config_data)
                (root / "control/stop.tsv").write_bytes(encode(STOP))
                (root / "current/index.tsv").write_bytes(engine.index(projected, digest(encode(records[-1]))))
                return engine.preview(root, supplied, request(candidate=candidate), {"control": H, "manifest": X, "approval": X, "master": H})
        self.assertEqual(view(proof)["proposed"], 1)
        for key, bad in [("status", "failure"), ("status", "unknown"), ("status", "pending"), ("app", "99"), ("head", H), ("base", H), ("tree", T), ("lock", Y), ("name", "arbitrary")]:
            malformed = copy.deepcopy(proof); malformed["refresh"]["current"]["checks"][key] = bad
            self.refuse(view, malformed)
        for key, bad in [("prepared", {}), ("branch", {"batch": X, "branch": payload["branch"], "head": H}), ("current-dev", H), ("proof", {})]:
            malformed = copy.deepcopy(proof); malformed["refresh"]["current"][key] = bad
            self.refuse(view, malformed)
        malformed = copy.deepcopy(proof); del malformed["refresh"]["current"]["checks"]
        self.refuse(view, malformed)
        # Current schema always applies, but branch proposal does not demand checks.
        branch_events = events[:4]
        branch_proof = copy.deepcopy(proof)
        branch_proof["refresh"]["current"]["branch"]["head"] = "-"
        branch_proof["refresh"]["current"]["checks"] = None
        self.assertEqual(view(branch_proof, branch_events)["proposed"], 1)
        malformed = copy.deepcopy(branch_proof); malformed["refresh"]["current"]["unknown"] = "value"
        self.refuse(view, malformed, branch_events)
        # Completed historical PR is absorbing when current checks later fail.
        completed_events, completed, _, _, _, _, _ = refresh_flow()
        completed["source"] = proof["source"]
        completed["refresh"]["current"]["checks"]["status"] = "failure"
        self.assertEqual(view(completed, completed_events)["proposed"], 0)

    # INV repository/release-control-preview-only
    def test_refresh_promotion_effect_recovery_and_base_advance(self):
        events, proof, payload, _, _, _, _ = refresh_flow(prefix=base_events())
        merge = {"repository": "shk95/configs", "number": "7", "dev": D, "master": H, "tree": T}
        unknown = {"status": "unknown", "target": {}, "complete": True}
        applied = {"status": "present", "target": {"merged": True, "commit": "d" * 40, "parents": [H, D], "tree": T, "source": D}, "complete": True}
        absent = {"status": "absent", "target": {}, "complete": True}
        proof["observations"][X] = [unknown, applied, absent]
        unresolved = copy.deepcopy(events) + [effect("merge", merge), effect("merge", merge, "unknown", unknown)]
        integrated = {"base": payload["base"], "head": payload["head"], "commit": "f" * 40, "parents": [payload["base"], payload["head"]], "tree": payload["tree"]}
        proof["refresh"]["current"].update(integration=integrated, **{"current-dev": integrated["commit"]})
        integration = event("refresh-integrated", payload=canonical(integrated).decode())
        self.refuse(engine.reduce, sequence(copy.deepcopy(unresolved) + [integration]), CONFIG, proof)
        original = engine.reduce(sequence(copy.deepcopy(unresolved)), CONFIG, proof)
        self.assertEqual(original["candidate"], CANDIDATE)
        recovered = copy.deepcopy(unresolved) + [effect("merge", merge, "observed", applied), integration]
        state = engine.reduce(sequence(recovered), CONFIG, proof)
        self.assertTrue(state["frozen"]); self.assertEqual(state["refresh-stage"], "next-opportunity")
        self.assertEqual(state["operations"][X]["remote"], applied["target"]["commit"])
        missing = copy.deepcopy(unresolved) + [effect("merge", merge, "intent", absent), integration]
        state = engine.reduce(sequence(missing), CONFIG, proof)
        self.assertIsNone(state["candidate"]); self.assertIsNone(state["approval"]); self.assertEqual(state["evidence"], [])
        self.assertEqual(state["operations"][X]["state"], "superseded")
        self.assertEqual(sum(o["state"] == "intent" for o in state["operations"].values()), 0)
        self.refuse(engine.reduce, sequence(copy.deepcopy(missing) + [effect("merge", merge, "observed", applied)]), CONFIG, proof)
        for bad in ("failure", "unknown"):
            failed = copy.deepcopy(proof); failed["refresh"]["current"]["checks"]["status"] = bad
            self.refuse(engine.reduce, sequence(copy.deepcopy(events) + [integration]), CONFIG, failed)
        # A verified required base update invalidates old dev approval before intent.
        new = refresh_fixture(source="d" * 40, parent="d" * 40, base=H, head="e" * 40, previous=T, lock="c" * 64)
        new_context = refresh_context_fixture(new)
        proof["refresh"]["revisions"].append(new_context); proof["refresh"]["current"] = copy.deepcopy(new_context)
        advanced = copy.deepcopy(events) + [refresh_event(new)]
        state = engine.reduce(sequence(copy.deepcopy(advanced)), CONFIG, proof)
        self.assertIsNone(state["candidate"]); self.assertIsNone(state["approval"]); self.assertEqual(state["promotion-generation"], "1")
        self.refuse(engine.reduce, sequence(copy.deepcopy(advanced) + [effect("merge", merge)]), CONFIG, proof)
        self.refuse(engine.reduce, sequence(copy.deepcopy(unresolved) + [refresh_event(new)]), CONFIG, proof)
        # Reselect at generation2 and authenticate exact current-dev evidence/approval.
        new_candidate = dict(CANDIDATE, dev=H, **{"candidate-generation": "2"})
        evidence = list(EVIDENCE); evidence[1] = H
        proof["checks"].append(evidence)
        proof["source"] += transcript(candidate=new_candidate)["source"]
        approval = copy.deepcopy(base_events()[4]); approval.update(dev=H, **{"candidate-generation": "2", "evidence-digest": digest(canonical([evidence]))})
        current = advanced + [event("candidate", **new_candidate), event("evidence", evidence=[evidence], **{"evidence-digest": digest(canonical([evidence]))}), approval, effect("merge", dict(merge, dev=H))]
        state = engine.reduce(sequence(current), CONFIG, proof)
        self.assertEqual(state["candidate"]["dev"], H); self.assertEqual(state["operations"][X]["state"], "intent")



class GlobalHistoryProof(unittest.TestCase):
    # INV repository/release-control-preview-only
    # INV repository/fixture-git-isolation
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.public = self.root / 'public'; self.public.mkdir()
        self.operating = self.root / 'operating'; self.operating.mkdir()
        for repo in (self.public, self.operating):
            run_git(repo, 'init', '-q', '-b', 'master')
            run_git(repo, 'config', 'user.name', 'Fixture')
            run_git(repo, 'config', 'user.email', 'fixture@example.invalid')
            run_git(repo, 'config', 'core.hooksPath', str(self.root / 'no-hooks'))
        (self.public / 'seed').write_text('seed\n')
        self.commit(self.public)
        self.packages = {}
        for protocol, source in [('1','24cf09b5efbb4db821210632da8b44dcb822a337'),
                                 ('2','7f43ec3b49243d10b0ea3d75272d8cd4c6ff3d7f'), ('3',None)]:
            if protocol == '1':
                run_git(self.public, 'checkout', '-qb', 'dev')
            else:
                run_git(self.public, 'checkout', '-q', 'dev')
            for name in loader.FILES | {loader.MANIFEST}:
                target = self.public / name; target.parent.mkdir(parents=True, exist_ok=True)
                data = (TOOLS.parent.parent / name).read_bytes() if source is None else subprocess.run(
                    ['git','-C',str(TOOLS.parent.parent),'show',source+':'+name],capture_output=True,check=True).stdout
                target.write_bytes(data)
            run_git(self.public, 'add', '.')
            for name in ('release-preview', 'classify'):
                (self.public/'tool/version-control'/name).chmod(0o755)
                run_git(self.public, 'update-index', '--chmod=+x', 'tool/version-control/'+name)
            run_git(self.public, 'commit', '-qm', 'fixture package '+protocol)
            run_git(self.public, 'checkout', '-q', 'master')
            run_git(self.public, 'merge', '--no-ff', '-qm', 'fixture promotion '+protocol, 'dev')
            control = run_git(self.public, 'rev-parse', 'HEAD')
            self.packages[protocol] = {'public-repository':'shk95/configs','control':control,
                'master':control,'manifest':digest((self.public/loader.MANIFEST).read_bytes()),'approval':X,'protocol':protocol}
        master = run_git(self.public, 'rev-parse', 'HEAD')
        for approval in self.packages.values():
            approval['master'] = master
        for folder in ('config','control','current','history'):
            (self.operating/folder).mkdir()
        (self.operating/'control/stop.tsv').write_bytes(encode(STOP))
        self.approval_file=self.root/'approved.tsv';self.approval_file.write_bytes(encode(self.packages['3']))
        self.transcript_file=self.root/'transcript.json';self.transcript_file.write_bytes(canonical(transcript('preview',candidate=None)))
        self.request_file=self.root/'request.tsv';self.request_file.write_bytes(encode(request(candidate=None)))
        self.contexts=[];self.events=[];self.ledger=[];self.projections=[]

    def commit(self, repo):
        run_git(repo,'add','.');run_git(repo,'commit','-qm','fixture snapshot')
        return run_git(repo,'rev-parse','HEAD')

    def append(self, item):
        item=copy.deepcopy(item)
        item['sequence']=str(len(self.events)+1)
        item['prior']=digest(encode(self.events[-1])) if self.events else Z
        self.events.append(item)
        (self.operating/'history'/('%012d.tsv'%len(self.events))).write_bytes(encode(item))

    def add_batch(self, protocol, batch, completed):
        config=encode(dict(CONFIG,protocol=protocol))
        (self.operating/'config/operating.tsv').write_bytes(config)
        (self.operating/'current/transcript.json').write_bytes(self.transcript_file.read_bytes())
        cfg_commit=self.commit(self.operating)
        transcript_blob=run_git(self.operating,'rev-parse',cfg_commit+':current/transcript.json')
        approval=self.packages[protocol]
        before=len(self.events);prior=digest(encode(self.events[-1])) if self.events else Z
        start_event=start(approval['control'],approval['manifest'],approval['approval'],blob_identity(config))
        start_event.update(batch=batch,protocol=protocol,**{'approved-master':approval['master'],'config-commit':cfg_commit})
        if protocol!='3':
            start_event.pop('approved-master');start_event.pop('config-commit')
        self.append(start_event);self.append(event('claim',batch=batch,**OWNER))
        if completed:
            self.append(event('complete',batch=batch))
        context={'start':str(before+1),'batch':batch,'master':approval['master'],'control':approval['control'],
                 'manifest':approval['manifest'],'approval':approval['approval'],'protocol':protocol,
                 'config-commit':cfg_commit,'config':blob_identity(config),
                 'transcript-commit':cfg_commit if completed else '-',
                 'transcript':transcript_blob if completed else '-'}
        self.contexts.append(context)
        isolated=self.root/('package-'+str(len(self.contexts)));loader.extract(self.public,approval,isolated)
        isolated_batch=self.root/('batch-'+str(len(self.contexts)))
        (isolated_batch/'config').mkdir(parents=True);(isolated_batch/'history').mkdir()
        (isolated_batch/'config/operating.tsv').write_bytes(config)
        for number,item in enumerate(self.events[before:],before+1):
            (isolated_batch/'history'/('%012d.tsv'%number)).write_bytes(encode(item))
        # Fixture generator uses the exact historical serializer/reducer independently
        # of the global selector, including original global filenames and bytes.
        generator="""import sys,json
from pathlib import Path
sys.path.insert(0,sys.argv[1]);import records,engine
root=Path(sys.argv[2]);protocol=sys.argv[3];before=int(sys.argv[4]);prior=sys.argv[5]
cfg=records.parse(records.read(root/'config/operating.tsv'),'config')
transcript=json.loads(sys.stdin.buffer.read())
events,last=records.history(root/'history',before,prior) if protocol=='3' else records.history(root/'history')
state=engine.reduce(events,cfg,transcript)
sys.stdout.buffer.write(engine.index(state,last))
"""
        projection=subprocess.run([sys.executable,'-I','-S','-B','-c',generator,str(isolated/loader.ROOT),str(isolated_batch),protocol,str(before),prior],
            input=self.transcript_file.read_bytes(),capture_output=True,check=True).stdout
        self.ledger.append({'context':context,'projection':digest(projection)})
        self.final=dict(row for row in [line.split('\t') for line in projection.decode().splitlines()[1:]])
        self.projections.append(self.final.copy())

    def save(self):
        fields=('start','batch','master','control','manifest','approval','protocol','config-commit','config','transcript-commit','transcript')
        raw='format\t1\n'+''.join('context\t'+'\t'.join(c[k] for k in fields)+'\n' for c in self.contexts)
        (self.operating/'current/batches.tsv').write_bytes(raw.encode('utf-8'))
        index=dict(self.final,**{'index-kind':'global-1','ledger-digest':digest(canonical(self.ledger))})
        (self.operating/'current/index.tsv').write_bytes(encode(index))
        self.head=self.commit(self.operating)

    def prepare(self, first='1', second=True):
        self.add_batch(first,X,True)
        if second:
            self.add_batch('3',Y,False)
        else:
            (self.operating/'config/operating.tsv').write_bytes(encode(CONFIG))
        self.save()

    def invoke(self):
        command=['sh',WRAPPER,'preview','--fixture-inputs','--global-history','--operating-head',self.head,
            '--bundle-repository',self.public.as_posix(),'--approved',self.approval_file.as_posix(),
            '--operating',self.operating.as_posix(),'--transcript',self.transcript_file.as_posix(),'--request',self.request_file.as_posix()]
        return subprocess.run(command,capture_output=True)

    def refuse(self):
        result=self.invoke();self.assertEqual(result.returncode,1,result.stdout)
        self.assertEqual(result.stdout,b'');self.assertEqual(result.stderr,b'release-control: refused'+os.linesep.encode('ascii'))

    # INV repository/release-control-preview-only
    def test_global_original_bytes_retained_one_and_later_three(self):
        self.prepare()
        original={name:subprocess.run(['git','-C',str(self.operating),'show',self.head+':'+name],capture_output=True,check=True).stdout
                  for name in run_git(self.operating,'ls-files').splitlines()}
        status=run_git(self.operating,'status','--porcelain');head=self.head
        result=self.invoke();self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout),{'outcome':'preview','stage':'active','proposed':0})
        self.assertEqual(run_git(self.operating,'rev-parse','HEAD'),head)
        self.assertEqual(run_git(self.operating,'status','--porcelain'),status)
        for name,data in original.items():self.assertEqual((self.operating/name).read_bytes(),data)
        # Working tree config changes do not substitute the accepted Git snapshot.
        (self.operating/'config/operating.tsv').write_bytes(b'untrusted working bytes\n')
        self.assertEqual(self.invoke().returncode,0)
        # A current config disabling new work cannot suppress old obligations.
        (self.operating/'config/operating.tsv').write_bytes(encode(dict(CONFIG,enabled='0',actors='-',checks='-')))
        self.head=self.commit(self.operating)
        self.assertEqual(json.loads(self.invoke().stdout)['stage'],'active')
        (self.operating/'control/stop.tsv').write_bytes(encode(dict(STOP,stop='1',revision='1')))
        self.head=self.commit(self.operating)
        self.assertEqual(json.loads(self.invoke().stdout),{'outcome':'stopped','proposed':0})
        (self.operating/'history/000000000001.tsv').write_bytes(b'format\t1\n')
        self.head=self.commit(self.operating)
        self.refuse() # fresh stop never excuses invalid old history

    # INV repository/release-control-preview-only
    def test_global_actual_protocol_two_and_quiet_completed_selection(self):
        self.prepare(first='2',second=False)
        result=self.invoke();self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout),{'outcome':'preview','stage':'complete','proposed':0})
        (self.operating/'config/operating.tsv').write_bytes(encode(dict(CONFIG,enabled='0',actors='-',checks='-')))
        self.head=self.commit(self.operating)
        result=self.invoke();self.assertEqual((result.returncode,result.stdout),(0,b''),result.stderr)

    # INV repository/release-control-preview-only
    def test_global_semantic_completed_prefix_not_structural_marker(self):
        self.prepare(second=False)
        run_git(self.operating,'reset','--hard',self.contexts[0]['config-commit'])
        (self.operating/'config/operating.tsv').write_bytes(encode(CONFIG))
        self.events=self.events[:2]
        (self.operating/'history').mkdir(exist_ok=True)
        for path in (self.operating/'history').iterdir():path.unlink()
        for n,item in enumerate(self.events,1):(self.operating/'history'/('%012d.tsv'%n)).write_bytes(encode(item))
        self.append(event('candidate',**CANDIDATE));self.append(event('complete'))
        self.save()
        paths={'operating':self.operating,'bundle_repository':self.public,'approved':self.approval_file,
               'transcript':self.transcript_file,'request':self.request_file}
        with self.assertRaisesRegex(ValueError,'retained-replay-refusal'):
            loader.global_preview(paths,self.packages['3'],self.head,self.root/'failure')
        self.refuse()

    # INV repository/release-control-preview-only
    def test_global_chain_overlap_context_and_index_refusals(self):
        self.prepare()
        original=self.head
        cases=[('history/000000000006.tsv',encode(self.events[-1])),
               ('history/000000000002.tsv',encode(dict(self.events[1],prior=Y))),
               ('history/000000000002.tsv',encode(dict(self.events[1],batch=Y))),
               ('current/index.tsv',encode(dict(self.final,**{'index-kind':'global-1','ledger-digest':Y}))),
               ('current/batches.tsv',b'format\t1\n')]
        for name,data in cases:
            with self.subTest(name=name):
                run_git(self.operating,'reset','--hard',original)
                (self.operating/name).write_bytes(data);self.head=self.commit(self.operating);self.refuse()
        run_git(self.operating,'reset','--hard',original)
        path=self.operating/'history/000000000003.tsv';path.unlink()
        self.head=self.commit(self.operating);self.refuse()

    # INV repository/release-control-preview-only
    def test_global_missing_config_source_and_unsafe_objects_refuse(self):
        self.prepare();original=self.head
        path=self.operating/'current/batches.tsv';raw=path.read_bytes()
        for key in ('config','config-commit','manifest','protocol'):
            run_git(self.operating,'reset','--hard',original)
            old=self.contexts[0][key];new='9' if key=='protocol' else 'f'*len(old)
            path.write_bytes(raw.replace(old.encode(),new.encode()))
            self.head=self.commit(self.operating);self.refuse()
        run_git(self.operating,'reset','--hard',original)
        target=self.operating/'history/000000000001.tsv'
        run_git(self.operating,'update-index','--chmod=+x','history/000000000001.tsv')
        run_git(self.operating,'commit','-qm','fixture unsafe mode')
        self.head=run_git(self.operating,'rev-parse','HEAD');self.refuse()

    # INV repository/release-control-preview-only
    def test_global_old_offset_and_ambiguous_boundaries_refuse(self):
        self.prepare()
        old=self.head
        # Offset protocol1/2 is never adapted to global3 by renumbering.
        for protocol in ('1','2'):
            with self.assertRaisesRegex(ValueError,'unsupported-retained-offset'):
                loader.replay_package(self.root/'unused',self.root/'unused',protocol,3,X)
        # A second start while the first batch is outstanding refuses before replay.
        run_git(self.operating,'reset','--hard',old)
        self.events=self.events[:2]
        (self.operating/'history').mkdir(exist_ok=True)
        for path in (self.operating/'history').iterdir():path.unlink()
        for n,item in enumerate(self.events,1):(self.operating/'history'/('%012d.tsv'%n)).write_bytes(encode(item))
        self.append(dict(self.events[0],batch=Y))
        self.head=self.commit(self.operating);self.refuse()


    # INV repository/release-control-preview-only
    def test_global_empty_snapshot_and_invalid_request(self):
        (self.operating/'config/operating.tsv').write_bytes(encode(CONFIG))
        (self.operating/'current/transcript.json').write_bytes(self.transcript_file.read_bytes())
        self.final=parse(engine.index(engine.initial(),Z),'index')
        self.save()
        result=self.invoke();self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout),{'outcome':'preview','stage':'empty','proposed':0})
        self.request_file.write_bytes(encode(request()))
        self.refuse()
        self.request_file.write_bytes(encode(request(mode='start',candidate=None)))
        self.refuse()
        self.request_file.write_bytes(encode(request(candidate=None)))
        (self.operating/'config/operating.tsv').write_bytes(encode(dict(CONFIG,enabled='0',actors='-',checks='-')))
        self.head=self.commit(self.operating)
        result=self.invoke();self.assertEqual((result.returncode,result.stdout),(0,b''),result.stderr)

    # INV repository/release-control-preview-only
    def test_global_unreachable_shallow_and_replaced_history(self):
        self.prepare();original=self.head
        # An available config object on an unrelated history is not accepted ancestry.
        context=self.contexts[0]
        tree=run_git(self.operating,'rev-parse',context['config-commit']+'^{tree}')
        unrelated=run_git(self.operating,'commit-tree',tree,'-m','fixture unrelated config')
        run_git(self.operating,'reset','--hard',self.contexts[1]['config-commit'])
        for n,item in enumerate(self.events,1):(self.operating/'history'/('%012d.tsv'%n)).write_bytes(encode(item))
        original_config_commit=context['config-commit'];context['config-commit']=unrelated
        self.save();self.refuse()
        context['config-commit']=original_config_commit
        run_git(self.operating,'reset','--hard',original);self.head=original
        (self.operating/'.git/shallow').write_bytes((original+'\n').encode())
        self.refuse();(self.operating/'.git/shallow').unlink()
        run_git(self.operating,'replace',original,context['config-commit'])
        self.refuse();run_git(self.operating,'replace','-d',original)
        run_git(self.public,'replace',self.packages['3']['control'],self.packages['1']['control'])
        self.refuse()


    # INV repository/release-control-preview-only
    def test_global_coherent_truncation_and_repointed_archive_refuse(self):
        self.prepare();original=self.head
        contexts=copy.deepcopy(self.contexts);ledger=copy.deepcopy(self.ledger);final=self.final.copy()
        for path in (self.operating/'history').iterdir():
            if int(path.stem)>3:path.unlink()
        self.contexts=self.contexts[:1];self.ledger=self.ledger[:1];self.final=self.projections[0]
        self.save()
        with self.assertRaisesRegex(ValueError,'rewritten-or-truncated-history'):
            loader.verify_append_only_snapshot(self.operating,self.head)
        self.refuse() # even a recomputed internally consistent index cannot hide tail loss
        run_git(self.operating,'reset','--hard',original)
        self.contexts=contexts;self.ledger=ledger;self.final=final
        # Repoint to identical archived bytes at a newer reachable commit; identity
        # remains immutable even when the old semantic projection would be unchanged.
        self.contexts[0]['transcript-commit']=self.contexts[1]['config-commit']
        self.ledger[0]['context']=self.contexts[0]
        self.save()
        with self.assertRaisesRegex(ValueError,'changed-retained-context-prefix'):
            loader.verify_append_only_snapshot(self.operating,self.head)
        self.refuse()

    # INV repository/release-control-preview-only
    def test_global_outstanding_completion_archives_once(self):
        self.prepare()
        self.append(event('complete',batch=Y))
        current=self.contexts[-1];current['transcript-commit']=current['config-commit']
        current['transcript']=run_git(self.operating,'rev-parse',current['config-commit']+':current/transcript.json')
        state=engine.reduce(self.events[3:],CONFIG,json.loads(self.transcript_file.read_bytes()))
        projection=engine.index(state,digest(encode(self.events[-1])))
        self.final=parse(projection,'index')
        self.ledger[-1]={'context':current,'projection':digest(projection)}
        self.save()
        result=self.invoke();self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout),{'outcome':'preview','stage':'complete','proposed':0})

    # INV repository/release-control-preview-only
    def test_global_tampered_bytes_under_recorded_blob_id_refuse(self):
        self.prepare()
        blob=self.contexts[0]['transcript']
        original=subprocess.run(['git','-C',str(self.operating),'cat-file','blob',blob],capture_output=True,check=True).stdout
        # Different original bytes, same decoded JSON and otherwise identical ledger.
        altered=original+b'\n'
        path=self.operating/'.git/objects'/blob[:2]/blob[2:]
        path.chmod(0o600)
        path.write_bytes(zlib.compress(b'blob '+str(len(altered)).encode()+b'\0'+altered))
        # cat-file alone accepts this corruption; explicit blob identity must refuse.
        self.assertEqual(subprocess.run(['git','-C',str(self.operating),'cat-file','blob',blob],capture_output=True,check=True).stdout,altered)
        self.refuse()

    # INV repository/release-control-preview-only
    def test_global_legacy_grafts_refuse_in_both_repositories(self):
        self.prepare()
        for repo, head in ((self.operating, self.head), (self.public, self.packages['3']['master'])):
            with self.subTest(repository=repo.name):
                grafts=repo/'.git/info/grafts'
                grafts.parent.mkdir(exist_ok=True)
                grafts.write_bytes((head+'\n').encode('ascii'))
                self.refuse()
                grafts.unlink()
                result=self.invoke()
                self.assertEqual(result.returncode,0,result.stderr)

if __name__ == "__main__":
    unittest.main()
