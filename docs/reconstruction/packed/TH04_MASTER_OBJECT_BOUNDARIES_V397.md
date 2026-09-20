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
