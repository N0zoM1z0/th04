# TH04 MAIN_033 Orange mode-handler cohort (v131)

## Scope

This packet reviews and naturally reconstructs four contiguous authored near
functions in `MAIN_033_TEXT`. The target artifact is the local Japanese
`MAIN.EXE` identified by SHA-256
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.
Its canonicality remains only `candidate-local-attested`.

The four reviewed functions occupy one contiguous physical producer range:

| Function | Ghidra image | Load offset | File offset | Size | Historical TASM PROC |
| --- | ---: | ---: | ---: | ---: | --- |
| `_orange_phase_random_rings` | `0x29686` | `0x19686` | `0x1AE86` | `0x9A` | `orange_19686` |
| `_orange_phase_aimed_clouds` | `0x29720` | `0x19720` | `0x1AF20` | `0x9B` | `orange_19720` |
| `_orange_phase_ring16` | `0x297BB` | `0x197BB` | `0x1AFBB` | `0x59` | `orange_197BB` |
| `_orange_phase_side_rings` | `0x29814` | `0x19814` | `0x1B014` | `0x64` | `orange_19814` |

Together they span load `0x19686..0x19877`, file `0x1AE86..0x1B077`,
`0x1F2 / 498` bytes. The next pinned TASM PROC starts at load `0x19878`.
The complete target cohort SHA-256 is
`6b7044a4c532c36e54fec2ed68e324b6389234d4013ef81ba309f92796b2adee`.

## Boundary and dispatcher evidence

Fresh attested Ghidra observations report all four functions as
`__cdecl16near`, parameterless, non-thunk, non-external functions. Their body
coverage is complete and contiguous: 154/154, 155/155, 89/89, and 100/100
bytes respectively. Ghidra reports zero direct callers for these entries, but
that is a target-analysis blind spot rather than ownership evidence.

The target-derived `MAIN_033_TEXT` residual contains a central `boss.mode`
dispatcher with exactly one direct `CALL` to each historical PROC. Pinned TASM,
raw 16-bit decoding, and the next-PROC seam agree with the four Ghidra extents.
There are no gaps, alignment bytes, shared tails, or post-return data inside the
498-byte cohort.

The target has five MZ relocations overlapping the cohort, at load offsets
`0x19710`, `0x19747`, `0x197A3`, `0x19804`, and `0x19868`. Exact reconstruction
therefore requires ordered relocation equality in addition to raw instruction
shape.

## Natural-source reconstruction

The maintained source is `src/main/boss/orange_mode_phases.cpp`, SHA-256
`ec815bd3f883a2989e032780c361d536077e94315839bde117a2a97ddd50acab`.
It is ordinary Turbo C++ source with four independent near public functions and
no inline assembly, target-derived byte arrays, `#pragma codestring`, fake
returns, inert padding, or target patching.

The first natural probe compiled successfully but emitted 483 code bytes. A
linked disassembly comparison isolated two source-shape differences rather than
an ABI or boundary failure:

- `bullet_template.origin = boss.pos.cur` made TC4J use a 32-bit `MOV EAX`
  structure copy. The target uses separate natural 16-bit assignments to the
  X and Y fields. Writing those fields explicitly restores four bytes in each
  affected function.
- The aimed-cloud handler initially stored `iatan2()` directly into
  `bullet_template.angle`. The target first stores that result in `boss.angle`
  and later derives `bullet_template.angle = boss.angle - 0x20`. Preserving
  that data flow restores the remaining three bytes in that function.

After those natural-source corrections, TC4J emits exactly 498
`MAIN_033_TEXT` bytes with public offsets `0`, `0x9A`, `0x135`, and `0x18E`.
A bounded diagnostic TLINK, explicitly carrying zero exactness credit, placed
that producer at `13A9:5BF6` size `0x1F2`, restored the residual start to
`13A9:5DE8`, reproduced all 498 target bytes, and matched all five overlapping
relocations. That diagnostic result was used only to justify entering formal
replay.

## Formal exact replay

Focused two-cold replay actually ran and passed:

`python3 scripts/replay_th04_main_exact_units.py --unit th04-main-orange-mode-phases-v131 --run-id gptweb-v131-orange-mode-phases-focused-001`

Receipt:
`.analysis/reconstruction/exact-unit-replay/gptweb-v131-orange-mode-phases-focused-001/receipt.json`.

Both isolated builds report exact raw bytes, exact map placement, and exact
ordered relocation overlap for the 498-byte owner. Both place
`th04/orangeph.cpp` at `13A9:5BF6` size `0x1F2`. The candidate slice SHA-256 is
`6b7044a4c532c36e54fec2ed68e324b6389234d4013ef81ba309f92796b2adee`.
The formal TC86 object is identical across A/B: raw SHA-256
`d170bd22763d412499ff2612cb66b4a352c054d9fe0d57a9e5e8283daa343cda`
and dependency-timestamp-normalized SHA-256
`ee44c794d03b1cc77f8e1f239f2703bdacd83fb80320791696ab2fc69a8eed2c`.
Focused candidate MAIN identity is deterministic at
`049ffca8b362f9a27a5a1c739ea8f8b6066b55690893b336585c659ad2249e48`.

The required default aggregate then actually ran and passed:

`python3 scripts/replay_th04_main_exact_units.py --run-id gptweb-v131-orange-mode-phases-aggregate-001`

Receipt:
`.analysis/reconstruction/exact-unit-replay/gptweb-v131-orange-mode-phases-aggregate-001/receipt.json`.

All 167 default owners pass together twice. The Orange cohort retains the same
498-byte slice, map extent, object identity, and ordered relocation sequence;
no previously exact owner regresses. Aggregate candidate MAIN identity is
identical across A/B at
`b75b810982f384bdd2cfca76d64e8401e818712facaa3c6c9f3e705374e83b6a`.

## Function-review gate

The current target-bound function-review input adds fresh Ghidra observations
for all four entries to the retained reviewed metadata set and uses the v131
167-owner aggregate map. The reviewer passes at **294/296 reviewed authored
functions exact (99.324324%)**, with 148 automatic acceptances, 146 manual
acceptances, and zero strict rejections.

All four functions are ordinary automatic exact functions because their fresh
Ghidra bodies are complete and contiguous. The four `[[new_exact]]` policy
entries only authorize adding previously unreviewed functions to the reviewed
ledger; they are not manual boundary overrides.

## Scope limits and continuation

The repository exact-unit Oracle proves this reviewed physical owner and its
four function extents. After committing the exact claim at
`e818be5ad0bcfd81dd35db08d619f9448d75eeae`, Factory Truth-Kernel replay job
`job:f977704d7e344484910a95498cd1bd1c` independently replayed the imported
`owned_extent_exact` claim under `isolated-double-build`. Factory receipt
`receipt:2d71f9eb7dcc6c2120e58ff30549417ce715daa0fb3978a29b2d802e6ee710c7`
returned `receipt_verdict=pass` and `acceptance_decision=accepted`, with registry
`registry:5dfdbfbb97c92c5f553d5032ab463da6181219a52196931522dcecb52b950088`.
This Factory acceptance is scoped to that exact-owner claim. It does not
establish a standalone TH04 product build, original runtime-storage identity,
or runtime-scenario validation.

The first connected continuation candidate is the next pinned PROC at load
`0x19878` / Ghidra image `0x29878`. Its extent, dispatcher role, callers,
callees, data/tail ownership, relocations, and natural source form must be
re-established from current target evidence before reconstruction credit.
