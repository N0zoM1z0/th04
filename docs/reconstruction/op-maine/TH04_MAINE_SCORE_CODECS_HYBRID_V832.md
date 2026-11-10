# TH04 MAINE SCORE codec artifact-local hybrid closure (v832)

## Result

v832 promotes MAINE `scoredat_decode()` at payload `0xC149` (88 bytes) and
`scoredat_encode()` at payload `0xC1A1` (101 bytes) to decoded-exact.

MAINE advances from **66/72 to 68/72**, leaving four reviewed authored blockers.

This is artifact-local decoded-function exactness. OP v821 contributes only the
independent provenance for the single-byte ROR primitive; MAINE receives exact
credit from its own cold compile/link and raw-byte checks.

## Maintained source policy

Maintained source keeps all codec control/data flow in C++:

- checksum accumulation;
- key generation and XOR;
- loop bounds and record layout;
- byte loads/stores and return behavior.

Only one primitive remains symbolic:

```cpp
asm { ror feedback, 3; }
```

TC4.02 has no 8-bit rotate intrinsic that emits the required byte ROR. TH03
OP/MAINL release targets independently bind this primitive to historical SCORE
codec code, as established by v821 and re-attested by the v832 driver.

No `__emit__`, codestring, target-byte array, object patch, or post-link patch is
used.

## Artifact-local focused replay

Checked-in driver:

```sh
python3 scripts/probes/replay_th04_maine_score_codecs_hybrid_v832.py \
  --output-dir .analysis/reconstruction/probes/v832-maine-score-codecs-focused-001
```

Two isolated TC4.02/TLINK MAINE rounds reproduce:

- complete `0xB30` `SCORE_TEXT` object CODE SHA-256
  `d8180ee4acb342cefe168337bb6dff4986b6bac625a4c614128c1b9430cec693`;
- all **203 ordered OMF fixup operands**;
- complete 88-byte decode body raw-zero;
- complete 101-byte encode body raw-zero;
- retained MAINE EXE/MAP identity;
- all **559 ordered MZ relocations**.

SHA-256:

`fc753dc4e4dd6f00588968a9c59c42a8caed42db1cfb53954d61020787609341`

The individual maintained-source harnesses also cold-replay each codec
standalone and inside grouped SCORE_TEXT. v832 fixes a latent exact-path harness
bug by preserving the historical grouped function signature/include context;
other ScoreFunction users keep the previous default behavior.

## Canonical acceptance

Canonical replay checks **68 unique current MAINE accepted function slices**,
all with `raw_difference_count = 0`.
SHA-256:

`b468c5305eebbd2378d86a876cabfc999b0eb12e1133f41f51cf6ba21bbdbcf5`

## Scope and remaining frontier

v832 grants exactness only to the two codec functions. The rest of the
`scoreall.cpp` producer is replay scaffold unless separately accepted.

The four remaining MAINE authored blockers are:

- `regist_menu()` (924 bytes);
- `box_1_to_0_masked(box_mask_t)` (134 bytes);
- cutscene `egc_start_copy()` (52 bytes);
- SCORE `_egc_start_copy_inlined` (67 bytes).

Packed-file ownership and whole-`MAINE.EXE` exactness remain separate claims.
