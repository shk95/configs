id: repository/pull-request-spans-an-evidence-lane
statement: A change that belongs to a spec verifies at least one acceptance criterion in its required lanes and carries the report rows, status and report end that verification produces, or states where its evidence was produced outside the repository.
rationale: AGENTS.md § Governance design
enforced-by: manual the reviewer confirms a coherent source outcome carries its produced evidence and result records, or names their external source without requiring a separate bookkeeping delivery
owner: repository maintainer
decision: docs/policy/decisions/repository/local-development-workflow.md § Decision

A coherent outcome may span several evidence lanes. Evidence accompanies the
result that produced it; concise local records follow the small-change
procedure. External runtime or remote check evidence is referenced where it
was produced rather than mirrored in a separate bookkeeping delivery.

This is manual because a path-only check cannot distinguish unsupported
bookkeeping from a legitimate record of evidence produced outside the
repository. Historical measurements remain in the decision history rather
than the current invariant's operating guidance.
