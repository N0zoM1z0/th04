# TH04 native MAIN large-model runtime owners (v1131)

This note records a bounded ABI and startup experiment. It does not promote
the MAIN artifact or any of these owners to `exact`.

## Maintained owners

The TH04-owned tree now contains large-model providers for `EMS_*`,
`GRC_SETCLIP`, `TEXT_FILLCA`, `TEXT_PUTCA`, `palette_entry_rgb`, and
`SUPER_CONVERT_TINY`. The ASM providers use far Pascal entry points and keep
their algorithmic bodies separate from the pinned `masters.lib` calibration
members. `palette_entry_rgb_large.cpp` uses the maintained file and graphics
interfaces rather than copying archive declarations. The OP and MAINE source
manifests list these translation units so their source-graph checks remain
closed; this is routing/source-presence evidence only.

## Independent observations

- The pinned large-model MAIN boundary for `GRC_SETCLIP` ends in `RETF 8`, and
  the `SUPER_CONVERT_TINY` boundary ends in `RETF 2`; the archive calibration
  members use near returns. The maintained providers therefore model the
  observed calling distance without claiming target bytes.
- A clean v1108 diagnostic link with the EMS, text, palette, and other local
  owners compiled 193 C/C++ roots, 128 ASM roots, and eight state owners, and
  TLINK returned no unresolved symbols or overflow diagnostics. Its candidate
  MZ was 191,919 bytes with 1,182 relocations and SHA-256
  `c970879eabf7343575ce7fadf16442e03616e379b2f0a2d9069525f74007033e`.
  Receipt: `.analysis/reconstruction/probes/native-main-link-v1108-20260930/receipt.json`.
- The clean v1136 source replay includes both far owners and returns from TLINK
  with zero unresolved, duplicate, fixup-overflow, or group-overflow errors:
  193 C/C++ roots, 130 ASM roots, eight state owners, and four sprite owners.
  Its diagnostic MZ is 191,935 bytes with 1,182 relocations and SHA-256
  `895fe2d54479b7316f84abc817d9d40358f2ee31abc70f43a7b3fd05fb2757a1`.
  Receipt: `.analysis/reconstruction/probes/native-main-link-v1136-20260930/receipt.json`.

## Runtime frontier

The pre-owner v1130 GAME.BAT run stopped at the private `B5` marker during the
100-call `SUPER_CONVERT_TINY` preload loop. A later manual owner run reached
the EMS completion marker (`EMS.BIN=1D`) but its stage trace selected stage 3,
so the 0/6 play-character resource branch—and therefore the new conversion
call—was not exercised. The clean v1136 run has the same bounded result
(`MAIN.BIN=08`, `EMS.BIN=1D`) and a 45-second frame receipt. The comparison
receipts are retained under
 and
.

This leaves two separate blockers: establish the correct segment/order owner
for the far conversion routine without perturbing the surrounding runtime,
then force an evidence-backed stage-0/6 scenario and validate success/error
semantics independently. Neither marker trace waives target DATA/BSS layout,
relocation, raw-byte, cold-aggregate, or complete PC-98 startup gates.

## Artifact retention

Expanded source/object/MZ/HDI trees from this lane were compacted on
2026-09-30. Receipts, frames, and boot logs remain; the pinned runtime image,
toolchain, Ghidra database, and target corpus were not removed.
