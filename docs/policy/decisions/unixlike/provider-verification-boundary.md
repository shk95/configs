# Provider verification follows the public composition boundary

date: 2026-10-13
scope: unixlike
status: accepted
reopen-when: A provider-owned behavior cannot be adequately verified without realizing a selected artifact.

`configs` owns typed composition APIs and their declarative environment
contributions. The synthetic outputs witness supported API compositions;
they are not deployable machines supplied by the provider. The public
`configs-host-template` illustrates consumer ownership through the public API;
its source and pins are verified in that repository, not fetched by provider CI.

Routine provider verification checks input acceptance and refusal, defaults,
consumer native-module overrides, supported constructor/system/environment selections forced to
toplevel derivations independently of example output names, public contract data, an independently locked synthetic
consumer, payload validity and provider-owned scripts. Internal composition and
module-order checks remain because they protect the provider implementation.

Host closure realization, boot, graphical sessions and platform adoption belong
to the consumer. They are removed from the provider's automatic verification.
A consumer may build its configuration to reproduce a provider bug; this is
not a provider release prerequisite. Provider-owned source patches
still require realization of their focused positive and negative checks: they
change source themselves and cannot rely on evaluation to prove applicability.

The verification suite has one implementation entry point. CI and local checks
invoke it rather than assembling different fixture lists. Payload validators and lint tooling resolve
Nix tools from the provider's locked input so their result does not depend on a
clone's registry. This replaces the native synthetic-host build requirement in
`docs/policy/decisions/repository/ci-evidence-without-hosted-runners.md`.

Native parser checks realize only generated configuration sources and include
parser-specific malformed-input refusals. Niri repeat-delay rendering is also
covered. The graphical files are checked on matching Linux systems, not by a
host closure or session. A Darwin-only run must name that Linux evidence as
unavailable. Example-output traversal and the independent finite API matrix
have different obligations: examples must remain evaluable, and deleting an
example must not silently remove support coverage.
