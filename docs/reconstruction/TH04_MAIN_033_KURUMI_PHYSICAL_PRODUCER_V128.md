# TH04 MAIN_033 Kurumi physical producer v128

## Scope

v128 recovers the original Turbo C++ physical producer spanning Kurumi
`MAIN_033_TEXT` from load `0x18A14` through `0x195E3`. Earlier v124-v127
packets reconstructed semantic functions in this range as separate exact
owners, but the first natural `kurumi_update()` replay failed only the ordered
MZ-relocation gate. That failure identified an incomplete physical-TU boundary,
not a byte/code-generation defect.

The final natural producer is one TLINK contribution:

- `MAIN_033_TEXT` / `MAIN_03`;
- map `13A9:4F84`, size `0x0BD0` / 3,024 bytes;
- load `0x18A14..0x195E3`, file `0x1A214..0x1ADE3`;
- diagnostic full-range SHA-256
  `4a839795417695cd1412c40d99cc37408e835f70043870012adbeb4b1e438159`.

Maintained semantic source remains split under `src/main/boss/`:
`kurumi_spawnrays.cpp`, `kurumi_spawnray_phases.cpp`,
`kurumi_late_phases.cpp`, `kurumi_bullet_stacks.cpp`, and
`kurumi_update.cpp`. When `TH04_KURUMI_MAIN033_COMBINED` is defined,
`kurumi_update.cpp` includes the existing semantic fragments in target order so
the Oracle emits one physical TC4J object. The fragments retain standalone
preambles outside that mode. No target-byte emission, inline assembly,
`#pragma codestring`, fake returns, inert padding, or object patching is used.

## Dispatcher boundary

Fresh Ghidra starts FAR `kurumi_update()` at linear `0x2915D` but cross-links
to `0x2A71F` while recording only 41 body addresses. Pinned TASM and gap-free
target decoding prove instead:

- executable function load `0x1915D..0x195C2`, `0x466` / 1,126 bytes;
- terminal `RETF` at the end of that span;
- one alignment byte at `0x195C3`;
- trailing 4-, 5-, and 7-entry near switch tables through `0x195E3`;
- complete compiler owner `0x1915D..0x195E3`, `0x487` / 1,159 bytes;
- owner SHA-256
  `ee4c76d8aa70d2665ffd07d22f7bf0976e49e05e3fee34afa4df7e5a64d56451`;
- ordered MZ relocations
  `0x19591, 0x19457, 0x1925F, 0x19233, 0x19212`.

Function review intentionally counts only the executable `0x466` bytes. The
following `0x21` bytes remain exact compiler-owned data in the byte owner.

## Orbit helpers and physical-TU diagnosis

The last replay-only code between the existing v124 and v125 natural owners was
two adjacent 63-byte near helpers:

- `kurumi_orbit_step_forward()`: `0x18B68..0x18BA6`;
- `kurumi_orbit_step_reverse()`: `0x18BA7..0x18BE5`.

Their combined 0x7E-byte target SHA-256 is
`6e0519f60a1936046594b8c611245e2d9ed6086830073cd46c44382b97dee340`.
Fresh Ghidra constructs both bodies completely. Natural C++ emits both exact
63-byte skeletons; target packed `polar()` calls require source argument order
`(192, 64)` and `(91, 20)`.

The earlier `gptweb-v128-kurumi-update-focused-002` reproduced dispatcher bytes,
map placement, OMF, and relocation addresses but failed ordered relocations:

target: `19591 19457 1925F 19233 19212`

candidate: `19457 1925F 19233 19212 19591`

The Oracle was not weakened. A wider relocation audit showed that this ordering
comes from TC4J physical translation-unit/FIXUPP grouping. The exact Kurumi
ranges tile without gaps:

`0x154 + 0x7E + 0x1D0 + 0x2A4 + 0x103 + 0x487 = 0xBD0`.

Diagnostic full-producer probe 014 combined those maintained natural bodies in
one TC4J object. It matched all 3,024 target bytes and all 28 ordered MZ
relocations. This diagnostic has no exactness credit by itself; the formal cold
replays below provide acceptance evidence.

## Replay layout and final Oracle results

When v128 is active, v124-v127 use producer overrides so all six ownership
ranges come from `obj/th04/kupdate.obj`. Its map contribution is:

`13A9:4F84 0BD0 C=CODE S=MAIN_033_TEXT G=MAIN_03 M=th04/kupdate.cpp ACBP=28`.

The old `m33kpre.asm` becomes a valid zero-code auxiliary object and
`m33kseam.asm` retains only code after the Kurumi producer. Both remain
hash-bound replay plumbing with zero reconstruction/function credit.

Final manifest SHA-256:
`4ac55fb4ccd0f3e4c720853a776c039778cf4dadca747a5c0de6a281c05fe62a`.

`kurumi_update.cpp` SHA-256:
`03e7695dfc88a78ddc1553aa8913247c6df83d53de17242b57462c3a81c86f49`.

Final focused replay:

`gptweb-v128-kurumi-full-focused-002` — PASS, `failures=[]`.

Receipt SHA-256:
`8fdb4094b0a021ad71593d3f43af16ea05a5f8e764f85d92815937b5684a2999`.

Both A/B builds emit candidate MAIN
`978bd87221b7b539fd38c3a81d85c6aa3bc7a33b2c9eb29a75d25bf770d9bde5`,
raw `kupdate.obj`
`bee9be8ae23512cfad1043f88c947a1f6616d155fbc2bc59239ebcb0415802c9`,
and normalized OMF
`37cd43983e5530355f355fbb217bac1776932331549f7453a29859cd69641d8f`.

Mandatory aggregate:

`gptweb-v128-kurumi-full-aggregate-001` — PASS, `failures=[]`, 165 default
owners in two isolated cold builds.

Receipt SHA-256:
`e7ab2f885ad537be52f5139a9c945b6a98bccfcc7c7b7de0a04af860db6f2989`.

Both aggregate builds emit candidate MAIN
`a43129b502291d37518347a554ffc8eada80ee073b9e5fc737a8740ed927cbb1`.
No previously exact owner regresses.

## Function review and metrics

Private report:
`.analysis/reconstruction/functions/function-review-v128-current.json`.

Report SHA-256:
`978fd9750841bc937c028fe89bc58d9e99f45957aab42246c01a538abb193055`.

Result:

- 289 / 291 exact functions = 99.312715%;
- automatic 144, manual 145;
- strict rejections 0;
- reviewed nonexact functions 2.

The two orbit helpers use normal contiguous-Ghidra/TLINK/exact-owner admission.
`kurumi_update()` uses `reviewed_exact_extent` over the 0x466 executable body:
329 gap-free decoded instructions ending in `RETF`. Its 0x21 trailing compiler
data is not counted as function-body bytes.

Current reviewed C/C++ bytes are 45,253 / 45,284 exact = 99.931543%, with 165
exact C/C++ owners. These are reviewed-ledger metrics, not percentages of the
executable or whole game.

## Independent planes and continuation

v128 establishes bounded repository focused/aggregate exactness only. It does
not establish standalone TH04 product closure, runtime-storage identity,
deterministic runtime validation, whole-image exactness, portable runtime
validation, Factory Truth-Kernel acceptance, or project completion.

The next adjacent candidate is `orange_195E4`:

- load `0x195E4..0x19685`, file `0x1ADE4..0x1AE85`;
- physical size `0xA2` / 162 bytes;
- target SHA-256
  `28ec524c11fbf14f6dec94f4a24c5fa16b21461952a75ecadfc93b6f8e450b1a`;
- one MZ relocation at `0x19668`;
- four Ghidra callers and four callees.

Ghidra has the correct min/max span but only 103 body addresses. Reconcile the
59 omitted bytes against TASM/raw control flow before source work; do not accept
the sparse body as a complete function solely from Ghidra.
