id: unixlike/composition-in-one-place
statement: Only one file decides which module classes reach a Unix-like host, including classes selected through a host choice; a feature module contributes to classes and never names a host or forces another class's decision.
rationale: AGENTS.md § Goal and authority
enforced-by: tool unixlike/tool/checks/composition
enforced-by: fixture unixlike/tool/checks/composition-test
enforced-by: fixture unixlike/tool/checks/flake-test

The classes are the whole interface between a feature file and a host. The
host choice names only a profile its machine kind offers; the composition file
turns that choice into imports. The flake fixture accepts a selected and an
omitted profile and refuses an unavailable one. The composition tool's
check is lexical because the two ways a feature file can take the decision
are literal names: a host flavour (`homeConfigurations` and its two
siblings) and a priority override (`mkForce`, `mkOverride`, `mkVMOverride`).
Comments are stripped first, `mkDefault` stays allowed because lowering a
file's own priority forces nothing, and the composition file's own subtree
is not a feature file. "Names a host" is read as naming a host flavour: a
feature file that conditions on an identity value (`config.identity.…`,
`config.home.username`) is not caught lexically, because feature files read
identity legitimately, and is the reviewer's to notice. The leak that
motivated #127 — the desktop class forcing a zellij file the shared class
already declared — is gone: the zellij asset is rendered once from
`homeManager.shared`, and since #156 no second class writes into
`programs.zellij.extraConfig` at all.
