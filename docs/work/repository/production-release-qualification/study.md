# Unselected source-bound bootstrap proposal
kind: study
date: 2026-10-01
scope: repository
status: open

This proposal inventories source 0b474aac4e7e7546b38c1813550a7f2cda799a43;
it does not select that source for release. Initial independent versions remain
unixlike-v1.0.0 and windows-v1.0.0. Maintainer review, actual native evidence,
separate source-bound bootstrap records and authenticated operating inputs are
still required. Calendar releases remain immutable with no implicit conversion.

The qualification rules enumerate actual public paths and 17 source-bound contract
surfaces. The rules revision is c9cc4c441331e574aeafcd1bd2c6367e4e2a242a,
committed separately from this proposal. The official read-only command accepted
this inventory and reported selected=false, production_certification=false and
calendar_conversion=false. There are no synthetic verification receipts.
No synthetic receipt is included in this proposal.

Operating record repository, actors, refs, workflow, secret connection,
Environment and control/bootstrap identities remain UNRESOLVED. The user chose
implementation and verification because no private operating repository exists.
Actual manual and scheduled operating proof remains pending in the parent report.

## Pinned public surfaces

| Surface | Git blob |
| --- | --- |
| unixlike-api | `737346f22b95753123b83890a4e8a169617c786f` |
| unixlike-capture-adapter | `61a3aefad3f2e10ddaa9137254bbd196dbfb0ed6` |
| unixlike-capture-consumer | `9edcfc2641dc6a55f6c83297c96644cd49700de4` |
| unixlike-capture-engine | `f2a71e2cfa8a18f1cff390664f368935982834ac` |
| unixlike-capture-schema | `f629aa430cfb395451748c3505d454216e65107c` |
| unixlike-capture-units | `b497d72e3ec894e48a63fff54273e3c586efe177` |
| unixlike-constructors | `c298e319a20103afeec3d68a9c43969c1a368ebb` |
| unixlike-import-classes | `f1aba07e2f0fc0fea6898af6b792861eb6906cde` |
| unixlike-inspection | `3bf25d061fa7444217c71d55d4f7b06d2af6b043` |
| unixlike-lock | `2bb89f9659d9b46ab8c8c5077457cb001030947a` |
| unixlike-readiness | `25e0f4b5009133ac87b10d56af6c017b538e8781` |
| windows-capture | `ba4d064c1371bd5a04f4d614c36020b428e63aa0` |
| windows-catalogue | `5d825b581e5a4e4fdb6776f5c7ff252e259c0af5` |
| windows-entry | `80b0db3d1882479c919eced70a1851b64d5fd56c` |
| windows-formats | `08fb54297a7238976ea8f4ff474073504466c019` |
| windows-generation | `b471a9ba058e32eab4de4cd62c0d89c621855b6c` |
| windows-runtime | `eceed7d9a0000cd07a35cc443819f1bc51e03178` |

Reproduce with `tool/configs release-preview --production --bootstrap-proposal`
using the source above, master 2542d77c09823417c62c179f4c69d9f7f5ba51ae
and the separately committed rules revision. The JSON also reports exact tool,
engine, classifier and rule digests and all representative obligations.
