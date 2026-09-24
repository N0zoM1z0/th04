# MAINE cutscene helper boundary at payload 0xA815 (v572)

## Claim and limits

The target-derived decoded MAINE load module contains a contiguous 50-byte
function-like body at payload `[0xA815, 0xA847)`, loaded at `1A05:07C5..07F6`.
This is boundary progress only. The inventory's candidate name
`box_1_to_0_animate()` and its source/meaning are not target-attested; the
decoded-function ledger remains unchanged at 24 exact MAINE functions.

The packed MAINE target passed preflight with SHA-256
`670de6ba907a2edbc1592de810acd92e5b89541d3dc35b70210171166d1713f8` and the
active packed-target Ghidra database check passed. The retained target-roundtrip
MZ has SHA-256
`6b4547182b9d53d069c0e4efc33bdabb69065cb544bb187ced7b0f51918aa533`; the
target-restored payload has SHA-256
`7495ae43641bc696d13d18c366e364f6bc8b6a86a1afb681f34c9a334dae792c`. The
268-byte neighborhood `[0xA73B, 0xA847)` hashes identically when read from the
restored MZ load module and the retained payload.

## Boundary evidence

The fresh diagnostic-image Ghidra inventory check passed against
`analysis.exe` SHA-256
`332cbf172dec3394410f9d43844b2a81f8909a6b7ec48e989602d014a5aebcbc`. The
inventory row at `1A05:07C5` reports a single contiguous 50-byte body ending at
`1A05:07F6`, one caller, and four callees. This Ghidra result locates candidate
code but is not an independent semantics Oracle.

Independent NDISASM 2.16.01 decoding of target bytes from payload `0xA73B`
through `0xA846` shows the preceding body returning before `0xA78F`, a
`RET 2` at `0xA812`, two zero bytes at `0xA813..0xA814`, and the entry at
`0xA815`. The 50-byte extent ends with `pop si; pop bp; ret` at `0xA844..0xA846`.
The next reviewed physical entry begins at `0xA847`. A target-local near call at
`0xA75E` targets `0xA815`; the helper's target-observed call edges reach
`0xA2D6`, `0xA78F`, `CC7:0033`, and `0000:085C`. Local conditional branches
remain within the 50-byte span.

The target extent SHA-256 is
`a37885def37b920a0c19ce2670e7a0e7468fb74069bfe4565cd44f4a3b8c6b9f`. The
same slice hash was independently recorded from the restored-MZ and payload
views. The adjacent padding is outside this extent. The function-boundary row
is now `reviewed`; no source-presence, decoded exactness, or packed-file
exactness claim was added.

## Reproduction and next step

Evidence is recorded as `ev-th04-maine-box-animate-boundary-v572`. The durable
target-observation command is:

```sh
python3 scripts/preflight.py
python3 scripts/ghidra.py th04-maine check
python3 scripts/boundary_review/export_ghidra_inventory.py th04-maine \
  .analysis/reconstruction/probes/v569-polar-ghidra-prepare/th04-maine/analysis.exe \
  --format mz --project-name TH04-polar-boundary-maine-v569 \
  --export-dir .analysis/reconstruction/probes/v569-polar-ghidra-prepare/ghidra/maine check
dd if=.analysis/reconstruction/diet-replay/v228-maine-target-roundtrip/a/restored.bin \
  bs=1 skip=46395 count=268 status=none | ndisasm -b16 -o0xa73b -
```

Next, verify the candidate translation-unit composition and recover a natural
maintained MAINE source body before adding a cold replay backend. ReC98's
candidate name or generated match alone cannot establish source authority.
