# Current handoff

## Phase

Control-plane, target-ingestion, build-chain calibration, and headless Ghidra
bring-up. No TH04 source or unit has been accepted yet.

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
- The local candidate build chain pins and validates TC4J media plus installed
  BIN/INCLUDE/LIB/startup trees, TCC 4.02, TLINK 6.10, TASM32 5.0,
  configuration files, Wine 8.0, and ReC98's MS-DOS Player P0281 binary.
- Two execution-probe rounds produced identical C OMF, ASM OMF, map, and MZ
  outputs.  Embedded OMF producers and the compiler's `dos.h` dependency agree
  with the pinned installation; the linked DOS probe executes successfully.
- An empty-clone bootstrap test independently downloaded and rebuilt the
  complete private toolchain and passed all 16 identity/execution surfaces.
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
  relocation, mapping, and stale-nonce mutations all fail the intended
  database-Oracle dimension.

## Open provenance issue

The local hashes identify this exact legal disk image, but have not yet been
confirmed against an independently sourced pristine dump.  Keep
`canonicality = "candidate-local-attested"` until that independent check
passes.  A ReC98 rebuild is useful toolchain/output calibration, but upstream
status alone is not independent provenance or acceptance evidence.

## Remaining tool gaps

- No DOSBox-X or Neko Project II debug runtime is installed yet.
- No IDA backend is installed. Pinned Ghidra is operational through
  `.tools/ghidra` and `scripts/ghidra.py`; it intentionally need not be on the
  host `PATH`.
- `ndisasm`, GNU `objdump`, Wine, `unar`, and mtools are available.

## Next bounded work

1. Extend the headless Ghidra private export with a bounded provisional
   function/xref inventory when the reconstruction phase begins.
2. Generate the initial artifact/segment/function inventory without making
   source or exactness claims.
3. Use bounded compiler/ABI probes and map/OMF evidence to separate
   compiler-library ownership from game-authored units.
4. Reconcile the cold-built ReC98 TH04 maps/link responses against the pinned
   target topology before selecting a first bounded reconstruction unit.
