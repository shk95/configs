id: repository/reconstruction-ci
kind: workaround
statement: Run CI on the reconstruction branch against its fixed a886934 base until the new shared history is adopted.
since: 2026-10-06
exit-when: The validated reconstruction endpoint is adopted by dev/master and ordinary protected PR CI is restored.
watch: manual
review-by: 2026-10-20
issue: #515
decision: docs/policy/decisions/repository/minimal-release-automation.md § One-time reconstruction
owner: repository maintainer

The exception adds one push branch and one fixed range, not a general bypass.
For the single cutover it also admits only the two recorded old tips to the
verified bootstrap SHA supplied through the one-time GitHub variable. Other
pushes retain their ordinary before..head range.
Retire its workflow branch and ci-base conditional together after cutover.
