# The shared Linux graphical base is Niri and Noctalia

date: 2026-09-23
scope: unixlike
status: accepted
issue: #332
reopen-when: Niri or Noctalia cannot provide a reliable Wayland session on both VMware and UTM, or the installed hosts require incompatible session models.
source: docs/work/unixlike/niri-noctalia-graphical-base/spec.md § Decisions

The repository already owns cross-platform graphical terminals and fonts in
`homeManager.desktop`, but it has no Linux graphical session. The maintainer
chose Ryan Yin's MIT-licensed `ryan4yin/nix-config` at
`3b13291216bbea04169360b9d8a18a210d816c04` as the behavioral reference and
replaced the earlier tentative GNOME direction.

## Niri and Noctalia form the reusable base

Niri owns the Wayland compositor and Noctalia owns the shell, bar, launcher,
control center, lock screen and screenshot interface. Greetd with tuigreet
starts the session. PipeWire and WirePlumber, portals, polkit, GNOME Keyring,
dconf, graphics and removable-media services complete the system side. The
home side owns Hypridle, XWayland Satellite, Fcitx5 with Hangul, XDG and GTK
integration, media tools and the selected Wayland applications.

The reference supplies the interaction model and the integration points. Its
module tree is not imported. Fixed home paths, private inputs, secrets,
wallpaper, avatar, location, weather, monitor and hardware values, networking,
containers, gaming and the excluded application collection stay out. Existing
WezTerm, Ghostty and font ownership remains unchanged.

## Two classes preserve the composition boundary

System fragments contribute to `nixos.graphical`; Linux-only user fragments
contribute to `homeManager.linuxGraphical`. Concern files own their packages
and generated configuration and name no host. The existing
`homeManager.desktop` class remains the home of graphical programs shared with
Darwin. `unixlike/modules/flake/configurations.nix` remains the only place that
may map these classes to a host.

The classes are first evaluated, built and boot-tested in an isolated NixOS VM.
They are not composed into any declared host at this stage. A later roadmap
order may adopt them into VMware and UTM after its own installed-host evidence.

## The locked inputs are sufficient

The locked nixpkgs and Home Manager already provide the Niri, Noctalia and
Hypridle modules and the required packages. This choice adds no flake input and
does not update the lock. Generated Niri and Noctalia configuration is checked
with those locked implementations before it can enter a closure.

The cost is a larger x86_64 flake check: the boot test carries the real system
and home classes so it can detect module and package integration failures. It
cannot prove rendering, GPU acceleration, physical input, audio output or an
installed host activation; those remain evidence for the host-adoption order.
