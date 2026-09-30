#!/usr/bin/env python3
"""Synthetic capture/apply and pure Nix consumer-validation fixtures.

INV unixlike/host-written-payload-projected
"""
import argparse
import contextlib
import copy
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
from unittest.mock import patch

DOMAIN = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("capture", DOMAIN / "tool/darwin-capture/engine.py")
c = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(c)


def refuses(function, kind=c.Refusal):
    try:
        function()
    except kind:
        return
    raise AssertionError("expected refusal")


def quiet(function):
    with contextlib.redirect_stdout(io.StringIO()) as output:
        status = function()
    return status, output.getvalue()


def test(work):
    host = work / "observed.json"
    hotkeys = work / "observed-hotkeys.json"
    desired = c.defaults("karabiner")
    wanted_hotkeys = c.defaults("symbolic-hotkeys")
    host.write_bytes(c.encoded({**desired, "unmanaged": {"runtime": True}}))
    observed_hotkeys = copy.deepcopy(wanted_hotkeys)
    observed_hotkeys["AppleSymbolicHotKeys"]["7"] = {"enabled": True, "value": None}
    observed_hotkeys["runtime"] = "outside"
    hotkeys.write_bytes(c.encoded(observed_hotkeys))
    first = work / "karabiner-document.json"
    second = work / "hotkey-document.json"

    def preview(targets=None, units=None, name="proposal"):
        output = work / (name + ".json")
        args = argparse.Namespace(unit=units or ["karabiner", "symbolic-hotkeys"],
                                  document=list(map(str, targets or [first, second])),
                                  output=str(output), host=str(host), hotkeys_host=str(hotkeys))
        quiet(lambda: c.preview(args))
        assert output.stat().st_mode & 0o777 == 0o600
        return output

    def save(proposal):
        return quiet(lambda: c.save(argparse.Namespace(preview=str(proposal))))

    # Finite scope/whole parents, first explicit destination, atomic document
    # replacement, and regeneration from saved data rather than hardcoded defaults.
    proposal = preview()
    assert save(proposal)[0] == 0
    assert c.document("karabiner", first.read_bytes())["settings"] == desired
    assert c.document("symbolic-hotkeys", second.read_bytes())["settings"] == wanted_hotkeys
    assert "unmanaged" not in json.loads(first.read_bytes())["settings"]
    assert "7" not in json.loads(second.read_bytes())["settings"]["AppleSymbolicHotKeys"]
    assert first.stat().st_mode & 0o777 == second.stat().st_mode & 0o777 == 0o600
    assert save(preview(name="unchanged"))[0] == 0
    modified = copy.deepcopy(desired)
    modified["profiles"].append({"name": "Second", "selected": True})
    modified["profiles"][0].pop("virtual_hid_keyboard")
    host.write_bytes(c.encoded({**modified, "unmanaged": "survives outside capture"}))
    assert save(preview(name="whole-array"))[0] == 0
    assert json.loads(first.read_bytes())["settings"] == modified
    assert len(json.loads(first.read_bytes())["settings"]["profiles"]) == 2

    # Host/configs ownership and dormant recovery data, false disable, required
    # parents/entries, app-normalized empties and valid native-tested nested empties.
    dormant = {"formatVersion": 1, "source": "configs", "settings": {"dormant": {"arbitrary": None}}}
    assert c.document("karabiner", c.encoded(dormant)) == dormant
    dormant["source"] = "host"
    refuses(lambda: c.document("karabiner", c.encoded(dormant)))
    valid_empty = copy.deepcopy(desired)
    rule = valid_empty["profiles"][0]["complex_modifications"]["rules"][0]
    rule["description"] = ""
    rule["manipulators"][0]["from"]["modifiers"]["optional"] = []
    rule["manipulators"][0]["parameters"] = {}
    c.validate_settings("karabiner", valid_empty)
    valid_disable = copy.deepcopy(wanted_hotkeys)
    valid_disable["AppleSymbolicHotKeys"]["60"]["enabled"] = False
    c.validate_settings("symbolic-hotkeys", valid_disable)
    bad_settings = []
    for parent, value in [("global", {}), ("global", None), ("profiles", []), ("profiles", [{}]), ("profiles", [None])]:
        v = copy.deepcopy(desired)
        v[parent] = value
        bad_settings.append(("karabiner", v))
    for key in c.CONTRACT["units"]["karabiner"]["unstableEmptyProfileKeys"]:
        v = copy.deepcopy(desired)
        v["profiles"][0][key] = [] if key in c.CONTRACT["units"]["karabiner"]["profileArrayKeys"] else {}
        bad_settings.append(("karabiner", v))
    v = copy.deepcopy(desired)
    del v["global"]
    bad_settings.append(("karabiner", v))
    for entry, value in [("60", None), ("61", "deleted")]:
        v = copy.deepcopy(wanted_hotkeys)
        v["AppleSymbolicHotKeys"][entry] = value
        bad_settings.append(("symbolic-hotkeys", v))
    v = copy.deepcopy(wanted_hotkeys)
    del v["AppleSymbolicHotKeys"]["60"]
    bad_settings.append(("symbolic-hotkeys", v))
    for number in [-9223372036854775809, 9223372036854775808]:
        v = copy.deepcopy(wanted_hotkeys)
        v["AppleSymbolicHotKeys"]["60"]["value"]["parameters"][0] = number
        bad_settings.append(("symbolic-hotkeys", v))
    v = copy.deepcopy(wanted_hotkeys)
    v["AppleSymbolicHotKeys"]["60"]["enabled"] = 0
    bad_settings.append(("symbolic-hotkeys", v))
    v = copy.deepcopy(wanted_hotkeys)
    v["AppleSymbolicHotKeys"]["60"]["value"]["parameters"] = []
    bad_settings.append(("symbolic-hotkeys", v))
    for unit, v in bad_settings:
        refuses(lambda u=unit, value=v: c.validate_settings(u, value))

    # Strict original-byte JSON: escaped-equivalent duplicate keys, nested
    # duplicates, malformed/trailing bytes, UTF-8/surrogate/nonfinite refusals.
    malformed = [b'{"a":1,"\\u0061":2}', b'{"a":{"x":1,"x":2}}', b'{"a":1} trailing',
                 b'{"a":', b'{"a":"\xff"}', b'{"a":NaN}', b'{"a":"\\ud800"}']
    for raw in malformed:
        refuses(lambda r=raw: c.decode(r))
    assert c.decode(b'{"a":{"x":1},"b":{"x":2},"string":"x\\\"y,{}[]"}')["b"]["x"] == 2
    bad_envelopes = [dict(formatVersion=True, source="host", settings=desired),
                     dict(formatVersion=2, source="host", settings=desired),
                     dict(formatVersion=1, source="auto", settings=desired),
                     dict(formatVersion=1, source="host", settings=desired, extra=True)]
    for envelope in bad_envelopes:
        refuses(lambda v=envelope: c.document("karabiner", c.encoded(v)))

    # Every Nix document consumer validates the same shape and raw bytes as
    # the runtime tool, including dormant data and valid/refused empties.
    validation = DOMAIN / "tool/darwin-capture/validation.nix"
    contract = c.CONCERN / "units.json"

    def nix(unit, raw):
        path = work / "nix-document.json"
        path.write_bytes(raw)
        expr = f'(import {validation} {{lib={{}};contract=builtins.fromJSON (builtins.readFile {contract});}}).document "{unit}" {path}'
        return subprocess.run(["nix", "eval", "--impure", "--json", "--expr", expr], capture_output=True)

    for unit, settings in [("karabiner", desired), ("karabiner", valid_empty), ("symbolic-hotkeys", valid_disable)]:
        doc = {"formatVersion": 1, "source": "host", "settings": settings}
        r = nix(unit, c.encoded(doc))
        assert r.returncode == 0, r.stderr.decode()
        assert json.loads(r.stdout) == c.document(unit, c.encoded(doc))
    dormant["source"] = "configs"
    assert nix("karabiner", c.encoded(dormant)).returncode == 0
    for unit, settings in bad_settings:
        assert nix(unit, c.encoded({"formatVersion": 1, "source": "host", "settings": settings})).returncode != 0
    for raw in malformed:
        assert nix("karabiner", raw).returncode != 0
    for envelope in bad_envelopes:
        assert nix("karabiner", c.encoded(envelope)).returncode != 0
    # Duplicate key scopes are independent and strings cannot spoof structural tokens.
    assert nix("karabiner", c.encoded({"formatVersion": 1, "source": "configs", "settings": {"a": {"x": 1}, "b": {"x": 2}, "s": "x\"y,{}[]"}})).returncode == 0

    # Prospective path guards and aliases refuse before preparing any writes.
    # Packaging may copy a concern to a store leaf; its ancestors must not
    # become arbitrary protected roots such as / while the store stays guarded.
    with patch.object(c, "CONCERN", Path("/nix/store/synthetic-karabiner")):
        assert c.guard_path(work / "packaged-destination.json", []) == work / "packaged-destination.json"
        refuses(lambda: c.guard_path(Path("/nix/store/refused.json"), []))
    symlink = work / "symlink.json"
    symlink.symlink_to(first)
    hardlink = work / "hardlink.json"
    os.link(first, hardlink)
    for destination in [symlink, hardlink, host, DOMAIN / "should-not-write.json", Path("/nix/store/should-not-write.json"), work / "missing-parent/file.json"]:
        refuses(lambda d=destination: preview([d], ["karabiner"], "refused-path"))
    app = work / "Synthetic.APP/Contents"
    app.mkdir(parents=True)
    refuses(lambda: preview([app / "settings.json"], ["karabiner"], "bundle-refusal"))
    refuses(lambda: preview([Path("/Applications/settings.json")], ["karabiner"], "applications-refusal"))
    synthetic_home = work / "synthetic-home"
    (synthetic_home / "Applications").mkdir(parents=True)
    with patch.object(c.Path, "home", return_value=synthetic_home):
        refuses(lambda: preview([synthetic_home / "Applications/settings.json"], ["karabiner"], "home-applications-refusal"))
    refuses(lambda: preview([second, second], name="alias"))
    hardlink.unlink()
    refuses(lambda: c.prepare(["karabiner", "karabiner"], [str(first), str(second)], [c.reader_for("karabiner", argparse.Namespace(host=str(host))), c.reader_for("karabiner", argparse.Namespace(host=str(host)))]))
    refuses(lambda: c.read_reader({"kind": "file", "path": str(work / "absent-reader")}), c.Unavailable)

    # Any input byte/sibling, target identity/content/mode or tool binding change
    # invalidates the reviewed proposal; tampering never silently recaptures.
    stale = preview(name="stale-input")
    host.write_bytes(c.encoded({**modified, "unmanaged": "changed sibling"}))
    refuses(lambda: save(stale))
    stale = preview(name="stale-target")
    first.write_bytes(c.encoded({"formatVersion": 1, "source": "configs", "settings": {}}))
    refuses(lambda: save(stale))
    stale = preview(name="tampered")
    v = json.loads(stale.read_bytes())
    v["entries"][0]["document"]["settings"]["global"]["check_for_updates"] = True
    stale.write_bytes(c.encoded(v))
    refuses(lambda: save(stale))
    stale = preview(name="stale-tool")
    v = json.loads(stale.read_bytes())
    v["tool"]["engine"] = "0" * 64
    stale.write_bytes(c.encoded(v))
    refuses(lambda: save(stale))
    stale = preview(name="stale-mode")
    first.chmod(0o644)
    refuses(lambda: save(stale))
    first.chmod(0o600)

    # Prepare-all rejects a malformed second reader before first writes. A later
    # write failure preserves completed documents, reports all outcomes, requires
    # a fresh preview, and leaves no partly written JSON or leftover private temp.
    before = first.read_bytes()
    good_hotkeys = hotkeys.read_bytes()
    hotkeys.write_bytes(b'{broken')
    refuses(lambda: preview(name="prepare-all"))
    assert first.read_bytes() == before and not (work / "prepare-all.json").exists()
    hotkeys.write_bytes(good_hotkeys)
    partial = preview(name="partial")
    real_replace = c.atomic_replace
    calls = []

    def fail_second(path, *args):
        calls.append(path)
        if len(calls) == 2:
            raise OSError("synthetic second replacement failure")
        return real_replace(path, *args)

    # Both destinations must actually need writes for the second failure case.
    second.write_bytes(c.encoded({"formatVersion": 1, "source": "configs", "settings": {}}))
    partial.unlink()
    partial = preview(name="partial")
    before_second = second.read_bytes()
    with patch.object(c, "atomic_replace", side_effect=fail_second):
        status, output = save(partial)
    result = json.loads(output)
    assert status == 1 and [r["state"] for r in result["results"]] == ["completed", "incomplete"]
    assert second.read_bytes() == before_second
    refuses(lambda: save(partial))
    assert save(preview(name="retry"))[0] == 0
    assert not list(work.glob(".darwin-capture-*"))
    prior = first.read_bytes()
    failure = preview(name="atomic-failure")
    # Change observed state to demand a new write, then create a fresh proposal.
    v = json.loads(host.read_bytes())
    v["global"]["show_in_menu_bar"] = False
    host.write_bytes(c.encoded(v))
    failure.unlink()
    failure = preview(name="atomic-failure")
    with patch.object(c.os, "replace", side_effect=OSError("synthetic atomic rename failure")):
        assert save(failure)[0] == 1
    assert first.read_bytes() == prior and not list(work.glob(".darwin-capture-*"))

    # A permanent apply adapter consumes the same contract/projection and keeps
    # runtime siblings. Disabled/unselected units perform no reads or writes.
    settings_path = work / "adapter-settings.json"
    settings_path.write_bytes(c.encoded(desired))
    hotkeys_settings = work / "adapter-hotkeys.json"
    hotkeys_settings.write_bytes(c.encoded(valid_disable))
    args = argparse.Namespace(command="apply", unit=["karabiner", "symbolic-hotkeys"],
                              settings=[str(settings_path), str(hotkeys_settings)], host=str(host), hotkeys_host=str(hotkeys),
                              target=str(host), hotkeys_target=str(hotkeys))
    assert quiet(lambda: c.adapt(args))[0] == 0
    assert json.loads(host.read_bytes())["unmanaged"] == "changed sibling"
    assert json.loads(hotkeys.read_bytes())["AppleSymbolicHotKeys"]["7"] == observed_hotkeys["AppleSymbolicHotKeys"]["7"]
    args.command = "check"
    assert quiet(lambda: c.adapt(args))[0] == 0
    args.unit = []
    args.settings = []
    args.host = str(work / "must-not-read")
    args.hotkeys_host = str(work / "must-not-read-either")
    assert c.adapt(args) == 0


if __name__ == "__main__":
    with tempfile.TemporaryDirectory(prefix="configs-darwin-capture-fixture-") as temporary:
        test(Path(temporary).resolve())
    print("✓ finite capture/default/shape/strict-JSON/path/stale/atomic/partial/apply fixtures")
