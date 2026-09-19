# DIET 1.45f target round trip and candidate frontier (v228)

## Claim and replay

`scripts/probes/roundtrip_diet_target.py` starts from two isolated, verified
copies of each **packed target**, runs DIET 1.45f `-RA`, verifies the restored
payload and relocation application order against the independent target-stub
observation from [v218](TH04_PACKED_PAYLOAD_FRONTIER_V218.md), and packs both
copies again. `config/diet145f.toml` pins the public release archive, DIET
binary, DOSBox-X profile, and artifact-specific pack options. This is a
**target-derived packer calibration**: equal output is circular and earns no
source or exact-unit acceptance.

| Artifact | Target packed | Restored target copy | Extra zero bytes after observed payload | Pack options | A/B repack |
| --- | ---: | ---: | ---: | --- | --- |
| OP.EXE | 42,290 | 76,864-byte MZ; 804 relocations | 3,228 | `-B -G` | Both raw equal target |
| MAINE.EXE | 38,035 | 69,218-byte MZ; 559 relocations | 3,220 | `-B -G` | Both raw equal target |
| ZUN.COM | 7,754 | 13,422-byte flat COM | 0 | `-B` | Both raw equal target |

The v228 receipts are
`.analysis/reconstruction/diet-replay/v228-{op,maine,zun}-target-roundtrip/receipt.json`.
Their SHA-256 values, respectively, are
`d21980d651da9a1d0a28de7a8e49561714f3c40e81207fc62c7f9820d86b91f2`,
`d57ca6fb9b53406716ed9332e9ed2662d0ee0ec62a56bffaed23ac018858ee9e`,
and `42f6d51551808e16544f3440a9d307e4b8f0df2884757b6b5cdd0430c996e40f`.
Both cold restored outputs and both repacked outputs are identical per
artifact. Restored files are retained as `a/restored.bin` and `b/restored.bin`.

For OP/MAINE, the restored MZ program-image prefix is exactly the independent
v218 target payload. The following 3,228/3,220 bytes are all zero. DIET's
restored relocation table order equals its stub's relocation **application**
order. It is not evidence for the lost historical TLINK relocation order or
original unpacked MZ header. The restored MZ is a DIET-generated view.

## Current source-candidate comparison

`scripts/probes/replay_diet145f.py` packed the two byte-identical v214 cold
**ReC98-overlay** candidates with the calibrated options. A/B packed outputs
are identical, but only ZUN equals its complete packed target:

| Artifact | Candidate packed | Target packed | Raw result | v226 receipt SHA-256 |
| --- | ---: | ---: | --- | --- |
| OP.EXE | 42,251 | 42,290 | different | `40026279b6fb3b18df5097764d8ec4c5d28f9717dca0ce9ef482617d2ecb9860` |
| MAINE.EXE | 37,985 | 38,035 | different | `574367076ed70ded452bd7c99793f92b770390902c7a75939e27bceb8294aaaa` |
| ZUN.COM | 7,754 | 7,754 | raw equal | `847b3a701b01b22f034b6aa020701d4e0997620d358a30e2e4b9e355850661c4` |

The candidate input payload residual remains OP seven bytes and MAINE five
bytes. OP/MAINE candidate MZ headers and ordered relocations also differ from
the DIET-restored target view, whose topology itself may have been changed by
`-RA`. The 39/50-byte packed length gaps therefore cannot be assigned to
source opcodes alone. The ZUN candidate composite includes IDA-derived ASM
and an external ONGCHK binary; its raw equality is a packaging diagnostic,
not authored-source credit.

The earlier [v224 note](TH04_DIET145F_PACKING_V224.md) records an initial
`-B` experiment on all three artifacts. `-B -G` is the current calibrated
OP/MAINE recipe; the earlier `-B` failures remain valid negative controls.
The subsequent [v231 MZ partition](TH04_DIET145F_MZ_PARTITION_V231.md)
confirms byte-for-byte `-RA` inversion of our candidate MZs and localizes
the candidate-versus-target-restored difference to payload, ordered
relocations, and coupled header/tail topology. Recover natural source and
standalone link ownership before any acceptance claim.
