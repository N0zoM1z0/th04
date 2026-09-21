# TH04 OP/MAINE master object boundaries v397

## Observation

Four remaining decoded-payload CODE mismatches have the same shape:

| Artifact | Payload byte | Candidate | Target | Next public |
|---|---:|---:|---:|---|
| OP | `0x2D59` | `90` | `00` | `SUPER_PUT` |
| OP | `0x34AF` | `90` | `00` | `_BGM_BELL_ORG` |
| MAINE | `0x0CBD` | `90` | `00` | `GET_MACHINE_98` |
| MAINE | `0x2D11` | `90` | `00` | `_BGM_BELL_ORG` |

All four publics come from `libs/master.lib/*.asm`. Their entry macro is
`public name; EVEN; name proc`.

In the current ReC98 reconstruction these source modules are included into one
large TASM translation unit. At the four odd entry positions, TASM sees the
preceding instruction context and emits `90`.

## Pinned assembler/linker controls

A same-object control containing an odd `RET`, a close/reopen of
`_TEXT`, and then `EVEN` still assembles as
`C3 90 C3`. Merely reopening the segment therefore cannot explain target
padding.

A two-object control instead emits one odd byte in the first word-aligned
object and one byte in the second. TLINK 6.10 links:

- CODE: `C3 00 C3`
- DATA: `11 00 22`

Thus a real object contribution boundary naturally produces the target
`00` without explicitly requesting a target fill byte.

## Real master.lib modules

The affected reconstructed sources can be assembled as independent TH04
large-model TASM objects once their ordinary cross-module symbols are declared:

- `SUPER_PUT`
- `GET_MACHINE_98`
- `_BGM_BELL_ORG`

All three produce valid OMF.

The repository also contains `bin/masters.lib`. TLIB shows corresponding
historical modules `superput`, `getmac98`, and `b_b_org`,
confirming real module granularity. The shipped archive is **not** a drop-in
TH04 OP/MAINE candidate: its extracted objects use a different memory-model
ABI than the large-model game source, so v397 does not link it into the games.

Private receipt SHA-256:
`2e976b1b7e5d3b68ca30b27594a34279cf1ea068e49eb4046720b92b05d744d9`.

## Conclusion

The four CODE bytes are now explained by physical producer topology rather than
a desired padding value. The next candidate should restore large-model
master-module object boundaries while preserving module order.

This does not close OP or MAINE. Their DATA alignment bytes, ordered relocation
tables, MZ length/minalloc/trailing topology, and shared `snd_load`
`89 C3` residual remain independent gates.

## v400 linked object-boundary replay

v400 tests the v397 producer-topology hypothesis against the same hash-pinned
v214 ReC98-overlay candidate used by the v218 decoded-payload frontier. The
replay does not add an explicit `db 0`, patch OMF bytes, or copy any target
byte. It changes only `_TEXT` translation-unit boundaries plus the symbol
visibility needed to link the existing large-model master.lib source across
those OMF objects.

`scripts/probes/probe_th04_master_object_split.py` first requires the frozen
baseline identities, including OP candidate SHA-256
`cb9b1c6cbd6b2c7bad6763fabd106c3cf451b1c20efef0f1fcfd3e3a47c0cdaa`
and MAINE candidate SHA-256
`7e6b78861613cdd06d72e2f8584268444642b31abcc35d686c0ed1f4cc668f70`.
It verifies the pinned TASM32/TLINK identities, reproduces the old v218
mismatch vectors, copies the source tree twice, applies the object split to both
copies, rebuilds, and reruns the DIET payload Oracle.

For OP, `_TEXT` becomes three linked contributions: the original head object,
a middle object beginning at `SUPER_PUT`, and a tail object beginning at
`_BGM_BELL_ORG`. The decoded-payload mismatch count falls from 7 to 5. Target
bytes `00` at `0x2D59` and `0x34AF` are now produced naturally by TLINK's
word-aligned object contribution boundary. Payload size remains `0x10DA4`, the
804-site relocation multiset remains target-equal, and both cold copies produce
candidate SHA-256
`7d3e9887f633474278e89023d315858394b12527860ca5cbc2ecdbbd082bb60d`.

For MAINE, `_TEXT` likewise becomes a head object, a middle object beginning at
`GET_MACHINE_98`, and a tail object beginning at `_BGM_BELL_ORG`; DATA/BSS stay
with the head object. Splitting exposed a real ABI detail hidden by the old
monolith: same-segment FAR calls emitted through `nopcall` must retain their
`PUSH CS; CALL near` lowering across OMF objects. Preserving that lowering and
the exact external-symbol spelling (`gdc_outpw`) restores the original payload
length and relocation topology. The mismatch count falls from 5 to 3, removing
`0x0CBD` and `0x2D11`; payload size remains `0xF3CE`, the 559-site relocation
multiset remains target-equal, and both copies produce candidate SHA-256
`98e1a1c270837d4c154fb9cacc3176fa95ff053ab215e84d9ee72d3c212e6779`.

The replay is deterministic A/B. Private receipt SHA-256:
`8f5203364b876557d71d645911ee612a4ba4df89361d03266eec5cb3314a70e9`.
The checked-in replay templates describe only OMF ownership/interface changes.
They preserve the pre-existing `db 0` after `pfint21.asm` from the baseline
monolith, but introduce no new explicit padding and contain no target-derived
alignment byte.

This validates the v397 object-topology mechanism for all four CODE seams. It
does **not** promote OP or MAINE to exact, establish historical source
filenames, recover the original unpacked relocation-table order, or solve the
remaining DATA alignment, OP music opcode-direction, or shared `snd_load`
residuals.

## v401 historical VS.OBJ data ownership

v400 removed the four CODE seams but left one master-owned DATA mismatch in
each artifact: OP payload `0xFB97` and MAINE payload `0xE933`, both target
`90` versus candidate `00`. v401 tests whether those bytes belong to an
independent historical master.lib object rather than to the monolithic game
assembler source.

`scripts/probes/probe_th04_master_vs_object.py` starts from the hash-pinned
v400 topology candidate, verifies the independent `bin/masters.lib` archive
(SHA-256 `6be41dbcfcf4504977165ccc44443525a29a01f85a1580e6ad0c620bf802faf6`),
and extracts its historical `VS.OBJ` (SHA-256
`3bb280d22f01581b08c4fed605f09c198f54cde8b9b6767a4fef5a09953a8318`).
The surrounding monolithic DATA/BSS ranges are split into separate maintained
tail objects; the historical library object is linked between the head and
tail contributions. No target byte or explicit alignment directive is added.

The result is deterministic in two copied builds. OP drops from 5 to 4 payload
differences, removing `0xFB97`; MAINE drops from 3 to 2, removing `0xE933`.
Payload lengths remain `0x10DA4` and `0xF3CE`, and the 804-site / 559-site
relocation multisets remain target-equal. A/B executable SHA-256 values are
`3000d2c113cc4a7eb4d2f79cdb9c5cebbec1d7180e699525dafe86fbb8af3d5a`
(OP) and
`8b4a3bb3e6985f729113967398b35cff2c9c4d32860b9034fc84b839e8862553`
(MAINE).

The producer-version control matters: the historical `VS.OBJ` independently
contains an eight-byte VS DATA contribution whose tail is `90`, while pinned
TASM32 5.0 reassembly of the same maintained `vs[data].asm` / `vs[bss].asm`
source produces a zero-filled tail. Thus the recovered bytes are explained by
historical library-object identity, not by choosing a desired fill value.

Private receipt SHA-256:
`c36fb2656a3bb9435e5c1c32e2d485f890318337b96eb56878255358f3010faf`.

This closes the two remaining master.lib DATA alignment residuals as library
physical ownership. It does not grant authored reconstruction credit, prove
packed-file equality, recover the original unpacked relocation-table order, or
resolve OP music's two XOR direction bytes or the shared `snd_load` `89 C3`.
