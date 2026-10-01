"""Local Git/CLI qualification proof; every receipt is explicitly synthetic."""
# INV repository/production-release-qualification
# INV repository/scope-ownership
# INV repository/release-preview-read-only
# INV repository/fixture-git-isolation
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
RULES = (TOOLS / "release-preview.rules").read_bytes()


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content.encode() if isinstance(content, str) else content)


class Qualification(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="production-qualification-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "repo"
        self.root.mkdir()
        self.git("init", "-q", "-b", "dev")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "core.hooksPath", (self.root / "no-hooks").as_posix())
        self.git("config", "core.autocrlf", "false")
        historical = {r.split("\t")[1] for r in RULES.decode().splitlines()
                      if r.startswith("production-historical-only\t")}
        for row in RULES.decode().splitlines():
            fields = row.split("\t")
            if fields[0] == "production-map" and fields[1] == "exact" and fields[2] not in historical:
                write(self.root / fields[2], "Synthetic fixture data; never production evidence.\n")
        write(self.root / "tool/version-control/release-preview.rules", RULES)
        self.commit("feat(repository): synthetic public tree")
        self.base = self.head()
        self.candidate = self.base
        self.rules = self.base
        self.baselines = self.root.parent / "baselines.tsv"
        self.evidence = self.root.parent / "evidence.tsv"
        write(self.baselines, "format\t1\n")
        write(self.evidence, "format\t1\n")
        for domain in ("unixlike", "windows"):
            self.tag(domain, "1.0.0", self.base)
        self.git("tag", "-a", "unixlike-v2026.09.01", self.base, "-m", "Immutable calendar fixture")
        self.semantic()

    def git(self, *args, data=None):
        result = subprocess.run(["git", *args], cwd=self.root, input=data, capture_output=True)
        self.assertEqual(result.returncode, 0, (args, result.stderr.decode(errors="replace")))
        return result.stdout

    def head(self):
        return self.git("rev-parse", "HEAD").decode().strip()

    def commit(self, message):
        self.git("add", ".")
        self.git("commit", "-q", "-m", message)
        return self.head()

    def tag(self, domain, version, source):
        annotation = f"Release-Format: 1\nDomain: {domain}\nVersion: {version}\nSource: {source}\n"
        self.git("tag", "-a", f"{domain}-v{version}", source, "-F", "-", data=annotation.encode())

    def semantic(self):
        rows = ["format\t1"]
        for domain in ("unixlike", "windows"):
            name = f"{domain}-v1.0.0"
            oid = self.git("rev-parse", f"refs/tags/{name}").decode().strip()
            rows.append(f"semantic\t{domain}\t1.0.0\t{name}\t{oid}")
        write(self.baselines, "\n".join(rows) + "\n")

    def declaration(self, domain="unixlike", impact="patch", contracts="prod-unixlike-api",
                    compatibility="compatible", migration="none", reverts=None):
        message = (f"feat({domain}): synthetic public change\n\nRelease-Format: 1\n"
                   f"Release-Domain: {domain}\nRelease-Impact: {impact}\n"
                   f"Release-Contracts: {contracts}\nRelease-Compatibility: {compatibility}\n"
                   f"Release-Rationale: Synthetic fixture intent.\nRelease-Migration: {migration}\n")
        if reverts:
            message += f"Release-Reverts: {reverts}\n"
        self.candidate = self.commit(message)
        return self.candidate

    def bootstrap(self, domains=("unixlike", "windows"), source=None, version="1.0.0"):
        source = source or self.candidate
        for domain in domains:
            path = f"records/bootstrap-{domain}.tsv"
            write(self.root / path, f"format\t1\ndomain\t{domain}\nsource\t{source}\n"
                  f"version\t{version}\ncontracts\tprod-{domain}-contract\n")
        record = self.commit("docs(repository): synthetic separate bootstrap record")
        rows = ["format\t1"] + [
            f"bootstrap\t{domain}\t{self.candidate}\t{record}\trecords/bootstrap-{domain}.tsv"
            for domain in domains]
        write(self.baselines, "\n".join(rows) + "\n")
        return record

    def snapshot(self):
        # Scratch merge objects are caches; refs/index/source/input bytes must stay exact.
        files = {p.relative_to(self.root).as_posix(): (p.stat().st_mode, p.read_bytes())
                 for p in self.root.rglob("*") if p.is_file() and ".git" not in p.relative_to(self.root).parts}
        return (self.git("show-ref"), (self.root / ".git/index").read_bytes(), files,
                self.baselines.read_bytes(), self.evidence.read_bytes())

    def preview(self, *, proposal=False, public=False):
        before = self.snapshot()
        args = ["sh", (self.root / "tool/configs" if public else TOOLS / "release-preview").as_posix()]
        if public:
            args.append("release-preview")
        args += ["--production",
                "--master", self.base, "--candidate", self.candidate, "--rules", self.rules, "--json"]
        if proposal:
            args.append("--bootstrap-proposal")
        else:
            args += ["--baselines", self.baselines.as_posix(), "--evidence", self.evidence.as_posix()]
        result = subprocess.run(args, cwd=self.root, capture_output=True)
        self.assertEqual(before, self.snapshot(), "qualification changed source, refs, index or inputs")
        try:
            value = json.loads(result.stdout)
        except (ValueError, UnicodeError):
            self.fail(f"Non-JSON output: {result.stdout!r} {result.stderr!r}")
        return result.returncode, value

    def receipts(self, *, pair=True):
        code, discovery = self.preview()
        self.assertIn(code, (0, 1), discovery)
        rows = ["format\t1"]
        for check in discovery.get("checks", []):
            rows.append("\t".join(("evidence", check["id"], self.candidate, self.base,
                                  discovery["merge_tree"], self.rules, check["expected_tool"],
                                  "verified", "fixture://synthetic/" + check["id"])))
        if pair:
            rows.append(f"template-pair\tunixlike\tshk95/configs-host-template\t{self.base}\t"
                        f"{self.candidate}\tdelivered\tverified")
        write(self.evidence, "\n".join(rows) + "\n")

    def accepted(self):
        code, value = self.preview()
        self.assertEqual(code, 0, value.get("reasons", value))
        self.assertFalse(value["production_certification"])
        self.assertEqual(value["evidence_authority"], "asserted-offline")
        return value

    def refused(self, reason, *, proposal=False):
        code, value = self.preview(proposal=proposal)
        self.assertNotEqual(code, 0, value.get("reasons", value))
        self.assertIn(reason, value["reasons"])
        return value

    def rules_change(self, change):
        path = self.root / "tool/version-control/release-preview.rules"
        write(path, change(path.read_text(encoding='utf-8')))
        self.rules = self.commit("docs(repository): synthetic rules revision")
        self.candidate = self.rules

    def test_proposal_identities_and_no_selection(self):
        code, value = self.preview(proposal=True)
        self.assertEqual(code, 0, value.get("reasons", value))
        for key in ("selected", "calendar_conversion", "production_certification"):
            self.assertFalse(value[key])
        self.assertEqual(value["source"], self.candidate)
        self.assertEqual(len(value["surfaces"]), 17)
        self.assertTrue(all(r["id"].startswith("prod-") for r in value["requirements"]))
        self.assertTrue(any("unixlike-lock-" in r["tool"] for r in value["requirements"]))

    def test_public_operator_proposal(self):
        # Independently trusted entry tools, not executable candidate fixture blobs.
        for source in (TOOLS.parent / "configs", TOOLS / "classify",
                       TOOLS / "release-preview", TOOLS / "release-preview.awk"):
            destination = self.root / "tool" / source.relative_to(TOOLS.parent)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        code, value = self.preview(proposal=True, public=True)
        self.assertEqual(code, 0, value.get("reasons", value))
        self.assertFalse(value["selected"])
        self.assertFalse(value["production_certification"])

    def test_batch_ownership_preserves_aggregate(self):
        paths = b"windows/desired/manifest.json\nunixlike/flake.nix\nunknown.file\n"
        command = ["sh", (TOOLS / "classify").as_posix()]
        records = subprocess.check_output(command + ["--records", "--stdin"], cwd=self.root, input=paths).decode()
        self.assertEqual(records, "unixlike/flake.nix\tunixlike\nunknown.file\tunclassified\n"
                         "windows/desired/manifest.json\twindows\n")
        aggregate = subprocess.check_output(command + ["--stdin"], cwd=self.root, input=paths).decode()
        self.assertEqual(aggregate, "unixlike\nwindows\nunclassified\n")

    def test_unknown_and_unmapped_paths(self):
        write(self.root / "unknown.file", "unknown\n")
        self.candidate = self.commit("docs(repository): synthetic unknown")
        self.refused("unclassified-path", proposal=True)
        self.git("reset", "--hard", "-q", self.base)
        write(self.root / "unixlike/new-contract.nix", "unmapped\n")
        self.candidate = self.commit("feat(unixlike): synthetic unmapped")
        self.refused("mapping-review-needed", proposal=True)

    def test_historical_root_is_not_live_candidate(self):
        write(self.root / "flake.nix", "historical, not a second live authority\n")
        self.candidate = self.commit("feat(unixlike): synthetic historical root")
        self.refused("historical-path-in-candidate", proposal=True)

    def test_missing_and_symlink_public_surface(self):
        path = "unixlike/api/contract.json"
        (self.root / path).unlink()
        self.candidate = self.commit("feat(unixlike): synthetic missing surface")
        self.refused("missing-production-surface", proposal=True)
        self.git("reset", "--hard", "-q", self.base)
        blob = self.git("hash-object", "-w", "--stdin", data=b"synthetic-target").decode().strip()
        self.git("update-index", "--cacheinfo", "120000", blob, path)
        self.git("commit", "-qm", "feat(unixlike): synthetic symlink surface")
        self.candidate = self.head()
        self.refused("missing-production-surface", proposal=True)

    def test_foreign_map_cannot_hide_among_matching_checks(self):
        self.rules_change(lambda s: s.replace("production-map\texact\tunixlike/api/contract.json\tprod-unixlike-api",
                                             "production-map\texact\tunixlike/api/contract.json\tprod-unixlike-api,prod-windows-native"))
        self.refused("production-mapping-domain-mismatch", proposal=True)

    def test_unknown_template_and_wrong_tool_source(self):
        self.rules_change(lambda s: s.replace("unixlike-api,prod-unixlike-api,prod-unixlike-darwin-capture,prod-unixlike-inspection",
                                             "unknown-check,prod-unixlike-api"))
        self.refused("invalid-production-template-trigger", proposal=True)
        self.rules_change(lambda s: RULES.decode().replace("prod-windows-native\twindows-runtime",
                                                         "prod-windows-native\tunixlike-lock"))
        self.refused("production-tool-source-mismatch", proposal=True)

    def test_separate_source_bound_bootstrap_and_pair(self):
        record = self.bootstrap()
        self.assertNotEqual(record, self.candidate)
        self.receipts()
        value = self.accepted()
        self.assertEqual({d["next_version"] for d in value["domains"]}, {"1.0.0"})
        selected = {c["id"] for c in value["checks"]}
        self.assertTrue({"prod-windows-ltsc-runtime", "prod-windows-bootstrap",
                         "prod-unixlike-build-aarch64-linux"} <= selected)
        write(self.evidence, self.evidence.read_bytes().replace(self.candidate.encode(), b"1" * 40, 1))
        self.refused("evidence-identity-mismatch")

    def test_unavailable_native_tool_mismatch_and_defect(self):
        self.bootstrap()
        self.receipts()
        original = self.evidence.read_bytes()
        cases = [
            (b"\tverified\tfixture://synthetic/prod-windows-ltsc-runtime",
             b"\tunverified\tfixture://synthetic/prod-windows-ltsc-runtime", "required-evidence-not-verified"),
            (b"pwsh-7.6.6-x64", b"pwsh-7.5.0-x64", "evidence-tool-mismatch")]
        for before, after, reason in cases:
            with self.subTest(reason=reason):
                write(self.evidence, original.replace(before, after))
                self.refused(reason)
        write(self.evidence, original + b"defect\tprod-unixlike-api\tfixture://declared-defect\n")
        self.refused("contract-defect")

    def test_bootstrap_requires_review_and_exact_pair(self):
        self.bootstrap()
        self.receipts(pair=False)
        self.refused("missing-template-pair")
        self.receipts()
        rows = self.evidence.read_text(encoding='utf-8').splitlines()
        write(self.evidence, "\n".join(r for r in rows if not r.startswith("evidence\tprod-unixlike-bootstrap-review\t")) + "\n")
        self.refused("missing-required-evidence")

    def test_bootstrap_mismatch_and_calendar_refusal(self):
        self.bootstrap(version="2026.09.01")
        self.refused("bootstrap-record-mismatch")
        calendar = self.git("rev-parse", "refs/tags/unixlike-v2026.09.01").decode().strip()
        write(self.baselines, f"format\t1\nsemantic\tunixlike\t2026.09.01\tunixlike-v2026.09.01\t{calendar}\n")
        self.refused("baseline-annotation-mismatch")

    def test_windows_release_selects_no_unixlike_evidence(self):
        write(self.root / "windows/desired/manifest.json", "synthetic patch\n")
        self.declaration("windows", contracts="prod-windows-catalogue")
        self.receipts()
        value = self.accepted()
        self.assertFalse(any(c["id"].startswith("prod-unixlike") for c in value["checks"]))
        self.assertEqual(next(d["next_version"] for d in value["domains"] if d["domain"] == "windows"), "1.0.1")

    def test_already_on_master_still_qualifies_public_promise(self):
        write(self.root / "unixlike/api/contract.json", "synthetic patch\n")
        self.declaration()
        self.base = self.candidate
        self.receipts()
        value = self.accepted()
        self.assertEqual(value["promotion_delta"], [])
        selected = {c["id"] for c in value["checks"]}
        self.assertTrue({"prod-unixlike-build-aarch64-darwin", "prod-unixlike-template-pair"} <= selected)

    def test_major_requires_breaking_migration(self):
        write(self.root / "unixlike/api/contract.json", "synthetic breaking API\n")
        self.declaration(impact="major", compatibility="breaking",
                         migration="docs/policy/decisions/unixlike/public-environment-host-boundary.md")
        self.receipts()
        value = self.accepted()
        self.assertTrue({"major", "migration"} <= set(value["approval_reasons"]))
        self.assertEqual(next(d["next_version"] for d in value["domains"] if d["domain"] == "unixlike"), "2.0.0")

    def test_exact_inverse_revert(self):
        path = self.root / "unixlike/api/contract.json"
        original = path.read_bytes()
        write(path, "synthetic patch\n")
        target = self.declaration()
        write(path, original)
        self.declaration(reverts=target)
        self.receipts(pair=False)
        value = self.accepted()
        self.assertEqual(value["checks"], [])
        self.assertFalse(any(d["next_version"] for d in value["domains"]))
        write(path, "noninverse\n")
        self.declaration(reverts=target)
        self.refused("ambiguous-revert")
        self.git("reset", "--hard", "-q", target)
        write(path, "noninverse\n")
        self.declaration(reverts=target)
        self.refused("noninverse-revert")

    def test_source_blob_change_cannot_reuse_old_tool_receipt(self):
        write(self.root / "unixlike/api/contract.json", "synthetic API patch\n")
        self.declaration()
        self.receipts()
        old = next(row.split("\t")[6] for row in self.evidence.read_text(encoding="utf-8").splitlines()
                   if row.startswith("evidence\tprod-unixlike-evaluation\t"))
        write(self.root / "unixlike/flake.lock", "synthetic changed lock\n")
        self.declaration()
        self.receipts()
        rows = self.evidence.read_text(encoding="utf-8").splitlines()
        for i, row in enumerate(rows):
            if row.startswith("evidence\tprod-unixlike-evaluation\t"):
                fields = row.split("\t")
                self.assertNotEqual(fields[6], old)
                fields[6] = old
                rows[i] = "\t".join(fields)
        write(self.evidence, "\n".join(rows) + "\n")
        self.refused("evidence-tool-mismatch")

    def test_stale_template_pair_and_undelivered_revision(self):
        write(self.root / "unixlike/api/contract.json", "synthetic API patch\n")
        self.declaration()
        self.receipts()
        original = self.evidence.read_text(encoding="utf-8")
        pair = next(row for row in original.splitlines() if row.startswith("template-pair\t"))
        for wrong in (pair.replace(self.candidate, self.base), pair.replace("\tdelivered\t", "\tproposed\t")):
            with self.subTest(pair=wrong):
                write(self.evidence, original.replace(pair, wrong))
                self.refused("invalid-template-pair")

    def test_legacy_master_root_deletion_is_qualified_without_conversion(self):
        write(self.root / "flake.nix", "legacy master fixture\n")
        self.base = self.commit("feat(unixlike): synthetic historical master")
        (self.root / "flake.nix").unlink()
        self.candidate = self.commit("refactor(unixlike): synthetic source cutover")
        self.bootstrap()
        self.receipts()
        value = self.accepted()
        self.assertIn("flake.nix", {p["path"] for p in value["promotion_delta"]})

    def test_breaking_patch_refuses_and_missing_production_rules_refuse(self):
        write(self.root / "unixlike/api/contract.json", "synthetic breaking patch\n")
        self.declaration(compatibility="breaking")
        self.refused("incompatible-impact")
        self.rules_change(lambda s: s.replace("production\t1\n", ""))
        self.refused("production-rules-required", proposal=True)

    def test_raw_invalid_utf8_path(self):
        blob = self.git("hash-object", "-w", "--stdin", data=b"synthetic invalid path\n").decode().strip()
        entries = self.git("ls-tree", "-z", self.candidate)
        tree = self.git("mktree", "-z", data=entries + f"100644 blob {blob}\t".encode() + b"bad-\xff.txt\0").decode().strip()
        self.candidate = self.git("commit-tree", tree, "-p", self.candidate,
                                  data=b"docs(repository): synthetic invalid UTF8 tree\n").decode().strip()
        self.refused("unsupported-path", proposal=True)

    def test_candidate_executable_is_never_run(self):
        sentinel = self.root.parent / "candidate-executed"
        write(self.root / "unixlike/tool/contract-inspect", f"#!/bin/sh\ntouch '{sentinel.as_posix()}'\n")
        self.candidate = self.commit("feat(unixlike): synthetic executable surface")
        code, value = self.preview(proposal=True)
        self.assertEqual(code, 0, value.get("reasons", value))
        self.assertFalse(sentinel.exists())


if __name__ == "__main__":
    unittest.main()
