# Separate operator commands from automation tools
kind: spec
date: 2026-09-26
scope: repository
status: approved
review-by: 2026-10-26
issue: #403

The repository currently documents individual implementation scripts as operator commands. Hooks and CI also call the Windows operator entry point. Give people a deliberate interface while automation depends on internal commands owned by each scope.

## Decisions

The repository scope gets one operator entry point with an explicit command table. It forwards arguments and exit status to existing implementation scripts and does not duplicate their policy. Hooks and CI keep calling internal scripts. Domain entry points remain inside their domains; the repository entry point does not dispatch domain deployment.

An operational dependency is a hook, CI job, or implementation calling a command to do work. A test calling an entry point to verify its public contract is not an operational dependency. An agent acting for a person may use the operator entry point. A person debugging an internal command does not make it public.

Rejected: moving every executable into new `system` directories. Existing domain `tool/` trees already hold implementations, and a physical move would change many invariant locators without improving the interface. Rejected: combining Windows and Unix-like host operations in the repository entry point; each domain must remain independently operable.

## Increments

1. Repository fixtures and policy checks verify the repository operator entry point and its routing.
2. Affected dispatch and review verify that Windows automation calls internal commands without weakening their execution contract, while the Windows scope supplies native evidence.

## Acceptance

| ID | Criterion | Required lanes |
| --- | --- | --- |
| AC1 | A discoverable repository operator entry point exposes the intended human commands, preserves their arguments and exit status, and refuses unknown commands without executing a target. | fixtures, policy checks |
| AC2 | Repository guidance and the agent workflow use the operator entry point for human operations, while hooks and CI use internal commands; scope ownership and check selection cover the new file. | fixtures, review, affected dispatch |
| AC3 | Windows CI and pre-push no longer depend operationally on the Windows operator entry point, and their failure and unavailable statuses retain their meaning. | fixtures, affected dispatch, review |
