#!/usr/bin/env python3
"""Selection, complete inventory, supplier and lifecycle regression probes."""
# INV unixlike/tool-supply-ownership
# INV unixlike/editable-file-generation-backup
import json
from pathlib import Path
import subprocess
import tempfile
import os
import shutil

root = Path(__file__).resolve().parents[2]
prefix = '''let
  p = builtins.getFlake "path:ROOT";
  lib = p.inputs.nixpkgs.lib;
  spec = {system = "x86_64-linux"; user = "example"; homeDirectory = "/home/" + "example";
    git = {name = "Example"; email = "example@example.invalid";}; environment.graphical = false;};
  home = modules: (p.lib.mkHome (spec // {homeModules = modules;}));
  cfg = modules: (home modules).config;
  row = id: c: builtins.head (builtins.filter (r: r.id == id) c.providerTools.inventory);
  mac = modules: p.lib.mkDarwin {system = "aarch64-darwin"; user = "example"; inherit (spec) git;
    homeModules = modules; systemModules = [({pkgs,...}: {system.primaryUser = "example"; users.users.example.home = "/Users/" + "example";
      homebrew.enable = true; homebrew.brews = ["mas"]; homebrew.masApps.Example = 123; environment.systemPackages = [pkgs.hello];})];};
in '''.replace('ROOT', str(root))

def evaluate(expr):
    return subprocess.run(['nix', 'eval', '--impure', '--json', '--expr', prefix + expr], text=True, capture_output=True)

positive = '''let
  c = cfg [];
  off = cfg [{providerTools.programs = {codex.enable = false; ripgrep.enable = false; bat.enable = false;};}];
  native = cfg [{programs.bat.enable = false;}];
  nativeBat = cfg [{providerTools.groups.text = false; programs.bat.enable = true;}];
  versioned = cfg [{providerTools.programs.codex.version = "0.100";}];
  excluded = cfg [{providerTools.excludedPackages = ["ripgrep"];}];
  allOff = cfg [{providerTools.agents.enable = false;}];
  extra = cfg [({pkgs,...}: {home.packages = [pkgs.hello];})];
  m = (mac []).config;
  macWith = module: ((mac []).extendModules {modules = [module];}).config;
  forcedCasks = macWith {homebrew.casks = lib.mkForce ["obsidian"];};
  disabledBrew = macWith {homebrew.enable = lib.mkForce false;};
  skipBrewSettings = c: let h = c.home-manager.users.example;
  in !h.programs.ghostty.enable && !(h.home.activation ? karabinerDesiredState)
    && !(row "ghostty" c).selected && !(row "karabiner-elements" c).selected
    && !(row "ghostty" h).selected && !(row "karabiner-elements" h).selected;
  directBrew = ((mac [{providerTools.groups.text = false;}]).extendModules {
    modules = [{homebrew.brews = ["fd"];}];
  }).config;
  settingsOff = (mac [{providerDarwin.appSettings.enable = false;}]).config;
  appOff = (mac [{providerTools.programs.ghostty.enable = false;}]).config;
  graphical = modules: (p.lib.mkHome (spec // {environment.graphical = true; homeModules = modules;})).config;
  desktopOff = {providerTools.programs = {zellij.enable = false; ghostty.enable = false; wezterm.enable = false;};};
  linuxDesktop = graphical [];
  ghosttyConfigOnly = graphical [{programs.ghostty = {package = null; systemd.enable = false;};}];
  terminalOff = {providerTools.groups.terminal = false;};
  noTerminal = graphical [terminalOff];
  restoredZellij = graphical [terminalOff {providerTools.programs.zellij.enable = true;}];
  forcedGroups = {
    providerTools.groups = {text = false; terminal = true; productivity = true;};
  };
  forcedHome = home [forcedGroups];
  developmentOff = {providerTools.groups.development = false;};
  noDevelopment = cfg [developmentOff];
  noNativeGit = cfg [{programs.git.enable = false;}];
  restoredGit = cfg [developmentOff {providerTools.programs.git.enable = true;}];
  gitConfigured = c: c.xdg.configFile ? "git/config";
  gitBackup = c: c.home.activation ? backupExistingGitconfig;
  noCodingAgents = cfg [{providerTools.groups."coding-agents" = false;}];
  forcedAgents = cfg [{providerTools.agents.enable = false; providerTools.groups."coding-agents" = true;}];
  noNetworkOrProductivity = graphical [{providerTools.groups = {network = false; productivity = false;};}];
  noMedia = graphical [{providerTools.groups.media = false;}];
  restoredImv = graphical [{providerTools.groups.media = false; providerTools.programs.imv.enable = true;}];
  imageTypes = ["image/gif" "image/jpeg" "image/png" "image/webp"];
  fontChoice = {providerTools.programs.d2coding-nerd-font.enable = true;};
  desktopFont = graphical [fontChoice];
  wslFont = (p.lib.mkHome (spec // {environment = {wsl = true; graphical = false;}; homeModules = [fontChoice];})).config;
  individualOverrides = cfg [{providerTools.groups = {text = false; development = false; coding-agents = false;};
    providerTools.programs = {bat.enable = true; codex.enable = true;};}];
  noSettings = cfg [{providerTools.programs = {glow.enable = false; powershell.enable = false;};}];
  noPaneru = (mac [{providerTools.programs.paneru.enable = false;}]).config.home-manager.users.example;
  noSystem = (p.lib.mkNixos {inherit (spec) system git; user = spec.user; environment.graphical = false;
    homeModules = [{providerTools.groups.system = false;}];
    systemModules = [{ users.users.example.isNormalUser = true; }];
  }).config;
  sys = p.nixosConfigurations.fixture-cli.config;
  linuxOff = graphical [desktopOff];
  macHome = m.home-manager.users.example;
  macNoAgents = (mac [{providerTools.agents.enable = false;}]).config;
  macOff = (mac [desktopOff]).config.home-manager.users.example;
  editable = c: lib.attrNames (lib.filterAttrs (_: enabled: enabled) c.configs.editableFiles);
  linkedZellij = cfg [{configs.editableFiles.${"/home/" + "example/.config/zellij/config.kdl"} = false;}];
  names = c: map lib.getName c.home.packages;
  casks = c: map (cask: cask.name) c.homebrew.casks;
  codingAgents = ["claude-code" "codex"];
  inventoryNames = c: map (r: r.packageName or r.identifier) (builtins.filter (r: r.selected && r.provider == "nix") c.providerTools.inventory);
in {
  shared = (row "ripgrep" c).selected && (row "bat" c).selected;
  cli = !(row "ghostty" c).selected && !(row "remmina" c).selected;
  agents = lib.all (id: (row id c).selected && (row id c).provider == "mise"
    && !(builtins.elem id (names c))) codingAgents
    && c.providerTools.mise.tools."aqua:openai/codex" == "latest"
    && c.providerTools.mise.tools."aqua:anthropics/claude-code" == "latest";
  version = versioned.providerTools.mise.tools."aqua:openai/codex" == "0.100";
  optOut = !(row "codex" off).selected && !(builtins.elem "ripgrep" (names off)) && !off.programs.bat.enable;
  nativeOverride = !(row "bat" native).selected;
  gitFollowsSelection = !gitConfigured noDevelopment && !gitBackup noDevelopment
    && !gitConfigured noNativeGit && !gitBackup noNativeGit
    && gitConfigured restoredGit && gitBackup restoredGit;
  settingsOnlyGhostty = ghosttyConfigOnly.programs.ghostty.enable
    && ghosttyConfigOnly.xdg.configFile."ghostty/config".source != null
    && !(builtins.elem "ghostty" (names ghosttyConfigOnly))
    && !(row "ghostty" ghosttyConfigOnly).selected;
  effectiveCasks = skipBrewSettings forcedCasks && (row "obsidian" forcedCasks).selected
    && (row "bettercap" forcedCasks).selected
    && !(builtins.elem "ghostty" forcedCasks.home-manager.users.example.providerDarwin.selectedApps)
    && forcedCasks.system.build.toplevel.drvPath != "";
  inactiveBrew = skipBrewSettings disabledBrew
    && !(lib.any (r: r.selected && builtins.elem r.provider ["homebrew" "mas"]) disabledBrew.providerTools.inventory)
    && lib.all (id: !(row id disabledBrew).selected && (row id disabledBrew).provider == "homebrew") codingAgents
    && disabledBrew.system.build.toplevel.drvPath != "";
  nativeInventory = let rows = builtins.filter (r: r.id == "bat") nativeBat.providerTools.inventory;
  in builtins.length rows == 1 && (row "bat" nativeBat).selected
    && (row "bat" nativeBat).source == "native-home" && (row "bat" nativeBat).deployment == "home";
  nativeBrewInventory = let rows = builtins.filter (r: r.id == "fd") directBrew.providerTools.inventory;
  in builtins.length rows == 1 && (row "fd" directBrew).selected
    && (row "fd" directBrew).source == "native-system" && (row "fd" directBrew).provider == "homebrew"
    && directBrew.system.build.toplevel.drvPath != "";
  inventoryDeployment = (row "chatgpt" m).deployment == "system"
    && (row "bettercap" m).deployment == "system"
    && (row "hello" m).deployment == "system"
    && (row "Example" m).deployment == "system"
    && (row "codex" c).deployment == "home";
  legacyExclusion = !(row "ripgrep" (cfg [{providerTools.excludedPackages = ["ripgrep"]; providerTools.programs.ripgrep.enable = true;}])).selected;
  managerOptOut = !(builtins.elem "mise" (names (cfg [{providerTools.agents.enable = false; providerTools.programs.mise.enable = false;}])));
  excluded = !(row "ripgrep" excluded).selected;
  groupOverride = allOff.providerTools.mise.tools == {} && !(allOff.home.activation ? providerMiseInstall);
  extra = (row "hello" extra).source == "native-home";
  complete = lib.all (n: builtins.elem n (inventoryNames c)) (names c);
  darwin = builtins.length m.homebrew.casks == 34 && builtins.length m.homebrew.brews == 6;
  darwinTrashAlias = macHome.home.shellAliases.rm == "trash"
    && (mac [{home.shellAliases.rm = "rm -i";}]).config.home-manager.users.example.home.shellAliases.rm == "rm -i";
  linuxIdleLock = linuxDesktop.services.hypridle.settings.listener == [{timeout = 900; on-timeout = "noctalia msg session lock";}]
    && (graphical [{services.hypridle.settings.listener = [];}]).services.hypridle.settings.listener == [];
  darwinAgents = lib.all (id: builtins.elem id (casks m) && (row id m).selected
    && (row id m).provider == "homebrew" && (row id m).deployment == "system"
    && !(builtins.elem id (names macHome)) && !(builtins.elem id (map lib.getName m.environment.systemPackages))) codingAgents
    && macHome.providerTools.mise.tools == {} && macHome.home.sessionVariables.DISABLE_AUTOUPDATER == "1";
  darwinAgentsOptOut = lib.all (id: !(builtins.elem id (casks macNoAgents)) && !(row id macNoAgents).selected) codingAgents;
  settingsOnly = builtins.elem "ghostty" (map (x: x.name) settingsOff.homebrew.casks) && !settingsOff.home-manager.users.example.programs.ghostty.enable;
  appOptOut = !(builtins.elem "ghostty" (map (x: x.name) appOff.homebrew.casks)) && !appOff.home-manager.users.example.programs.ghostty.enable;
  hostExceptions = lib.any (r: r.provider == "mas" && r.id == "Example") m.providerTools.inventory
    && lib.any (r: r.id == "mas" && r.source == "native-system") m.providerTools.inventory
    && lib.any (r: r.id == "hello" && r.source == "native-system") m.providerTools.inventory;
  sourceObjects = p.lib.programCatalog.ripgrep.owner == "modules/programs/text/ripgrep.nix"
    && p.lib.programCatalog.chatgpt.owner == "modules/programs/productivity/chatgpt.nix"
    && p.lib.programCatalog.codex.owner == "modules/programs/coding-agents/codex.nix"
    && p.lib.programCatalog.ghostty.defaults == {linux = "nix"; darwin = "homebrew";};
  groupSubset = !(row "remmina" noNetworkOrProductivity).selected
    && !(builtins.elem "remmina" (names noNetworkOrProductivity))
    && (row "ghostty" noNetworkOrProductivity).selected
    && !(builtins.elem "firefox" (names noNetworkOrProductivity))
    && !(noNetworkOrProductivity.xdg.mimeApps.defaultApplications ? "text/html");
  mediaBindings = !(builtins.elem "imv" (names noMedia))
    && builtins.elem "imv" (names restoredImv)
    && lib.all (mime: !(builtins.hasAttr mime noMedia.xdg.mimeApps.defaultApplications)
      && !(builtins.hasAttr mime restoredImv.xdg.mimeApps.defaultApplications)) imageTypes;
  groupOptIn = (row "bat" individualOverrides).selected && builtins.elem "bat" (names individualOverrides)
    && !(row "ripgrep" individualOverrides).selected && !(builtins.elem "ripgrep" (names individualOverrides));
  individualDependency = (row "codex" individualOverrides).selected && (row "mise" individualOverrides).selected
    && builtins.elem "mise" (names individualOverrides) && !(row "claude-code" individualOverrides).selected;
  consumerFontChoice = (row "d2coding-nerd-font" linuxDesktop).profiles == []
    && !(row "d2coding-nerd-font" linuxDesktop).selected
    && (row "d2coding-nerd-font" linuxDesktop).group == "fonts"
    && (row "d2coding-nerd-font" desktopFont).selected && (row "d2coding-nerd-font" wslFont).selected
    && !(row "d2coding-nerd-font" c).selected;
  directoryGroups = lib.all (entry:
    entry.group == builtins.elemAt (lib.splitString "/" entry.owner) 2
    && builtins.hasAttr entry.group c.providerTools.groups)
    (builtins.attrValues p.lib.programCatalog)
    && builtins.attrNames c.providerTools.groups
      == lib.sort builtins.lessThan (lib.unique (map (entry: entry.group) (builtins.attrValues p.lib.programCatalog)))
    && (row "ghostty" linuxDesktop).group == "terminal"
    && (row "zellij" linuxDesktop).group == "terminal"
    && (row "ghostty" linuxDesktop).profiles == ["desktop"]
    && (row "zellij" linuxDesktop).profiles == ["shared"];
  terminalOptOut = c.providerTools.groups.terminal == null
    && lib.all (item: (item.group or null) != "terminal" || !item.selected) noTerminal.providerTools.inventory
    && !(builtins.elem "zellij" (names noTerminal))
    && !(builtins.elem "ghostty" (names noTerminal))
    && (row "git" noTerminal).selected;
  individualOverGroup = (row "zellij" restoredZellij).selected
    && builtins.elem "zellij" (names restoredZellij)
    && !(row "ghostty" restoredZellij).selected;
  forcedGroupEligibility = (row "zellij" forcedHome.config).selected
    && !(row "ghostty" forcedHome.config).selected
    && !(row "chatgpt" forcedHome.config).selected
    && !(row "ripgrep" forcedHome.config).selected
    && forcedHome.activationPackage.drvPath != "";
  groupDependency = (row "mise" noDevelopment).selected && builtins.elem "mise" (names noDevelopment)
    && !(row "git" noDevelopment).selected && (row "codex" noDevelopment).selected;
  agentGroupOverride = noCodingAgents.providerTools.mise.tools == {}
    && !(noCodingAgents.home.activation ? providerMiseInstall)
    && (row "codex" forcedAgents).selected;
  nativeService = (row "paneru" macHome).selected && !noPaneru.services.paneru.enable
    && !(row "paneru" noPaneru).selected;
  systemGroup = sys.programs.nix-ld.enable && (row "nix-ld" sys).selected
    && (row "nix-ld" sys).deployment == "system" && !(row "nix-ld" c).available
    && !noSystem.programs.nix-ld.enable && !(row "nix-ld" noSystem).selected;
  inactiveSettings = !(noSettings.xdg.configFile ? "glow/glow.yml")
    && !(noSettings.home.file ? ".config/powershell/profile.ps1");
  arm = p.nixosConfigurations.fixture-arm-cli.config.home-manager.users.example.providerTools.mise.tools == c.providerTools.mise.tools;
  font = p.lib.programCatalog.font-hack-nerd-font.kind == "font";
  supplierPlatforms = p.lib.programCatalog.codex.providers.mise.platforms == ["x86_64-linux" "aarch64-linux"]
    && p.lib.programCatalog.bettercap.providers.homebrew.platforms == ["aarch64-darwin"];
  distinct = p.lib.programCatalog ? claude && p.lib.programCatalog ? claude-code;
  linuxWritable = builtins.length (editable linuxDesktop) == 4;
  darwinWritable = builtins.length (editable macHome) == 5;
  linuxDisabledWritable = editable linuxOff == [".zshrc.local"] && !linuxOff.programs.zellij.enable
    && !linuxOff.programs.ghostty.enable && !linuxOff.programs.wezterm.enable;
  darwinDisabledWritable = editable macOff == [".paneru.lua" ".zshrc.local"] && !macOff.programs.zellij.enable
    && !macOff.programs.ghostty.enable && !macOff.programs.wezterm.enable;
  ghosttySettingsWritable = !(builtins.elem ("/Users/" + "example/.config/ghostty/config")
    (editable settingsOff.home-manager.users.example));
  explicitWritableOptOut = linkedZellij.xdg.configFile."zellij/config.kdl".enable
    && !(builtins.elem ("/home/" + "example/.config/zellij/config.kdl") (editable linkedZellij));
  miseRemainsLinked = c.xdg.configFile."mise/conf.d/10-provider.toml".enable
    && !(builtins.elem ("/home/" + "example/.config/mise/conf.d/10-provider.toml") (editable c));
}'''
r = evaluate(positive)
assert r.returncode == 0, r.stderr
results = json.loads(r.stdout)
assert all(results.values()), results
print(f'✓ programs: {len(results)} selection/inventory probes')
refusals = [
    ('profile is not a directory group', '(home [{providerTools.groups.desktop = true;}]).activationPackage.drvPath', 'providerTools.groups.desktop'),
    ('empty version', '(home [{providerTools.programs.codex.version = "";}]).activationPackage.drvPath', 'not of type'),
    ('duplicate catalog definition', """
      ((p.inputs.flake-parts.lib.mkFlake {inputs = p.inputs // {self = p;};} {
        imports = [(p.inputs.import-tree "${p.outPath}/modules") {programCatalog.ripgrep.kind = "another";}];
      }).lib.programCatalog.ripgrep.group)
    """, 'duplicate definition for ripgrep'),
    ('duplicate Nix/Homebrew', """
      ((mac []).extendModules {
        modules = [{homebrew.brews = ["fd"];}];
      }).config.system.build.toplevel.drvPath
    """, 'duplicate Nix/Homebrew ownership: fd'),
    ('duplicate Nix/Homebrew cask', """
      ((mac []).extendModules {
        modules = [({pkgs,...}: {environment.systemPackages = [pkgs.codex];})];
      }).config.system.build.toplevel.drvPath
    """, 'duplicate Nix/Homebrew ownership: codex'),
    ('system duplicate', '(p.nixosConfigurations.fixture-cli.extendModules {modules=[({pkgs,...}: {environment.systemPackages=[pkgs.codex];})];}).config.system.build.toplevel.drvPath', 'duplicate Nix/mise ownership'),
    ('Darwin Nix Ghostty', '(mac [{providerTools.programs.ghostty.provider="nix";}]).system.drvPath', 'unsupported supplier platform'),
]
for agent in ['claude-code', 'codex']:
    override = f'{{providerTools.programs.{agent}.provider = "nix";}}'
    refusals.extend([
        (f'Linux Nix {agent}', f'(home [{override}]).activationPackage.drvPath', 'not of type'),
        (f'Darwin Nix {agent}', f'(mac [{override}]).system.drvPath', 'not of type'),
    ])
for label, module, message in [
    ('unknown group', '{providerTools.groups.not-a-program-group = true;}', 'providerTools.groups.not-a-program-group'),
    ('unknown ID', '{providerTools.programs.unknown.enable = true;}', 'unknown program ID'),
    ('unknown supplier', '{providerTools.programs.codex.provider = "unknown";}', 'not of type'),
    ('Linux Homebrew Codex', '{providerTools.programs.codex.provider = "homebrew";}', 'unsupported supplier platform for codex'),
    ('unsupported platform', '{providerTools.programs.chatgpt.enable = true;}', 'unsupported platform'),
    ('supplier platform', '{providerTools.programs.bettercap.provider = "homebrew";}', 'unsupported supplier platform'),
    ('class unavailable', '{providerTools.programs.remmina.enable = true;}', 'remmina requires a host class from linuxGraphical'),
    ('system class unavailable', '{providerTools.programs.nix-ld.enable = true;}', 'nix-ld requires a host class from nixos'),
    ('missing mise', '{providerTools.programs.mise.enable = false;}', 'mise-selected programs require mise'),
    ('Nix version', '{providerTools.programs.ripgrep.version = "99";}', 'version constraints require mise'),
    ('duplicate Nix/mise', '({pkgs,...}: {home.packages = [pkgs.codex];})', 'duplicate Nix/mise ownership'),
]:
    refusals.append((label, f'(home [{module}]).activationPackage.drvPath', message))
for label, expression, message in refusals:
    r = evaluate(expression)
    assert r.returncode and message in r.stderr, (label, r.stdout, r.stderr)
print(f'✓ programs: {len(refusals)} refusal probes')
# Exercise the actual rendered activation command with a fake installer. No
# tool download or real activation occurs. Keep the writable local file intact.
r = evaluate('(cfg []).home.activation.providerMiseInstall.data')
assert r.returncode == 0, r.stderr
script = json.loads(r.stdout)
import re
match = re.search(r'/nix/store/[^\s]+/bin/mise', script)
assert match, script
assert "MISE_SYSTEM_CONFIG_FILE=" in script and "provider-empty-mise-system.toml" in script
with tempfile.TemporaryDirectory() as directory:
    directory = Path(directory)
    local = directory / 'config.toml'
    local.write_text('[tools]\njq = "latest"\n')
    old = directory / 'installs/old/version'
    old.mkdir(parents=True)
    fake = directory / 'mise'
    fake.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$PROBE_LOG"\nexit "${PROBE_EXIT:-0}"\n')
    fake.chmod(0o755)
    probe = script.replace(match.group(), str(fake))
    env = os.environ | {'HOME': str(directory), 'PROBE_LOG': str(directory / 'calls')}
    for code in [0, 7]:
        r = subprocess.run(['sh', '-c', probe], env=env | {'PROBE_EXIT': str(code)}, capture_output=True, text=True)
        assert (r.returncode == 0) == (code == 0), r
        if code:
            assert 'failed to install' in r.stderr and 'codex' in r.stderr
    assert local.read_text() == '[tools]\njq = "latest"\n' and old.is_dir()
    calls = (directory / 'calls').read_text().splitlines()
    assert calls == ['--cd / install'] * 2, calls
print('✓ mise lifecycle: install only, failure propagation and preservation')

# Run the rendered PATH contribution with inherited shims deliberately first.
r = evaluate('(cfg []).programs.zsh.initContent')
assert r.returncode == 0, r.stderr
init = json.loads(r.stdout)
path_line = next(line.strip() for line in init.splitlines() if '/mise/shims' in line and 'path=' in line)
with tempfile.TemporaryDirectory() as directory:
    directory = Path(directory)
    managed, shims = directory / 'nix/bin', directory / 'mise/shims'
    managed.mkdir(parents=True)
    shims.mkdir(parents=True)
    for folder, name, output in [(managed, 'node', 'nix'), (shims, 'node', 'mise'), (shims, 'claude', 'claude')]:
        command = folder / name
        command.write_text(f'#!/bin/sh\necho {output}\n')
        command.chmod(0o755)
    line = path_line.replace(str(Path('/home') / 'example' / '.local/share/mise/shims'), str(shims))
    r = subprocess.run([shutil.which('zsh'), '-f', '-c', line + '; node; claude'],
        env=os.environ | {'PATH': f'{shims}:{managed}:/usr/bin:/bin'}, text=True, capture_output=True)
    assert r.returncode == 0 and r.stdout.splitlines() == ['nix', 'claude'], r
print('✓ mise PATH: Nix priority, available supplementary command')
