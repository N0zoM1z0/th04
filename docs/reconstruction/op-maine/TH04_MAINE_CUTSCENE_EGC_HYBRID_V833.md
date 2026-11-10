# TH04 MAINE cutscene EGC artifact-local hybrid closure (v833)

> **Status:** Historical checkpoint. v833 raised MAINE to 70/72; v834 closes the SCORE EGC helper and v835 closes `regist_menu()`, bringing current MAINE to 72/72.

## Result

v833 promotes two MAINE CUTSCENE_TEXT functions:

- `egc_start_copy()` at payload `0xA2D6`, 52 bytes;
- `box_1_to_0_masked(box_mask_t)` at payload `0xA78F`, 134 bytes.

MAINE advances from **68/72 to 70/72**, leaving only `regist_menu()` and the
SCORE `_egc_start_copy_inlined` helper blocked.

## Cross-game hardware primitive

The target six-register EGC setup core is the complete 42-byte sequence:

`AX=value -> DX=port -> OUT DX,AX` repeated for ports `4A0h`, `4A2h`, `4A4h`,
`4A8h`, `4ACh`, and `4AEh`, including `MOV AX,0` at the address register.

Registered release targets independently preserve this complete core in:

- TH02 MAINE `egc_start_copy()`;
- TH03 MAINL `egc_start_copy()`;
- TH04 MAIN / MAINE EGC copy helpers;
- TH05 MAIN `egc_start_copy_noframe()`;
- TH05 MAINE `egc_start_copy()`.

The common 42-byte SHA-256 is
`e3e761f7f926d17f1265e9dc32d665131a3ca4ae47fd415290d6f6e8db41cfb0`.

This corroborates the machine mechanism, not literal original-source spelling.

## Maintained source policy

`src/maine/cutscene/egc_start_copy.inl` expresses the six word-register writes
with source-level AX/DX register semantics. Only the zero write needs an
explicit `asm { mov ax, 0; }` to prevent TC4.02 from selecting XOR AX,AX.

`src/maine/cutscene/box_1_to_0_masked.inl` keeps its loop, mask selection, VRAM
addressing, page switching, and copy body in C++; only the first three fixed
EGC word writes use the same cross-game AX-before-DX primitive.

The maintained fragments contain no `__emit__`, `outport2`, `keep_0`,
`optimization_barrier`, codestring, target-byte array, object patch, or
post-link patch.

## Focused replay

Checked-in driver:

```sh
python3 scripts/probes/replay_th04_maine_cutscene_egc_hybrid_v833.py \
  --output-dir .analysis/reconstruction/probes/v833-maine-cutscene-egc-focused-002
```

Two isolated TC4.02/TLINK MAINE rounds reproduce:

- complete `0xC3E` CUTSCENE_TEXT CODE;
- all 214 ordered OMF fixups;
- both reviewed function bodies raw-zero;
- retained MAINE EXE/MAP identity;
- all 559 ordered MZ relocations.

SHA-256:
`c9caccae1a5ab038796bbf42b8bd55e5cebcaae3270def2a0ede05560ab3965a`

## Canonical acceptance

Canonical replay checks **70 unique current MAINE accepted slices**, all with
`raw_difference_count = 0`.

SHA-256:
`f182faddf025dfee948ffde86c9c742715182127de4ae06401c1e37c6458e6b9`

## Remaining frontier

Only two authored blockers remain in MAINE:

- `regist_menu()` (924 bytes), bounded by v831 to one CFG-preservation issue;
- SCORE `_egc_start_copy_inlined` (67 bytes), whose ordinary source remains
  one byte short because TC4.02 selects XOR AX,AX instead of target MOV AX,0.

Packed-file ownership and whole-`MAINE.EXE` exactness remain separate claims.
