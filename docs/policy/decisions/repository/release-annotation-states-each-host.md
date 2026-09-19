# A release annotation states each host's evidence

date: 2026-09-19
scope: repository
status: accepted
reopen-when: A domain declares its hosts in a form a repository tool can read without evaluating the domain, so an annotation can be compared with the list.
source: docs/work/repository/release-tag-contract/spec.md § Decisions

The annotation `tool/version-control/plan-release` templated had one
`Evaluation`, one `Build` and one `Native runtime` line for a whole domain.
The Unix-like domain already configures three hosts and means to configure
more. `unixlike-v2026.08.31` fits its hosts into those lines as prose, and
its `Native runtime: passed` is true of two hosts and silent about the third:
a reader cannot tell a host that passed from one nobody ran. The audit asked
only that the field names be present, so any text after them was a valid
release record.

## The annotation carries a block per host

A `unixlike` or `windows` annotation states `Domain: <domain>`, then one
block per host the release speaks for — `Host: <label>` followed by the
three lanes, each exactly once — and no lane outside a block. A lane's value
opens with `passed`, `unavailable` or `not applicable`, optionally followed
by `;` and a reference. No fourth value exists: a host whose check failed is
not released around, because the tag certifies the domain. A `common`
release deploys nowhere, so its annotation keeps the three lanes at the
domain level under the same value rule and carries no host block.

Rejected: the three lanes kept at the top with a line per host under each,
because one host's state is then read in three places and a host missing
from one lane is not visibly missing.

## A label names a kind of host, never a machine

A label matches `[a-z0-9][a-z0-9-]*` and names a kind of host, such as the
lane names of `docs/work/roadmap.md`. A tag is immutable and public, and the
hygiene scan reads the index and never a tag, so an annotation carries no
machine name, account name or machine-unique identifier; an operating-system
version or build describes a kind of host and may stand in a reference. The
grammar is checked by the audit. A machine name is not lexically decidable,
so its absence is a reviewer's evidence item in the repository Definition of
Done, owned by the repository maintainer.

## The annotation declares its own hosts

The contract holds the form, not the list: which hosts a release speaks for
is the releaser's statement. `plan-release` and the audit are POSIX shell
tools of the `repository` scope and must not evaluate a domain to learn its
hosts, and a host list written for them would be a second inventory beside
the domain's own.

Rejected: a per-domain host list file read by the repository tools.

## The tags of 2026-08-31 are excepted by name

`unixlike-v2026.08.31` and `windows-v2026.08.31` are immutable and predate
the form. The audit names those two and holds them to the check they were
created under, the presence of the four field names. The list is closed.

Rejected: a cutoff date read from the tag name, because a tag created later
with an earlier date in its name would pass as one of them.

Cost: an annotation is longer, and a release that speaks for many hosts
repeats three lines for each.
