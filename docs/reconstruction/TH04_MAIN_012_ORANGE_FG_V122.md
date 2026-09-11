# TH04 `MAIN_012_TEXT` Orange foreground and adjacent boundary packet (v122)

## Scope and target identity

v122 reconstructs the Orange boss foreground renderer immediately before the
v121 default midboss defeat renderer, then performs a target-first audit of the
preceding Ghidra-missed Kurumi foreground boundary. The active artifact is
`th04-main` / `MAIN.EXE`; the private target remains operator input with
`candidate-local-attested` canonicality and SHA-256
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.
No target bytes were modified, relocated, copied into product source, or used
to patch a candidate.

## Orange boundary and callback ownership

The complete Orange foreground function is `orange_fg_render()` at:

- TLINK `0AAF:6E7B`;
- load-module `0x1196B..0x11A99`;
- Ghidra `2000:196B`, linear `0x2196B..0x21A99`;
- target file `0x1316B..0x13299`;
- size `0x12F` / 303 bytes;
- target slice SHA-256
  `59fd1f99049f3b500797cc5ba03823d62d7be6c1f80664a95eaaa30880ead739`.

Fresh attested Ghidra constructs one contiguous 303-byte near body. Pinned TASM
and raw decoding agree through the terminal `RET` at `0x21A99`, and exact
`midboss_defeat_render()` begins at the next byte. The extent contains seven
ordered target MZ relocation sites at load addresses `0x119B0`, `0x119E7`,
`0x119FA`, `0x11A08`, `0x11A53`, `0x11A65`, and `0x11A8E`.

Ghidra reports no direct caller or xref to the function entry. This is expected
from TH04-local maintained source: `stage1_setup()` assigns
`boss_fg_render_func = orange_fg_render`, and the stage transition later
publishes that function pointer through `boss_fg_render`. The zero direct-xref
observation is therefore not used against authored ownership or the boundary.

## Natural source and compiler feedback

The maintained source is `src/main/boss/orange_fg_render.cpp`. It follows the
same target-proved TC4J source shapes already used by exact Reimu, Elly,
Mugetsu, Gengetsu, and Yuuka foreground renderers:

- SI/DI hold screen-space left/top values;
- `stage_frame_mod8 / 4` and `stage_frame_mod16 / 4` naturally reproduce the
  target signed division sequences;
- damage rendering uses `super_put_1plane()` with the ordinary plane mask;
- the big-explosion path reuses live AX as the top argument;
- the HP-fill effect uses the repository GRCG mode/color helpers and three
  `grcg_circle()` calls;
- GRCG shutdown uses `_DX = 0x7C; _AL = 0; outportb(_DX, _AL)`, not the
  prohibited `_outportb_`/`__emit__` form;
- both explosion update/render helpers remain at the common tail.

The first compilable natural source required no source-shape tuning. Under the
pinned large-model TC4J profile it emits exactly 303 code bytes and the complete
instruction/control-flow stream is target-identical before linking. The only
candidate-versus-target differences are thirty two-byte unresolved link-time
words. Zeroing those diagnostic words makes all 303 bytes identical with
SHA-256
`33579ec5504a2b19192db90c6fd2f8e1876479c40526f6f5eb7bfff18e263489`.
The bounded probe object is valid TC86 Borland C++ OMF. This observation alone
was retained as compiler evidence and did not grant exactness before the cold
link replays below.

The final maintained source contains no inline assembly, `__emit__`,
`#pragma codestring`, target-derived byte arrays, fake return, inert padding,
object patching, or ABI lie.

## Replay integration and focused replay

v122 applies after the v121 transforms. The source transform is fail-closed
over:

- v121-transformed scaffold SHA-256
  `6d8d48624dac2693a32962fee8790f32a72d81260f113da2cb745a0ddcd4c0a9`;
- removed target-derived Orange TASM PROC span SHA-256
  `a4215eb58cf1003e39b2dd66fc0b5e90c7a6b8ec8eaf5bc69ef281a56599684f`;
- patched scaffold SHA-256
  `e37c600ce4aefd698d0979a4d20cb84fec4c10b2461cf0d82b2a7bb5b2b069ce`.

The original uppercase public spelling `@ORANGE_FG_RENDER$QV` is externalized
without changing the ABI, and TC4J publishes the same PUBDEF. The new
`th04/orangefg.cpp` producer is inserted immediately before `th04/mbdrend.cpp`.

Focused two-cold replay:

```text
python3 scripts/replay_th04_main_exact_units.py \
  --unit th04-main-orange-fg-v122 \
  --run-id gptweb-v122-orange-fg-focused-001
```

passes both isolated builds. Each reports all 303 raw bytes exact, map
contribution `0AAF:6E7B 012F ... M=th04/orangefg.cpp`, identical ordered seven-
relocation overlap, valid deterministic TC86 OMF, normalized object SHA-256
`b82b8adef483ad34fc772ae66862c2c2306f7acfaf3bcd968cc637cb9a79e153`,
and candidate MAIN SHA-256
`b57e46b7048fb8daa42865280b5ea844c3e81943433492ef7277337b21f3fb50`.

## Aggregate replay and function review

The required aggregate replay:

```text
python3 scripts/replay_th04_main_exact_units.py \
  --run-id gptweb-v122-orange-fg-aggregate-001
```

passes all 158 default owners twice. Both candidate MAIN executables have
SHA-256
`a1f989b350bd40e8b7b5ece86a6696aec1c0d76093bfd46774f3b650db244bc0`.
No previously accepted owner regresses.

A fresh target-bound function review uses the v122 aggregate map plus a fresh
complete Ghidra metadata block for `0x2196B`. It reports:

- reviewed authored functions: 277;
- exact functions: 275 (99.277978%);
- automatic exact acceptances: 134;
- manual exact acceptances: 141;
- strict provisional rejections: 0;
- reviewed nonexact functions: 2.

The private report SHA-256 is
`13e022165a22603fccdaffb848e4cce1dc5edb3f5d6ff0c9c50c7604124886bc`.
Orange is accepted through the ordinary contiguous-Ghidra/TLINK/exact-owner
gate, not a manual boundary exception.

## Adjacent Kurumi boundary correction

The immediately preceding `kurumi_fg_render()` remains intentionally
**provisional / unreviewed**, but its physical target extent is no longer
unknown:

- TLINK `0AAF:6CA3`;
- load-module `0x11793..0x1196A`;
- target file `0x12F93..0x1316A`;
- size `0x1D8` / 472 bytes;
- target slice SHA-256
  `92fa7b21814e15e6b2ed43a256b764fbab2e4f000079985dc9edbed2664e090d`;
- eight MZ relocation sites inside the extent.

Pinned TASM begins the near PROC at `0x11793`; gap-free raw 16-bit decoding
continues through `RET` at `0x1196A`; exact Orange begins at the next byte.
`stage2_setup()` installs `kurumi_fg_render` through `boss_fg_render_func`.

Fresh Ghidra has no function at the true `0x21793` entry. Its apparent
`switchD_2000:c2fc::caseD_0` function at `0x218B2` is a demonstrable analysis
artifact: `0x218B2` is the displacement byte of the real instruction
`FF 76 FE` beginning at `0x218B0` inside the Kurumi body. That Ghidra-only row
remains excluded, while the true Kurumi row now records the full target-proved
extent. This boundary correction grants no source or exactness credit.

## Current state and continuation

v122 expands the reviewed C/C++ byte denominator by 303 bytes and closes all of
them exactly. The live MAIN total is 41,757 / 41,788 exact (99.925816%). The
reviewed function total is 275 / 277 exact (99.277978%). The only 31 reviewed
nonexact bytes remain the two older blocked functions.

The `shot_velocity_set()` / `sub_11DE6` source-origin seam is unchanged. Fresh
v122 analysis reconfirmed `sub_11DE6` as the complete 44-byte FAR threshold
scanner, and no new falsifiable natural-source hypothesis emerged; the old
ordinary-loop matrix was therefore not repeated.

The first concrete continuation candidate is now the target-proved Kurumi
foreground extent above. Source work should start from its full 0x1D8 raw/TASM
body, six-record spawn-ray traversal, callback installation, eight relocation
sites, and the known Ghidra false-entry pathology rather than trusting the
Ghidra pseudo-function at `0x218B2`.
