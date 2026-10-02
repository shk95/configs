# Font install states

date: 2026-08-30
scope: windows
status: accepted
source: 9f1e8ce:docs/status.md § Font install states

The font check answers one question — may Apply write here — and it needs
four answers rather than three. `Installed`, `RegistrationRepairable` and
`Missing` left one shape undescribed: a host holding some of the faces the
manifest lists, each of them the manifest's own file, valid, and registered
to its own path. That is what every host that installed D2Koding before the
manifest's file list grew from two faces to four looks like, and the model
called it `Conflict`, so `-Check` reported `partial/conflicting installation`
and Apply refused with `automatic overwrite is disabled` on a host with
nothing wrong on it.

`Incomplete` names that shape: no machine-wide registration of the family,
no present file whose hash is not the pinned one, no registration under one
of the manifest's own names pointing at another path, at least one artifact
already present, and at least one listed face not yet fully installed. `-Check`
reports it as its own drift line naming how many of the faces are installed,
and Apply treats it like `Missing` — the same installer, which fetches
the pinned archive, leaves a face this host already holds byte for byte
alone rather than copying over a file Windows holds open, and writes and
registers the rest. Post-apply validation still expects `Installed`.

`Conflict` keeps everything else and its refusal is unchanged: a present
file whose bytes are not the pinned ones, a registration under a manifest
name that points somewhere else, a machine-wide install of the same family,
and a fully registered font DirectWrite still cannot resolve. There is no
`-Force` for fonts, deliberately. Nothing on this path overwrites a file
this repository did not put there.

That last sentence is now true of registrations too. `RegistrationRepairable`
used to be decided from the file count alone, so a host holding every listed
file whose registrations were valid except for one pointing elsewhere was read
as a repair and Apply rewrote that value. A registration naming another path is
not a missing registration, and repairing it means overwriting something this
repository did not write, so it now leaves that state the same way it leaves
`Incomplete`, and both of the states that write are bounded by the same rule.

`Get-WinEnvFontStatus` decides the state from three injected host observations
— the per-user font directory, the two registry keys, and the DirectWrite
family probe — for the same reason package detection injects its two: the
states a font can be in outnumber the ones any one host can be put into on
request, and the one that caused this regression is among them. The seam is
what gives every state a fixture; it reads no registry the tests do not hand it.
