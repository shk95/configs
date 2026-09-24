# One private repository owns the current Unix-like hosts

date: 2026-09-24
scope: repository
status: accepted
reopen-when: Two host groups require different repository access, review ownership or release schedules that per-host flakes and locks cannot express clearly.
source: docs/work/unixlike/host-provider-api/spec.md § Decisions

The seven current Unix-like outputs have one maintainer and are early in their
move out of `configs`. Separate repositories now would repeat access control,
checks and migration records without a host boundary that needs them.

`shk95/configs-hosts` is one private repository for all seven instances. Each
host has its own flake and lock, so a provider input can be advanced and
verified for one host without advancing another. Host identities, profile
choices, hardware facts and secret delivery belong there. The repository
does not silently import another host's files.

`shk95/configs-host-template` is a public GitHub template with a synthetic,
non-secret host. Creating `configs-hosts` from it was a one-time copy. The
generated repository owns subsequent edits and may diverge; no template
update is synchronized into it. The only continuing code dependency is a
host's explicitly pinned `configs` Unix-like provider API. A host adopts a
new provider revision through its own lock and verification.

SOPS + age recipients, private identities and encrypted values are host-owned.
The public template records the setup boundary without a real recipient or
secret. Real recipients and delivery modules are added only when the host's
key and secret need are verified. Evaluation and builds do not authorize
activation.

Rejected: a separate private repository per host at this stage, because the
same maintainer would repeat governance with no current access or release
boundary. Also rejected: treating the public template as a shared framework
or automatically synchronizing its structure into generated repositories;
that would make template changes an implicit host adoption.

Cost: a single private repository can later hold unrelated host changes in
one history. Per-host flakes and locks keep their outputs independent; the
reopen condition names when repository ownership itself should be split.
