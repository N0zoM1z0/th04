# TH04/TH05 ZUN-modified MASTER provenance (v493)

## Question

v492 identifies a normal TASM/TLINK mechanism that reproduces the target
file-backed MASTER BGM BSS surface, but v430/v491 extract the pinned generic
`masters.lib:b_data.OBJ` and show that its `0xC6` `_BSS` contribution has no
LEDATA/LIDATA. That generic object is useful independent evidence only if it is
representative of the MASTER build ZUN actually linked.

v493 tests that assumption against other MASTER routines whose historical bug
is visible directly in code bytes.

## Generic archive objects

The probe freshly extracts two members from the pinned generic
`_reference/ReC98/bin/masters.lib` (archive SHA-256
`6be41dbcfcf4504977165ccc44443525a29a01f85a1580e6ad0c620bf802faf6`):

| Member | Public | Object SHA-256 | Generic instruction |
| --- | --- | --- | --- |
| `grpgjput` | `GRAPH_GAIJI_PUTC` | `fa85d77b90daea85910f921fcf465415b300db41846f9e5a67fade40de2a529d` | local `+0x10`: `81 D5 80 56` = `ADC BP,5680h` |
| `grpgputs` | `GRAPH_GAIJI_PUTS` | `9643b6a564c37cfcedcc72797dce7a1b7400f42aaf07272bf1074807092c7e89` | local `+0x4E`: `15 80 56` = `ADC AX,5680h` |

These are the known generic MASTER gaiji carry bug.

## Independent target comparison

The same function-local sites are checked in four independently restored target
MZs, using only MAP public addresses to locate the routines:

- TH04 OP;
- TH04 MAINE;
- TH05 OP;
- TH05 MAINE.

All four targets contain the corrected instructions:

- `GRAPH_GAIJI_PUTC +0x10`: `81 C5 80 56` = `ADD BP,5680h`;
- `GRAPH_GAIJI_PUTS +0x4F`: `05 80 56` = `ADD AX,5680h`.

Therefore the TH04/TH05 binaries **cannot have linked these routines verbatim
from the pinned generic archive**. A ZUN-modified MASTER source/object set is a
target-attested build fact, not merely a source-tree convention.

## Consequence for the BGM T surface

This changes how v430/v491 should be interpreted. Their generic
`b_data.OBJ` remains valuable evidence:

- its layout and public offsets independently attest the `0xC6` BGM BSS shape;
- its generic `_BSS` contribution contains no LEDATA/LIDATA;
- restoring that exact generic member boundary under current TLINK does not
  change TH04 file extent.

But it is **not evidence that ZUN's modified MASTER build used the same
`b_data.OBJ` bytes or initialization records**. Since other MASTER objects are
provably different between the generic archive and the ZUN-linked TH04/TH05
binaries, the generic no-LEDATA result cannot by itself disprove v492's
file-backed-BGM mechanism.

This still does not prove that ZUN's historical `b_data` explicitly initialized
its BSS to zero. The exact modified object or source remains unavailable. v492
therefore remains a corroborated mechanism/provenance frontier rather than an
authored-source promotion.

Private receipt SHA-256:
`0dfb1d4fa82f94031493d9871999705818b497cc946b00eea942fe359ecb633e`.
