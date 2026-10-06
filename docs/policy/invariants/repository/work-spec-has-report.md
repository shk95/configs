id: repository/work-spec-has-report
statement: A tracked spec is paired with a report answering every criterion; report state follows those answers, criteria change only by dated amendment, and only a valid terminal pair may be archived together after fixed remote preservation and active-reference review.
rationale: docs/policy/architecture.md § Repository governance plane
enforced-by: tool tool/version-control/work
enforced-by: fixture tool/version-control/test
enforced-by: manual the maintainer verifies the fixed remote original and absence of active references before terminal-pair archival
owner: repository maintainer
decision: docs/policy/decisions/repository/work-planned-and-verified-in-documents.md § Work is planned and verified in documents, and a branch is one increment

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

A valid terminal pair may be removed together after maintainer review of its
fixed remote preservation and active references. Pending or malformed acceptance
cannot disappear through archival. The original spec/report remains historical.
