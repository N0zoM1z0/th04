# Current handoff

## Phase

Control-plane, target-ingestion, build-chain calibration, headless Ghidra, and
the optional DOSBox-X headless host smoke are ready for handoff.
The first reconstruction screen covers 58 `MAIN.EXE` source-module
contributions and 151 Ghidra function entries. Sixteen small authored units
have reviewed boundaries; 42 larger or ambiguous module candidates remain
provisional. No unit is promoted to exact and no deterministic TH04 runtime
scenario has been authored.

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
- `slowdown_frame_delay` is reviewed at target file `0xC2F2`, load-module
  `0xAAF2`, link/Ghidra `1AAF:0002`, with a complete 26-byte function extent
  and no overlapping MZ relocation. The pinned TC4J candidate output is 26/26
  bytes identical to the target and its OMF/map checks pass. Maintained source
  now exists at `src/th04/main/slowdown.cpp`, but the ledger remains
  `source-present` until a complete checked-in unit replay satisfies every
  exact Oracle.
- The initial `MAIN.EXE` authored screen accounts for 58 nonzero source-module
  contributions totaling 17,412 bytes in the pinned cold-build map. Fifty-four
  contributions totaling 14,123 bytes are raw-identical at the same target
  load offsets; the remaining four contain 25 byte differences in total.
  Read-only Ghidra finds 151 function entries in these spans.
- Fifteen additional one-function module contributions have target boundaries
  that agree with both Ghidra bodies and linker-map extents. Together with
  `slowdown_frame_delay`, the current reviewed authored denominator is 16
  units and 1,446 bytes. The other 42 module candidates retain provisional
  ownership and do not enter progress totals.

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

## Next bounded work

Continue with the 15 reviewed units in
`docs/reconstruction/TH04_MAIN_AUTHORED_SCREEN.md`; `tile_ring_set_vo`,
`frame_delay`, `mpn_free`, and the short sound-mode helpers are the smallest
source-recovery targets. Then split the raw-aligned multi-function candidates
using target control flow. Keep the four mismatch modules (`dialog`, `stages`,
`snd_load`, and `it_spl_u`) as focused compiler/source-shape investigations.
Do not broaden runtime work until a reconstruction claim actually needs it.
