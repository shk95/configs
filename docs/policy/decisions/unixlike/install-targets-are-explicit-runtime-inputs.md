# Installation targets are explicit runtime inputs

date: 2026-09-23
scope: unixlike
status: accepted
issue: #341
reopen-when: A supported installer can accept a typed disk identity without committing a machine-specific identifier or generating a wrapper configuration.
source: docs/work/unixlike/installation-and-deployment/spec.md § Let each host class own its storage layout

Disko declares how each ordinary NixOS host is partitioned and formatted, but
the repository does not know which physical device an installation may erase.
The tracked layouts therefore use `/dev/disk/by-id/INSTALL_TARGET_REQUIRED`, a
deliberately unusable value. No command scans block devices or replaces it by
position, model or size.

`unixlike/tool/install-plan` accepts one inventory host, one persistent
`/dev/disk/by-id/...` path and a new output directory. It refuses hosts without
a declared one-disk layout, writes the choice into a small wrapper flake, locks
that plan and evaluates the selected value. Planning writes only that
directory. The destructive nixos-anywhere command is text in its `PLAN` file;
running it remains a separate, explicitly authorized maintainer action after
the path is compared with the target's own block-device listing.

Disko's install test replaces declared disk paths with disposable QEMU disks.
That is the only automatic substitution: it exists inside the test derivation
and cannot select a device on an installed host. The test may prove layout,
installation and boot behavior, while a real format and installation remain
separate evidence.
