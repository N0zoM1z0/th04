# TH04 `MAIN.EXE` unresolved producer probes

This is a compact routing index for unresolved FIXUPP and code-generation
problems. It deliberately omits resolved per-version experiments and does not
define current progress. Before acting, query `config/units.csv`,
`config/th04_main_authored_functions.csv`, `config/evidence.csv`, and
`config/knowledge.csv`.

The target remains the hash-attested Japanese `MAIN.EXE`. ReC98 is pinned build
scaffolding and candidate provenance, not an independent Oracle. None of the
accepted experiments may insert target opcodes, patch OMF, edit generated
assembly, or add inline assembly to maintained C/C++.

## Unresolved cases

### `snd_load`: two bytes

The reviewed function occupies target file `0x14C96..0x14D7F` (234 bytes). After v391, maintained source owns **232/234 bytes exact**.

v391 closes the two segment-register preservation bytes:

```text
file 0x14D4E: 1E       PUSH DS    exact
file 0x14D76: 1F       POP DS     exact
```

These are not accepted merely because ReC98 contains inline assembly. Independent attested TH02 and TH05 targets preserve the same DS lifetime around their song-data read paths: caller DS is saved, the driver/read path uses another DS value, and DS is restored afterward. The checked-in symbolic fragments uniquely match the pinned TH04 scaffold and pass focused A/B plus the promoted 266-owner aggregate.

The sole remaining target bytes are now:

```text
file 0x14D57: 89 C3    MOV BX,AX
```

The following approaches are already disproved for this exact TC4J producer path and should not be repeated without materially new compiler evidence:

- ordinary `_BX = _AX`, casts, aliases, references, and register pressure;
- TASM 4.1/5.0 syntax or mode changes for `MOV BX,AX`;
- `TCC -B`, `-Z`/`-Z-`, and tested compiler option matrices;
- pseudoregister alias tricks that attempt to make BX an addressable lvalue.

Cross-game target evidence now makes the blocker stronger rather than weaker. The homologous TH02 loader uses `8B D8` after DOS open, and the TH05 loader does the same. TH04 alone uses `89 C3`. Therefore no shared low-level producer provenance currently justifies forcing TH04's direction-bit encoding.

Direct `_AX = func` also promotes the parameter to DI and changes surrounding code. The accepted memory-resident reload spelling is already preserved in the maintained source.

Next useful work must explain why this TH04 producer alone selected `89 C3` without injecting bytes or target-derived inline assembly. Otherwise these final two bytes stay blocked.

### `enemy_bullet_template_push`: 27 bytes

The complete reviewed Pascal near function occupies target file
`0x1963E..0x19658` and ends in `RET 2`. Target raw decode, TASM, TLINK, and fresh
Ghidra agree on this boundary.

Natural `-G` struct assignment, `__memcpy__`, and tested inline-helper source
forms reach the correct extent but order the `REP MOVSW` setup differently.
ReC98's inline-assembly shortcut is not acceptable evidence. Keep the entire
27-byte function blocked until a natural source or independently justified
producer reproduces the target setup order.

### `dialog_op` and `dialog_run`: relocation order

Both maintained bodies reproduce the target program bytes, but their complete
ordered overlapping MZ relocation sequences differ. They therefore remain
blocked units outside the reviewed exact-function denominator.

Already disproved controls include:

- restoring tested historical translation-unit split points;
- natural shared-function boundary matrices;
- source wrappers that leave the same producer shape;
- `#line`, local debug metadata, and external declaration reordering;
- `TCC -B` and the tested TC86 option matrix;
- `TCC -y` line-number output: [two cold dialog compiles](../../../scripts/probes/probe_th04_dialog_line_info.py)
  add three LINNUM records but retain the same two DIALOG_TEXT LEDATA/FIXUPP
  groups and change 20 program bytes at object offsets `0x790..0x7A6`
  (receipt SHA-256 `f25a2c3c770595c2c88cc71dc58f6e2621c566679e2f4c351097dc4d257996bc`);
- comparing target file offsets instead of parsing each MZ header.

The last item is a measurement hazard, not a solution: relinked candidates can
have a different `e_cparhdr`. Always compare program/load-module coordinates
and ordered relocation sites derived independently from each MZ.

Next useful work must explain the producer's FIXUPP batching while preserving
raw code, final symbol placement, and every relocation value. A matching
relocation set in a different order is still nonexact.

## Resolved controls worth retaining

The detailed evidence is in `config/evidence.csv`; these are routing summaries,
not additional exact claims.

| Control | Verified lesson |
| --- | --- |
| `bullets_update` | Correct TU/segment ownership plus `samecodeseg` framing and normal TLINK optimization can naturally recover far-to-near bridge bytes and relocation removal. |
| contiguous midboss and MAIN_035/BOSS producers | A reconstructed segment split can be false even when each isolated code range looked plausible. |
| `snd_pmd_resident` | `void far * __es *` can emit a target `LES` form that generic far pointers cannot. |
| `snd_mmd_resident` | `-WX` changes control flow and alignment; a separate zero-code alignment TU can preserve ownership honestly. |
| Yuuka/Elly/Reimu helpers | Local order, sparse switches, table ownership, and target-attested next boundaries can recover natural TC86 output despite sparse Ghidra views. |
| exact replay snapshots | Preserve source metadata and freeze all live inputs before cold A/B because Borland OMF records are metadata-sensitive. |

These controls do not authorize copying their source shape into another unit;
each candidate still needs target-local ABI, boundary, and compiler evidence.

## Adding a new probe

1. State one falsifiable source, ABI, producer, or layout hypothesis.
2. Bind the target artifact and complete compared extent.
3. Attest the toolchain before execution.
4. Inspect valid OMF CODE records and final linked placement; do not scan raw
   object bytes as if all records were instructions.
5. Compare raw bytes and complete ordered overlapping relocations.
6. Record a `pass`, `fail`, or `inconclusive` evidence row.
7. Add a scoped knowledge row only if the result changes future routing.
8. Remove bulky private probe trees after the result and digests are durable.

Private paths in historical evidence rows may no longer exist after retention
cleanup. Recreate an experiment from its checked-in command and pinned inputs
only when the recorded observation is insufficient; do not treat a missing
cache directory as permission to repeat every old source-shape guess.
