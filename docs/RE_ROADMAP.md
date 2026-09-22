# TH04 reconstruction roadmap

Updated 2026-09-22. Live counts come from `python3 scripts/status.py` and
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
Next, write bounded cold backends for the remaining maintained shared
OP/MAINE owners, then incrementally replace ZUN's external link inputs.
Keep decoded function acceptance apart from `units.csv` raw-file exactness;
never invent packed `file_offset` values. Preserve OP/MAINE SCORE TU
composition and v489/v494 aggregate Oracles during every source edit. A new
backend must actually compile the claimed source and compare its own artifact;
the BGIMAGE backend cannot grant credit to another TU.

## 2. Harvest maintained shared source in small cohorts

The currently maintained reviewed shared hardware/PI/sound cohort is now
complete in both OP and MAINE: three BGIMAGE functions plus VRAM, frame delay,
three PI functions, PMD, MMD, KAJA, mode detection, and delay-until-measure.
That is 13 decoded-exact functions / 840 source-owner bytes per artifact.
MMD keeps its 47-byte natural-C body separate from the following target 0x90
padding, and MAINE delay keeps target 0xD077 linker fill outside its authored
extent. These accepted functions now need replay maintenance and later
packed-file accounting. v540 has now target-reviewed the decode/encode/recreate
SCORE codec boundaries in both OP and MAINE, but their pinned ReC98
implementation history is explicitly decompilation provenance and grants no
source credit. Continue SCORE by reviewing the remaining hiscore view/end
physical owners, while keeping source authority separate from byte/codegen
corroboration.

## 3. Reconcile boundary and origin alongside mature TUs

Review the 15 remaining provisional authored boundaries by neighboring ownership:
OP's eight (prioritize the Ghidra-only and noncontiguous music/main owners) and
MAINE's seven (the remaining MAP-public/sound and cutscene/registration entries).
ZUN's authored physical boundaries are already fully reviewed by v520/v521.
For each remaining owner, inspect attested target entry, callers, all returns/tails,
tables, alignment, adjacent bytes, MAP/TASM contribution, and segment identity.
A provisional owner cannot be promoted exact, but it need not block an unrelated
reviewed source TU.

Classify the 40 unresolved `target-derived-asm` authored candidates by
subsystem and independent producer fingerprints: OP ZUNSOFT animation 4;
MAINE staff/verdict/registration/EGC families 25; ZUN ZUNINIT/MEMCHK 11.
This is an authority question, not an instruction to transcribe disassembly
as source. Independently attest the 35 non-MAIN `attest-asm` observations
(OP 16, MAINE 15, ZUN 4) without counting them as authored C/C++ progress.

## 4. Reconstruct by physical translation unit

OP first: finish SCORE physical review without importing the decompiled candidate
C++; then small input/vector/init helpers, title/setup, music and character units,
and larger main/animation units after boundary/origin review. MAINE: finish the
remaining hiscore/end SCORE owners in the grouped physical producer, again keeping
decompilation provenance separate from source acceptance; then small ending/cutscene
helpers and the larger cutscene/staff/verdict/registration families after their
respective physical reviews. Candidate byte totals in the boundary inventory
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
