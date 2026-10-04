# Required-base merge carrier feasibility
kind: study
date: 2026-10-04
scope: repository
status: open

Root supplied a live graph proxy: master c98ce7d, base 32f4e75, merge-base ae5bf44;
1184 commits, 199 trees, 630 blobs, 6236891 raw bytes, 7 chunks and 232070
manifest bytes. This measures feasibility only, not an actual previous refresh,
accepted carrier, native runtime or operating receipt. Full ancestry plus three
snapshots needs a retained chunk carrier; small transcript references preserve the
4 MiB API limit. No ancestry truncation or silent bound widening is permitted.

Modern Git merge-tree computes a complete tree without checkout/index; multiple
bases are unsupported here. Exact runtime and admitted original attribute behavior
need fixtures. See [git-merge-tree](https://git-scm.com/docs/git-merge-tree) and
[git-merge-base](https://git-scm.com/docs/git-merge-base).

Omit caller anchor commits to avoid same-commit event self-hash cycles. Select
original introducing tree through authenticated private history; verify immutable
retention across every later transition. Source pickup remains NOT ready until
staging/publication, atomic event/index adoption, loader quotas/interfaces and
unknown-acknowledgement recovery are settled. Verifier objects are not public API
receipts. Source/native, transport and actual operating evidence remain separate.

## Actual native profile study, 2026-10-04

# macOS merge-proof native feasibility (actual disposable Git)

2026-10-04. Darwin, `/etc/profiles/per-user/shk/bin/git`, actual `git version 2.55.0`. Python runner `/opt/homebrew/bin/python3.13`. No install, network, host configuration or repository/worktree source changes. This is runtime design review evidence only: no source5 fixture/delivery, Linux/Windows proof, approved carrier or operating receipt.

Repro runner: `/tmp/configs-merge-native-feasibility.py`. Final retained bare SHA1 ODB and actual logs: `/tmp/configs-merge-native-30ey_9gy/proof.git`, `commands.json`, `results.json`; aggregate output `/tmp/configs-merge-native-final-output.json`. An initial runner used a nonexistent Git path and failed before Git init; corrected to the actually observed binary. Subsequent early assertion failures exposed the renormalize abort below; final runner records all outcomes and exits0.

## Commands and isolation

Every command uses the fixed executable with `--no-replace-objects -c core.attributesFile=/dev/null -c core.hooksPath=<owned empty dir> -c core.autocrlf=false -c core.safecrlf=false -C <owned bare repo>`. Bare repo initialized with `init --bare --object-format=sha1 --template=<owned empty dir>`. Raw fixture blobs are written by `hash-object -w --stdin`, canonical direct trees by `mktree`, deterministic commits by `commit-tree <tree> [-p <parent>]` (identity/date set solely in the fresh explicit environment). No checkout/index/remotes/fetch/network commands.

Fresh allowlisted environment: fixed PATH, owned HOME/TMPDIR, LC_ALL/LANG=C/TZ=UTC; GIT_CONFIG_NOSYSTEM=1, GIT_CONFIG_GLOBAL=/dev/null, GIT_ATTR_NOSYSTEM=1, GIT_NO_REPLACE_OBJECTS=1, GIT_NO_LAZY_FETCH=1, GIT_GRAFT_FILE=/dev/null, GIT_ALLOW_PROTOCOL='', GIT_TERMINAL_PROMPT=0. No inherited credential/proxy/Git variables. Repo info/attributes, objects/info/alternates, refs/replace absent; nonshallow assertion and fsck --full passed. Original repo .gitattributes remains in literal trees. Poisoned disposable HOME/.gitconfig with merge.renormalize=true and external '* binary' attrs did not affect the explicitly isolated false-profile merge (same exact tree). This proves this fixture's config boundary, not full OS isolation or a packaged executable closure.

Independently parsed literal commit headers/parents and SHA1-checked all reachable commits to zero-parent roots, computed common ancestors and removed dominated ancestors, then compared the unique result to `merge-base --all <previous> <base>`. Actual toy graph3commits/root586713e6553a7a65edec4d2c5e97d9d8acc2fdfd; independent unique base matches Git.

Exact computation command: `merge-tree --write-tree --no-messages --merge-base=<unique-base> <previous> <base>`. Successful result requires exit0 AND one exact tree line. Exit1 emits an apparent tree plus conflict-stage entries even with --no-messages; accepting its first line would falsely accept conflict. Multiple best bases are rejected before invoking merge-tree; no virtual-base inference.

## Actual outcomes

- Clean disjoint lock lines: previous6f5e4fee2e6a53444f22ccbe90229b0a22825b46 changed first line to ONE; base dea037caf22b626689db0b8abf300afb72ab5882 changed last line to FIVE. Exit0, one tree44de3baf7b9b6b19c12783ef430d295fb5f43fd9; merged bytes `ONE\ntwo\nthree\nfour\nFIVE\n`. Novel blobdbf86fa8f46c0e88522ea39b32d0c9d0bc8f120c differs from all three operand lock blobs; full result tree differs from operand trees. This demonstrates computed novel objects need explicit closure/public observation.
- Same-line lock conflict: exit1, conflict stages on unixlike/flake.lock; finitely reject.
- Non-lock plain.txt conflict: exit1 with stages; finitely reject, no lock-only projection to discard it.
- Criss-cross two-parent graph: merge-base --all returns two distinct best bases77fe95a6b140205dfa0ec33cd521a8f68e2eb218 and19d34a16ba5a070071487d68d79ebc021ec2a46c. Runner refuses before merge-tree. Full graph exists; ambiguity is genuine.
- `check-attr --source=<original base> text eol -- unixlike/flake.lock plain.txt`: exit0, lock text=set/eol=lf, plain text=unset/eol=unspecified. This reads original tree attributes without a checkout.

## Built-in attribute source matters

The bare default profile and explicit `-c merge.renormalize=false` WITHOUT GIT_ATTR_SOURCE allowed clean disjoint text merges even when original `.gitattributes` declared `unixlike/flake.lock binary`. Thus storing/validating original attributes alone does NOT prove they were applied by bare merge-tree.

With `GIT_ATTR_SOURCE=<independently hashed previous commit>` and explicit `merge.renormalize=false`, the same binary case exits1 (correct binary refusal); -text, text=auto and text eol=crlf disjoint clean cases exit0. The existing text eol=lf clean case also succeeds with explicit source/false and ignores poisoned external attrs. Binary is a built-in macro expanding unset diff/merge/text: its accepted spelling must be distinguished from forbidden user-defined macros by reviewed parser.

CRLF-only previous versus LF/content-changing base with original text eol=lf: default false exits1, both with and without exact GIT_ATTR_SOURCE. This is finite conflict, not a promise that eol normalizes existing operand bytes during ordinary merge. Permit text/eol while preserving normal false behavior; do not silently preprocess blobs.

Explicit `merge.renormalize=true` on that CRLF case ABORTS (Python returncode-6/SIGABRT) with `BUG: attr.c:685: non-INDEX attr direction in a bare repo`. Same abort with GIT_ATTR_SOURCE absent, previous or base. Preserve this actual limitation. True was an exploratory unsupported profile, not specified by the reviewed ordinary-false contract. Recommend exact original5 runtime profile force `merge.renormalize=false`; no ambient config may enable true. Any abort/nonzero/extra output is refusal, never merge proof.

Recommended design clarification (PROPOSAL): select GIT_ATTR_SOURCE=verified previous/ours commit explicitly; independently parse all previous/base/merge-base attr files and admit only supported declarations. Until exact attribute evolution semantics are reviewed, refuse differing .gitattributes across these snapshots rather than guess one or blanket-disable them. This narrows support and requires dated plan acceptance. No current source implementation adopts this proposal.

## Limits

Tiny deterministic fixture graphs, not 4096-commit/16MiB/deadline/stress proof. No measured original private introduction, actual GitHub API canonicalization, public publication or approval custody. No Windows/Linux behavior. No signed-original commit carrier fixture in this run; signed originals remain a separate required fixture. No native source5 executable closure pin/dispatch. Process timeout20s was imposed per disposable command; streaming aggregate disk/output/process-group termination was not implemented or proved. Core attribute/config boundaries checked above do not imply platform isolation.
