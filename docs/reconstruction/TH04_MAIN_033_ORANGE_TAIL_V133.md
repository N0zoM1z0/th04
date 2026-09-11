# TH04 MAIN_033 Orange tail reconstruction (v133)

## Scope

This packet closes the remaining `MAIN_033_TEXT` Orange tail immediately after
the v132 bounce/random owner. The selected target is the local Japanese
`MAIN.EXE`, SHA-256
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.
Its canonicality remains only `candidate-local-attested`.

Two authored functions and the dispatcher's compiler-owned switch data occupy
the complete remaining physical contribution:

| Item | Image extent | Load extent | File extent | Size | Ownership |
| --- | --- | --- | --- | ---: | --- |
| `orange_phase_multi_burst()` | `0x2998B..0x29AA2` | `0x1998B..0x19AA2` | `0x1B18B..0x1B2A2` | `0x118` | near executable function |
| `orange_update()` | `0x29AA3..0x29EA5` | `0x19AA3..0x19EA5` | `0x1B2A3..0x1B6A5` | `0x403` | FAR executable function |
| compiler switch tables | `0x29EA6..0x29EBB` | `0x19EA6..0x19EBB` | `0x1B6A6..0x1B6BB` | `0x16` | dispatcher owner data |
| complete v133 owner | `0x2998B..0x29EBB` | `0x1998B..0x19EBB` | `0x1B18B..0x1B6BB` | `0x531` | natural TC86 physical producer |

The complete target owner SHA-256 is
`3b94c066c783cc8700526d1f94030e33a2086c7822835126d945c59830a4051e`.
The near helper alone is
`1fdf52ab39394cc4156fb589635fc44dcc04cd3c831886b41bd66c28c7bb4e51`.
The FAR executable body alone is
`8a6b062486296c3787c2006cedeed6768ee5d115e644aaec8a83d30d265d28e6`.
The two trailing tables together are
`939cba61115dbf63056999ab876498d0d66c30cda138fbd7e0eef2ba6c71f882`.

The owner ends exactly with `MAIN_033_TEXT`; the following linker contribution
starts at `13A9:642C` in `MIDBOSS_TEXT`.

## Boundary correction

Fresh target-attested Ghidra is useful for identifying both entries but is not
usable as the boundary authority here.

At image `0x2998B`, Ghidra reports a near function whose body ranges from
`0x2272E` through `0x29AA2` with 406 body addresses. Target raw decoding and the
pinned TASM `orange_1998B PROC NEAR` instead prove one gap-free 0x118-byte body
through terminal `RET` at `0x29AA2`. The FAR dispatcher contains a direct near
`CALL` at image `0x29D9B` that resolves exactly to this entry. The next target
entry begins at `0x29AA3`.

At image `0x29AA3`, Ghidra incorrectly labels the dispatcher `__cdecl16near`
and cross-links its body from `0x22042` through `0x2C735`. Pinned TASM declares
`@orange_update$qv PROC FAR`; gap-free target decoding closes the executable
body at `POP SI; POP BP; RETF` through `0x29EA5`. The following 0x16 bytes are
not a third function. They are two compiler switch tables:

- `off_19EA6`: five near targets at `0x29C23`, `0x29C4F`, `0x29C54`,
  `0x29C59`, and `0x29C5E`;
- `off_19EB0`: six near targets at `0x29AC8`, `0x29B88`, `0x29C10`,
  `0x29C8A`, `0x29CF0`, and `0x29DEB`.

Every table word lands on a decoded instruction start inside the FAR body. The
tables contain no MZ relocation entries. Counting them as physical compiler
owner data while excluding them from the authored-function denominator matches
the established dispatcher policy used elsewhere in MAIN.

The complete owner has six ordered overlapping MZ relocation sites, at load
offsets `0x19D3D`, `0x19C00`, `0x19B6F`, `0x19B08`, `0x199E6`, and `0x19E70`.
The order is intentionally preserved rather than reduced to a set.

## Natural source and compiler feedback

The maintained source is `src/main/boss/orange_update.cpp`, SHA-256
`ccca586c096fbba7ffec83d1e4d34db6d48d4a12a9ce3157c02d039d269e242a`.
It is ordinary Turbo C++ source: no inline assembly, target-byte arrays,
`#pragma codestring`, fake returns, inert padding, target patching, or copied
switch-table words are used.

The source keeps the helper `static near` before public
`void pascal far orange_update()`. That source order naturally reproduces the
historical physical order and leaves only `orange_update()` as a TLINK public.
The outer `switch(boss.phase)` and inner `switch(boss.mode)` naturally generate
the two post-`RETF` TC86 switch tables.

The first real TC4J object was eight bytes short: the C++ source combined the
phase-4 hit-test condition and the `defeat_bonus` assignment into one
`if`/`else`, allowing TC4J to reuse one `boss.phase_frame <= 600` comparison.
The target performs that comparison twice for two independent decisions.
Expressing those decisions as two independent ordinary `if` statements restores
exactly the missing six-byte `CMP` plus two-byte `JG`; the CODE segment then
becomes exactly `0x531` bytes with `orange_update()` at object offset `0x118`.

A separate diagnostic link initially exposed an ABI-name mismatch for
`boss_explode_big(explosion_type_t)`. Same-target already-exact boss update
source publishes the historical symbol as `boss_explode_big(unsigned int)`.
Using that established declaration and an ordinary cast changes the external
OMF symbol binding without changing the generated 0x531-byte code shape.

The final diagnostic TC4J object is a valid `TC86 Borland C++ 4.02` module. A
bounded zero-credit TLINK using the v132 aggregate objects read-only placed the
natural producer at `MAIN_033_TEXT 13A9:5EFB`, size `0x531`, with
`orange_update()` at `13A9:6013`. All 1,329 owner bytes and all six ordered
relocations matched the target. This diagnostic result justified formal replay;
it did not itself grant exactness.

## Residual ownership and failed focused replay

The v132 residual assembler originally contributed exactly the same final
`0x531` bytes. v133 hash-removes the complete helper, FAR dispatcher, and both
switch tables while preserving the segment/layout object. The input scaffold is
SHA-256
`cc276ac7e3c91043b54c3dfa042db26509b487f9d2b0b4da1a6b59c51201e199`;
the removed textual span is
`a85ccdca09d3469ba156934d76c9b8d32b5883a93ff9fb90faac66821b24c443`;
the final zero-code residual source is
`8eb959ffdbe2c468ec59e14f879cf229b47e0857fc7d092305ced1aed5b2a9cc`.

Focused run `gptweb-v133-orange-tail-focused-001` deliberately remains negative
evidence. TASM stopped before Oracle comparison because the residual still
contained top-level `PUBLIC @ORANGE_UPDATE$QV` after its body moved to C++.
Moving producer ownership requires the established symbol-only adaptation
`PUBLIC` -> `EXTRN ...:far`. A standalone production-profile TASM probe after
that correction yields a valid Turbo Assembler 5.0 OMF with 21 SEGDEF records
and zero LEDATA records. No residual code receives reconstruction credit.

## Formal exact replay

The final focused two-cold replay actually ran and passed:

`python3 scripts/replay_th04_main_exact_units.py --unit th04-main-orange-tail-v133 --run-id gptweb-v133-orange-tail-focused-002`

Receipt SHA-256:
`7ba201568c4b7610246a5bbd07f7d136d44dd2758751b69c4c4661461f842cf3`.
The dependency closure contains 105 exact owners. Both builds place
`th04/orangeup.cpp` at `13A9:5EFB`, size `0x531`; both reproduce the owner SHA
`3b94c066c783cc8700526d1f94030e33a2086c7822835126d945c59830a4051e`
and the same ordered six relocations. The focused candidate MAIN identity is
`bb6651be5555160d989c178482e9c7db746eacac744cdb8b0657088cf017fa8b`.

The formal `orangeup.obj` is identical across A/B: raw SHA-256
`eae24f63a0d9832860d8b2b11e6bc878ee6656fedea5181191cf01238e0b9e96`
and dependency-timestamp-normalized SHA-256
`4351688dbb8cb287e12ee3e9ab6302edc2f0185ac4e38b6a821c4ef612afd4de`.
The zero-code residual OMF is valid in both builds and has stable normalized
SHA-256
`1b7b0da2b3de8f2b12e0ca418e0d77d8b010d617c5b5f446bdf04f139d199680`.
Its raw identity varies only with normal Borland dependency timestamps.

The required complete default aggregate then actually ran and passed:

`python3 scripts/replay_th04_main_exact_units.py --run-id gptweb-v133-orange-tail-aggregate-001`

Receipt SHA-256:
`4c931a9cb22662db87c3f1bcac299d36dabab18e9a48b61738c9781c926bed74`.
All 169 default owners pass together twice without regression. Aggregate A/B
candidate MAIN identity is
`875e1cbce327549e2e27c1c0e6787d2407bcae81b64ff3160c856b968fd4ed4a`.

## Independent function review

The two function entries require manual target-first policy because Ghidra's
body construction is wrong for both.

`orange_update()` uses the existing `reviewed_exact_extent` path: exact owner,
TLINK public, target metadata entry, and gap-free raw decoding independently
prove exactly 0x403 executable bytes and terminal `RETF`. Its trailing tables
remain outside the function denominator.

The helper is intentionally static and therefore has no TLINK public. The
existing `reviewed_exact_internal_call` gate was extended with an explicit
`allow_crosslinked_body=true` mode. This mode does not trust or repair a Ghidra
body. It requires a target-attested Ghidra entry, exact authored ownership, no
public at the internal entry, a gap-free raw terminal decode, an independently
attested next-target prefix, and a target near `CALL` whose signed displacement
resolves exactly to the internal entry. Without the explicit opt-in, the old
bounded-body requirement is unchanged. Focused tests cover both the positive
cross-linked case and the fail-closed no-opt-in case.

Using fresh provider observations for `0x2998B` and `0x29AA3`, the v133
169-owner aggregate map, pinned target bytes, and retained reviewed metadata,
the reviewer reports **297/299 exact functions (99.331104%)**, 148 automatic
acceptances, 149 manual acceptances, and zero strict rejections. The retained
report SHA-256 is
`336b8a692f71e455d47624c9b5705835a4aa9ce38573eef866cb83314710e21d`.

## Scope limits and continuation

This packet establishes repository exact-unit evidence for the declared
`0x531` physical owner and independently reviews the two executable function
extents. It does not establish standalone TH04 production closure, runtime
storage identity, a runtime scenario, or whole-image exactness. Factory
Truth-Kernel acceptance is a separate post-commit plane. The first two
controlled replay attempts (`job:fef5c79669dd42b4b5978df02a57c8b2` and
`job:3d0a5e9191164c5792bcbe72dfea8c53`) terminated before producing an Oracle
receipt because another Factory operation owned the TH095 registered worktree.
Both failures have `outcome=null`; neither is a TH04 replay verdict or rejection.

After that external lock cleared, the same committed claim
`claim:unit:th04-main-orange-tail-v133:owned-extent-exact` was independently
replayed from clean source commit
`239d2e16446edc4d9c2687ecc8425ebbcc412b35`. Controlled job
`job:ae0a488b4b434e3cb605fd6366d118c5` completed with Factory receipt
`receipt:c39c7d03dc07b85bcb83677594067870ed2a452ee0b38cca42284455d7b18071`,
`receipt_verdict=pass`, and `acceptance_decision=accepted`. The registry identity
reported by that job is
`registry:652d5b31639388a4aba9fc5f088b490d39af85c8ac835cb0e6abd12ef0049c16`.
This establishes Factory acceptance only for the v133 `owned_extent_exact`
claim; it does not establish standalone product closure, runtime-storage
identity, a runtime scenario, whole-image exactness, or project-wide Factory
acceptance.

The next useful target-first packet is the `MAIN_032_TEXT` dual-entry
`pointnums_add_yellow()` / `pointnums_add_white()` shared-tail seam. Fresh Ghidra
still reports yellow as a closed 0x1A body at `0x23D90..0x23DA9`, but target
instruction `JMP 0x23DBE` at `0x23DA8` enters the same tail reached by the white
entry at `0x23DAA`; that shared code continues through `RET 6` at `0x23DEE`.
The live ledger therefore correctly keeps yellow provisional. The next packet
should reconcile logical function entry semantics, physical PROC ownership,
shared-tail denominator treatment, ABI/source shape, and relocation ownership
before attempting natural C++.
