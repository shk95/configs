id: unixlike/local-consumer-development
statement: Consumer development keeps real identities and connection state local, tests explicit source pairs without changing adoption pins, and accepts promotion evidence only for the tested content and closure.
rationale: AGENTS.md § Domain boundaries
enforced-by: schema unixlike/tool/dev-host/main.py
enforced-by: fixture unixlike/tool/checks/dev_host_test.py
enforced-by: fixture unixlike/tool/checks/dev_host_integration_test.py

The provider contains a generic consumer adapter protocol, synthetic fixtures
and developer documentation. Consumer paths, selected identities, publication
recipes and application receipts belong to the selected checkout's private Git
metadata. Provider checks need no private consumer.

Development snapshots include tracked and nonignored new source files, exclude
maintainer notes and ignored local data, and reject symlinks and submodules.
The consumer owns native target checks, activation and release adoption.

Info reads existing coordinated records without initializing local state or
invoking a consumer adapter. Record creation belongs to explicit mutators;
inspection does not qualify native/runtime or promotion evidence.
Publication delegates to explicitly configured repository procedures and checks
immutable release content and the final pinned closure before final activation.
