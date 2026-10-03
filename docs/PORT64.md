# TH04 native x64 port

`port/modern-64` is a separate product based on the semantic DOS source. The
DOS build remains the behavioral reference and keeps its own Borland/TASM
acceptance rules. The portable product uses fixed-width state, ordinary host
pointers and host backends; it does not claim byte equality with PC-98 code.

## Current executable slice

`port64/main.cpp` currently owns the read-only resource path: TH04 HDI FAT12,
PAR directory/decompression and 16-color PI decoding. `port64/view.cpp` owns
the first graphics boundary. It decodes mask-only and combined CD2 sheets,
composes the recovered OP menu layout at 640x400, writes deterministic BMPs,
and opens an SDL2/Linux or Win32/GDI window. The user supplies the original
HDI or loose OP archive at runtime.

The title is a bring-up surface rather than a complete OP port. Up/Down moves
among six source-derived menu labels. Enter reports the selected index and
exits; Esc closes. Descriptions, option screens, transitions, idle demos,
sound and executable handoff remain to be migrated.

The first gameplay contract is separated into
`src/main/bullet/group_types.hpp` and `port64/bullet_geometry.cpp`. Both DOS
and portable sources share the numeric group and 8-bit clockwise angle
definitions. Portable persistent group storage is explicitly one byte.
Deterministic tests cover odd/even spread order, accumulator wrapping, rings,
aim plus template rotation, directional sprite cels and rejection of a zero
ring count. Random-number and speed state remain outside this bounded slice.

## Verified builds

The same source builds and runs as Linux ELF64 x86-64 and Windows PE32+
x86-64. Both decode the attested HDI fixtures with packed-pixel FNV32 values
`232AE649` and `EDFA0534`. Both produce the same title BMP, SHA-256
`b52ea8615865bfc11945fbe23828b7c391d8424c998062a8abfb5d62b4b31d2a`.
Both portable contract executables report `pointer_bits=64 angle_bits=8`.

Replay the complete cross-build check with:

```sh
python3 port64/verify.py \
  --linux-dir .analysis/port64/linux \
  --windows-dir .analysis/port64/windows \
  --hdi .analysis/runtime/images/zun.hdi \
  --output .analysis/port64/verification/receipt.json
```

The private receipt records executable format and hashes, the source manifest,
resource outputs and the HDI digest. It never copies game assets into the
repository.

## Migration order

1. Split the resource services behind reusable host interfaces while retaining
   the verified byte/pixel controls.
2. Migrate the full OP title input/timing and option state machine onto the
   framebuffer/palette backend.
3. Add audio and saved configuration adapters, then OP-to-MAIN/MAINE process
   transitions.
4. Port MAIN entity pools around fixed-width state, beginning with bullet
   generation and rendering controls.
5. Add route-level differential checkpoints for gameplay, Ending and score
   persistence on Linux and Windows.
