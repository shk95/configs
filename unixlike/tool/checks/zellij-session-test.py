#!/usr/bin/env python3
# INV unixlike/editable-file-generation-backup
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True


class LiveSession(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.native_zellij = shutil.which("zellij")
        if cls.native_zellij is None:
            raise RuntimeError("pinned native Zellij is required; run editable-files-test")
        source = subprocess.check_output(["nix", "eval", "--raw", "--impure", "--expr", '''
          let
            p = builtins.getFlake (toString ./unixlike);
            args = { system = builtins.currentSystem; user = "example"; git = {name="Example"; email="example@example.invalid";}; };
            home = if p.inputs.nixpkgs.lib.hasSuffix "-darwin" builtins.currentSystem then
              (p.lib.mkDarwin (args // {systemModules = [{system.primaryUser="example"; users.users.example.home="/Users/" + "example";}];})).config.home-manager.users.example
            else (p.lib.mkHome (args // {homeDirectory="/home/" + "example"; environment.graphical=false;})).config;
          in home.programs.zsh.initContent
        '''], text=True)
        cls.function = re.search(r"(?ms)^zellij\(\) \{\n.*?^\}", source).group()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name).resolve()
        self.config = self.home / "xdg" / "zellij" / "config.kdl"
        self.config.parent.mkdir(parents=True)
        self.log = self.home / "argv.json"
        stub = self.home / "zellij"
        stub.write_text(f"#!{sys.executable}\nimport json, os, sys\nopen(os.environ['ZELLIJ_WRAPPER_LOG'], 'w').write(json.dumps(sys.argv[1:]))\n")
        stub.chmod(0o700)
        self.env = {key: value for key, value in os.environ.items()
                    if key not in ("ZELLIJ_CONFIG_FILE", "ZELLIJ_CONFIG_DIR", "XDG_CONFIG_HOME")}
        self.env.update(PATH=str(self.home) + os.pathsep + self.env["PATH"],
                        XDG_CONFIG_HOME=str(self.config.parent.parent), ZELLIJ_WRAPPER_LOG=str(self.log))

    def invoke(self, *args, success=True):
        self.log.unlink(missing_ok=True)
        result = subprocess.run(["zsh", "-f", "-c", self.function + '\nzellij "$@"', "fixture", *args],
                                env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if success:
            self.assertEqual(result.returncode, 0, result.stderr.decode())
            return json.loads(self.log.read_text())
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.log.exists())

    def test_live_edits_raw_strings_comments_and_quoting(self):
        for contents, expected in [
            ('session_name "first"\n', "first"),
            ('session_name "edited-at-runtime"\n', "edited-at-runtime"),
            ('/- session_name "ignored"\n// comment\nnode { session_name "nested"; }\nsession_name r#"raw space name"#\n', "raw space name"),
            ('session_name "quote\\\" and newline\\n"\n', 'quote" and newline\n'),
            ('session_name (custom)"typed string"\n', 'typed string'),
        ]:
            self.config.write_text(contents)
            self.assertEqual(self.invoke(), ["--config", str(self.config), "attach", "--create", expected])

    def test_native_cli_keeps_session_name_out_of_initial_command(self):
        # An invalid index makes the actual CLI parser exit before session
        # lookup. Invalid KDL also prevents startup if a misplaced -- causes
        # the index to be swallowed as an initial command (the 0.46 regression).
        broken = self.home / "invalid.kdl"
        broken.write_text("unclosed {")
        for name in ("unixlike", "space name", 'quote" name', "newline\nname"):
            self.config.write_text('session_name ' + json.dumps(name) + '\n')
            arguments = self.invoke()
            arguments[arguments.index("--config") + 1] = str(broken)
            result = subprocess.run(
                [self.native_zellij, *arguments, "--index=invalid"],
                env=dict(self.env, HOME=str(self.home), XDG_STATE_HOME=str(self.home / "state"),
                         XDG_CACHE_HOME=str(self.home / "cache")),
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
            self.assertEqual(result.returncode, 2, result.stderr.decode())
            self.assertIn(b"invalid value 'invalid' for '--index <INDEX>'", result.stderr)

    def test_option_and_subcommand_names_are_refused_before_exec(self):
        for name in ("--help", "--index=1", "-dash", "options", "help"):
            self.config.write_text('session_name ' + json.dumps(name) + '\n')
            self.invoke(success=False)

    def test_missing_name_and_explicit_args_use_native_cli(self):
        self.assertEqual(self.invoke(), [])
        self.config.write_text('default_mode "normal"\n')
        self.assertEqual(self.invoke(), ["--config", str(self.config)])
        self.config.write_text("malformed {")
        self.assertEqual(self.invoke("attach", "--create", "manual"), ["attach", "--create", "manual"])
        self.invoke(success=False)
        self.config.write_text("session_name 42\n")
        self.invoke(success=False)

    def test_config_file_and_directory_environment_precedence(self):
        self.config.write_text('session_name "xdg"\n')
        alternate = self.home / "alternate"
        alternate.mkdir()
        (alternate / "config.kdl").write_text('session_name "directory"\n')
        self.env["ZELLIJ_CONFIG_DIR"] = str(alternate)
        self.assertEqual(self.invoke()[-1], "directory")
        explicit = self.home / "explicit.kdl"
        explicit.write_text('session_name "file"\n')
        self.env["ZELLIJ_CONFIG_FILE"] = str(explicit)
        self.assertEqual(self.invoke()[-1], "file")

    def test_explicit_config_matches_the_file_used_for_the_name(self):
        native = self.home / ".config" / "zellij"
        native.mkdir(parents=True)
        (native / "config.kdl").write_text('session_name "native-home"\n')
        self.env["HOME"] = str(self.home)
        self.config.write_text('session_name "live-xdg"\n')
        self.assertEqual(self.invoke(), ["--config", str(self.config), "attach", "--create", "live-xdg"])


if __name__ == "__main__":
    unittest.main()
