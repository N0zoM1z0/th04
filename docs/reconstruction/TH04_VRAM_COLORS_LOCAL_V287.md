# TH04 VRAM color declaration, v287

The maintained MAIN renderers used `compat/rec98/th02/v_colors.hpp` only for
`V_WHITE`. The forwarded header supplied the value 15; no maintained source
uses its TH02 enum type. `src/shared/hardware/v_colors.hpp` now owns the
constant for TH04, and 37 product translation units include that header.
The old forwarder was removed.

The MAIN exact-unit replay now freezes recursively referenced `src/` headers
with the selected source, copies those frozen bytes into each cold source
tree, and records their digests. It never reads the live header during either
build. This gives the checked-in declaration a replayable input identity.

`python3 scripts/replay_th04_main_exact_units.py --run-id
gptweb-v287-vcolors-aggregate-001` passed twice for all 248 default MAIN
owners, with zero failures. Both candidate MAIN digests remain
`d859d5e5547baa963a6a2b441c771f7af865334e497143b85e0d5ca87d2c6a9e`.
The frozen header digest is
`4c9b3db236a9ca2ed4031c76907ad5f40646559362362e6fd4777ba1d9d88cb5`;
the private replay receipt digest is
`fa1bb2c54fa22fcbcef5cfcbaa4c0ed107a9378185244c11fc28d3f3a6949119`.
For example, `yuuka5_fg_render` remains raw/MAP/relocation exact in
`MAIN_TEXT` 0AAF:3DB3, load 0xE8A3..0xEA6E, file 0x100A3..0x1026E.

This is source and control-plane closure, not a new exact byte owner. Other
`compat/rec98` forwarders and the ReC98 build scaffold still block a
standalone product build.
