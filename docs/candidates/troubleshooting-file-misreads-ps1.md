# Index `file` reporting a PowerShell script as "Windows setup INFormation"

kind: addition
scope: repository
first-observed: 2026-09-05
target: docs/troubleshooting.md § The agent sandbox, beside the CRLF entry
promote-when: one more session is misled by it after this record
drop-when: no new occurrence by 2027-03-05

## Observation

`file windows/tools/setup-dev.ps1` answers "Windows setup INFormation" from the file's content, so a line-ending check that trusts `file` reports nothing about CRLF. The bytes are CRLF as `.gitattributes` requires; `tail -c2 <f> | od -c` shows `\r \n`.

## Evidence

- Observed while verifying CRLF on the entry-point branch; `.gitattributes` line `*.ps1 text eol=crlf`.

## Occurrences

- 2026-09-05: one session.
