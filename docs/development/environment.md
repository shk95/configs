# Prepare a clone

## Prepare a clone

`tool/configs help` lists repository operations intended for a person or an
agent acting for one. The command forwards to the implementation under
`tool/`; hooks and CI invoke those implementations directly. Windows host
commands remain under `windows/win-env.ps1`, and Unix-like host commands use
the `Justfile`.

```sh
tool/configs setup
tool/configs setup --fix
tool/configs doctor
```

`tool/configs setup` changes only the clone-local hooks setting and only with `--fix`.
`tool/configs doctor` is read-only. `tool/configs doctor` also prints a one-line
summary of the outcomes the hooks have recorded on this clone;
`tool/configs hook-evidence` prints the full count. Pass `unixlike`,
`windows`, `common`, or `repository` to check only that scope; omit the
scope for a complete host inventory. A missing foreign-platform capability
does not block scoped work.
The summary separates missing candidate prerequisites from a completed host
inventory. Missing gitleaks still allows source preparation and is reported
as unavailable for local candidate verification. An inventory does not execute
the selected checks, verify hosted proof or grant deployment permission.
Use setup for clone preparation and doctor before relying on an unverified
capability or after an environment change. These are not a startup sequence
to repeat for every task.

## Prerequisites by operation

| Operation | Prerequisites and preparation |
| --- | --- |
| Repository tools and local hooks | Git, a POSIX shell with standard text utilities, and an executable Python 3. Hook setup is clone-local and explicit. |
| Local committed-candidate verification | The above, gitleaks with its `git` command, and prerequisites of the selected domain suites. Missing tooling is not a successful verification. |
| Hosted proof or requested GitHub operations | Authenticated `gh` plus the exact source/run required by the operation. Local editing does not require it. |
| Unix-like checks | Nix with nix-command/flakes enabled. Checks obtain parsers from the locked input; `nix develop ./unixlike` or direnv supplies optional editing tools. The devShell does not provision all repository-operation prerequisites. |
| Native Windows checks | Native PowerShell and the domain's declared toolchain. Use the explicit installer `windows/win-env.ps1 setup-dev` when requested, then the Windows validate/test/check verbs. No Nix is required. |

Choose the [development verification route](verification.md#development-feedback-before-a-commit)
for the source state being checked. A foreign-host capability warning can
limit the evidence available here without blocking preparation in that scope.
