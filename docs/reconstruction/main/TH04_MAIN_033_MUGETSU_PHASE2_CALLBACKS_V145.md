# TH04 MAIN_033_TEXT Mugetsu phase-2 callbacks (v145)

## Scope

Artifact: `th04-main / MAIN.EXE` (`candidate-local-attested`). Target SHA-256:
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.
The private executable remains ignored operator input and was not patched,
replaced, relocated, staged, or published.

v145 reviews the two callbacks immediately following the v144 dense-transition
pair. Fresh target/TASM/raw evidence proves:

| Function | MAIN_033_TEXT | Load | File | Size | MZ relocations |
| --- | --- | --- | --- | ---: | --- |
| `mugetsu_18314` | `13A9:4884..48F9` | `0x18314..0x18389` | `0x19B14..0x19B89` | `0x76` | `0x18379` |
| `mugetsu_1838A` | `13A9:48FA..49CD` | `0x1838A..0x1845D` | `0x19B8A..0x19C5D` | `0xD4` | `0x183AC`, `0x183FD`, `0x1844D` |

Together they own `0x14A / 330` reviewed authored bytes. The first slice SHA-256
is `c63dfb08b9fa8d7ebc510e92112962c6f2af6169b8bcbdaeabecd2bf64a59ed5`;
the second is
`ab6af923167da9402458eed53336904f59b635f9a2285a27f8a962e162efad5c`.

## Boundary correction

Fresh attested Ghidra has no function entry at image `0x28314`. Pinned TASM and
linear target decoding close `mugetsu_18314` exactly at the `RET` at
`13A9:48F9`; the next TASM PROC begins at `13A9:48FA`. The target
`mugetsu_update()` dispatcher independently calls this callback for phase-2
modes 0 and 6.

Fresh Ghidra creates a function at image `0x2838A` but includes only ten bytes.
That extent is rejected. Pinned TASM keeps the PROC open through `RET` at
`13A9:49CD`, immediately before `mugetsu_1845E` at `13A9:49CE`. The target
`mugetsu_update()` dispatcher calls this callback for phase-2 modes 2 and 7.
The complete reviewed body is therefore `0xD4` bytes, not the previous Ghidra
`0xA` body.

Both observations are now reviewed blocked authored functions. The correction
adds two reviewed functions and 330 reviewed authored bytes to the live
denominator.

## Maintained natural source

`src/main/boss/mugetsu_phase2_callbacks.cpp` is the maintained natural-C++
source. Its SHA-256 is
`a5af91c75b8c75a81900782c2500c126e6753c85128594cf560042cd415117e1`.
It uses TH04-local boss, bullet, frame, player, RNG, and sound declarations plus
the existing compatibility forwarder for MASTER.LIB declarations. It contains
no inline assembly, target-derived byte array, `#pragma codestring`, fake return,
inert padding, copied target bytes, ABI lie, or target patching.

Two bounded compiler-shape corrections are material:

- `mugetsu_18314` expresses the direction-dependent `+4/-4` delta through the
  legal Borland `_AL` pseudo-register so TC4J emits the target `MOV AL,imm;
  ADD AL,[angle]` dataflow instead of loading the angle first.
- `mugetsu_1838A` uses a `volatile int` local plus live `_AX` reuse for
  `boss.phase_frame & 7`. TC4J then naturally emits the target `ENTER 2,0`,
  `MOV [BP-2],AX`, `OR AX,AX`, stack-local reload, and shared/direct
  `LEAVE; RET` shapes rather than allocating the local to SI.

A fresh production-profile TC4J probe validates this instruction architecture.
Compiler-shape agreement alone receives no exactness credit.

## Replay-only layout seam

The two v144 callbacks at MAIN_033_TEXT `13A9:469A..4883` remain maintained
source-present but nonexact. v145 does not copy those bytes into product source.
Instead the exact-unit Oracle uses a hash-bound replay-only extraction of the
original scaffold span into `th04/m5tr12.asm`, generated from checked-in
`config/replay/th04_main033_mugetsu_blocked_prefix.asm.in`. The generated TASM
producer contributes exactly `0x1EA` bytes before the v145 natural C++ owner and
receives zero reconstruction credit.

The replay source order is therefore:

1. replay-only v144 blocked prefix `13A9:469A..4883` (`0x1EA`);
2. natural v145 `m5p1.cpp` at `13A9:4884..49CD` (`0x14A`);
3. residual `th04_main.asm` resuming with `mugetsu_1845E` at `13A9:49CE`.

No padding or target-byte emission is used to create this placement.

## Focused cold replay

The first focused attempt,
`gptweb-v145-mugetsu-phase2-focused-candidate-001`, failed before an Oracle
verdict because the replay-only v144 prefix did not export `mugetsu_1812A` and
`mugetsu_1821E` for later residual references. Both new C++ and replay-only TASM
objects had already compiled successfully. The fix changed symbol ownership only:
the prefix now publishes those two assembler entries and the residual declares
them external. The receiptless 34 MiB failed run was deleted as current-session
reproducible scratch after this conclusion was retained.

The corrected focused replay is
`gptweb-v145-mugetsu-phase2-focused-candidate-002`. It selects a 112-unit
dependency closure and performs two isolated cold builds. Receipt SHA-256 is
`354d1f63b18a0ec7c277f2082b85be8aa7c2451ab52b452bd39aec03b03a29da`.

Both cold builds agree on all of the following for the new owner:

- exact map contribution:
  `13A9:4884 014A C=CODE S=MAIN_033_TEXT G=MAIN_03 M=th04/m5p1.cpp`;
- exact 330-byte raw slice, target/candidate SHA-256
  `94324449758e2307b2b994df14a45238c619d05b7d63f7f4b1d4f9f02f2a9865`;
- valid deterministic TC86 Borland C++ 4.02 OMF;
- deterministic replay-only prefix TASM OMF;
- no raw/map regression in the other selected accepted owners.

The focused verdict is nevertheless **FAIL** because ordered MZ relocation
comparison does not pass. The same four relocation sites are present, but their
order differs:

- target: `0x183FD, 0x183AC, 0x18379, 0x1844D`;
- candidate: `0x1844D, 0x183FD, 0x183AC, 0x18379`.

Raw equality does not waive ordered-relocation failure. The unit therefore
remains `source-present`, and both functions remain `blocked`. No candidate-state
or post-promotion aggregate replay is run because there is no exact promotion.
The repository exact baseline remains v143's 178-owner final aggregate.

## Physical-producer routing evidence

The relocation failure reveals a larger producer question rather than a useful
reason to keep tuning these two function bodies.

In the original target, Mugetsu relocations around this region occur as descending
address runs:

- indices 567-573:
  `0x183FD, 0x183AC, 0x18379, 0x18295, 0x181A0, 0x180EF, 0x180A2`;
- indices 574-579:
  `0x18787, 0x1873A, 0x185D3, 0x18545, 0x1849B, 0x1844D`;
- index 580: `0x1898E`.

The already exact v107/v108 Mugetsu functions own the last two sites of the
first run: `0x180A2` and `0x180EF`. Independently, exact large TC4J owners in the
same repository show Borland's ordinary OMF chunking behavior: `kupdate.obj`
uses CODE LEDATA payloads `1020, 1017, 987`; `orangeup.obj` uses `1020, 309`;
and `r4update.obj` uses `1019, 328`, with FIXUPP following the chunks.

This makes a larger original TC4J Mugetsu producer beginning near the already
recovered `mugetsu_1802F` a strong falsifiable hypothesis. A first approximately
`0x3FC` CODE chunk from load `0x1802F` would end near `0x1842B`, naturally
placing `0x180A2..0x183FD` in one fixup chunk and `0x1844D` in the next. This is
routing evidence, not proof of historical translation-unit identity or author
source.

Two bounded alternatives were rejected. TC4J rejects a function-body
`#pragma option -zC...`, so source code cannot legally request a same-segment
record flush at the desired site. Compiling the same natural C++ with `-S` and
then assembling the generated source with TASM preserves the same 330 code bytes
but produces ascending relocation order, also unlike the target. Do not bypass
the ordered-relocation gate; reconstruct the larger producer instead.

Compact private diagnostics are summarized in
`.analysis/gpt-web/th04-main-20260912-v145/relocation-v145.txt` and are bound by
tracked evidence. They are ignored working state, not repository authority.

## Accounting and verification planes

After admitting the two reviewed blocked functions, live MAIN accounting is:

- reviewed authored bytes: **47,564 / 48,388 exact (98.297098%)**;
- reviewed authored functions: **300 / 305 exact (98.360656%)**;
- blocked reviewed functions: **5**;
- MAIN authored boundary candidates: **543**, with **238** unreviewed;
- all-artifact authored candidates: **722**, with **417** unreviewed.

This denominator expansion is a boundary-discovery result, not an exact-owner
regression.

Function/extent exactness for the v145 callbacks is **not established** because
ordered relocation fails despite raw/map equality. Standalone TH04 production
source/link closure is not established. Runtime-storage identity is not
established. No runtime scenario validation was run. No v145 Factory acceptance
claim was submitted or implied. Target pristine provenance remains open and
canonicality stays `candidate-local-attested`.

## Continuation

Do not retry isolated source spelling for `mugetsu_18314` or `mugetsu_1838A`:
their raw bytes already match. The evidence-connected next route is to test the
larger MAIN_033 Mugetsu physical producer beginning near `mugetsu_1802F`, first
by composing already maintained v107/v108/v144/v145 semantics under one TC4J
producer and observing OMF LEDATA/FIXUPP boundaries. The remaining adjacent
callbacks `mugetsu_1845E`, `mugetsu_184AC`, `mugetsu_18556`, `mugetsu_185E4`,
`mugetsu_18655`, `MUGETSU_PHASE2_NEXT`, `mugetsu_186B9`, and finally
`mugetsu_update()` are the target-local continuation needed to close or falsify
that physical-TU hypothesis.
