# Capture saves explicit host originals

date: 2026-09-30
scope: windows
status: accepted
issue: #427
source: docs/work/windows/host-consumer-contract/spec.md

Capture consumes the version1 host environment and explicit selected/enabled
unit connections. It previews supported observed settings and saves originals
only with explicit Save. It changes neither provider source nor generated bundles,
app configuration, feature selection or runtime Apply state. Publication belongs
to the host repository; capture performs no Git branch/commit/push/PR/auto-merge
operation. The provider capture/publication behavior is retired, and unsupported
legacy publishing parameters refuse before any mutation.

The currently chosen payload defines the owned projection. JsonSubset captures
its object keys and whole arrays, retaining no undeclared object keys; a later
host-owned capture uses its own connected payload rather than new provider
defaults. Missing keys and incompatible shapes refuse without inventing deletion.
Terminal generated profiles and external PowerShell blocks remain excluded;
retired private WSL/layout units and runtime files do not become capture units.
Captured settings are complete host sources, never automatically merged with
provider defaults. No last-applied snapshot is required to infer UI deltas.

All requested units prepare before Save. Identity checks protect pending source,
original, app-target and prospective destination writes. An existing document
is replaced atomically. A first document is saved before its explicit connection;
connection failure reports an inert document to inspect on explicit retry.
Conflicting unconnected content is refused. Completion is reported per unit;
there is no multi-file atomicity or automatic rollback service. Regeneration is
required after originals change. Save is independent of Apply and authorizes
neither actual host deployment nor publication.
