# CI and release evidence follow the provider verification boundary

date: 2026-10-13
scope: repository
status: accepted
reopen-when: Provider verification adds or removes an evidence lane represented in automatic annotations.

CI invokes the Unix-like provider's complete suite once, alongside its format
and lint checks. Repository classification, effect dispatch, policy scans and
the stable Required checks gate remain in place. Unix-like semantics stay in
the owning suite; repository CI does not maintain a second fixture list.

Automatic Unix-like annotations report composition evaluation and focused
provider-owned artifact checks on the CI system. Host native runtime is
not applicable to this provider qualification and is stated as such. Native
execution of parser and script fixtures does not certify a consumer host.
Existing immutable annotations and their historical evidence are unchanged.

This connection adopts
`docs/policy/decisions/unixlike/provider-verification-boundary.md`. It replaces
the provider native-host build requirement in
`docs/policy/decisions/repository/ci-evidence-without-hosted-runners.md` and the
provider runtime wording in
`docs/policy/decisions/repository/minimal-release-automation.md` for future
writer-created annotations. Windows validation and Apply are unaffected.

An existing bounded input patch publication may be recognized in the current
complete writer format or the one previous complete writer format. Recognition
checks target and declaration metadata, refuses missing or conflicting fields,
and performs no write. Confirmation after a new write remains strictly current
format. This preserves immutable historical evidence without reporting it as
newly observed evidence.
