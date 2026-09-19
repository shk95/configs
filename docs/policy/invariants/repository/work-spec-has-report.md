id: repository/work-spec-has-report
statement: A spec is tracked together with a report that answers each of its acceptance criteria, the report's state follows from those answers, and a criterion is never removed or rewritten after the work began except by a dated amendment that names it.
rationale: docs/policy/architecture.md § Repository governance plane
enforced-by: tool tool/version-control/work
enforced-by: fixture tool/version-control/test

A plan kept where it can be edited after the fact cannot be held to account,
and a spec with no report sets a bar nobody is asked to meet. The pair is
created in one commit, so no commit holds a spec without the place its
evidence goes, and the report ends as done, abandoned or superseded rather
than by being forgotten.

The amendment rule is what makes the criteria a bar rather than a
description: it is read between two commits, and a criterion that stood
beside a report at the first must be present, word for word and lane for
lane, at the second, unless the spec gained an `Amended` paragraph naming it.
Adding a criterion needs no amendment. A spec that has no report yet is not
held to anything, which is the first commit of the pair and nothing else.

Accepted limits, which are the reviewer's: whether the evidence in a verified
row is evidence, whether a lane named as required was the right one, and
whether an amendment's reason is a reason. The check reads that each exists.
