# Current handoff

## Phase

Control-plane, target-ingestion, build-chain calibration, headless Ghidra, and
the optional DOSBox-X headless host smoke are ready for handoff. The first
large `MAIN.EXE` authored reconstruction batch is also cold-replayed and
accepted. After the no-Ghidra/public/internal audits, natural `dialog_animate`, shared script-parameter recovery, exact `snd_mmd_resident`, the contiguous midboss/HUD/defeat TU recovery, the v21 contiguous `MAIN_035`/boss TU recovery, and target-driven recovery of `chasecrosses_add` from the formerly unowned `MAIN_034` prefix, reviewed authored C/C++ bytes are 29,934 / 29,965 (99.896546%) exact, and reviewed authored functions are 210 / 212 (99.056604%) exact. Nine standalone original-style ASM units totaling 1,489 bytes are
separately exact and are not counted in the authored C/C++ percentage. No
deterministic TH04 runtime scenario has been authored.

## Verified locally

- The supplied RAR contains a Japanese Anex86 `zun.hdi` and a separate Chinese
  image.
- The Japanese HDI has a 4096-byte Anex86 header, 512-byte physical geometry,
  and a PC-98 FAT partition whose boot sector is at file offset 38912.
- The FAT volume label is `TOUHOU`; TH04 is installed below `GENSO`.
- Sizes and digests for TH04 `OP.EXE`, `MAIN.EXE`, `MAINE.EXE`, and `ZUN.COM`
  are pinned in `config/targets.toml`.
- `ZUN.COM` begins with an MZ header and is intentionally classified as MZ.
- TH01-TH05 private executable artifacts are pinned for cross-version Oracle
  smoke testing; they are calibration inputs and never TH04 progress.
- All 20 pinned artifacts pass size, MD5, SHA-256, byte-detected format, and MZ
  integrity checks.
- Real-corpus self-comparisons and per-game injected invalid-size, header,
  relocation-order, relocated-word, non-relocation program, overlay, load-
  segment, and flat-COM controls pass.
- `MAIN.EXE` has a 6,144-byte header and 1,136 relocation entries.  The other
  three TH04 artifacts have 32-byte headers and no relocation entries; all four
  have relative entry `0000:0000` in this image.
- The deterministic private TH04 `MAIN.EXE` analysis bundle contains a
  150,114-byte load module plus normalized/relocated views and relocation CSV.
- Cross-game candidate mining found multiple raw-identical TH04/TH05 `MAIN`
  runs over 1 KiB, with 1,572 bytes the longest of the recorded top five.
  These are navigation anchors only, not boundary/source/exactness evidence.
- Exact ledger promotion now requires every configured Oracle and rejects
  upstream, cross-game, external, or inference evidence as gate substitutes.
  Target/format evidence binds to the artifact; compilation/layout/raw/cold
  evidence binds to the unit and exact file extent. Forged exact-ledger
  fixtures fail closed on reuse, missing metadata, bad extents, and unequal raw
  hashes.
- `scripts/progress.py` now generates both `docs/PROGRESS.md` and
  `resources/progress.svg` from the ledgers using the established TH095 layout.
  Its check mode detects stale output, and CI rejects generated progress that
  was not committed.
- The local candidate build chain pins and validates TC4J media plus installed
  BIN/INCLUDE/LIB/startup trees, TCC 4.02, TLINK 6.10, TASM32 5.0,
  configuration files, and ReC98's MS-DOS Player P0281 binary. Wine 8.0 is the
  observed host runner, not a portable binary-identity requirement.
- Required acquisition identities are now checked before any downloaded code
  is executed. Host Wine binary hashes are diagnostic for portability; probe,
  cold-build, and exact output results remain mandatory.
- Two execution-probe rounds produced identical C OMF, ASM OMF, map, and MZ
  outputs.  Embedded OMF producers and the compiler's `dos.h` dependency agree
  with the pinned installation; the linked DOS probe executes successfully.
- An empty-clone bootstrap test independently downloaded and rebuilt the
  complete private toolchain, passed all 14 required identity surfaces and
  execution probes, and also matched both calibrated-host Wine diagnostics.
- Three isolated ReC98 cold builds produced the same 20 selected TH01-TH05
  outputs (aggregate identity `80127bc4…e3603e25d`).  All 416 generated OMF
  objects validate structurally and by checksum; each game-specific object set
  reproduces after narrowly normalizing only dependency timestamps.
- Strict target comparison accepts `ZUNSOFT.COM` exactly and rejects
  `OP.EXE`, `REIIDEN.EXE`, and `FUUIN.EXE`: their program images match, but
  header and/or ordered-relocation dimensions do not.  This is a pinned known
  calibration vector, not an exactness waiver.
- The all-game strict survey accepts only TH01 `ZUNSOFT.COM`, TH02 `ZUN.COM`,
  and TH05 `ZUN.COM` (3/20).  Every TH04 candidate is rejected.  TH04 `MAIN`
  retains the target's 1,136 relocation count but has 3,326 program-byte
  differences outside relocation sites; TH04 `OP`/`MAINE` differ broadly in
  content and relocation topology, and the candidate `ZUN.COM` is flat COM
  while the target is MZ.
- The all-game calibration pins source/archive provenance, the cold receipt,
  every candidate hash and compact multi-dimensional vector, the 20-output
  identity, OMF validity, and five per-game normalized OMF identities.  A
  deliberate one-byte candidate mutation makes the gate fail closed.
- Ghidra 12.1.3 and Temurin JDK 21.0.12.1+1 are pinned below `.tools/` with
  exact official archives, complete extracted-tree identities, stable
  `.tools/ghidra` and `.tools/jdk` links, loader source, banners, and headless
  execution attested by `scripts/attest_analysis_toolchain.py`.
- A separate empty temporary fixture replayed archive extraction and stable
  link creation from scratch and passed every identity/execution check twice.
- Private headless databases live under ignored `ghidra-project/`, matching
  TH095's working layout. An attempted `.analysis/` project root was rejected
  by Ghidra because a path element starts with a dot; exports and receipts
  still belong below `.analysis/ghidra/`.
- A clean analyzed TH04 `MAIN.EXE` project and subsequent read-only replay pass
  the independent MZ database Oracle. The checked state has 920 provisional
  auto-analysis functions and 38,666 instructions; these counts are
  navigation state only. The exact checks cover the 156,258-byte target,
  6,144-byte header, 150,114-byte relocated load image, 1,136 relocation
  records, seven source mappings, entry `1000:0000`, timeout state, and eight
  deterministic samples.
- Loader-only real-corpus controls also pass for TH01 `OP.EXE` with 625
  relocations and TH04 `OP.EXE` with zero relocations. Independent loaded-byte,
  relocation, mapping, unexpected cross-category alias, and stale-nonce
  mutations all fail the intended database-Oracle dimension.
- The MZ parser now rejects invalid last-page encodings, inverted allocation
  bounds, and a stack outside minimum allocation while all 20 pinned targets
  continue to pass. The OMF parser rejects concatenated valid modules by
  requiring exactly one THEADR and one MODEND/MODEND32.
- Ubuntu's DOSBox-X 2024.03.01 package is installed and pinned by package
  version plus `/usr/bin/dosbox-x` SHA-256. The checked-in no-GUI profile passes
  PC-98 startup and uses dummy SDL video/audio, isolated XDG state, fixed CPU
  cycles, explicit PIT/GDC settings, and disabled host MIDI.
- The same `candidate-local-attested` Japanese HDI used for target import is
  retained privately below `.analysis/runtime/`, revalidated by SHA-256, and
  enters the DOSBox-X PC-98 image boot path under a hard time limit. This is an
  infrastructure smoke only, not a deterministic TH04 behavior observation.
- `slowdown_frame_delay` is now exact from maintained source. It remains the
  smallest reviewed example at target file `0xC2F2`, load-module `0xAAF2`,
  link/Ghidra `1AAF:0002`, and is replayed by the same checked-in batch driver
  used for the larger authored cohort.
- `scripts/replay_th04_main_exact_units.py` now replays complete maintained
  translation units and identity-preserving natural-source fragments through
  two isolated cold materializations. Latest aggregate receipt
  `gptweb-std-run-v68-final-precommit-web-001` passes all 106 current default-selected
  exact-replay units across raw bytes, containing/exact TLINK placement,
  ordered overlapping MZ relocations, OMF validity, and deterministic output.
- The current reviewed authored byte denominator is 29,965 bytes; 29,934 bytes are exact.
  The reviewed nonexact bytes are four blocked bytes in `snd_load` plus all 27
  bytes of `ENEMY_BULLET_TEMPLATE_PUSH`, whose boundary is complete but whose
  tested natural C++ copy forms do not reproduce the target REP MOVSW setup order.
- `snd_pmd_resident` is fully exact from maintained pure C. After `_ES = 0`,
  `*(void far * __es *)(PMD * 4)` makes TC4J naturally generate the target
  `LES BX, ES:[0180h]`; no inline assembly, `__emit__`, codestring, or raw-byte
  directive is involved.
- The old `MIDBOSS_TEXT` / `HUD_HP_TEXT` / `MB_DFT_TEXT` split is now reviewed
  as a **false reconstruction boundary**. Their target bytes are contiguous
  (`0x5A + 0x58 + 0x119 = 0x1CB`), and target `midboss_defeat_update` uses a
  four-byte `PUSH CS; CALL near` back to `midboss_reset`. Rebuilding all six
  functions in target flat order as one maintained natural-C++ TU makes the
  complete 459-byte range exact; the ordinary `midboss_reset()` call naturally
  emits the target bridge. Focused `gptweb-midboss-tu-v20-002` and 65-unit
  aggregate `gptweb-midboss-tu-v20-default-001` pass raw/map/ordered-relocation/
  OMF/determinism replay. The historical HUD_HP/MB_DFT segment labels become
  zero-length while the following `MAIN_034_TEXT` start remains unchanged.
- The old `MAIN_035_TEXT` / `BOSS_TEXT` split is also a **false reconstruction
  boundary**. Target `0x2DF61..0x2E916` is one contiguous 0x9B6-byte natural-C++
  producer region. The first 0x677 bytes were previously unowned because
  `th04_main.asm` hid `boss_reset`, `bb_boss_load/free`, and `stage1..stagex`;
  pinned TASM local-label offsets plus target raw RET/RETF tiling establish ten
  true function extents and reject Ghidra internal false splits. The following
  historical 0x33F `BOSS_TEXT` is part of the same TU. `src/main/boss/boss.cpp`
  compiles to one 0x9B6 `MAIN_035_TEXT` contribution, leaves `BOSS_TEXT`
  zero-length, and preserves the next `MAIN_036_TEXT` start. Focused
  `gptweb-boss-tu-v21-003` and 65-unit aggregate
  `gptweb-boss-tu-v21-default-001` reproduce all 2,486 bytes and all 60
  overlapping MZ relocation entries in target order. Ordinary
  `bb_boss_free();` naturally emits the target four-byte `PUSH CS; CALL near`
  inside the 468-byte `boss_defeat_update`; no inline ASM or byte emission is
  used. ReC98's TH04 stage2/stage3 semantics were materially wrong and were
  replaced from target raw/decompile evidence rather than copied.
- `chasecrosses_add(unsigned char,unsigned char)` is the first reviewed exact
  function recovered directly from the previously unowned `MAIN_034_TEXT`
  prefix rather than from a ReC98 implementation. Fresh target Ghidra reports a
  contiguous 74-byte body at `0x2A087`; TLINK places the matching public at
  `13A9:65F7`. `src/main/boss/chasecrosses_add.cpp` was derived from target raw
  behavior plus the independently checked structure layout and cold-replays
  74/74 bytes exact. ReC98 supplied only the structure/prototype and was not
  treated as source truth. Because moving a prefix out of monolithic
  `th04_main.asm` changes TLINK's first-segment ordering, replay materializes
  `src/main/layout/main_code_order_anchor.asm`: a zero-code OMF with 50 SEGDEF,
  2 GRPDEF, and **zero LEDATA**. It owns no authored bytes; its only purpose is
  to establish the original global code-segment order before `chase.obj` and
  residual `main.obj`. Focused `gptweb-chasecross-v22-001` and 66-unit aggregate
  `gptweb-chasecross-v22-precommit-003` pass raw/map/ordered-relocation/OMF and
  zero-code-anchor gates.

- The `MAIN_034_TEXT` natural-C++ prefix now extends from 0x4A to **0x89 bytes**.
  Immediately after `chasecrosses_add`, target `0x2A0D1..0x2A10F` is a
  63-byte internal safety-circle initializer. Ghidra creates the correct entry
  but truncates its body to 25 bytes; target raw decode reaches `RET`, the next
  TASM/Ghidra true entry is exactly `0x2A110`, and target near call `0x2ADD6`
  resolves to `0x2A0D1`. The new `reviewed_exact_internal_call` gate requires
  all of those anchors before admitting the function. ReC98's candidate
  `safetycircle_t` tail is also wrong: target writes `col_ring` at `+0x18`, so
  the natural exact layout needs `unused_3[4]`, not `[8]`. Focused
  `gptweb-safetycircle-v23-002` and 66-unit aggregate
  `gptweb-safetycircle-v23-precommit-004` reproduce the complete 137-byte prefix
  and its ordered relocation overlap exactly.

- v24 extends that same `MAIN_034_TEXT` natural-C++ prefix from 0x89 to
  **0x33C bytes** by recovering the adjacent 691-byte internal
  `yuuka6_entities_update()` at target `0x2A110..0x2A3C2`. ReC98 has no
  decompiled implementation. Target raw/TASM semantics plus existing typed
  vector, shot, spark, item, and bullet APIs reproduce the entire gameplay
  routine naturally. TC86 emitted the exact 0x2B3 function size and instruction
  sequence; its only object-layer difference was the expected far call to
  `sparks_add_random`, and `#pragma samecodeseg` plus normal TLINK optimization
  produces the target five-byte `NOP; PUSH CS; CALL near` bridge. The last 16
  linked byte differences came solely from BP-relative local-slot offsets and
  disappeared by reordering four C++ local declarations. Ghidra starts the
  function but reports only 372 body addresses and stops at `0x2A3C0`; it also
  misses the next true TASM function at `0x2A3C3`. The extended
  `reviewed_exact_internal_call` gate therefore attests that next target entry
  by an 8-byte target prefix SHA, while still requiring the current Ghidra
  entry, full raw `RET`, exact owner, and target near-call `0x2B8F9 -> 0x2A110`.
  Final-source focused `gptweb-yuuka6-update-v24-002` and 66-unit aggregate
  `gptweb-yuuka6-v24-precommit-001` pass all exactness gates.
- v25 extends the same `MAIN_034_TEXT` prefix by another **0x76 = 118 bytes**
  through `yuuka6_phase2_fly()` at target `0x2A3C3..0x2A438`. ReC98 has no
  decompiled implementation and target Ghidra has no function entry there.
  Pinned TASM local `PROC` boundaries, raw `RET`, target call `0x2B563 ->
  0x2A3C3`, and the complete next Ghidra entry at `0x2A439` establish the
  function independently. Natural C++ compiled four bytes too short when the
  two frame cases were written as `if/else if`; expressing them as
  `switch(boss.phase_frame)` produces the exact TC86 AX-load/two-compare/default
  lowering and exact 0x76 function size. Private and formal full-link replay
  reproduce the complete 0x3B2 prefix and all seven ordered relocations.
- v26 extends the same `MAIN_034_TEXT` natural-C++ prefix by another **0x6F =
  111 bytes** through `yuuka6_move_towards()` at target
  `0x2A439..0x2A4A7`. ReC98 still had this function only as ASM. Fresh Ghidra
  reports the complete 111-byte body, pinned TASM fixes the next true entry at
  `0x2A4A8`, and raw target near call `0x2B5B0 -> 0x2A439` independently anchors
  the entry. Natural C++ reproduces the exact SI/DI parameter loads, sparse
  `boss.phase_frame` switch, animation calls, and callee-cleanup `RET 4`. Two
  private ASM data labels are exposed to the C++ TU only through zero-byte public
  aliases at their original storage; no data bytes are copied or emitted. Focused
  `gptweb-yuuka6-move-v26-001` and 66-unit aggregate
  `gptweb-yuuka6-move-v26-default-001` reproduce the full **0x421-byte** prefix,
  exact map placement, all seven ordered relocations, deterministic TC86 OMF, and
  the zero-LEDATA order anchor. The internal-call reviewer now also accepts
  `RET/RETF imm16` through the same fail-closed terminal predicate used by raw
  decoding, with a negative non-return regression.
- v27 extends `MAIN_034_TEXT` by another **0x5B = 91 bytes** through
  `yuuka6_horizontal_wave()` at `0x2A4A8..0x2A502`. Fresh Ghidra gives a
  complete body, pinned TASM fixes the next entry at `0x2A503`, and target near
  call `0x2B659 -> 0x2A4A8` anchors the entry. Natural C++ immediately produced
  the exact function size and relocation topology; the only private full-link
  mismatch was two immediate bytes because the first draft reversed the natural
  `polar()` center/radius arguments. Target Pascal argument packing proves the
  intended call is `polar(80px, 48px, SinTable8[boss.angle])`; correcting that
  source semantics makes the full **0x47C-byte** prefix raw exact with all eight
  ordered relocations unchanged.
- v28 extends the same `MAIN_034_TEXT` natural-C++ prefix by **0x3A = 58 bytes**
  through `yuuka6_move_to_center()` at `0x2A503..0x2A53C`. ReC98 has no
  high-level implementation for this helper. Fresh Ghidra reports the complete
  58-byte body and begins the next target function exactly at `0x2A53D`; raw MZ
  scanning independently finds two `E8 rel16` calls (`0x2B697` and `0x2B791`)
  resolving to the helper. Target code shows a sprite-state animation branch,
  clears the existing private auxiliary flag, then moves boss X by one pixel
  toward the narrow `[192px,193px)` center window. Natural C++ reproduces the
  full 0x3A bytes and extends the linked prefix to **0x4B6 bytes**. Focused
  `gptweb-yuuka6-center-v28-001` and final 66-unit aggregate
  `gptweb-yuuka6-center-v28-precommit-001` pass raw/map/ordered-relocation/OMF/
  determinism in both cold materializations.
- v29 recovers the next **0x3CA = 970 bytes** as eight Yuuka6 sprite-animation
  helpers in a dedicated natural-C++ TU at target `0x2A53D..0x2A906`. Fresh
  Ghidra identifies all eight entries but omits the compiler-owned trailing
  switch tables from its function bodies. Pinned TASM local symbols, raw RET
  boundaries and the next target entry at `0x2A907` tile the complete range.
  `reviewed_exact_extent` now validates `code -> optional alignment byte ->
  optional compare table -> jump table` with every jump target required to be
  a decoded instruction start. Focused `gptweb-yuuka6-anims-v29-004` and
  67-unit aggregate `gptweb-yuuka6-anims-v29-final-web-001` pass both cold
  materializations. The reviewed baseline becomes **17,646 / 17,650 bytes**
  and **155 / 156 functions exact**.
- v30 extends the reviewed `MAIN_034_TEXT` frontier by another **0x256 = 598
  bytes** at target `0x2A907..0x2AB5C` as five natural-C++ Yuuka6 gather
  helpers. This range was not exposed by the old linker-public-only queue:
  pinned TASM contains five local `PROC` starts, Ghidra recognizes only four,
  and it omits all four trailing TC86 switch tables. The fifth helper at
  `0x2A9B5` has no Ghidra entry or TLINK public; target near call `0x2AA14 ->
  0x2A9B5`, raw `RET`, and next Ghidra/TASM entry `0x2A9CA` close it
  independently. Focused `gptweb-yuuka6-gather5-v30-web-001` and 68-unit
  aggregate `gptweb-yuuka6-gather5-v30-precommit-web-001` are raw/map/ordered-
  relocation/OMF/determinism exact twice. The reviewed baseline is now
  **18,244 / 18,248 bytes** and **160 / 161 functions exact**.

- `snd_mmd_resident` is now a full **47-byte exact pure-C function** at
  target `0x233AC..0x233DA` / TLINK `130E:02CC`. Removing `-WX` from the
  maintained TH04 wrapper is the decisive codegen fix: the same natural `__es`
  pointer form keeps the target `LES`/magic checks while TC4J emits the target's
  distinct true/false `RETF` paths. Focused `gptweb-snd-mmd-no-wx-align-002`
  and 67-unit aggregate `gptweb-snd-mmd-no-wx-align-default-001` pass all
  raw/map/ordered-relocation/OMF/determinism gates. A checked-in zero-code C TU
  (`src/main/sound/mmd_align.c`) emits a word-aligned `SHARED` SEGDEF and no
  LEDATA, restoring the following KAJA/MODE/LOAD starts without patching an
  object or emitting a target byte. Target `0x233DB = 0x90` is a separate
  excluded padding owner. This independently falsifies the older candidate
  comment that `-WX` was required for the early `RETF` codegen.
- `snd_se_reset` adds a separately reviewed **11-byte exact pure-C owner** at
  target `0x238A6..0x238B0`. TLINK places `_snd_se_reset` at the first byte and
  raw 16-bit decode reaches `RETF` after exactly 11 bytes; the following
  `0x238B1` NOP is upstream `#pragma codestring` padding and is deliberately
  outside authored C/C++ accounting. The maintained source uses
  `compat/rec98` one-line adapters plus `source_mode=forwarded-fragment`, and
  focused replay plus the 67-unit aggregate are exact. Ghidra has no function
  at `0x238A6`; the checked-in no-Ghidra TLINK/raw boundary gate now promotes
  `_snd_se_reset` as a reviewed exact function without fabricating Ghidra data.
- Re-screening the remaining 0x5A-byte `stages.cpp` prefix shows that it is the
  single `carpet_lighting_put_new()` function and that the candidate relies on
  inline ASM for DS/ES setup, `MUL`, `LODSB`, `SHL`, and `LOOP`. The following
  0x1AA-byte render suffix is already exact. Keep the mixed-ASM prefix outside
  maintained authored-C/C++ ownership unless those operations are naturally
  recovered first.
- A fresh coverage pass retired seven stale generic module umbrellas. Six had
  only a single target-observed padding byte left (`tile`, `initmain`,
  `snd_se_r`, `snd_se`, `scrolly3`, and `grcg_3`), now represented explicitly
  as excluded `origin=padding` owners; pinned ReC98 only corroborates the
  matching codestring values. `bullet_u` is fully covered by two exact authored
  owners. The live candidate-module queue therefore falls from 16 to 9; later no-Ghidra review and `dialog_animate` recovery raise the live metrics without reopening those retired umbrellas.
- `item_splashes_init()` is a real remaining 26-byte mixed-code gap at target
  `0x23F16`: target Ghidra and TLINK agree on the full function, and the current
  candidate matches 25/26 bytes. The only difference is target `31 C0` versus
  TC4J `33 C0`; standard `memset`, Borland `__memset__`, and `_AX ^= _AX`
  natural-source probes do not recover the target layout. Keep it nonexact and
  do not replace the mismatch with inline ASM or byte emission.
- A TLINK-public-versus-ledger audit inside exact authored owners exposed eight
  function-boundary false negatives hidden by Ghidra: `midboss_invalidate_func`,
  `boss_backdrop_render`, `snd_se_reset`, `grcg_setmode_rmw_seg3`, both bullet
  turn functions, `tune_for_easy`, and `BULLET_TEMPLATE_TUNE_EASY`. Seven have
  no target Ghidra entry; `bullet_turn_y` was swallowed into a bogus oversized
  body. The checked-in no-Ghidra gate reconstructs these boundaries from target
  raw decode plus TLINK and exact-owner evidence instead of fabricating Ghidra
  metadata. `tune_for_easy` additionally validates its metadata byte and all 22
  jump-table targets. The exact-owner TLINK-public audit now reports zero
  omissions.
- `dialog_animate` is now a 62-byte exact natural-C++ owner and automatic exact
  function. The maintained source replaces the upstream hand-written
  `NOP; PUSH CS; CALL near` bridge with an ordinary call plus `#pragma
  samecodeseg`. TC86/TLINK reproduce the target bridge and ordered relocation
  sites naturally; focused `gptweb-dialog-animate-001` and the later 66-unit aggregate
  `gptweb-script-params-internal-precommit-002` both pass.
- A full C/C++ linker-public sweep then found two previously unowned pure-C++
  script helpers in shared `th03/formats/script.hpp`: target/TLINK entries
  `0x1D0CA` / `25DA` (201 bytes) and `0x1D193` / `26A3` (41 bytes), with
  `dialog_op` starting immediately at `0x1D1BC`. Maintained
  `src/main/dialog/script_params.inl` contains only natural C++, and focused
  `gptweb-dialog-script-params-002` plus the 66-unit aggregate reproduce all
  242 bytes with exact map/relocation/OMF surfaces. Both helpers are now
  automatic exact functions.
- The same coverage pass did not stop at linker publics. Auditing Ghidra entries
  inside exact authored owners exposed one credible static function,
  `tiles_render_all_timed` at `0x1CB80`, which has no TLINK public. Its 25-byte
  contiguous Ghidra/raw body ends immediately before public `tiles_activate` at
  `0x1CB99`, and `tiles_activate_and_render_all_for_next_N_frames` independently
  stores near-function offset `0x2090`; under `MAIN_01` CS base `0x1AAF0` that
  resolves exactly to `0x1CB80`. The checked-in internal-function gate requires
  all of those surfaces before denominator admission.
- The earlier linker-public-only sweep left 14 routing candidates, but v30 proves
  that list is **not an exhaustive authored-function queue**. Immediately after
  the former exact frontier at `0x2A907`, pinned TASM local `PROC` inventory
  exposes a long Yuuka6/Elly family that is invisible to a public-only sweep;
  Ghidra also misses some entries entirely. Keep the 14 intervals only as a
  public-symbol worklist. Candidate expansion must additionally scan target raw
  control flow and local TASM boundaries beyond every exact frontier.
- `snd_load` now has three additional exact natural-source subspans. Identity
  fragments recover the DOS-open and driver-dispatch/read sequences. The
  parameter reload uses `_AX = *reinterpret_cast<snd_load_func_t near *>(&func);`;
  taking the address prevents TC4J from promoting `func` to DI and naturally
  emits target `8B 46 06`. A fail-closed `source_mode=replace` gate verifies the
  complete pinned scaffold SHA plus source-span offset/size/SHA before applying
  that one maintained replacement, so surrounding upstream low-level source is
  never claimed as maintained exact source.
- The latest aggregate cold replay `gptweb-std-run-v68-final-precommit-web-001`
  passed all 106 current default exact-replay owners in two isolated
  materializations, including the contiguous 0x1CB midboss TU. The replay driver removes the exact checked-in init+exit
  suffix from the pinned scaffold, materializes it as a second current-header
  C++ TU, and inserts that source immediately after `th04/dialog.cpp` in the
  cold `Tupfile.lua`; normal `build.bat`/Tup/TC4J/TLINK then perform the build.
- `config/th04_main_authored_functions.csv` tracks function progress separately
  from byte ownership. The current review accepts 114 strict automatic functions
  plus 96 replayable manual exact reviews. A fresh
  TLINK-public audit found eight real exact-owner functions that the target
  Ghidra inventory had missed or misgrouped. `reviewed_exact_no_ghidra` admits
  them only with exact authored ownership, a matching TLINK public, gap-free raw
  decode through `RET`/`RETF`, and an exact next-public or owner-end boundary;
  `tune_for_easy` additionally requires its metadata byte and complete 22-entry
  jump table to fill the trailing extent and target decoded instruction starts.
  A separate `reviewed_exact_internal` path covers static functions with no
  linker public only when a contiguous Ghidra body, raw terminal decode, exact
  next-public boundary, and an independent target function-pointer word all
  agree. This admits `tiles_render_all_timed` at `0x1CB80`; a regression test
  mutates the pointer word and requires rejection. `bullets_update` remains the
  separate exact-extent/table case, and the two `MB_DFT_TEXT` score-bonus
  functions remain Ghidra-min/max manual cases. The v21 stage3/stage4/stagex and
  `boss_defeat_update` extents additionally demonstrate that a configured manual
  reviewed extent must shadow any shorter same-address Ghidra automatic claim;
  the writer rejects residual automatic/manual overlap. `snd_load` is the sole
  reviewed nonexact function, giving 190/191 exact.
- `dialog_init` is no longer a relocation-order blocker. Restoring its original
  second C++ translation unit keeps all linked code bytes unchanged and restores
  the exact six-entry MZ relocation order. `dialog_op` and `dialog_run` remain
  blocked: their historical pre-merge object already has the same non-target
  fixup order as the current candidate, so the lower-TU split does not solve
  them.
- Maintained C/C++ exact source intentionally excludes `_asm`, `asm {}`,
  `#pragma codestring`, and `__emit__`. Genuine standalone TASM translation
  units are classified `original-asm` rather than `authored` and contribute no
  bytes to the authored C/C++ percentage.
- The source tree now follows the TH08 product rule: reconstructed MAIN code is
  under `src/main/<subsystem>/`, with no `exact/`, `partials/`, or `modules/`
  directories. Complete translation units keep `.cpp`/`.c`/`.asm`; bounded
  included bodies use `.inl`. Acceptance state remains exclusively in the
  ledgers. Historical evidence and stable unit IDs may retain old `module` or
  `partial` wording only to keep receipts addressable; they are not a current
  work queue or source-layout model. Replay manifests and historical map
  evidence may still name ReC98 `th01`/`th02`/`th03` paths because they
  describe the pinned scaffold, not the product source layout.
- All 71 direct ReC98 include sites (31 unique headers, including the 47
  cross-game sites) now route through `compat/rec98/<upstream-path>`. That
  reusable directory contains one-line forwarders only; exact replay copies and
  hashes it as a declared build input. Direct ReC98 paths are rejected in
  `src/`. No recursive ReC98 header closure was copied into the repository.

## Open provenance issue

The local hashes identify this exact legal disk image, but have not yet been
confirmed against an independently sourced pristine dump.  Keep
`canonicality = "candidate-local-attested"` until that independent check
passes.  A ReC98 rebuild is useful toolchain/output calibration, but upstream
status alone is not independent provenance or acceptance evidence.

## Remaining tool gaps

- A Neko Project II debug build is not installed. Add and attest it when the
  first bounded runtime claim needs independent cross-emulator replay; it is
  not required for static exact reconstruction.
- No deterministic TH04 input/checkpoint/state-capture runtime scenario exists
  yet. `scripts/smoke_runtime.py` deliberately does not claim that role.
- No IDA backend is installed. Pinned Ghidra is operational through
  `.tools/ghidra` and `scripts/ghidra.py`; it intentionally need not be on the
  host `PATH`.
- `ndisasm`, GNU `objdump`, Wine, `unar`, and mtools are available.

## Remaining source/build gap

- The repository does not yet contain every TH04 translation unit or the local
  ABI/header surface needed for an independent full build. The remaining
  upstream declaration dependency is explicit under `compat/rec98/`; do not
  vendor TH01/TH02/TH03/TH05 trees to hide it. The next source-architecture work
  is bounded declaration/header recovery into the owning TH04 subsystem (or
  proved `src/shared/`) followed by a clean local compile. Exact replay through
  pinned ReC98 remains a separate Oracle during that migration.

## Next bounded work

Before repeating compiler/TU experiments, read
`docs/reconstruction/TH04_MAIN_FIXUP_CODEGEN_PROBES.md`. It records the tested
`dialog_op` TU rotation matrix (including every current natural shared-function
boundary), the negative `dialog_run` RET split and source shapes, the TC86
option matrix, and the pinned-media TASM 4.1 `-B` behavior. The remaining work
should target genuinely new source/IR or producer evidence, not previously
falsified boundary/assembler modes.

Preserve the >99% reviewed authored function/byte baseline with the default
two-cold replay before changing shared source or toolchain surfaces. `snd_load`
is now narrowed to four blocked bytes after 37 middle bytes were recovered from
maintained natural C++ and two-cold replay. Do not solve the remaining `PUSH DS`,
`89 C3`, or `POP DS` with inline assembly or byte injection. C++
reference/template/comma/conditional aliasing of `_BX` is now also falsified:
the pseudo-register is not addressable and direct assignment remains `8B D8`.
The same-media PC-98 `TC.EXE` Integrated Compiler 4.0 was also batch-replayed
under the pinned DOSBox-X PC-98 profile; generated OMF still reports
`TC86 Borland C++ 4.02`, and natural `_BX = _AX` still emits `8B D8`. Do not
repeat IDE-versus-TCC producer switching as an explanation for target `89 C3`.
The `snd_pmd_resident` `LES` blocker is solved by the reusable Borland `__es`
segment-pointer source shape. `snd_mmd_resident` confirms the same `__es` LES
shape but remains source-present because C-mode return tail merging does not yet
reproduce the target's early `RETF`; do not repeat the tested ordinary-return,
explicit-goto, `_AX` self-assignment, or whole-function `-O-` variants. `bullets_update` is now fully exact from maintained
natural C++: `#pragma samecodeseg sparks_add_random` changes the TC86 Pointer16
frame, then default TLINK 6.10 far-call optimization (enabled because `/f` is not
specified) turns the five-byte `CALL FAR` into target `NOP; PUSH CS; CALL near`
in the final MZ. Do not regress to judging this mechanism at object LEDATA alone.
In parallel, investigate the two remaining `dialog_op`/`dialog_run`
relocation-order blockers at the OMF FIXUPP/source-emission level;
the original lower-TU split and historical pre-decomp ASM producer are already
falsified for target ordering. Runtime work can stay deferred until a
reconstruction claim actually needs behavioral evidence.


### Contiguous `MAIN_035` / `BOSS_TEXT` recovery (v21)

A target-first audit found a previously unowned 0x677-byte suffix of
`MAIN_035_TEXT` immediately before the reconstructed `BOSS_TEXT`. Pinned TASM
local labels, target raw RET/RETF boundaries, and final natural-C++ PUBDEF
offsets identify ten true functions there: `boss_reset`, `bb_boss_load`,
`bb_boss_free`, and `stage1_setup` through `stagex_setup`. Ghidra truncates
`stage3_setup` and `stagex_setup` and false-splits `stage4_setup`, so those
entries use the exact-extent manual gate rather than weakening automatic body
review.

The apparent segment boundary was false. `src/main/boss/boss.cpp` emits one
0x9B6-byte natural TC4J C++ contribution beginning at target `0x2DF61`,
containing the recovered 0x677 suffix plus the former 0x33F `BOSS_TEXT`. The
old `BOSS_TEXT` becomes zero-length and `MAIN_036_TEXT` starts at the unchanged
address. Focused `gptweb-boss-tu-v21-003` and 65-unit aggregate
`gptweb-boss-tu-v21-default-001` reproduce all 2,486 bytes and all 60 ordered
overlapping relocations. `boss_defeat_update` is 468/468 exact with an ordinary
`bb_boss_free()` call; no inline ASM, codestring, emit, or object patch is used.

This expands the confirmed authored denominator by 2,123 bytes and eleven true
functions over v20. The historical v21 baseline was 15,470/15,474 bytes and 140/141
functions exact; v22 superseded it at 15,544/15,548 bytes and 141/142 functions exact; v23 reached 15,607/15,611 bytes and 142/143 functions exact; v24 reached 16,298/16,302 bytes and 143/144 functions exact; v25 reached 16,416/16,420 bytes and 144/145 functions exact; v26 reached 16,527/16,531 bytes and 145/146 functions exact; v27 reached 16,618/16,622 bytes and 146/147 functions exact; v28 reached 16,676/16,680 bytes and 147/148 functions exact; v29 reached 17,646/17,650 bytes and 155/156 functions exact; v30 reaches 18,244/18,248 bytes and 160/161 functions exact; the only reviewed nonexact authored function remains
`snd_load`, with four blocked bytes.


### Yuuka6 animation switch extent recovery (v29)

The next eight `MAIN_034_TEXT` target helpers span `0x2A53D..0x2A906` /
`13A9:6AAD..6E76`, for a total **0x3CA = 970 bytes**. Fresh Ghidra recognizes
all eight entry addresses but truncates several bodies and never owns the
compiler compare/jump tables following each `RET`. Target TLINK publics, pinned
TASM local boundaries, raw terminal decoding, and exact switch-table contents
therefore define the reviewed function extents. `reviewed_exact_extent` now
requires any metadata byte plus compare/jump tables to be contiguous and to fill
the complete public extent; every jump target must decode at an instruction
start.

The decisive compiler result is alignment, not handwritten padding. Default
TC86 / `-a1` emits an animation block four bytes short. `-a` / `-a2` naturally
emits exactly four `00` alignment bytes before the open, spin-back, appear, and
shield switch tables, matching the target's only four `db 0` sites. Maintained
`src/main/boss/yuuka6_animations.cpp` uses file-start `#pragma option -a`; it
contains no inline ASM, codestring, `__emit__`, object patch, or target-byte
injection. Focused `gptweb-yuuka6-anims-v29-004` and 67-unit aggregate
`gptweb-yuuka6-anims-v29-final-web-001` reproduce all 970 bytes, exact map
placement, relocation overlap, and deterministic valid OMF. Eight functions are
newly reviewed exact; `snd_load` remains the sole reviewed nonexact function.


### Yuuka6 gather-pattern/local-PROC recovery (v30)

The first post-v29 target-first rescreen invalidated the assumption that linker
publics or Ghidra entries enumerate authored functions. Pinned `MAIN_034_TEXT`
TASM starts five consecutive local procedures at `0x2A907`, `0x2A9B5`,
`0x2A9CA`, `0x2AA45`, and `0x2AAE5`. Their target extents are respectively
`0xAE`, `0x15`, `0x7B`, `0xA0`, and `0x78`, tiling `0x2A907..0x2AB5C` with no
gap. Four are sparse TC86 switches whose compare/jump tables live after the
final `RET`; Ghidra owns only the CFG code. The `0x15` shared gather helper is
missed by Ghidra entirely and has no TLINK public, but raw call `0x2AA14` resolves
to it and the next complete Ghidra/TASM entry is exactly `0x2A9CA`.

`src/main/boss/yuuka6_gather_patterns.cpp` is ordinary C++ with file-start
`#pragma option -a`; it uses the typed gather/circle APIs and source-level shared
control-flow labels only. No inline ASM, codestring, `__emit__`, object patch or
target-byte array is present. TC86 contributes exactly `0x256` bytes at
`13A9:6E77`, followed by residual ASM at `13A9:70CD`. Two independent focused
cold builds and the 68-unit aggregate reproduce the target slice SHA
`0735b992...f82ac`, all ten ordered overlapping MZ relocations, and normalized
OMF SHA `dde9097f...39c88`. Function review admits all five, raising the reviewed
baseline to **18,244 / 18,248 authored bytes exact (99.978080%)** and **160 /
161 functions exact (99.378882%)**.

Candidate expansion must continue from target `0x2AB5D`, not from the stale
14-public list. The same pinned TASM residual already exposes further local
Yuuka6 procedure starts at `0x2AB5D`, `0x2ABE5`, `0x2ACCC`, `0x2AD6F`,
`0x2ADDB`, `0x2AE8F`, `0x2AFA8`, `0x2B099`, `0x2B1B1`, `0x2B22B`, `0x2B282`,
`0x2B313`, and `0x2B3E2` before `yuuka6_update()`, followed by a similar Elly
local-procedure family. Treat these as target-first candidates and re-establish
each boundary from raw/TASM/Ghidra evidence before source reconstruction.


### v31-v36 target-first expansion beyond the Yuuka6 gather frontier

- v31 recovers five Yuuka6 attack helpers at `0x2AB5D..0x2AE8E` (0x332 bytes). A standalone natural TU matched every byte but not ordered MZ relocations; fusing chase + animations + gather + attack into the target physical TC86 producer restores the exact relocation order without low-level code.
- v32 continues through eight target-only Yuuka6 local helpers at `0x2AE8F..0x2B42E` (0x5A0 bytes). The last mismatch exposed a stale ReC98 `thicklaser_t` layout; target TASM proves four unknown bytes after `origin`, and a SHA-locked ABI transform removes the mismatch.
- v33 corrects a false boundary at `0x2B42F`: `YUUKA6_PHASE_NEXT` is a separate 0x4F function, followed by `yuuka6_update()` at `0x2B47E` with 0x48A code bytes and 0x54 bytes of compiler switch tables. The complete 0x52D owner is natural-C++ exact.
- v34 resumes local-PROC screening at `0x2B95C` and recovers the 0x2E0 Elly scythe state machine. Ghidra truncates the true entry to 38 bytes and invents four internal functions, while target raw/TASM show 0x2D0 code bytes plus an eight-entry compiler jump table through `0x2BC3B`. Natural source exactness depends on target-driven block placement, a read/modify/write speed expression, a volatile signed turn byte, and `<= 4` branch direction; no padding or inline ASM is used.
- v35 recovers the adjacent 55-byte `elly_scythe_init()` at `0x2BC3C`; here Ghidra happens to agree with raw/TASM completely.
- v36 recovers the 176-byte `elly_orbit_update()` at `0x2BC73`; Ghidra constructs only 19/176 bytes. Target `JL/JGE` opcodes prove the private frame word is signed `int`, and an otherwise redundant `if(frame >= 768)` is required for the exact eight-byte CMP/JL sequence.
- Focused v34/v35/v36 replays and final aggregate `gptweb-elly-v36-precommit-web-002` pass raw bytes, map placement, ordered relocations, OMF validity, and A/B determinism for all 74 default owners. The reviewed baseline is now **22,794 / 22,798 authored bytes exact (99.982455%)** and **178 / 179 functions exact (99.441341%)**. `snd_load` remains the sole reviewed nonexact function with four blocked bytes.
- The target-first candidate universe is still not exhausted. Pinned local TASM continues at `0x2BD23`, `0x2BD4B`, `0x2BDB4`, `0x2BE43`, `0x2BE78`, `0x2BF52`, `0x2BFAB`, `0x2C044`, `0x2C0BF`, `0x2C164`, `0x2C1CF`, and `0x2C251` before public `elly_update()`. Resume at `0x2BD23`; do not fall back to the obsolete public-only queue.


### Elly local-PROC family completion (v37-v48)

The target-first scan after v36 was continued through every remaining local Elly
procedure before the public update routine. Twelve consecutive maintained C++
owners now cover runtime `0x2BD23..0x2C2E4`, adding **0x5C2 = 1,474 bytes** and
12 exact reviewed functions. Focused two-cold replays for v37 through v48 and
final aggregate `gptweb-elly-local-family-v48-precommit-web-002` reproduce all
86 default owners twice with exact raw bytes, TLINK placement, ordered MZ
relocations, valid deterministic OMF, and no regression of earlier Yuuka6/Elly
owners.

The boundary audit deliberately does not treat Ghidra entries as authoritative.
`0x2BD23`, `0x2BD4B`, `0x2BE43`, `0x2C1CF`, and `0x2C251` are complete Ghidra
bodies; `0x2BDB4` owns compiler switch data after its raw `RET`; and the other
helpers range from sparse bodies to internal false splits. In particular,
`0x2C044` has only 13 Ghidra body bytes despite a true 0x7B-byte PROC, while
`0x2BE78`, `0x2BF52`, `0x2BFAB`, `0x2C0BF`, and `0x2C164` require TASM/raw
next-PROC closure. The v39 `elly_gather_update()` extent additionally includes
one zero alignment byte, four compare words `[1,8,16,32]`, and four near jump
words before the next local entry.

Three compiler rules from this sequence are reusable. First, ABI-bearing headers
such as `bullet.hpp` must be parsed before enabling `#pragma option -a`; enabling
alignment before the header changes `BulletTemplate` member offsets even when
code size and relocations otherwise match. Second, DOS-facing overlay basenames
must remain 8.3-safe (`ellybrst.cpp` rather than `ellyburst.cpp`) or TC86 emits a
tilde-shortened object name that Tup cannot match. Third, when the target tests a
callee return value directly in AX, introducing a source local can make TC86
allocate SI and change the prologue; `switch(elly_gather_update())` preserves the
target AX lowering.

The reviewed baseline is now **24,268 / 24,272 authored C/C++ bytes exact
(99.983520%)** and **190 / 191 reviewed functions exact (99.476440%)**. The only
reviewed nonexact function remains `snd_load`, with four blocked bytes. The next
live target-first frontier is the public **`elly_update()` at runtime `0x2C2E5`**;
its Ghidra body is cross-linked far beyond the local Elly region, so re-establish
its complete target boundary from raw/TASM/public/switch data before attempting
source reconstruction.


### Elly public dispatcher and MAIN_034 completion (v49)

The target-first frontier continued through public `elly_update()` at runtime
`0x2C2E5`. Raw 16-bit decoding reaches the common-tail `RETF` at `0x2C691`;
compiler-owned data then occupies every remaining byte through `0x2C6CD`: a
5-entry jump table at `0x2C692`, a 10-value/10-jump sparse switch at
`0x2C69C/0x2C6B0`, and a final 5-entry phase table at `0x2C6C4`. Ghidra
cross-links the entry far outside this region, so it is retained only as
provisional entry evidence. The next byte, runtime `0x2C6CE`, is the already
reviewed exact `bullet_turn_x` public in `BULLET_U_TEXT`.

Maintained natural C++ in `src/main/boss/elly_update.cpp` reproduces all
**0x3E9 = 1,001 bytes** plus both ordered relocation sites. The complete Elly
physical TC86 producer is `13A9:7ECC 0D72`. Aggregate integration exposed one
ABI detail that focused byte matching alone could not: the separately exact
`boss.cpp` declares the callback `pascal far`, so the definition must use that
ABI and the residual TASM must bind the OMF external as `@ELLY_UPDATE$QV`.
With that correction, focused `gptweb-elly-update-v49-focused-final-web-004`
and 87-owner aggregate `gptweb-elly-update-v49-precommit-web-003` both pass two
independent cold materializations across raw bytes, map placement, ordered
relocations, OMF validity, and determinism.

Two independent rescreens close this particular candidate frontier. The target
map says `MAIN_034_TEXT` is exactly `0x2647` bytes from `13A9:65F7` through
`13A9:8C3D`; the 22 reviewed exact authored owners in that segment sum to the
same `0x2647` and tile it with no gap or overlap, while residual `th04_main.asm`
contributes zero bytes at `8C3E`. Separately, pinned TASM contains 38 numeric
local `PROC` starts in `MAIN_034_TEXT`, and all 38 addresses are already exact
function-ledger entries. Thus the former Yuuka6/Elly local-PROC frontier is
exhausted rather than merely hidden by the >99% ratio.

The reviewed baseline is now **25,269 / 25,273 authored C/C++ bytes exact
(99.984173%)** and **191 / 192 reviewed functions exact (99.479167%)**. The
sole reviewed nonexact function remains `snd_load`, with the same four blocked
bytes.

### MAIN_033 Stage 4 Marisa target-first recovery (v50-v66)

Whole-artifact rescreening after MAIN_034 completion proved that the authored
candidate universe was still large: target `MAIN_033_TEXT` is a 0x32B7-byte
compiler-like segment that had no authored owner at the v49 baseline. Target
TASM begins that region with the Stage 4 Marisa local family at runtime
`0x26C05`. ReC98 only contains a high-level reconstruction of the earlier
`marisa_flystep_pointreflected()` helper; the v50-v66 functions were therefore
recovered target-first from raw code, TASM control flow, exact data layout, and
TC4.02 code-generation probes rather than copied from an upstream solution.

Seventeen maintained natural-C++ logical owners now cover Marisa from
`0x26C05..0x27CF2`, adding **4,334 reviewed authored bytes and 17 exact
functions**. v66 `marisa_update()` has 0x2CB bytes of code through RETF at
`0x27CBE`, followed by an 11-value / 11-jump mode switch and a four-entry
phase jump table through `0x27CF2`; public `enemies_add` starts at `0x27CF3`.

Ordered MZ relocations exposed two physical TC86 producer boundaries invisible
in raw code. Borland TDUMP showed that FIXUPP entries are listed high-to-low
inside one LEDATA/FIXUPP record, while successive records retain record order.
The accepted physical layout is:

- v50-v58: `0x26C05..0x2717C`, `th04/m4bits.cpp`, 0x578 bytes;
- v59-v63: `0x2717D..0x2788D`, `th04/m4late.cpp`, 0x711 bytes;
- v64-v66: `0x2788E..0x27CF2`, `th04/m4tail.cpp`, 0x465 bytes.

A competing B4M+MAIN_033 fused-object hypothesis was rejected. Putting one
fused object in the `boss_4m.cpp` slot preserved B4M placement but moved
MAIN_033 from target `13A9:3175` to `13A9:563D`; TDUMP also showed that this
fusion did not change MAIN_033 LEDATA chunking. The already exact B4M producer
therefore remains independent.

Focused replay `gptweb-marisa-main033-v66-focused-final-web-001` and 104-owner
aggregate `gptweb-marisa-main033-v66-precommit-web-009` pass two independent
cold materializations across raw bytes, map ownership, ordered MZ relocations,
OMF validity, and deterministic normalized objects. Function review reports
**208 / 209 exact (99.521531%)** with zero strict rejections. The reviewed byte
baseline is **29,603 / 29,607 = 99.986490% exact**; `snd_load` accounts for the
only four nonexact authored bytes.

MAIN_033 is not exhausted. After the public enemy helpers, pinned TASM exposes
Mugetsu local procedures beginning at **`0x2802F`** (0x15 bytes), followed by
`0x28044`, `0x280BB`, `0x2812A`, `0x2821E`, `0x28314`, `0x2838A`, `0x2845E`,
`0x284AC`, `0x28556`, `0x285E4`, and `0x28655` before `mugetsu_update()`.
Resume target-first there.


### MAIN_033 post-Marisa frontier: `ENEMIES_ADD` (v67)

Target-first screening continues past the completed Marisa family instead of
treating `marisa_update()` as the end of `MAIN_033_TEXT`. The next TLINK public
is `ENEMIES_ADD` at `13A9:4263` / runtime `0x27CF3`. TLINK places `std_run()`
at `13A9:4341` / `0x27DD1`, closing a **0xDE = 222-byte** function. Target
Ghidra has the correct `0x27CF3` entry but constructs only 12 body bytes, so
the accepted boundary comes from pinned TASM, gap-free raw decoding through
`RET 8` at `0x27DD0`, and the next TLINK public.

`src/main/enemy/enemies_add.cpp` is maintained natural C++. Its only non-obvious
TC4 source-shape constraint is the left/right-half flag: leaving the comparison
as a generic boolean makes TC4 materialize `1/0` in AX and adds one byte, while
an explicitly byte-valued ternary naturally emits the target AL-valued branch.
No inline ASM, codestring, `__emit__`, object patch, padding, or target-byte
injection is used. Focused `gptweb-enemies-add-v67-focused-web-006` and
105-owner aggregate `gptweb-enemies-add-v67-precommit-web-001` pass raw bytes,
exact map placement, ordered relocations, OMF validity, and A/B determinism.

The reviewed baseline is now **29,825 / 29,829 authored C/C++ bytes exact
(99.986590%)** and **209 / 210 reviewed functions exact (99.523810%)**.
`snd_load` still accounts for all four reviewed nonexact bytes. `MAIN_033_TEXT`
is not exhausted: resume at **`std_run()` `0x27DD1`**, a 0x6D-byte function
ending immediately before `ENEMY_BULLET_TEMPLATE_PUSH` at `0x27E3E`;
`ENEMIES_UPDATE` follows at `0x27E59`.


### MAIN_033 stage VM and copy boundary: `std_run` exact, template push blocked (v68-v69)

Target-first screening continues immediately after `ENEMIES_ADD`. `std_run()`
occupies runtime `0x27DD1..0x27E3D` (0x6D = 109 bytes); TLINK, pinned TASM,
raw decode, and fresh Ghidra all agree that `ENEMY_BULLET_TEMPLATE_PUSH` starts
at the next byte `0x27E3E`. Maintained `src/main/stage/std_run.cpp` is exact.
The key TC4 source-shape detail is a tiny inline byte-to-word helper around the
item field: direct source lets TC4 reuse AH=0 and drops a target-redundant
`MOV AH,0`, while the inline semantic boundary emits no call and naturally
restores exactly that instruction. Focused
`gptweb-std-run-v68-focused-final-web-001` and 106-owner aggregate
`gptweb-std-run-v68-final-precommit-web-001` pass raw/map/ordered-relocation/
OMF/determinism in two cold materializations.

The next public `ENEMY_BULLET_TEMPLATE_PUSH` is a separately reviewed 27-byte
authored function at `0x27E3E..0x27E58`. Its target boundary is unambiguous,
but exact source is intentionally **blocked** rather than forged. A plain
assignment emits `SCOPY@`; `#pragma option -G` gives an inline 27-byte
`REP MOVSW` with exact relocations but setup order SI/DI/ES/CX instead of the
target CX/SI/DI/ES; `__memcpy__` gives SI/ES/DI/CX; and an inline assignment
helper grows to 36 bytes. ReC98 uses an inline-ASM decomp macro for analogous
reordered copies, but that shortcut is prohibited here. The best natural
negative receipt is `gptweb-enemy-btpush-v69-negative-final-web-001`.

The current reviewed baseline is **29,934 / 29,965 authored bytes exact
(99.896546%)** and **210 / 212 reviewed functions exact (99.056604%)**. The two
reviewed nonexact functions are `snd_load` and `ENEMY_BULLET_TEMPLATE_PUSH`.
MAIN_033 is still not exhausted: `ENEMIES_UPDATE` begins at **`0x27E59`** and
fresh Ghidra/raw extend it 470 bytes through `0x2802E`, immediately before the
Mugetsu local frontier at `0x2802F`. Preserve the 27-byte physical ordering
blocker when recovering later code; do not silently move a later C++ producer
ahead of it.
