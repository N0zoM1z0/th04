# ZUN launcher mover and customization stub (v787)

The attested `th04-zun` decoded payload ends its four embedded COM components
with two separate launcher code regions:

| Region | Decoded payload extent | Source | SHA-256 |
| --- | --- | --- | --- |
| Selected-COM mover | `0x3422+0x8` | `src/zun/launcher/selector_moveup.asm` | `a580939da3b518b3001c1a4ff48fd9860511eddc239d702c6e13e41ac9125b00` |
| Outer customization stub | `0x342A+0x44` | `src/zun/launcher/customization_stub.asm` | `0982f4fa42c53b1df727fd10f64ef5ae2515bbdc90fb1a595209b8dc943d95fd` |

The eight-byte mover copies the selected embedded COM down to PSP:0100 and
returns to it. The 68-byte outer stub prints the usage text for `?` and `-?`
or relocates the inner composite over itself using lengths in the COMCSTM
header. Both sources use symbolic instructions and labels; neither embeds a
target byte array. The pinned ReC98 pipeline assembly describes the same
build mechanism but is corroboration, not independent target or original-source
authority.

```sh
taskset -c 0,1 nice -n 10 python3 scripts/probes/replay_th04_zun_launcher_tails.py \
  --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME
```

The probe attests target and tool identities, assembles each local source with
TASM32 5.0, checks valid OMF, then links a Tiny-model COM with TLINK 6.10.
Two isolated cold rounds produce identical objects and linked files. Each
complete linked stub is raw-identical to its full target extent. The OMF code
starts at COM origin `0x100`, has exactly the configured size, and has no
FIXUPP. The low-priority two-core focused receipt is
`.analysis/reconstruction/probes/v787-zun-launcher-tails-001/receipt.json`,
SHA-256 `52229ccedd3c1fccc3760a6ad2285e593fb77c12d9c31e15fed48a90b84b3001`.

Both units stay `source-present`: they are decoded payload extents, not
physical offsets in the DIET-packed MZ file. The generated directory, embedded
component source closure, and packed `ZUN.COM` are separate acceptance claims.
