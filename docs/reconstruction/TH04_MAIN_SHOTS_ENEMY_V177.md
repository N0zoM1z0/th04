# TH04 MAIN shot / enemy renderer recovery (v177)

## Scope and recovery

This packet reconstructs the contiguous `MAIN__TEXT` shot tail and the adjacent
enemy renderer in the attested local `th04-main / MAIN.EXE` target. The private
target remains ignored operator input with `candidate-local-attested`
canonicality; it is not modified, patched, relocated, staged, or published.

The conversation began from clean `main` HEAD
`2eb1d84490d271f79e0a00bedb3d6d772983c6f2`. During the mandatory read-only
startup review, the worktree changed while HEAD stayed fixed: six tracked paths
became unstaged and two natural-source files appeared untracked. Complete diff,
source, replay, process, and handoff review classified all eight paths as one
coherent `recoverable-current-work` v177 packet. No unrelated or unknown tracked
work was found. The packet had already completed focused, candidate-state
aggregate, and post-promotion aggregate replay before recovery; those retained
receipts were rebound to the live source/manifest instead of being rerun.

## Target-first boundaries

Six logical functions tile load `0x1042A..0x107E1`, immediately before the exact
v176 `player_invalidate()` owner at load `0x107E2`:

| Function | MAIN__TEXT | Load range | Size | Terminal |
| --- | --- | --- | ---: | --- |
| `shots_reset()` (target `sub_1042A`) | `0AAF:593A` | `0x1042A..0x10443` | `0x1A` | `RET` |
| `shots_invalidate()` | `0AAF:5954` | `0x10444..0x104B5` | `0x72` | `RET` |
| `shots_update()` (target `sub_104B6`) | `0AAF:59C6` | `0x104B6..0x10551` | `0x9C` | `RET` |
| `shots_render()` | `0AAF:5A62` | `0x10552..0x105B8` | `0x67` | `RET` |
| `shots_hittest()` | `0AAF:5AC9` | `0x105B9..0x10712` | `0x15A` | `RETF` |
| `enemies_render()` | `0AAF:5C23` | `0x10713..0x107E1` | `0xCF` | `RET` |

`shots_invalidate()` corrects a material Ghidra undercount. The live database
records `body_size=0x6C`, `body_span=0x72`, and two ranges. Independent raw
16-bit decode tiles the complete `0x72` bytes through `RET` at load `0x104B5`,
and the next pinned TASM PROC begins exactly at `0x104B6`. The other five target
extents are likewise closed by terminal return plus the next adjacent boundary.

Independent recovery-time raw decoding reproduced every seam above. The target
shot-owner slice SHA-256 is
`47804105eef832fcc43f7fe4ad2ba28e0e395535c1f35f15722d17366614931e`
for load `0x1042A..0x10712` (`0x2E9 / 745` bytes). The adjacent enemy-renderer
slice SHA-256 is
`1569689d4fb4c791a5f8e782282f01c6d4e5d2765a09e7651fe8fc2900d202f6`
for load `0x10713..0x107E1` (`0xCF / 207` bytes).

Raw MZ relocation parsing also independently reproduces the physical split. In
original relocation-table order the shot producer owns
`[0x10702, 0x106D2, 0x1065B]`; the enemy renderer owns
`[0x107CA, 0x107B3]`. The two groups therefore remain separate natural TC86
objects instead of being fused merely because their code is adjacent.

## Natural source and physical producers

Maintained natural source is:

- `src/main/player/shots.cpp`, SHA-256
  `acad88d7e7345bf43dece46d21d7b94b496af1db85bfebfdcf37093a8c24dd7e`;
- `src/main/enemy/enemies_render.cpp`, SHA-256
  `51926025a766ae6a193f6d3869130a86b4df5f9a65818ef17349f7a315dc8704`.

`shots.cpp` compiles as one `0x2E9` `MAIN__TEXT` contribution containing five
logical functions. Natural source choices preserve the target AX/DX return use
from movement, the dword position copy, the transient pattern number in CX, the
unsigned rectangle tests, the FAR hit-test ABI, and the target damage-halving
shape. `enemies_render.cpp` compiles independently as `0xCF`; preserving the
still-live AX return value in the ordinary render branch reproduces the target
call setup while the damage-flash branch keeps its explicit top value.

Replay removes only the corresponding target-derived TASM suffix from the
current `m1rsuf.asm` scaffold and inserts `shotmain.cpp` followed by
`enrend.cpp`, immediately before exact v176 `pinv.cpp`. Symbol-only transforms
publish or retarget existing C/C++ linkage names; they do not allocate duplicate
storage or copy target bytes.

Neither maintained source uses inline assembly, `__emit__`, target-derived byte
arrays, `#pragma codestring`, fake returns, inert padding, target/object patching,
or ABI lies.

## Exact replay

All authoritative runs bind replay manifest SHA-256
`420fe713f3cf62ed0f89665524dd4a954e1af82a5f0b7a2edc639517539bd71a`.

Focused run `gptweb-v177-shots-enemy-focused-candidate-003` selects a 132-owner
dependency closure and passes two isolated cold builds with `failures=[]`.
Receipt SHA-256 is
`fa2c73d81fd6d78f52826e1de3c5ad3588d5059b9498fadfc29e650a50638182`.
Both v177 owners are raw exact, MAP exact, ordered-relocation exact, and emit
valid deterministic TC86 Borland C++ 4.02 OMF.

Candidate-state aggregate `gptweb-v177-shots-enemy-aggregate-candidate-001`
passes all 211 selected default owners twice before ledger promotion, with
`failures=[]`. Receipt SHA-256 is
`fe255d3df131fe3b2f4fba631888105843b7330e212a921f3e48dba0c1fc60f6`.

The already-completed post-promotion aggregate
`gptweb-v177-shots-enemy-aggregate-final-001` was recovered from the interrupted
packet and independently rebound to the same current source and manifest. It
passes all 211 default owners twice with `failures=[]`; receipt SHA-256 is
`cb95a60f17ab1df39c77cefc9b438fa95e268cc390f91c535a3d400c5eac4b0d`.
Its receipt was created at `2026-09-15T09:13:03.174415+00:00` and explicitly
selects both v177 units.

Two earlier focused directories receive zero exactness credit. Candidate001
produced no receipt. Candidate002 reached the real link and failed on missing
zero-byte linkage aliases `_byte_25980` and `_byte_259A7`; this was replay
plumbing, not a target-byte mismatch. After proving no tracked references and no
active producer, both receiptless directories were removed as current-packet
reproducible output. Focused003 and both successful aggregates are retained.

## Accounting and verification planes

After v177 promotion the non-overlapping MAIN ledger reports:

- `71,447 / 75,041` exact reviewed authored bytes (`95.210618%`);
- `421 / 435` exact reviewed authored functions (`96.781609%`);
- 14 reviewed blocked MAIN functions;
- 102 unreviewed MAIN authored candidates;
- 31 original-style ASM attestation observations.

The denominator expands by the complete `0x3B8 / 952` newly reviewed natural-C++
window and six logical functions. This is a moving reviewed authored denominator,
not a percentage of `MAIN.EXE` or the game.

Repository-native owned-extent/function exactness is PASS for both v177 physical
owners, all six logical functions, and the 211-owner post-promotion cohort.
Standalone TH04 production compile/link closure is not established. Whole-image
exactness is not established. Runtime-storage identity is not established. No
runtime scenario was executed. No v177 Factory Truth-Kernel acceptance claim is
submitted or claimed. Independent pristine-release provenance remains open.

Other TH04 artifacts remain separate active queues and receive no v177 MAIN
credit: OP has 94 unreviewed authored candidates, MAINE has 72, and ZUN has 13.
None currently has an honest accepted exact-byte/function denominator. `ZUN.COM`
remains treated as an MZ artifact despite its extension.

## Continuation

Continue immediately left into the connected bomb producer/boundary cohort, not
an unrelated small helper. The current unreviewed ledger has provisional
`PLAYER_BOMB` at load `0xFFB4` (`body_size=0x4D`, `body_span=0x76`), tiny
corroborated `BB_PLAYCHAR_PUT`, `BOMB_REIMU`, and `BOMB_MARISA` entries, then
provisional `bomb_update_and_render()` at `0x1020A` (`body_size=0x3C`,
`body_span=0x103`) and corroborated `BOMB_STARS_UPDATE_AND_RENDER_FOR` at
`0x1030D..0x10429`. Exact v177 `shots_reset()` begins at `0x1042A`.

The next packet should first determine which tiny entries are true authored
function boundaries versus internal labels/shared tails/compiler artifacts,
validate both provisional body spans through raw control flow, and audit the
physical TC4J/TASM producer and MZ relocation ordering before writing or fusing
natural source.
