# TH04 MAIN B4M thick-laser producer review v181

## Scope

v181 reviews the complete historical `B4M_UPDATE_TEXT` thick-laser producer in
the attested local `th04-main / MAIN.EXE` target. The physical owner is
`13A9:22E4..243D`, MZ load `0x15D74..0x15ECD`, target file
`0x17574..0x176CD`, size `0x15A / 346`. It sits exactly between the accepted
v156 explosion owner and the accepted v157 Yuuka5 owner.

The target owner SHA-256 is
`e2f991b94fd1976978c612c8641c84ef4746f55493bfa66ef63fd08615c80627`.
The private target remains ignored operator input with only
`candidate-local-attested` provenance.

## Authored boundaries

Target-first raw decode, pinned TASM, v179 MAP ownership, and provisional
attested Ghidra observations agree on four contiguous logical functions:

| Function | Load extent | Size | Target SHA-256 |
| --- | --- | ---: | --- |
| `thicklasers_init()` | `0x15D74..0x15DA4` | `0x31` | `3cf6bdf754c21008fab0b8a311c5669a1114cd543835b8aac99befe750de0374` |
| `thicklaser_template_pull(thicklaser_t near&)` | `0x15DA5..0x15DBC` | `0x18` | `2fcf5853b4d28d55a6cdef3d4c8173daf8731288ac74464af89de7f1b30e38e3` |
| `thicklaser_add()` | `0x15DBD..0x15DE7` | `0x2B` | `ff93663e7e0686ab9f861ed38cbac6d55cc8aa532257d5f97d1884033518dff2` |
| `thicklasers_update()` | `0x15DE8..0x15ECD` | `0xE6` | `d5e1238ba29b4ed0d0fcf94a920271e354455170efc15e3de055419d13bfb51a` |

There are no gaps or post-return tables inside this producer. Exact
`yuuka5_move_transition()` begins at load `0x15ECE`.

Independent target call anchors close the internal starts. Session initialization
contains FAR CALL bytes `9A E4 22 A9 13` at load `0xB286`, resolving exactly to
`13A9:22E4`. `thicklaser_add()` calls the template helper from load `0x15DCF`.
Exact `y6_phase_dual_lasers()` calls `thicklaser_add()` from load `0x1AF91`.
Exact `yuuka5_update()` calls `thicklasers_update()` from load `0x169C4`.

The target ordered MZ relocation overlap is exactly
`[0x15E1B, 0x15DD7]`, the segment words of the `snd_se_play(6)` and
`snd_se_play(5)` FAR calls respectively.

## Historical producer ownership

The v157 replay scaffold extracts the entire target span as one zero-credit
`b4mthick.asm` object. The v179 exact MAP preserves one historical contribution:

`13A9:22E4 015A C=CODE S=B4M_UPDATE_TEXT G=MAIN_03 M=th04\b4mthick.asm ACBP=28`

This is stronger evidence than adjacency alone: the four functions are reviewed
as one physical producer, while logical function accounting remains separate.

## Natural source

Maintained source is `src/main/bullet/thicklaser_update.cpp`, SHA-256
`97b632ca700eaa8f8e55be1208cc337149306211e04e11a62469c2e00ae45a56`.
It reconstructs the init, add, update, and template-copy semantics using ordinary
C++ plus legitimate TC4J controls. It contains no inline assembly, emitted target
bytes, `#pragma codestring`, fake returns, inert padding, target patching, or ABI
fabrication.

Bounded compiler probes established the source mechanisms rather than spelling
matrices:

- the initial ordinary source emitted `0x157` bytes;
- `#pragma option -G` naturally restored the target classic stack frame of
  `thicklasers_update()` and its exact `0xE6` length;
- treating the flag comparison as unsigned naturally restored target `JBE`;
- Borland `__memcpy__()` naturally restores the complete producer size `0x15A`
  and exact public offsets `0x00 / 0x31 / 0x49 / 0x74`.

The remaining mismatch is isolated to `thicklaser_template_pull()`. The target
orders the copy setup as `MOV CX; PUSH DS; POP ES; MOV SI; MOV DI; REP MOVSW`.
TC4J's legal `__memcpy__()` intrinsic emits `PUSH DS; POP ES; MOV DI; MOV SI;
MOV CX; REP MOVSW`. Applying `-G` to the helper does not change this order.

ReC98's own `copy_near_struct_member` comment describes this family as the same
operation as `__memcpy__()` with reordered instructions, and its reproduction
uses inline assembly for `REP MOVSW`. That mechanism is deliberately rejected by
this reconstruction policy. No further source-spelling matrix is justified
without a genuinely new legal TC4J intrinsic, compiler-IR, or producer-history
hypothesis.

## Authoritative cold replay diagnostic

Focused historical dependency subsets were unsuitable for this current-source
candidate: one lacked the later B4M layout, another lacked later symbol aliases,
and an artificial union failed an earlier hash-bound scaffold gate. Those setup
failures have zero exactness meaning.

The authoritative diagnostic therefore used a bounded temporary default-enabled
v181 candidate on top of the complete current default cohort and immediately
restored the manifest afterward:

`python3 scripts/replay_th04_main_exact_units.py --run-id gptweb-v181-thicklaser-aggregate-negative-001`

Receipt SHA-256:

`087fbd90fb78599533ea70401d03dfbe252d266d17c7d01bca92f0760990a69b`

Two isolated cold builds select 215 owners. Every previously accepted default
owner passes. v181 is the sole failure, with:

- `map_exact_a/b = true`;
- `relocations_exact_a/b = true`;
- `object_valid_a/b = true`;
- slice and normalized-OMF determinism = true;
- `raw_exact_a/b = false`.

Candidate OMF SHA-256 is
`d30ce8a1d148b4dddd244c3a599bad801adf743eb33c9117d69a122fdd54b3ff`.
Candidate MAP SHA-256 is
`a44a9e0a09db5c5ef378e0138dfb63d5fbe9278a439a599a9c3f0a062dbb3083`.
The linked candidate owner SHA-256 is
`1731e8125b1eda9916b0a07bd8c7ea70aa18830a74f115999ede3875ca7ab26f`.

The target/candidate owner differs in exactly eight bytes, all at owner-relative
`0x36..0x40` inside the template-copy setup. The init, add, and update logical
slices are individually byte-identical in both cold builds. These slice matches
are diagnostic only: because the declared physical producer is not raw-exact,
none of the four functions receives function exactness credit.

## Accounting and verification planes

v181 expands the reviewed MAIN denominator honestly. Repository status after the
review is `74,881 / 80,148` exact reviewed authored bytes (`93.428407%`) and
`450 / 470` exact reviewed authored functions (`95.744681%`). MAIN now has 20
reviewed blockers and 67 unreviewed authored candidates.

No v181 exact promotion occurred. No focused exact receipt, candidate-state exact
aggregate, or post-promotion aggregate exists. The v179 post-promotion aggregate
remains the accepted repository-native exact baseline.

Standalone TH04 production compile/link closure, whole-image exactness,
runtime-storage identity, runtime-scenario validation, portable-runtime
validation, Factory Truth-Kernel acceptance, and independently pristine release
provenance are not established by this packet.

## v215 bounded aggregate-assignment control

A new TC86 Borland C++ 4.02 mechanism probe compared a plain 24-byte structure
assignment with `__memcpy__()` under the production `-ml -3 -O -Z -d -b-`
profile. The private input, two OMF objects, and JSON receipt are in
`.analysis/reconstruction/probes/v215-laser-assignment/`; receipt SHA-256 is
`fe4048274a8941c9899ffa16885d7582fff40dce74f8feaf40a79c5f7cc8604a`.
Target helper bytes at MAIN.EXE / B4M_UPDATE_TEXT `13A9:2315`, load
`0x15DA5..0x15DBC`, file `0x175A5..0x175BC`, are 24 bytes. The minimal
aggregate-assignment probe instead emits 23 CODE bytes containing a FAR runtime
copy call (`9A`) and no `REP MOVSW`; the intrinsic emits 24 bytes with the
already known wrong register-setup order. This falsifies simple aggregate
assignment as the natural source mechanism for the target helper. The probe
used an ordinary 24-byte struct, not the full `thicklaser_t` declaration, so
its conclusion is limited to that compiler pattern. No source change or exact
promotion follows.

## v277 copy-length producer control

`python3 scripts/probes/probe_th04_laser_count.py --output-dir
.analysis/reconstruction/probes/v277-laser-count-replay` attests the target and
TC4J, then compiles four 24-byte synthetic near-copy bodies under the production
flags. Direct `__memcpy__` emits 24 CODE bytes with the known wrong setup order.
Moving the byte count into a `register unsigned int`, expressing it as a
register word count times two, and using a local `const unsigned int` emit 32,
36, and 30 bytes respectively. Each valid OMF body retains one `REP MOVSW`;
none reproduces the target 24-byte sequence. Receipt SHA-256:
`0aa9ece20c046786cf989971dc38462d83627cdccf534f2cd1c55ffcf8394393`.
This rules out those count-expression mechanisms for the synthetic struct only;
the full producer remains blocked and its original source form unresolved.
