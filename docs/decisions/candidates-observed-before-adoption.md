# A rule or a deletion is observed before it is adopted

date: 2026-09-05
scope: repository
status: accepted
reopen-when: a candidate is cited as authority by any document, tool or agent, or the observation stage is bypassed twice for text that later rotted

On 2026-09-05 one piece of work produced twelve lessons, two independent
audits that disagreed on a third of them, and two pieces of tracked prose
that were false within a day of being written: a claim that a script leaked
an exit status, which reached a commit message and an issue before it was
withdrawn, and a registry count in `docs/status.md` that went stale with the
next entry. A sentence added to a policy document without a check behind it
rots, and a deletion is as easy to get wrong as an addition.

New prose and deletions therefore pass through an observation stage first:
`docs/candidates/`, one file per candidate, tracked so that every clone and
every session sees the same observations. A candidate records what was met,
where, and how often, with the criterion that would promote it and the date
that drops it. It is an observation and never a source of authority; nothing
cites it, and an agent does not follow one as a rule. Two things do not
wait: a change that is fatal on a host and invisible to every gate, and the
correction of tracked text that is false today.

Rejected:

- Recording candidates in the untracked session ledger. Invisible to the
  Windows clone and to any other session, so the same mistake is made
  again elsewhere.
- Recording them as GitHub issues. Issues are the planning surface for work
  that has been decided; a candidate has not been.
- Adding the text straight to the documents. That is the failure the stage
  prevents.

What it costs: a fourth place to look before writing a rule, an index to
keep by hand, and no checker, deliberately, because a checker on the
buffer would be the haste the buffer exists to absorb.
