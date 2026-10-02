"""Pure API contract: construct requests and interpret supplied observations only."""
# INV repository/release-control-preview-only
import json
import hashlib
import re
from datetime import datetime, timezone
from records import Refusal, canonical, digest, identity, require

API_VERSION = "2026-03-10"
BOUNDS = {"writer_minutes": 15, "api_seconds": 30, "cancel_seconds": 30,
          "cancel_limit_seconds": 300, "retry_minutes": [5, 15, 30],
          "wait_job_minutes": [6, 16, 31]}


def document(data):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "duplicate-json-key")
            result[key] = value
        return result
    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=unique,
                          parse_constant=lambda _: (_ for _ in ()).throw(Refusal("nonfinite-json")))
    except (UnicodeError, json.JSONDecodeError):
        raise Refusal("invalid-transcript-json") from None


PAYLOADS = {
    "record": {"repository", "parent", "commit", "event", "index"},
    "pr": {"repository", "head", "base", "dev", "master", "body-operation"},
    "merge": {"repository", "number", "dev", "master", "tree"},
    "tag-object": {"repository", "tag", "source", "annotation", "tagger-time", "tagger-name", "tagger-email", "initial-run", "object"},
    "tag-ref": {"repository", "tag", "object"},
    "cancel": {"repository", "run", "attempt", "workflow", "jobs"},
}

REFRESH_FIELDS = {"batch", "source", "base", "parent", "head", "tree", "before-lock",
                  "lock", "utility-source", "utility-manifest", "source-fingerprint",
                  "previous", "branch"}
for refresh_kind in ("refresh-branch", "refresh-pr"):
    PAYLOADS[refresh_kind] = REFRESH_FIELDS | {"repository"}


def refresh_branch(batch):
    identity(batch)
    return "feature/unixlike-refresh-" + batch


def refresh_candidate(value):
    require(isinstance(value, dict) and set(value) == REFRESH_FIELDS, "invalid-refresh-candidate")
    require(all(isinstance(v, str) for v in value.values()), "invalid-refresh-value")
    for name in ("source", "base", "parent", "head", "tree", "utility-source"):
        identity(value[name], 40)
    for name in ("batch", "before-lock", "lock", "utility-manifest", "source-fingerprint"):
        identity(value[name])
    require(value["previous"] == "-" or identity(value["previous"], 40), "invalid-refresh-previous")
    require(value["branch"] == refresh_branch(value["batch"]), "wrong-refresh-branch")
    require(value["head"] != value["parent"] and value["before-lock"] != value["lock"], "unchanged-refresh-candidate")
    require(value["source"] == value["parent"], "wrong-refresh-source")
    require(value["previous"] != "-" or value["parent"] == value["base"], "wrong-initial-refresh-parent")
    return value


def refresh_operation_id(kind, payload):
    require(kind in {"refresh-branch", "refresh-pr"}, "wrong-refresh-kind")
    refresh_candidate({k: payload[k] for k in REFRESH_FIELDS})
    return digest(canonical({"kind": kind, "payload": payload}))


def refresh_context(transcript, candidate, *, checks=False, current=False, current_dev=None):
    supplied = transcript.get("refresh")
    require(isinstance(supplied, dict) and set(supplied) == {"revisions", "current"}
            and isinstance(supplied["revisions"], list), "invalid-refresh-transcript")
    if current:
        context = supplied["current"]
    else:
        matches = [c for c in supplied["revisions"] if isinstance(c, dict) and c.get("prepared") == candidate]
        require(len(matches) == 1, "ambiguous-refresh-provenance")
        context = matches[0]
    require(isinstance(context, dict) and set(context) == {"prepared", "proof", "current-dev", "branch", "checks", "integration"}, "missing-refresh-context")
    require(context["prepared"] == candidate and context["current-dev"] == (current_dev or candidate["base"]), "stale-refresh-source-or-base")
    proof = context["proof"]
    require(isinstance(proof, dict) and set(proof) == {"head-parents", "merge-parents", "changed", "before-lock", "lock", "before-mode", "mode"}, "missing-refresh-preparation-proof")
    require(proof["head-parents"] == [candidate["parent"]] and proof["changed"] == ["unixlike/flake.lock"]
            and proof["before-lock"] == candidate["before-lock"] and proof["lock"] == candidate["lock"]
            and type(proof["mode"]) is int and type(proof["before-mode"]) is int
            and proof["mode"] == proof["before-mode"] and 0 <= proof["mode"] <= 0o777, "contaminated-refresh-preparation")
    expected_merge = [] if candidate["previous"] == "-" else [candidate["previous"], candidate["base"]]
    require(proof["merge-parents"] == expected_merge, "wrong-refresh-update-parents")
    observed_branch = context["branch"]
    require(isinstance(observed_branch, dict) and set(observed_branch) == {"batch", "branch", "head"}
            and observed_branch["batch"] == candidate["batch"] and observed_branch["branch"] == candidate["branch"], "wrong-refresh-branch-owner")
    require(observed_branch["head"] in {candidate["previous"], candidate["head"]}, "stale-refresh-branch-head")
    expected = {"head": candidate["head"], "base": candidate["base"], "tree": candidate["tree"],
                "lock": candidate["lock"], "name": "Required checks", "app": "15368"}
    supplied_checks = context["checks"]
    if supplied_checks is not None:
        require(isinstance(supplied_checks, dict) and set(supplied_checks) == set(expected) | {"status"}
                and all(supplied_checks[k] == v for k, v in expected.items())
                and supplied_checks["status"] in {"success", "failure", "pending", "unknown"}, "invalid-current-refresh-checks")
    if checks:
        require(supplied_checks is not None and supplied_checks["status"] == "success", "missing-current-refresh-checks")
    return context


def tag_identity(payload):
    """Canonical synthetic annotation object; actual API byte behavior needs rollout proof."""
    date = datetime.strptime(payload["tagger-time"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    require(not any(c in payload["tagger-name"] + payload["tagger-email"] for c in "<>\n\r\t"), "invalid-tagger-identity")
    raw = ("object " + payload["source"] + "\ntype commit\ntag " + payload["tag"]
           + "\ntagger " + payload["tagger-name"] + " <" + payload["tagger-email"]
           + "> " + str(int(date.timestamp())) + " +0000\n\n" + payload["annotation"]).encode("utf-8")
    return hashlib.sha1(b"tag " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def operation(kind, payload):
    require(kind in PAYLOADS and isinstance(payload, dict) and set(payload) == PAYLOADS[kind], "invalid-operation-payload")
    require(all(isinstance(v, str) and v and not any(c in v for c in ("\r\t\0" if k == "annotation" else "\r\n\t\0")) for k, v in payload.items()), "invalid-payload-value")
    require(payload["repository"] == "shk95/configs" or kind == "record", "wrong-target-repository")
    require(re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", payload["repository"]) is not None, "invalid-target-connection")
    if kind in {"refresh-branch", "refresh-pr"}:
        refresh_candidate({k: payload[k] for k in REFRESH_FIELDS})
        prefix = "/repos/" + payload["repository"]
        if kind == "refresh-branch":
            creating = payload["previous"] == "-"
            method = "POST" if creating else "PATCH"
            path = prefix + ("/git/refs" if creating else "/git/refs/heads/" + payload["branch"])
            body = {"ref": "refs/heads/" + payload["branch"], "sha": payload["head"]} if creating else {"sha": payload["head"], "force": False}
        else:
            method, path = "POST", prefix + "/pulls"
            body = {"head": payload["branch"], "base": "dev", "title": "Refresh Unix-like dependencies",
                    "body": "refresh-operation=" + refresh_operation_id(kind, payload)}
        return {"api-version": API_VERSION, "method": method, "path": path, "body": body,
                "payload-digest": digest(canonical(payload))}
    for key in {"parent", "commit", "dev", "master", "tree", "source", "object"} & set(payload):
        identity(payload[key], 40)
    for key in {"event", "index", "body-operation"} & set(payload):
        identity(payload[key])
    if kind == "pr":
        require(payload["head"] == "dev" and payload["base"] == "master", "wrong-promotion-source")
    if kind.startswith("tag"):
        require(re.fullmatch(r"(unixlike|windows|common)-v[1-9][0-9]*\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", payload["tag"]) is not None, "invalid-tag-name")
    for key in {"number", "run", "attempt", "workflow", "initial-run"} & set(payload):
        require(re.fullmatch(r"[1-9][0-9]*", payload[key]) is not None, "invalid-endpoint-id")
    if kind == "tag-object":
        require(re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", payload["tagger-time"]) is not None, "noncanonical-tagger-time")
        try:
            datetime.strptime(payload["tagger-time"], "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            raise Refusal("invalid-tagger-time") from None
        require(payload["object"] == tag_identity(payload), "tag-object-byte-identity-mismatch")
    prefix = "/repos/" + payload["repository"]
    method, path, body = {
        "record": ("PATCH", prefix + "/git/refs/heads/operations", {"sha": payload.get("commit"), "force": False}),
        "pr": ("POST", prefix + "/pulls", {"head": "dev", "base": "master", "body": payload.get("body-operation")}),
        "merge": ("PUT", prefix + "/pulls/" + payload.get("number", "-") + "/merge", {"sha": payload.get("dev"), "merge_method": "merge"}),
        "tag-object": ("POST", prefix + "/git/tags", {"tag": payload.get("tag"), "message": payload.get("annotation"), "object": payload.get("source"), "type": "commit", "tagger": {"name": payload.get("tagger-name"), "email": payload.get("tagger-email"), "date": payload.get("tagger-time")}}),
        "tag-ref": ("POST", prefix + "/git/refs", {"ref": "refs/tags/" + payload.get("tag", "-"), "sha": payload.get("object")}),
        "cancel": ("POST", prefix + "/actions/runs/" + payload.get("run", "-") + "/cancel", {}),
    }[kind]
    return {"api-version": API_VERSION, "method": method, "path": path,
            "body": body, "payload-digest": digest(canonical(payload))}


def reconcile(kind, payload, observation):
    """Unknown responses are decided by target observation, never acknowledgement."""
    operation(kind, payload)
    require(isinstance(observation, dict) and set(observation) == {"status", "target", "complete"}, "invalid-observation-schema")
    require(type(observation["complete"]) is bool and observation["complete"], "incomplete-observation")
    status, target = observation["status"], observation["target"]
    require(status in {"present", "absent", "unknown"}, "invalid-observation-status")
    require(isinstance(target, dict), "invalid-observation-target")
    if status == "unknown":
        return "unknown"
    if status == "absent":
        expected = ({"parent": payload["parent"]} if kind == "record" else
                    {"batch": payload["batch"], "branch": payload["branch"], "head": payload["previous"]}
                    if kind == "refresh-branch" else {})
        require(target == expected, "unconfirmed-absence")
        return "absent"
    if kind in {"refresh-branch", "refresh-pr"}:
        candidate = {k: payload[k] for k in REFRESH_FIELDS}
        if kind == "refresh-branch":
            require(set(target) == {"candidate"}, "invalid-refresh-branch-observation")
            return "applied" if target["candidate"] == candidate else "conflict"
        require(set(target) == {"matches"} and isinstance(target["matches"], list), "invalid-refresh-pr-observation")
        if len(target["matches"]) != 1:
            return "conflict"
        match = target["matches"][0]
        require(isinstance(match, dict) and set(match) == {"number", "repository", "base-ref", "state", "candidate", "checks"}, "invalid-refresh-pr-match")
        require(isinstance(match["number"], str) and re.fullmatch(r"[1-9][0-9]*", match["number"]), "missing-refresh-pr-number")
        expected_checks = {"head": payload["head"], "base": payload["base"], "tree": payload["tree"], "lock": payload["lock"], "name": "Required checks", "app": "15368", "status": "success"}
        return "applied" if (match["repository"] == payload["repository"] and match["base-ref"] == "dev"
                             and match["state"] in {"open", "merged"} and match["candidate"] == candidate
                             and match["checks"] == expected_checks) else "conflict"
    if kind == "record":
        require(set(target) == {"history", "head"} and isinstance(target["history"], list), "incomplete-record-history")
        identity(target["head"], 40)
        commits, events, matches, previous = set(), set(), [], None
        for item in target["history"]:
            require(isinstance(item, dict) and set(item) == {"parent", "commit", "event", "index"}, "invalid-history-observation")
            identity(item["parent"], 40); identity(item["commit"], 40)
            identity(item["event"]); identity(item["index"])
            require(item["commit"] not in commits and item["event"] not in events
                    and (previous is None or item["parent"] == previous), "contradictory-record-history")
            commits.add(item["commit"]); events.add(item["event"]); previous = item["commit"]
            if item["event"] == payload["event"]:
                matches.append(item)
        require(previous == target["head"], "incomplete-record-head-history")
        return "applied" if matches == [{k: payload[k] for k in ("parent", "commit", "event", "index")}] else "conflict"
    if kind == "pr":
        require(set(target) == {"matches"} and isinstance(target["matches"], list), "invalid-pr-observation")
        if len(target["matches"]) != 1:
            return "conflict"
        match = target["matches"][0]
        require(isinstance(match, dict) and set(match) == {"number", "payload"}
                and isinstance(match["number"], str) and re.fullmatch(r"[1-9][0-9]*", match["number"]), "missing-pr-identity")
        return "applied" if match["payload"] == payload else "conflict"
    if kind == "merge":
        require(set(target) == {"merged", "commit", "parents", "tree", "source"}, "invalid-merge-observation")
        require(type(target["merged"]) is bool, "invalid-merged-status")
        identity(target["commit"], 40)
        return "applied" if target == {"merged": True, "commit": target["commit"], "parents": [payload["master"], payload["dev"]], "tree": payload["tree"], "source": payload["dev"]} else "conflict"
    if kind == "cancel":
        require(set(target) == {"run", "attempt", "workflow", "jobs", "latest-attempt", "terminal"}, "invalid-cancel-observation")
        return "applied" if target == {"run": payload["run"], "attempt": payload["attempt"], "workflow": payload["workflow"], "jobs": payload["jobs"], "latest-attempt": payload["attempt"], "terminal": True} else "unknown"
    return "applied" if target == payload else "conflict"


def remote_identity(kind, payload, observation):
    require(observation["status"] == "present", "missing-remote-identity")
    target = observation["target"]
    if kind == "refresh-branch":
        return payload["head"]
    if kind == "refresh-pr":
        return target["matches"][0]["number"]
    if kind == "record":
        return payload["commit"]
    if kind == "merge":
        return target["commit"]
    if kind == "pr":
        return target["matches"][0]["number"]
    if kind == "cancel":
        return target["run"]
    return target["object"]


def authenticate(transcript, config, request, candidate_digest):
    require(set(transcript) in ({"source", "checks", "owner", "observations", "protection"},
                              {"source", "checks", "owner", "observations", "protection", "refresh"}), "unknown-transcript-field")
    sources = transcript["source"]
    expected = {"repository": config["repository"], "workflow": config["workflow"],
                "actor": request["actor"], "run": request["run"], "attempt": request["attempt"],
                "ref": "refs/heads/master", "event": "workflow_dispatch",
                "mode": request["mode"], "candidate": candidate_digest}
    require(isinstance(sources, list) and all(isinstance(s, dict) and set(s) == set(expected) for s in sources), "invalid-source-observations")
    require(sum(s == expected for s in sources) == 1 and request["ref"] == "refs/heads/master", "unauthenticated-request")
    require(request["actor"] in config["actors"].split(","), "unauthorized-actor")
    require(request["candidate"] == candidate_digest, "stale-request-candidate")
    protection = transcript["protection"]
    expected_protection = {"required": "Required checks", "app": "15368", "administrators": True,
                           "conversations": True, "force": False, "deletion": False,
                           "dev-strict": True, "master-strict": False}
    require(isinstance(protection, dict) and protection == expected_protection
            and all(type(protection[k]) is type(v) for k, v in expected_protection.items()), "missing-or-mismatched-protection")


def takeover(owner, observed):
    require(isinstance(observed, dict) and set(observed) == {"owner", "latest-attempt", "jobs", "complete", "status"}, "incomplete-owner-observation")
    require(observed["owner"] == owner and observed["latest-attempt"] == owner["attempt"], "changed-owner-attempt")
    require(observed["complete"] is True and observed["status"] == "terminal", "unconfirmed-termination")
    require(observed["jobs"] == {owner["job"]: "terminal"}, "unconfirmed-writer-jobs")
    return True


def opportunity(hour, refresh):
    require(type(hour) is int and 0 <= hour <= 23, "invalid-opportunity-hour")
    require(refresh in {"ready", "waiting", "failed", "absent"}, "invalid-refresh-state")
    if hour < 6:
        return "not-due"
    if refresh == "waiting" and hour < 7:
        return "wait"
    # Cutoff never means canceling the refresh. It changes opportunity selection.
    return "reconcile"


def refresh_window(day, hour, seen, *, manual=False, refresh="absent", promoted=False):
    """Supplied synthetic calendar observation; never reads a clock or schedules."""
    require(isinstance(day, str) and re.fullmatch(r"\d{4}-\d\d-\d\d", day), "invalid-refresh-day")
    try:
        datetime.strptime(day, "%Y-%m-%d")
    except ValueError:
        raise Refusal("invalid-refresh-day") from None
    require(isinstance(seen, list) and all(isinstance(d, str) for d in seen)
            and len(set(seen)) == len(seen), "invalid-refresh-days")
    require(type(manual) is bool and type(promoted) is bool, "invalid-opportunity-flag")
    selection = opportunity(hour, refresh)
    action = "join" if day in seen else "start" if manual or hour == 5 else "missed" if hour > 5 else "not-due"
    return {"refresh": action, "promotion": selection,
            "integration": "next-opportunity" if promoted else "invalidate"}
