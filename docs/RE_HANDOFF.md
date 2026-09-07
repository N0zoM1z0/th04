# Current handoff

## Phase

Control-plane, target-ingestion, build-chain calibration, headless Ghidra, and
the optional DOSBox-X headless host smoke are ready for handoff. The first
large `MAIN.EXE` authored reconstruction batch is also cold-replayed and
accepted. After expanding the reviewed authored boundary into `MB_DFT_TEXT`,
`snd_mmd_resident`, and the pure-C body of `snd_se_reset`, reviewed authored
C/C++ bytes are 12,932 / 12,983 (99.607179%) exact, and reviewed authored
functions are 115 / 116 (99.137931%) exact. Nine standalone original-style ASM units totaling 1,489 bytes are
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
  `gptweb-authored-expand-default-004` passes all 64 current default-selected
  exact-replay units across raw bytes, containing/exact TLINK placement,
  ordered overlapping MZ relocations, OMF validity, and deterministic output.
- The current reviewed authored byte denominator is 12,983 bytes across 59
  authored units/regions; 12,932 bytes across 55 units/regions are exact. The
  reviewed nonexact byte remainder is deliberately visible: 47 bytes belong to
  the source-present `snd_mmd_resident` candidate, and four blocked bytes remain
  in `snd_load` (`PUSH DS`, target `89 C3` `MOV BX,AX`, and `POP DS`).
- `snd_pmd_resident` is fully exact from maintained pure C. After `_ES = 0`,
  `*(void far * __es *)(PMD * 4)` makes TC4J naturally generate the target
  `LES BX, ES:[0180h]`; no inline assembly, `__emit__`, codestring, or raw-byte
  directive is involved.
- The raw-identical 0x119-byte `th04/mb_dft.cpp` contribution is **not**
  blanket-classified as authored C/C++. Fresh target Ghidra + TLINK review
  admits only its 0xD9-byte pure-C/C++ prefix: 106-byte `midboss_score_bonus`
  plus 111-byte `boss_score_bonus`. The next public, `midboss_defeat_update`,
  starts at `0x2A047` and its upstream candidate contains inline assembly, so it
  remains outside this authored owner. The 217-byte prefix is exact in focused
  two-cold replay and the 64-unit aggregate.
- `snd_mmd_resident` is now a reviewed 47-byte authored source-present candidate
  rather than an unclassified whole-module candidate. The TH04-wrapper natural
  C source recovers the target `LES`, all three magic checks, and both global
  stores. Ordinary C returns still make TC4J tail-merge the true path into a
  `JMP` plus shared `RETF`, leaving seven raw-byte differences. Explicit `goto`,
  `_AX` self-assignment, and `-O-` probes did not fix it. A first replay attempt
  also proved that overlaying the shared `th02/snd/mmd_res.c` is wrong ownership:
  it changes the GAME=2 build and causes five header/type errors. Keep the
  maintained candidate on the TH04 wrapper `th04/snd_mmdr.c` and do not restore
  the upstream inline `RETF` assembly.
- `snd_se_reset` adds a separately reviewed **11-byte exact pure-C owner** at
  target `0x238A6..0x238B0`. TLINK places `_snd_se_reset` at the first byte and
  raw 16-bit decode reaches `RETF` after exactly 11 bytes; the following
  `0x238B1` NOP is upstream `#pragma codestring` padding and is deliberately
  outside authored C/C++ accounting. The maintained source uses
  `compat/rec98` one-line adapters plus `source_mode=forwarded-fragment`, and
  focused replay plus the 64-unit aggregate are exact. Ghidra has no function
  at `0x238A6`, so this expands byte ownership only; no function-ledger row is
  fabricated.
- Re-screening the remaining 0x5A-byte `stages.cpp` prefix shows that it is the
  single `carpet_lighting_put_new()` function and that the candidate relies on
  inline ASM for DS/ES setup, `MUL`, `LODSB`, `SHL`, and `LOOP`. The following
  0x1AA-byte render suffix is already exact. Keep the mixed-ASM prefix outside
  maintained authored-C/C++ ownership unless those operations are naturally
  recovered first.
- `snd_load` now has three additional exact natural-source subspans. Identity
  fragments recover the DOS-open and driver-dispatch/read sequences. The
  parameter reload uses `_AX = *reinterpret_cast<snd_load_func_t near *>(&func);`;
  taking the address prevents TC4J from promoting `func` to DI and naturally
  emits target `8B 46 06`. A fail-closed `source_mode=replace` gate verifies the
  complete pinned scaffold SHA plus source-span offset/size/SHA before applying
  that one maintained replacement, so surrounding upstream low-level source is
  never claimed as maintained exact source.
- The latest aggregate cold replay `gptweb-authored-expand-default-004`
  passed all 64 current default exact-replay units in two isolated
  materializations. The replay driver removes the exact checked-in init+exit
  suffix from the pinned scaffold, materializes it as a second current-header
  C++ TU, and inserts that source immediately after `th04/dialog.cpp` in the
  cold `Tupfile.lua`; normal `build.bat`/Tup/TC4J/TLINK then perform the build.
- `config/th04_main_authored_functions.csv` tracks function progress separately
  from byte ownership. The current review accepts 101 contiguous functions
  automatically plus 14 replayable manual exact reviews. `bullets_update` is
  the exact-extent case: one 0x36B exact owner is bound to its TLINK public,
  0x360-byte raw code decode through `RETF`, trailing switch metadata/table, and
  next-public boundary despite unusable Ghidra body ranges. The two new
  `MB_DFT_TEXT` score-bonus functions also use the manual gate because Ghidra's
  min/max spans are correct but its body sets are noncontiguous; TLINK + exact
  owner + gap-free raw decode validate their complete 0x6A and 0x6F extents.
  `snd_load` remains the sole reviewed nonexact function, giving 115/116 exact.
  No current function candidate is provisional.
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
