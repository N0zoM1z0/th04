# TH04 MAIN bomb cohort reconstruction (v178)

## Scope

This packet reviews and naturally reconstructs the complete `MAIN__TEXT` bomb
window immediately before the exact v177 shot producer in the attested local
`th04-main / MAIN.EXE` target. The private target remains ignored operator input
with `candidate-local-attested` canonicality. It is never modified, patched,
relocated, staged, or published.

The packet covers load `0xFF34..0x10429`, file `0x11734..0x11C29`, a contiguous
`0x4F6 / 1270` authored-byte window. Exact v177 `shots_reset()` begins at the
next byte, load `0x1042A`.

## Boundary corrections

Target-first raw decoding, pinned TASM boundaries, TLINK publics, and exact cold
replay close nine logical functions:

| Function | Load range | Size | Target terminal |
| --- | --- | ---: | --- |
| `bb_playchar_load()` | `0xFF34..0xFF88` | `0x55` | `RET` |
| `bb_playchar_free()` | `0xFF89..0xFFA3` | `0x1B` | `RET` |
| `bomb_reset()` (target `sub_FFA4`) | `0xFFA4..0xFFB3` | `0x10` | `RET` |
| `player_bomb()` | `0xFFB4..0x10029` | `0x76` | `RET` |
| `bb_playchar_put(int)` | `0x1002A..0x1004C` | `0x23` | `RET 2` |
| `bomb_reimu()` | `0x1004D..0x10112` | `0xC6` | `RET` |
| `bomb_marisa()` | `0x10113..0x10209` | `0xF7` | `RET` |
| `bomb_update_and_render()` | `0x1020A..0x1030C` | `0x103` | `RET` |
| `bomb_stars_update_and_render_for(int)` | `0x1030D..0x10429` | `0x11D` | `RET 2` |

This is a material denominator correction, not merely a source rewrite. The
prior Ghidra/ledger body sizes materially undercounted five functions:

- `PLAYER_BOMB`: `0x4D` body bytes versus complete `0x76` body span;
- `BB_PLAYCHAR_PUT`: `0x03` versus complete `0x23`;
- `BOMB_REIMU`: `0x04` versus complete `0xC6`;
- `BOMB_MARISA`: `0x01` versus complete `0xF7`;
- `bomb_update_and_render()`: `0x3C` body bytes versus complete `0x103` span.

The complete raw control flow tiles the entire `0x4F6` window with no gap or
post-return data between these entries. `bomb_update_and_render()` contains two
genuine shared source tails. Natural C++ expresses them with semantic labels and
`goto`, rather than manufacturing padding or copied target bytes.

## Physical producer split

The logical functions are owned by two physical TC86 C++ producers.

The bomb core is `MAIN__TEXT 0AAF:5444..581C`, load `0xFF34..0x1030C`, size
`0x3D9 / 985`, target/candidate SHA-256:

`354fe2369fbbb605d8b1e7deea259afd64470f1d15927e8a66c6c4c0b220f640`

Its target ordered MZ relocation overlap is:

`[0x102ED, 0x1029A, 0x10256, 0x101F2, 0x10134, 0x100FC, 0x100E8,
0x100BF, 0x1006D, 0x10019, 0xFF9A, 0xFF85, 0xFF77, 0xFF72, 0xFF63,
0xFF5B]`.

The bomb-star renderer is independent `MAIN__TEXT 0AAF:581D..5939`, load
`0x1030D..0x10429`, size `0x11D / 285`, target/candidate SHA-256:

`7a97e3330f4d74739ba44c8e108f4dc2ef1b0d9187c595f370e68d79c1fc0664`

Its ordered MZ relocation overlap is `[0x103A4]`. The next byte begins the exact
v177 shot producer.

Replay removes this final target-derived code window from the residual
`m1rsuf.asm`. The residual object is required to be zero-code; it remains in the
link order only for its surviving non-code ownership. Natural `bomb.cpp` and
`bstar.cpp` are inserted before the exact v177 shot objects.

## Natural source

Maintained source is:

- `src/main/player/bomb.cpp`, SHA-256
  `1fb6a50345f6e7ee59a92a1d4a74d7bd59dce95c0ed850aa7d0d6a0f5821b30f`;
- `src/main/player/bomb_stars.cpp`, SHA-256
  `ab54122307da94f8f3d2e3ea1085b2989e88183b1001dce75d8435e6b273f9ce`.

Production-profile TC86 Borland C++ 4.02 compiler probes independently emitted
exact code contribution lengths of `0x3D9` and `0x11D` before replay integration.
The probes recovered ordinary source-language shapes for far filename pointers,
HMem segment storage, deathbomb state, BB rendering, Reimu/Marisa effects,
shared palette tails, bomb-star vector updates, and Pascal argument cleanup.

The core legitimately uses the repository-established `#pragma samecodeseg`
mechanism for `hud_bombs_put` and `circles_add_growing`. This does not change the
source ABI or inject bytes. It changes the TC4J OMF Pointer16 FIXUPP frame so
TLINK 6.10 can perform its historical same-segment FAR-call optimization,
producing the target `NOP; PUSH CS; CALL near` sequence without a segment
relocation.

No maintained source uses inline assembly, `__emit__`, target-derived byte
arrays, `#pragma codestring`, fake returns, inert padding, copied target bytes,
object/target patching, or ABI lies.

## Useful negative evidence

Focused candidate006 had correct source length, MAP placement, deterministic OMF,
and all target relocation sites, but four additional segment relocations at load
`0xFFF8`, `0x100CC`, `0x100F5`, and `0x101EB`. They correspond to
`hud_bombs_put()` and three `circles_add_growing()` calls. Reusing the already
accepted repository `samecodeseg` mechanism removed those four relocations and
made ordered relocation comparison exact.

Candidate007 then had exact MAP, exact ordered relocations, deterministic OMF,
and only four raw-byte differences. Both differences were packed coordinate
arguments to `cdg_put_noalpha_8()` in the Reimu/Marisa paths: source `(56, 32, 0)`
encoded the opposite coordinate order from target `(32, 56, 0)`. Correcting the
natural arguments closed focused candidate008.

Bounded copies of the candidate006/007 receipts and corresponding source snapshots
are retained under `.analysis/gpt-web/th04-main-20260915-v178/`. Their large cold
build trees were removed only after tracked references were redirected to the
bounded copies and no producer remained active.

## Exact replay

All authoritative exact runs bind replay manifest SHA-256:

`f37c1c68d8c7b2c522805502f2b50a5d14524aabbd23618f6035cbc0df7ff0a6`.

Focused run `gptweb-v178-bomb-focused-candidate-008` selects a 134-owner
dependency closure and passes two isolated cold builds with `failures=[]`.
Receipt SHA-256:

`371435f7865801cfafec3294f973ed0c15a676eaed30194cd71b76504f663eb3`.

Both v178 owners are raw exact, MAP exact, ordered-relocation exact, and emit
valid deterministic TC86 OMF. The residual `m1rsuf.obj` zero-code gate also
passes.

Candidate-state aggregate `gptweb-v178-bomb-aggregate-candidate-001` passes all
213 selected default owners twice before ledger promotion with `failures=[]`.
Receipt SHA-256:

`8fe16889154b29dd4242d3581b1be67f4f3ab4ecacdc8415827fa7a972d371e1`.

Post-promotion aggregate `gptweb-v178-bomb-aggregate-final-001` passes all 213
default owners twice from the promoted ledger state with `failures=[]`. Receipt
SHA-256:

`ba4cd9ad30bbe47f7ff20d24d604475894c7965445ca960e6666d5105fe4d301`.

## Accounting and verification planes

After v178 promotion the non-overlapping reviewed MAIN ledger reports:

- `72,717 / 76,311` exact reviewed authored bytes (`95.290325%`);
- `430 / 444` exact reviewed authored functions (`96.846847%`);
- 14 reviewed blocked MAIN functions;
- 93 unreviewed MAIN authored candidates;
- 31 original-style ASM attestation observations.

The v178 denominator increases by the complete `0x4F6 / 1270` bomb window and
nine logical functions. These percentages refer only to the reviewed authored
ledger, not to `MAIN.EXE` or TH04 as a product.

Repository-native owned-extent/function exactness passes for both v178 physical
owners, all nine logical functions, and the complete post-promotion 213-owner
cohort. Standalone TH04 production compile/link closure is not established.
Whole-image exactness is not established. Runtime-storage identity is not
established. No runtime scenario was executed. Portable-runtime validation is not
established. No v178 Factory Truth-Kernel acceptance claim is submitted or
claimed. Independent pristine-release provenance remains open.

Other TH04 executables remain independent active queues and receive no v178 MAIN
credit: OP has 94 unreviewed authored candidates, MAINE has 72, and ZUN has 13.
None currently has an honest accepted exact-byte/function denominator. `ZUN.COM`
continues to be treated as an MZ executable despite its extension.

## Continuation

The next structural boundary packet should examine the Marisa B late-shot cohort
rather than an unrelated leaf. The live ledger currently has provisional
`shot_marisa_b_l6` at load `0xDF56` with `body_size=0x71` and `body_span=0x8B`,
followed by zero-body provisional `shot_marisa_b_l7`, `shot_marisa_b_l8`,
`shot_marisa_b_l9`, and `sub_E1F4` entries. This is a strong Ghidra
body-construction / missing-entry signal.

Start target-first: reconcile the true l6/l7/l8/l9/sub_E1F4 extents, direct
callers, shared tails or internal entries, physical producer boundaries, and
ordered relocations before writing or fusing source.
