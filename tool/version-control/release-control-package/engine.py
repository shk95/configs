"""Event projection and inert effect proposals, without a write implementation."""
# INV repository/release-control-preview-only
import json
import os
import subprocess
from pathlib import Path
from records import blob_identity, canonical, decimal, digest, encode, history, identifiers, parse, read, require
from adapter import authenticate, document, operation, reconcile, remote_identity, takeover


def retained_replay(source_repository, control, master, candidate, baselines, evidence):
    """Use only the manifest-retained R-preview/classifier, with its existing interface.

    Its asserted evidence remains synthetic. The controller adapter must authenticate
    real evidence in a later operating lane; this function creates no such authority.
    """
    tools = Path(__file__).resolve().parent.parent
    runtime_keys = {"PATH", "SYSTEMROOT", "SystemRoot", "WINDIR", "COMSPEC", "ComSpec",
                    "PATHEXT", "TEMP", "TMP", "TMPDIR", "LANG", "LC_ALL", "TZ"}
    env = {key: os.environ[key] for key in runtime_keys if key in os.environ}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
               GIT_NO_REPLACE_OBJECTS="1", GIT_TERMINAL_PROMPT="0")
    command = ["sh", (tools / "release-preview").as_posix(), "--master", master,
               "--candidate", candidate, "--rules", control, "--baselines",
               Path(baselines).resolve().as_posix(), "--evidence",
               Path(evidence).resolve().as_posix(), "--json"]
    result = subprocess.run(command, cwd=source_repository, env=env,
                            capture_output=True, timeout=30)
    require(result.returncode == 0, "retained-release-preview-refusal")
    replay = document(result.stdout)
    require(replay.get("master") == master and replay.get("candidate") == candidate
            and replay.get("rules") == control and replay.get("decision") in {"candidate", "no-op"},
            "retained-replay-binding-mismatch")
    return replay


def initial():
    return {"batch": "0" * 64, "generation": "0", "stage": "empty", "owner": None,
            "candidate": None, "evidence": [], "approval": None, "operations": {},
            "releases": [], "stopped": False, "sequence": "0", "control": None,
            "retry": 0, "publication-payloads": {}, "stop-revision": "0"}


def candidate_digest(candidate):
    return digest(canonical(candidate)) if candidate else "0" * 64


def reconciled(op):
    return op["state"] == "observed" or (op["state"] == "intent" and op["observation"]
            and op["observation"]["status"] == "absent" and op["observation"]["complete"] is True)


def reduce(events, config, transcript):
    state = initial()
    for event in events:
        kind = event["kind"]
        require(state["stage"] != "complete", "event-after-complete")
        require(kind == "batch-start" or event["batch"] == state["batch"], "wrong-event-batch")
        if kind == "batch-start":
            require(state["stage"] == "empty", "duplicate-outstanding-batch")
            state.update(batch=event["batch"], stage="active", control=event["control"])
        elif kind == "claim":
            require(state["stage"] not in {"empty", "stopped"}, "impossible-claim-stage")
            require(decimal(event["generation"]) == decimal(state["generation"]) + 1, "wrong-owner-generation")
            require(event["repository"] == config["repository"] and event["workflow"] == config["workflow"], "wrong-owner-connection")
            if state["owner"]:
                takeover(state["owner"], transcript["owner"])
                require(all(reconciled(o) for o in state["operations"].values()), "unreconciled-operation-before-takeover")
            state["owner"] = {key: event[key] for key in ("repository", "workflow", "run", "attempt", "job", "generation", "operating-head")}
            state["generation"] = event["generation"]
        elif kind == "candidate":
            require(state["owner"] and state["stage"] in {"active", "candidate", "validated", "approved", "blocked", "waiting"}, "candidate-after-publication-or-unowned")
            old = state["candidate"]
            require(decimal(event["candidate-generation"]) == (decimal(old["candidate-generation"]) + 1 if old else 1), "wrong-candidate-generation")
            fields = ("candidate-generation", "dev", "master", "tree", "rules", "tool", "baselines", "selected", "classification", "versions", "migrations", "approval-required")
            selected = identifiers(event["selected"])
            require(selected and set(selected) <= set(identifiers(config["checks"])), "unsupported-coverage")
            state["candidate"] = {k: event[k] for k in fields}
            state.update(evidence=[], approval=None, releases=event.get("release", []), stage="candidate")
            for row in state["releases"]:
                require(row[2] == event["dev"], "release-source-candidate-mismatch")
        elif kind == "evidence":
            candidate = state["candidate"]
            require(candidate and state["stage"] == "candidate", "impossible-evidence-stage")
            values = event.get("evidence", [])
            require(sorted(row[0] for row in values) == identifiers(candidate["selected"]), "missing-required-checks")
            require(event["evidence-digest"] == digest(canonical(values)), "evidence-digest-mismatch")
            for row in values:
                require(row[1:6] == [candidate[k] for k in ("dev", "master", "tree", "rules", "tool")] and row[6] == "verified", "unverified-or-stale-evidence")
                # Source identity is an explicit fake adapter observation, not row prose.
                require(isinstance(transcript["checks"], list) and transcript["checks"].count(row) == 1, "unauthenticated-check-provenance")
            state.update(evidence=values, stage="validated")
        elif kind == "approval":
            require(state["stage"] == "validated", "impossible-approval-stage")
            candidate = state["candidate"]
            require(event["actor"] in config["actors"].split(",") and event["ref"] == "refs/heads/master", "unauthorized-approval")
            require(all(event[k] == candidate[k] for k in ("candidate-generation", "dev", "master", "tree", "classification", "versions", "migrations")), "stale-approval")
            require(event["evidence-digest"] == digest(canonical(state["evidence"])), "stale-approval-evidence")
            request = {k: event[k] for k in ("actor", "run", "attempt", "ref")}
            request.update(mode="approve", candidate=candidate_digest(candidate))
            authenticate(transcript, config, request, candidate_digest(candidate))
            state.update(approval=request, stage="approved")
        elif kind in {"intent", "observation"}:
            require(state["owner"] and (kind == "observation" or not state["stopped"]), "unowned-or-stopped-operation")
            tuples = event.get("operation", [])
            require(len(tuples) == 1, "missing-single-operation")
            row = tuples[0]
            op_id, op_kind, payload_digest, generation, status, remote, observation = row
            payload = document(event["payload"].encode("utf-8"))
            request = operation(op_kind, payload)
            if op_kind == "record":
                require(payload["repository"] == config["operating-repository"], "wrong-operating-target")
            require(request["payload-digest"] == payload_digest and generation == state["generation"], "operation-payload-or-owner-mismatch")
            previous = state["operations"].get(op_id)
            if kind == "intent":
                require(all(o["state"] not in {"unknown", "conflict"} for o in state["operations"].values()), "unreconciled-operation")
                require(status == "intent" and remote == "-" and observation == "-", "invalid-intent")
                if previous:
                    require(previous["payload"] == payload and previous["kind"] == op_kind, "changed-duplicate-operation")
                    require(previous["state"] != "observed", "repeated-completed-operation")
                if op_kind == "merge":
                    require(state["stage"] in {"validated", "approved"}, "unvalidated-promotion")
                    require(state["candidate"]["approval-required"] == "0" or state["approval"], "missing-exact-approval")
                    require(all(payload[k] == state["candidate"][k] for k in ("dev", "master", "tree")), "stale-merge-payload")
                if op_kind.startswith("tag"):
                    require(state["stage"] in {"promoted", "publishing"}, "tag-before-verified-promotion")
                    matches = [r for r in state["releases"] if payload["tag"] == r[0] + "-v" + r[1]]
                    require(len(matches) == 1, "unselected-release")
                    release = matches[0]
                    require(payload["object"] == release[5], "changed-fixed-tag-object")
                    if op_kind == "tag-object":
                        require(op_id == release[6], "changed-fixed-publication-operation")
                        require(payload["source"] == release[2] and blob_identity(payload["annotation"].encode("utf-8")) == release[4], "changed-fixed-publication")
                        frozen = state["publication-payloads"].get(payload["tag"])
                        require(frozen is None or frozen == payload, "changed-frozen-publication-payload")
                        state["publication-payloads"][payload["tag"]] = payload
                    else:
                        require(payload["tag"] in state["publication-payloads"], "tag-ref-before-fixed-object")
                state["operations"][op_id] = {"kind": op_kind, "payload": payload, "state": "intent", "observation": None, "phase": state["stage"]}
            else:
                require(previous and previous["payload"] == payload and previous["kind"] == op_kind, "observation-without-matching-intent")
                supplied = transcript["observations"].get(op_id)
                require(isinstance(supplied, list), "missing-operation-observations")
                matches = [o for o in supplied if digest(canonical(o)) == observation]
                require(len(matches) == 1, "observation-digest-mismatch")
                observed = matches[0]
                result = reconcile(op_kind, payload, observed)
                if result == "applied":
                    require(remote == remote_identity(op_kind, payload, observed), "observed-remote-identity-mismatch")
                require(status == {"applied": "observed", "absent": "intent", "unknown": "unknown", "conflict": "conflict"}[result], "false-observation-result")
                previous.update(state=status, observation=observed)
                if result in {"unknown", "conflict"}:
                    state["stage"] = "blocked"
                elif not state["stopped"] and result == "applied" and op_kind == "merge":
                    state["stage"] = "promoted"
                elif not state["stopped"] and result == "applied" and op_kind.startswith("tag"):
                    state["stage"] = "publishing"
                elif not state["stopped"] and result == "absent":
                    state["stage"] = previous["phase"]
        elif kind == "retry-wait":
            require(state["stage"] not in {"empty", "stopped"} and event["transient"] == "1", "nontransient-or-invalid-wait")
            require(state["retry"] < 3 and decimal(event["minutes"]) == (5, 15, 30)[state["retry"]], "unbounded-retry")
            state["retry"] += 1
            state["stage"] = "waiting"
        elif kind == "blocker":
            require(state["stage"] != "empty", "blocker-without-batch")
            state["stage"] = "blocked"
        elif kind == "stop-observed":
            require(decimal(event["revision"]) > decimal(state["stop-revision"]), "nonmonotonic-stop-revision")
            state.update(stopped=True, stage="stopped", **{"stop-revision": event["revision"]})
        elif kind == "resume":
            require(state["stage"] in {"stopped", "blocked", "waiting"}, "impossible-resume")
            request = {k: event[k] for k in ("actor", "run", "attempt", "ref")}
            request.update(mode="resume", candidate=candidate_digest(state["candidate"]))
            authenticate(transcript, config, request, request["candidate"])
            require(all(reconciled(o) for o in state["operations"].values()), "resume-before-reconciliation")
            state.update(stopped=False, stage="candidate" if state["candidate"] else "active", evidence=[], approval=None)
        elif kind == "complete":
            require(state["stage"] in {"active", "publishing", "promoted"}, "impossible-completion")
            require(all(o["state"] == "observed" for o in state["operations"].values()), "incomplete-operations")
            if state["releases"]:
                for release in state["releases"]:
                    require(any(o["kind"] == "tag-ref" and o["state"] == "observed" and o["payload"]["object"] == release[5] for o in state["operations"].values()), "incomplete-release")
            state["stage"] = "complete"
        state["sequence"] = event["sequence"]
    return state


def index(state, prior):
    return encode({"sequence": state["sequence"], "prior": prior, "batch": state["batch"],
                   "generation": state["generation"], "stage": state["stage"],
                   "state-digest": digest(canonical(state))})


def preview(directory, transcript, request, approved):
    root = Path(directory)
    require(root.is_dir() and not root.is_symlink(), "unsafe-operating-root")
    for name in ("config", "control", "history", "current"):
        require((root / name).is_dir() and not (root / name).is_symlink(), "unsafe-operating-directory")
    config_data = read(root / "config/operating.tsv")
    config = parse(config_data, "config")
    if config["enabled"] == "0":
        return None
    require(config["actors"] != "-" and config["checks"] != "-", "enabled-misconfiguration")
    stop = parse(read(root / "control/stop.tsv"), "stop")
    events, prior = history(root / "history")
    if events:
        start = events[0]
        require(start["kind"] == "batch-start" and start["control"] == approved["control"] and start["manifest"] == approved["manifest"] and start["approval-provenance"] == approved["approval"], "wrong-retained-batch-control")
        # Pinned config is supplied at its recorded blob SHA, not current config.
        actual = blob_identity(config_data)
        require(actual == start["config"], "changed-pinned-batch-config")
    state = reduce(events, config, transcript)
    actual_index = read(root / "current/index.tsv")
    parse(actual_index, "index")
    require(actual_index == index(state, prior), "history-index-mismatch")
    require(request["mode"] == "preview", "live-mode-unavailable")
    if state["candidate"]:
        authenticate(transcript, config, request, candidate_digest(state["candidate"]))
    elif request["candidate"] != "0" * 64:
        require(False, "missing-request-candidate")
    if stop["stop"] == "1" or state["stopped"]:
        return {"outcome": "stopped", "proposed": 0}
    # Safe public output reveals neither repository connection nor raw records.
    pending = [o for o in state["operations"].values() if o["state"] == "intent"]
    return {"outcome": "preview", "stage": state["stage"], "proposed": len(pending)}
