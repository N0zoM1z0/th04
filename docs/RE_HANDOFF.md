# TH04 reconstruction handoff

Updated 2026-09-21. This file contains only live state and the next work queue.
Use focused reconstruction notes and the CSV ledgers for experiment history.

## Resume here

Read `AGENTS.md`, `docs/ARCHITECTURE.md`, `docs/RE_WORKFLOW.md`, and the relevant
TH04 skill. Then run:

```bash
git status --short --branch
python3 scripts/preflight.py
python3 scripts/status.py
python3 scripts/audit_compat_dependencies.py --check
```

## Current verified state

- Target canonicality is `candidate-local-attested`. MAIN.EXE is 156,258 bytes,
  SHA-256 `077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.
- MAIN has **83,442 / 83,469 reviewed authored C/C++ bytes exact** and
  **492 / 494 reviewed authored C/C++ functions exact**.
- The accepted MAIN byte gap is **27 bytes** only: checkerboard `LOOP` (2),
  Stage 4 carpet low-level residuals (23), and `snd_load` `MOV BX,AX` (2).
- Latest accepted complete MAIN aggregate is
  `gpt-web-v410-carpet-frame-aggregate-final-001`, receipt SHA-256
  `d1c5af30fe7419391e48b60156b87b8d4ccb5202ca7e7ca216f18e1c877c2487`.
- The v421 carpet hybrid is **quarantined**. It proves that TC4J integrated
  assembly can reproduce the 23 residual bytes and link the whole function
  exactly, but it lacks independent historical source provenance. v409/v410
  natural-source ownership remains authoritative: 67 exact + 23 blocked.
- Checkerboard is similarly reduced to one two-byte `E2 F7` blocked owner.
  Natural source/optimizer/IDE/cross-artifact/semantic-lineage searches do not
  justify target-derived inline assembly.
- `snd_load` is reduced to target `89 C3` versus natural TC4J `8B D8`. TH02,
  TH03, and TH05 homologs use `8B D8`; integrated assembly explains the TH04
  encoding mechanism but does not prove original inline-ASM provenance.
- The compiler/provenance searches through v424 and the supplied-HDI forensic
  searches are closed negative. Do not repeat them without a materially new
  evidence source.
- OP/MAINE diagnostic payload candidates now differ only at shared `snd_load`
  (2 bytes each) after the master/object and OP-music topology work.
- **Important v425/v427 correction:** their relocation-order reference is the
  v231 **restored-candidate inverse control**, not the DIET-restored target and
  not a historical pre-DIET MZ. OP's 804/804 ordering and MAINE's two-entry
  residual are candidate-to-candidate topology diagnostics only. Do not use
  that ordering as a target acceptance Oracle.
- v429 rebases the current v427 OP and v425 MAINE candidates onto the actual
  v228 target-derived DIET restore. Relocation-site multisets remain equal, but
  ordered indices differ at **223 / 804** OP entries and **299 / 559** MAINE
  entries. The changed owner set is now localized; next packed work should test
  physical segment/object cuts, not the v231 candidate-control ordering.
- v430 localizes the v228 restored MZ zero-tail EOF to the end of the shared
  MASTER.LIB BGM BSS (`_snd_load_fn`, exactly `0xC6` after `timerorg`) in both
  OP and MAINE. Independent historical `b_data.OBJ` has that exact `0xC6` BSS
  layout but **no BSS LEDATA/LIDATA**, so do not materialize the v228 zero tail
  in source merely to imitate a DIET-restored preimage. v446 later confirms the
  target container's logical unpacked length, but not TLINK `minalloc` origin.
- v436 re-packs the current candidates: OP is 42,256 vs target 42,290 and
  MAINE 37,989 vs 38,035. Private target-derived `R+T` controls land exactly
  one packed byte short in both; adding the two-byte `snd_load` `P` residual
  makes `PRT` raw exact. This is localization only, not product acceptance.
- v436 also closes active TLINK 6.10 `/i` (`Initialize all segments`) as the
  missing `T` mechanism. Natural `/i` packs +93 OP / +167 MAINE bytes over
  target, and even target-derived payload+relocation controls retaining `/i`'s
  own extent/minalloc remain +79/+119. Do not repeat `/i` on this linker.
- v441 closes the remaining obvious active-TLINK switch surface: `/e`, no
  extended-dictionary switch, and `/P` reproduce current OP/MAINE EXE/MAP and
  relocation order byte-for-byte; `/f` changes >1.2 KiB of program bytes and
  changes relocation counts/multisets. Do not revisit these switches by default.
- v446 uses DIET 1.45f's bundled-documented hidden `-^` diagnostic. The packed
  targets themselves report `unpacksize=0x12C40` OP (76,864) and `0x10E62`
  MAINE (69,218), exactly v228 restored sizes. `T` file length is therefore a
  real packed-container constraint, while historical relocation order and
  `minalloc` provenance remain open. MAINE `T` alone also selects target
  `dlzflag=0x30` / 496-byte SFX overhead; `P/R` alone stay `0x20` / 444.
- v447 proves pinned DIET 1.45f preserves relocation-table order: five legal
  private orders per artifact all pack differently and all `-RA` roundtrip
  byte-exact. Therefore v228's target-restored relocation order is now a
  **packed-container constraint**. The blocker is recovering its natural
  OMF/FIXUPP/link cause, not deciding whether DIET sorted the table.
- v448 decomposes that order at OMF-record granularity. OP/MAINE master DATA
  and both OP music FIXUPP records are exact per-record reversals; BGIMAGE also
  projects as one reversed record. OP `hi_view` is different: FIXUPP 76 is exact
  while FIXUPP 74 rotates left by 9, yielding target runs 74×23, 76×29, 74×9.
  MAINE monolith similarly interleaves multiple records. Treat assembler
  emission direction and historical TU/object ownership as separate blockers.
- v453 closes pinned TASM32 5.0 option/version emulation as the source of
  those pure reversals. Real OP music OMF/multipass variants keep current order;
  symbolic `/uT100..T500` and MASM compatibility fixtures remain ascending even
  when FAR-call fixup kind changes. Look for a different producer or TU shape.
- v461 recovers a natural OP topology instead of permuting MZ entries. TC86
  4.02 naturally emits the four `SND_LOAD_EXT` pointer FIXUPPs in target reverse
  order; placing that data-only owner after `snd_load`, moving master tail after
  PI load, and placing OP music after `op_setup` keeps the payload unchanged and
  the 804-site multiset exact while cutting ordered mismatch **223 -> 105**. The
  `SND_LOAD_EXT` block is exact at indices 158..161. Remaining OP R is only
  BGIMAGE 8, OP music 35, and `score_e`/`hi_view` 63 relocation entries.
- MAIN has no provisional authored C/C++ boundaries. `compat/rec98` has zero
  forwarders and zero product include sites.

## Ordered work queue

1. **MAIN final 27 bytes:** continue only with genuinely new independent source
   provenance or a new legal compiler mechanism. Do not reopen already-closed
   optimizer, register-form, HDI-remnant, or cross-game scans by default.
2. **OP/MAINE packed closure:** continue from v461 for OP and v448 for MAINE.
   OP global owner order is now aligned through OP music; attack only BGIMAGE
   internal direction, OP-music internal direction, and the `hi_view` /
   `score_e` historical TU split. MAINE still needs its monolith interleavings.
   Preserve target-attested unpacked lengths 76,864 / 69,218 and v228 relocation
   order. Historical `minalloc` provenance remains unresolved. Active TLINK 6.10
   switch routes and pinned TASM5 option/version emulation are closed; do not
   hand-permute the table.
3. **Standalone build/runtime:** after source/link closure can produce the
   artifacts under test, add deterministic DOSBox-X runtime scenarios.

## Private evidence retention

Expanded cold-build trees are disposable once their receipt SHA-256 and checked-
in evidence rows are durable. Keep targets, toolchains, runtime image, Ghidra
database, boundary-review inputs, `receipt-archive/`, and the current DIET v218/
v228/v231 observations.

For current OP/MAINE replay dependencies, keep only these source snapshots:

- `.analysis/gpt-web/v401-master-vs-object-replay-001/a/source`
- `.analysis/gpt-web/v402-opmusic-hybrid-replay-001/a/source`

Keep receipt-only directories for current blocker/frontier evidence, especially
v391, v396, v398-v406, v411-v420, v423-v427, v429-v430, v436, v441, v446-v448, v453, v461. Superseded scratch matrices,
second A/B source copies, and expanded exact-unit replay trees can be deleted
and regenerated from checked-in source.

## Finish every packet

Run focused A/B replay and the complete affected aggregate before exact
promotion, then:

```bash
python3 scripts/preflight.py
python3 scripts/ci.py
git diff --check
```

Record artifact, segment:offset, evidence class, replay/receipt, result, and
remaining unknowns in the focused note and ledgers. Never commit original
executables, game assets, disk images, compiler installations, or private
analysis output.
