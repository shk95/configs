# UTM Ghostty uses software OpenGL

date: 2026-09-23
scope: unixlike
status: accepted
issue: #339
reopen-when: UTM's virtual GPU gives GTK and Ghostty a working OpenGL context without software rendering, or the CPU cost makes Ghostty unusable.
source: docs/work/unixlike/graphical-vm-guests/report.md § Acceptance

UTM's `virtio-gpu-gl-pci` provides VirGL and renders Niri and Noctalia, but
Ghostty 1.3.1 could not obtain an EGL configuration from GTK when launched on
either Wayland or X11. The installed guest displayed Ghostty's OpenGL context
error. Launching the same package with `LIBGL_ALWAYS_SOFTWARE=1` displayed a
usable shell, including after a native aarch64 build and NixOS test activation.

## Keep the renderer choice on the UTM host

The UTM host module wraps only its Home Manager Ghostty package to set
`LIBGL_ALWAYS_SOFTWARE=1` for that process. Niri, Noctalia, WezTerm and the
other graphical hosts continue to use their normal renderers. The software
renderer spends guest CPU to keep the repository's default terminal usable in
this VM; that cost is accepted for the installed UTM guest. The package wrapper
preserves the Ghostty package's resources and desktop entry.

This is the supported UTM rendering mode. Reconsider it when a new graphics
stack is available on the installed guest. A successful evaluation or build
alone does not justify removing it: removal requires a Ghostty shell observed
on screen after login, followed by reboot and rollback checks on the same
candidate.
