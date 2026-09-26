# ZUNINIT complete symbolic component (v785)

## Claim and extent

The hash-attested `th04-zun` decoded payload contains ZUNINIT at
`com-payload 0x6F3..0xB67`, 1,141 bytes, SHA-256
`692b1e056d907a9649bd1effa6e83239f71039d17de3569464067d0b42b7aa5e`.
The v520 target boundary review partitions this component into eight code
entries and two data islands. The six maintained translation units below cover
the complete file extent. Their COM runtime offsets begin at `0x100`; TLINK's
`ORG 100h` allocation in the first module is the COM address base and is not
an extra 256 file bytes.

| Source | TLINK `_TEXT` allocation | Decoded file extent | Content |
| --- | ---: | ---: | --- |
| `interrupt_ui.asm` | `0x0000+0x1BD` | `0x6F3+0xBD` | Entry, FAR STOP/COPY handlers, modal |
| `text_support.asm` | `0x01BD+0x4D` | `0x7B0+0x4D` | Shift-JIS converter, text writer |
| `messages.asm` | `0x020A+0x102` | `0x7FD+0x102` | Resident marker, vector slots, UI text |
| `resident_check.asm` | `0x030C+0x27` | `0x8FF+0x27` | DOS banner and resident check |
| `main.asm` | `0x0333+0xDA` | `0x926+0xDA` | Command parsing, vector lifecycle, DOS exit |
| `trailing_text.asm` | `0x040D+0x168` | `0xA00+0x168` | DOS output messages |

Source paths are all under `src/zun/zuninit/`. These are reconstructed,
symbolic original-style ASM units, **not recovered literal historical source**.
The origin classification is an inference from the flat register ABI, FAR IRET
handlers, direct DOS and PC-98 interrupt calls, VRAM writes, and corroborated
cross-game lineage of the text helpers. The old ReC98 source is IDA-generated
and supplies no original-source authority. Strings are readable Japanese
literals converted from UTF-8 to CP932 before assembly; source contains no
copied target byte arrays or filler directives.

## Cold link evidence

Run with a fresh direct child output directory:

```sh
python3 scripts/probes/replay_th04_zuninit_symbolic.py \
  --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME
```

The checked-in probe verifies the pinned target, TASM32 5.0, TLINK 6.10,
DOS runner, all six source hashes, OMF LEDATA/FIXUPP ownership, complete MAP
placement, and COM entry `0000:0100`. It builds twice in separate directories.
All six objects, MAP files, and complete COM files agree across the two rounds.
Both COM files are raw-identical to the complete 1,141-byte target component.

Focused receipt:
`.analysis/reconstruction/probes/v785-zuninit-symbolic-001/receipt.json`,
SHA-256 `352e2a429caa86a090c61ddd2740f126fcf2d3c76f0c95b8c54c95a7eb28bca6`.
The target-derived boundaries remain independently supported by v520. The
converter and text writer also retain their v777/v778 runtime Oracles.

The six units stay `source-present` in `config/units.csv`: they have decoded
component offsets, not physical file offsets in the packed MZ container. This
result establishes complete raw equality for ZUNINIT.COM only. The packed
outer `ZUN.COM`, its other embedded components, and historical ASM provenance
remain open.
