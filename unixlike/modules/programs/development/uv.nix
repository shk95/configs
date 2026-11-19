# Replaces conda; modules/foundation/shell/shared.nix no longer sources its hook. This
# module does not remove an unmanaged `~/miniconda3` installation or a hook
# in `~/.bashrc`.
#
# No `settings`. uv reads ~/.config/uv/uv.toml and this module will write it, but
# every value worth setting is already uv's default, and a file full of restated
# defaults is the exact failure that modules/programs/starship.nix exists to record.
# It goes in when there is a reason.
#
# uv prefers to download its own CPython. Those portable builds use a hardcoded
# interpreter path; modules/programs/nix-ld.nix supplies the loader on NixOS.
# This declares compatibility support, not runtime verification of uv's Python.
_: {
  # The package ships its own `_uv` completion, which programs.zsh picks up from
  # the profile's share/zsh/site-functions — so, as expected, there is no shell
  # wiring to add.
  modules.homeManager.shared.programs.uv.enable = true;
}
