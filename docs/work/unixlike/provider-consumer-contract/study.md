# State baseline, template transport and host extension research
kind: study
date: 2026-09-27
scope: unixlike
status: open

## Evidence boundary

Research ran during 2026-09-26/27 on aarch64-darwin with Nix 2.34.8.
Provider e11bd1368d2f5138ad0f9b7017040b2b76e055e6; private host checkout
f7f3010ca4675f705e8a8895dede19786530b6ca; template checkout
dcb8c6d81ebd72ca4b19e8364269494ffcbdc5c2. Provider nixpkgs was
e94cb152ed51bd6e24eb4a41f1460252beb52cd2 and Home Manager was
7b4c5ec4bedaf1e062bbc1bcaeddbc6bd242aa1b. Source/evaluation findings below
are not build, runtime or activation evidence. No project source/lock or
host configuration was changed by these probes.

## State versions

The maintainer selected central NixOS/Home Manager 25.11 and Darwin 6 after
reviewing the history. This supersedes the earlier research recommendation
to make all three state versions host inputs; do not revive that proposal
from an old scratch study. Centralization and future reviewed changes are
compatible; routine dependency updates do not advance the baseline.

Spotlight was fixed in commit 962fc6f by changing home.stateVersion from
25.05 to 25.11, not 26.11. Pinned Home Manager copyapps/linkapps modules use
25.11 as the threshold. NixOS UTM and OrbStack 25.11 and VMware 26.05 were
deliberately aligned with installation/image history. Desktop 26.11 was
introduced as provisional evaluation identity, not Spotlight configuration.

For each provider fixture and each private NixOS consumer, compare the original
toplevel drvPath with this temporary extension:

```nix
candidate = original.extendModules {
  modules = [{ system.stateVersion = lib.mkForce "25.11"; }];
};
```

The extension changes effective system.stateVersion only. It intentionally
leaves read-only host.stateVersion metadata unchanged to isolate behavior;
it is not the final centralization/schema implementation. Each private flake
used its own existing pinned provider/input graph, without lock writes.

| Composition | Old value | Candidate | Provider comparison | Private consumer comparison |
| --- | --- | --- | --- | --- |
| Desktop | 26.11 | 25.11 | identical drvPath | identical drvPath |
| VMware | 26.05 | 25.11 | identical drvPath | identical drvPath |
| NixOS WSL | 26.05 | 25.11 | identical drvPath | identical drvPath |
| UTM | 25.11 | 25.11 | identical drvPath | identical drvPath |
| OrbStack | 25.11 | 25.11 | identical drvPath | identical drvPath |

For durable evidence, the before and after drvPath hash prefixes were:

| Composition | Provider | Consumer |
| --- | --- | --- |
| Desktop | 4dkzv6hqih3ln5crpqrffkrppsyvvg6w | hmip4rjijlzpvqyda35y9gngixqb02ar |
| VMware | vypnlfviszwdfpv3kdw81jgyqnznkk1h | d6xmrm4dmpar5wqn5vgsak3y5dlg9aka |
| NixOS WSL | hq5g543932jg91gy89iibws3zaangwvy | 30asjccj0wfgavh68qjjazz8vc16n168 |
| UTM | dyazvwb3yczgwf9p88xwm1hhizpwnan6 | 85sv5mj6hwiprljxwknbf8w12bqv06az |
| OrbStack | 7q9g2fs700pxba9sac52a3hyfn0zkzd6 | kglhzf4jhzsp23n1f8sdj1bnvhbhwr3d |

Reproduce provider comparison from the configs checkout, without activation:

```sh
nix eval --impure --json --expr '
let
  p = builtins.getFlake ("path:" + toString ./unixlike);
  lib = p.inputs.nixpkgs.lib;
in builtins.mapAttrs (_: original:
  let candidate = original.extendModules {
    modules = [{ system.stateVersion = lib.mkForce "25.11"; }];
  }; in {
    before = original.config.system.stateVersion;
    after = candidate.config.system.stateVersion;
    oldDrv = original.config.system.build.toplevel.drvPath;
    newDrv = candidate.config.system.build.toplevel.drvPath;
  }) p.nixosConfigurations'
```

For a private consumer, obtain original from that flake's nixosConfigurations
and lib from its inputs.configs.inputs.nixpkgs.lib. Rediscover directories and
pins through Context Bridge first; do not substitute current provider dev
while claiming to test the adopted revision.

Pinned nixpkgs has post-25.11 gates affecting PostgreSQL, MySQL, Nextcloud,
Dovecot, Sabnzbd, Lauti, OliveTin, Tandoor, Taskchampion, Grav, Netbox, Hyphanet
and ZFS root force-import behavior. All twelve services and ZFS support
evaluated disabled in all five provider fixtures. Stalwart's similar gate
uses its separate service stateVersion. No compensating behavior option was
needed for these current compositions. Future host extensions enabling other
services need separate review; equal derivations do not inspect live drift.

Implementation must rerun constructor/fixture/template and consumer checks
after removing the old host field, then obtain the appropriate build and
host-adoption evidence. Home Manager 25.11 and Darwin 6 stay unchanged.

## Extension and capture probes

Current configurations.nix accepts systemModules/homeModules for mkNixos and
mkDarwin, and homeModules for mkHome. Actual mkDarwin evaluations showed:

- Added environment.variables.HOST_TEST evaluated to yes.
- time.timeZone = lib.mkForce "UTC" evaluated to UTC.
- Plain time.timeZone = "UTC" conflicted with the provider's Asia/Seoul;
  builtins.tryEval returned success=false.

Nix is not last-file-wins. Make intended preferences mkDefault, document
list concatenation/order/replacement and preserve read-only fields/types and
assertions. mkForce is a technical mechanism, not a blanket supported-contract
escape. Internal embedded payloads need named extension options rather than
host copies of provider activation scripts.

Current Justfile karabiner-capture invokes tool/version-control/commit capture
karabiner, writing provider karabiner.json and symbolic-hotkeys.json.
The HM activation in modules/programs/karabiner/module.nix references these
files directly. Moving only capture output would not make subsequent builds
consume host data. Change the host payload API and capture destination together,
and separate capture from provider publication. Keep projected desired state
distinct from application runtime keys. Array/delta deletion semantics remain
an implementation design task before pickup.

## Template and platform probes

Earlier scratch Git-flake experiments found: overriding a provider input
uses its candidate dependency graph without changing the consumer lock during
ephemeral evaluation; persisted adoption updates the provider's dependencies
while preserving an unrelated root input. These are fixture observations, not
a guarantee for arbitrary input overrides.

For a local Git source, a submodule payload was absent by default and present
with submodules=1 or inputs.self.submodules=true; a local path included it,
while git archive omitted it. A GitHub metadata probe did not establish that
the real remote submodule payload is fetched. Avoid making provider evaluation
depend on template contents, and test the chosen generation transport.

The actual template with a temporary current-provider override evaluated its
OrbStack toplevel; its original lock remained unchanged. All seven existing
synthetic Unix-like compositions evaluated their final derivations. Intel
Darwin, despite its constructor enum, failed with pinned nixpkgs reporting
that 26.11 dropped x86_64-darwin. Minimum supported Nix/OS versions were not
established by local Nix 2.34.8 success.

References: [Nix module priorities](https://nixos.org/manual/nixos/stable/#sec-option-definitions-setting-priorities),
[Home Manager state version management](https://nix-community.github.io/home-manager/usage/upgrading.html#state-version-management),
[Nixpkgs release notes](https://nixos.org/manual/nixpkgs/unstable/release-notes),
[Git submodules](https://git-scm.com/docs/gitsubmodules).
