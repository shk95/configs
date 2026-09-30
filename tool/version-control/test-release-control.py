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
          "workflow": "2", "actors": "3", "checks": "gate", "protocol": "1"}
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
                 **{"approval-provenance": approval, "config": config, "protocol": "1",
                    "day": "2026-09-30", "run": "4", "attempt": "1", "time": "2026-09-30T00:00:00Z"})


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
                        "master": old, "manifest": m, "approval": X, "protocol": "1"}
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
            self.refuse(loader.approved, encode(dict(approved, protocol="2")))
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
            self.assertEqual(engine.preview(root, replacement_proof, request(candidate=replacement), {"control": H, "manifest": X, "approval": X})["proposed"], 0)
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


if __name__ == "__main__":
    unittest.main()
