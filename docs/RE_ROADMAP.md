# TH04 reconstruction roadmap

Updated 2026-09-24. Live counts come from `python3 scripts/status.py` and
`docs/PROGRESS.md`; regenerate them rather than editing counts here. This
replaces MAIN-last-bytes-first work. MAIN's 27 bytes are an evidence-triggered
side lane, not a dependency for the other artifacts.

## 1. Establish OP/MAINE/ZUN acceptance surfaces

**Baseline complete:** `config/th04_decoded_function_acceptance.csv` and
`scripts/decoded_function_acceptance.py` provide reviewed physical extent,
source/backend binding, producer-scoped evidence, function-scoped equal raw
hashes, two cold rounds, and artifact-local target comparison. CI/preflight
validate the ledger. Six existing OP/MAINE BGIMAGE rows replay decoded-exact;
ZUN's two C++ rows replay as nonexact diagnostics. ZUN's resident component
driver is rebased on retained inputs. See the
[acceptance contract](reconstruction/packed/TH04_DECODED_FUNCTION_ACCEPTANCE_V508.md).

**First extension verified:** the v509 VRAM backend cold-compiles the checked-in
shared C++ TU independently into OP and MAINE, with complete decoded raw-zero
function comparisons and target-ordered relocations. The ZUN graph-clear
support backend is also rebased and raw-zero on its 36-byte library-origin
slice, but this does not grant authored-function acceptance. See the
[three-artifact smoke](reconstruction/packed/TH04_THREE_ARTIFACT_SMOKE_V509.md).
The v565 shared input-wait backend now cold-compiles one maintained natural C++
producer into OP and MAINE; both complete 86-byte target slices are raw-zero,
with all target relocations and v489 linked images preserved. At that v565
checkpoint, the full decoded-acceptance wrappers passed 22/22 slices per
artifact. The replay materializer
now copies only compiler-facing source/includes and response-file link objects,
reducing source snapshot data from about 27 MiB to about 2.6 MiB per A/B artifact
worktree. See the [input-wait replay note](reconstruction/packed/TH04_SHARED_INPUT_WAIT_V565.md).

The v570 shared vector-math cohort adds natural-source `polar` and
`VECTOR2_AT` bodies to OP and MAINE. The complete adjacent `0x5E` producer is
raw-zero in both targets, with RETF cleanup, MAP placement, OMF, relocation,
two-round determinism, and full decoded aggregate replay checked. At that v570
checkpoint, both artifact aggregates passed 24/24 slices; OP preserves 804 and
MAINE 559 ordered relocations. `VECTOR2_AT` uses a narrow target-observed
two-word near-reference ABI view, not a full `SPPoint` API claim. See the
[vector-math note](reconstruction/op-maine/TH04_SHARED_VECTOR_MATH_V570.md).

At the v573 checkpoint, the MAINE cutscene helper added a naturally compiled
50-byte decoded function at `1A05:07C5` (payload `[0xA815,0xA847)`). Its complete slice is
raw-zero, the `0xC3E` linked `CUTSCENE_TEXT` producer span matches target, and
the MAINE aggregate then passed 25/25 slices with all 559 ordered
relocations preserved. This does not establish the candidate function name or
whole-file MAINE exactness; see the
[helper replay note](reconstruction/op-maine/TH04_MAINE_BOX_ANIMATE_BOUNDARY_V572.md).

The shared hardware/PI/sound/input/math cohort is complete. MAINE has nine and OP
has eight artifact-local SCORE function backends; expand natural source one
reviewed physical owner at a time while resolving ZUN's remaining source authority.
v562/v563 add maintained natural-C++ source for OP `scoredat_encode` and
`scoredat_decode`, but pinned standalone objects are 111/197 bytes against
reviewed 101/173-byte targets. Both remain source-present only; do not turn the
target rotates into copied assembly. The shared input/vector cohort is complete;
choose the next unit from remaining OP/MAINE target-reviewed work or the ZUN
authored/source-authority queue after fresh boundary/origin review. Do not
preselect by address or carry a stale work order across checkpoints. In
particular, do not treat MAINE `egc_start_copy`, MAINE `box_1_to_0_masked`,
OP `SND_SE_PLAY`, OP `_snd_se_update`, or OP `nopoly_b_put` as ordinary
natural-C++ leaves. The v642
`snd_se_update` probe narrows its natural mismatch to one byte of array-index
codegen; a register-specific control explains the target but receives no exact
credit. These cases require source/ABI ownership review before any exact attempt.
Keep decoded function acceptance apart from `units.csv` raw-file exactness;
never invent packed `file_offset` values. Preserve OP/MAINE SCORE TU
composition and v489/v494 aggregate Oracles during every source edit. A new
backend must actually compile the claimed source and compare its own artifact;
the BGIMAGE backend cannot grant credit to another TU.

## 2. Harvest maintained shared source in small cohorts

The currently maintained reviewed shared hardware/PI/sound/input/math cohort is
complete in both OP and MAINE: three BGIMAGE functions plus VRAM, frame delay,
three PI functions, PMD, MMD, KAJA, mode detection, delay-until-measure,
input-wait, `snd_se_reset`, plus `polar` and `VECTOR2_AT`. That is 17
decoded-exact functions / 1,031 source-owner bytes per artifact. MAINE has 35
decoded-exact functions / 2,867 exact source-owner bytes plus two
source-present/nonexact SCORE candidates, `scoredat_decode` (88 bytes) and
`scoredat_encode` (101 bytes), plus the 134-byte nonexact
`box_1_to_0_masked`, for 3,190 decoded source-owner bytes; OP has
51 decoded-exact functions / 4,273 exact source-owner bytes, with two separate
codec candidates (274 bytes) plus `snd_se_update` (76 bytes) still
source-present and nonexact, for 4,623 decoded source-owner bytes total.
MMD keeps its 47-byte natural-C body separate from the following target 0x90
padding, and MAINE delay keeps target 0xD077 linker fill outside its authored
extent. These accepted functions now need replay maintenance and later
packed-file accounting. v540/v541 have now target-reviewed the codec plus
selected loading/saving/score-rendering SCORE boundaries in both artifacts.
MAINE's hi_end candidate-C++ owners and OP's five remaining hi_view owners are
now physically reviewed. The OP review corrected Ghidra's truncated
`rank_render` body from `0x3C` to a reachable `0x7A` bytes. All pinned ReC98
implementations examined in v540-v542 have explicit decompilation provenance
and grant no source credit. In v543-v544 MAINE `score_insert` and `score_put`
were independently cold-compiled from maintained natural source and matched
all 340 and 230 linked bytes. v547 adds the adjacent 121-byte stage renderer
with a reusable bounded SCORE function harness. v548 adds the adjacent 172-byte
name cursor renderer after proving its standalone near-call OMF fixup and
grouped raw-zero link. v549 adds the adjacent 184-byte score-entry row
renderer with two separately attested near-call fixups. v550 adds the 26-byte
places dispatcher with its single near-call fixup. v551 adds the 49-byte
alphabet cursor renderer with standalone CODE equality. v557 adds MAINE's
105-byte high-score loader, and v570 adds shared vector math; at that checkpoint
MAINE had 24 functions / 2,247 decoded source-owner bytes. v573 adds one
50-byte natural-C++ cutscene helper with raw-zero function bytes and a 25/25
exact-state aggregate replay. v574 adds a target-first MAINE `scoredat_decode`
source candidate at `0xC149`; its natural TC86 CODE is 97 bytes against the
reviewed 88-byte target because the target's byte `ROR` is not reproduced by
natural shift/OR C++. It remains source-present/nonexact. This is
function-level work, not a packed-file or entire SCORE-TU claim. v577 adds the
adjacent MAINE `scoredat_encode` candidate at `0xC1A1`: target flow has a
separate observation, while natural TC86 output is 113 bytes against 101 because
the byte rotate expands to shifts/OR. It remains source-present/nonexact; no
target-derived assembly is used. v580 adds a natural maintained
`scoredat_recreate` body at `0xC206` and promotes only that 167-byte decoded
function after focused two-cold raw-zero replay and a 26-slice MAINE aggregate.
The candidate MZ/MAP baseline and all 559 relocations remain stable, but its
program image is still shorter than the target and no packed offset is known.
The candidate function name remains unverified. Preserve the v580
`#undef SCOREDAT_FN`/external filename declaration: leaving the header macro
active emitted an extra DGROUP filename literal in the failed v579 attempt.
v581 adds the shared 11-byte `snd_se_reset` leaf to both artifacts from one
maintained natural-C++ producer. OP uses its contiguous target Ghidra body;
MAINE deliberately uses a separate no-Ghidra review path bound to the TLINK
public and complete linear decode. Full aggregates pass 25/25 OP and 27/27
MAINE slices with 804/559 ordered relocations preserved.
v582-v585 then add four target-first leaves: MAINE's 5-byte
`cutscene_script_free` and 31-byte `box_bg_free`, plus OP's 10-byte
`main_cdg_free` and 14-byte `nopoly_B_free`. Their focused natural-source
replays preserve the complete surrounding `CUTSCENE_TEXT`, `OP_TITLE_TEXT`,
or `OP_MUSIC_TEXT` producer as applicable. The v586 full aggregates pass
27/27 OP and 29/29 MAINE decoded slices with 804/559 ordered relocations
preserved. These labels remain candidate/MAP-derived and grant no packed-file
or whole-product exactness.
v587-v588 then add OP's separate 21-byte `frame_delay_2`
producer and 23-byte `raise_bg_free` leaf. `frame_delay_2` receives independent
producer-local replay even though its target body equals the earlier accepted
frame-delay body; `raise_bg_free` is bound to `_raise_bg` and two
`HMEM_FREE` calls by target operands plus MAP corroboration. The v589 OP
aggregate passes 29/29 decoded slices with all 804 ordered relocations
preserved. These remain decoded-function claims, not packed-file or whole-OP
exactness.
v590 then adds MAINE's 40-byte `script_param_read_number_second(int far&)`
helper from target-first operand evidence: `_script_p`,
`script_param_number_default`, and the near call to the adjacent first-number
parser all resolve independently. Standalone TC86 output has exactly four
expected OMF fixups, while the grouped replay preserves the complete `0xC3E`
`CUTSCENE_TEXT` producer. The v591 MAINE aggregate passes 30/30 decoded
slices with all 559 ordered relocations preserved. The helper name remains
candidate/MAP-derived, and no packed-file or whole-MAINE exactness is claimed.
v592 then adds OP's 25-byte `game_exit_to_dos` wrapper. Its source-level calls
remain ordinary natural C++; the replay separately proves the Borland OMF and
TLINK behavior that converts the same-segment `game_exit` FAR-call footprint
into `NOP / PUSH CS / CALL rel16`, while the three master.lib calls remain FAR.
The v593 OP aggregate passes 30/30 decoded slices with all 804 ordered
relocations preserved. This is still decoded-function evidence only, not
packed-file or whole-OP exactness.
v594 then adds OP's 39-byte `tracklist_put_both` renderer. Target flow fixes the
24-entry loop, selected/normal colors 3 and 5, and the sole near call to
`track_put_both`; standalone TC86 output has one near-call fixup and the grouped
replay leaves the full `OP_MUSIC_TEXT` producer unchanged. The v595 OP aggregate
passes 31/31 decoded slices with all 804 ordered relocations preserved. This is
decoded-function evidence only, not packed-file or whole-OP exactness.
v596 then adds the paired 46-byte OP setup help renderers,
`bgm_help_put` and `se_help_put`. Target operands independently bind their help
tables (`_BGM_HELP` / `_SE_HELP`) and the shared `GRAPH_PUTSA_FX` FAR-call
target; standalone TC86 output contains the expected two table and two call
fixups across the pair. The grouped replay preserves the complete `0x5A6`
`OP_SETUP_TEXT` producer. The v597 OP aggregate passes 33/33 decoded slices
with all 804 ordered relocations preserved. These remain decoded-function
claims, not packed-file or whole-OP exactness.
v598 then adds OP's 48-byte `cmt_unput_both_animate` leaf.
Target bytes independently fix the effect value, rectangle constants, two
`BGIMAGE_PUT_RECT_16` FAR calls, and the near call to
`music_update_render_and_flip`. Standalone TC86 output has the expected four
fixups, and the grouped replay preserves the complete `OP_MUSIC_TEXT` producer.
The v599 OP aggregate passes 34/34 decoded slices with all 804 ordered
relocations preserved. This remains decoded-function evidence only, not
packed-file or whole-OP exactness.
v600 then adds the adjacent 49-byte `cmt_fadein_both_animate`
leaf. Target flow fixes the effect loop 4..7, final effect 2, and the alternating
`cmt_put` / `music_update_render_and_flip` calls. Standalone TC86 output has
nine expected word fixups; the grouped replay again preserves the complete
`OP_MUSIC_TEXT` producer. The v601 OP aggregate passes 35/35 decoded slices
with all 804 ordered relocations preserved. This remains decoded-function
evidence only, not packed-file or whole-OP exactness.
v602 then adds OP's 49-byte `main_cdg_load` leaf. Target
call blocks fix slots 0/10/35/40, resolve four filename pointers in the target,
and bind three `CDG_LOAD_ALL` calls plus one `CDG_LOAD_ALL_NOALPHA` call.
Standalone TC86 output has the expected four string-address and four FAR-call
fixups; grouped replay preserves the complete `OP_TITLE_TEXT` producer. The
v603 OP aggregate passes 36/36 decoded slices with all 804 ordered relocations
preserved. This remains decoded-function evidence only, not packed-file or
whole-OP exactness.
v604 then adds MAINE's 49-byte `cfg_load_resident_ptr`
leaf. Target bytes and MAP evidence independently bind the `MIKO.CFG` file
flow, 10-byte local CFG read, the resident-segment extraction, and the
`_resident` far-pointer update. Standalone TC86 output has six expected fixups;
the grouped replay preserves the complete `MAINE_E_TEXT` producer. The v605
MAINE aggregate passes 31/31 decoded slices with all 559 ordered relocations
preserved. This remains decoded-function evidence only, not packed-file or
whole-MAINE exactness.
v606 then adds OP's 49-byte `nopoly_B_snap` leaf. Target
operands bind the `0x7D00` `HMEM_ALLOCBYTE` allocation, `_nopoly_B` destination,
and `_VRAM_PLANE_B` source; the signed target loop comparison also rejects an
unsigned loop-variable hypothesis. Standalone TC86 output has four expected
fixups, and the grouped replay preserves the complete `OP_MUSIC_TEXT` producer.
The v607 OP aggregate passes 37/37 decoded slices with all 804 ordered
relocations preserved. This remains decoded-function evidence only, not
packed-file or whole-OP exactness.
v608 then adds MAINE's 51-byte `game_exit_and_exec` wrapper.
Target operands and MAP evidence bind the six call targets and the `_execl`
argument layout independently of the candidate source label. Standalone TC86
output has six expected FAR-call fixups; the grouped replay preserves the full
`MAINE_E_TEXT` producer. The v609 MAINE aggregate passes 32/32 decoded slices
with all 559 ordered relocations preserved. This remains decoded-function
evidence only, not packed-file or whole-MAINE exactness.
v610 then adds OP's 55-byte
`music_update_render_and_flip` helper. Target operands bind two near calls,
`GRCG_SETCOLOR`, `frame_delay_2`, three `_music_page_accessed` references,
and the inline 0x7C/0xA4/0xA6 port writes. Standalone TC86 output has seven
expected fixups, and the grouped replay preserves the complete
`OP_MUSIC_TEXT` producer. The v611 OP aggregate passes 38/38 decoded slices
with all 804 ordered relocations preserved. This remains decoded-function
evidence only, not packed-file or whole-OP exactness.
v612 then adds OP's 60-byte `rollup` helper. Target operands
bind `window.h` through `_window+2`, and target arithmetic independently fixes
the 16-pixel tile height, two frames per tile, and 8-pixel roll speed. Standalone
TC86 output has two data fixups plus the expected near/FAR call fixups; grouped
replay preserves the complete `OP_SETUP_TEXT` producer. The v613 OP aggregate
passes 39/39 decoded slices with all 804 ordered relocations preserved. This
remains decoded-function evidence only, not packed-file or whole-OP exactness.
v614 then adds MAINE's 63-byte `cutscene_script_load` helper.
Target operands and MAP evidence bind the free/open/size/read/close call chain,
`_script`, `_script_p`, and both return values independently of the candidate
source label. Standalone TC86 output has one near-call, four FAR-call, and three
data fixups; grouped replay preserves the complete `CUTSCENE_TEXT` producer.
The v615 MAINE aggregate passes 33/33 decoded slices with all 559 ordered
relocations preserved. This remains decoded-function evidence only, not
packed-file or whole-MAINE exactness.
v616 then adds MAINE's 69-byte `end_animate` helper.
Target operands bind three maintained resident fields, the ending-script far
pointer, and the three cutscene calls independently of the candidate source
label. Standalone TC86 output has one static-data initializer fixup plus ten
code fixups; the grouped link-relevant OMF is baseline-exact and preserves the
complete `MAINE_E_TEXT` producer. The v617 MAINE aggregate passes 34/34
decoded slices with all 559 ordered relocations preserved. This remains
decoded-function evidence only, not packed-file or whole-MAINE exactness.
v618 then adds OP's 74-byte `cmt_put` comment renderer.
Target operands bind `_cmt`, the 40-byte line stride, 20-line loop,
semicolon-line suppression, layout constants, and the two `GRAPH_PUTSA_FX`
calls independently of the candidate source label. Standalone TC86 output has
three data and two FAR-call fixups; the grouped replay preserves the complete
`OP_MUSIC_TEXT` producer. The v619 OP aggregate passes 40/40 decoded slices
with all 804 ordered relocations preserved. This remains decoded-function
evidence only, not packed-file or whole-OP exactness.
v620 then adds the adjacent 73-byte `cmt_load` helper.
Target operands bind the four file calls, `_cmt`, the `0x320` file block,
20×40-byte line layout, and byte-38 terminators. The target filename operand
falls inside the pinned OP-music data contribution, and the restored target has
one `_MUSIC.TXT` literal at the linked location. Standalone TC86 output has
seven expected file/data fixups; the grouped replay preserves the complete
`OP_MUSIC_TEXT` producer. The v621 OP aggregate passes 41/41 decoded slices
with all 804 ordered relocations preserved. This remains decoded-function
evidence only, not packed-file or whole-OP exactness.
v622 then adds the 72-byte
`cmt_load_unput_and_put_both_animate` transition wrapper. Target control flow
binds the shown-state byte, seven callees, the 320×320 background restore, and
the first-show versus fade-in branch independently of the candidate source
label. Standalone TC86 output has eleven word fixups plus one FAR-call fixup;
the grouped replay preserves the complete `OP_MUSIC_TEXT` producer. The v623
OP aggregate passes 42/42 decoded slices with all 804 ordered relocations
preserved. This remains decoded-function evidence only, not packed-file or
whole-OP exactness.
v624 then adds OP's 79-byte `bgm_choice_put` renderer.
Target mode values and linked data addresses bind the three Shift-JIS BGM
choice strings and their vertical offsets independently of the candidate label;
the sole callee is `GRAPH_PUTSA_FX`. Focused replay preserves the complete
`OP_SETUP_TEXT` producer and grouped choice-string OMF. The v625 OP aggregate
passes 43/43 decoded slices with all 804 ordered relocations preserved. This
remains decoded-function evidence only, not packed-file or whole-OP exactness.
v626/v627 then add the adjacent 81-byte `se_choice_put` renderer. Independent
target review corrects the SE mode ABI to OFF=0, FM=1, BEEP=2; target branches
and pinned setup data bind those values to the three Shift-JIS strings and
vertical offsets +32/+0/+16. Natural maintained C++ raw-matches the complete
function, preserves the full `OP_SETUP_TEXT` producer and grouped OMF, and the
v627 OP aggregate passes 44/44 decoded slices with all 804 ordered relocations
preserved. This remains decoded-function evidence only, not packed-file or
whole-OP exactness.
v628/v629 then close the nearby 89-byte `window_rollup_put` helper. Fresh
target review binds the window width, EGC copy, three bottom-tile draws, and
Pascal cleanup before codegen tuning. Natural maintained C++ raw-matches the
complete function and full `OP_SETUP_TEXT` producer; the v629 OP aggregate
passes 45/45 decoded slices with all 804 ordered relocations preserved. This
again is decoded-function evidence only, not packed-file or whole-OP exactness.
v630/v631 then close the 112-byte `dropdown` animation. Fresh target review
binds both window dimensions, the three top-tile draws, `window_dropdown_put`,
`frame_delay`, and Pascal cleanup; the maintained OMF independently preserves
the `window.h` +2 field addend. Natural maintained C++ raw-matches the complete
function and full `OP_SETUP_TEXT` producer, and the v631 OP aggregate passes
46/46 decoded slices with all 804 ordered relocations preserved. This remains
decoded-function evidence only, not packed-file or whole-OP exactness.
v632/v633 then close the 122-byte `window_dropdown_put` renderer. Target-first
review binds the EGC restore, window width, six SUPER_PUT calls, paired tile
IDs 2/6, 0/3, 4/7, and Pascal cleanup. Natural maintained C++ produces exactly
the target instruction shape modulo nine ordinary OMF fixups, then raw-matches
the complete function and full `OP_SETUP_TEXT` producer after linking. The
v633 OP aggregate passes 47/47 decoded slices with all 804 ordered relocations
preserved; an independent aggregate recheck also passes. This remains
decoded-function evidence only, not packed-file or whole-OP exactness.
v634/v635 then close the adjacent 122-byte `singleline` renderer. Target-first
review fixes the 32-pixel restore height, paired tile IDs 5/6, 1/3, 8/7,
window-width loop, and Pascal cleanup. Natural maintained C++ again produces
exactly the target standalone CODE modulo the same nine ordinary OMF fixups,
then raw-matches the complete function and full `OP_SETUP_TEXT` producer.
The v635 OP aggregate passes 48/48 decoded slices with all 804 ordered
relocations preserved. This remains decoded-function evidence only, not
packed-file or whole-OP exactness.
v636/v637 then close the 108-byte `track_put_both` music-room helper. Fresh
target review binds the two VRAM-page writes, choice-table indexing, the two
`GRAPH_PUTSA_FX` renders, coordinates, and Pascal cleanup independently of
the candidate name. The initial replay draft exposed and fixed an unreachable
maintained-source stability check before acceptance. Natural maintained C++
raw-matches the complete function and full `OP_MUSIC_TEXT` producer, and the
v637 OP aggregate passes 49/49 decoded slices with all 804 ordered relocations
preserved. This remains decoded-function evidence only, not packed-file or
whole-OP exactness.
v638/v639 then close the 106-byte `playchar_title_box_put` renderer. Target-
first review fixes the playchar-dependent x positions, two GRCG colors, two
round-box extents, radius, direct GRCG-off port write, and Pascal cleanup.
Standalone natural C++ produces exactly the target CODE modulo four ordinary
FAR-call fixups. A first grouped attempt caught standalone-only symbol names in
the .inl; after making the body composable with the original TU, focused replay
raw-matches the complete function and full `OP_01_TEXT` producer. The v639
OP aggregate passes 50/50 decoded slices with all 804 ordered relocations
preserved. This remains decoded-function evidence only, not packed-file or
whole-OP exactness.
v640/v641 then close the 123-byte `pic_darken` helper. Target-first review
fixes the two initial VRAM offsets, GRCG color call, alternating 32-bit mask
patterns, 244-row geometry, VRAM-plane reference, row-tail stride, direct
GRCG-off port write, and Pascal cleanup. Standalone natural C++ is exactly the
target CODE modulo two ordinary OMF fixups. The dedicated replay independently
binds the target extent, MAP symbols, fixup sites, and original-TU replacement
anchors before the full-TU build. The linked replay then raw-matches the
complete function and full `OP_01_TEXT` producer, and the
v641 OP aggregate passes 51/51 decoded slices with all 804 ordered relocations
preserved. This remains decoded-function evidence only, not packed-file or
whole-OP exactness.
v643/v644 then close MAINE's 84-byte `cursor_advance_and_animate` helper.
Target-first review binds cursor/fast-forward state, box animation, input wait,
the two page writes, box redraw, and the complete near-function extent. Natural
C++ raw-matches the complete function and full `CUTSCENE_TEXT` producer with
all 559 ordered relocations preserved. The first aggregate attempt exposed a
replay integration bug: the new backend rejected the nested private output
directory used by the aggregate wrapper. Commit 8289f36 fixes only that path
policy; the repaired v644 aggregate passes 35/35 MAINE decoded slices raw-zero.
This remains decoded-function evidence only, not packed-file or whole-MAINE
exactness.
v645 then target-reviews the adjacent 134-byte `box_1_to_0_masked` leaf and
keeps it deliberately nonexact. Natural maintained C++ reaches the target
length once the PC-98 planar offset is expressed as y<<6 + y<<4, but after
masking the three ordinary pointer/data fixups, 18 bytes still differ solely
in the first three EGC port-write load orders. A y*ROW_SIZE control is 127
bytes, independently explaining the seven-byte arithmetic gap. The only known
target-order helper, `outport2`, is explicit decompilation `_asm` and is not
compiled or credited. Treat this as a low-level source-authority problem, not
an invitation to copy the target instruction order.
Choose subsequent units from current OP/MAINE/ZUN evidence and unfinished
boundary/authored-review queues; do not treat C206 as pending or restart MAIN
by default.

## 3. Reconcile boundary and origin alongside mature TUs

Review the 13 remaining provisional authored boundaries by neighboring ownership:
OP's eight (prioritize the Ghidra-only and noncontiguous music/main owners) and
MAINE's five (the remaining MAP-public/sound and cutscene/registration entries).
ZUN's authored physical boundaries are already fully reviewed by v520/v521.
For each remaining owner, inspect attested target entry, callers, all returns/tails,
tables, alignment, adjacent bytes, MAP/TASM contribution, and segment identity.
A provisional owner cannot be promoted exact, but it need not block an unrelated
reviewed source TU.

Classify the 33 unresolved `target-derived-asm` authored candidates by
subsystem and independent producer fingerprints: OP ZUNSOFT animation 4;
MAINE staff/verdict/registration/EGC families 18; ZUN ZUNINIT/MEMCHK 11.
This is an authority question, not an instruction to transcribe disassembly
as source. Independently attest the 35 non-MAIN `attest-asm` observations
(OP 16, MAINE 15, ZUN 4) without counting them as authored C/C++ progress.

## 4. Reconstruct by physical translation unit

OP now has all five target-reviewed hi_view functions locally maintained after
v545/v552-v556: 80-byte stage, 293-byte two-column row, 122-byte rank,
335-byte registration menu, and 180-byte clear-state/sprite initializer.
The v553 rank acceptance checks the v542 Ghidra-missed reachable tail;
candidate MAP publics corroborate layout but not original names. v558/v559/v561
add `hiscore_scoredat_load_both`, `scores_put`, and `scoredat_recreate` to the
maintained OP SCORE set. v562 reviews `scoredat_encode` at `0xC627` and adds a
natural-C++ source candidate, but standalone CODE is 111 bytes against the
target's 101 because TC86 emits a byte-rotate helper call rather than the
target's in-place byte ROR. v563 adds natural-C++ `scoredat_decode` at `0xC57A`,
whose shift/OR rotation yields 197 bytes against 173 target bytes. Keep both
source-present only, do not use target-derived inline assembly. v565 adds the
reviewed 0x56-byte OP input-wait owner beginning at `0xDB62`; v570 adds the
adjacent shared vector-math producer. OP remains 24/24; MAINE's v573 checkpoint
passed 25/25 and v580 brings its accepted function slices to 26/26. The
surrounding SCORE scaffold
remains untrusted; continue with title/setup,
music and character units, and larger main/animation units after boundary/origin
review. MAINE's candidate-C++ hi_end boundaries are physically reviewed after
v541 and its first seven SCORE_TEXT functions are accepted after v543-v551;
v557 adds the high-score loader, v565 adds shared input-wait, and v570 adds
shared vector math, bringing MAINE at that checkpoint to 24 / 2,247 decoded
function bytes. v577 adds MAINE `scoredat_encode` source at `0xC1A1`, but the
natural standalone CODE is 113 bytes against a reviewed 101-byte target because
of the rotate codegen mismatch. v580 then reconstructs the adjacent
`scoredat_recreate` from target evidence and obtains a decoded-function raw-zero
slice at `0xC206`; MAINE reached 26/26 at v580. v581 then adds shared
`snd_se_reset` to OP and MAINE. v582-v585 add the four small cutscene/title/music
leaves described above; v587-v588 then add OP frame_delay_2 and raise_bg_free,
and v590/v591 add the second MAINE script-number helper. The current
decoded-function totals are 51/51 OP and 35/35 MAINE. The next unit is not
preselected: re-evaluate outstanding small reviewed/corroborated owners and
boundary/origin maturity before starting it.
Registration-menu and cutscene work remain separate ownership questions, with
source provenance kept apart from target-boundary confidence. v572 reviewed
the adjacent 50-byte MAINE cutscene helper at payload
`0xA815..0xA846` (`1A05:07C5..07F6`); v573 now has a natural maintained C++
body and decoded-function raw-zero acceptance for that complete extent. The
candidate name remains an open hypothesis, and neither this function nor the
matching producer span establishes whole-file MAINE exactness. v571
target-review closes the MAINE
indirect-dispatch candidate at
payload `0xA847..0xADBB` (`0x575` bytes), including 16 switch targets omitted
from Ghidra's 0x3A-byte/two-range body. Its mapped ReC98 path is only a TH03
forwarder; recover a natural TH04 source owner/TU before attempting decoded
acceptance, and do not promote its candidate name. If that ownership cannot be
closed, pivot to a smaller reviewed owner. Candidate byte totals in the boundary inventory
are **not** exact denominators; prioritize by evidence maturity and TU/link
impact, not by address order or attractive percentage.

ZUN: `cfg_init` and resident `_main` are now explicit
function-level blockers while their units remain source-present. v519 proves
the 152-byte cfg_init has no non-FIXUPP target/object differences. v539
revalidates it on the current compact-MASTER c0t+CT link: three FIXUPP words
already equal target and the other twelve are each exactly target minus 6,
accounting for all 13 raw linked differences under the six-byte blocked _main layout. v518 closes the supported TC4J profile surface for
_main's selective print-call shape and rejects ReC98 inert barriers as
independent source provenance. v538 additionally closes pragma option -O-
scoping: the pinned TCC cannot use BCC-style -Od, and pragma placement cannot
selectively preserve the two target calls. Reopen either C++ function only for
a natural raw-zero link, materially new provenance, or a genuinely new compiler mechanism. v520 now closes the complete ZUNINIT physical function/data partition, so no ZUN
authored boundary remains provisional; its eight code entries still retain
`target-derived-asm` source provenance and zero exact credit. Routine ZUN work
should now resolve ZUNINIT/MEMCHK source/origin authority and component ownership
and replace external library inputs. v524 removes DOS_FREE from that external surface after GRAPH_CLEAR/RESDATA/FILE_READ; v525 also removes DOS_AXDX while keeping its trailing module-alignment NOP outside the function owner; v526 additionally removes DOS_PUTS2; v527-v532 now close the immediate MASTER file-helper family: FILE_CREATE, FILE_ROPEN, FILE_WRITE, FILE_SEEK/FILE_TELL, FILE_APPEND, and FILE_FLUSH/FILE_CLOSE all have maintained support source with physical module ownership and alignment explicit. v533 additionally removes the fontopen code/data member; v534 removes the VERSION/GRP pure-data members while preserving the historical GRP-to-VERSION force-link dependency. v535 also localizes fil as four initialized file-state DATA bytes plus a separate 0x14-byte BSS layout owner, without inventing BSS target bytes. v536 then removes the external 640-member masters.lib entirely by rebuilding a deterministic 15-member local archive; v537 proves emu.lib and maths.lib are unused and removes them from the resident link response. The remaining external runtime surface is c0t.obj plus exactly 26 pulled CT.LIB members; classify those compiler/runtime owners before choosing any replacement, and keep them separate from game-authored work. The library-origin `GRAPH_CLEAR` slice is
support-only. v521 additionally closes all three MEMCHK authored physical function extents while keeping the IDA-generated candidate source at zero source/exact credit. All 13 current ZUN authored candidates are now target-reviewed. v522 also closes the pinned ReC98 generated-assembly route: ZUNINIT and MEMCHK enter that ancestry as IDA-generated initial-state reconstructions, so their raw-equal candidate links cannot satisfy source authority. The remaining work is independent provenance or natural reconstruction plus component ownership. After source ownership and inputs close, compare the composite
link and only then the DIET-packed container.

The v546 current-source replay confirms that ZUN's 4,241 resident
same-position differences are dominated by the six-byte `_main` layout
cascade: after a read-only gap alignment, 46 of 6,354 mapped positions still
differ. This narrows diagnosis but grants no byte credit. Treat `c0t.obj` and
the 26 pulled CT.LIB members as pinned compiler/runtime inputs unless a
specific full-product Oracle proves a replacement necessary; they are not
TH04 authored source. Prioritize a legitimate natural-source explanation for
the two `_main` calls and independent ZUNINIT/MEMCHK ownership evidence, not
bulk runtime transcriptions or comparator normalization.

## 5. Close whole artifacts and validate runtime behavior

Once enough maintained source and external object ownership are present,
replace ReC98 overlay materialization with checked-in TH04 source/headers,
attest ordered link inputs, compare full decoded images and ordered
relocations, then pack and compare complete target files. OP/MAINE's shared
two-byte `snd_load` residual is one provenance/codegen question across three
artifacts, not three independent exact claims. Add deterministic PC-98
runtime scenarios as soon as a representative product build can run; do not
defer semantic checks until whole-file exactness. Runtime agreement cannot
waive raw byte differences.

Each checkpoint should be one coherent boundary family, source TU, or
artifact-local acceptance cohort, with focused replay, ledger update,
affected cold aggregate, CI, and a concise handoff update. Do not batch
unrelated artifacts merely to increase a progress number.
