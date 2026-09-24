# MAINE cutscene helper at payload 0xA815 (v573)

## Claim and limits

The target-derived decoded MAINE load module contains a contiguous 50-byte
function body at payload `[0xA815, 0xA847)`, loaded at `1A05:07C5..07F6`.
Maintained natural C++ in `src/maine/cutscene/box_animate.cpp` and
`box_animate.inl` now reproduces the complete decoded-function extent raw-zero
in two cold rounds. The exact-state decoded-function aggregate passes 25/25
MAINE slices. This does **not** make MAINE.EXE byte-exact: source is replayed
inside a pinned ReC98 v489 scaffold, the complete candidate MZ program image
is smaller than target, and no whole-file extent has been accepted. The
candidate name `box_1_to_0_animate()` remains an open, upstream-derived
hypothesis rather than a target-attested symbol.

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

Independent NDISASM 2.16.01 decoding tiles the 50-byte extent as 21
instructions with three direct branches; each branch lands on an instruction
inside the extent. It ends with `pop si; pop bp; ret` at `0xA844..0xA846` and
the next reviewed physical entry begins at `0xA847`. A target-local near call
at `0xA75E` targets `0xA815`. Relocation words at payload sites `0xA832` and
`0xA842` encode far pointers `0CC7:0033` and `0000:085C`; with the MZ image
loaded at segment `0x1000`, their runtime segment values are `1CC7` and
`1000`, respectively. Do not treat the encoded words as runtime addresses.

The target extent SHA-256 is
`a37885def37b920a0c19ce2670e7a0e7468fb74069bfe4565cd44f4a3b8c6b9f`. The
same slice hash was independently recorded from the restored-MZ and payload
views. The adjacent padding is outside this extent. The boundary row remains
`reviewed`; source presence is in `units.csv`, while decoded-function
acceptance is separately bound in `th04_decoded_function_acceptance.csv`.

## Boundary reproduction

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

## Natural source and replay evidence

The maintained body starts the EGC copy operation, checks the target-observed
8-bit `fast_forward` operand, iterates four mask values with `frame_delay`,
then copies the final mask and turns EGC off. This is a source hypothesis whose
complete generated function is byte-checked; it does not prove the upstream
name or source authority. The `CUTSCENE_TEXT` compiler producer spans payload
`[0xA292,0xAED0)` (`0xC3E` bytes), maps at `0A05:0242`, and its complete linked
bytes match the restored target. Only the 50-byte helper is credited as a
maintained exact function; the remaining producer bytes are still scaffold.
All 559 ordered MAINE MZ relocations agree with target. The candidate program
image is 62,414 bytes versus the target's 65,634 bytes.

Pinned TC86 standalone OMF and grouped-TU OMF are both valid. Standalone
LEDATA differs from grouped CODE only at offsets `[5,6,20,21,40,41]`; the
three 16-bit fields at offsets `5`, `20`, and `40` are unresolved same-TU
near-call fixups in the isolated object. Grouped compilation resolves those
calls and the complete linked helper is raw-zero. Grouped raw OMF files carry
Borland E9 dependency timestamps, so raw OMF hashes vary; strict E9
timestamp-normalized, link-relevant hashes are stable across the two rounds.

The focused maintained-source replay receipt is
`.analysis/reconstruction/probes/v573-maine-box-animate-fixup-006/receipt.json`
(SHA-256 `681a4e89aae7ef0e5f52addc9e48a36f0bccfbe5334cb90ddc85fbca5e4305cc`).
It records target function SHA-256
`a37885def37b920a0c19ce2670e7a0e7468fb74069bfe4565cd44f4a3b8c6b9f`,
producer SHA-256 `ff3e03ee0a5cf33604810a0ab8e70555d9cf4ec680f523fac7f13e7aec7390e6`,
and the two-round toolchain/OMF/layout checks. The exact-state aggregate
receipt is
`.analysis/reconstruction/probes/v573-maine-box-animate-exact-aggregate-002/receipt.json`
(SHA-256 `d46e3a1aa7e032106b3315727e11be926b94355367c5a15ae2d34d4f7f115d98`);
its helper subreceipt SHA-256 is
`280703540e52264add7173e95fa09b7f1ac6549426d17e2561d0b2972a861a58`.
Evidence is linked under `ev-th04-maine-box-animate-*-v573`.

Next, close natural source ownership around the larger reviewed MAINE
dispatcher at payload `[0xA847,0xADBC)` before adding another backend, or pivot
to a fresh target-first OP/ZUN owner. The local candidate `th04/cutscene.cpp`
is an include-only forwarder to TH03 and is not maintained MAINE source.
ReC98's candidate name or generated match alone cannot establish source
authority.
