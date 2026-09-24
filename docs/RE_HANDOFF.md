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
| OP.EXE | 30 / 55 / 8 | 27 | 66 / 0 | 2,876 |
| MAINE.EXE | 34 / 33 / 5 | 29 | 43 / 0 | 2,700 |
| ZUN.COM | 13 / 0 / 0 | 0 | 11 / 2 | 404 |

OP's 2,876 source-owner bytes include two source-present but nonexact SCORE
codec candidates (274 bytes); 2,602 bytes are in the 27 accepted exact
functions. MAINE has 29 decoded-function exact functions (2,511 bytes), plus
two source-present/nonexact SCORE codec candidates (`scoredat_decode` 88 bytes
and `scoredat_encode` 101 bytes); total decoded source-owner bytes are 2,700.
These are decoded-function extents, not packed-file byte totals. No honest
packed-file denominator exists yet for OP, MAINE, or ZUN. MAIN is not on the
active reconstruction path: its 492/495
accepted authored functions and 27 file-backed authored bytes remain an
evidence-triggered side lane.

## Latest verified cohort: OP/MAINE small leaf batch

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
are disposable; current private acceptance directories retain only their small
receipts. Delete experiment intermediates immediately after recording their
receipt, and preserve only artifacts covered by `config/analysis_retention.toml`.

Do not reopen MAINE `scoredat_recreate` at payload `0xC206` or the v582-v585
leaf batch: their complete decoded-function extents now pass raw-zero
acceptance. Select the next small unit from fresh OP/MAINE/ZUN boundary and
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
