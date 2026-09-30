# Unix-like input refresh

Run `just up` or `unixlike/tool/refresh-inputs` to refresh this provider's
independently locked direct inputs. The flake is resolved from the tool's
location, independently of the caller's working directory. `--check` reports
the current selection offline without updating the lock.

Runtime prerequisites are Nix with flakes and the named-input update,
reference-lock and output-lock options (verified with Nix 2.34.8), plus a
functional Python >= 3.9 using only its standard library. The launcher
checks the interpreter by executing it. Missing runtime exits 69; it does
not install software. An explicit temporary runtime environment can use
the provider's locked nixpkgs Python:

```sh
nix shell --no-update-lock-file --no-write-lock-file --inputs-from path:./unixlike nixpkgs#python3 --command just up
```

`unixlike/flake-refresh-exclusions.json` starts with
`{"formatVersion":1,"exclusions":[]}`. To omit an independently locked direct
input, add `{"input":"home-manager","reason":"reviewed compatibility hold"}`
to `exclusions`. Unknown/duplicate names, follows aliases, unsupported format
or blank reasons fail. Excluding Home Manager preserves its own source,
while its followed nixpkgs owner may still refresh. Newly added independent
inputs participate automatically; transitive nodes are not selection names.

The tool uses a temporary candidate and verifies exclusions, graph validity
and unchanged original sources before atomic lock publication. Source checks
include file bytes and permission modes, since executable bits affect Nix
source identity. Unchanged upstreams preserve the original bytes; an empty
selection runs no update
command. Failed pre-publication operations leave the original lock intact.
Runtime temporary directories and the cooperating refresh claim are removed
on normal exit. If abruptly interrupted, inspect `.refresh-inputs-running`
and `.refresh-inputs-*` under `unixlike/`, confirm no refresh owns them and
preserve useful evidence before explicitly removing stale runtime artifacts.
Do not blindly rerun or remove a live claim. An interruption at atomic
publication can leave a complete old or new lock; inspect the actual file.
The tool does not provide compare-and-swap against arbitrary outside editors.
Provider source symlinks (including a symlinked lock or exclusion file) are
refused: fingerprinting a link cannot guard changes to its external target.
The current provider source tree contains no symlinks. Atomic replacement
requires a local filesystem with atomic same-directory rename; it prevents
partial file visibility, but is not a power-loss durability guarantee.

No commit, push, schedule, release, host lock update or activation is performed.
Review a resulting provider lock and publish it separately from tool source.
