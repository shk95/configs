id: windows/declared-list-has-content
statement: A subset payload declares a list only when it has content to declare.
rationale: docs/architecture.md § Windows domain
enforced-by: fixture windows/tests/WinEnv.Tests.ps1

Declaring a list claims the whole list, and declaring an empty one claims
whatever the host happens to hold there — the one shape in which a payload
absorbs host state silently. No loader refuses it; the suite walks every
subset payload the manifest declares and fails on an empty declared list.
