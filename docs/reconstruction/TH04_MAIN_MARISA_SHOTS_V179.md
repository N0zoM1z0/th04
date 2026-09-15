# TH04 MAIN Marisa shot reconstruction (v179)

## Scope

This packet reviews and naturally reconstructs the complete `MAIN_TEXT` Marisa
shot producer in the attested local `th04-main / MAIN.EXE` target. The private
target remains ignored operator input with `candidate-local-attested`
canonicality. It is never modified, patched, relocated, staged, or published.

The physical owner is `MAIN_TEXT 0AAF:2F5F..37D2`, load
`0xDA4F..0xE2C2`, file `0xF24F..0xFAC2`, size `0x874 / 2164`. Target and
accepted natural-source slice SHA-256 are both:

`41961528c20d7d12d43494e173984672032ab069b0e64bf2fd21211ab2f8d341`

The next independently exact producer, `th04/tlr.cpp`, begins at
`MAIN_TEXT 0AAF:37D3` / load `0xE2C3`.

## Authored-boundary review

Target-first raw decoding, pinned TASM, TLINK MAP ownership, relocation review,
and provisional attested Ghidra observations close twenty logical functions in
the owner. Ghidra is not authoritative for these boundaries: it undercounted
`shot_marisa_b_l6()` and did not create entries for the following late-shot
functions.

| Function | Load start | Logical body | Physical span |
| --- | ---: | ---: | ---: |
| `shot_marisa_l0()` | `0xDA4F` | `0x24` | `0x24` |
| `shot_marisa_l1()` | `0xDA73` | `0x33` | `0x33` |
| `shot_laser_update(unsigned int, shot_laser_style_t)` | `0xDAA6` | `0xA4` | `0xA4` |
| `shot_marisa_a_l2()` | `0xDB4A` | `0x3E` | `0x3E` |
| `shot_marisa_a_l3()` | `0xDB88` | `0x46` | `0x46` |
| `shot_marisa_a_l4()` | `0xDBCE` | `0x46` | `0x46` |
| `shot_marisa_a_l5()` | `0xDC14` | `0x4C` | `0x4C` |
| `shot_marisa_a_l6()` | `0xDC60` | `0x4D` | `0x4D` |
| `shot_marisa_a_l7()` | `0xDCAD` | `0x4D` | `0x4D` |
| `shot_marisa_a_l8()` | `0xDCFA` | `0x4D` | `0x4D` |
| `shot_marisa_a_l9()` | `0xDD47` | `0x4D` | `0x4D` |
| `shot_marisa_b_l2()` | `0xDD94` | `0x63` | `0x63` |
| `shot_marisa_b_l3()` | `0xDDF7` | `0x65` | `0x65` |
| `shot_marisa_b_l4()` | `0xDE5C` | `0x7A` | `0x7A` |
| `shot_marisa_b_l5()` | `0xDED6` | `0x80` | `0x80` |
| `shot_marisa_b_l6()` | `0xDF56` | `0x8B` | `0x94` |
| `shot_marisa_b_l7()` | `0xDFEA` | `0x8B` | `0x94` |
| `shot_marisa_b_l8()` | `0xE07E` | `0xA9` | `0xB2` |
| `shot_marisa_b_l9()` | `0xE130` | `0xB7` | `0xC4` |
| `sub_E1F4()` | `0xE1F4` | `0xC4` | `0xCF` |

The final five functions own compiler-generated post-`RET` switch metadata.
Their trailing bytes are part of the physical TC4J producer and exact-byte
accounting, but not part of the executable logical function bodies.

The same boundary pass also corrects the independent `CIRCLE_TEXT`
`SHOT_LASER_PUT_RAW` observation. Pinned `th04/main/player/shot_laser.asm`
contains a real `PROC near`; target raw closes the routine at load
`0xBE68..0xBECA`, size `0x63`. The following `NOP` at `0xBECB` is residual
layout before the next callback. This independent assembly routine receives no
Marisa C++ exactness credit and its source-origin classification remains open.

## Natural source

Maintained source is `src/main/player/marisa_shot.cpp`, SHA-256:

`9b42810185e050cc2c125c6014efa98c96446921db63970ce0d37a584912b79b`

The accepted source uses ordinary maintainable C++ plus the legitimate TC4J
`#pragma option -a` switch-table alignment control. It does not use inline
assembly, `__emit__`, target-derived byte arrays, `#pragma codestring`, fake
returns, inert padding, target patching, or ABI lies.

Three source-shape details were necessary and are semantically natural:

1. `shot_marisa_a_l5()` through `shot_marisa_a_l9()` declare the local angle
   before `shot_laser_update()` but assign it after the call, matching the target
   local-store lifetime and instruction order.
2. The `SLS_4`, `SLS_6`, and `SLS_1_4_1` paths in `sub_E1F4()` use ascending
   threshold ladders. TC4J then naturally emits the target `JA next; JMP celN`
   double-branch forms instead of optimizing them into inverse single branches.
3. The `SLS_8` path uses semantic shared labels so TC4J lays out the common CEL
   blocks in target order `CEL0 -> CEL1 -> CEL2 -> CEL4`; `SLS_2` falls through
   to `CEL0` as in the target control flow.

The ABI probe for `SHOT_LASER_PUT_RAW` independently shows that
`extern "C" void pascal near SHOT_LASER_PUT_RAW(void)` preserves the observed
AX/DX/BX/SI register contract and exact OMF external name. An `__fastcall`
variant produces the wrong decorated name and is rejected.

## Useful negative evidence

The recovered v179 worktree entered with a deterministic but nonexact natural
candidate. Focused run `gptweb-v179-marisa-shots-focused-negative-002` emitted
`0x867` bytes instead of target `0x874`; it preserved the owner start and ordered
relocations but shifted the next producer by 13 bytes. That receipt remains
retained as negative evidence.

Bounded compiler/link probes then isolated the deficit rather than padding it:

- five missing bytes were compiler-owned zero metadata before dense switch
  tables; legitimate `#pragma option -a` restores all five;
- the remaining eight-byte deficit was four optimized-away short jumps in
  `sub_E1F4()`;
- whole-function `#pragma option -O-` was rejected because it over-expanded and
  changed unrelated control flow;
- function-internal `#pragma option -O-/-O` was accepted by TC4J but had no
  useful effect on the function-level optimization decision;
- an all-threshold early-exit ladder came within one byte but emitted an extra
  SLS_8 jump;
- a hybrid threshold/fallthrough shape reached exact size but still had 42 raw
  branch-target mismatches;
- the final natural hybrid (`probe017`) reproduced the complete `0x874` linked
  owner byte-for-byte before authoritative cold replay.

These probes are bounded ignored analysis artifacts. None is exactness evidence
by itself; exactness comes from the configured cold replay gates below.

## Exact replay

Focused authoritative run:

`python3 scripts/replay_th04_main_exact_units.py --unit th04-main-marisa-shots-v179 --run-id gptweb-v179-marisa-shots-focused-exact-003`

passes two isolated serial cold builds with `failures=[]`. v179 reports
`raw=True`, `map=True`, `relocs=True`, `size=2164`, and target slice SHA-256
`41961528c20d7d12d43494e173984672032ab069b0e64bf2fd21211ab2f8d341`.
Receipt SHA-256:

`10790bd1bc37dd735302ff94f3f5b864eb5085f38f6e3579d9d9a892dff27271`

Candidate-state aggregate before ledger promotion:

`python3 scripts/replay_th04_main_exact_units.py --run-id gptweb-v179-marisa-shots-aggregate-candidate-001`

passes the complete default cohort twice with `failures=[]`; v179 remains raw,
MAP, and ordered-relocation exact. Receipt SHA-256:

`c4dda384b9f435f738387162067855884eaec479c9d750fad2748e875f106206`

Post-promotion aggregate:

`python3 scripts/replay_th04_main_exact_units.py --run-id gptweb-v179-marisa-shots-aggregate-final-001`

again passes the complete default cohort twice with `failures=[]`; v179 remains
raw/MAP/ordered-relocation exact. Receipt SHA-256:

`e51840bf0a437d646f4f9b8a04d9b51c8ad12db83e2b9097dcb39d06061989ac`

Both final aggregate builds produce candidate `MAIN.EXE` SHA-256
`6685687e0f7554e4f84395e71cabac1f2e3babccaa76abaa86877846108145a4`
and identical `mshot.obj` SHA-256
`4f83fa08287a037bffb60de082444002457d3fb53e7eb0ed436499073cb83999`.
The candidate whole image is not claimed identical to the target; owned-extent
Oracle equality is the acceptance plane.

## Accounting and verification planes

After v179 promotion the non-overlapping reviewed MAIN ledger reports:

- `74,881 / 78,475` exact reviewed authored bytes (`95.420198%`);
- `450 / 464` exact reviewed authored functions (`96.982759%`);
- 14 reviewed blocked MAIN functions;
- 73 unreviewed MAIN authored candidates;
- 31 original-style ASM attestation observations.

`docs/PROGRESS.md` intentionally reports a more conservative generated mapping
percentage and therefore has a different denominator. Neither percentage is a
claim about all of `MAIN.EXE` or the game.

Owned-extent/function exactness is PASS for the v179 physical owner and all
20 reviewed logical functions, and post-promotion aggregate replay is PASS.
Standalone TH04 production compile/link closure is not established. Runtime
storage identity is not established. No runtime scenario was executed.
Portable-runtime validation is not established. No v179 Factory Truth-Kernel
acceptance claim is submitted or claimed. Independent pristine-release
provenance remains open.

Other TH04 artifacts remain independent active queues and receive no v179 MAIN
credit: OP has 94 unreviewed authored candidates, MAINE has 72, and ZUN has 13.
`ZUN.COM` continues to be treated as an MZ executable despite its extension.

## Continuation

The strongest next source-present structural blocker is
`th04-main-items-update-v154`: one `0x546` `MAIN_035_TEXT` producer containing
six reviewed functions. Focused replay is already exact in MAP placement, all
15 ordered MZ relocations, deterministic OMF, and the first five function slices.
Only four raw bytes remain different, both inside `items_update()`:

- load `0x1DF1F`: target `29 C3`, candidate `2B D8` (`SUB BX,AX`);
- load `0x1DF2F`: target `29 D3`, candidate `2B DA` (`SUB BX,DX`).

Previous direct-expression, alternate-local, compound-assignment, and original
PC-98 IDE probes all retained the alternate equivalent encodings or changed the
surrounding allocation. The next session should begin from this bounded negative
evidence and test a genuinely new source/compiler lifetime hypothesis rather than
another spelling matrix. Boundary auditing should continue in parallel; no tool
inventory is assumed complete.
