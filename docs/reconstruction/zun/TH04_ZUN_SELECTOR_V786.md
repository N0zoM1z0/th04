# ZUN launcher selector source and boundary (v786)

## Target extent and ownership

The attested `th04-zun` decoded payload has a 223-byte selector stub at
`com-payload 0x12F..0x20D`, SHA-256
`cda3d3f38031f14988d236cc6725109d2f162e65224509101ca55c6dcb05fcfc`.
It consists of a two-byte entry jump at `0x12F`, a two-byte saved offset and
19-byte DOS error string at `0x131..0x145`, then a gap-free 200-byte dispatch
body at `0x146..0x20D`. The last instruction is a near jump at
`0x20B..0x20D` into the generated mover call at `0x352`. The separate
327-byte selector directory begins at `0x20E`.

Ghidra's earlier provisional body at `0x146` crossed into that directory.
Target decoding, the entry jump, branch closure, adjacent directory seam, and
the complete local build close the code extent at `0x20D`. The boundary ledger
now records `0x146+0xC8` as reviewed while retaining the raw Ghidra range
metadata as a rejected view.

## Maintained source and replay

`src/zun/launcher/selector.asm` is a semantic symbolic TASM source for command
tail parsing, embedded program lookup, FCB transfer, and relocation of the
selected COM. Its final `ORG` declarations reserve offsets for the directory
that the composite builder writes; they emit no bytes in the standalone stub.
The source uses neither copied target byte arrays nor filler instructions.
The pinned ReC98 `Pipeline/zun_stub.asm` corroborates the overall pipeline
shape, but is not treated as independent target or historical-source authority.

```sh
taskset -c 0,1 nice -n 10 python3 scripts/probes/replay_th04_zun_selector.py \
  --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME
```

The focused probe attests the target, TASM32 5.0, TLINK 6.10, DOS runner, and
source dependency. Two isolated cold rounds each produce a valid OMF with one
223-byte LEDATA at COM origin `0x100`, one FIXUPP record, and a 223-byte
linked selector. Both objects and linked files are deterministic. The complete
selector has zero raw differences against the target slice. Focused receipt:
`.analysis/reconstruction/probes/v786-zun-selector-focused-001/receipt.json`,
SHA-256 `40520e0ef44a6fa41112122efcd55260c86d8f1a97978ed698fe96550ce6376f`.

The unit is `source-present`. The generated directory, four embedded COM
components, move-up code, customization wrapper, and DIET-packed outer
`ZUN.COM` remain separate ownership surfaces; the selector match does not
promote any of them.
