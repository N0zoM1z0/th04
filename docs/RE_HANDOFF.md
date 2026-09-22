# TH04 reconstruction handoff

Updated 2026-09-22. This file is the **current-state entry point**. Versioned
notes under `docs/reconstruction/` are historical experiment snapshots; their
intermediate residual counts are not the live frontier unless repeated here.
Use the CSV ledgers and generated progress reports as the exactness authority.

## Resume here

Read `AGENTS.md`, `docs/ARCHITECTURE.md`, `docs/RE_WORKFLOW.md`, and the relevant
TH04 skill. Then run:

```bash
git status --short --branch
python3 scripts/preflight.py
python3 scripts/status.py
python3 scripts/audit_compat_dependencies.py --check
```

Do not continue from an old version-number narrative in a focused note. Start
from the live facts below and open historical packets only when a current claim
points to them.

## Current verified state

- Target canonicality is `candidate-local-attested`. MAIN.EXE is 156,258 bytes,
  SHA-256 `077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.
- MAIN has **83,442 / 83,469 reviewed authored C/C++ bytes exact** and
  **492 / 494 reviewed authored C/C++ functions exact**.
- The complete reviewed MAIN byte gap is **27 bytes**:
  - checkerboard counted `LOOP`: 2 bytes;
  - Stage 4 carpet low-level instruction-selection residuals: 23 bytes;
  - shared `snd_load` `MOV BX,AX` encoding: 2 bytes.
- MAIN has no provisional authored C/C++ boundaries. `compat/rec98` has zero
  forwarders and zero product include sites.
- OP and MAINE relocation tables are target-index exact after v488/v489:
  **804/804 OP** and **559/559 MAINE**.
- OP and MAINE decoded program images now differ from the target-restored MZs
  only at the same shared two-byte `snd_load` encoding.

## MAIN final blockers

### `snd_load`: 2 bytes

Target TH04 uses `89 C3`; natural TC86 C++ `_BX = _AX` uses `8B D8`.

Accepted facts:

- all other reviewed `snd_load` bytes are source-owned/exact, including the
  DS save/restore spans promoted in v391;
- TH02, TH03, and TH05 homologs use `8B D8`;
- pinned TC4J integrated inline assembly can emit `89 C3`, proving the encoding
  mechanism, but there is no independent TH04 low-level-source provenance;
- ordinary source/register/alias/optimizer/TASM routes already recorded in the
  compiler notes are negative.

Do **not** inject inline assembly merely to select the alternate ModR/M direction.
Reopen only for materially new compiler-version/backend evidence or independent
source provenance.

Primary notes:

- `docs/reconstruction/main/TH04_SND_LOAD_DS_V391.md`
- `docs/reconstruction/main/TH04_MAIN_FIXUP_CODEGEN_PROBES.md`

### Checkerboard: 2 bytes

The 174-byte function has **172 natural exact bytes**. The only blocked owner is
target `E2 F7` (`LOOP -9`). Natural counted-loop spellings, accepted optimizer
surfaces, same-media IDE probing, intrinsics, cross-game/cross-artifact scans,
and semantic-lineage searches do not justify target-derived inline assembly.

Do not re-run the existing countdown spelling/optimizer matrices without a new
compiler mechanism or independent source clue.

Primary note: `docs/reconstruction/main/TH04_MAIN_CHECKERBOARD_V396.md`.

### Stage 4 carpet: 23 bytes

`carpet_lighting_put_new()` is partitioned into **67 natural exact + 23 blocked
bytes**. The v421 hybrid proves the remaining instruction forms can be emitted
by TC4J integrated assembly, but it remains quarantined: no independent target
or source provenance establishes original low-level ownership.

Closed natural-codegen families include the DS/ES transfer, unsigned `MUL BX`,
`LODSB`, `SHL DI,1`, and compact `LOOP` shapes already covered by v409-v424.

Primary note: `docs/reconstruction/main/TH04_MAIN_KURUMI_CARPET_V174.md`.

## OP / MAINE packed state

Use the **v228 target-derived DIET restores** as the target preimage reference.
Do not use the older v231 restored-candidate inverse control as a target Oracle.

Current facts:

- v488/v489 close all SCORE/BGIMAGE relocation-order residuals naturally; OP and
  MAINE relocation order is fully target exact.
- v490 proves `e_minalloc` is derived from the file-backed load extent and the
  unchanged initial `SS:SP`; it is not an independent search variable.
- v492 gives a natural TASM/TLINK mechanism for the target `T` extents: file-
  backing the shared 0xC6 MASTER BGM BSS zero span yields exact TH04 OP/MAINE
  load extents and minalloc while preserving the program prefix and relocation
  tables. TH05 targets independently corroborate the same physical BGM span.
- v493 proves the pinned generic `masters.lib` is not the exact MASTER object set
  used by ZUN: generic gaiji objects retain the official `ADC 5680h` bug while
  TH04/TH05 targets contain ZUN's corrected `ADD` form. Therefore generic
  `b_data.OBJ` is not definitive negative evidence about ZUN's modified object.
- v494 finds an independent project-history representation of the same file-
  backing surface. ReC98 Reduction #172 (2014) used `timerorg dd ?` plus
  `part/esound dup(<0>)` specifically to avoid MZ header-size changes. Replaying
  that exact historical blob reproduces the v492 TH04 outputs byte-for-byte.
  This is a binary-preserving reconstruction representation, **not** a claim
  that ZUN's original source used zero initialization.
- With `T` and relocation order exact, pinned DIET leaves only the shared
  `snd_load` two-byte program residual. A private P-only diagnostic control packs
  OP and MAINE raw-exact; it grants no source credit.

Do not reopen BGIMAGE relocation order, SCORE owner order, `minalloc`, DIET
relocation sorting, TLINK `/i`, or the already-tested TLINK/TASM option surfaces
without materially new evidence.

Primary packed notes:

- `docs/reconstruction/op-maine/TH04_BGIMAGE_HYBRID_V489.md`
- `docs/reconstruction/op-maine/TH04_OP_SCORE_GROUP_V488.md`
- `docs/reconstruction/packed/TH04_DIET145F_MZ_PARTITION_V231.md`
- `docs/reconstruction/packed/TH04_BGM_BSS_FILEBACK_V492.md`
- `docs/reconstruction/packed/TH04_ZUN_MASTER_VERSION_V493.md`
- `docs/reconstruction/packed/TH04_BGM_BSS_REDUCTION172_V494.md`

## Closed routes that should not be repeated by default

- supplied-HDI deleted/free/slack/source-remnant forensics (v413-v419);
- pinned ReC98 2023 decompilation history plus the complete documented
  MAGNet2010 TH04 transcription lineage (v495-v496): all nine tag-changing
  history commits keep tag-bearing hunks in demo/input/EMS/memory material and
  never independently witness checkerboard, carpet, or snd_load low-level source;
- TC4J -WX / DPMI16 final-blocker codegen (v497): the switch is
  demonstrably active via CODE SEGDEF alignment but does not change the tested
  register, LOOP, LODSB, or DS-to-ES instruction selections;
- TC4J processor-target codegen (v498): default/80186/80286/80386/80486
  selection yields no target register/core or LODSB forms; only 386/486 can
  compile the checkerboard _EAX forms and neither profile emits LOOP;
- TC4J C/C++ language mode (v499): a front-end sentinel proves real C versus
  C++ selection, but the tested register/MUL/DS-ES, checkerboard countdown, and
  fixed-SI byte-load lowerings remain byte-identical and avoid the target forms;
- TC4J inline pseudo-register return propagation (v501): helpers returning
  _AX fully inline across direct, INT 21h, and DOS-open-shaped forms, but the
  resulting AX-to-BX transfer remains 8B D8; a local temporary spills/reloads
  through memory rather than selecting target 89 C3;
- checkerboard ordinary countdown source spellings / accepted optimizer / IDE /
  cross-artifact scans (v396, v398, v404-v406), plus inline-expansion boundary
  placement (v502): a small body helper inlines byte-identically while helpers
  owning the countdown remain CALL-based; none emits LOOP;
- carpet natural opcode/source-lineage/cross-artifact scans (v396, v404-v405,
  v409-v424), plus inline-helper expansion (v503): all tested helpers fully
  inline but preserve the non-target IMUL, MOV/INC, register-direction,
  zeroing, doubling, and shift lowerings;
- `snd_load` ordinary register/alias/codegen and cross-game provenance searches
  documented through v391/v392 and the compiler probe notes;
- active TLINK 6.10 `/i`, `/e`, `/P`, `/f` and related layout-switch searches
  (v436/v441);
- DIET relocation sorting as an explanation (v447);
- pinned TASM32 5.0 option/version-emulation as the relocation-order cause
  (v453);
- generic historical `b_data.OBJ` member boundaries alone as the `T` mechanism
  (v491).

A new attempt is justified only if it introduces a genuinely new evidence
source, compiler/backend mechanism, historical toolchain version, or physical
producer model.

## Ordered work queue

1. **MAIN final 27 bytes.** The highest-value new provenance source is the
   1998-07-02 public TH04 trial. v500 provides a fail-closed structural intake
   gate for a private `GEN_TS1.EXE` candidate, but no candidate bytes are
   currently attested. Do not infer blocker bytes from public metadata alone.
   Otherwise seek only genuinely new provenance or compiler/backend mechanisms;
   do not re-run closed matrices.
2. **Packed source provenance.** Technically the container is constrained to the
   shared `snd_load` two bytes; the exact historical ZUN MASTER BGM object/source
   behind the file-backed BSS surface remains unavailable. Do not turn private
   controls into product source.
3. **Standalone build/runtime.** After source/link closure produces the artifacts
   under test, add bounded deterministic PC-98 runtime scenarios. The existing
   runtime script is only a pinned headless-host smoke and must fail closed on an
   uncalibrated/missing emulator.

## Private evidence retention and cleanup

Never commit targets, game assets, disk images, compiler installations, expanded
cold-build trees, or private receipts.

Always keep:

- `.analysis/targets/`;
- `.analysis/toolchain/`;
- `.analysis/runtime/` when the retained image is present;
- `.analysis/ghidra/`, `ghidra-project/`, and boundary-review inputs;
- `.analysis/reconstruction/receipt-archive/`;
- the current DIET v218/v228/v231 observations under `.analysis/reconstruction/`.

Keep these expanded source snapshots because current replay commands still use
them:

- `.analysis/gpt-web/v401-master-vs-object-replay-001/a/source`;
- `.analysis/gpt-web/v402-opmusic-hybrid-replay-001/a/source`;
- `.analysis/gpt-web/v489-bgimage-hybrid-replay-003/a/op/source`;
- `.analysis/gpt-web/v489-bgimage-hybrid-replay-003/a/maine/source`.

Everything else under `.analysis/gpt-web` should be treated as disposable unless
it is referenced by tracked evidence/docs. Use:

```bash
python3 scripts/prune_analysis.py --compact-referenced          # dry run
python3 scripts/prune_analysis.py --apply --compact-referenced  # prune + safe receipt compaction
```

Referenced directories are compacted only when tracked references are limited
to the directory/receipt plus explicitly configured small replay dependencies.
A small explicit `superseded_compact_dirs` allowlist covers human-reviewed old
replays whose `a/source` snapshots have been replaced by later retained source
trees; their historical command strings may therefore mention paths that are no
longer kept locally. The durable evidence is the receipt/hash, not permanent
retention of every cold-build tree. Expanded exact-unit replay trees can likewise
be regenerated from checked-in source once their receipt SHA-256 is durable.

## Finish every reconstruction packet

Run focused replay and the complete affected aggregate before exact promotion,
then:

```bash
python3 scripts/preflight.py
python3 scripts/ci.py
git diff --check
```

Record artifact, segment:offset, evidence class, replay/receipt, result, and the
remaining unknown in the focused note and ledgers. Never promote a target-derived
control merely because it is byte-exact.
