# TH04 `MAIN_033_TEXT` Kurumi spawn-ray phase-handler packet (v125)

## Scope and target identity

v125 follows the exact v124 Kurumi spawn-ray allocator/updater into the first
three phase handlers that call it. The active artifact is `th04-main` /
`MAIN.EXE`; the private target remains operator input with
`candidate-local-attested` canonicality and SHA-256
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.
No target bytes were patched, copied into product source, or used as padding.

One natural-C++ producer owns the continuous `MAIN_033_TEXT` target extent at
TLINK `13A9:5156`, load `0x18BE6..0x18DB5`, Ghidra linear
`0x28BE6..0x28DB5`, and file `0x1A3E6..0x1A5B5`. Its size is `0x1D0` / 464
bytes and its target SHA-256 is
`9c3767153a800277fd9c7fcdad6603f9c1999edbd48a35673b65dd15962e3c69`.
The three adjacent near functions are:

- `kurumi_spawnray_phase_left()` at `13A9:5156`, size `0x90` / 144 bytes;
- `kurumi_spawnray_phase_right()` at `13A9:51E6`, size `0x8E` / 142 bytes;
- `kurumi_spawnray_phase_dual()` at `13A9:5274`, size `0xB2` / 178 bytes.

The combined owner contains seven ordered MZ relocation overlaps. Focused and
aggregate receipts record identical target/candidate lists at load addresses
`0x18D4D`, `0x18D41`, `0x18D2E`, `0x18CAB`, `0x18C9F`, `0x18C1B`, and
`0x18C0F`.

## Boundary correction at `0x28BE6`

The first function was deliberately not accepted from Ghidra alone. Fresh
attested Ghidra reports the correct min/max span `0x28BE6..0x28C75`, but only
111 body addresses out of the physical 144 bytes. It omits exactly
`0x28BFE..0x28C1E` (33 bytes), and a direct disassembly query for `0x28BFE`
reports no containing Ghidra function.

Pinned TASM and raw target decoding prove that the omitted bytes are ordinary
in-function code, not data, alignment, or a shared tail. The missing branch is
the `boss_phase_frame == 48` path: it creates the left shrinking circle, sets
`circles_color` to white, plays sound effect 8, and returns. Both MZ
relocations owned by the physical `0x90`-byte procedure (`0x18C0F` and
`0x18C1B`) occur inside this Ghidra-omitted block. The next pinned TASM PROC
and final generated public both begin exactly at `0x28C76`.

The function reviewer therefore uses its existing `reviewed_exact` manual gate,
not the ordinary contiguous-Ghidra gate. That gate requires Ghidra's min/max to
agree with the configured extent and independently decodes all 144 target bytes
gap-free. v125 decodes 47 instructions and terminates in `RET` exactly at
`0x28C76`. `kurumi_spawnray_phase_right()` and
`kurumi_spawnray_phase_dual()` have complete contiguous Ghidra bodies and use
the ordinary exact-owner gate.

## Natural-source compiler result

The maintained source is
`src/main/boss/kurumi_spawnray_phases.cpp`, SHA-256
`eec905e4795d803d99adda984a0ae5c4d726de4b7bc9d19022455c8df12f9782`.
It keeps the three phase bodies independent rather than hiding target code
shape behind a helper.

The source expresses the target-observed phase-frame transitions directly:

- frame 16 selects sprite 8, 9, or 10;
- frame 48 creates the appropriate left/right shrinking circles and plays SE 8;
- frame 64 clears the sprite and starts one or two exact v124 spawn rays;
- later frames configure the blue outlined-ball aimed ring and use the exact
  v124 updater to reset `boss.phase_frame` and `boss.mode` when all rays are
  free.

The first bounded TC4J compile already emitted exactly 464 CODE bytes with
PUBDEF offsets `0x000`, `0x090`, and `0x11E`. Those offsets exactly match the
three physical target boundaries. There was therefore no source-size or
control-flow tuning loop: pre-link mismatches were address/fixup words only.
The cheap probe dependency-normalized OMF SHA-256 was
`38f5415cffbbdeb42ade978fc3530af24156214a61d9ece189f18ff5f5b8b691`;
the formal cold-replay object below has normalized SHA-256
`65f3d67f230c91dad9c9e6c4e857828f5ced974f359d6ffb5618504659b8a7f5`.

The maintained source contains no inline assembly, target-derived byte arrays,
`#pragma codestring`, fake returns, inert padding, target patching, or ABI lies.

## Physical producer split

v124 already established that this region lies inside the original monolithic
`MAIN_033_TEXT` assembler contribution. Its replay-only residual began at
`0x18B68` and ran to the end of the segment. v125 must insert the 464-byte
natural owner into the middle of that residual without converting untouched
assembler into product source.

The cold replay layout is therefore:

```text
exact v124 kurrays.cpp
replay-only m33kpre.asm     0x18B68..0x18BE5
natural kphase.cpp          0x18BE6..0x18DB5
replay-only m33kseam.asm    0x18DB6..MAIN_033_TEXT end
```

The new prefix is extracted from pinned `th04_main.asm` only inside cold replay.
Its raw source-text span is `kurumi_18B68 proc near` through
`kurumi_18BA7 endp`, 1,033 bytes with SHA-256
`63a8315348a0c6c499bf04a77c42ef0115859dfb92e39a8be171fe4a38d2b8dd`.
The generated wrapper is fail-closed at SHA-256
`1c981e4b667f44a409de1dcba2367ecbe38a7b3364f3bea77b1c0036e8bf06a5`;
a symbol-only transform publishes the two residual near functions and closes
`MAIN_033_TEXT`, producing SHA-256
`d763c687b53509a44503baef38b38bbb324e4a823672210b0848e99ab90bd6b3`.

The v124 suffix scaffold is separately bound at SHA-256
`26869d8279967a46471a36d4ce202cafcce1a2bfec8081dd7b3d8857446d84c6`.
v125 removes the old `kurumi_18B68` through `kurumi_18D04` physical body from
that replay object; the removed source-text span is 6,020 bytes with SHA-256
`a973d522efe3cf1b073568ab816a4d913bda5e1cbe52a2084d7e07df62e2ff7f`.
It declares the two residual prefix functions plus the three new C++ publics
and rebinds one later dispatcher call to each natural function. The patched
suffix SHA-256 is
`b7e278aaecd81f8f22b71a7f8245294d5ee4cdaa72a4162368768c316b351edd`.

A cheap pre-link TASM test initially exposed that the two residual prefix
functions had been local symbols in the original monolith while the later
suffix calls them. v125 resolves that object-boundary effect by publishing them
from the prefix and declaring them external in the suffix. A second pre-link
probe assembles both residual objects cleanly. This changes symbol ownership
only; it does not move storage or synthesize bytes.

Both residual objects remain replay plumbing and receive zero reconstruction,
function, or byte-exactness credit.

## Focused and aggregate replay

Focused two-cold replay:

```text
python3 scripts/replay_th04_main_exact_units.py \
  --unit th04-main-kurumi-spawnray-phases-v125 \
  --run-id gptweb-v125-kurumi-phases-focused-001
```

passes all 97 dependency-closure owners in both isolated builds. The new owner
is raw/map/relocation exact at
`13A9:5156 01D0 ... M=th04/kphase.cpp`. The natural C++ object is valid TC86
OMF with A/B normalized SHA-256
`65f3d67f230c91dad9c9e6c4e857828f5ced974f359d6ffb5618504659b8a7f5`.
The replay-only prefix and suffix objects are also valid and deterministic at
normalized SHA-256
`895f77ea9cb23dfcd9287e60c25824956c6fe6497a147200de45a03675f3a4b7`
and
`2452711b7c78227ec3bda5b9ac2c13bc1e2288cbd074e4c844e6becde91cae63`.
Focused A/B candidate MAIN SHA-256 is
`a5a502b9cd343ed9d1f67b04fa0c33a71d879fffeb167e57a7bb4b761334c428`.

Required aggregate replay:

```text
python3 scripts/replay_th04_main_exact_units.py \
  --run-id gptweb-v125-kurumi-phases-aggregate-001
```

passes all 161 default owners twice with no previous accepted-owner regression.
Both aggregate candidate MAIN executables have SHA-256
`ac0d5a823fc5ec3aae0566ed811fcd5673790bc1684fee8f7752b7d535d6c942`.
The replay manifest SHA-256 is
`55ac7a5b42e752432192468fdf6478d48b598a88fad2aff0fe930c2a359fb1f5`.
The aggregate receipt SHA-256 is
`e568bfe70025346e0ce8cbad723709b596374344ea8de5cac0d469e3b9d058f8`.

## Function review and continuation

Fresh target-bound metadata plus the aggregate map produce:

- reviewed authored functions: 283;
- exact functions: 281 (99.293286%);
- automatic exact acceptances: 138;
- manual exact acceptances: 143;
- strict provisional rejections: 0;
- reviewed nonexact functions: 2.

The private report SHA-256 is
`2294566f1f5f8ed39040fd9d260ef8f7dd9c459f45539520c82220e25cfef332`.
The reviewed C/C++ byte total is now 43,033 / 43,064 exact (99.928014%). The
only 31 reviewed nonexact bytes remain the two older blocked functions.

`shot_velocity_set()` / `sub_11DE6` remain unresolved. Fresh v125 target review
again finds no new natural source-level explanation for the DS-resident
nine-threshold `LOOP` scanner, so no old negative loop matrix was repeated.

The first target-first continuation is the immediately following
`kurumi_18DB6`. Pinned TASM defines load `0x18DB6..0x18E42`, file
`0x1A5B6..0x1A642`, size `0x8D` / 141 bytes, target SHA-256
`f8e080e24994a4bf2600ccebdfaf1628dfae08b4160371e82ad11b7ca88fc1a0`,
with no MZ relocations. Fresh Ghidra has the correct min/max but only 114 body
addresses, omitting exactly `0x28E26..0x28E40` (27 bytes). Raw/TASM show that
block as ordinary second-pass special-bullet code: turn angle by `0x80`, reduce
speed, randomize the angle, emit the second special bullet, and increment the
local Kurumi toggle before the function's terminal `RET`. The next physical
PROC starts exactly at `0x28E43`. Reconcile this sparse body formally before
attempting natural source.
