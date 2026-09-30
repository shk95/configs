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
        expected = {"parent": payload["parent"]} if kind == "record" else {}
        require(target == expected, "unconfirmed-absence")
        return "absent"
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
    require(set(transcript) == {"source", "checks", "owner", "observations", "protection"}, "unknown-transcript-field")
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
