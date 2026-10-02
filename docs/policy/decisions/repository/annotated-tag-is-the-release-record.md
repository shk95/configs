# The annotated tag is the only release record

date: 2026-08-31
scope: repository
status: accepted
issue: #120
reopen-when: A consumer needs a release artifact or a note that a tag annotation cannot carry.

The first domain tags were pushed on 2026-08-31: `windows-v2026.08.31` and
`unixlike-v2026.08.31`, annotated, under the `<domain>-vYYYY.MM.DD[.N]`
scheme, each carrying the evidence `tool/version-control/plan-release`
templates. (The Unix-like tag was recreated minutes after its first push, to
carry the native-runtime evidence from both Unix-like hosts, before anything
had consumed it; `common` has no consumers and stays untagged.) The
maintainer decided then that no GitHub Release is created for those tags or
for any later one.

The annotation already holds what a release record must: the domain, the
commit, and the evaluation, build and native-runtime evidence stated
separately. It is immutable, which is what lets a tag certify anything. A
Release is a second surface for the same event, editable and deletable
without touching the tag, so the two records could disagree and the mutable
one would be the more visible of the pair.

Rejected: a Release per tag mirroring the annotation, because a mirror that
can drift certifies nothing and costs a step per release; Releases for notes
only, because a note belongs in the annotation or in the pull requests the
tag reaches.

Cost: no download page and no release feed on GitHub. A consumer reads
`git tag -n` or `git show <tag>`.
