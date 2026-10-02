id: repository/classify-unixlike-old-roots
kind: workaround
statement: Historical Unix-like root paths and the exact retained Nix editor settings keep their owning scope while migration deletions remain in master-to-dev ranges.
since: 2026-10-01
exit-when: master retains no tracked flake.nix, flake.lock, assets/, modules/, tool/checks/, tool/darwin/ or .vscode/settings.json path after the Unix-like migration and editor relocation.
watch: manual
review-by: 2026-10-31
issue: #472
decision: docs/policy/decisions/unixlike/unixlike-domain-owns-its-tree.md § The Unix-like domain owns its tree
owner: repository maintainer

The original master classifier owns the six historical namespaces as Unix-like.
The retained editor file contains only NixEnvSelector keys and is relocated in a
separate Unix-like change. These answers classify history and migration deletions;
they do not authorize new Unix-like source outside its owning tree. The destination
unixlike/.vscode/settings.json already follows ordinary domain classification.

The disposable classifier arm and positive historical fixtures carry this entry's
tag. Negative unrelated-path fixtures remain after retirement. Inspect master
itself at review; a dev merge, vanished process or calendar tag cannot satisfy the
exit condition. Remove the tagged arm, historical positive fixtures and this entry
together only after the condition holds. No promotion is assigned by this measure.
