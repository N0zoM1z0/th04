# TH04 native MAIN EMS-stage startup differential (v1077–v1080)

This note records private runtime overlays used to bound the native MAIN
startup blocker after the v1074 normal-route differential. The overlays were
applied only to copied probe trees; no maintained `src/` file, target byte, or
shared input module was changed. The retained receipts are evidence of the
diagnostic runs, not product-build or exactness acceptance.

## v1077: native MAIN entry is reached

The selective relink receipt
`.analysis/reconstruction/probes/native-main-link-v1077-20260930/receipt.json`
(SHA-256
`0251152578490c1d5699ab6e8b11cc1b987f17c92d8f6dc284aa128554788492`)
links an MZ candidate of 191,469 bytes with 1,171 relocations and candidate
SHA-256
`5c7c5a3bebd96c41ea4b73693c871b1984c5f2c3dbe45ac7f3d2884811448029`.
The private MAIN trace writes marker `02` after `game_init_main()`; the
normal `GAME.BAT` run receipt

(SHA-256
`0929a56aaff3d831b35f24bf37b0d8692bae456786e16a4468498dc1b3bf0cc0`)
has `main_trace_hex = "02"`, no input trace, and frame SHA-256
`77f5aaa8cb211d336ff1fa899404e2ff580601f95289211aa25040bbbf65b12b`.
The run timed out in the host wrapper while remaining on the diagnostic
failure path. This is runtime-observed MAIN entry only.

## v1079: EMS capability boundary

The v1079 private EMS overlay split the original combined capability guard
into markers around `ems_exist()`, `ems_space()`, allocation, and preload.
The selective relink receipt
`.analysis/reconstruction/probes/native-main-link-v1079-20260930/receipt.json`
(SHA-256
`540ddebdc20833fa5104636087b96ca0b77780847592319b3ed2b8f513a8c51d`)
links 191,653 bytes with 1,175 relocations and candidate SHA-256
`0ee8d429345944074a4b292062865c945659e97d0045a57671f7ae824afb9ed5`.
The run receipt

(SHA-256
`7dfed96e195ed822af84d5c713c0ed2206da353e65ec9e157fe3f69e071cf73d`)
records `main_trace_hex = "02"` and `ems_trace_hex = "12"`. Marker `12` is
immediately before the `ems_exist()` call; markers after that call were not
observed. The frame SHA-256 is
`341223e8592bcb7ef5187180a0fedb1901e650bfbd5dff2387fc9e4dd6f4095d` and
shows an invalid-interrupt diagnostic (INT D1h). This bounds the next failure
surface to the EMS capability probe boundary or its diagnostic writer; it does
not by itself distinguish the two.

Static candidate inspection still shows calls to `EMS_EXIST` at `_TEXT:08CA`,
`EMS_SPACE` at `_TEXT:0A00`, and `EMS_ALLOCATE` at `_TEXT:08A4`, with MZ
relocations at the corresponding call operands. The support routine reads the
EMS IVT signature before the later INT 67h path, so the next experiment must
isolate the ABI/interrupt-vector behavior rather than copy target addresses or
bytes.

## v1080: skip-EMS follow-on (diagnostic only)

For a control experiment, a private overlay returned from the EMS preload
function after marker `10`. The selective relink receipt
`.analysis/reconstruction/probes/native-main-link-v1080-20260930/receipt.json`
(SHA-256
`4957570671712fe7e428f15a4b9399d27583b88a887d9919d781caf22a572847`)
links 191,269 bytes with 1,168 relocations and candidate SHA-256
`4e874d1ffe508ba4cbb4f8367fec398a7a47d802b01b2f555827e5ee97e1b681`.
The run receipt

(SHA-256
`87f8c9a4b55379389a6cd91ef301caaad777270dffc7d886a6c3b4fc153daa0e`)
records `main_trace_hex = "06"`, `ems_trace_hex = "10"`, and diagnostic
`START`/`EXIT` markers. It did not reach the first-frame input trace and ended
on a DOS abnormal-termination screen (frame SHA-256
`7160d771489043584deb4df7ca5aaadb087598942ba5d0cf510b88d6068a6404`).
Skipping EMS is therefore not a startup workaround or acceptance result; it
only shows that MAIN proceeds past sound initialization to the
`stage_session_init()` boundary under this altered diagnostic.

## Current boundary

The v1077–v1079 traces establish a runtime-observed path through native MAIN
and into the EMS preload boundary. Full startup, first-frame input behavior,
target DATA/BSS ownership, packed-file equality, and exact promotion remain
open. The next bounded probe should independently validate `ems_exist()` and
the PC-98 EMS/INT 67h environment while retaining the original source and
link layout. Any shared-header, segment, or global-layout change requires a
cold replay of affected units.
