# Semantic bullet generation contracts

This semantic-readability batch clarifies MAIN's bullet-group generation
without changing its DOS product bytes or its accepted historical owner. The
pinned MAIN target passes identity, MZ and Ghidra database attestation; its
canonicality remains `candidate-local-attested`.

## Source contract

`bullet_angle_t` records the actual one-byte storage contract. One clockwise
turn contains 256 units: `00h` points right, `40h` down, `80h` left and `C0h`
up. Intermediate arithmetic remains 16-bit. Assignment to `bullet_angle_t`
performs the original wrap at `100h`.

`bullet_velocity_and_angle_set()` now names its stages in execution order:

1. compute the member's relative spread, ring, stack or random offset;
2. add player aim for aimed groups;
3. add the template rotation;
4. derive velocity and retain the final absolute spawn angle.

The spread accumulator, final spawn angle and fixed-speed selector are
synchronous per-group scratch state. They remain globals because the original
near-call ABI owns them across helper calls, but no value becomes persistent
bullet entity state. `bullet_t::spawn_group` records the source group as one
byte even though `bullet_group_t` is compiler-sized. Directional sprite cels
repeat after an unsigned half turn because opposite travel directions share
the same unoriented sprite axis.

The ASM-visible scratch names remain their historical symbols. The C++ source
uses semantic aliases so isolated exact-owner replay can link against the
pinned surrounding objects. This separates source vocabulary from a 16-bit
link contract that the portable backend does not need to inherit.

## TC4J signedness counterexample

An initial named half-turn constant was spelled `0x80` in the sprite modulo.
That changed the original unsigned expression `% 0x80u` into signed modulo.
At native MAP address `156A:996F`, TC4J emitted an additional signed division
by 128 before the existing division by 8. `BULLET_A_TEXT` grew from `0870h` to
`0875h`, and the complete native MAIN changed from SHA-256 `cb4c5b66...` to
`bf1288b5...`.

`BULLET_DIRECTION_SPRITE_ANGLE_PERIOD` is therefore explicitly `0x80u`.
After this correction, TC4J again emits the original direct division by 8.
The rejected comparison is
`.analysis/semantic-bullet-v1236-compare.json`. It is a compiler observation
about this expression, rather than a general rule that named constants are
unsafe.

## Validation

The final dependency-validated MAIN build is 199,455 bytes with SHA-256
`cb4c5b667f9a2d5a5c3ef62865fdc926a74a100155068c63e5dfbd019362b70c`.
It is raw-identical to the preceding native build over the complete MZ file.
The final receipt is
`.analysis/reconstruction/probes/product-20261003-091336-fdcadeb4-main/receipt.json`.
This is source-to-source preservation and does not claim complete target
equality.

The bullet-header probe compiles equivalent historical and semantic
identifier spellings with pinned TC4J. After COMENT/dependency records are
excluded, both objects have semantic OMF SHA-256
`9ed2b36bcdd5ce19767e7f90c6230a81e03fc3f295d4ceeb3e384f3c3c1ca9d8`.
Receipt:
`.analysis/reconstruction/probes/semantic-bullet-v1236-header-v2/receipt.json`.

Finally, two isolated cold builds replay the already accepted
`th04-main-module-th04-bullet-a-cpp-1cc33` owner. Both reproduce its complete
2,139-byte target extent, exact MAP contribution and overlapping relocation.
The target and candidate slice SHA-256 is
`f7dfaeae5b18749d6687a94139488a825f86f00b85a4eb4072985223a5f1cc5e`.
Receipt:
`.analysis/reconstruction/exact-unit-replay/20261003T091153Z-52f9889b/receipt.json`.
No ledger state is promoted by this replay.
