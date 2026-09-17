# ZUN resident declaration localization, v309

The pinned Japanese `ZUN.COM` is SHA-256
`0a12e9a489d3b704a77cf04ca3062ee48f298a9df6d237dc7dad46986e2d116e`
(`candidate-local-attested`). Preflight and the live ZUN Ghidra MZ/database
check passed. The independently decoded payload is SHA-256
`baf5a58b333af1135d67c7dd7a4f86e2c828ae149c8219d5d1f589073b0bde9e`.

`src/shared/config/resident.hpp` now owns the TH04 resident declaration used
by maintained ZUN `cfg_init` and `_main`. The target `_main` at decoded `_TEXT`
`0xE67..0xF62` clears a `0x100`-byte block and writes `debug` at offset
`0x1A`; MAIN gameplay reads `rem_lives` at offset `0x0B`. The header makes
these offsets, the total size, and the current 16-bit `frames` layout fail
at compile time if they drift. The remaining member names and widths come
from the ReC98 candidate layout and remain inferred pending field-specific
target or runtime evidence.

The two checked-in diagnostic replays copy this header into each isolated
source snapshot and replace the wrapper's external `th04/resident.hpp`
include. Run, serially:

```sh
python3 scripts/probes/replay_th04_zun_cfg_init.py --output-dir .analysis/reconstruction/probes/v309-zun-resident-local-cfg
python3 scripts/probes/replay_th04_zun_main.py --output-dir .analysis/reconstruction/probes/v309-zun-resident-local-main
```

Both A/B TC4J 4.02 objects pass OMF parsing and are deterministic. The
standalone `cfg_init` CODE remains 152 bytes, SHA-256
`4c80c1405ba9994053738757cbdad5478425ff6ff92baf455c8f2f4c32383fd4`;
the diagnostic composite still links the target `cfg_init` bytes at
`0xDCF..0xE66`, produces the same `RES_HUMA.COM` digest
`cdcb949b8b0353ebe5e83f4cd6e580d93cc5383b35b8cb9db3f820c151c95110`,
and DIET packs the full untrusted composite raw equal to the target. The
standalone `_main` CODE remains 246 bytes, SHA-256
`24ddea5b31e175794bfd602f08bec7a03a88e26d9e39341c32e2690e9e3557ea`,
against 252 target bytes. The header SHA-256 is
`414a76887fbcee144886607705f22df827838245524d0c41708dc8a4332d6ec8`.

Private receipt SHA-256 values: `cfg_init`
`9c9433524c7864c343d3af3b29b299c5a328a8f2444ebfca63f31cc3bfd7acf4`;
`_main` `5b9f4de92ad46b53e139c5995d8efe699f0f2c88b9d08a61e91b212dd4434544`.
This is a checked-in declaration and source-closure improvement. Other ZUN
headers, support objects, ZUNINIT/MEMCHK, and ONGCHK still come from the
pinned ReC98 scaffold; neither a standalone build nor artifact-local exact
acceptance is established.
