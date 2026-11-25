# SDKMAN initialization is user-owned

date: 2026-11-25
scope: unixlike
status: accepted
supersedes: docs/policy/decisions/unixlike/sdkman-adopted-not-owned.md

The user owns SDKMAN installation and shell initialization. The provider
removes the Zsh hook and the assertions that required it to run after every
declared PATH entry and refused consumer-declared JDK packages.
Gradle remains provider-supplied through Nix. Existing SDKMAN installations
and their JDKs stay under the user's control.
