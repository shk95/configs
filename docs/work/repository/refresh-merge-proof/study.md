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

## Required preparation binding study, 2026-10-04

# Required-merge preparation bindings — recommended design (unadopted)

Read-only review 2026-10-04. Compared actual `unixlike/tool/refresh_inputs.py` at PR504 12a40ca/current dev32f4e75 and original4 adapter construction/context. No SourceData class exists in this actual Python utility; source_snapshot() is its concrete source-data contract. Nix flake metadata supplies `locks`, not a consumed producer Git commit identity. New names/receipt/schema below are PROPOSALS requiring dated review; no source/Git/API changes, source5 readiness or actual Nix/producer operating proof.

## Recommendation: prepare from verified computed TREE, form merge commit later

Choose (a). Original5 independently computes and verifies required merge TREE T from previous/base/unique merge-base raw carrier. A separate credential-free preparation producer realizes EXACT tree bytes into an owned source directory and runs the reviewed data-only utility there. Its receipt binds roots, carrier/runtime proof identity and input tree T, not a not-yet-created merge commit. After successful actual job completion, controller observes completed-at and approved declaration custody, canonically forms unsigned merge commit M(tree=T, parents=[previous,base], date=completed-job epoch), then final lock-only commit H(parent=M). Candidate retains source=parent=M. Producer need not know M; no field in the preparation digest or receipt contains M, H or their operation IDs.

This avoids time/self-hash cycles. Changing generated message/declaration after preparation yields a different M/H and requires exact reviewed declaration binding, but does not pretend the utility ran on that Git commit; it ran on literal TREE T. All generated bytes/context/operation IDs are finalized before durable refresh-result publication and before public effects. Neither source5 nor a transport helper may relabel tree-run as commit-run evidence.

## Actual utility justification and limits

refresh_inputs.py:53 source_snapshot(root,ignored) recursively records regular-file SHA256 and executable mode, refuses symlinks, ignores .git and temporary claim/data directories. It does not call Git, inspect HEAD, read author/committer/time or require a commit. Lines81-96 read literal before flake.lock/exclusions/source snapshot and call `nix flake metadata --json --no-write-lock-file --reference-lock-file <before> path:<root>`, consuming only result['locks']. Lines116-131 call selected `nix flake update ... --flake path:<root>` then validate candidate with metadata against candidate reference lock. Selection/follows/exclusions are independently checked; source snapshots must remain unchanged before final owned lock replacement. This supports immutable tree input preparation without a preexisting M.

Current unixlike/flake.nix declares fixed inputs/follows; this read-only search found no self.rev/dirtyRev/sourceInfo/lastModified/narHash usage in current Unix-like Nix sources. That is source evidence, not an actual Nix metadata equivalence test. Path-flake evaluation can in general depend on path/source metadata. Before admitting future source, producer contract must explicitly realize stable permitted path/modes/content and reject unsupported source-metadata/absolute-path/mtime dependence or prove it under exact Nix/runtime/source closure. Do not silently claim tree execution equals Git checkout evaluation. No utility invocation/network was executed in this review.

## Exact identity mapping

| Name | Required5 proposed meaning | Binding |
| --- | --- | --- |
| previous | Prior public refresh head P | literal carrier commit, current branch observation |
| base | Actual required dev B | literal carrier commit plus fresh current-dev identity |
| merge-base | Independently derived unique ancestor A | complete raw DAG and Git cross-check |
| input-tree / merge-tree | Independently computed full tree T before refresh | original5 computation; exact tree realization and producer receipt |
| base-lock | SHA256 literal B:unixlike/flake.lock (diagnostic/proof operand) | base snapshot raw object; NOT candidate.before-lock unless coincidentally equal |
| merged-lock / before-lock | SHA256 literal T:unixlike/flake.lock | actual utility original bytes, merged result blob+mode, receipt.before-lock and candidate.before-lock |
| lock | SHA256 validated after.lock | receipt.after-lock/candidate.lock; generated final blob |
| candidate.source | New canonical required-base merge commit M | source=parent=M, tree=T and ordered parents[P,B] verified; NOT preparation workflow source |
| candidate.parent | M | final H has exactly one parent M |
| candidate.tree | Final tree U | independently replace only T's unixlike/flake.lock with after data; preserve every other entry/mode |
| candidate.head | H | canonical final unsigned single-parent commit with exact reviewed declarations |
| utility-source | Approved PUBLIC commit selecting exact utility code/runtime closure | independently existing before producer runs; utility-manifest matches original utility blobs; may differ from B/M/controller-source |
| controller-source | Accepted PUBLIC master commit selecting original5 semantic/transport package and workflow authority | batch approval/control/manifest and original context.master; independently existing before job; no implicit equality to B/M |
| producer-source | Actual completed manual preparation run.head_sha/workflow blob commit | reviewed public source/utility workflow custody; explicit binding to approved utility-source/producer role, not M |
| source-fingerprint | Digest of exact pre-refresh realized utility input source map | domain-relative regular file SHA256/mode map before replacing lock; recompute from T:unixlike literal closure with explicit ignored temporary paths |

Current4 candidate.before-lock hashes base's lock because source=parent=base and refresh_construction reads original(candidate.base). Required5 must instead hash COMPUTED MERGED LOCK. A base-lock substitute is invalid whenever merge retained previous lock edits. Required5 final lock-only proof compares H/U to M/T, not to B. Initial support that every non-lock leaf equals B still preserves T's possibly novel merged lock; it does not authorize replacing before.lock with base.lock.

## Proposed receipt/consumption evolution

Do not overload current4 receipt.source (commit) with a tree SHA. Version a separate required5 receipt grammar, with explicit input-kind='computed-merge-tree', input-tree=T, previous=P, base=B, merge-base=A, carrier-manifest digest/runtime-profile, utility-source/utility-manifest, producer-source/workflow-blob, source-fingerprint, literal before/after lock digests/mode and inventory. Keep exact public repository/run/attempt/job/artifact/archive/receipt provenance as observed transport custody. No asserted M/H, declaration, approval or checks in the data-only artifact.

Preparation consumption digest hashes canonical exact public producer identity + artifact/archive/receipt + roots/input-tree/carrier + utility-source/manifest, excludes batch, transient writer identities, M/H, construction's own digest and operation IDs. This is a NEW5 consumption grammar, not an edit to original4 digest. Original5 replay returns accepted consumptions; global loader enforces same identity not consumed by another batch. Unused revisions never create actual consumption.

Actual job completed-at cannot be truthfully authored inside a receipt before that job has completed. Controller must independently observe exact sole job/run/latest attempt completed success and completed-at AFTER completion (and reobserve custody/artifact), use canonical epochUTC in generated M/H, and carry that observed timestamp in transport-owned construction binding. Producer data receipt can bind its data creation, but cannot certify its own future completed-job time. Missing/ambiguous/changed completion metadata refuses. Epoch/declaration custody remains asserted offline in semantic fixtures until transport provides observed receipts; no synthetic metadata upgrades it.

## Order without a cycle

1. Select accepted original5 controller/utility sources; independently verify P/B/full graph and compute T from carrier. No merge commit/public POST.
2. Producer independently validates/realizes T, obtains before.lock from T, runs reviewed data-only utility on path source, emits exact receipt+before/after. Bind actual source fingerprint/inventory and roots, not M.
3. Observe actual successful completed producer job/artifact and approved Release-* declaration custody. Compute consumption digest and canonical M with completed-job epoch/tree T/ordered parents P,B; compute H/U and complete novel object closure. Finalize candidate.source=parent=M, before-lock=merged-lock. Re-run original5 independent proof.
4. Atomically introduce immutable carrier + refresh-result/context/index; actual original private history derives introduction, no caller anchor commit. Publish/independently observe all novel merge/final objects in dependency order, then ref/PR. No private acknowledgement/ODB object is a public receipt.

Any actual change to P/B/input tree/fingerprint/before.lock/utility closure invalidates preparation; reprepare explicitly. A changed approved declaration alone changes generated commits but must be reviewed/rebound before effects; it cannot alter preparation input tree or accepted producer evidence.

## Alternatives rejected for this proposal and review gates

(b) could precompute M before preparation only with a separately fixed non-completion epoch/metadata independent of producer output. That changes the reviewed completed-job-date custody contract and requires actual materialization/source=commit producer semantics. Keeping epoch=completed-preparation while requiring receipt.source=M is causally impossible: M is unknown until job finishes. Do not substitute assertion dates or predict a future completion time.

Accept exact5 receipt and candidate/source meanings through a dated amendment; verify path-Nix behavior on realized merge tree with immutable mode/mtime policy, fingerprint encoding and utility input-selection fixture; independent before-lock divergence fixture where B-lock != T-lock; actual job completion timestamp custody; separate controller/utility/producer source mismatch refusals; declaration changes/consumption no-crossbatch cases. Preserve original1–4 schemas/replay and initial4 source=parent=base. These gates remain pending; this recommendation does not assign source implementation.
