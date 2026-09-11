# TH04 MAIN_033 Orange bounce/random phase v132

## Scope

- Artifact: `th04-main / MAIN.EXE`
- Segment: `MAIN_033_TEXT`
- Historical TASM PROC: `orange_19878`
- Reviewed load extent: `0x19878..0x1998A`
- Reviewed file extent: `0x1B078..0x1B18A`
- Ghidra image extent: `0x29878..0x2998A`
- Size: `0x113 / 275` bytes
- Target slice SHA-256: `2ff70fb11ee2af9cefdeba1c7a454cbadf28050af5d8ce0b4e5e4fcdc6c4733d`
- Overlapping target MZ relocations: load `0x198AD`

## Boundary review

Fresh attested Ghidra constructs `FUN_23a9_5de8` only over the first eight bytes
at image `0x29878..0x2987F` and reports no callers or callees. That body is a
truncation, not a function boundary. Pinned TASM keeps `orange_19878 PROC near`
open through the terminal `POP BP; RET` at load `0x19989..0x1998A`, and the next
historical PROC begins immediately at load `0x1998B`. A gap-free raw 16-bit
decode agrees with the TASM control flow throughout all 275 bytes. The residual
`boss.mode` dispatcher contains the unique direct call to `orange_19878`.
There is no shared tail, post-return table, or jump out of the reviewed extent.

The reviewed authored denominator therefore uses the full 0x113-byte extent,
not Ghidra's eight-byte body.

## Natural-source probe

`src/main/boss/orange_phase_bounce_random.cpp` expresses the motion, playfield
bounce, Easy-rank frame gate, HP/rank bullet-count selection, and two independent
random bullet-type/angle shots as ordinary C++. The first probe stored the
`PlayfieldMotion::update_seg3()` structure return in a local. TC4J consequently
emitted `ENTER 4`, a saved `SI`, and a `DX:AX` spill, producing 289 bytes.

The historical header explicitly documents callers that consume
`update_seg3()` through the returned AX/DX registers. Using `_AX` immediately
after the call is therefore an evidence-backed 16-bit source idiom, not inline
assembly or an ABI fabrication. That form emits one 275-byte `MAIN_033_TEXT`
LEDATA with the same 85-instruction shape as the target, including the target's
unsigned `JBE/JB` X-bound checks. Source SHA-256 is
`566e789a51dc072b175345e6b1b5815b52b7496538d4d1cd61dfcee77b59f178`.

This compiler-shape result had zero exactness credit by itself. At that probe
stage the native unit remained `candidate` and the reviewed function remained
`blocked`; promotion occurred only after the focused and aggregate cold replays
below established exact map placement, ordered relocation overlap, raw bytes,
OMF integrity, and determinism.

## Exact replay

Focused replay `gptweb-v132-orange-bounce-random-focused-002` selected the
104-owner dependency closure and passed both isolated cold builds. In A and B,
`th04/orbounce.cpp` contributes exactly `MAIN_033_TEXT 13A9:5DE8`, size `0x113`;
the candidate and target slice SHA-256 are both
`2ff70fb11ee2af9cefdeba1c7a454cbadf28050af5d8ce0b4e5e4fcdc6c4733d`,
and both ordered overlapping relocation lists contain only load `0x198AD`.
`orbounce.obj` is valid `TC86 Borland C++ 4.02` OMF with raw SHA-256
`4d8af83c3ce307f2c258f044aebb6d8b31164896a16955798c3cfd3a7dde2d06`
and dependency-timestamp-normalized SHA-256
`717733fbfea5edea298f789efcf7d40e596433dd20f4711a1d5956e6d76827b1`
in both builds. The focused receipt SHA-256 is
`f734733391b89b1ccf586ca9b11fdf9db9406d9f16f06090e06fac90320d1644`.

Required aggregate replay `gptweb-v132-orange-bounce-random-aggregate-002`
then passed all 168 default owners twice. Both aggregate candidates have SHA-256
`b75b810982f384bdd2cfca76d64e8401e818712facaa3c6c9f3e705374e83b6a`;
the v132 owner retains the exact map/raw/relocation/OMF result above and no prior
accepted owner regresses. The aggregate receipt SHA-256 is
`8208a6e4c9c97b4646f2f58e1917b3b5b344301f3b905c56b8c903be39522998`.

These repository Oracles establish exact ownership of this reviewed extent.
After committing the claim at `37d3cb0c6e1a6e16764d4fb1fd320b8c358c2dee`, Factory Truth-Kernel job `job:e64738fc545a4434bc6cae63d69ff2b5`
independently replayed `claim:unit:th04-main-orange-bounce-random-v132:owned-extent-exact` under `isolated-double-build`. Factory receipt
`receipt:6db3097e1b081a55569cadbfda0f143c0e2bb013cdb157fb18c48353b49814a5` returned `receipt_verdict=pass` and
`acceptance_decision=accepted`; the accepted registry identity reported by that
job is `registry:e136ea293207da22f0a7286eee362765d399f9f587ac32369a9459c7619b7d29`. This Factory acceptance is scoped to the v132
`owned_extent_exact` claim. It does not establish standalone TH04 product
closure, runtime-storage identity, or runtime-scenario validation.
