# TH04-local BFNT sprite service

2026-09-28 native product-build batch. `super_sprite.cpp` owns BFNT pattern
registration, cancellation, release, and `SUPER_PUT` for MAINE. The separate
`super_state.asm` owns `super_buffer`, `super_patnum`, `super_patdata[512]`, and
`super_patsize[512]` in DGROUP with C/Pascal aliases. The product sources name
no ReC98 path. These are semantic owners; target-byte exactness is not claimed.

The pinned OP/ending PAR contains `SCNUM2.BFT`, SHA-256
`8c4715c11dcdd6ed63fdb0897268ade0cbdb4bc0ecf7b94c6294329ff645d03b`:
20 patterns, each 16×16 pixels, four packed color planes, one 48-byte palette,
and no extension header. The checked-in
`scripts/probes/probe_th04_native_super_runtime.py` extracts it from the
hash-checked HDI and PAR, executes a separate small-model historical
`masters.lib` BFNT loader, and executes the TH04-only large-model implementation
through the local PAR hook and as a loose DOS file. Both loaders produce the
same FNV-1a hash for all 3,200 stored mask/color bytes (`A24A77B5`) and the
converted 48-byte palette (`81529745`). The local fake-VRAM test draws three
patterns at unaligned and edge-clipped positions, then checks all four
32,000-byte plane buffers (`0BE615EA`). It also checks pattern cancellation,
free/reload, missing/bad files, hook shutdown, and 256 valid test-MZ
relocations at load segments `0x2000` and `0x6000`. Receipt SHA-256:
`fc981ebb45b3891319dbb35997da59adf2a9b90a479c749b477b453548a15eca`.

Two cold MAINE no-support links compile 128 TH04-owned translation units
(82 C/C++, 46 ASM) without warnings and leave exactly four BGM symbols:
`BGM_INIT`, `BGM_FINISH`, `BGM_READ_SDATA`, `BGM_SOUND`. All 128 link-relevant
and timestamp-normalized OMF objects agree. BGIMAGE alone has raw timestamp
drift. First no-support receipt SHA-256:
`252061159a52d858c8c64fb5065bb497aa37d2f32a11a0f3a4dec0cb010c1d6e`.

A diagnostic link with the pinned historical library resolves the four BGM
names with its known extended-dictionary warning. The MAP places local
`SUPER_FREE` at `07C9:47AC`, `SUPER_ENTRY_BFNT` at `07C9:47CE`, and
`SUPER_PUT` at `07C9:4B8E`; these are candidate link addresses, not target
MAINE addresses. Its MZ has 649 valid relocation sites at DOS load segments
`0x2000` and `0x6000`. The call audit checks 33 far returns, 141 relocated
direct far calls, and one same-CS far call. Calibration, MZ, and call-audit
receipt SHA-256 values are respectively
`3807bfda0e9e17a83bd1f3603bbafaaa7335dcb8f184e5f71844b764ee5b0caf`,
`bbf1ccac1825ce71f9b5c179ca024388a33200d57cd3b5c024a4b15113b1e963`,
and `04f6ad1e5c0bb12f4875d070e490af006753266d017460033cb24c67c07c89ae`.
The historical library is only a diagnostic input to this MZ.

The historical BFNT loader is near/small-model; its isolated harness is a
behavioral data Oracle, not a product link input. The local `SUPER_PUT`
implements the final four-plane pixel result through masked byte-sized planar writes and
leaves GRCG off. Its fake-VRAM test establishes the pixel transformation;
the OP animation scenario below covers one real-emulator path, while MAINE
page selection and ending display remain untested. Pinned
BFNT files have zero extension length; nonzero extension metadata and
transparent colors other than zero need separate coverage before reuse. The
historical `super_charfree` callback is outside this MAINE BFNT path.

## Byte-sized rendering and animation timing

The first standalone `SUPER_PUT` updated all four VRAM planes once per opaque
pixel. OP's ZUN Soft animation can issue 256 calls and visit 154,624 candidate
pixels in one frame; MAIN's big boss explosion can issue 16 calls over a
48×48 BFNT pattern. The maintained renderer now composes transparent masks
and colors per destination byte, including unaligned and clipped placements.
The DOS fake-VRAM test still produces screen hash `0BE615EA`; an independent
48×48 randomized comparison passed 45 clipped and unaligned positions. This
is a native product performance change, not a historical exactness promotion.

An isolated old/new OP startup comparison used the same pinned DOSBox-X
binary (SHA-256 `30a5fdf8fa95abaf7bae1a9e624ccfc9e26e5357a19cc567bf3a2ac659699258`),
disk-data source, and 10/20/30-second checkpoints. The old build remained in
the ZUN Soft fireworks at 30 seconds (`frame.png` SHA-256
`325fead5e24d9508531a2b1e1483e538169025e193e0ed2e9620938d27c52c48`);
the changed build reached the title menu (`7c1babb62b297a462173ed7428416af138059fa1d5e3d25bf84f10c3de029356`).
Private receipts are under
`.analysis/runtime/candidates/super-perf-{before,after}-20261002/run-logo/receipt.json`.
This is a bounded wall-clock observation under one emulator configuration,
not a full-game timing or Windows-host acceptance claim.

Replay the focused runtime gate with a fresh private directory:

```text
python3 scripts/probes/probe_th04_native_super_runtime.py --output-dir .analysis/reconstruction/probes/NEW-super
```

Replay full-link structure with fresh private directories, serializing the
three Borland builds:

```text
python3 scripts/probes/probe_th04_native_maine_link.py --without-support --output-dir .analysis/reconstruction/probes/NEW-super-a
python3 scripts/probes/probe_th04_native_maine_link.py --without-support --output-dir .analysis/reconstruction/probes/NEW-super-b
python3 scripts/probes/compare_th04_native_maine_link.py .analysis/reconstruction/probes/NEW-super-a .analysis/reconstruction/probes/NEW-super-b
python3 scripts/probes/probe_th04_native_maine_link.py --output-dir .analysis/reconstruction/probes/NEW-super-lib
python3 scripts/probes/audit_th04_native_maine_mz.py --link-receipt .analysis/reconstruction/probes/NEW-super-lib/receipt.json --output-dir .analysis/reconstruction/probes/NEW-super-mz
python3 scripts/probes/audit_th04_native_maine_call_abi.py --link-receipt .analysis/reconstruction/probes/NEW-super-lib/receipt.json --output-dir .analysis/reconstruction/probes/NEW-super-call
```

The four BGM names now form the MAINE no-support link frontier. `MIKO.EFS`
is the same 8,284-byte beeper-effect input in both PAR archives (SHA-256
`12045fed57d7c5a07da0047ae13c6607cbc78155cfbf5baa719fc310131de607`).
Its parser, sound buffers, timer/vector ownership, and PC-98 beeper output require a separate
bounded batch. Native MAINE still needs a TH04-only successful link, complete
relocation and ABI checks, and a game-entry PC-98 runtime scenario.
