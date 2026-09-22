# ZUN resident component separate link, v317

The pinned Japanese `ZUN.COM` is SHA-256
`0a12e9a489d3b704a77cf04ca3062ee48f298a9df6d237dc7dad46986e2d116e`
with `candidate-local-attested` provenance. Its independently decoded payload
is SHA-256 `baf5a58b333af1135d67c7dd7a4f86e2c828ae149c8219d5d1f589073b0bde9e`.
The embedded `RES_HUMA.COM` region is payload `0xB68..0x243F`, 6360 bytes,
SHA-256 `cdcb949b8b0353ebe5e83f4cd6e580d93cc5383b35b8cb9db3f820c151c95110`.

Run `python3 scripts/probes/replay_th04_zun_separate_link.py --output-dir
.analysis/reconstruction/probes/v317-zun-separate-link-ab`. The probe attests
the packed target and toolchain, compiles the maintained `cfg_init.cpp` and
`main.cpp` as **separate translation units** from only six checked-in TH04
source/header files, and links their valid OMF with pinned TLINK 6.10. The
link uses the standard TC4J startup and libraries plus the external ReC98
`masters.lib` diagnostic scaffold, SHA-256
`6be41dbcfcf4504977165ccc44443525a29a01f85a1580e6ad0c620bf802faf6`.
No ReC98 source or header is an input to the C++ compilation.

Two isolated cold rounds produce identical objects, MAP, and flat component.
MAP places `cfg_init` at `_TEXT:0367` for 152 bytes and `_main` at
`_TEXT:03FF` for 246 bytes. Their COM bytes begin at payload `0xDCF` and
`0xE67` respectively, matching the target entry locations. The linked
component is 6360 bytes, SHA-256
`a15ee1e7eac9616e9cd60656a00fb5700c7e20299efc2c0ab44bce6c27cf1dab`;
the MAP SHA-256 is
`ffda2356c3321b354cf7ae172da206667b7009ca506080fe69a95134efb2182e`.
Receipt SHA-256:
`be93bdfe2e111d301683f5ad8fb9ccd99530a23c7aa3c68a00bb50567b570d14`.

The target and product-source component differ at **4241 of 6360 bytes**.
The natural `_main` is six bytes shorter than the target's 252-byte body,
moving following support code by six bytes. In the pre-main and data ranges,
five CRT bytes, thirteen `cfg_init` bytes, and six data bytes differ; each
candidate value is six less than the target value, consistent with shifted
linked addresses. A diagnostic unified-TU
concatenation yields the **same** component SHA-256 as the separate-TU link,
so the tested C++ translation-unit split itself does not account for these
residuals. This is a diagnostic observation, not permission to insert six
target bytes or claim normalized exactness.

This closes an independent link step for the maintained ZUN C++ source.
`masters.lib`, ZUNINIT, MEMCHK, ONGCHK, the full composite build, and the
packer inputs still have external ownership; the natural `_main` body and
component raw bytes fail exactness. No ZUN unit or artifact is promoted.

## Current replay route (v508)

The old v317 path is a historical receipt location. The driver now obtains
the same hash-attested `masters.lib` from the protected v489 OP source snapshot
and materializes the current seven-file transitive TH04 source/header closure;
the stale `HEADERS` import and pruned v214 library path are removed. Run with
a fresh `--output-dir` under `.analysis/reconstruction/probes/`, or use the
common `python3 scripts/decoded_function_acceptance.py --artifact th04-zun`
entrypoint. The latter's v508 receipt SHA-256 is
`6542091d838059274c470c9f567c2e3bb2ba57d42a71f411cca99326908560b5`.
Two cold links reproduce the v317 component SHA-256 and 4,241 differences.
Within target-sized function extents, `cfg_init` differs at 13 linked bytes
and `_main` at 130 bytes; neither is decoded-exact. The current acceptance
contract and limits are in the
[v508 note](../packed/TH04_DECODED_FUNCTION_ACCEPTANCE_V508.md).
