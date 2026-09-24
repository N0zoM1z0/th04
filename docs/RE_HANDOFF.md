# TH04 reconstruction handoff

Updated 2026-09-24. This is the concise resume index; live counts come from
`config/units.csv`, `config/th04_main_authored_functions.csv`,
`config/th04_function_boundaries.csv`,
`config/th04_decoded_function_acceptance.csv`, and `python3 scripts/status.py`.
The roadmap is [RE_ROADMAP.md](RE_ROADMAP.md); bounded evidence notes are
routed by [reconstruction/README.md](reconstruction/README.md).

## Resume checks

```sh
git status --short
python3 scripts/preflight.py
python3 scripts/status.py
python3 scripts/compat_audit.py
```

Current target identity is `candidate-local-attested`: size, SHA-256, MZ
structure, tracking, function-boundary ledgers, and decoded acceptance validate,
but this is not proof of an official pristine release. Re-attest the active
disassembler database to target/header/entry/relocations/load digest/sampled
bytes before any new target observation. Keep one writable Borland session.

## Current non-MAIN state

| Artifact | Candidate boundaries: reviewed / corroborated / provisional | Function exact | Pending / blocked | Decoded source-owner bytes |
| --- | ---: | ---: | ---: | ---: |
| OP.EXE | 51 / 34 / 8 | 48 | 45 / 0 | 4,210 |
| MAINE.EXE | 39 / 28 / 5 | 34 | 38 / 0 | 2,972 |
| ZUN.COM | 13 / 0 / 0 | 0 | 11 / 2 | 404 |

OP's 4,210 source-owner bytes include two source-present but nonexact SCORE
codec candidates (274 bytes); 3,936 bytes are in the 48 accepted exact
functions. MAINE has 34 decoded-function exact functions (2,783 bytes), plus
two source-present/nonexact SCORE codec candidates (`scoredat_decode` 88 bytes
and `scoredat_encode` 101 bytes); total decoded source-owner bytes are 2,972.
These are decoded-function extents, not packed-file byte totals. No honest
packed-file denominator exists yet for OP, MAINE, or ZUN. MAIN is not on the
active reconstruction path: its 492/495
accepted authored functions and 27 file-backed authored bytes remain an
evidence-triggered side lane.

## Latest verified cohort: OP setup single-line renderer

v634 reconstructs the 122-byte `singleline(int,int)` helper at payload
`0xB5E2` (`1A74:0EA2`) inside `OP_SETUP_TEXT`. Fresh target review closes
one contiguous near Pascal body with two callers and two callees. Raw target
operands plus the pinned MAP bind `_window.w` at `0F34:2B48`,
`EGC_COPY_RECT_1_TO_0_16` at `0DA1:0968`, and `SUPER_PUT` at
`0000:2D5A`. The function restores a 32-pixel-high strip, uses paired
left/middle/right tile IDs 5/6, 1/3, and 8/7, advances columns by 16 pixels,
and terminates with Pascal `RET 4`.

Maintained natural source is `src/op/setup/singleline.cpp`. Standalone TC86
produces exactly 122 CODE bytes; every pre-link byte difference is confined to
the same nine ordinary OMF fixup sites expected from two window references,
one EGC FAR call, and six SUPER_PUT FAR calls. Focused A/B cold replay
raw-matches the complete function and the full `0x5A6`-byte `OP_SETUP_TEXT`
producer while preserving the retained OP program image and all 804 ordered
relocations. The v635 complete OP aggregate passes 48/48 registered decoded
functions raw-zero:
`.analysis/reconstruction/probes/v635-op-singleline-aggregate-001/receipt.json`,
SHA-256 `c7bd5344e2deffc1fa4a32429f26916138063c39112c863668c1d31e747990e1`.
This is decoded-function exactness only; no DIET-packed offset or whole-OP
exactness is claimed.

## Prior verified cohort: OP setup window-dropdown renderer

v632 reconstructs the 122-byte `window_dropdown_put(int,int)` helper at
payload `0xB49F` (`1A74:0D5F`) inside `OP_SETUP_TEXT`. Fresh target
review closes one contiguous near Pascal body with one caller and two callees.
Raw target operands plus the pinned MAP bind `_window.w` at `0F34:2B48`,
`EGC_COPY_RECT_1_TO_0_16` at `0DA1:0968`, and `SUPER_PUT` at
`0000:2D5A`. The paired left/middle/right tile IDs are 2/6, 0/3, and 4/7;
the function terminates with Pascal `RET 4`.

Maintained natural source is `src/op/setup/window_dropdown_put.cpp`. A
standalone TC86 probe produces exactly 122 CODE bytes with all differences
confined to the nine expected OMF fixup sites (two window references, one EGC
FAR call, six SUPER_PUT FAR calls). Focused A/B cold replay then raw-matches
the complete function and the full `0x5A6`-byte `OP_SETUP_TEXT` producer,
preserving the retained OP program image and all 804 ordered relocations. An
independent focused replay and a second aggregate replay reproduce the result.
The v633 complete OP aggregate passes 47/47 registered decoded functions
raw-zero:
`.analysis/reconstruction/probes/v633-op-window-dropdown-aggregate-001/receipt.json`,
SHA-256 `ce4e061eaa6e8f2ca4a54552b436dd3cbbdd7da8c6a5890d1512e2950dcd0c3b`.
This is decoded-function exactness only; no DIET-packed offset or whole-OP
exactness is claimed.

## Prior verified cohort: OP setup dropdown animation

v630 reconstructs the 112-byte `dropdown(int,int)` helper at payload `0xB572`
(`1A74:0E32`) inside `OP_SETUP_TEXT`. Fresh target review closes one contiguous
near Pascal body with two callers and three callees. Raw target operands plus
the pinned MAP bind `_window.w` / `_window.h`, `SUPER_PUT`,
`window_dropdown_put`, and `frame_delay`; the top-row pattern IDs are 5/1/8 and
the function terminates with Pascal `RET 4`. The maintained object independently
retains the `+2` structure-field fixup for `window.h`, matching target operands
`0x2B48` / `0x2B4A`.

Maintained natural source is `src/op/setup/dropdown.cpp`. Focused A/B cold
replay reproduces all 112 function bytes and the complete `0x5A6`-byte
`OP_SETUP_TEXT` producer while preserving grouped link-relevant OMF, the
retained OP program image, and all 804 ordered relocations. An independent
focused recheck also raw-matched the complete function. The v631 complete OP
aggregate passes 46/46 registered decoded functions raw-zero:
`.analysis/reconstruction/probes/v631-op-dropdown-aggregate-001/receipt.json`,
SHA-256 `c99b4c50eb09fd1f60d48b268c4f682c850a856ebaf5269adc96cfb1d04e0b78`.
This is decoded-function exactness only; no DIET-packed offset or whole-OP
exactness is claimed.

## Prior verified cohort: OP setup window-rollup renderer

v628 reconstructs the 89-byte `window_rollup_put(int,int)` helper at payload
`0xB519` (`1A74:0DD9`) inside `OP_SETUP_TEXT`. Fresh target review closes one
contiguous near Pascal body with one caller and two callees. Raw operands plus
the pinned MAP bind `_window.w` at `0F34:2B48`, `EGC_COPY_RECT_1_TO_0_16` at
`0DA1:0968`, and `SUPER_PUT` at `0000:2D5A`. The target independently fixes
16-pixel window tiles, the 8-pixel drop step, bottom pattern IDs 6/3/7, and
terminal `RET 4`.

Maintained natural source is `src/op/setup/window_rollup_put.cpp`. Two separate
focused A/B cold replays reproduce all 89 function bytes and the complete
`0x5A6`-byte `OP_SETUP_TEXT` producer while preserving grouped link-relevant OMF,
the full retained OP program image, and all 804 ordered relocations. The v629
complete OP aggregate passes 45/45 registered decoded functions raw-zero:
`.analysis/reconstruction/probes/v629-op-window-rollup-aggregate-001/receipt.json`,
SHA-256 `e025be7d369c913df35a18339145781e6a4e0e9ab9ef1a54311df04301a50fcf`.
This is decoded-function exactness only; no DIET-packed offset or whole-OP
exactness is claimed.

## Prior verified cohort: OP SE choice renderer

v626 reconstructs the 81-byte `se_choice_put(int,unsigned int)` renderer at
payload `0xB6E7` (`1A74:0FA7`) inside `OP_SETUP_TEXT`. Ghidra closes one
contiguous body with one caller and one callee. Fresh target/codegen review
corrected an initially tempting but wrong enum assumption: the actual ABI is
`SND_SE_OFF=0`, `SND_SE_FM=1`, `SND_SE_BEEP=2`. Target control flow and pinned
`op_setup.obj` data independently bind these modes to linked DGROUP strings at
`0x0E08` / `0x0DE6` / `0x0DF7`, rendered at vertical offsets +32 / +0 / +16
from `CHOICE_TOP=136`; `CHOICE_LEFT=48`. The sole FAR call is
`GRAPH_PUTSA_FX` at `0DA1:04A4`.

Maintained natural source is `src/op/setup/se_choice_put.cpp`. Focused A/B cold
replay raw-matches all 81 bytes and preserves the full `OP_SETUP_TEXT` producer,
grouped link-relevant OMF, full OP program image, and all 804 ordered
relocations. The v627 complete OP aggregate passes 44/44 registered decoded
functions raw-zero:
`.analysis/reconstruction/probes/v627-op-se-choice-aggregate-001/receipt.json`,
SHA-256 `2df7cc741775a01c97d950deb71003d92ac2da8327a3c9e0f2214941ab1db419`.
This is decoded-function exactness only; no DIET-packed offset or whole-OP
exactness is claimed.

## Prior verified cohort: OP BGM choice renderer

v624 reconstructs the 79-byte `bgm_choice_put(int,unsigned int)` renderer at
payload `0xB698` (`1A74:0F58`) inside `OP_SETUP_TEXT`. Ghidra closes one
contiguous body with one caller and one callee. Target mode values 0/1/2 select
three linked DGROUP strings at `0x0DD5` / `0x0DC4` / `0x0DB3` and place them
at vertical offsets +32 / +16 / +0 from `CHOICE_TOP=136`; `CHOICE_LEFT=48`.
The sole FAR call is `GRAPH_PUTSA_FX` at `0DA1:04A4`. Pinned
`op_setup.obj` data independently confirms that those linked addresses hold
the three 16-byte Shift-JIS BGM-choice strings.

Maintained natural source is `src/op/setup/bgm_choice_put.cpp`. Focused A/B
cold replay raw-matches the complete 79-byte body and preserves the full
`OP_SETUP_TEXT` producer plus grouped choice-string OMF. The v625 complete OP
aggregate passes 43/43 registered decoded functions raw-zero:
`.analysis/reconstruction/probes/v625-op-bgm-choice-aggregate-001/receipt.json`,
SHA-256 `58d6ace11ddd208399ca180e987eb945416c2b47b921412341b142f579e72f91`.
All 804 ordered target relocations remain preserved. This is decoded-function
exactness only; no DIET-packed offset or whole-OP exactness is claimed.

## Earlier verified cohort: OP music-room comment transition wrapper

v622 reconstructs the 72-byte `cmt_load_unput_and_put_both_animate(int)`
wrapper at payload `0xC36F` (`1A74:1C2F`) inside `OP_MUSIC_TEXT`. Ghidra
closes one contiguous body with one caller and seven callees. Raw target
control flow independently binds `_cmt_shown_initial` and the calls to
`cmt_unput_both_animate`, `cmt_load`, `nopoly_B_put`,
`BGIMAGE_PUT_RECT_16`, `cmt_fadein_both_animate`, `cmt_put`, and
`music_update_render_and_flip`. The target also fixes the background restore
rectangle to (320,64,320,320) and the Pascal `RET 2` argument cleanup.

Maintained natural source is
`src/op/music/cmt_load_unput_and_put_both_animate.cpp` with the function body
in the matching `.inl`. Standalone TC86 output matches the complete 72-byte
instruction shape with eleven word fixups and one FAR-call fixup. The grouped
link-relevant OMF remains stable and the replay preserves the complete
`0x6A5`-byte `OP_MUSIC_TEXT` producer, full OP program image, and all 804
ordered relocations. The v623 complete OP aggregate passes 42/42 registered
decoded functions raw-zero:
`.analysis/reconstruction/probes/v623-op-cmt-transition-aggregate-001/receipt.json`,
SHA-256 `0fbe738d3811d014ad8dba3b448c74ed1afac73f985865ef4ae86825a9235ac3`.
This is decoded-function exactness only; no DIET-packed offset or whole-OP
exactness is claimed.

## Prior verified cohort: OP music-room comment loader

v620 reconstructs the 73-byte `cmt_load(int)` helper at payload `0xC27B`
(`1A74:1B3B`) inside `OP_MUSIC_TEXT`. Ghidra closes one contiguous body with
one caller and four callees. Raw target operands independently bind the four
file calls (`FILE_ROPEN`, `FILE_SEEK`, `FILE_READ`, `FILE_CLOSE`), `_cmt` at
`0F34:3A92`, total comment storage size `0x320`, 20 lines of 40 bytes, and
the byte-38 terminator written to every line. The filename operand is DGROUP
offset `0x132E` inside the pinned `th04/op_music.cpp` data contribution; the
restored target contains a unique `_MUSIC.TXT` literal at the linked data
location. This is support for the operand identity, not a source-authority
claim.

Maintained natural source is `src/op/music/cmt_load.cpp` with the function body
in `src/op/music/cmt_load.inl`. The standalone producer is compiled against
the maintained runtime ABI and matches the complete 73-byte instruction shape
with exactly seven expected OMF fixups: filename/data references plus four FAR
file calls. The grouped replay preserves the complete `0x6A5`-byte
`OP_MUSIC_TEXT` producer, the full OP program image, and all 804 ordered
relocations. The v621 complete OP aggregate passes 41/41 registered decoded
functions raw-zero:
`.analysis/reconstruction/probes/v621-op-cmt-load-aggregate-001/receipt.json`,
SHA-256 `e75791c0380f5230076c3174cd90ab3642b0d9a530123bc8259aed883e42e062`.
This is decoded-function exactness only; no DIET-packed offset or whole-OP
exactness is claimed.

## Prior verified cohort: OP music-room comment renderer

v618 reconstructs the 74-byte `cmt_put()` helper at payload `0xC2C4`
(`1A74:1B84`) inside `OP_MUSIC_TEXT`. Ghidra closes one contiguous body with
two callers and one callee. Raw target operands independently bind `_cmt` at
`0F34:3A92` and both FAR calls to `GRAPH_PUTSA_FX` at `0DA1:04A4`. The target
also fixes the 40-byte comment-line stride, 20 total lines, title coordinates
(320,64), comment x=320, 16-pixel row height, color 7, and suppression of lines
whose first byte is ';'.

Maintained natural source is `src/op/music/cmt_put.cpp` with the function body
in `src/op/music/cmt_put.inl`. Standalone TC86 output matches the complete
74-byte instruction shape with exactly five expected OMF fixups: three `_cmt`
offset references and two FAR-call references. The grouped replay preserves
the complete `0x6A5`-byte `OP_MUSIC_TEXT` producer, the full OP program image,
and all 804 ordered relocations. The v619 complete OP aggregate passes 40/40
registered decoded functions raw-zero:
`.analysis/reconstruction/probes/v619-op-cmt-put-aggregate-001/receipt.json`,
SHA-256 `56ad081c2eee0dcbfcaeab442547a124a760fbc9918f08c15aa090da5817de7f`.
This is decoded-function exactness only; no DIET-packed offset or whole-OP
exactness is claimed.

## Prior verified cohort: MAINE ending script-name animation

v616 reconstructs the 69-byte `end_animate()` helper at payload `0xA0BD`
(`1A05:006D`) inside `MAINE_E_TEXT`. Ghidra closes one contiguous body with
one caller and three callees. Raw target operands independently bind
`_resident` at `0E53:0E9E`; the accessed resident offsets `+0x12`, `+0x19`,
and `+0x25` match the maintained `playchar_ascii`, `shottype`, and
`end_type_ascii` layout. The target writes those bytes into the ending-script
far string at indices 3/4/5, adds ASCII '0' to the shot type, then near-calls
`cutscene_script_load`, `cutscene_animate`, and `cutscene_script_free`.

Maintained natural source is `src/maine/end/end_animate.cpp` with the function
body in `src/maine/end/end_animate.inl`. Standalone TC86 output matches the
complete 69-byte instruction shape. Its OMF has one static-data initializer
fixup for the script pointer plus ten code fixups; the grouped link-relevant
OMF is exactly the v489 baseline, so both the static script data and function
code ownership are preserved. The v617 complete MAINE aggregate passes 34/34
registered decoded functions raw-zero:
`.analysis/reconstruction/probes/v617-maine-end-animate-aggregate-001/receipt.json`,
SHA-256 `04c97930c16a38c77b093dc4a302dd0d5da712f3758ae1c342ecc8df07f332aa`.
All 559 ordered target relocations remain preserved. This is decoded-function
exactness only; no DIET-packed offset or whole-MAINE exactness is claimed.

## Prior verified cohort: MAINE cutscene script loader

v614 reconstructs the 63-byte `cutscene_script_load(const char far*)` helper
at payload `0xA292` (`1A05:0242`), the first function in `CUTSCENE_TEXT`.
Ghidra closes one contiguous body with one caller and five callees. Raw target
operands plus the MAP independently bind the near call to
`cutscene_script_free`, FAR calls to `FILE_ROPEN`, `FILE_SIZE`, `FILE_READ`,
and `FILE_CLOSE`, `_script` at `0E53:1F48`, and `_script_p` at
`0E53:3F48`. The target also fixes the failure return to 1 and success return
to 0.

Maintained natural source is `src/maine/cutscene/script_load.cpp` with the
function body in `src/maine/cutscene/script_load.inl`. Standalone TC86 output
matches the complete 63-byte instruction shape with exactly eight expected OMF
fixups: one near call, four FAR file calls, and three script/script-pointer
references. The grouped replay preserves the complete `0xC3E`-byte
`CUTSCENE_TEXT` producer, the retained MAINE program image, and all 559 ordered
relocations. The v615 complete MAINE aggregate passes 33/33 registered decoded
functions raw-zero:
`.analysis/reconstruction/probes/v615-maine-script-load-aggregate-001/receipt.json`,
SHA-256 `2dd8ba4704d75c0dc3e13804548e4efbe5fb5338454f4caf5f4838d3c0561f34`.
This is decoded-function exactness only; no DIET-packed offset or whole-MAINE
exactness is claimed.

## Prior verified cohort: OP setup rollup helper

v612 reconstructs the 60-byte `rollup(int,int)` helper at payload `0xB65C`
(`1A74:0F1C`) inside `OP_SETUP_TEXT`. Ghidra closes one contiguous body with
two callers and two callees. MAP places `_window` at `0F34:2B48`, while the
target reads `0x2B4A` twice, independently identifying the second 16-bit
field as `window.h`. The target arithmetic also fixes `MSWIN_H=16`,
`DROP_FRAMES_PER_TILE=2`, and `DROP_SPEED=8`; its calls resolve to
`window_rollup_put` and FAR `frame_delay`.

Maintained natural source is `src/op/setup/rollup.cpp` with the function body
in `src/op/setup/rollup.inl`. Standalone TC86 output matches the complete
60-byte instruction shape with exactly four expected OMF fixups: two
`_window` references, one near call, and one FAR call. The grouped replay
preserves the complete `0x5A6`-byte `OP_SETUP_TEXT` producer, the retained OP
program image, and all 804 ordered relocations. The v613 complete OP aggregate
passes 39/39 registered decoded functions raw-zero:
`.analysis/reconstruction/probes/v613-op-rollup-aggregate-001/receipt.json`,
SHA-256 `6bc6488bf542c265b08f18b35f67d6bbb7f5c1cc1e707c250bb9d0571e40e3c3`.
This is decoded-function exactness only; no DIET-packed offset or whole-OP
exactness is claimed.

## Prior verified cohort: OP music update/render/page-flip helper

v610 reconstructs the 55-byte `music_update_render_and_flip()` helper at
payload `0xC244` (`1A74:1B04`) inside `OP_MUSIC_TEXT`. Ghidra closes one
contiguous body with four callers and four callees. Raw target operands and
MAP evidence independently bind `nopoly_b_put`, `GRCG_SETCOLOR`,
`polygons_update_and_render`, `_music_page_accessed`, and `frame_delay_2`;
the target also fixes the inline page/GRCG port writes at 0x7C, 0xA4, and
0xA6.

Maintained natural source is
`src/op/music/music_update_render_and_flip.cpp`. Standalone TC86 output matches
the complete target instruction shape with seven expected OMF fixups: two near
calls, two FAR calls, and three references to `_music_page_accessed`. The
grouped replay preserves the complete `0x6A5`-byte `OP_MUSIC_TEXT` producer,
the retained OP program image, and all 804 ordered relocations. The v611
complete OP aggregate passes 38/38 registered decoded functions raw-zero:
`.analysis/reconstruction/probes/v611-op-music-update-aggregate-001/receipt.json`,
SHA-256 `07402645c29b2f907af0d8975c4dda590b102fa06f68c1d43da459878a8d065d`.
This is decoded-function exactness only; no DIET-packed offset or whole-OP
exactness is claimed.

## Prior verified cohort: MAINE game exit-and-exec wrapper

v608 reconstructs the 51-byte `game_exit_and_exec(char far*)` wrapper at
payload `0xA08A` (`1A05:003A`) inside `MAINE_E_TEXT`. Ghidra closes one
contiguous body with one caller and six callees. Raw target operands plus the
MAP independently bind the sequence to `CDG_FREE_ALL`, `GRAPH_HIDE`,
`TEXT_CLEAR`, `GAIJI_RESTORE`, `game_exit`, and `_execl`; the `_execl` call
receives the same far filename pointer twice, followed by a null terminator.

Maintained natural source is `src/maine/core/game_exit_and_exec.cpp`.
Standalone TC86 output contains exactly six expected FAR-call fixups. The
grouped replay preserves the complete `0x239`-byte `MAINE_E_TEXT` producer,
the retained MAINE program image, and all 559 ordered relocations. The v609
complete MAINE aggregate passes 32/32 registered decoded functions raw-zero:
`.analysis/reconstruction/probes/v609-maine-game-exec-aggregate-001/receipt.json`,
SHA-256 `317d150c83eb9b930e36143df4831e86c2ec54e0fc8e3fbf2c153bdb175253d4`.
This is decoded-function exactness only; no DIET-packed offset or whole-MAINE
exactness is claimed.

## Prior verified cohort: OP nopoly B-plane snapshot

v606 reconstructs the 49-byte `nopoly_B_snap()` leaf at payload `0xBF68`
(`1A74:1828`). Ghidra closes one contiguous body with one caller and one
callee. Target operands independently bind the `0x7D00` allocation to
`HMEM_ALLOCBYTE` at `0000:2752`, the destination segment to `_nopoly_B` at
`0F34:3A80`, and the source far pointer to `_VRAM_PLANE_B` at `0F34:22DA`.
The loop advances by four bytes and, importantly, the target uses a signed
`JL` comparison; declaring the loop variable unsigned naturally produced
`JB` and was rejected before the maintained source was finalized.

Maintained natural source is `src/op/music/nopoly_snap.cpp`. Standalone TC86
output matches the complete 49-byte instruction shape with exactly four
expected OMF fixups: `HMEM_ALLOCBYTE`, two `_nopoly_B` references, and
`_VRAM_PLANE_B`. The grouped replay preserves the complete `0x6A5`-byte
`OP_MUSIC_TEXT` producer and the retained OP program image. The v607 complete
OP aggregate passes 37/37 registered decoded functions raw-zero:
`.analysis/reconstruction/probes/v607-op-nopoly-snap-aggregate-001/receipt.json`,
SHA-256 `8940dc51ae42b5cbfafd18a8d6fe965ce393b6dff752492eff2435feb3aae777`.
All 804 ordered target relocations remain preserved. This is decoded-function
exactness only; no DIET-packed offset or whole-OP exactness is claimed.

## Prior verified cohort: MAINE resident-pointer CFG loader

v604 reconstructs the 49-byte `cfg_load_resident_ptr()` leaf at payload
`0xA059` (`1A05:0009`). Ghidra closes one contiguous body with one caller and
three callees. The target itself fixes the file flow: open `MIKO.CFG`, read
exactly 10 bytes into the local CFG structure, close the file, load the
`resident` segment field, store that segment in `_resident+2`, clear the
`_resident` offset word, and return the segment.

Maintained natural source is `src/maine/core/cfg_load_resident_ptr.cpp`.
Standalone TC86 output has exactly six expected fixups: the CFG filename,
three FAR file calls, and two `_resident` address references. The grouped replay
preserves the complete `0x239`-byte `MAINE_E_TEXT` producer and the retained
MAINE program image. The v605 complete MAINE aggregate passes 31/31 registered
decoded functions raw-zero:
`.analysis/reconstruction/probes/v605-maine-cfg-resident-aggregate-001/receipt.json`,
SHA-256 `885d28b9be1c3bd2bbb6a960cef52daca288fae7a336627de57ac8c014bbb8ed`.
All 559 ordered target relocations remain preserved. This is decoded-function
exactness only; no DIET-packed offset or whole-MAINE exactness is claimed.

## Prior verified cohort: OP main CDG loader

v602 reconstructs the 49-byte `main_cdg_load()` leaf at payload `0xCC97`
(`1A74:2557`). Ghidra closes one contiguous body with one caller and two
distinct callees. Raw target call blocks independently fix slots 0/10/35/40;
the target DS:offset pointers resolve to `sft1.cd2`, `sft2.cd2`, `car.cd2`,
and `sl.cd2`. The first three calls target `CDG_LOAD_ALL` at `0DA1:0C2E`;
the final call targets `CDG_LOAD_ALL_NOALPHA` at `0DA1:0C28`.

Maintained natural source is `src/op/title/main_cdg_load.cpp`. Standalone TC86
output is the complete 49-byte call sequence with exactly eight OMF fixups:
four string-address references and four FAR-call operands. The grouped replay
preserves the complete `0x2C7`-byte `OP_TITLE_TEXT` producer raw-equal. The
v603 complete OP aggregate passes 36/36 registered decoded functions raw-zero:
`.analysis/reconstruction/probes/v603-op-main-cdg-load-aggregate-001/receipt.json`,
SHA-256 `56c20bb521cc0e72556db6d3f9ef6807a7679ebbb1bcf61108f195edd80bb524`.
All 804 ordered target relocations remain preserved. This is decoded-function
exactness only; no DIET-packed offset or whole-OP exactness is claimed.

## Prior verified cohort: OP comment fade-in animation

v600 reconstructs the 49-byte `cmt_fadein_both_animate()` leaf at payload
`0xC30E` (`1A74:1BCE`). Ghidra closes one contiguous body with one caller and
two callees. Raw target control flow fixes the effect loop to 4..7, alternates
`cmt_put` and `music_update_render_and_flip`, then stores final effect 2 and
executes the closing put/update/put sequence.

Maintained natural source is `src/op/music/cmt_fadein_both_animate.cpp`.
Standalone TC86 output has the complete target control-flow shape and exactly
nine word fixups across the two global effect stores and seven near-call
operands. The grouped replay preserves the complete `0x6A5`-byte
`OP_MUSIC_TEXT` producer raw-equal. The v601 complete OP aggregate passes
35/35 registered decoded functions raw-zero:
`.analysis/reconstruction/probes/v601-op-cmt-fadein-aggregate-001/receipt.json`,
SHA-256 `8342ecd2fbe297742991dddebfb8c5509a7fa757d8c98a1d32271b9c5c1b2b36`.
All 804 ordered target relocations remain preserved. This is decoded-function
exactness only; no DIET-packed offset or whole-OP exactness is claimed.

## Prior verified cohort: OP comment unput animation

v598 reconstructs the 48-byte `cmt_unput_both_animate()` leaf at payload
`0xC33F` (`1A74:1BFF`). Ghidra closes one contiguous body with one caller and
two callees. Raw target evidence fixes the global write
`graph_putsa_fx_func = 2`, two identical `BGIMAGE_PUT_RECT_16` calls with
arguments `(320, 64, 320, 320)`, and the single near call to payload `0xC244`,
corroborated by the MAP as `music_update_render_and_flip()`.

Maintained natural source is `src/op/music/cmt_unput_both_animate.cpp`.
Standalone TC86 output has exactly four expected fixups: the effect global, one
near call, and two FAR calls. The grouped replay leaves the complete
`0x6A5`-byte `OP_MUSIC_TEXT` producer raw-equal. The v599 complete OP
aggregate passes 34/34 registered decoded functions raw-zero:
`.analysis/reconstruction/probes/v599-op-cmt-unput-aggregate-001/receipt.json`,
SHA-256 `36cf2cc7870e8c16f75c527c8ffd953bd49b6aa80e7a4c0c4208901273a69576`.
All 804 ordered target relocations remain preserved. This is decoded-function
exactness only; no DIET-packed offset or whole-OP exactness is claimed.

## Prior verified cohort: OP setup help renderers

v596 reconstructs the paired 46-byte `bgm_help_put()` and `se_help_put()`
leaves at payloads `0xB738` and `0xB766` inside `OP_SETUP_TEXT`. Ghidra closes
both complete contiguous bodies. Raw target operands independently bind
`_BGM_HELP` at `0F34:0A4C` or `_SE_HELP` at `0F34:0A70`, and both renderers
FAR-call `GRAPH_PUTSA_FX` at `0DA1:04A4`. The target constants fix the same
9-line help geometry in each function: top 136, left 208, glyph height 16, and
color 15.

Maintained natural source is `src/op/setup/help_put.cpp`. Standalone TC86
output contains two consecutive 46-byte renderer bodies with exactly two table
fixups and two `GRAPH_PUTSA_FX` fixups across the pair. The grouped cold replay
keeps the complete `0x5A6`-byte `OP_SETUP_TEXT` producer raw-equal. The v597
complete OP aggregate passes 33/33 registered decoded functions raw-zero:
`.analysis/reconstruction/probes/v597-op-help-aggregate-001/receipt.json`,
SHA-256 `bd3146358c794d2f06c721bf902d223132515e67038b381301ab3abb3a1b93cb`.
All 804 ordered target relocations remain preserved. These are decoded-function
exact claims only; no DIET-packed offsets or whole-OP exactness are claimed.

## Prior verified cohort: OP tracklist renderer

v594 reconstructs the 39-byte `tracklist_put_both(unsigned char)` leaf at payload
`0xBF41` (`1A74:1801`). Ghidra closes one contiguous body with one caller and
one callee; the raw target iterates 24 track slots, uses color 3 for the
selected row and 5 otherwise, and near-calls payload `0xBED5`, corroborated
by the MAP as `track_put_both`.

Maintained natural source is `src/op/music/tracklist_put_both.cpp`. Standalone
TC86 output has exactly one near-call OMF fixup, while the grouped replay keeps
the entire `0x6A5`-byte `OP_MUSIC_TEXT` producer raw-equal. The v595 complete
OP aggregate passes 31/31 registered decoded functions raw-zero:
`.analysis/reconstruction/probes/v595-op-tracklist-aggregate-001/receipt.json`,
SHA-256 `dad2706759498dca0ca90b71593dce8ce5dfe18843e1cc7c4aab00f8fe16e599`.
All 804 ordered target relocations remain preserved. This is decoded-function
exactness only; no DIET-packed offset or whole-OP exactness is claimed.

## Prior verified cohort: OP DOS-exit wrapper

v592 reconstructs the 25-byte `game_exit_to_dos()` wrapper at payload `0xDDB1`
(`1DA1:03A1`). Target-first evidence closes one contiguous FAR body and binds
the four calls independently: `game_exit` at `0DA1:069C` plus
`KEY_BEEP_ON`, `TEXT_SYSTEMLINE_SHOW`, and `TEXT_CURSOR_SHOW` in master.lib.

A useful toolchain detail is now explicitly covered by the replay: TC86 emits
four five-byte FAR-call footprints in `exit_dos.obj`, but TLINK recognizes that
`game_exit` resides in the same `SHARED` segment and rewrites only that call to
`NOP / PUSH CS / CALL rel16` while preserving the five-byte footprint. No
target-derived assembly is used. The focused A/B replay reproduces the complete
25-byte linked function, the full retained OP program image, MAP identity, and
all 804 ordered relocations.

The v593 complete OP aggregate passes 30/30 registered decoded functions
raw-zero: `.analysis/reconstruction/probes/v593-op-dos-exit-aggregate-001/receipt.json`,
SHA-256 `2bd6d76fb175a08ad1edb06e5a1436e641e2323caea311fd058e912503c60909`.
This is decoded-function exactness only; no DIET-packed offset or whole-OP
exactness is claimed.

## Prior verified cohort: MAINE second script parameter

v590 reconstructs the 40-byte `script_param_read_number_second(int far&)`
helper at payload `0xA713` (`1A05:06C3`). Target evidence is independent of
the candidate source label: Ghidra closes one contiguous 40-byte body; raw
operands bind `_script_p` at `0E53:3F48`,
`script_param_number_default` at `0E53:3F94`, and the sole near call resolves
to payload `0xA64D`, the adjacent first-number parser.

Maintained natural source is
`src/maine/cutscene/script_param_second.cpp`. Standalone TC86 output has the
complete 40-byte instruction shape with exactly four expected OMF fixups; the
grouped replay preserves the complete `0xC3E`-byte `CUTSCENE_TEXT` producer.
The v591 complete MAINE aggregate passes 30/30 registered decoded functions
raw-zero: `.analysis/reconstruction/probes/v591-maine-script-param-aggregate-001/receipt.json`,
SHA-256 `b5d6bde55cbda6e1e7e1b804ee8ae6c15a31b6701d3ee4df11ecb2f941cf194c`.
All 559 ordered target relocations remain preserved. This is decoded-function
exactness only; no DIET-packed offset or whole-MAINE exactness is claimed.

## Prior verified cohort: OP frame-delay and background-free leaves

v587-v588 add two more target-first OP leaves. `frame_delay_2(int)` at payload
`0xE6DE` is a separate 21-byte FAR Pascal producer in `SHARED`; its target
bytes independently match the already accepted frame-delay logic, but credit is
not transferred. Maintained source `src/op/hardware/frame_delay_2.cpp` is
cold-compiled into the distinct `th02/frmdely2.cpp` owner, and both focused
rounds reproduce the complete function while preserving the v489 OP program
image and all 804 ordered relocations.

`raise_bg_free()` at payload `0xD1F3` is a 23-byte near leaf in `OP_01_TEXT`.
Target operands independently bind `_raise_bg` at `0F34:3F7A` and both FAR
calls to `0000:2856 HMEM_FREE`. Maintained natural source
`src/op/menu/raise_bg_free.cpp` compiles to the expected four normal OMF
fixups; the grouped replay preserves the complete `0xAB3`-byte `OP_01_TEXT`
producer raw-equal.

The v589 complete OP aggregate passes 29/29 registered decoded functions
raw-zero: `.analysis/reconstruction/probes/v589-op-leaf-batch-aggregate-001/receipt.json`,
SHA-256 `eb34efeb2eb692e029a1b9beeb2825d158ea2689ddadac16a14cfe9f3c0605cd`.
All 804 ordered target relocations remain preserved. These are decoded-function
exact claims only; neither function has a DIET-packed file offset and no
whole-OP exactness is claimed.

## Prior verified cohort: OP/MAINE small leaf batch

v582-v585 reconstruct four small target-first leaves without target-derived
assembly. MAINE `cutscene_script_free()` at payload `0xA2D1` is the complete
five-byte empty near function `PUSH BP / MOV BP,SP / POP BP / RET`; maintained
source is `src/maine/cutscene/script_free.cpp`. OP `main_cdg_free()` at
`0xCCC8` is a ten-byte wrapper whose only FAR call targets `0DA1:0CC0`,
corroborated by the MAP as `CDG_FREE_ALL`; maintained source is
`src/op/title/main_cdg_free.cpp`. OP `nopoly_B_free()` at `0xBF99` is a
14-byte leaf whose target operands independently bind `_nopoly_B` at
`0F34:3A80` and `HMEM_FREE` at `0000:2856`; maintained source is
`src/op/music/nopoly_free.cpp`. MAINE `box_bg_free()` at `0xA57F` is a
31-byte leaf whose target operands bind `_box_bg` at `0E53:3F4A` and
`HMEM_FREE` at `0000:2454`; maintained source is
`src/maine/cutscene/box_bg_free.cpp`.

Each function has a focused A/B natural-source replay. `main_cdg_free` keeps
the complete `0x2C7`-byte `OP_TITLE_TEXT` producer raw-equal; `nopoly_B_free`
keeps the complete `0x6A5`-byte `OP_MUSIC_TEXT` producer raw-equal; both
MAINE leaves keep the complete `0xC3E`-byte `CUTSCENE_TEXT` producer
raw-equal. Standalone OMF checks account only for normal symbol/link fixups.
The v586 complete decoded aggregates then pass all registered functions:

- OP: 27/27 raw-zero, receipt `.analysis/reconstruction/probes/v586-op-leaf-batch-aggregate-001/receipt.json`, SHA-256 `0300357209b7efc6d1f67f5ef22c0c8d042e8a7be7849262c31b87a343c62f66`; all 804 ordered target relocations preserved.
- MAINE: 29/29 raw-zero, receipt `.analysis/reconstruction/probes/v586-maine-leaf-batch-aggregate-001/receipt.json`, SHA-256 `14f35284a0764e0120b1606f9cc9502c4b7b56f2192e0586335df4ad3b7ea53c`; all 559 ordered target relocations preserved.

The function names remain candidate/MAP-derived labels rather than target
source-authority claims. These are decoded-function exact results only; neither
aggregate establishes a DIET-packed file offset or whole-executable exactness.

## Prior verified cohort: OP/MAINE shared sound-effect reset

Maintained natural C++ in `src/shared/sound/se_reset.cpp` now owns the complete
11-byte `snd_se_reset` body in both OP and MAINE. Each compiler producer is
12 bytes: two byte stores, terminal `RETF`, then one explicit `0x90`
codestring padding byte that remains outside function ownership. OP is at
payload `0xE2E6` (`1DA1:08D6`) and has an independently attested contiguous
Ghidra body. MAINE is at payload `0xD594` (`1CC7:0924`); its attested Ghidra
inventory has no function entry, so the review uses the explicit fail-closed
no-Ghidra gate plus the TLINK public and gap-free target decode rather than
inventing a disassembler boundary.

The v581 focused A/B replay reproduces both the 11-byte function and 12-byte
producer raw-zero while preserving the retained v489 linked image and all
ordered relocations. Full decoded aggregates then pass 25/25 OP functions and
27/27 MAINE functions:

- OP receipt: `.analysis/reconstruction/probes/v581-op-se-reset-aggregate-001/receipt.json`, SHA-256 `96cdcb934de64c67d9feb5825b7e9e65017c628ffadf88f3b102d048dfc4bdf9`; all 804 ordered target relocations preserved.
- MAINE receipt: `.analysis/reconstruction/probes/v581-maine-se-reset-aggregate-001/receipt.json`, SHA-256 `16d31881d7298b31873d40b2aeb6e2b70dd2220ab316ad71f7cd2a694dab6ab1`; all 559 ordered target relocations preserved.

This is decoded-function exactness only; it does not establish a DIET-packed
file offset or whole-executable exactness.

## Prior verified cohort: OP/MAINE shared vector math

Maintained source is `src/shared/math/vector.cpp` and its local declarations.
It naturally compiles a contiguous `0x5E`-byte OP/MAINE `SHARED` producer:
`polar` (`0x1C`) followed immediately by `VECTOR2_AT` (`0x42`). OP loaded
addresses are `1DA1:01A8` and `1DA1:01C4` (payload `0xDBB8` and `0xDBD4`);
MAINE addresses are `1CC7:0260` and `1CC7:027C` (payload `0xCED0` and
`0xCEEC`). Complete function bodies match raw-zero; independent tiling closes
them with `RETF 6` and `RETF 0xA`. The `vector2_at` declaration is only a
target-observed near reference to two 16-bit output words, not a full `SPPoint`
API claim.

At the v570 checkpoint, full decoded aggregate replay passed 24/24 functions
in each artifact:

- OP receipt: `.analysis/reconstruction/probes/v570-op-vector-exact-aggregate-001/receipt.json`, SHA-256 `c68fd2ef401e95ec1135a2577aaa0a5f0a6b05838b6d7296ab8349a713e73c99`; all 804 ordered target relocations preserved.
- MAINE receipt: `.analysis/reconstruction/probes/v570-maine-vector-exact-aggregate-002/receipt.json`, SHA-256 `6539b07824f74d88146dbded2dda2f87b1e127a109e9e376458cbb219a48a22e`; all 559 ordered target relocations preserved.

Both candidate linked program images remain equal to the retained target-local
v489 baselines. This verifies the accepted decoded extents and aggregate replay,
not a packed EXE byte-for-byte reconstruction. The prior input-wait cohort
remains documented in
[TH04_SHARED_INPUT_WAIT_V565.md](reconstruction/packed/TH04_SHARED_INPUT_WAIT_V565.md);
the vector/math evidence is in
[TH04_SHARED_VECTOR_MATH_V570.md](reconstruction/op-maine/TH04_SHARED_VECTOR_MATH_V570.md).

The v573 MAINE cutscene helper at payload `[0xA815,0xA847)` adds one decoded
function (50 bytes). Its maintained natural-C++ body is cold-compiled in
`CUTSCENE_TEXT`; the complete function slice is raw-zero, the full
`0xC3E` linked producer span matches target, all 559 ordered MAINE relocations
remain equal, and the exact-state aggregate passes 25/25. The surrounding
MAINE executable is still not byte-exact: this is function-level acceptance
through a pinned ReC98 replay scaffold, not packed-file acceptance. The name
`box_1_to_0_animate()` remains an open upstream-derived hypothesis. See
[the helper note](reconstruction/op-maine/TH04_MAINE_BOX_ANIMATE_BOUNDARY_V572.md).

The v574 MAINE SCORE decoder candidate at payload `0xC149` (`1A05:20F9`) adds
88 source-owner bytes. Target disassembly indicates a forward feedback
transform and checksum-difference return; pinned TC86 emits 97 standalone bytes,
so this remains source-present/nonexact. No target-derived assembly or packed
offset is claimed; details are in
[the SCORE codec note](reconstruction/op-maine/TH04_SCORE_CODEC_BOUNDARIES_V540.md).

The v577 MAINE SCORE encoder candidate at payload `0xC1A1` (`1A05:2151`) adds
101 source-owner bytes. Target instructions sum bytes `+4..+195`, call the far
helper at `0000:1C5A` twice for key bytes, then encode backward using the
previous output byte rotated right three bits and XORed with the second key.
Natural maintained C++ emits 113 standalone bytes; the 12-byte excess is the
16-byte shift/OR rotation versus target's four-byte in-place `ROR`. It remains
source-present/nonexact; the helper's candidate name is not target-attested,
and no packed offset is claimed. v580 adds MAINE `scoredat_recreate` at payload
`0xC206` (`1A05:21B6`): the complete 167-byte reviewed decoded function is
raw-zero in two focused cold builds and the 26-slice MAINE aggregate. Grouped
`SCORE_TEXT`, candidate MZ/MAP baseline, and all 559 ordered relocations remain
stable. Standalone-only near-call FIXUPP displacement words differ in the
separate-TU diagnostic; no target-derived assembly is used. This is decoded
function exactness only: DIET-packed offset is unknown and the candidate name
is not target-attested. Details and the v579 macro-expansion hazard are in
[the SCORE codec note](reconstruction/op-maine/TH04_SCORE_CODEC_BOUNDARIES_V540.md).

## Latest physical-boundary review: MAINE cutscene and indirect dispatcher

MAINE payload `0xA847..0xADBB` (`1A05:07F7..0D6B`) is now boundary-reviewed
as one `0x575`-byte owner. A target-local 16-entry CS-relative dispatch table
at payload `0xADBC` reaches case blocks that Ghidra omitted from its 58-byte,
two-range body; all paths reach a shared `RET 2`. This is boundary progress
only: source, meaning, and the candidate `script_op(unsigned char)` name remain
unverified. See
[TH04_MAINE_SCRIPT_OP_BOUNDARY_V571.md](reconstruction/op-maine/TH04_MAINE_SCRIPT_OP_BOUNDARY_V571.md).

The helper at payload `[0xA815,0xA847)` is now a decoded-function exact
50-byte extent (`1A05:07C5..07F6`), closed by a target-local caller and `RET`
immediately before the next reviewed entry. Natural maintained C++ reproduces
the complete slice; only this function receives exact credit. Its candidate
name remains an open hypothesis. See
[TH04_MAINE_BOX_ANIMATE_BOUNDARY_V572.md](reconstruction/op-maine/TH04_MAINE_BOX_ANIMATE_BOUNDARY_V572.md).

## Cleanup checkpoint and paused low-level candidates

After v635, tracked reconstruction state is **OP 48 decoded-exact / 45
pending**, **MAINE 34 / 38**, and **ZUN 0 / 11 pending plus 2 blocked**. There is no unfinished tracked source edit or bootstrap acceptance
left in the worktree. Resume only from a fresh boundary/origin review, not from
ignored cache contents or address order.

Three small-looking candidates were deliberately **not** promoted:

- MAINE `egc_start_copy()` at payload `0xA2D6` (52 bytes): ordinary maintained
  `outport(port,value)` codegen produces the wrong register-load order and
  shortens the zero-address write to `XOR AX,AX`. Using the historical
  `keep_0` decompilation helper or copying the old inline-assembly `outport2`
  would force bytes without first proving authored low-level source ownership.
- OP `SND_SE_PLAY` at payload `0xE2F2` (57 bytes): ordinary Pascal C++ produces
  a 60-byte BP-framed function. The target uses the old `snd_get_param`
  register/peek parameter mechanism and `_BL/_BH` indexing shape. Do not claim
  natural-source exactness by importing those decompilation helpers without
  first resolving source/ABI authority.
- OP `nopoly_b_put()` at payload `0xBFA7` (30 bytes): the candidate implementation
  contains explicit DS save/restore and the `__memcpy__` intrinsic. Treat it as
  a low-level authored/intrinsic ownership question rather than a routine C++
  leaf.

Private probe cleanup was performed after v625. All 1,207
`.analysis/reconstruction/probes/**/receipt.json` files were archived to
`.analysis/reconstruction/receipt-archive/probes-v625-cleanup-20260924.tar.zst`
with archive SHA-256
`f015afe31af4715aacc40f268e424b541c3e6aa280a4f1fd656156adf0ad6b07`.
The live probe tree now keeps only the full
`v546-zun-runtime-inventory-001` directory (a current script dependency) plus
receipt-only `v616-maine-end-animate-focused-003`,
`v617-maine-end-animate-aggregate-001`,
`v624-op-bgm-choice-focused-001`, and
`v625-op-bgm-choice-aggregate-001`. Subsequent v626/v627 work added the SE
choice focused and aggregate replay directories; no new cleanup claim is made
for those directories here. Historical analysis paths in ledgers remain
provenance strings, not promises that expanded worktrees still exist.

`scripts/prune_analysis.py --compact-referenced` reported no safe
`.analysis/gpt-web` deletions under the current retention policy. Do **not**
manually remove pinned targets/toolchains, active Ghidra boundary-review inputs,
or retained v401/v402/v489 snapshots merely to save space.

## Replay footprint and next work

The replay helper now materializes compiler-facing C/C++ source and include
files plus only response-file-linked objects, while keeping independent
writable A/B trees. A diagnostic full boundary-ledger rebuild against the
retained v489 compact source root produced 513 unrelated row drifts, so that
root is not an authority-equivalent replacement for the boundary input snapshot
behind the current ledger. Do not wholesale-regenerate
`config/th04_function_boundaries.csv` from it; use fresh attested boundary inputs
or project only independently reviewed local overrides. OP snapshots contain 2,549,948 source/include bytes,
171,255 root support-object/archive bytes, and 101,922 response-linked object
bytes; MAINE contains 2,583,609, 171,255, and 90,749 bytes respectively. The
previous source-tree copy was about 27 MiB per artifact/round. The helper is
TCC-only (do not apply its source filter to TASM). Focused worktrees and logs
are disposable. After the v625 cleanup, only the four latest OP/MAINE
focused/aggregate receipts and the full v546 ZUN runtime
inventory remain expanded under `.analysis/reconstruction/probes`; older probe
receipts are archived as described above. Delete new experiment intermediates
after recording their receipt, and preserve pinned inputs plus artifacts
covered by `config/analysis_retention.toml`.

Do not reopen MAINE `scoredat_recreate` at payload `0xC206`, the v582-v585
leaf batch, OP v587-v588/v592/v594/v596/v598/v600/v602/v606/v610/v612/v622/v624/v626/v628/v630/v632/v634,
or MAINE v590/v604/v608/v614: their complete decoded-function extents now pass
raw-zero acceptance. Select the next small unit from fresh OP/MAINE/ZUN boundary and
origin evidence rather than address order or candidate names. Keep the reviewed `0xA847..0xADBB` indirect
dispatcher as a separate ownership question: its candidate `th04/cutscene.cpp`
is only a forwarder to TH03 and is not maintained MAINE product code. Do not
trust candidate names or assume address order establishes source ownership.
Continue unfinished OP/MAINE boundary and authored-origin review alongside
ZUN's source-authority/component-ownership work; MAIN remains an evidence-triggered
side lane, not the default next target.
Preserve OP and MAINE SCORE TU composition, target restore provenance, v489
BGIMAGE, and v494 relocation/layout Oracles. Keep OP's two codec candidates and
MAINE's `scoredat_decode` and `scoredat_encode` source-present/nonexact until the
complete configured exact Oracle vector passes; never transcribe target rotates
into inline assembly.
For ZUN, all 13 authored
boundaries are reviewed, but 11 remain pending and two C++ units are blocked;
resolve source authority and component/runtime ownership before claiming
authored exactness. The ZUN library-origin graph-clear slice is support-only.

Historical MAIN residuals, ZUN runtime inventories, and per-version experiment
logs belong in their bounded notes, not this current-state handoff. After each
coherent change, run the focused replay, affected cold aggregate, full CI, and
`git diff --check`; update the ledgers and this handoff only from verified
results.
