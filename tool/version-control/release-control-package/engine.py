"""Event projection and inert effect proposals, without a write implementation."""
# INV repository/release-control-preview-only
import json
import os
import subprocess
from pathlib import Path
from records import blob_identity, canonical, decimal, digest, encode, history, identifiers, parse, read, require
from adapter import (authenticate, document, operation, reconcile, remote_identity, takeover,
                     REFRESH_FIELDS, refresh_candidate, refresh_context, refresh_operation_id,
                     refresh_construction)


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
            "retry": 0, "publication-payloads": {}, "stop-revision": "0",
            "frozen": False, "publication-stage": None, "refresh": None,
            "refresh-stage": "absent", "refresh-integrations": [], "promotion-generation": "0",
            "preparations": []}


def candidate_digest(candidate):
    return digest(canonical(candidate)) if candidate else "0" * 64


CANDIDATE_EFFECTS = {"pr", "merge", "tag-object", "tag-ref"}
REFRESH_EFFECTS = {"refresh-object", "refresh-branch", "refresh-pr"}


def publication_ref_id(release):
    return digest(canonical({"kind": "tag-ref", "object-operation": release[6],
                             "tag": release[0] + "-v" + release[1],
                             "source": release[2], "object": release[5]}))


def reconciled(op):
    return op["state"] == "observed" or (op["state"] in {"intent", "superseded"} and op["observation"]
            and op["observation"]["status"] == "absent" and op["observation"]["complete"] is True)


def invalidate_promotion(state, current_dev):
    candidate = state["candidate"]
    if not candidate or candidate["dev"] == current_dev:
        return
    effects = [o for o in state["operations"].values() if o["kind"] in CANDIDATE_EFFECTS]
    require(all(reconciled(o) for o in effects), "dev-moved-before-promotion-reconciliation")
    if not state["frozen"]:
        for op in effects:
            if op["state"] == "intent":
                op["state"] = "superseded"
        state.update(candidate=None, evidence=[], approval=None, stage="active")


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
            require(not state["stopped"] and state["stage"] not in {"empty", "stopped"}, "impossible-claim-stage")
            require(decimal(event["generation"]) == decimal(state["generation"]) + 1, "wrong-owner-generation")
            require(event["repository"] == config["repository"] and event["workflow"] == config["workflow"], "wrong-owner-connection")
            if state["owner"]:
                takeover(state["owner"], transcript["owner"])
                require(all(reconciled(o) for o in state["operations"].values()), "unreconciled-operation-before-takeover")
            state["owner"] = {key: event[key] for key in ("repository", "workflow", "run", "attempt", "job", "generation", "operating-head")}
            state["generation"] = event["generation"]
        elif kind == "candidate":
            require(not state["frozen"] and not state["stopped"] and state["owner"] and state["stage"] in {"active", "candidate", "validated", "approved", "blocked", "waiting"}, "candidate-after-publication-or-unowned")
            require(all(reconciled(o) for o in state["operations"].values()), "candidate-before-effect-reconciliation")
            # Confirmed-absent old candidate effects remain in history but cannot
            # be proposed or acquire success on behalf of the replacement.
            for op in state["operations"].values():
                if op["kind"] in CANDIDATE_EFFECTS and op["state"] == "intent":
                    op["state"] = "superseded"
            old = state["candidate"]
            require(decimal(event["candidate-generation"]) == decimal(state["promotion-generation"]) + 1, "wrong-candidate-generation")
            state["promotion-generation"] = event["candidate-generation"]
            fields = ("candidate-generation", "dev", "master", "tree", "rules", "tool", "baselines", "selected", "classification", "versions", "migrations", "approval-required")
            selected = identifiers(event["selected"])
            require(selected and set(selected) <= set(identifiers(config["checks"])), "unsupported-coverage")
            state["candidate"] = {k: event[k] for k in fields}
            state.update(evidence=[], approval=None, releases=event.get("release", []), stage="candidate")
            for row in state["releases"]:
                require(row[2] == event["dev"], "release-source-candidate-mismatch")
            if state["releases"]:
                require(event["versions"] == ",".join(r[0] + ":" + r[1] for r in sorted(state["releases"])), "release-version-candidate-mismatch")
        elif kind == "refresh-result":
            require(state["owner"] and not state["stopped"], "unowned-or-stopped-refresh")
            result = document(event["payload"].encode("utf-8"))
            require(isinstance(result, dict) and result.get("status") in {"changed", "noop", "failed", "terminated-timeout"}, "invalid-refresh-result")
            if result["status"] != "changed":
                require(set(result) == {"status"}, "nonconsumable-refresh-has-candidate")
                require(state["refresh"] is None, "nonconsumable-replaces-candidate")
                state["refresh-stage"] = result["status"]
            else:
                require(set(result) == {"status", "candidate"}, "invalid-changed-refresh")
                candidate = refresh_candidate(result["candidate"])
                require(candidate["batch"] == state["batch"], "wrong-refresh-batch")
                context=refresh_context(transcript, candidate)
                preparation={'digest':context['construction']['inputs']['preparation'],'batch':state['batch']}
                if preparation not in state['preparations']:
                    require(len(state['preparations'])<16, 'preparation-replay-count-bound')
                    state['preparations'].append(preparation)
                old = state["refresh"]
                if old == candidate:
                    state["sequence"] = event["sequence"]
                    continue
                require(all(reconciled(o) for o in state["operations"].values()), "refresh-before-effect-reconciliation")
                if old:
                    observed_branches = [o for o in state["operations"].values() if o["kind"] == "refresh-branch" and o["state"] == "observed" and o["refresh"] == candidate_digest(old)]
                    require(candidate["base"] != old["base"] and
                            ((len(observed_branches) == 1 and candidate["previous"] == old["head"])
                             or (not observed_branches and candidate["previous"] == "-")), "unowned-or-unrequired-refresh-update")
                else:
                    require(candidate["previous"] == "-", "unowned-existing-refresh-branch")
                for op in state["operations"].values():
                    if op["kind"] in REFRESH_EFFECTS and op["state"] == "intent":
                        op["state"] = "superseded"
                invalidate_promotion(state, candidate["base"])
                state.update(refresh=candidate, **{"refresh-stage": "prepared"})
        elif kind == "refresh-integrated":
            candidate = state["refresh"]
            require(candidate and state["refresh-stage"] == "ready", "unverified-refresh-integration")
            integrated = document(event["payload"].encode("utf-8"))
            require(isinstance(integrated, dict) and set(integrated) == {"base", "head", "commit", "parents", "tree"}, "invalid-refresh-integration")
            require(integrated["base"] == candidate["base"] and integrated["head"] == candidate["head"]
                    and integrated["parents"] == [candidate["base"], candidate["head"]]
                    and integrated["tree"] == candidate["tree"], "stale-refresh-integration")
            from records import identity
            identity(integrated["commit"], 40)
            context = refresh_context(transcript, candidate, checks=True, current=True, current_dev=integrated["commit"])
            require(context.get("integration") == integrated and context.get("current-dev") == integrated["commit"], "unobserved-refresh-integration")
            require(integrated not in state["refresh-integrations"], "duplicate-refresh-integration")
            require(all(reconciled(o) for o in state["operations"].values()), "integration-before-effect-reconciliation")
            invalidate_promotion(state, integrated["commit"])
            state["refresh-integrations"].append(integrated)
            if state["frozen"]:
                state["refresh-stage"] = "next-opportunity"
            else:
                state["refresh-stage"] = "integrated"
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
                bound_candidate = candidate_digest(state["candidate"]) if op_kind in CANDIDATE_EFFECTS else None
                bound_refresh = candidate_digest(state["refresh"]) if op_kind in REFRESH_EFFECTS else None
                if op_kind in CANDIDATE_EFFECTS:
                    require(state["candidate"] is not None, "candidate-effect-without-candidate")
                if previous:
                    require(previous["payload"] == payload and previous["kind"] == op_kind, "changed-duplicate-operation")
                    require(previous["state"] not in {"observed", "superseded"}, "repeated-completed-or-superseded-operation")
                    require(previous["candidate"] == bound_candidate, "changed-operation-candidate")
                    require(previous["refresh"] == bound_refresh, "changed-operation-refresh")
                if op_kind in REFRESH_EFFECTS:
                    require(state['refresh'], 'missing-refresh-candidate')
                    context = refresh_context(transcript, state["refresh"], checks=op_kind == "refresh-pr")
                    object_plans=refresh_construction(context,state['refresh'])
                    if op_kind=='refresh-object':
                        remaining=[(oid,p) for oid,p in object_plans if not (oid in state['operations'] and state['operations'][oid]['state']=='observed')]
                        require(remaining and remaining[0]==(op_id,payload), 'wrong-next-refresh-object')
                        for dep in document(payload['dependencies'].encode()):
                            if dep['operation']!='-':
                                prerequisite=state['operations'].get(dep['operation'])
                                require(prerequisite and prerequisite['state']=='observed' and prerequisite['remote']==dep['sha'], 'unobserved-object-dependency')
                    else:
                        require({k:payload[k] for k in REFRESH_FIELDS}==state['refresh'] and op_id==refresh_operation_id(op_kind,payload), 'changed-fixed-refresh-operation')
                        require(all(oid in state['operations'] and state['operations'][oid]['state']=='observed' and state['operations'][oid]['payload']==p for oid,p in object_plans), 'refresh-ref-before-object-closure')
                    if op_kind == "refresh-pr":
                        branches = [o for o in state["operations"].values() if o["kind"] == "refresh-branch" and o["refresh"] == bound_refresh and o["state"] == "observed"]
                        require(len(branches) == 1 and context["branch"]["head"] == payload["head"], "pr-before-current-owned-branch")
                if op_kind == "pr":
                    require(all(payload[k] == state["candidate"][k] for k in ("dev", "master")), "stale-pr-payload")
                if op_kind == "merge":
                    require(not state["frozen"], "repeated-promotion")
                    require(state["stage"] in {"validated", "approved"}, "unvalidated-promotion")
                    require((state["candidate"]["approval-required"] == "0" and state["candidate"]["classification"] != "major" and state["candidate"]["migrations"] == "-") or state["approval"], "missing-exact-approval")
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
                        require(op_id == publication_ref_id(release), "changed-fixed-ref-operation")
                        object_op = state["operations"].get(release[6])
                        require(object_op and object_op["kind"] == "tag-object"
                                and object_op["state"] == "observed"
                                and object_op["remote"] == release[5]
                                and object_op["payload"]["tag"] == payload["tag"], "tag-ref-before-observed-object")
                if op_kind == "record":
                    require(payload["parent"] == state["owner"]["operating-head"], "stale-operating-parent")
                if op_kind == "cancel":
                    require(all(payload[k] == state["owner"][k] for k in ("run", "attempt", "workflow"))
                            and payload["jobs"] == state["owner"]["job"], "cancel-target-not-recorded-owner")
                state["operations"][op_id] = {"kind": op_kind, "payload": payload, "state": "intent", "observation": None, "phase": state["stage"], "candidate": bound_candidate, "refresh": bound_refresh, "remote": "-"}
            else:
                require(previous and previous["payload"] == payload and previous["kind"] == op_kind, "observation-without-matching-intent")
                if op_kind in CANDIDATE_EFFECTS:
                    require(previous["candidate"] == candidate_digest(state["candidate"])
                            and previous["state"] != "superseded", "stale-candidate-effect-observation")
                if op_kind in REFRESH_EFFECTS:
                    require(previous["state"] != "superseded" and
                            (previous["state"] == "observed" or previous["refresh"] == candidate_digest(state["refresh"])), "stale-refresh-effect-observation")
                supplied = transcript["observations"].get(op_id)
                require(isinstance(supplied, list), "missing-operation-observations")
                matches = [o for o in supplied if digest(canonical(o)) == observation]
                require(len(matches) == 1, "observation-digest-mismatch")
                observed = matches[0]
                result = reconcile(op_kind, payload, observed)
                if result == "applied":
                    require(remote == remote_identity(op_kind, payload, observed), "observed-remote-identity-mismatch")
                require(status == {"applied": "observed", "absent": "intent", "unknown": "unknown", "conflict": "conflict"}[result], "false-observation-result")
                already_observed = previous["state"] == "observed"
                if already_observed:
                    require(result == "applied" and remote == previous["remote"], "contradictory-completed-effect-observation")
                if result == "applied" and op_kind == "record":
                    current_head = state["owner"]["operating-head"]
                    target = observed["target"]
                    require(current_head == target["head"]
                            or current_head in {item["commit"] for item in target["history"]}
                            or (not already_observed and current_head == payload["parent"]),
                            "stale-operating-head-observation")
                previous.update(state=status, observation=observed, remote=remote)
                if result == "applied" and op_kind == "record":
                    state["owner"]["operating-head"] = observed["target"]["head"]
                if already_observed:
                    state["sequence"] = event["sequence"]
                    continue
                if result == "applied" and op_kind == "merge":
                    state.update(frozen=True, **{"publication-stage": "promoted"})
                if result == "applied" and op_kind.startswith("tag"):
                    state["publication-stage"] = "publishing"
                if result == "applied" and op_kind in {'refresh-branch','refresh-pr'}:
                    state["refresh-stage"] = "branch-ready" if op_kind == "refresh-branch" else "ready"
                if result in {"unknown", "conflict"}:
                    state["stage"] = "blocked"
                elif not state["stopped"] and result == "applied" and op_kind == "merge":
                    state["stage"] = "promoted"
                elif not state["stopped"] and result == "applied" and op_kind.startswith("tag"):
                    state["stage"] = "publishing"
                elif not state["stopped"] and result == "absent":
                    state["stage"] = previous["phase"]
        elif kind == "retry-wait":
            require(not state["stopped"] and state["stage"] not in {"empty", "stopped"} and event["transient"] == "1", "nontransient-or-invalid-wait")
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
            if state["frozen"]:
                state.update(stopped=False, stage=state["publication-stage"])
            else:
                state.update(stopped=False, stage="candidate" if state["candidate"] else "active", evidence=[], approval=None)
        elif kind == "complete":
            require(state["stage"] in {"active", "publishing", "promoted"}, "impossible-completion")
            require(all(o["state"] in {"observed", "superseded"} for o in state["operations"].values()), "incomplete-operations")
            require(state["refresh"] is None or state["refresh-stage"] in {"ready", "integrated", "next-opportunity"}, "incomplete-refresh")
            if state["frozen"] and state["candidate"]["versions"] != "-":
                require(state["releases"], "missing-publication-plan")
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


def preview(directory, transcript, request, approved, before=0, prior="0" * 64):
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
    events, prior = history(root / "history", before, prior)
    if events:
        start = events[0]
        require(start["kind"] == "batch-start" and start["control"] == approved["control"] and start["manifest"] == approved["manifest"] and start["approval-provenance"] == approved["approval"] and start["approved-master"] == approved["master"], "wrong-retained-batch-control")
        # Pinned config is supplied at its recorded blob SHA, not current config.
        actual = blob_identity(config_data)
        require(actual == start["config"], "changed-pinned-batch-config")
    state = reduce(events, config, transcript)
    if state["refresh"]:
        expected_dev = state["refresh-integrations"][-1]["commit"] if state["refresh-stage"] in {"integrated", "next-opportunity"} else state["refresh"]["base"]
        pending_pr = any(o["kind"] == "refresh-pr" and o["state"] == "intent" for o in state["operations"].values())
        current = refresh_context(transcript, state["refresh"], checks=pending_pr, current=True, current_dev=expected_dev)
        require(current.get("branch") == {"batch": state["batch"], "branch": state["refresh"]["branch"],
                "head": state["refresh"]["head"] if state["refresh-stage"] != "prepared" else state["refresh"]["previous"]}, "stale-current-refresh-head")
    actual_index = read(root / "current/index.tsv")
    parse(actual_index, "index")
    require(actual_index == index(state, prior), "history-index-mismatch")
    require(request["mode"] == "preview", "live-mode-unavailable")
    if state["candidate"] or state["refresh"]:
        authenticate(transcript, config, request, candidate_digest(state["candidate"] or state["refresh"]))
    elif request["candidate"] != "0" * 64:
        require(False, "missing-request-candidate")
    if stop["stop"] == "1" or state["stopped"]:
        return {"outcome": "stopped", "proposed": 0}
    # Safe public output reveals neither repository connection nor raw records.
    pending = [o for o in state["operations"].values() if o["state"] == "intent"]
    return {"outcome": "preview", "stage": state["stage"], "proposed": len(pending)}


def project_range(directory, transcript, approved, before, prior):
    """Protocol-3 replay interface; original event bytes and verified boundary only."""
    root = Path(directory)
    config_data = read(root / "config/operating.tsv")
    config = parse(config_data, "config")
    events, last = history(root / "history", before, prior)
    require(not events or (config["enabled"] == "1" and config["actors"] != "-" and config["checks"] != "-"), "disabled-retained-batch")
    if events:
        start = events[0]
        require(start["kind"] == "batch-start" and start["control"] == approved["control"]
                and start["manifest"] == approved["manifest"]
                and start["approval-provenance"] == approved["approval"]
                and start["approved-master"] == approved["master"]
                and start["config"] == blob_identity(config_data), "wrong-retained-range-context")
    state = reduce(events, config, transcript)
    pending = sum(o["state"] == "intent" for o in state["operations"].values())
    return index(state, last), state["stage"], pending
