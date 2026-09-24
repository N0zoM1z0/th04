# OP/MAINE shared polar and vector2_at

## Scope and target evidence

This cohort reconstructs the adjacent `polar` and `VECTOR2_AT` bodies in the
resident `SHARED` contribution of OP.EXE and MAINE.EXE. Target provenance remains
`candidate-local-attested`; these are direct observations from the configured
and hash-checked local targets, not proof of an official pristine release.

| Artifact | Function | Payload extent | Loaded address | Target bytes |
| --- | --- | --- | --- | --- |
| OP | `polar(int,int,int)` | `0xDBB8..0xDBD3` (`0x1C`) | `1DA1:01A8` | `362fa9a65b789e4c171b6cc18578f68939e0089939a418cb804aa451f1c7ea13` |
| OP | `VECTOR2_AT` | `0xDBD4..0xDC15` (`0x42`) | `1DA1:01C4` | `e0fcd9a6d9cb53e21bac38aaeefca8231abbf987671ace75bd5fd480f84aa732` |
| MAINE | `polar(int,int,int)` | `0xCED0..0xCEEB` (`0x1C`) | `1CC7:0260` | `362fa9a65b789e4c171b6cc18578f68939e0089939a418cb804aa451f1c7ea13` |
| MAINE | `VECTOR2_AT` | `0xCEEC..0xCF2D` (`0x42`) | `1CC7:027C` | `f970fa1e1c704b154b603edb922c2bb7c611a260b82544337bfb2c269b788faf` |

The two functions form a contiguous `0x5E`-byte producer in each artifact.
Independent instruction tiling closes `polar` after nine instructions with
`RETF 6`, and `VECTOR2_AT` after 21 instructions with `RETF 0xA`. The producer
follows the already accepted input-wait body and ends immediately before the
accepted PMD resident body. Ghidra inventory and MAP placement support ownership
and layout; neither is treated as an independent semantic oracle.

## Maintained implementation and ABI limit

The maintained implementation is `src/shared/math/vector.cpp`, with declarations
in `polar.hpp` and `vector.hpp`. One natural C++ translation unit produces the
same `TC86` OMF object (`bfdc04576512e7cd3f13613242125c1351048139fc1e8cbaa775fde58dcaefff`)
under the pinned Borland C++ 4.02/TLINK 6.10 profile. No target bytes, copied
instruction sequences, or target-derived inline assembly are used.

`VECTOR2_AT` currently uses an explicitly narrow ABI view: a near reference to
two adjacent 16-bit output coordinates. That view is sufficient for the
observed caller cleanup and exact code generation; it is **not** a recovered
full `SPPoint` declaration or proof of a project-wide vector API. Keep that
unknown open until independent callers/declarations establish it.

## Replay and acceptance

Focused independent A/B source materializations reproduce both complete
functions raw-zero in OP and MAINE. The OP exact-state aggregate receipt is
`.analysis/reconstruction/probes/v570-op-vector-exact-aggregate-001/receipt.json`
(SHA-256
`c68fd2ef401e95ec1135a2577aaa0a5f0a6b05838b6d7296ab8349a713e73c99`): all 24
registered OP slices are raw-zero and all 804 ordered relocations are
preserved. The MAINE exact-state aggregate is
`.analysis/reconstruction/probes/v570-maine-vector-exact-aggregate-002/receipt.json`
(SHA-256
`6539b07824f74d88146dbded2dda2f87b1e127a109e9e376458cbb219a48a22e`): all 24
MAINE slices are raw-zero and all 559 ordered relocations are preserved.

The generated vector object contributes exactly `0x5E` bytes at the expected
`SHARED` MAP positions in each link. Both complete candidate linked images are
unchanged from the retained v489 candidate baselines. Their program extents
remain shorter than the target packed programs, so this is decoded-function
exactness only—not whole OP.EXE or MAINE.EXE exactness, and not a packed-file
offset claim.

Replay command:

```sh
python3 scripts/probes/replay_th04_shared_vector_math.py \
  --output-dir .analysis/reconstruction/probes/v570-vector-math-focused-004
```
