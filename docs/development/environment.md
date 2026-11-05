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
Use setup for clone preparation and doctor before relying on an unverified
capability or after an environment change. These are not a startup sequence
to repeat for every task.
