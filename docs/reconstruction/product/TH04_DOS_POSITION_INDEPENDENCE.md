# DOS position independence

The maintained DOS `MAIN.EXE`, `OP.EXE`, and `MAINE.EXE` passed three
relinks that moved code and data within their frames. The unchanged-object
control reproduced the complete executable and MAP for each artifact.
The cold baseline used the product sources at `75ff6d2` and the pinned
Borland toolchain. Every run used the same ZUN startup program.
[ReC98 scope](../../REFERENCE_ANALYSIS.md#th04-position-independence).

## Link and source evidence

The replay inserts public-segment contributions after an existing
definition. It preserves the order and hashes of the original objects.
The runs insert 16/32/48, 32/16/64, and 3/7/11 bytes of CODE/DATA/BSS
respectively. The last run also changes alignment within paragraphs.
Each real contribution retains its extent. The check maps MZ relocation
sites back to those contributions and follows immediate far CALL/JMP
targets to their code owners. The 2,666 relocation sites retain their
order within the matched owners in all three runs. The table shows the
minimum number of moved contributions over the three layouts.

| DOS artifact | CODE / DATA / BSS contributions moved within frame | MZ relocation sites | Far transfers with matching destinations |
| --- | ---: | ---: | ---: |
| MAIN | 343 / 87 / 61 | 1,183 | 957 |
| OP | 195 / 73 / 27 | 819 | 569 |
| MAINE | 174 / 56 / 23 | 664 | 511 |

For the 185 MZ segment relocations in initialized data, the preceding
offset word and relocated segment word resolve to the same owner and
relative byte in all four images. This includes far string pointers and
Borland startup and teardown callbacks.

All layouts pass the existing IRQ-vector and self-modifying operand checks
for all three executables, and both MAIN bullet switch checks. MAINE's SHARED
paragraph frame is an alias within its larger link group. The far calls
from the PAR and BGM interrupt owners still land at the same offsets in
their respective destination owners. The MAINE negative controls kept
the original layout, dropped a relocation, or restored a moved far call's
old offset. The checker rejected all three.

Capstone 5.0.6 screened 10,841 direct 16-bit CS/DS displacements that could
name a mapped owner. Of 75 candidates flagged for review, 22 belong to
maintained sources. In MAIN they fall in compiler switch keys and jump
tables. In MAINE three fall in jump tables and one starts inside the
displacement of a real instruction in `sub_bb81()`. OP has no maintained
source candidates from this screen. The odd-byte layout flags the same
75 baseline sites. The other 53 are in Borland runtime members. A separate
source review covered direct numeric memory operands,
absolute pointer construction, and emitted asm opcodes. The observed
fixed addresses belong to PC-98 hardware, BIOS, and DOS interfaces.

OP's resident counter follows its resident pointer from `0FF2:2626`
to `1012:2676` in the alternate layout. MAINE's entry operand follows
`CONG00.pi` from `0F3B:0111` to `0F61:0121`. The latter is the reference
that ReC98 resolved to reach its TH04 PI milestone.
[OP counter check](../../../scripts/probes/th04_product_surface.py),
[ReC98 change](https://github.com/nmlgc/ReC98/commit/97f0c3b4f53a60caed48ffba1a7fa0817fd1dd0e).

## Register-carried address review

The source review cleared the absolute-address candidates in the maintained
DOS code for all three executables. It covered numeric ASM operands and
inline ASM, pointer construction, and hand-encoded instructions. For example,
the two emitted far CALL forms use symbolic offset and segment words.
[Far CALL macro](../../../src/shared/runtime/master_large.inc#L24),
[BGM interrupt call](../../../src/shared/sound/bgm_timer.asm#L123).

An independent linked screen followed literal values from MOV and PUSH through
register operations to address uses. It examined 185,558 bytes from CODE
owners identified by source suffix, including the Borland startup object.
All 268 hits with literals stable under both initial relinks came from
maintained code. In the 158 table-index cases, the indexed displacement
resolves to the same MAP owner and owner-relative offset in all three images.

| Executable | Candidate uses | Indices with relocated bases | Patched immediates | Hardware, OS or stack |
| --- | ---: | ---: | ---: | ---: |
| MAIN | 160 | 73 | 19 | 68 |
| OP | 59 | 46 | 3 | 10 |
| MAINE | 49 | 39 | 3 | 7 |

The 25 uses of patched immediates refer to 13 instruction fields across the
three executables. The linked CS writes reach the same instruction fields
in both shifted builds. For `SUPER_ROLL_PUT`, all four branches replace
`1234h` with the appropriate local label before the indirect JMP. The four
linked destinations preserve their offsets within the blitter owner.
[Blitter dispatch](../../../src/shared/hardware/super_roll_put.asm#L74).

The remaining values select PC-98 video memory, BIOS state, DOS/EMS headers,
or stack slots. For example, `RESDATA_EXIST` uses `10h` relative to a DOS
allocation header, and `SELECT_FOR_RANK` adds `0Ah` to a stack-derived index.
[Resident allocation lookup](../../../src/shared/dos/resdata.asm#L24),
[Pascal argument indexing](../../../src/main/select_for_rank.asm#L21).

The follow-up traced 16-bit MOV, PUSH, and arithmetic literals through
direct branches within a CODE contribution. It reviewed 78 new MOV/PUSH
origins and found no literals carried directly into a register CALL or JMP.
For 34 of the origins, a consuming instruction's displacement follows the
same mapped owner and offset in the baseline and all three relinks. OP's
`0DC5h` and `0DE9h` come from the row and column of the portrait borders in
VRAM. MAIN's `0FA0h` indexes the shift-key half of a demo recording.
The arithmetic screen also found `1111h` placeholders in the zoom and EGC
renderers, which those routines write before use. The scan stops at calls
and indirect transfers and can follow branch outcomes that the actual
values would rule out.
[Portrait code](../../../src/op/menu/selection.cpp),
[demo input](../../../src/main/demo.cpp),
[zoom patches](../../../src/main/formats/super_zoom.asm).

The follow-up checked 208 linked CS-relative stores across 39 assembly
contributions. Each store has the same width and targets the same relative
address in its own contribution in all four EXE/MAP sets. The check uses the
MAP frame and the CS frames observed at relocated immediate far CALL/JMP
destinations. It covers more renderers, including `SUPER_ZOOM`,
`SUPER_WAVE_PUT`, and the EGC shifts.

The three maintained executables pass the local ReC98-style source criterion.
The score pair and random ring plus cursor retain their internal layouts when
moved as units.
[ReC98 criterion and score control](../../REFERENCE_ANALYSIS.md#th04-position-independence).

## Runtime evidence

Muted DOSBox-X runs booted the baseline and the 32/16/64 build through
GAME.BAT and OP into all four bundled demos. The demos cover Stages 4, 1, 3,
and 2, with both characters and shot types. The observer verified the
complete relocated MAIN image on each entry against its build's own file.
All 15,984 gameplay rows and four terminal rows match on consumed input,
score, RNG state and call order, player state, and the recorded resident
fields. The earlier 16/32/48 run also matched all 3,997 Demo 1 rows.

Independent 16-bit CPU replays use the pinned `SFF1B.CDG` and `SFF1.CDG`
resources in the baseline, 16/32/48 and 3/7/11 MAINE layouts at load
segments `2000h` and `6000h`.
Both far calls return, the four self-modifying operands stay in their own
renderers, and the aligned plane output matches the source image bytes.
[Component scope](TH04_NATIVE_ENDING_CDG_CS_V1230.md).

A seeded Reimu/Lunatic Good Ending exercised the baseline and 3/7/11
MAINE executables in DOSBox-X. The Good End and congratulation frames
at 225, 241, and 253 host seconds match pixel for pixel. Both runs closed
before the requested final checkpoint and left `GENSOU.SCR` unchanged.
The [private resident fixture](../../../scripts/runtime/fixtures/good_ending.asm)
starts MAINE with a fixed result and covers the ending from that entry.

A separate score-only seed entered MAINE's registration menu directly.
Both layouts saved byte-identical `GENSOU.SCR` files. Reimu/Lunatic gained
the seeded score of 12,345,678 and the entered name. All ten section
checksums passed, and only the selected section changed after decoding.
The raw bytes for Marisa/Hard also changed because the save routine
re-encodes all sections with new keys.
[Score save loop](../../../src/maine/score/hisave.inl).

## Replay

```sh
python3 scripts/build.py --output-dir .analysis/build/pi-dos-baseline
python3 scripts/audit_th04_dos_pi.py --baseline .analysis/build/pi-dos-baseline \
  --output-dir .analysis/build/pi-dos-audit-final
python3 scripts/audit_th04_dos_pi.py --baseline .analysis/build/pi-dos-baseline \
  --output-dir .analysis/build/pi-dos-audit-alt --padding 32 16 64
python3 scripts/audit_th04_dos_pi.py --baseline .analysis/build/pi-dos-baseline \
  --output-dir .analysis/build/pi-dos-odd --padding 3 7 11
python3 scripts/audit_th04_pi_registers.py --baseline .analysis/build/pi-dos-baseline \
  --shifted .analysis/build/pi-dos-audit-final .analysis/build/pi-dos-audit-alt \
  --output .analysis/build/pi-register-candidates.json
```

Review candidate producers against the source and compare their consumer
operands in fresh EXE/MAP pairs. The private source-only helpers remain under
`.analysis/build/pi-address-review/` and `.analysis/build/pi-recheck/`, including
the path, CS-store and far-pointer checks and the MAINE score-only seed.
Completed builds, reports and runtime disk copies have been removed. Recreate
their inputs before using these helpers; the conclusions above remain useful
without retaining the generated files.

Use each build's own MAIN MAP with `capture_th04_dos_demos.py --demos 4`.
Compare the two runs with `compare_th04_dos_demos.py --baseline` and
`--candidate`. Run `probe_th04_native_cdg_cs.py` against both builds.
The `ev-th04-*-dos-pi-*` evidence rows record the historical input and output
digests. These results describe the standalone DOS product; the historical
exact-match ledger has a separate scope.
