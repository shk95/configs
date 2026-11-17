#!/usr/bin/env python3
# INV unixlike/editable-file-generation-backup
import importlib.machinery
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
tool = Path(__file__).resolve().parents[1] / "editable-files"
loader = importlib.machinery.SourceFileLoader("editable_files", str(tool))
spec = importlib.util.spec_from_loader(loader.name, loader)
engine = importlib.util.module_from_spec(spec)
loader.exec_module(engine)


class EditableFiles(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.home = self.root / "home"
        self.store = self.root / "store"
        self.home.mkdir()
        self.store.mkdir()
        self.source = self.store / "generation" / "config"
        self.source.parent.mkdir()
        self.source.write_bytes(b"shared\nnew-only\n")
        self.target = self.home / "config"
        self.manifest = dict(schemaVersion=1, home=str(self.home), storeDir=str(self.store),
                             lock=str(self.home / "state" / "lock"),
                             files=[dict(source=str(self.source), target=str(self.target))])
        self.real_run = subprocess.run
        self.addCleanup(patch.stopall)
        patch.object(engine.subprocess, "run", side_effect=self.run_command).start()
        patch("sys.stdout", new=io.StringIO()).start()

    def run_command(self, argv, **kwargs):
        if argv[0] == "fixture-nix-store":
            link = Path(argv[2])
            if not link.is_symlink():
                link.symlink_to(argv[-1])
            return subprocess.CompletedProcess(argv, 0)
        return self.real_run(argv, **kwargs)

    def install(self):
        engine.install(self.manifest, "diff", "fixture-nix-store", "fixture-generation")

    def backups(self):
        return sorted(self.target.parent.glob(self.target.name + ".backup-*"))

    def restore(self, backup):
        metadata = json.loads((backup / "metadata.json").read_text())
        self.assertEqual(metadata["direction"], "new-generation-to-before-switch")
        self.assertEqual(metadata["sourceSha256"], engine.digest(self.source.read_bytes()))
        restored = self.root / "restored"
        restored.unlink(missing_ok=True)
        delta = (backup / "changes.patch").read_bytes()
        if delta:
            subprocess.run(["patch", "-s", "-o", str(restored), str(self.source),
                            str(backup / "changes.patch")], check=True)
            return restored.read_bytes()
        return self.source.read_bytes()

    def test_diff_direction_and_incoming_generation_changes(self):
        self.target.write_bytes(b"shared\nold-only\n")
        self.target.chmod(0o640)
        self.install()
        backup = self.backups()[0]
        metadata = json.loads((backup / "metadata.json").read_text())
        self.assertEqual(metadata["previousMode"], 0o640)
        self.assertIsNone(metadata["previousLink"])
        delta = (backup / "changes.patch").read_text()
        self.assertIn("-new-only\n", delta)
        self.assertIn("+old-only\n", delta)
        self.assertEqual(self.restore(backup), b"shared\nold-only\n")
        self.assertFalse(self.target.is_symlink())
        self.assertEqual(self.target.read_bytes(), self.source.read_bytes())
        self.assertEqual(self.target.stat().st_mode & 0o777, 0o600)
        self.assertEqual(backup.stat().st_mode & 0o777, 0o700)
        self.source.write_bytes(b"a different incoming generation\n")
        self.install()
        self.assertEqual(self.restore(self.backups()[1]), b"shared\nnew-only\n")

    def test_leaf_symlink_metadata_is_preserved(self):
        self.target.symlink_to(self.source)
        previous_mode = self.target.lstat().st_mode & 0o777
        self.install()
        metadata = json.loads((self.backups()[0] / "metadata.json").read_text())
        self.assertEqual(metadata["previousMode"], previous_mode)
        self.assertEqual(metadata["previousLink"], str(self.source))
        self.assertFalse(self.target.is_symlink())
        self.assertEqual(self.target.read_bytes(), self.source.read_bytes())

    def test_missing_identical_empty_and_no_final_newline(self):
        self.install()
        self.assertEqual(self.backups(), [])
        self.install()
        self.assertEqual((self.backups()[0] / "changes.patch").read_bytes(), b"")
        for previous in (b"", b"no final newline", "한글\r\n".encode()):
            self.target.write_bytes(previous)
            self.install()
            self.assertEqual(self.restore(self.backups()[-1]), previous)

    def test_numbering_preserves_existing_and_incomplete_backups(self):
        self.target.write_text("local\n")
        prior = self.target.with_name("config.backup-000009")
        prior.mkdir()
        (prior / "keep").write_text("preserved")
        self.target.with_name("config.backup-000011").write_text("foreign occupied name")
        self.install()
        self.assertEqual(self.backups()[-1].name, "config.backup-000012")
        self.assertEqual((prior / "keep").read_text(), "preserved")

    def test_symlink_and_old_directory_migration_preserve_unselected_files(self):
        directory = self.store / "old-directory"
        directory.mkdir()
        (directory / "config").write_text("old linked contents\n")
        (directory / "unselected.lua").write_text("keep store ownership\n")
        (self.home / "linked").symlink_to(directory)
        self.target = self.home / "linked" / "config"
        self.manifest["files"][0]["target"] = str(self.target)
        self.install()
        self.assertFalse(self.target.parent.is_symlink())
        self.assertFalse(self.target.is_symlink())
        self.assertTrue((self.target.parent / "unselected.lua").is_symlink())
        retained = Path(self.manifest["lock"]).parent / "directory-baselines" / directory.name
        self.assertTrue(retained.is_symlink())
        self.assertEqual(retained.resolve(), directory)
        self.assertEqual((directory / "config").read_text(), "old linked contents\n")
        self.assertEqual(self.restore(self.backups()[0]), b"old linked contents\n")
        # A second generation reuses the root, preserving unselected leaf links.
        self.install()
        self.assertEqual((self.target.parent / "unselected.lua").read_text(), "keep store ownership\n")

    def test_directory_root_failure_keeps_original_directory_link(self):
        directory = self.store / "old-directory"
        directory.mkdir()
        (directory / "config").write_text("original\n")
        (self.home / "linked").symlink_to(directory)
        self.manifest["files"][0]["target"] = str(self.home / "linked" / "config")
        with patch.object(engine, "retain_root", side_effect=OSError("root failed")):
            with self.assertRaises(OSError):
                self.install()
        self.assertTrue((self.home / "linked").is_symlink())
        self.assertEqual((directory / "config").read_text(), "original\n")

    def test_check_and_invalid_second_file_do_not_write(self):
        self.target.write_text("keep\n")
        engine.prepare(self.manifest, "diff")
        self.assertEqual(sorted(p.name for p in self.home.iterdir()), ["config"])
        bad = self.home / "directory"
        bad.mkdir()
        self.manifest["files"].append(dict(source=str(self.source), target=str(bad)))
        with self.assertRaises(engine.Refused):
            self.install()
        self.assertEqual(self.target.read_text(), "keep\n")
        self.assertEqual(self.backups(), [])

    def test_refuses_binary_dangling_and_directory_sources(self):
        for contents in (b"binary\0contents",):
            self.target.write_bytes(contents)
            with self.assertRaises(engine.Refused):
                self.install()
            self.assertEqual(self.target.read_bytes(), contents)
        self.target.unlink()
        self.target.symlink_to(self.home / "absent")
        with self.assertRaises(engine.Refused):
            self.install()
        self.assertTrue(self.target.is_symlink())
        self.target.unlink()
        self.manifest["files"][0]["source"] = str(self.source.parent)
        with self.assertRaises(engine.Refused):
            self.install()

    def test_backup_and_replacement_failures_preserve_previous_contents(self):
        self.target.write_text("keep\n")
        with patch.object(engine, "write_file", side_effect=OSError("backup write failed")):
            with self.assertRaises(OSError):
                self.install()
        self.assertEqual(self.target.read_text(), "keep\n")
        with patch.object(engine.os, "replace", side_effect=OSError("replacement failed")):
            with self.assertRaises(OSError):
                self.install()
        self.assertEqual(self.target.read_text(), "keep\n")
        self.assertEqual(self.restore(self.backups()[-1]), b"keep\n")

    def test_root_failure_and_edit_during_backup_stop_replacement(self):
        self.target.write_text("keep\n")
        with patch.object(engine.subprocess, "run", side_effect=lambda argv, **kw:
                          (_ for _ in ()).throw(OSError("root failed"))
                          if argv[0] == "fixture-nix-store" else self.real_run(argv, **kw)):
            with self.assertRaises(OSError):
                self.install()
        self.assertEqual(self.target.read_text(), "keep\n")
        original = engine.backup_file

        def edit_after_backup(*args):
            original(*args)
            self.target.write_text("edited during switch\n")

        with patch.object(engine, "backup_file", side_effect=edit_after_backup):
            with self.assertRaises(engine.Refused):
                self.install()
        self.assertEqual(self.target.read_text(), "edited during switch\n")

    def test_duplicate_and_escaping_targets_refused(self):
        self.manifest["files"] *= 2
        with self.assertRaises(engine.Refused):
            engine.prepare(self.manifest, "diff")
        self.manifest["files"] = [dict(source=str(self.source), target=str(self.home / ".." / "escape"))]
        with self.assertRaises(engine.Refused):
            engine.prepare(self.manifest, "diff")

    def test_foreign_parent_link_and_concurrent_writer_refused(self):
        foreign = self.root / "foreign"
        foreign.mkdir()
        (foreign / "config").write_text("preserve foreign source\n")
        (self.home / "linked").symlink_to(foreign)
        self.manifest["files"][0]["target"] = str(self.home / "linked" / "config")
        with self.assertRaises(engine.Refused):
            self.install()
        self.assertEqual((foreign / "config").read_text(), "preserve foreign source\n")
        self.manifest["files"][0]["target"] = str(self.target)
        with engine.locked(Path(self.manifest["lock"])):
            with self.assertRaises(engine.Refused):
                self.install()
        self.assertFalse(self.target.exists())


if __name__ == "__main__":
    unittest.main()
