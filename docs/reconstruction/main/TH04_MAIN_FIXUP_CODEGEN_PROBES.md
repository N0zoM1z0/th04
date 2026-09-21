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

Cross-game target evidence now makes the blocker stronger rather than weaker. The homologous TH02 and TH05 loaders use `8B D8` after DOS open. v403 additionally restores the registered TH03 OP target and proves its complete 0x70-byte `snd_load` body is byte-identical to the shared natural candidate, including `8B D8` at load `0xBF9B`. TH04 alone uses `89 C3`. Therefore no shared low-level producer provenance currently justifies forcing TH04's direction-bit encoding.

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

## v399 pinned Turbo C++ optimizer-driver surface

External Borland C++ documentation suggested a genuinely different hypothesis:
the 16-bit `BCC.EXE` family exposes individual `-O*` optimization controls such
as loop optimization. That material is only search routing, not TH04 evidence.
The pinned TH04 toolchain is the locally attested Japanese Turbo C++ 4.0J
installation whose active compiler is `TCC.EXE` 4.02, and its active `TC4/BIN`
contains no `BCC.EXE`.

`scripts/probes/probe_tc4_optimizer_suboptions.py` therefore tests the candidate
switches against the actual pinned compiler instead of substituting another
Borland driver. Under the normal `-ml -b- -3 -Z -d` base profile, `TCC.EXE`
accepts `-O` and hard-rejects each of the following as an incorrect command-line
option:

`-Ob -Oc -Oe -Og -Oi -Ol -Om -Op -Os -Ot -Ov -O1 -O2 -Ox -Od`

The probe verifies the configured TCC SHA-256 before execution and records the
absence of `BCC.EXE` from the active TC4 binary directory. Private receipt:

`.analysis/gpt-web/v399-tcc-opt-surface-001/receipt.json`

SHA-256:

`21841e42bcdb3346d1ffb379319152804308c91460b0402a189f26d89dac69e8`

This closes the BCC-style optimizer-suboption route for the currently attested
Turbo C++ 4.0J toolchain. It does not prove that every possible C++ source form
is incapable of producing a remaining blocker, and it does not authorize a
different compiler, inline assembly, or target-derived machine code.

## v403 TH03 snd_load cross-check

The remaining TH04 `89 C3` anomaly is not shared by TH03 either.
`scripts/probes/probe_th04_snd_load_th03.py` restores the registered
`th03-op-smoke` target with pinned DIET 1.45f under pinned DOSBox-X PC-98,
then compares its decoded loader with the hash-pinned v401 candidate. The
complete TH03 `snd_load` body at load `0xBF52..0xBFC1` is byte-identical
(body SHA-256
`5f8f4aee2edc3a11243bc57dbd716cfd3665adcdccfd63192c6bda6be516ad6c`)
and encodes the DOS-open handle copy at `0xBF9B` as `8B D8`.

Private receipt SHA-256:
`0c42953f500081a16546e1767440c0acb26b2d4099d09a831a82c1b077058bd3`.

Together with v391, every independently checked homologous loader in TH02,
TH03, and TH05 uses `8B D8`; only TH04's shared MAIN/OP/MAINE producer uses
`89 C3`. This is stronger negative provenance, not permission to infer that the
TH04 line was inline assembly. The two bytes remain blocked.

## v404 TC4J pragma-intrinsic surface

A Borland C++ 4.0 manual surfaced one compiler mechanism not covered by the
command-line option matrix: `#pragma intrinsic` can request inline forms of
standard memory/string routines even when the driver does not expose `-Oi`.
The web/manual observation is routing only; v404 tests the pinned Japanese
TC4J compiler itself.

The attested TCC 4.02 accepts pragma intrinsics and naturally emits string
instructions: `memcpy` produces `REP MOVSW`, `memset(...,0,...)` produces
`REP STOSW`, `strlen` uses `REPNE SCASB`, `memcmp` uses `REPE CMPSB`, and the
string-copy family combines SCAS/MOVS/STOS forms. The same driver hard-rejects
lowercase `-z/-z-`, `-Oa/-Oa-`, and `-OW/-Ow`, so those BCC manual switches do
not extend the pinned TCC surface.

Across the tested `memcpy`, `memset`, `strlen`, `memcmp`, `strcpy`, `strncpy`,
and `strcat` bodies, none emits `LODSB` or x86 `LOOP`. More importantly, these
are contiguous-range primitives: substituting them for carpet's stride-0x40
tile writes / stride-0x20 dirty writes or checkerboard's stride-8 stores would
change the touched addresses and is therefore not a legal reconstruction.

Private receipt SHA-256:
`4c65b90e53178acefaf2ae68506d33fbc9800d205acc77e15252d32996c5db73`.

This is a bounded compiler negative, not a universal proof about every TC4J
source form. It closes the newly discovered intrinsic/string-op route for the
current final MAIN blockers without granting exactness.

## v406 same-media PC-98 IDE optimizer surface

Borland C++ 4.0 documentation for other distributions exposes an IDE loop
optimizer, so the command-line TCC rejection of `-Ol` did not by itself close
the possibility that the Japanese PC-98 integrated environment stored a hidden
project flag. v406 tests that exact mechanism using only the pinned TC4J media.

The probe extracts Borland's own `TCALC.PRJ` and PC-98 `TC.EXE` from the
attested media, parses all 102 scalar project option records, and uses the
media's `PRJ2MAK.EXE` to toggle every binary-valued record. Across 120 mutated
project configurations plus the CPU=386 enum control, the complete observed
optimizer flag set is only `-O`; no `-Ol`, `-O1`, `-O2`, or other `-O*`
suboption appears. The production-like project resolves to `-ml -3 -O -Z -d
-b-` with the sample debug flags removed.

The same-media PC-98 integrated compiler is then run under the pinned DOSBox-X
PC-98 profile. Its OMF still identifies `TC86 Borland C++ 4.02` and emits:

- counted loop: `55 8B EC 57 B9 06 00 83 C7 08 49 8B C1 0B C0 75 F6 5F 5D CB`;
- load/increment: `55 8B EC 56 8A 04 46 5E 5D CB`.

Thus the IDE producer also emits `DEC/MOV/OR/JNZ`, not x86 `LOOP`, and
`MOV AL,[SI]; INC SI`, not `LODSB`. The long project scan can be finalized
with `--resume-existing`, which revalidates every generated `P.MAK`, the
production configuration, DOSBox markers, OMF identity, and both public code
slices before writing the receipt.

Private receipt SHA-256:
`e63c0972715f1f681eb06fb086ee2dd272fc144691df685ce4777ef4fa721ef5`.

This closes the same-media IDE hidden-optimizer route for the remaining
checkerboard/carpet instruction shapes. It does not prove original source
language and does not authorize target-derived inline assembly.

## v411 register-encoding front-end matrix

The final `snd_load` and carpet residuals share one remaining compiler question:
could a different *attested* TC4J front end or register/optimization strategy
naturally select the target-equivalent register/register opcode directions?
`scripts/probes/probe_tc4_register_encoding_surface.py` closes that surface.

The pinned TCC 4.02 driver compiles one combined pseudo-register probe under
production `-O`, no `-O`, explicit `-O-`, `-O -G`, `-O -G-`, `-O -r`, and
`-O -G- -r`. All seven profiles emit the same CODE body. The probe then builds
the same operations with the independently attested same-media PC-98 `TC.EXE`
under the production-like IDE project established by v406. Its OMF translator
identity remains `TC86 Borland C++ 4.02` and the opcode choices agree with TCC.

Observed natural forms are `8B D8` for `_BX=_AX`, `8B F0` for `_SI=_AX`,
`8B FA` for `_DI=_DX`, `33 D2` for `_DX=0`, `03 DB` for `_BX+=_BX`, `03 FF`
for `_DI<<=1`, and `F7 EB` (`IMUL BX`) for the tested low-word `_AX*_BX`
expression. None emits the target residual forms `89 C3`, `89 C6`, `89 D7`,
`31 D2`, `01 DB`, `D1 E7`, or `F7 E3`. Explicit unsigned C multiplication was
also checked separately in the private scratch matrix and still selects IMUL
when only the low 16-bit result is consumed.

Private receipt SHA-256:
`73096dccfd0f4ad4a813378407d8a49d170059b86da6fd7dd9e78e5d152e887a`.

This is bounded negative compiler evidence. It does not prove original source
language and does not authorize target-derived inline assembly. `snd_load`'s
`89 C3` and the corresponding carpet register/MUL/shift residuals stay blocked.
