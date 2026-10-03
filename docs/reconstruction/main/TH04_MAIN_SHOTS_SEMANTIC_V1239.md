# MAIN shot lifecycle and damage semantics (v1239)

## Scope

This readability batch is limited to `src/main/player/shots.cpp`, the existing
exact `th04-main-shots-main01-v177` owner in `MAIN__TEXT` at file offset
`0x11C2A`, size `0x2E9`. It changes source names, layout and comments. It does
not change structure layout, integer types, expression order, calls, linker
symbols or the owner boundary.

The maintained source now exposes these contracts at their use sites:

- `shots_update()` rebuilds a compact collision cache from live shots. Hit
  animation entries remain in the main pool, advance their flag/cel clock and
  are excluded from collision tests.
- `shots_render()` draws the two-column laser first, traverses the fixed shot
  pool backwards, derives the live-shot animation cel from age parity and
  disables the GRCG after all drawing.
- `shots_hittest()` uses unsigned-subtraction rectangle tests. Each colliding
  shot is slowed, enters its hit animation, and contributes its byte-truncated
  damage divided by the number of hits already seen in that call.
- Bomb damage is added every fourth stage frame. The boss-specific Bomb
  reduction divides the accumulated ordinary-shot and periodic Bomb damage
  before laser damage is added.
- Active lasers are tested on odd stage frames after their stored bottom Y has
  reached the hitbox top. Each option column contributes three damage.
- One byte shared by ordinary-shot and laser hits advances the random-spark
  phase. Ordinary shots emit on odd values; lasers emit every fourth value.
- The returned damage is also added to `score_delta`.

`byte_25980` is therefore used through the local semantic name
`shot_hit_spark_cycle`. The laser renderer is called through the local semantic
name `shot_laser_render`, while both historical linker names remain unchanged.
`byte_259A7` is only observed being cleared by maintained source, so its
address-derived name remains visible behind the deliberately cautious local
alias `shot_reset_unknown`.

## Compiler and complete-product controls

A dependency-validated native build compiled the changed translation unit with
TC86 Borland C++ 4.02. The pre-batch and v1239 shot objects are both 3,737-byte
valid OMF. After dependency timestamp normalization they are byte-identical,
SHA-256:

`13dc7b6901a986c0b04565b493aef7376a5ef994bf167b8b24911753e8f9d37b`

The final source SHA-256 is
`46a3631aa5d055f3da66e8af6d7355df042ec138b2751de588d286e3bed0c9e8`.
The build receipt is
`.analysis/reconstruction/probes/product-20261003-103004-cf1d2236-main/receipt.json`
(SHA-256
`135c09a9c6b17d8f30d5f9a9eb07e16869d77382bca1868a140c234b67a60da5`).

The linked candidate at
`.analysis/build/semantic-shots-readable-v1239-v3/MAIN.EXE` is the same complete
199,455-byte MZ as the preceding semantic source build, SHA-256
`cb4c5b667f9a2d5a5c3ef62865fdc926a74a100155068c63e5dfbd019362b70c`.
Header, program image, overlay and all 1,181 ordered relocations are identical.
The strict comparison is
`.analysis/build/semantic-shots-readable-v1239-v3/compare-vs-cb4c5b66.json`
(SHA-256
`b8ac011e2c99aa11f06a7d8f3ce19b29c65b82d8a278b94c4585100c7cc553ad`).
This is source-to-source preservation of the native product, not a new claim
that the complete product equals the pinned target.

## Historical exact replay boundary

The focused command was:

    python3 scripts/replay_th04_main_exact_units.py \
      --unit th04-main-shots-main01-v177 \
      --run-id gpt-6-1-sol-semantic-shots-v1239

It stopped during dependency compilation because the selected historical
closure staged the current `bullet/add.cpp` without the already verified
semantic bullet header, leaving `ANGLE_PER_SPRITE` and `from_group` undefined.
A second run explicitly selected both owners:

    python3 scripts/replay_th04_main_exact_units.py \
      --unit th04-main-module-th04-bullet-a-cpp-1cc33 \
      --unit th04-main-shots-main01-v177 \
      --run-id gpt-6-1-sol-semantic-shots-v1239-deps

That run passed the earlier compiler boundary but stopped when the historical
point-number dependency assembled `PN_WIDTH` and `PN_DIGITS_LEBCD` twice. It
never linked or compared the v1239 shot extent against the target. The replay
manifests need a dependency-coherent semantic-header and point-number staging
repair before another cold run; neither failure justifies a scaffold allowlist
change. The existing v177 exact evidence remains unchanged, and this batch adds
no exact promotion.
