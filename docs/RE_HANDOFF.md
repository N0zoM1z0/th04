# Current handoff

## Phase

Control-plane, target-ingestion, and Oracle-calibration bring-up.  No TH04
source or unit has been accepted yet.

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

## Open provenance issue

The local hashes identify this exact legal disk image, but have not yet been
confirmed against an independently sourced pristine dump.  Keep
`canonicality = "candidate-local-attested"` until that independent check
passes.  A ReC98 rebuild is useful toolchain/output calibration, but upstream
status alone is not independent provenance or acceptance evidence.

## Tool blockers

- Turbo C++ 4.0J/TASM/TLINK are not installed or attested.
- No DOSBox-X, Neko Project II debug build, IDA, or Ghidra headless backend is
  currently available on `PATH`.
- `ndisasm`, GNU `objdump`, Wine, `unar`, and mtools are available.

## Next bounded work

1. Attest/install the exact Borland toolchain and independently reproduce the
   ReC98 TH01 outputs as untrusted positive-control candidates.
2. Pass those locally built outputs through this repository's complete target,
   MZ, relocation, layout, and raw-byte comparison stack.
3. Select a headless 16-bit MZ analysis backend and build a reproducible TH04
   database/export with segment:offset and relocation awareness.
4. Generate the initial artifact/segment/function inventory without making
   source or exactness claims.
