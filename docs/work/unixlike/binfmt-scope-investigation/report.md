# Report: binfmt registry scope on WSL and OrbStack

kind: report
spec: docs/work/unixlike/binfmt-scope-investigation/spec.md
status: done

## Acceptance

| ID | State | Evidence |
| --- | --- | --- |
| AC1 | verified | Read-only sessions on WSL-NixOS and Ubuntu at 2026-09-20 19:13:42 UTC, repeated at 19:15:39 UTC, from investigation commit 56b5ba7. The command and captured output are below. PID 1 namespace links could not be read as the session user; this is unavailable evidence, not an absent namespace. |
| AC2 | verified | OrbStack 2.2.3 machine observations at 19:13:24 UTC and 19:15:38 UTC, and a native arm64 container at 19:13:55 UTC. Image provenance, exact restricted run command, output and removal check are below. |
| AC3 | verified | Source review on 2026-09-21 KST at 56b5ba7: the Microsoft kernel release matching uname, pinned nixpkgs, systemd release sources and OrbStack architecture documentation. The source table pins revisions. The exact OrbStack kernel source was not available in the inspected public repository; upstream 7.0.14 is explicitly a comparison, not proof of the vendor build. |
| AC4 | verified | All non-timestamp fields in each before/after host capture are byte-identical. No WSL write, sudo, restart, shutdown, mount, activation or registration command was issued. The single labeled disposable container is absent after its --rm run; no image was pulled. The conclusions below retain both existing protections and leave direct-registration effects untested. |

## Conclusion and limits

**Observed:** WSL-NixOS and Ubuntu share user namespace `4026531837` and
binfmt device `0:35`, with the same `WSLInterop` and `python3.14` entries.
Their mount namespaces differ. NixOS sees a read-only bind view; Ubuntu sees
a writable view of the same filesystem. The NixOS protection service is
`loaded`, `active`, `exited`. This supports keeping its existing protection.
It does not repeat the historical shutdown test.

**Observed:** the OrbStack machine and container report the same OrbStack
kernel version, but different user namespaces (`4026532276` versus
`4026531837`). Neither sees a binfmt mount or readable registry entries at
the conventional path. The machine's service is runtime-masked. The
container has zero capabilities and is not a probe of what a privileged
container or the Docker daemon could do. Namespace inode numbers are
compared only within a platform's kernel, never between WSL and OrbStack.

**Source-derived inference:** the reviewed kernels associate a registry with
a user namespace, whereas registration writes operate on the mounted
filesystem's registry. Execution looks upward for the first available
registry when the caller's namespace has none. A fresh local registry can
therefore change inherited handler availability even before adding a rule.
A different mount namespace alone does not provide a separate registry.
A bind-mounted ancestor registry would not become local merely because the
writer belongs to another namespace. [S1, S2]

**Unverified:** a new registration's effects across OrbStack machines or on
containers, the actual namespace ancestry and ancestor registry contents,
Rosetta's registration path in this vendor build, and whether the vendor
kernel changes the upstream behavior. No second OrbStack machine was created
and no x86 executable was run. No direct registration or mount test occurred.
Absence of a visible mount is not proof that execution cannot use a handler.

**Disposition:** keep the current WSL read-only protection and OrbStack
no-registration assertion. WSL has positive evidence of a shared registry;
OrbStack has a different namespace arrangement and an unresolved vendor
source/runtime boundary. The OrbStack rule remains justified by ownership of
emulation, not a demonstrated claim that every machine-local registration
propagates. This work proposes no policy change and does not reopen Order 7.
If an actual registration is needed later, obtain the matching vendor source
and determine namespace ancestry and mount ownership before designing a
separately approved mutation experiment. Ubuntu remains outside such an
experiment unless the maintainer explicitly changes the present constraint.

## Method and provenance

Observation date is 2026-09-21 in Asia/Seoul; raw output uses UTC on
2026-09-20. Repository input was `56b5ba7`, whose first commit established the
spec and pending report before collection. This report is written afterward.
The collector below was streamed over stdin; no script was installed remotely.
The session users were unprivileged and no sudo command was run.

```sh
ssh -o BatchMode=yes -o ConnectTimeout=10 homewslnix sh -s < probe.sh
ssh -o BatchMode=yes -o ConnectTimeout=10 homewsl sh -s < probe.sh
orb -m orbstack sh -s < probe.sh
```

The exact collector follows. A failed `readlink` can print no diagnostic and
no newline: `init_user=self_mnt=...` in the raw captures is that presentation
artifact, not a value of the link. Those PID 1 links are unavailable evidence.
The service link is likewise blank on WSL; `systemctl show` separately
identifies the service state. Missing registry entries only describe the
visible path; no attempt is made to mount a registry to reveal more.

```sh
printf 'utc='; date -u '+%Y-%m-%dT%H:%M:%SZ'
printf 'kernel='; uname -r
printf 'arch='; uname -m
printf 'os='; sed -n 's/^PRETTY_NAME=//p' /etc/os-release
printf 'uid='; id -u
for item in user mnt pid; do
  printf 'self_%s=' "$item"; readlink "/proc/self/ns/$item"
  printf 'init_%s=' "$item"; readlink "/proc/1/ns/$item" 2>&1 || true
done
printf 'uid_map\n'; cat /proc/self/uid_map
printf 'capabilities\n'; sed -n '/^Cap/p' /proc/self/status
printf 'binfmt_mountinfo\n'; awk '$0 ~ / - binfmt_misc / {print}' /proc/self/mountinfo
printf 'registry_begin\n'
if [ -d /proc/sys/fs/binfmt_misc ]; then
  for entry in /proc/sys/fs/binfmt_misc/*; do
    [ -f "$entry" ] || continue
    case "$entry" in */register) continue ;; esac
    printf 'entry=%s\n' "${entry##*/}"
    cat "$entry" 2>&1 || true
  done
else
  printf 'directory_absent\n'
fi
printf 'registry_end\n'
if command -v systemctl >/dev/null 2>&1; then
  systemctl show systemd-binfmt.service --property=LoadState,ActiveState,SubState,UnitFileState,FragmentPath --no-pager 2>&1 || true
  printf 'service_link='; readlink /run/systemd/system/systemd-binfmt.service 2>&1 || true
fi
```

Additional read-only commands: `orb version`, `orb list`, Docker context/image
inventory, `docker --context orbstack info` restricted to kernel/architecture/
security fields, `systemctl --version | head -1` on each host, and on
WSL-NixOS `systemctl show wsl-binfmt-protect.service
--property=LoadState,ActiveState,SubState --no-pager`. `systemd --version`
was first attempted but the executable was not on PATH; `systemctl --version`
provided the version without installing anything. Versions: WSL-NixOS and
OrbStack `261 (261.2)`; Ubuntu `259 (259.5-0ubuntu3.4)`.

### Disposable container

OrbStack version: `2.2.3 (2020300)`, app commit
`c83556b0ef8f1ba9a33abbb194622b6b7a1c0307`. The existing local `postgres:18`
image is arm64, image ID
`sha256:47fcd92135b73f3b3ba0761ef77c305c4263093b999559505afec11a7ed8cbdc`,
repository digest
`postgres@sha256:1957b2ff3137e4ef7f3bc813e74fff50b1e1ffddc85c8b9d6f14ade972be8687`.
It supplied only `/bin/sh` and read utilities: its database entrypoint was
replaced, so no database server was started. No image was pulled. Docker may
provision image-declared anonymous storage; --rm removes the container and
its associated anonymous volumes. No existing volume was attached.

```sh
docker --context orbstack run --name binfmt-scope-probe-20260921   --label configs.investigation=binfmt-scope-20260921 --rm -i   --network none --read-only --cap-drop ALL   --security-opt no-new-privileges --pids-limit 32 --memory 64m   --cpus 0.25 --user 65534:65534 --entrypoint /bin/sh   sha256:47fcd92135b73f3b3ba0761ef77c305c4263093b999559505afec11a7ed8cbdc   -s < probe.sh
docker --context orbstack ps -a   --filter label=configs.investigation=binfmt-scope-20260921   --format '{{.Names}}'
```

The run completed successfully; the filtered container listing afterward
was empty. No host bind mount, daemon socket, host namespace or additional
capability was provided. No existing workload was stopped or restarted.

## Captured observations

### WSL-NixOS before

```text
utc=2026-09-20T19:13:42Z
kernel=6.18.33.2-microsoft-standard-WSL2
arch=x86_64
os="NixOS 26.11 (Zokor)"
uid=2000
self_user=user:[4026531837]
init_user=self_mnt=mnt:[4026532217]
init_mnt=self_pid=pid:[4026532219]
init_pid=uid_map
         0          0 4294967295
capabilities
CapInh:	0000000000000000
CapPrm:	0000000000000000
CapEff:	0000000000000000
CapBnd:	000001ffffffffff
CapAmb:	0000000000000000
binfmt_mountinfo
121 114 0:35 / /proc/sys/fs/binfmt_misc ro,relatime - binfmt_misc binfmt_misc rw
registry_begin
entry=python3.14
enabled
interpreter /usr/bin/python3.14
flags:
offset 0
magic 2b0e0d0a
entry=status
enabled
entry=WSLInterop
enabled
interpreter /init
flags: P
offset 0
magic 4d5a
registry_end
LoadState=not-found
ActiveState=inactive
SubState=dead
FragmentPath=
UnitFileState=
service_link=
```

### Ubuntu before

```text
utc=2026-09-20T19:13:42Z
kernel=6.18.33.2-microsoft-standard-WSL2
arch=x86_64
os="Ubuntu 26.04.1 LTS"
uid=1000
self_user=user:[4026531837]
init_user=self_mnt=mnt:[4026532233]
init_mnt=self_pid=pid:[4026532235]
init_pid=uid_map
         0          0 4294967295
capabilities
CapInh:	0000000000000000
CapPrm:	0000000000000000
CapEff:	0000000000000000
CapBnd:	000001ffffffffff
CapAmb:	0000000000000000
binfmt_mountinfo
212 205 0:35 / /proc/sys/fs/binfmt_misc rw,relatime shared:53 - binfmt_misc binfmt_misc rw
registry_begin
entry=WSLInterop
enabled
interpreter /init
flags: P
offset 0
magic 4d5a
entry=python3.14
enabled
interpreter /usr/bin/python3.14
flags:
offset 0
magic 2b0e0d0a
entry=status
enabled
registry_end
LoadState=loaded
ActiveState=active
SubState=exited
FragmentPath=/usr/lib/systemd/system/systemd-binfmt.service
UnitFileState=static
service_link=
```

### OrbStack machine before

```text
utc=2026-09-20T19:13:24Z
kernel=7.0.14-orbstack-00380-ga7e0a2dc9535
arch=aarch64
os="NixOS 26.11 (Zokor)"
uid=501
self_user=user:[4026532276]
init_user=self_mnt=mnt:[4026532277]
init_mnt=self_pid=pid:[4026532280]
init_pid=uid_map
         0          0 4294967295
capabilities
CapInh:	0000000000000000
CapPrm:	0000000000000000
CapEff:	0000000000000000
CapBnd:	000001ffffffffff
CapAmb:	0000000000000000
binfmt_mountinfo
registry_begin
registry_end
LoadState=masked
ActiveState=inactive
SubState=dead
FragmentPath=/run/systemd/system/systemd-binfmt.service
UnitFileState=masked-runtime
service_link=/dev/null

```

### Disposable container

```text
utc=2026-09-20T19:13:55Z
kernel=7.0.14-orbstack-00380-ga7e0a2dc9535
arch=aarch64
os="Debian GNU/Linux 13 (trixie)"
uid=65534
self_user=user:[4026531837]
init_user=user:[4026531837]
self_mnt=mnt:[4026532606]
init_mnt=mnt:[4026532606]
self_pid=pid:[4026532609]
init_pid=pid:[4026532609]
uid_map
         0          0 4294967295
capabilities
CapInh:	0000000000000000
CapPrm:	0000000000000000
CapEff:	0000000000000000
CapBnd:	0000000000000000
CapAmb:	0000000000000000
binfmt_mountinfo
registry_begin
registry_end

```

### Before/after comparison

| Host | Before UTC | After UTC | Result |
| --- | --- | --- | --- |
| WSL-NixOS | 19:13:42 | 19:15:39 | All fields except utc identical |
| Ubuntu | 19:13:42 | 19:15:39 | All fields except utc identical |
| OrbStack machine | 19:13:24 | 19:15:38 | All fields except utc identical |

The local comparison removed only the first timestamp line and compared the
remaining text byte for byte. Thus registry contents, mount flags, namespace
IDs, UID map, capabilities and observed service state were unchanged in
these snapshots. This is not continuous monitoring or proof that unrelated
workloads had no concurrent changes. SSH generates processes and normal log
activity. No WSL settings, files or running services were deliberately changed.

Captured-file SHA-256 values permit checking the before/after records. The
exact before bytes appear above (the final newline before the fence may be
presentation-only for captures ending with `service_link=`); an after record
is the corresponding before text with only its first timestamp replaced.

| Capture | SHA-256 |
| --- | --- |
| wslnix-before | `dc4fdb56d72f9b488755e59616949d34259e93f2cafad139f2d80a818b534aaa` |
| wslnix-after | `95fc6ee1b8b0ddd172f44690531fb8a8056c0881db7e8fc01b89fe7291051c76` |
| ubuntu-before | `62bcaccd2d85c6a3fb16120a9382e400090132d8fa52b613c659aac886634323` |
| ubuntu-after | `f5981e6df579849999b04d6d33651f78bded2bc21dd9931d7c4176a3d16f3bac` |
| orbstack-before | `3634c86ee60c23175e218c91b67dd9aa673a12743107d6a957e251784b99d850` |
| orbstack-after | `5d64624db8bfc297d9e3bfafe0d0f352864333c9287b62bb8360ed055919cb01` |

## Primary-source review

All sources were read on 2026-09-21 KST. Exact refs and functions make the
reasoning reproducible without trusting a current rolling documentation page.

| ID | Source and applicability | Relevant reading |
| --- | --- | --- |
| S1 | [Microsoft WSL kernel c21a03b](https://github.com/microsoft/WSL2-Linux-Kernel/blob/c21a03b2943d147c280bdf32530d4fe6badfd6bd/fs/binfmt_misc.c), tag `linux-msft-wsl-6.18.33.2`, matching the observed release string | `load_binfmt_misc` (182), `i_binfmt_misc`, `bm_register_write` (768), `bm_fill_super` (934), `bm_get_tree` (1007). Version match, not a binary reproducibility attestation. |
| S2 | [Upstream stable 7.0.14 at 458c607](https://github.com/gregkh/linux/blob/458c6079fc1d41d564c37679c8ace02cd83ee817/fs/binfmt_misc.c) | Same user-namespace registry and ancestor lookup model. Comparison only: does not include OrbStack's vendor changes. |
| S3 | [OrbStack architecture](https://docs.orbstack.dev/architecture) | Shared Linux kernel; engine runs alongside machines; Rosetta supplies x86 emulation on Apple Silicon. It does not specify binfmt registry ownership. |
| S4 | [OrbStack public kernel tree](https://github.com/orbstack/linux-macvirt/tree/308681584a45dba25ebd45499136bfec1b829468) | The inspected `mac-pub` head is Linux 6.3.9 (2023-06-25). API lookup for running suffix `a7e0a2dc9535` returned no commit. Repository description directs requests for newer source to the vendor; no request was sent. This is the exact-source gap, not proof no matching source exists elsewhere. |
| S5 | [Pinned nixpkgs binfmt module](https://github.com/NixOS/nixpkgs/blob/b1b875982b17dabde9b4a37f3e229e74913e6db3/nixos/modules/system/boot/binfmt.nix) | `emulatedSystems` expands into registrations; declarations generate `binfmt.d/nixos.conf`; nonempty registrations add mount/automount/service units and service restart triggers (235–311). |
| S6 | [systemd 261.2 binfmt utility](https://github.com/systemd/systemd/blob/4925d9f07fc697efccd98a93046ff535b8832445/src/shared/binfmt-util.c), [registration](https://github.com/systemd/systemd/blob/4925d9f07fc697efccd98a93046ff535b8832445/src/binfmt/binfmt.c), [shutdown](https://github.com/systemd/systemd/blob/4925d9f07fc697efccd98a93046ff535b8832445/src/shutdown/shutdown.c) | Registration writes the mounted `register` file. Shutdown separately invokes `disable_binfmt`, which checks filesystem type and writability before flushing via `status`. Upstream version matches the NixOS systemctl version; not a patch-by-patch audit of the installed package. |
| S7 | [systemd 259.5 utility](https://github.com/systemd/systemd/blob/b3d8fc43e9cb531d958c17ef2cd93b374bc14e8a/src/shared/binfmt-util.c) | The same filesystem/writability guard exists. Ubuntu's downstream package suffix is observed but its complete patch set was not audited. |

The source review distinguishes two operations. A write targets the registry
owned by the filesystem's superblock, while execution chooses the caller's
namespace registry or an ancestor's first existing registry. It does not merge
all ancestors' lists after a local lookup miss. Therefore the WSL shared
filesystem observations matter more than equal UID maps alone, and a fresh
machine-local mount could affect inherited emulation even if writes never
reach another machine. These are inferences from S1/S2, not new experiments.

At investigation commit 56b5ba7, `unixlike/modules/wsl.nix` lines 142–156
make the existing WSL mount private and bind-remount only that view read-only;
`unixlike/modules/host/orbstack.nix` lines 113–115 reject both emulatedSystems
and explicit registrations. A manually issued registry write bypasses a Nix
assertion; a service mask alone is not a general write-access boundary. These
are configuration/source observations, not a test of privileged writes.

## Evidence lanes

- Evaluation: no Nix evaluation was performed as investigation evidence;
  subsequent repository CI is validation of the documentation change.
- Build: not run; no package or configuration implementation changed.
- Native runtime: the read-only observations and disposable container run above.
- Activation / Apply: not run.
- Review: source mapping, before/after comparison and scoped conclusions above.

The existing Order 7 evidence and acceptance criteria remain unchanged.
