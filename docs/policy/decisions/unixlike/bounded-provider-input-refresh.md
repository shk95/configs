# Bounded provider input refresh

date: 2026-09-30
scope: unixlike
status: accepted
reopen-when: Refresh requires another repository's locks, overridden follows, additional permanent writes or deployment.
source: docs/work/unixlike/automatic-flake-refresh/spec.md § Pickup amendment, 2026-09-30

## Adopted utility boundary

The provider owns its Unix-like input graph and lock. Its refresh utility
selects independent direct inputs by default, including newly added inputs;
the tracked configuration lists only explicit exclusions and their reasons.
An exclusion preserves that input's own locked source and does not sever its
follows relationship. Unknown, duplicate and alias exclusions are refused.
The initial exclusion list is empty. Compatibility baselines and consumer
locks remain separate ownership decisions.

The operator explicitly invokes refresh. The utility publishes only a
validated provider lock, checks for stale source/configuration/lock state,
preserves bytes for no-op outcomes and refuses incomplete candidates. Empty
selection must not become an update-all request. Temporary runtime files are
removed and do not become permanent source outputs. No commit, publication,
schedule, release or deployment authority follows from this utility.

This boundary keeps routine input maintenance independent of repository
scheduling and consumer realization. Deterministic disposable local flakes
prove both successful refresh and refusal before lock publication.
