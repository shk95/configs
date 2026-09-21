id: unixlike/headless-key-only
statement: A headless NixOS host that boots itself admits its ssh port and no other, its ssh daemon accepts a key and nothing else and never a root login, and neither a password nor an authorized key for it is tracked.
rationale: docs/policy/architecture.md § Unix-like domain
enforced-by: schema unixlike/modules/sshd.nix
enforced-by: schema unixlike/modules/firewall.nix
enforced-by: schema unixlike/modules/account.nix
enforced-by: fixture unixlike/tool/checks/flake-test
enforced-by: fixture unixlike/modules/flake/headless-runtime-test.nix

A headless host is reached over the network or not at all, so what it admits
is the whole of its exposure. The class that makes such a host reachable
asserts its own shape: the firewall is on and opens exactly what the ssh
daemon listens on, on every interface; the daemon refuses a password, a
keyboard-interactive login and root; the account carries no password field
and no account carries an authorized key, because both are host state the
installing step writes; and sudo asks for the password the host holds, since
a passwordless wheel would make any accepted key equal to root. A service
added later that opens its own port is refused until this rule is changed on
purpose.

The NixOS-WSL host is not of this class. Its port and its account's UID are
facts about WSL's shared network and cgroups, it has no firewall of its own
to hold, and its daemon is declared beside this one with the same settings.
The fixture evaluates the real host of the class for each property and
extends it with each violation in turn.

The runtime fixture boots the headless class on x86_64 Linux. It writes a
disposable password and key after boot, reaches sshd through a separate
network namespace, and proves that a key reaches the account while a password
and a root login do not, sudo still asks for a password, and a listening port
other than ssh remains unreachable through the firewall.
