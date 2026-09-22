# TH04 reconstruction roadmap

Updated 2026-09-22. Live counts come from `python3 scripts/status.py` and
`docs/PROGRESS.md`; regenerate them rather than editing counts here. This
replaces MAIN-last-bytes-first work. MAIN's 27 bytes are an evidence-triggered
side lane, not a dependency for the other artifacts.

## 1. Establish OP/MAINE/ZUN acceptance surfaces

OP and MAINE have mature decoded-image/link Oracles, but lack a general
artifact-local function-acceptance ledger and accepted packed-file byte
extents. Extend the all-artifact boundary ledger or introduce a common
function ledger with explicit decoded segment:offset, complete physical
extent, source owner, artifact-local cold replay, ordered relocation/layout
comparison, and evidence references. Keep decoded function acceptance apart
from `units.csv` raw-file exactness. Never invent packed `file_offset` values
to make a percentage. Rebase ZUN's component replay on checked-in source and
headers, then add missing link inputs incrementally. Preserve OP/MAINE SCORE
TU composition and v489/v494 aggregate Oracles during each source edit. The
[replay handoff](reconstruction/packed/TH04_NONMAIN_REPLAY_HANDOFF_V507.md)
names working commands and gaps.

## 2. Harvest maintained shared source in small cohorts

For each of OP and MAINE, ten reviewed functions (633 decoded bytes) already
have maintained `src/shared/` source: VRAM/frame delay, PI palette/put/load,
and PMD/MMD/KAJA/mode/measure sound functions. Review each artifact's physical
extent and compare its own cold output. A hardware/PI cohort and a sound
cohort per artifact make focused, reviewable checkpoints. The three BGIMAGE
functions per artifact are already decoded/link-exact; only replay
maintenance and later packed-file accounting remain.

## 3. Reconcile boundary and origin alongside mature TUs

Review the 21 provisional authored boundaries by neighboring ownership:
OP's eight (prioritize Ghidra-only `FUN_1da1_09d8` and noncontiguous music/main
owners), MAINE's seven (the three MAP-public sound entries first, then
cutscene/registration), and ZUN's six (review ZUNINIT as one contiguous
physical block). For each, inspect attested target entry, callers, all
returns/tails, tables, alignment, adjacent bytes, MAP/TASM contribution, and
segment identity. A provisional owner cannot be promoted exact, but it need
not block an unrelated reviewed source TU.

Classify the 40 unresolved `target-derived-asm` authored candidates by
subsystem and independent producer fingerprints: OP ZUNSOFT animation 4;
MAINE staff/verdict/registration/EGC families 25; ZUN ZUNINIT/MEMCHK 11.
This is an authority question, not an instruction to transcribe disassembly
as source. Independently attest the 35 non-MAIN `attest-asm` observations
(OP 16, MAINE 15, ZUN 4) without counting them as authored C/C++ progress.

## 4. Reconstruct by physical translation unit

OP first: SCORE (`score_db + score_e + hi_view` as one producer), small
input/vector/init helpers, title/setup, music and character units, then
larger main/animation units after their boundary/origin reviews. MAINE:
SCORE (`score_d + score_hi + complete score`), small ending/cutscene helpers,
then large cutscene and staff/verdict/registration families only after their
respective physical reviews. Candidate byte totals in the boundary inventory
are **not** exact denominators; prioritize by evidence maturity and TU/link
impact, not by address order or attractive percentage.

ZUN: first accept or decisively block `cfg_init` at decoded `_TEXT`
`0xDCF..0xE66` (152 bytes), while keeping resident `_main` at
`0xE67..0xF62` source-present with a six-byte blocker (246 natural versus 252 target bytes).
Then ZUNINIT/MEMCHK origin and component ownership, external library
replacement, composite link, and finally the DIET-packed container. Rebase
the historical v214 component driver before claiming a full replay.

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
