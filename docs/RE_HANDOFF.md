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
- v463 recovers `zunsoft_pyro_new()` as a natural TC86 C++ function. Its
  linked 0x84 bytes at load `0xBA45` are target-exact and the whole OP program
  image is unchanged. TC86 emits its two far-call segment FIXUPPs in descending
  address order (`0x59`, `0x48`), matching the direction required by the target
  OP-music block. Mixed C++/ASM ownership keeps the global residual at 105; next
  recover the remaining 0x40C ZUNSOFT tail as C++ rather than reversing entries.
- v464 recovers `zunsoft_update_and_render()` as another linked-exact TC86
  function: 0x12B bytes at load `0xBAC9`. Together v463/v464 form a 0x1AF-byte
  natural C++ owner; its eight segment FIXUPPs are all emitted high-address
  first, exactly the local direction required by the target OP-music reversal.
  The remaining ZUNSOFT TASM tail is now only 0x2E1 bytes (palette + animate).
- v465 recovers `zunsoft_palette_update_and_show()` as 65/65 raw-and-linked
  exact natural C++. The TC86 owner is now 0x1F0 bytes with nine descending
  segment FIXUPPs; only `zunsoft_animate()` remains as a 0x2A0 TASM tail.
- v466 completes `zunsoft_animate()` and the entire 0x490-byte ZUNSOFT owner
  as one TC86 C++ TU. Linked owner bytes are target-exact; all 35 OP-music
  relocation entries at indices 271..305 are now target-index exact without MZ
  edits. OP ordered residual drops **105 -> 71**: BGIMAGE 8 plus
  `score_e`/`hi_view` 63. `#pragma option -a2` naturally supplies the switch-table
  pad; the exact historical spelling of the adjacent alive/age 16-bit zero
  statement remains a source-text caveat only, not a linked-byte blocker.
- v468 recovers two MAINE producer directions without moving their global
  blocks. TC86 naturally reverses the four `SND_LOAD_EXT` pointers, and compiling
  `score_e + hi_end` as one SCORE_TEXT TU keeps linked bytes unchanged while
  emitting `hi_end` 18 relocations before `score_e` 2, exactly the target-local
  order. These 24 entries are producer-closed; MAINE still stays at 299 global
  mismatches because `th04_maine.asm` must split into its target-attested
  139-entry `MAINE_01_TEXT` and 36-entry `SCORE_TEXT` owners.
- v470 performs that split at the existing assembly segment boundaries. A
  source-level MAINE_01 owner (139 kind-3), SCORE owner (36), and rest/data owner
  keep the complete program image byte-identical; combined with v468 producers,
  every global block through SCORE_TEXT is target-position exact. MAINE ordered
  mismatch drops **299 -> 178** (381/559 same-index). Remaining MAINE R is only
  BGIMAGE 8 plus internal FIXUPP order of MAINE_01 136 and SCORE 34.
- v471 recovers `graph_3_digit_put()` from the maintained verdict.cpp semantic
  shell as **150/150 raw-and-linked exact TC86 C++**. Replacing the function
  inside the v470 MAINE_01 owner preserves the entire MAINE EXE and all 559
  relocation entries byte-for-byte. This gives positive C++-producer evidence
  for the MAINE_01 residual; continue with the adjacent skill/fraction helpers.
- v472 recovers `skill_apply_and_graph_percentage_put()` as **245/245 raw-and-
  linked exact TC86 C++**. The whole MAINE program image stays unchanged; its
  two `graph_putsa_fx` segment FIXUPPs naturally reverse to target indices
  254..255, reducing ordered residual **178 -> 176**. Continue directly with
  adjacent `graph_fraction_of_million_put()`, then grow the same verdict owner.
- v473 recovers `graph_fraction_of_million_put()` as **119/119 raw-and-linked
  exact TC86 C++**. The complete v472 relocation table remains byte-for-byte
  unchanged, so residual stays 176; its one segment relocation was already at
  the correct index. The three adjacent verdict helpers are now source-recovered;
  continue into the larger following verdict logic beginning at `sub_B9F2`.
- v474 fuses `graph_3_digit_put + sub_B81D + skill + fraction + sub_B9F2`
  into one **0x3FA linked-exact TC86 MAINE_01 owner**. TC86's first-declaration
  code-segment rule is essential: graph3 must first be declared under the
  MAINE_01 pragma. One high-address-first FIXUPP record makes indices 251..258
  target-exact and reduces MAINE ordered residual **176 -> 170**. Continue with
  following `sub_BB81`, whose target segment run is indices 259..273.
- v475 recovers `sub_BB81()` as **0x577 raw-and-linked exact TC86 C++**,
  including both compiler switch tables. The complete MAINE image stays
  unchanged; target indices 259..273 become exact and ordered residual drops
  **170 -> 157**. Only the adjacent 0x51 `verdict_animate()` TASM tail remains
  in this verdict run before re-measuring the MAINE_01 producer frontier.
- v476 recovers `verdict_animate()` as 81/81 raw exact and fuses it with
  `sub_BB81` into one 0x5C8 TC86 TU. Linked bytes remain exact; target indices
  274..290 become exact and MAINE ordered residual drops **157 -> 140**. The
  verdict run is now fully C++; continue earlier MAINE_01 producer recovery.
- v477 recovers the first four staff-roll helpers as one **0x3C1 / 961-byte
  raw-and-linked exact TC86 C++ owner**. Compiler FIXUPP order naturally matches
  `B25B -> B144 -> B02D -> AED0`; target indices 152..194 become exact and
  MAINE ordered residual drops **140 -> 98**. Continue the contiguous
  `B291/B31E/B3AC + staffroll_animate` block.
- v478 completes all eight staff-roll functions as one **0x8B7 / 2231-byte
  raw-and-linked exact TC86 C++ owner**. Target indices 195..250 become exact;
  MAINE ordered residual drops **98 -> 42** and MAINE_01 internal order is fully
  closed. Remaining MAINE R is SCORE_TEXT 34 + BGIMAGE 8.
- v479 starts SCORE_TEXT producer recovery. The leading `0x154` registration
  score-insertion helper is **340/340 raw-and-linked exact TC86 C++**. Splitting
  only this function preserves the entire v478 MAINE image and all 559
  relocation entries byte-for-byte, so residual stays 42 by design. Continue
  adjacent SCORE helpers to grow one natural TC86 SCORE_TEXT owner.
- v480 extends that SCORE owner through the adjacent score and stage renderers.
  `score_insert + score_put + stage_put` are **0x2B3 / 691 raw bytes exact** as
  one TC86 TU. Its five segment FIXUPPs are already in the target-local order
  required at indices 327..331; global residual remains 42 only because the
  higher-address SCORE helpers are still in the following TASM owner. Continue
  from `sub_C665` and grow the same producer forward.
- v481 adds the name/cursor renderer and grows the natural SCORE owner to
  **0x35F / 863 linked-exact bytes**. Cross-game TH02 source supplies the exact
  gaiji string-pointer spelling; the only raw difference is a same-segment near
  call addend to the later private copy helper. Eight segment sites now appear
  in the exact target-local sequence for indices 324..331. Continue `sub_C711`
  and higher-address SCORE helpers in the same TC86 owner.
- v482 recovers `sub_C711`, `sub_C7C9`, and `sub_C7E3` as raw-exact
  natural C++ and grows the SCORE prefix to **0x462 / 1122 linked-exact bytes**.
  Its 12 segment sites map exactly to target-local indices 320..331. The
  temporary split residual is 43 (not an improvement) because higher-address
  `regist_menu`/EGC code is still a following TASM object; continue fusing that
  tail into the same TC86 TU.
- v483 narrows `regist_menu()` to a **920/924-byte natural TC86 C++
  frontier** at the exact 0x39C target size. Only one zero-test peephole remains:
  candidate `MOV AX,[key_det] / OR AX,AX` versus reference `CMP [key_det],0`;
  the following JZ/JMP and every other function byte are exact. Bounded
  control-flow/type/scope plus `-O/-y/-Z` probes do not close it without
  perturbing exact code. This packet is explicitly non-exact/no-credit. The
  natural SCORE prefix reaches 0x7FE bytes; only the 0xCA EGC tail remains.
- v484 recovers the final `score_rect_copy()` as **0x86 linked-exact natural
  TC86 C++**. Its raw differences are only same-segment near-call addends caused
  by splitting it from the preceding EGC-start helper; TLINK restores identical
  final bytes and the entire 559-entry relocation table remains unchanged. The
  exact SCORE frontier is now v482 prefix + this final copy helper; only the
  4-byte `regist_menu()` compiler peephole and 0x43 EGC-start helper remain.
- v485 closes the remaining 0x43 EGC-start helper and fuses it with the v484
  copy helper into a **0xC9 raw-and-linked exact TC86 C++ tail**. The key legal
  mechanism is `decomp.hpp::keep_0(0)`, independently used by TH05 for the same
  EGC address-register zero write. Program bytes and all 559 relocation entries
  stay unchanged. Only the v483 four-byte `regist_menu()` zero-test frontier
  remains inside SCORE_TEXT.
- MAIN has no provisional authored C/C++ boundaries. `compat/rec98` has zero
  forwarders and zero product include sites.

## Ordered work queue

1. **MAIN final 27 bytes:** continue only with genuinely new independent source
   provenance or a new legal compiler mechanism. Do not reopen already-closed
   optimizer, register-form, HDI-remnant, or cross-game scans by default.
2. **OP/MAINE packed closure:** continue from v466 for OP and v448 for MAINE.
   OP global owner order and the complete ZUNSOFT/OP-music producer are closed.
   Attack only BGIMAGE internal direction (8 relocation entries) and the
   `hi_view` / `score_e` historical TU split (63 entries). MAINE global block placement is closed through SCORE_TEXT. v471-v475 recover the verdict path through `sub_BB81`; continue the remaining `regist_menu()` four-byte compiler frontier;
   then re-evaluate SCORE record ownership before shared BGIMAGE direction.
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
v391, v396, v398-v406, v411-v420, v423-v427, v429-v430, v436, v441, v446-v448, v453, v461, v463-v466, v468, v470-v483. Superseded scratch matrices,
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
