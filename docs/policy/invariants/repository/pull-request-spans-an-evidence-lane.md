id: repository/pull-request-spans-an-evidence-lane
statement: A change that belongs to a spec verifies at least one acceptance criterion in its required lanes and carries the report rows, status and report end that verification produces, or states where its evidence was produced outside the repository.
rationale: AGENTS.md § Governance design
enforced-by: manual the reviewer confirms that the pull request verifies a criterion of its spec and carries its own bookkeeping, or that its body names the host or session outside the repository where the evidence it records was produced
owner: repository maintainer
decision: docs/policy/decisions/repository/work-planned-and-verified-in-documents.md § Work is planned and verified in documents, and a branch is one increment

A spec's increments are cut at its evidence lanes and scopes, not at its
steps. Measured on 2026-09-20, about twelve of forty merged pull requests
held only a report row, a report's end, a status sentence or a roadmap row,
each following evidence that another pull request had produced minutes
earlier; the record's paragraph of that date has the figures.

No tool holds this. The legitimate bookkeeping-only change — a report ended
after the maintainer installed a host by hand, a roadmap row that records an
end — has the same path list as the one this rule removes, so a path check
would refuse both or neither. A change with no spec is outside the
statement: its evidence is its pull request's body.
