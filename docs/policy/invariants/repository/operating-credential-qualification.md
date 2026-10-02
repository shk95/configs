id: repository/operating-credential-qualification
statement: Operating credential qualification independently binds the actual trusted source, actor, workflow, sole job and selected repository, makes only bounded read requests, emits no private data, and cannot certify mutation permissions or enable operation.
rationale: AGENTS.md § Rules that are expensive to break
enforced-by: schema tool/version-control/release-credential-check.py
enforced-by: fixture tool/version-control/test-release-credential-check
owner: repository maintainer
decision: docs/policy/decisions/repository/authenticated-release-transport.md § Read-only credential qualification

Source fixtures exercise public/private identity, runtime and API disagreement,
changed attempt/source, incomplete jobs, changed protection, foreign endpoints,
redirects, duplicate/oversize responses, unexpected secret-metadata access and
private-free refusals. Actual Environment/ref isolation and token access are
separate affected-dispatch observations after normal source promotion.
