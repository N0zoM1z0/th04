# TH04 reconstruction handoff

## Current phase

The headless reconstruction environment is operational. The whole-artifact
boundary/origin inventory remains the routing baseline while exact natural-source
reconstruction continues. `config/th04_function_boundaries.csv` is the current
routing inventory and `docs/BOUNDARY_REVIEW.md` is its generated explanation.

The inventory contains 2,120 distinct function-like observations:

- 732 authored reconstruction candidates: OP 94, MAIN 553, MAINE 72, ZUN 13;
- 295 accepted exact MAIN functions and two reviewed blocked MAIN functions;
- 435 authored candidates otherwise unreviewed;
- 52 original-style ASM observations in a separate attestation queue;
- 1,336 compiler/runtime/library/data/switch observations explicitly excluded.

Across the live MAIN source/acceptance ledgers, the current totals are:

- authored C/C++ bytes: **46,188 / 46,219 exact (99.932928%)**;
- accepted authored functions: **295 / 297 exact (99.326599%)**;
- accepted exact C/C++ owners: **168**;
- original-style ASM: **9 units / 1,489 exact bytes**, tracked separately;
- currently confirmed nonexact authored bytes: **31 bytes** in the two accepted
  blocked functions.

v119 promotes the v117/v118 source-present frontier owners only after focused
and aggregate cold replay. v120 then closes the structurally adjacent 0xD6
Yuuka6 chase-cross/safety-circle renderer through natural C++, focused replay,
and a 156-owner aggregate. v121 then recovers the adjacent 0xAA default
midboss defeat renderer with natural C++, while retaining its one-byte angle
in the original assembler data owner through a symbol alias. Focused and
157-owner aggregate replay close that owner. v122 recovers the preceding 0x12F
Orange foreground renderer on its first natural TC4J source shape and closes it
with focused plus 158-owner aggregate replay. The same packet target-reviews the
preceding no-Ghidra Kurumi physical extent without granting source/exact credit.
v123 then recovers that complete 0x1D8 Kurumi foreground owner as natural C++
and closes it with focused plus 159-owner aggregate replay and the explicit
no-Ghidra function-review gate. v124 then recovers the connected 0x154 Kurumi
spawn-ray allocator/updater cohort in `MAIN_033_TEXT`; hash-bound replay-only
suffix extraction preserves the original internal producer order while the
untouched residual suffix receives zero reconstruction credit. Focused and
160-owner aggregate replay close the natural owner. v125 then recovers the first
three adjacent spawn-ray phase handlers as one 0x1D0 natural-C++ owner, including
a 33-byte ordinary basic block omitted from Ghidra at `0x28BE6`; focused plus
161-owner aggregate replay close it while pre/post residual seams remain zero-credit
plumbing. v126 closes the next four late phase handlers as one 0x2A4 natural owner
with a 162-owner aggregate. v127 then closes the immediately following 0x103
bullet-stack phase with final focused plus 163-owner aggregate replay and target-
corrects the following FAR `kurumi_update()` dispatcher boundary. v128 follows the
ordered-relocation evidence back to the original physical translation-unit boundary:
the two remaining 0x3F orbit helpers plus all v124-v127 Kurumi source and the FAR
dispatcher compile as one exact 0xBD0-byte TC4J producer. Final focused plus a
165-owner aggregate close every declared slice, the shared map contribution, and
all 28 ordered MZ relocations. The unresolved shot residual still receives no
reconstruction or function exactness credit. These percentages are not a claim
about 99.931787% of an executable or the game. Derive current
numbers with `python3 scripts/status.py`; `config/units.csv`,
`config/th04_main_authored_functions.csv`, and
`config/th04_function_boundaries.csv` override prose.

`OP.EXE`, `MAINE.EXE`, and `ZUN.COM` still have no accepted reconstruction
units. No deterministic TH04 runtime-differential scenario has been authored.

## Target and analysis identity

The active `th04-main` target is `.analysis/targets/th04/main.exe`:

- size: 156,258 bytes;
- SHA-256: `077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`;
- MZ header: 6,144 bytes;
- entry `CS:IP`: `0000:0000` (`1000:0000` at the Ghidra image base);
- relocations: 1,136;
- load-module SHA-256:
  `3a30221339626ce7608e3169063864b55d78881d64e90e56e1dd8e5a02ae140d`.

The target and read-only Ghidra database pass the configured MZ, entry-point,
relocation, mapping, and sampled-byte attestations. Target canonicality remains
`candidate-local-attested`; this is a known provenance gap, not proof of a
pristine official dump.

The other three on-disk targets are DIET-packed MZ containers. Their own
attested decompressor stubs were run at load segments `0x1000` and `0x2000`;
both runs produced identical unrelocated payloads and relocation streams:

- OP: 69,028 bytes, 804 relocations, SHA-256
  `13222cb667e15c5034bd64c840a1db0a07c9acbb56e50f0bcf6025d12fe78d74`;
- MAINE: 62,414 bytes, 559 relocations, SHA-256
  `7495ae43641bc696d13d18c366e364f6bc8b6a86a1afb681f34c9a334dae792c`;
- ZUN: 13,422 bytes, no relocations, SHA-256
  `baf5a58b333af1135d67c7dd7a4f86e2c828ae149c8219d5d1f589073b0bde9e`.

OP and MAINE Ghidra projects use private diagnostic hybrid MZ images: the load
module is target-observed, while the checked header and relocation table come
from the cold candidate. They are not original-unpacked-EXE claims. The flat
ZUN payload is raw exact to the cold candidate composition pipeline and is
split into configured selector/data/embedded-COM/stub regions.

## Latest accepted batch

v88 recovers public FAR `reimu_update()` at `0x2F3AB..0x2F8ED` as one
0x543-byte exact owner: 0x515 bytes of code plus two compiler switch-table
regions. Fresh Ghidra cross-links its body beyond the true owner; pinned TASM,
raw decoding, switch-target validation, and exact map ownership define the
accepted extent.

v89-v94 recover the first Gengetsu family at `0x2F8EE..0x2FEDE`: 1,521 bytes,
seven exact C++ owners, and twelve exact functions. v95-v98 then close the rest
of `MAIN_036_TEXT` from `0x2FEDF..0x306EB`: another 2,061 exact bytes in four
natural-C++ owners and seven exact functions. Important boundaries are:

- `0x2F8EE`, `0x2F903`, and `0x2F97A` are three functions in one physical
  TC86 producer. Splitting the producer loses the alignment byte before the
  middle function's sparse switch tables.
- Ghidra has no entry at `0x2F8EE`, `0x2F97A`, **or `0x30050`**. The last one
  is admitted only through the no-Ghidra reviewer after pinned TASM, raw RET,
  generated-public, and next-PROC validation.
- `gengetsu_columns_phase()` at `0x2FEDF` owns code through `RET` at `0x30047`
  plus a four-word compiler jump table through `0x3004F`.
- `gengetsu_cycle_phase()` at `0x2FD30` owns 0xC4 code bytes through `RET` plus
  a five-word jump table, for a complete 0xCE-byte extent through `0x2FDFD`.
- public FAR `gengetsu_update()` at `0x3026A` continues through `RETF` at
  `0x306D7` and owns the following ten-word phase jump table through `0x306EB`.
  Fresh Ghidra stops early; raw/TASM/table-target review defines the exact end.

v99 expands the reviewed authored universe in `END_TEXT`: `end_game_good()`, `end_game_bad()`, and `end_extra()` at `0x1B7B9..0x1B834` are three contiguous FAR bodies (0x2B, 0x2B, 0x26) agreed by target Ghidra, pinned TASM, TLINK publics, and raw decode. One pure-C++ producer reproduces all 0x7C bytes; `#pragma samecodeseg GameExecl` selects the target TLINK `NOP; PUSH CS; CALL near` optimization and exact relocation order without byte emission.

v100 closes the `END_TEXT` suffix with target-first natural C++: `map_load()` at `0x1B971..0x1B9BA` (0x4A) and `map_free()` at `0x1B9BB..0x1B9D5` (0x1B) are full contiguous Ghidra/TASM/TLINK/raw bodies. No ReC98 C++ body exists. The exact link layout is `endmain.cpp` 0x7C + unchanged `th04_main.asm` middle 0x13C + `mapend.cpp` 0x65, preserving the complete segment length and ordered relocations without padding or ASM splitting.

v101 corrects a material authored-boundary error in `BOSS_FG_TEXT`: fresh Ghidra creates `gengetsu_fg_render()` at `0x22F5F` but includes only the first 5 bytes (`ENTER 2; PUSH SI`). Pinned TASM keeps the PROC open through segment end, and raw target decoding closes at `LEAVE; RET` on `0x230EB..0x230EC`, proving the full **0x18E / 398-byte** function. Target-first natural C++ reproduces all 398 bytes, exact map placement, and the complete ordered relocation overlap in focused and 139-owner aggregate cold replay.

v102 recovers the `BOSS_BG_TEXT` suffix `mugetsu_gengetsu_bg_render()` at `0x22979..0x22A09` as a full **0x91 / 145-byte** natural-C++ owner. Fresh Ghidra, pinned TASM, MAP ownership, and raw decoding agree on the boundary; focused and 140-owner aggregate cold replay are raw/map/ordered-relocation exact. Target packed Pascal arguments also disprove the initial `(16,32)` backdrop-coordinate hypothesis: both target calls require source arguments `(32,16)`.

v103 recovers the `TILE_TEXT` prefix `enemies_invalidate()` at `0x1C74C..0x1C776` as a **0x2B / 43-byte** pure-C++ owner. Fresh Ghidra, pinned TASM, MAP ownership, and raw decoding agree on the complete body. The following target byte `0x1C777 = 0x90` is the original `EVEN` alignment gap, not authored function code; linking the odd-sized C++ object before the remaining ACBP=48 assembler contribution naturally preserves that byte; focused and aggregate cold replay remain exact.

v104 recovers the `MAIN_01_TEXT` prefix `BB_TXT_LOAD` at `0x21551..0x2159A` (0x4A) and `BB_TXT_FREE` at `0x2159B..0x215B5` (0x1B) as one **0x65 / 101-byte** pure-C++ owner. The first focused source is raw/map/ordered-relocation exact, including the target Pascal far-buffer encoding for loading `TXT2.BB` at offset 0x800. Existing `txt.bb`/`txt2.bb` data is referenced through byte-preserving aliases rather than copied. Focused and aggregate replay are exact.

The same v104 boundary pass also downgrades `pointnums_add_yellow()` at `0x23D90` from corroborated to provisional: its Ghidra body stops after the 0x1A entry stub, but target `JMP 0x23DBE` enters a shared tail also reached by `pointnums_add_white()` at `0x23DAA`, continuing through `RET` at `0x23DF0`. Do not treat the 0x1A Ghidra body as a closed authored function extent.

v105 continues the `MAIN_01_TEXT` prefix with `mugetsu_fg_render()` at `0x215B6..0x21646`, a complete **0x91 / 145-byte** renderer. Fresh Ghidra, pinned TASM, raw decoding, focused cold replay, and its then-current aggregate all agree. The first v105 build also exposed a reusable symbol-ownership rule: because this TASM symbol had a top-level `PUBLIC` far from its PROC body, moving the producer to TC4J required changing that assembler declaration to `EXTRN`; adding a second `EXTRN` at the former body site leaves TASM trying to export an external symbol. The exact source remains ordinary C++ and publishes the former `byte_259E6` as the Mugetsu damage-flash parity counter.

v106 closes the remaining target-derived C/C++ code contribution in `MAIN_01_TEXT` by recovering the former `sub_11647` at `0x21647..0x21691` as `gengetsu_bomb_inv_render()`, a complete **0x4B / 75-byte** pure-C++ helper. The first focused probe was only two bytes too long because fixing X directly to `_SI` made TC4J emit `MOV AX,SI; ADD AX,48`; switching X to a compiler-managed register local while fixing Y to `_DI` produces the target `LEA AX,[SI+48]`. Focused and aggregate replay are raw/map/ordered-relocation exact. The final segment tiling is `bbtxt.cpp` 0x65 + `m5fg.cpp` 0x91 + `g6binv.cpp` 0x4B + zero bytes from target-derived `th04_main.asm`, followed by the independent 0x101-byte `scoreupd.asm` original-style ASM owner.

v107 opens the `MAIN_033_TEXT` Mugetsu frontier with one exact 0x8C-byte natural-C++ producer: `mugetsu_gathers_add_dual()` at `0x2802F` is a complete 0x15-byte body, while `mugetsu_gather_intro()` at `0x28044` is corrected from Ghidra's truncated 0x11 body to a reviewed **0x77-byte** authored extent. Raw/TASM decode closes code at `RET 0x280AA`; the following 4-word compare table (`0x20,0x22,0x24,0x30`) and 4-word jump table fill `0x280AB..0x280BA`. The reviewer verifies all four jump targets are instruction starts and the trailing extent is fully accounted. Focused and aggregate replay are raw/map/ordered-relocation/OMF exact.

v108 continues `MAIN_033_TEXT` with the Ghidra-missed `mugetsu_180BB()` callback at `0x280BB..0x28129`, a complete **0x6F / 111-byte** pure-C++ owner. Fresh Ghidra reports no function at the entry; pinned TASM and gap-free raw decode close at the next PROC `0x2812A`, the exact TC4J object generates `_mugetsu_180BB` at `13A9:462B`, and target stores at runtime `0x28748` and `0x2880C` independently encode that near offset into `fp_259E8`. The first source was five bytes too long because early returns changed branch layout; ordinary C++ `goto` labels reproduce the target shared `ret0` control-flow sink. Focused and aggregate replay are raw/map/ordered-relocation/OMF exact.

v109 then recovers the `BOSS_FG_TEXT` suffix `reimu_fg_render()` at `0x22E93..0x22F5E` as a complete **0xCC / 204-byte** pure-C++ owner. Fresh Ghidra, pinned TASM, raw decode, and segment tiling all agree. The first focused source is byte/map/relocation exact; it reuses the existing `_reimu_trail_visible` alias from v71 and publishes the unchanged ASM `sub_12E37` orb renderer as `_reimu_orbs_render` through a byte-preserving label. Focused and aggregate replay are exact.


v110 immediately replaces that temporary orb-render alias with maintained natural C++: `reimu_orbs_render()` at `0x22E37..0x22E92` is a complete **0x5C / 92-byte** helper. Reusing the already target-verified Reimu orb layout gives the exact SI pointer, DI index, three stack locals, 32-slot loop, and `super_roll_put` sequence on the first focused source. Fresh Ghidra/TASM/raw agree on the complete body.

v111 then recovers the preceding `items_render()` at `0x22DF0..0x22E36`, a complete **0x47 / 71-byte** pure-C++ function. Borland `_ES = SEG_PLANE_B` naturally emits the target `MOV AX,0xA800; MOV ES,AX`; after correcting C linkage and delaying SI/DI register-local assignment until after the ES setup and splash-render call, focused replay is byte exact. The then-current aggregate proves the suffix tiling `th04_main.asm` 0x10B + `items.cpp` 0x47 + `r4orbf.cpp` 0x5C + `r4fg.cpp` 0xCC + `g6fg.cpp` 0x18E with no manufactured padding.

v112 closes `BOSS_FG_TEXT` by recovering the final target-derived assembler owner, `BULLETS_RENDER` at `0x22CE5..0x22DEF`, as a complete **0x10B / 267-byte** pure-C++ function. Same-game exact compiler evidence from `bullets_update()` identifies `#pragma option -G` as the source-level switch that reproduces the target `PUSH BP; MOV BP,SP; SUB SP,2` frame instead of `ENTER 2,0`; assigning `_AX = bullet->patnum` before the three special cloud-sprite comparisons reproduces the target one-load/three-register-compare sequence. Focused and 150-owner aggregate replay are raw/map/relocation/OMF exact. The final segment tiling is `bulrend.cpp` 0x10B + `items.cpp` 0x47 + `r4orbf.cpp` 0x5C + `r4fg.cpp` 0xCC + `g6fg.cpp` 0x18E, with **zero bytes** from target-derived `th04_main.asm`.

v113 then peels the `BOSS_BG_TEXT` suffix with the Ghidra-missed `yuuka6_bg_render()` at `0x228B9..0x22978`, a complete **0xC0 / 192-byte** pure-C++ owner. Fresh Ghidra has no function entry there; pinned TASM/raw close at `RET 0x22978`, the TC4J object generates public `yuuka6_bg_render()` at `0AAF:7DC9`, and the owner ends exactly at the next exact public `mugetsu_gengetsu_bg_render()` at `0AAF:7E89`. The first compilable source is raw/map/relocation exact; it publishes byte-preserving aliases for the Yuuka6 background state/fade bytes, `playfield_fill`, and the unchanged `sub_12461` update helper. Focused and 151-owner aggregate replay are exact, reducing the remaining target-derived BOSS_BG_TEXT contribution from 0x7FB to **0x73B**.

v115 corrects another material Ghidra boundary error at the end of `MAIN_012_TEXT`. Ghidra constructs only `0x21ECB..0x21EF6` (**0x2C / 44 bytes**) for the former `sub_11ECB`, but pinned TASM keeps that PROC open to segment end and target raw decode continues through `RET 0x21F95`. The accepted authored extent is therefore **0xCB / 203 bytes**, ending exactly at the next exact public `cfg_load_resident_ptr()` at `0x21F96`. `src/main/stage_state_init.cpp` reproduces the full extent on its first focused source: scalar stage-state resets, packed-Pascal `grc_setclip`, nine target/BSS-verified dword storage clears through the unchanged `CLEAR_DWORDS`/`REP STOSD` helper, and gather-template initialization. Focused and 152-owner aggregate replay are exact, reducing target-derived `MAIN_012_TEXT` ownership from 0x803 to **0x738**.

v116 peels the next `MAIN_012_TEXT` suffix function, `elly_fg_render()` at `0x21E12..0x21ECA`, a complete **0xB9 / 185-byte** pure-C++ owner. Fresh Ghidra reports no function at this entry, while pinned TASM/raw close at `RET 0x21ECA`; TC4J generates public `elly_fg_render()` at `0AAF:7322`, and the owner ends exactly at the next exact `_stage_state_init` public at `0x21ECB`. The first focused source differed by one byte only (`PUSH DI` versus target `PUSH AX` for the no-damage top argument); explicitly passing the still-live `_AX` reproduces the target without changing the damage/explode DI paths. Focused and 153-owner aggregate replay are raw/map/ordered-relocation/OMF exact, reducing target-derived `MAIN_012_TEXT` ownership from 0x738 to **0x67F**.


v117 does **not** promote another exact owner. It resolves the immediate `MAIN_012_TEXT` frontier into three target-proved adjacent extents and preserves both positive and negative compiler evidence in `docs/reconstruction/TH04_MAIN_012_FRONTIER_V117.md`:

- `shots_add()` is the Ghidra-missed near function at map `0AAF:72A6`, load `0x11D96..0x11DC9`, runtime `0x21D96..0x21DC9`, file `0x13596..0x135C9` (**0x34 / 52 bytes**). Pinned TASM, raw decoding, and the next PROC close the extent; there are no MZ relocations. `src/main/player/shots_add.cpp` is now maintained `source-present` natural C++ using the real TH04 types. A bounded 24-header TC4J probe emits exactly 52 code bytes, and masking only the five unresolved 16-bit external data-symbol fixup words makes its instruction stream target-identical. This is deliberately **zero exactness credit**: `shot_velocity_set()` and `sub_11DE6` still follow it inside the monolithic assembler producer, so appending the C++ object would place it after those bodies and fail map/raw ownership.
- `shot_velocity_set()` is the next Ghidra-missed near function at map `0AAF:72DA`, load `0x11DCA..0x11DE5`, runtime `0x21DCA..0x21DE5`, file `0x135CA..0x135E5` (**0x1C / 28 bytes**), ending in `RET 4` with no MZ relocations. A natural Pascal-near stack-peek probe reaches the exact size and table-copy semantics, but TC4J emits `PUSH SI; MOV BX,SP` and `MOV BH,0` rather than target `MOV BX,SP; PUSH SI` and `XOR BH,BH`; ordinary `SPPoint` return forms add return shaping. The current ReC98 return type and authored-C++ versus original-style-assembly origin remain open.
- `sub_11DE6` remains the complete FAR **0x2C / 44-byte** function at map `0AAF:72F6`, load `0x11DE6..0x11E11`, Ghidra `2000:1DE6` / linear `0x21DE6..0x21E11`, file `0x135E6..0x13611`. The same-segment `NOP; PUSH CS; CALL near` tail is naturally explainable, but a matrix covering ordinary/register integer and byte counters, `for`/`while`/`do`, explicit `_CX`, `-k-`, `-G`, and CPU levels `-1/-2/-3` never emits the target `CX=9` plus `LOOP` scan. Do not bridge this mismatch with inline assembly, codestrings, target-byte emission, or padding.

Because v117 contains no exact promotion, no focused exact-unit cold replay and no new aggregate cold replay were run. The current accepted aggregate therefore remains `gptweb-v116-aggregate-001`; v117 evidence is boundary review plus bounded compiler/object probing only.


v118 takes the preceding `MAIN_012_TEXT` owner instead of forcing either unresolved v117 origin. `yuuka6_fg_render()` is now target-reviewed at map `0AAF:712A`, load `0x11C1A..0x11D95`, Ghidra `2000:1C1A`, file `0x1341A..0x13595` (**0x17C / 380 bytes**). Pinned TASM, one contiguous Ghidra body, raw `RET`, the immediate `shots_add()` entry, and ten FAR-call MZ relocations close the boundary. Ghidra reports zero direct callers because maintained `boss.cpp` installs this near public through `boss_fg_render_func`.

`src/main/boss/yuuka6_fg_render.cpp` is maintained natural C++ and is now recorded as `source-present`. A bounded TC4J probe first emitted 392 bytes when left/top were forced through `_SI`/`_DI`; replacing only those pseudo-register bindings with natural `register int` locals makes the compiler emit the six target `LEA` forms and produces exactly 380 code bytes. Candidate-versus-target has 45 two-byte mismatch runs, exactly matching all 45 OMF FIXUPP locations, and all other 290 bytes are target-identical. This is strong object/fixup-shape evidence, not exact acceptance. The target position precedes `shots_add`, `shot_velocity_set`, and `sub_11DE6` inside the still-monolithic assembler contribution, so there is no legal TLINK interleaving yet. No focused or aggregate exact replay was run for v118, and the accepted 153-owner aggregate remains `gptweb-v116-aggregate-001`.

v118 also corrects an overbroad intermediate interpretation of the v117 `sub_11DE6` result. A corrected scan of all 123 accepted exact MAIN C/C++ owner units finds 25 `LOOP` instructions in 13 units; **all 25** are TC4J compiler-generated CS switch-table scanners followed by indirect CS jump tables. Thus TC4J can emit `LOOP`, but the accepted natural-source corpus still contains no source-level DS-resident threshold scan matching `sub_11DE6`. The v117 ordinary/register loop matrix remains negative for that narrower shape and original assembly remains unproved. Same-target prologue-shape review likewise strengthens, but does not prove, an original-assembly hypothesis for `shot_velocity_set()`. Full evidence is in `docs/reconstruction/TH04_MAIN_012_YUUKA6_FG_V118.md`.

v119 resolves the v118 physical link-order blocker without laundering the unresolved residual into source recovery. `scripts/replay_th04_main_exact_units.py` now supports hash-bound replay-only scaffold extraction: the complete pinned scaffold, extracted `sub_11DE6` source span, checked-in wrapper template, symbol-only adaptations, generated source, and auxiliary TASM OMF are all receipted. `shot_velocity_set()` plus `sub_11DE6` remain unresolved and receive no accepted source/function credit. This plumbing allows natural `shots_add()` at `0AAF:72A6` and natural `yuuka6_fg_render()` at `0AAF:712A` to occupy their real target positions. Focused two-cold replays `gptweb-v119-shots-focused-001` and `gptweb-v119-yuuka-focused-001` pass, followed by the 155-owner aggregate `gptweb-v119-aggregate-001`; all declared raw slices, map extents, ordered relocations, OMF identities, and determinism gates pass. Full recovery and design evidence is in `docs/reconstruction/TH04_MAIN_012_FRONTIER_V119.md`.

v120 recovers the immediately preceding `sub_11B44` as maintained `yuuka6_entities_render()` at `0x21B44..0x21C19`, a complete **0xD6 / 214-byte** natural-C++ owner. Fresh Ghidra, pinned TASM, raw decode, and adjacency to exact `yuuka6_fg_render()` agree on the boundary. The function traverses 31 maintained 0x1A-byte chase-cross records and then interprets the final custom slot as the corrected 0x1A-byte safety-circle layout. A first natural candidate was two bytes short only at GRCG shutdown because `_outportb_` uses prohibited `__emit__`; ordinary `_DX = 0x7C; _AL = 0; outportb(_DX, _AL)` emits the target register-port sequence. Focused `gptweb-v120-yuuka-entities-focused-001` and 156-owner aggregate `gptweb-v120-yuuka-entities-aggregate-001` pass raw/map/ordered-relocation/OMF/determinism. Full evidence is in `docs/reconstruction/TH04_MAIN_012_YUUKA6_ENTITIES_V120.md`.

v121 recovers the immediately preceding `midboss_defeat_render()` at `0x21A9A..0x21B43`, a complete **0xAA / 170-byte** natural-C++ owner. Fresh Ghidra/TASM/raw agree on the boundary and the exact v120 owner begins at the next byte. The target-owned `angle_23212` byte stays in its existing assembler data contribution and is exposed only through the `_midboss_defeat_angle` alias. The natural source reaches the exact 170-byte TC4J skeleton after two narrowly diagnosed source-shape corrections: the capped increment must flow through live AL, and the `for` iteration expression must sequence `i++` before the angle update. Focused `gptweb-v121-midboss-defeat-focused-001` and 157-owner aggregate `gptweb-v121-midboss-defeat-aggregate-001` pass raw/map/ordered-relocation/OMF/determinism. Full evidence is in `docs/reconstruction/TH04_MAIN_012_MIDBOSS_DEFEAT_V121.md`.

v122 recovers the immediately preceding `orange_fg_render()` at `0x2196B..0x21A99`, a complete **0x12F / 303-byte** natural-C++ owner. The first compilable TC4J source already emits the exact instruction/control-flow skeleton; focused `gptweb-v122-orange-fg-focused-001` and 158-owner aggregate `gptweb-v122-orange-fg-aggregate-001` close all raw/map/seven-relocation/OMF/determinism gates. The same packet also corrects the adjacent boundary universe: no-Ghidra `kurumi_fg_render()` is target-proved as `0x21793..0x2196A`, while Ghidra's pseudo-function at `0x218B2` begins mid-instruction and remains excluded. Kurumi itself remains provisional/unreviewed with zero source or exactness credit. Full evidence is in `docs/reconstruction/TH04_MAIN_012_ORANGE_FG_V122.md`.

v123 converts that target-proved Kurumi extent into maintained `src/main/boss/kurumi_fg_render.cpp`, a complete **0x1D8 / 472-byte** exact natural-C++ owner. The first source was three bytes short because `if(flag != FREE)` let TC4J keep BX live across the branch; ordinary `if(flag == FREE) continue` reproduces the target reload and exact 472-byte skeleton. Focused `gptweb-v123-kurumi-fg-focused-001` and 159-owner aggregate `gptweb-v123-kurumi-fg-aggregate-001` pass raw/map/eight-relocation/OMF/determinism. The function reviewer admits `0x21793` only through the explicit no-Ghidra path; the mid-instruction `0x218B2` pseudo-function remains excluded. Full evidence is in `docs/reconstruction/TH04_MAIN_012_KURUMI_FG_V123.md`.

v124 follows the state consumed by that renderer into `MAIN_033_TEXT`: `kurumi_spawnrays_add(int,unsigned char)` at `0x28A14..0x28A78` and `kurumi_spawnrays_update()` at `0x28A79..0x28B67` form one exact **0x154 / 340-byte** natural-C++ producer. Because the target position lies inside the original monolithic assembler contribution, replay hash-extracts only the untouched `0x18B68..MAIN_033_TEXT end` suffix into an auxiliary TASM object. Focused `gptweb-v124-kurumi-spawnrays-focused-004` and 160-owner aggregate `gptweb-v124-kurumi-spawnrays-aggregate-001` close raw/map/four-relocation/OMF/determinism without granting the residual suffix reconstruction credit. Full evidence is in `docs/reconstruction/TH04_MAIN_033_KURUMI_SPAWNRAYS_V124.md`.

v125 continues through the first three adjacent Kurumi spawn-ray phase handlers at `0x28BE6..0x28DB5`, one exact **0x1D0 / 464-byte** natural-C++ producer. The first function closes a real boundary-analysis gap: Ghidra has the correct `0x28BE6..0x28C75` min/max but omits the 33-byte `phase_frame == 48` basic block; pinned TASM, both relocations, gap-free raw decode, exact natural ownership, and the next generated public close all 0x90 bytes through RET. Replay splits the v124 residual into a hash-bound `0x18B68..0x18BE5` prefix and `0x18DB6..MAIN_033_TEXT end` suffix around the natural C++ owner; both residual objects remain zero-credit plumbing. Focused `gptweb-v125-kurumi-phases-focused-001` and 161-owner aggregate `gptweb-v125-kurumi-phases-aggregate-001` close raw/map/seven-relocation/OMF/determinism. Full evidence is in `docs/reconstruction/TH04_MAIN_033_KURUMI_SPAWNRAY_PHASES_V125.md`.

v126 continues directly through the next four Kurumi late phase handlers at `0x28DB6..0x29059`, one exact **0x2A4 / 676-byte** natural-C++ producer. The first handler closes another real sparse-body gap: Ghidra has the correct `0x28DB6..0x28E42` min/max but omits ordinary code at `0x28E26..0x28E40`; pinned TASM, gap-free raw decode, the next generated public, and the exact owner close all 0x8D bytes through RET. A first TC4J probe was only three bytes long because direct branch stores duplicated a memory-immediate instruction; expressing the branch-selected byte through Borland `_AL` yields the target common-store shape and exact 676-byte/four-public object. Replay peels this owner from the v125 suffix, publishes only zero-byte semantic aliases for the unchanged reverse-orbit helper and turn-toggle BSS byte, and leaves the remaining suffix zero-credit. Focused `gptweb-v126-kurumi-late-phases-focused-001` and 162-owner aggregate `gptweb-v126-kurumi-late-phases-aggregate-001` close raw/map/seven-relocation/OMF/determinism. Full evidence is in `docs/reconstruction/TH04_MAIN_033_KURUMI_LATE_PHASES_V126.md`.

v127 peels the immediately following `kurumi_1905A` into maintained
`kurumi_bullet_stacks_phase()` at `0x2905A..0x2915C`, a complete **0x103 / 259-byte**
natural-C++ owner. The first successful source already has exact size/control flow;
two equivalent angle expressions must use `+ 0xA0` rather than `- 0x60` to emit the
target `ADD AL,A0h`. Final focused `gptweb-v127-kurumi-bullet-stacks-focused-003`
and 163-owner aggregate `gptweb-v127-kurumi-bullet-stacks-aggregate-001` close
raw/map/the sole relocation/OMF/determinism under the same final manifest. The same
packet corrects FAR `kurumi_update()` from Ghidra's 41-byte cross-linked body to a
target-proved 0x487-byte compiler owner containing 0x466 bytes of code plus one
alignment byte and three trailing jump tables; that dispatcher remains unreviewed
and zero-credit. Full evidence is in
`docs/reconstruction/TH04_MAIN_033_KURUMI_BULLET_STACKS_V127.md`.

v128 resolves the physical-TU evidence exposed by the first natural dispatcher replay.
Two adjacent 0x3F orbit helpers at `0x28B68` and `0x28BA7` replace the final
replay-only code between v124 and v125. Combining them with the maintained v124-v127
semantic functions and `kurumi_update()` produces one natural TC4J contribution at
`13A9:4F84`, size **0xBD0 / 3,024 bytes**, covering load `0x18A14..0x195E3`.
A diagnostic full-producer link first proves all 3,024 target bytes and all 28 ordered
MZ relocations; final focused `gptweb-v128-kurumi-full-focused-002` and 165-owner
aggregate `gptweb-v128-kurumi-full-aggregate-001` then prove the same physical
producer through two isolated cold builds. Function review counts only the 0x466-byte
executable `kurumi_update()` body through terminal RETF; its following 0x21 bytes of
alignment and three compiler jump tables remain exact byte-owner data. Full evidence is
in `docs/reconstruction/TH04_MAIN_033_KURUMI_PHYSICAL_PRODUCER_V128.md`.


The immediately preceding v114 experiment on the 0x60-byte `MAI_TEXT` scroll-update suffix was deliberately rolled back. Its best allowed natural-C++ shape made the first half and relocation order exact but remained seven bytes long because TC4 inserted an extra byte-to-word zero extension and a separate post-subtraction compare instead of preserving AX plus the `SUB` flags. Combining the compound subtraction with its condition clobbered AX through lvalue evaluation, while `SubpixelLength8::to_pixel()` moved the value through BL and was worse. This negative result is checked into evidence/knowledge; do not retry it without a new falsifiable compiler/source hypothesis.

Before accepting the Reimu batch, a target-first probe attempted the adjacent Mugetsu callbacks `0x2812A` and `0x2821E` as one 0x1EA-byte natural-C++ producer. `#pragma option -a` naturally reproduced both zero metadata bytes and both 33-word dense jump tables, but TC4J canonicalized each target `CMP; JGE; JMP ret0` gate into `CMP; JL ret0`, leaving a deterministic two-byte deficit per function. `if`/`goto`/loop/boolean forms and `-O-` probes did not solve it. The candidate was fully rolled back and is recorded as negative evidence; do not repeat it without a new falsifiable source/compiler hypothesis.

The maintained v89-v98 sources are under `src/main/boss/`; v99 adds `src/main/end/ending.cpp`, v100 adds `src/main/formats/map.cpp`, v101 adds `src/main/boss/gengetsu6_fg_render.cpp`, v102 adds `src/main/boss/mugetsu_gengetsu_bg_render.cpp`, v103 adds `src/main/enemy/enemies_invalidate.cpp`, v104 adds `src/main/formats/bb_txt.cpp`, v105 adds `src/main/boss/mugetsu_fg_render.cpp`, v106 adds `src/main/boss/gengetsu_bomb_inv_render.cpp`, v107 adds `src/main/boss/mugetsu_prefix.cpp`, v108 adds `src/main/boss/mugetsu_180bb.cpp`, v109 adds `src/main/boss/reimu_fg_render.cpp`, v110 adds `src/main/boss/reimu_orbs_render.cpp`, v111 adds `src/main/item/items_render.cpp`, v112 adds `src/main/bullet/render.cpp`, v113 adds `src/main/boss/yuuka6_bg_render.cpp`, v115 adds `src/main/stage_state_init.cpp`, and v116 adds `src/main/boss/elly_fg_render.cpp`. These accepted sources contain no target-byte emission, copied machine-code arrays, `#pragma codestring`, or inline assembly.

The v117/v118 source-present states remain useful historical evidence of the compiler-shape and layout blocker, but both maintained owners are superseded by v119 exact acceptance: `src/main/player/shots_add.cpp` owns 0x34 exact bytes and `src/main/boss/yuuka6_fg_render.cpp` owns 0x17C exact bytes. The replay-only residual that made legal interleaving possible is not product source and receives no reconstruction credit. v120 additionally makes `src/main/boss/yuuka6_entities_render.cpp` the exact owner of the preceding 0xD6 bytes. v121 adds `src/main/midboss/defeat_render.cpp` as the exact owner of the preceding 0xAA bytes while leaving the angle byte in its original data owner. v122 adds `src/main/boss/orange_fg_render.cpp` as the exact owner of the preceding 0x12F bytes. v123 adds `src/main/boss/kurumi_fg_render.cpp` as the exact owner of the preceding 0x1D8 bytes despite Ghidra missing its true entry. v124 adds `src/main/boss/kurumi_spawnrays.cpp` as one exact 0x154-byte owner containing the adjacent allocator and updater; the extracted `MAIN_033_TEXT` suffix remains replay plumbing only. v125 adds `src/main/boss/kurumi_spawnray_phases.cpp` as one exact 0x1D0-byte owner containing the first three adjacent spawn-ray phase handlers; replay now splits the untouched residual into pre/post seam objects around that natural owner, and both residuals remain zero-credit plumbing. v126 adds `src/main/boss/kurumi_late_phases.cpp` as the next exact 0x2A4-byte owner containing four adjacent late phase handlers; the remaining residual starts at `kurumi_1905A` and remains zero-credit plumbing. v127 adds `src/main/boss/kurumi_bullet_stacks.cpp` as the exact 0x103-byte owner at that former residual start. v128 adds the two 0x3F orbit helpers and `src/main/boss/kurumi_update.cpp`, then recovers the original physical translation-unit ownership by emitting the entire contiguous `0x18A14..0x195E3` Kurumi range from one natural `th04/kupdate.cpp` object; the remaining replay-only seams contain zero Kurumi function bytes and receive zero reconstruction credit.


v129 reviews the immediately following Orange phase-entry helper and corrects a
real sparse-Ghidra boundary. Fresh Ghidra has the correct `0x295E4..0x29685`
min/max but only 103/162 body bytes; pinned TASM and gap-free raw decode prove
the omitted 59-byte `phase_frame == 16` block is ordinary reachable code in the
same near PROC. The reviewed authored extent is load `0x195E4..0x19685`, file
`0x1ADE4..0x1AE85`, **0xA2 / 162 bytes**, with one MZ relocation at `0x19668`.
Maintained natural `src/main/boss/orange_phase_entry.cpp` reproduces the complete
instruction/control-flow shape; an ordinary shared `goto ret0` and Pascal source
argument order `(7, 6)` are required compiler-shape facts. v130 then runs the
formal focused two-cold replay `gptweb-v130-orange-phase-entry-focused-001` and
the complete 166-owner aggregate `gptweb-v130-orange-phase-entry-aggregate-001`.
Both close raw bytes, exact map `13A9:5B54` size `0xA2`, ordered relocation
`[0x19668]`, deterministic valid OMF, and no accepted-owner regression. Fresh
function review still sees only 103 Ghidra body bytes and therefore admits the
function only through the explicit reviewed sparse-body gate. Full evidence is
in `docs/reconstruction/TH04_MAIN_033_ORANGE_PHASE_ENTRY_V129.md`.

v131 continues through the next four contiguous Orange mode handlers at load
`0x19686..0x19877`, file `0x1AE86..0x1B077`, one natural **0x1F2 / 498-byte**
TC4J producer. Fresh attested Ghidra constructs complete contiguous near bodies
at image `0x29686`, `0x29720`, `0x297BB`, and `0x29814`; pinned TASM/raw review
closes each body at the following PROC boundary, while the residual `boss.mode`
dispatcher supplies the target-local direct calls that Ghidra misses. Natural
`src/main/boss/orange_mode_phases.cpp` reproduces all four publics after two
bounded source-shape corrections: explicit X/Y assignments avoid an unwanted
32-bit structure copy, and the aimed-cloud path preserves the target data flow
through `boss.angle`. Focused two-cold replay
`gptweb-v131-orange-mode-phases-focused-001` and the complete 167-owner aggregate
`gptweb-v131-orange-mode-phases-aggregate-001` both pass exact map placement at
`13A9:5BF6`, all 498 raw bytes, the ordered overlapping relocations at load
`0x19710`, `0x19747`, `0x197A3`, `0x19804`, and `0x19868`, valid deterministic
OMF, and no accepted-owner regression. Full evidence is in
`docs/reconstruction/TH04_MAIN_033_ORANGE_MODE_PHASES_V131.md`.

v132 audits the immediately following historical `orange_19878` boundary rather
than trusting Ghidra's 8-byte `0x29878..0x2987F` body. Pinned TASM, a gap-free
raw decode, the residual `boss.mode` dispatcher, terminal `RET` at `0x2998A`,
and the next PROC at `0x2998B` prove one near function at load
`0x19878..0x1998A`, file `0x1B078..0x1B18A`, size `0x113 / 275`. Natural
`src/main/boss/orange_phase_bounce_random.cpp` preserves the historical
`PlayfieldMotion::update_seg3()` AX-return idiom documented by the original
header; this removes the otherwise introduced local structure spill and yields
the exact TC4J instruction shape. Focused 104-owner replay
`gptweb-v132-orange-bounce-random-focused-002` and the required 168-owner
aggregate `gptweb-v132-orange-bounce-random-aggregate-002` both pass A/B cold
builds at `MAIN_033_TEXT 13A9:5DE8`, all 275 raw bytes, the sole ordered
overlapping MZ relocation at load `0x198AD`, valid deterministic TC86 OMF, and
no accepted-owner regression. Fresh function review admits this function only
through `reviewed_exact_extent`; the truncated Ghidra body receives no boundary
authority. Full evidence is in
`docs/reconstruction/TH04_MAIN_033_ORANGE_BOUNCE_RANDOM_V132.md`.

## Latest replay receipts

The latest exact owner passes repository focused two-cold replay at:

- `.analysis/reconstruction/exact-unit-replay/gptweb-v132-orange-bounce-random-focused-002/receipt.json`.

The complete default cohort then passes at:

- `.analysis/reconstruction/exact-unit-replay/gptweb-v132-orange-bounce-random-aggregate-002/receipt.json`
  — all 168 default owners, two isolated cold materializations.

The v119 shots/Yuuka foreground, v120 Yuuka entity-render, v121 midboss
defeat, v122 Orange, and v123 Kurumi foreground focused receipts remain valid
historical acceptance receipts for their respective owners.

The aggregate is the retained current private exact-unit replay baseline. Superseded
replay materializations and raw probe matrices may be pruned after their
commands, outcomes, and digests enter the checked-in ledgers; historical
`.analysis` paths are provenance rather than a cache-retention guarantee.

The 2026-09-08 retention pass kept all 275 replay `receipt.json` files,
compacted 273 superseded receipt-bearing runs, removed 88 receiptless run
directories, and retained the then-current full trees. Obsolete probe,
warm-build, one-off function-review, and isolated DOS-workspace caches were
also removed. This reduced the private `.analysis` tree from about 27 GiB to
1.6 GiB without removing targets, installed toolchains, Ghidra state, runtime
state, current boundary inputs, or the cold reconstruction seed.

The current 168-owner aggregate reports zero raw differences for every declared
owner, exact map placement, identical ordered overlapping MZ relocations, valid
deterministic OMF, and stable repository snapshots. The aggregate candidate
executable is deterministic across A/B with SHA-256
`b75b810982f384bdd2cfca76d64e8401e818712facaa3c6c9f3e705374e83b6a`.

The current private function-review artifact uses the v132 168-owner aggregate
map, retained target-bound metadata plus the fresh attested truncated Ghidra
observation at `0x29878`, pinned target bytes, and the configured reviewed-boundary
policy. It reports **295/297 exact functions (99.326599%)**, 148 automatic
acceptances, 147 manual reviewed acceptances, and zero strict rejections.
`orange_phase_bounce_random()` is a `reviewed_exact_extent` manual acceptance:
Ghidra contributes only its 8-byte provisional entry observation, while the exact
owner/TLINK public plus gap-free raw decode prove all 0x113 bytes through terminal
RET. The retained session report is
`.analysis/gpt-web/th04-main-20260912-v132/function-review-v132-current.json`.

Factory Truth-Kernel acceptance is independently closed for the v131 Orange
cohort. Commit `e818be5ad0bcfd81dd35db08d619f9448d75eeae` imported claim
`claim:unit:th04-main-orange-mode-phases-v131:owned-extent-exact`; controlled
`isolated-double-build` job `job:f977704d7e344484910a95498cd1bd1c` completed
with Factory receipt
`receipt:2d71f9eb7dcc6c2120e58ff30549417ce715daa0fb3978a29b2d802e6ee710c7`,
`receipt_verdict=pass`, and `acceptance_decision=accepted`. The accepted registry
identity reported by that job is
`registry:5dfdbfbb97c92c5f553d5032ab463da6181219a52196931522dcecb52b950088`.
This acceptance is scoped to the imported v131 `owned_extent_exact` claim; it
does not establish standalone product closure, runtime-storage identity, or a
runtime scenario. The repository v132 exact claim has passed its own focused and
aggregate Oracles but is not yet Factory-accepted in this checkpoint state; it
must first be committed, re-imported, independently replayed, and accepted by
the Factory registry.

## Remaining reviewed nonexact work

Two reviewed authored functions are nonexact:

1. `snd_load`: 4 bytes remain blocked by target-specific register/segment-save
   instruction encodings. Existing pure-C, TC4J flag, and TASM probes are
   recorded as negative results; do not repeat them without a new falsifiable
   source shape.
2. `enemy_bullet_template_push`: all 27 bytes remain blocked because natural
   TC4 struct-copy forms emit a different `REP MOVSW` setup order. ReC98's
   inline-assembly shortcut is not acceptable evidence.

`dialog_op` and `dialog_run` have maintained source and exact code bytes, but
remain outside the reviewed exact denominator because their ordered MZ
relocation sequences do not match. Restoring the lower historical TU split was
already tested and does not solve those two functions.

## Next target-first queue

Do not resume from the old prose-only MAIN frontier. Query
`config/th04_function_boundaries.csv` for `work_queue=reconstruct` and
`accepted_state=unreviewed`, then select one coherent artifact-local unit.
There are 435 such rows. Prefer `boundary_state=corroborated`; the remaining
provisional rows need focused target control-flow, return/shared-tail,
jump-table, alignment, and adjacent ownership review before source work.

The largest remaining class is 242 MAIN entries currently represented by
target-derived assembly. That label means “likely authored game code awaiting
natural source,” not “original handwritten ASM.” OP has 94 unreviewed authored
candidates, MAINE 72, and ZUN 13. Cross-game source paths in MAP evidence are
corroboration only and must become TH04-local or proved `src/shared/` source.

The current MAIN ledger still represents all 434 target-derived TASM `PROC` starts: **434/434 are represented and zero starts are missing**. Of those TASM starts, 165 are exact, 241 remain unreviewed, one is blocked, and 27 are library-excluded; no non-library TASM `PROC` is silently excluded. This does not exhaust boundary discovery: MAIN still has 256 unreviewed authored candidates. Continue target-first review of provisional/high-risk, no-Ghidra, and sparse/cross-linked rows rather than treating Ghidra or the TASM-visible inventory as a complete function universe. Continue target-first review of those rows rather than treating Ghidra or the TASM-visible inventory as a complete function universe.

The immediate `MAIN_012_TEXT` physical layout blocker is closed for the exact Yuuka6/shots owners, but the semantic origin/code-generation seam remains unresolved at `shot_velocity_set()` / `sub_11DE6`. Do not retry `sub_11DE6` with another ordinary source-level loop merely because TC4J is proved capable of generating `LOOP`: every accepted natural-source `LOOP` currently comes from compiler-generated CS switch-table scanning, not a DS threshold loop. A new probe must explain that distinction. `shot_velocity_set()` still requires either a genuinely new ABI/compiler source shape that explains `MOV BX,SP` before `PUSH SI` plus `XOR BH,BH`, or independent evidence for original-style assembly. Replay-only residual extraction is not such evidence.

The first concrete continuation is now historical `orange_1998B` at load
`0x1998B` / file `0x1B18B` / Ghidra image `0x2998B`, immediately after the v132
owner. Preliminary target/TASM review bounds the next historical PROC at
`0x1998B..0x19AA2` (`0x118 / 280` bytes) before FAR `@orange_update$qv` at load
`0x19AA3`, with an overlapping MZ relocation at load `0x199E6`. Fresh Ghidra is
not trustworthy here: its function entry is cross-linked/sparse far outside the
historical extent. Re-establish the complete 0x118 raw control flow, return and
shared-tail/data ownership, callers/callees, relocation ownership, and its
physical relationship to FAR `orange_update()` before writing source. Treat
`orange_1998B` plus the FAR dispatcher as one structural cohort until evidence
proves the seam; this continues the same MAIN_033 producer boundary campaign
rather than returning to easy isolated helpers.

Re-screening confirmed that several tempting ReC98 candidate-C++ paths are not acceptable drop-ins: checkerboard, TH03 vector, `item_splashes_init`, and `carpet_lighting_put_new` depend on inline ASM and/or `#pragma codestring` for instruction shape. Keep them as routing evidence until an allowed source form is proved. Ghidra also still misses CIRCLE_TEXT boundaries including `randring1_next16`, `randring1_next16_mod`, and the near/far null functions; MAP/TASM keeps those candidates visible.

Do not return to retired `exact/`, `partial/`, or `modules/` source layouts.
Product source follows `src/main/`, `src/op/`, `src/maine/`, `src/zun/`, and
proved `src/shared/` ownership with semantic subsystem directories.

## Build status

The current repository 168-owner exact-unit cohort compiles and links reproducibly through the
pinned ReC98 cold-replay scaffold. This is a strict exactness Oracle, not a
standalone TH04 build.

The repository still lacks many TH04 translation units, a fully localized
ABI/header surface, and a complete TH04-owned link graph. Unlocalized
declarations are explicitly quarantined behind one-line
`compat/rec98/<upstream-path>` forwarders. Do not bulk-copy ReC98 or other game
trees to hide this gap. Recover declarations into the owning TH04 subsystem or
a proved `src/shared/` surface, attest affected owners, then remove the matching
forwarder.

## Reproduction commands

Run before target-dependent work:

```bash
python3 scripts/preflight.py
python3 scripts/status.py
python3 scripts/boundary_review/validate_function_boundary_ledger.py
```

The complete private inventory refresh order and its DIET/Ghidra/MAP/TASM
limitations are in `docs/BOUNDARY_REVIEW.md`. Reusable scripts are grouped
under `scripts/boundary_review/`; generated payloads, listings, Ghidra exports,
and databases remain ignored.

Replay one owner or the complete accepted cohort:

```bash
python3 scripts/replay_th04_main_exact_units.py --unit UNIT_ID --run-id RUN_ID
python3 scripts/replay_th04_main_exact_units.py --run-id RUN_ID
```

Regenerate progress and finish a session with:

```bash
python3 scripts/progress.py
python3 scripts/ci.py
git diff --check
```

The compact acceptance contract and unresolved producer constraints remain in
`docs/reconstruction/TH04_MAIN_EXACT_BATCH.md`,
`docs/reconstruction/TH04_MAIN_FIXUP_CODEGEN_PROBES.md`, and
`config/knowledge.csv`. Whole-artifact boundary results are in
`docs/BOUNDARY_REVIEW.md` and `config/th04_function_boundaries.csv`.
