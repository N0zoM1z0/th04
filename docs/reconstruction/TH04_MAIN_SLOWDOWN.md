# TH04 `MAIN.EXE`: `slowdown_frame_delay`

## Current state

- Unit: `th04-main-slowdown-frame-delay`
- Ledger state: `exact`
- Origin: authored
- Boundary: reviewed
- Maintained source: `src/main/slowdown.cpp`
- Exact promotion: accepted by the checked-in two-cold-build replay

The source candidate is identical to the bounded implementation at pinned
ReC98 revision `b6ba5b0a529edbb31efdf8c0e939263804f8ee47`. Upstream identity is only
candidate provenance; the target and compiler observations below are kept
separate.

## Target observation

The artifact is the hash-attested Japanese `MAIN.EXE`
(`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`).
Its provenance remains `candidate-local-attested`.

| Coordinate | Value |
| --- | --- |
| Target file extent | `0xC2F2..0xC30B` |
| MZ load-module extent | `0xAAF2..0xAB0B` |
| Link segment | `SLOWDOWN_TEXT` |
| Link/Ghidra address | `1AAF:0002` |
| Size | 26 bytes (`0x1A`) |
| Slice SHA-256 | `c5a69d9d1869b865085b77c768747c2962bdbea165c7d1d21cc3d16320e59f54` |

After `python3 scripts/ghidra.py th04-main check`, a read-only bounded query
observed one `__cdecl16near` function covering exactly these 26 bytes, ending
in `RET`. The prior function ends at linear `0x1AAEA`, the next function begins
at `0x1AB0C`, and one near call reaches this entry from `0x1AC64`. No MZ
relocation site overlaps the extent.

```text
1AAF:0002  PUSH BP
1AAF:0003  MOV  BP,SP
1AAF:0005  MOV  AX,[2AB2]
1AAF:0008  CMP  AX,[5390]
1AAF:000C  JC   1AAF:0005
1AAF:000E  MOV  word ptr [2AB2],0
1AAF:0014  MOV  word ptr [5390],1
1AAF:001A  POP  BP
1AAF:001B  RET
```

The target accesses DS offsets `0x2AB2` and `0x5390`. Separate header evidence
identifies the candidate declarations as volatile VSync count and slowdown
factor respectively; the source therefore waits for the requested VSync count
and resets both values.

## Compiler observation

The existing pinned cold ReC98 build uses Turbo C++ 4.0J in the large model
with the repository-attested toolchain. The maintained source has SHA-256
`eb73a8be40de3a8d666bea1df85c92b742e3574fbf99c54fe6ca18572a7b17ff`,
identical to the source compiled by that cold build.

Its `slowdown.obj` is one valid 542-byte Intel OMF module with 24 records,
producer `TC86 Borland C++ 4.02`, one `LEDATA`, one `FIXUPP`, one `THEADR`, and
one `MODEND`. The linker map assigns the complete 26-byte module to
`SLOWDOWN_TEXT` at `1AAF:0002`; the resulting candidate load-module slice has
the same SHA-256 as the target slice and zero differing bytes.

That initial compiler observation did not by itself promote the unit. The
checked-in replay now overlays the maintained source into two isolated pinned
scaffolds and requires target identity, toolchain identity, valid deterministic
OMF, exact TLINK placement, relocation agreement, and raw zero difference over
the complete extent. Both cold builds pass, so the current ledger state is
`exact`. This bounded result does not make the whole executable exact or the
repository independently buildable.
