# ZUN configuration layout and defaults, v311

The pinned Japanese `ZUN.COM` (SHA-256
`0a12e9a489d3b704a77cf04ca3062ee48f298a9df6d237dc7dad46986e2d116e`,
`candidate-local-attested`) and its live Ghidra database passed the MZ check.
The independently decoded target payload is SHA-256
`baf5a58b333af1135d67c7dd7a4f86e2c828ae149c8219d5d1f589073b0bde9e`.

The target `cfg_init` at decoded `_TEXT` `0xDCF..0xE66` passes six bytes to
the options write, ten bytes to the configuration read, and seeks to byte
offset six for the resident pointer. The target payload's unique default
options at `0x2067` are `FF 03 02 01 01 01`. The checked-in
`src/shared/config/cfg.hpp` fixes those record sizes and offsets with TC4J
compile-time checks. `src/zun/config/defaults.hpp` owns the target-observed
default values, removing the maintained ZUN configuration source's direct
TH01 rank, TH03/TH02 configuration, and ReC98 TH04 sound-header dependencies.

The replay wrappers now replace those external includes with the checked-in
headers. Run the two independent compiler/link/DIET diagnostics serially:

```sh
python3 scripts/probes/replay_th04_zun_cfg_init.py --output-dir .analysis/reconstruction/probes/v311-zun-cfg-local-verified
python3 scripts/probes/replay_th04_zun_main.py --output-dir .analysis/reconstruction/probes/v311-zun-cfg-local-main
```

Both A/B builds retain the 152-byte standalone `cfg_init` CODE SHA-256
`4c80c1405ba9994053738757cbdad5478425ff6ff92baf455c8f2f4c32383fd4`.
The diagnostic linked component's six default bytes and `cfg_init` body match
the decoded target; its complete flat payload and DIET-packed candidate also
remain raw equal. Maintained `_main` remains 246 versus 252 target bytes.
The local configuration and default header SHA-256 values are
`34786f7e5b50d5230044e60725c60e7b553988fd20009046380d09edeb227243`
and `7561598f37a986cf8ce54c019bb379b9746021f021ca22d319954341377a4b56`.
Private receipt SHA-256 values are
`5179f6bfb6aa2e6803eac9ef7cf40f062ba8d520d5c8b9361cdc1788055a58d2`
and `b94729adf091a7cd3c5f9b1f25cd60099a2b9c1ce8e21cb28b6fee8ca0ed0ace`.

This localizes source declarations, not the ZUN product build. The diagnostic
still links ReC98 support objects and uses external ZUNINIT/MEMCHK/ONGCHK;
artifact-local exact acceptance remains open.
