# Independent TH04 OP build: source graph and 16-bit link frontier

The native OP build uses only checked-in `src/op/` and `src/shared/` product
sources, the pinned TC4J/TASM/TLINK toolchain, and Borland system libraries.
`config/native_op_sources.toml` lists the ordered objects. OP's own
`snd_se_update` is selected in place of the shared MAINE implementation.
The build deliberately makes no byte-exact claim for the product EXE.

## Reproducing the frontier

```sh
python3 scripts/preflight.py
python3 scripts/ghidra.py th04-op check
python3 scripts/probes/probe_th04_native_op_link.py --check-manifest
python3 scripts/probes/probe_th04_native_op_link.py --without-support \
  --output-dir .analysis/reconstruction/probes/<new-op-run>
```

The local OP target is `candidate-local-attested`; its SHA-256 is
`8fc3b67fa8470de15b4f2844d5623d0a93d7922fac16d82a25a90a378b516b0f`.
The current disassembler check matches that file, its MZ structure, entry,
relocations, mappings, and sampled bytes. This attests the local candidate,
not an official pristine release.

## Link observations

| Scratch run | Native objects | Undefined | TLINK warnings | Other issue |
| --- | ---: | ---: | ---: | --- |
| `native-op-frontier-v872-a-20260928` | 135 | 42 | 12 | No `main`; OP and shared SE update both linked. |
| `native-op-frontier-v873-d-20260928` | 136 | 32 | 0 | Main attached; missing implementation bodies and state. |
| `native-op-frontier-v874-a-20260928` | 149 | 14 | 0 | Menu/selection/title/ZUNSOFT bodies attached; remaining hardware and music-room owners. |
| `native-op-frontier-v875-a-20260928` | 154 | 2 | 0 | Music-room callback convention and polygon renderer remained. |
| `native-op-frontier-v876-a-20260928` | 155 | 0 | 0 | TLINK reported a generic OMF fixup fatal; no EXE. |
| `native-op-cold-v877-a-20260928` | 156 | 0 | 0 | Complete source-only MZ; first ABI audit exposed a far call into near/Tiny `DOS_PUTS2`. |
| `native-op-cold-v878-a-20260928` | 156 | 0 | 0 | OP-owned far `DOS_PUTS2` fixes that distance and four-byte pointer ABI; complete MZ. |

The initial warnings came from assigning one `OP_*_TEXT` segment to multiple
OMF groups in separately compiled translation units. More seriously, `near`
calls between those physical segments produced TLINK fixup overflows. OP
sources now select one `OP_NATIVE_TEXT` group under the existing `TH04P`
product-build flag; their original pragma stays selected in strict replay.
The v873 and v874 TLINK logs have no group warnings or near fixup overflows.

TC4J's DOS command tail is short. Adding a long product-only `-D` flag made
the compiler misread the longest OP path as an altered `.cpp` name. Even a
short `-DTH4N` failed for `cmt_load_unput_and_put_both_animate.cpp`. Reusing
the existing `-DTH04P` flag avoids that failure and leaves the strict replay
configuration alone.

The v876 `Fatal: General error` was caused by `near` code emitted in a
different code segment from its caller. The polygon initializer was defined
before the product `#pragma codeseg`, while TC4J also materialized ZUNSOFT
inline/template helpers in that translation unit's default `ZUNSOFT_TEXT`
segment. Moving the polygon helper under the product pragma and selecting the
ZUNSOFT pragma before its header definitions made the same scratch link finish
with TLINK exit 0. OMF framing and checksums had been valid throughout; a
generic TLINK fatal is not evidence of an invalid OMF record.

Several early unresolved names were ABI declaration errors: C++-mangled
calls to `cdg_load_all`, `cdg_put_noalpha_8`, `graph_putsa_fx`, `super_put`,
and `bgimage_put_rect_16` while the implementation exports C/Pascal names.
The local declarations now select the actual symbol and calling convention.
No alias stubs or patched target bytes were introduced.

The v878 source-only OP MZ is 75,212 bytes. The independent MZ audit reports
799 valid, unique, nonoverlapping relocation sites and checks relocated words
at DOS load segments `0x2000` and `0x6000`. The call audit checks 17 ASM
owners, 82 relocated direct far calls, and three same-CS pushed far calls.
The auditor initially reported eight more apparent near-source entries:
`FILE_APPEND`, `FILE_CLOSE`, `FILE_CREATE`, `FILE_READ`, `FILE_ROPEN`,
`FILE_SEEK`, `FILE_WRITE`, and `GRAPH_CLEAR`. Those source files select far
procedures and `retf` under `TH04_LARGE_PRODUCT`; the audit now checks their
linked first return and stack-pop count explicitly. The ZUN/Tiny near
`DOS_PUTS2` source remains intact, while OP owns its large-model, far-pointer
implementation in `src/op/dos/dos_puts2.asm`.

Independent v878 A/B cold builds have the same complete MZ SHA-256
`a21afefaf14c9530c2e6b85c4fd322bfe8b8c25bbd92c063c2534655f1f41180`
and all 156 link-relevant and timestamp-normalized OMF objects agree. Only
BGIMAGE's raw dependency timestamp comment differs. The source graph and
link response use no `masters.lib`.

The v877 disposable HDI ran the normal `GAME.BAT` route. Captures at 10 and
20 seconds show the ZUN Soft/Touhou Project animation; the 45-second capture
is black. The v878 candidate shows the TH04 title image at 60 and 100 seconds.
An original-image control at 45 seconds is already in demo gameplay. A
disposable `GAME.BAT` with markers around each of its five OP invocations
records `START` and `OP_BEFORE` at 100 seconds, with no `OP_AFTER`. This only
shows that OP did not return normally to the batch file. The demo route calls
`op_exit_into_main(false, false)`, which uses `execl("main", ...)` to replace
OP directly; `OP_AFTER` is therefore not an OP-to-MAIN checkpoint. The
original/candidate screens are separate runtime observations, not a byte or
behavioral equality claim.

A private source-overlay experiment skipped only the title sequence's song
load/play calls; its 85-second capture stayed on the same title image. The
maintained source was restored byte-for-byte after this diagnostic cold link.
The experiment rules out that call block alone as a sufficient cause. A
second private probe returns just before the title sequence's flash. Its
70-second capture shows the main-menu text on the title background, proving
that the slide/frame-delay loop has completed in that variant. Two later
return-after-background variants show a white frame at 85 seconds; one remains
white at 200 seconds. White is also the expected flash palette, so these
frames alone cannot prove which background subcall ran. A native-only PI slot
pointer-clear experiment still showed the title at 100 seconds and was
reverted; it is a negative result, not an accepted fix.

The deterministic `probe_th04_op_title_trace.py` now overlays one-byte stage
markers and restores all product inputs after building. Its first two file
paths did not record a marker and are instrumentation failures. The v887
version writes `OPMARK.TXT` in the current game directory. Its 100-second
receipt records `op_trace_marker_hex = 4a` (`J`), the marker just before the
main-menu loop. The trace variant therefore completed the slide, frees,
background load, palette fades, score/sprite/CDG loads, and reached the menu
loop. The static audit found 802 valid relocation sites in this private MZ.
The visible title at 100 seconds is a menu-rendering or loop-progress symptom;
the v888 trace narrows it further: its last marker is `N`, immediately before
the first `menu_init()` call, while the after-call marker is absent at 100
seconds. v889 ends at marker `P`: the initial EGC rectangle copy returned,
and the first `main_unput_and_put()` call did not. The v890 variant now marks
that first render's smaller EGC copy, GRCG setup, CDG command, and active
cursor/description calls. v890 ends at `U`, after the first label's EGC copy,
GRCG setup, main CDG command and GRCG shutdown; the active cursor/description
block has not returned. Its 100-second frame is black, unlike the earlier
title-background captures, so changes in trace code/layout can affect the
visible symptom. The v891 probe splits the two cursor CDG calls and description
rendering, and saves the three 16-byte CDG slot records involved. It reaches
marker `V` after the left cursor. Slot 10 has the `SFT2.CD2` header, slot 35
has the `CAR.CD2` header and allocated plane segments, but slot 36 is all
zero at the menu boundary. `cdg_put_8` loads that zero width into CX and then
uses `LOOP`, which wraps CX to `FFFF` and makes the right-cursor draw
pathological. The pinned archive's `CAR.CD2` header requests two images, so
slot 36 should have been populated.

The linked local `HMEM_ALLOCBYTE` uses `LES` and does not restore ES, while
`CDG_LOAD_ALL` previously set ES to DGROUP only once before its image loop.
It is therefore inferred that the second header copy wrote outside DGROUP.
The v892 native-only ASM change re-establishes `ES=DS` after each `cdg_free`
and before each `REP MOVSD`, leaving the strict replay path unchanged. Its
source-only OP links without warnings; 799 MZ relocations and the 17-owner
far-call audit pass. The normal 100-second frame is black; this frame alone
does not identify the running executable. The v893 trace reaches marker `j`
after the first main-menu `frame_delay(1)`. Its 48-byte CDG dump shows valid
headers and allocated plane segments for slots 10, 35, and 36; slot 36 was
zero before the change. This is runtime evidence that the native-only ES fix
restores the missing second cursor resource and advances the menu loop. These
private variants are diagnostic builds, not product acceptance builds.

To test the handoff independently of original MAIN behavior, the v894 private
HDI replaces only `MAIN.EXE` with a disposable TC4J large-model entry shim:
`_dos_creat("MAINHIT.TXT", 0, &h)`, one-byte `_dos_write` of `H`, and return.
The shim is a valid 29,186-byte MZ with 218 relocations (SHA-256
`0d9e186532ebf2687625c9399be0ddeef19f2268da0cce5fc0490954545efdc2`).
Native OP, pinned resources, and the normal `GAME.BAT` route are unchanged.
The 100-second DOSBox-X receipt

has `mainhit_marker_hex = 48` and `diagnostic_marker_hex` decoding to
`START` followed by `EXIT`. This is direct runtime evidence that native OP
passed control to `MAIN.EXE` and that the shim returned to the batch. It does
not show original or reconstructed MAIN running, nor an OP-to-MAINE transfer.
The shim source and compiler/linker logs are retained under
`.analysis/reconstruction/probes/native-op-mainhit-shim-v894-20260928/`;
the diagnostic image preparation receipt pins both the shim and OP MZ hashes.

The v892 native OP A/B cold links have identical complete MZs and all 156
link-relevant OMF records agree. Four raw objects differ only in Borland
source/dependency timestamp comments. A private source overlay rewrote the
timestamps for three of these files between runs. The OMF comparator now
normalizes both the previously known `E9` format and the observed `E8` form
(`00 E8 01`, Pascal path, four trailing DOS time/date bytes); it leaves the
path and all other records intact. The focused OMF test and A/B comparator pass.

For a bounded resource check, the pinned TH04 OP/ending PAR directory lists
`OP1.PI` as an 18,129-byte member, and its PI header declares 640×400.
That rules out a missing archive member and a 16-bit member-length overflow
for this image. The shared PI decoder already has a separate two-image
640×400 runtime Oracle; OP1 specifically still lacks decoded-pixel comparison.

The disposable DOSBox-X frame runner now records `host_timeout` and kills its
own process group after the requested frame deadline when the emulator does
not exit itself. A host-stopped run can support a screenshot and HDI marker
observation; its `returncode = -9` is not game-process exit evidence.

DOSBox-X logging showed candidate-only writes to `F5000` ROM addresses,
containing PMD.COM bytes. The original control had no such writes during its
55-second run. This is a separate symptom; source ownership and causality
remain unknown. Direct emulator runs must mount a copy of the prepared HDI:
one exploratory command changed a prepared private image, which was restored
from an identical freshly prepared image and hash-checked before further use.

## Product-only source status

The title, main menu, setup, character selection, logo, and music-room glue
uses maintained local `.inl` bodies and TH04-specific declarations/state.
The Shift-JIS menu literals are candidate data transcribed as byte escapes
from the local ReC98 reference; they still need a target-data/runtime check.
The new pixel GRCG primitives, rounded rectangle path, and sprite rectangle
entry are real PC-98 rendering code. The `super_put_rect` entry currently
shares the local `super_put` screen clipping behavior. `respal_create/free`
performs a real four-paragraph DOS allocation/free but does not mark an MCB
resident across processes; TH04 OP does not use its palette payload. These
implementation choices need scenario-based validation before runtime
acceptance. A successful link alone will not establish that acceptance.

The shared `CDG_LOAD_ALL` strict replay was cold-linked twice against each
accepted artifact owner after the native-only change. OP and MAINE decoded
module extents still have zero raw differences and their overlapping
relocations agree; the v895 receipt is
`.analysis/reconstruction/probes/cdg-load-native-guard-replay-v895-20260928/receipt.json`.
The affected standalone MAINE product was also cold-built twice after the
guard: 130 TH04-owned objects link without warnings or unresolved names to
the same complete MZ SHA-256
`adaea486a9931ae1dcead561c8b5ea2bbfab9619f13c3ace699e678c06b23aa2`.
Its independent audits pass 656 relocation sites, 36 far-return ASM owners,
148 direct far calls, and one same-CS call. These are static build checks;
MAINE runtime entry remains unproven.
Next gates: build MAIN from TH04-owned source, checkpoint its transition to
MAINE, and test the combined candidate product chain.
