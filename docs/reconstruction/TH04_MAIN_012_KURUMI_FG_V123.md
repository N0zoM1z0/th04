# TH04 `MAIN_012_TEXT` Kurumi foreground renderer packet (v123)

## Scope and target identity

v123 reconstructs the complete Kurumi foreground renderer whose true entry is
missed by Ghidra. The active artifact is `th04-main` / `MAIN.EXE`; the private
target remains operator input with `candidate-local-attested` canonicality and
SHA-256
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.
No target bytes were modified, relocated, copied into product source, or used
to patch a candidate.

## Boundary and analysis pathology

The complete function is `kurumi_fg_render()` at:

- TLINK `0AAF:6CA3`;
- load-module `0x11793..0x1196A`;
- target file `0x12F93..0x1316A`;
- size `0x1D8` / 472 bytes;
- target slice SHA-256
  `92fa7b21814e15e6b2ed43a256b764fbab2e4f000079985dc9edbed2664e090d`.

Fresh attested Ghidra has no function at the true linear entry `0x21793`.
Instead it creates `switchD_2000:c2fc::caseD_0` at `0x218B2`. Target raw decode
proves that `0x218B2` is the displacement byte of the real instruction
`FF 76 FE` beginning at `0x218B0`, so the Ghidra entry is not an instruction
boundary and remains excluded from the authored function universe.

Pinned TASM begins `@kurumi_fg_render$qv proc near` at load `0x11793` and keeps
that PROC open through the terminal `RET` at `0x1196A`. The exact v122 Orange
owner begins at the next byte, `0x1196B`. The Kurumi extent contains eight MZ
relocation sites at load addresses `0x117D9`, `0x11810`, `0x11823`, `0x11831`,
`0x118AA`, `0x118BC`, `0x11929`, and `0x1195F`.

TH04-local `stage2_setup()` installs `kurumi_fg_render` through
`boss_fg_render_func`, explaining why no direct code xref is needed to establish
callback ownership.

## Spawn-ray data ownership

The renderer consumes six records from the existing `custom_entities` storage.
TH04-local TASM independently fixes the relevant layout:

- six records;
- record stride `0x1A` bytes;
- one-byte state flag followed by one unused byte;
- `PlayfieldPoint target`;
- `PlayfieldPoint origin`;
- `PlayfieldPoint velocity`;
- twelve trailing padding bytes.

The same layout is exercised by the target `kurumi_spawnrays_add()` and the
adjacent spawn-ray updater in `MAIN_033_TEXT`; their TASM pointer increments are
also `0x1A`. ReC98's `b2.cpp` declaration is therefore used only as a source
shape hypothesis after the TH04-local stride and field accesses are confirmed.

The renderer deliberately uses signed `/ 16` for spawn-ray coordinates. Target
code emits `CWD; IDIV 16` for these fields rather than arithmetic shifts, so the
maintained source preserves that distinction.

## Natural-source feedback loop

The maintained source is `src/main/boss/kurumi_fg_render.cpp`. It uses the same
natural TC4J shapes already accepted for adjacent foreground renderers:

- SI/DI hold left/top;
- phase-zero animation derives from `stage_frame_mod16 / 4`;
- the HP-fill branch uses the repository GRCG helpers plus three circles;
- register-port GRCG shutdown is `_DX = 0x7C; _AL = 0; outportb(_DX, _AL)`;
- damage rendering uses `super_put_1plane()` with the ordinary all-plane mask;
- big-explosion rendering reuses live AX as the top argument;
- the common tail calls both explosion update/render helpers.

The first ordinary source shape used:

```cpp
if(spawnray->flag != B2SF_FREE) {
    // render the ray
}
```

and emitted 469 bytes, three bytes shorter than the target. The compiler kept
BX live across the conditional and therefore omitted the target's
`MOV BX,[spawnray]` reload before the first field read.

The target branch actually skips directly to the loop iteration expression.
Expressing that control flow naturally as:

```cpp
if(spawnray->flag == B2SF_FREE) {
    continue;
}
```

causes TC4J to reload BX in exactly the target position. The second bounded
probe therefore emits exactly 472 code bytes. Candidate-versus-target then has
39 mismatch runs, and every run is exactly one unresolved 16-bit link-time
word. Zeroing those diagnostic words makes all 472 bytes identical with
SHA-256
`90a0dd802af963ebdd2d876500fd8f3474286392d6df5e5b76530e07a92c4683`.
This compiler-shape result did not receive exactness credit until linked cold
replay passed.

The final maintained source contains no inline assembly, `__emit__`,
`#pragma codestring`, target-derived byte arrays, fake return, inert padding,
object patching, or ABI lie.

## Replay integration

v123 applies after the v122 transforms. Its fail-closed source transform binds:

- v122-transformed scaffold SHA-256
  `e37c600ce4aefd698d0979a4d20cb84fec4c10b2461cf0d82b2a7bb5b2b069ce`;
- removed Kurumi target-derived TASM PROC span SHA-256
  `2b6ef32d0f3e1b463fb5af6b94795c3d2da61cf38572daac4f48de53baf5b1c7`;
- patched scaffold SHA-256
  `989a82a4da82441d54a3e3f03ac5bf327539b6db192896887d792e15c04a9647`.

The original uppercase ABI spelling `@KURUMI_FG_RENDER$QV` is externalized and
TC4J publishes the same PUBDEF. `th04/kurumifg.cpp` is inserted immediately
before exact `th04/orangefg.cpp`.

## Focused replay

Focused two-cold replay:

```text
python3 scripts/replay_th04_main_exact_units.py \
  --unit th04-main-kurumi-fg-v123 \
  --run-id gptweb-v123-kurumi-fg-focused-001
```

passes both isolated builds. Each reports:

- all 472 target bytes exact;
- exact map contribution `0AAF:6CA3 01D8 ... M=th04/kurumifg.cpp`;
- exact ordered overlap for all eight target MZ relocations;
- valid TC86 Borland C++ OMF;
- dependency-timestamp-normalized object SHA-256
  `4a0111c84bead656872e2191fce26723ae247a82a9c68bde37580a5c7ed6af22`;
- deterministic candidate MAIN SHA-256
  `64c0fc43eb3832f88c504cfc67c566b1078388d3a803bd72f9482c2acebb051c`.

## Aggregate replay and no-Ghidra function review

The required aggregate replay:

```text
python3 scripts/replay_th04_main_exact_units.py \
  --run-id gptweb-v123-kurumi-fg-aggregate-001
```

passes all 159 default owners twice. Both candidate MAIN executables have
SHA-256
`99e38fa3783442c59c466cc2fed8cf2481e8be3e9caa3b9d0318d2943bd7ec1b`.
No previously accepted owner regresses.

Because Ghidra misses the true function entry, v123 uses the repository's
explicit `reviewed_exact_no_ghidra` path rather than fabricating metadata. The
reviewer independently requires the generated TLINK public, exact owner, target
file/load mapping, gap-free raw decode through the terminal RET, and an exact
owner-end boundary. The existing Ghidra pseudo-function at `0x218B2` remains an
excluded analysis artifact.

The fresh v123 function review reports:

- reviewed authored functions: 278;
- exact functions: 276 (99.280576%);
- automatic exact acceptances: 134;
- manual exact acceptances: 142;
- manual no-Ghidra acceptances: 17;
- strict provisional rejections: 0;
- reviewed nonexact functions: 2.

The private report SHA-256 is
`a06b13613987191a17d284e220d9bb2a50e02cbc550d07d77c3ef9294106270a`.

## Current state and continuation

v123 expands the reviewed C/C++ byte denominator by 472 bytes and closes all of
them exactly. The live MAIN total is 42,229 / 42,260 exact (99.926645%). The
reviewed function total is 276 / 278 exact (99.280576%). The only 31 reviewed
nonexact bytes remain the two older blocked functions.

The unresolved `shot_velocity_set()` / `sub_11DE6` source-origin seam is
unchanged. Fresh v123 provider disassembly again confirms the complete 44-byte
FAR `CX=9`/DS-table `LOOP` scan and same-segment `NOP; PUSH CS; CALL near`
tail. No new falsifiable natural-source hypothesis emerged, so the already
negative ordinary-loop matrix was not repeated.

The first structurally connected continuation is the `MAIN_033_TEXT` spawn-ray
producer/updater cohort that owns the data consumed here:

- `kurumi_spawnrays_add(int,unsigned char)`: load `0x18A14..0x18A78`, file
  `0x1A214..0x1A278`, 0x65 / 101 bytes, SHA-256
  `59f51c6db0ef89946794e5eb04d0620f049c0e77830f326d3a7b043316adb9a6`;
- `kurumi_18A79`: load `0x18A79..0x18B67`, file `0x1A279..0x1A367`,
  0xEF / 239 bytes, SHA-256
  `61b1c06f95299c7fa544a664b3126d84e65fab5b1cf9d15da247285875fcad27`.

Fresh attested Ghidra constructs both bodies contiguously. They are adjacent,
share the same six callers, operate on the same six 0x1A-byte records, and
contain four MZ relocations in total. The first creates a ray through `vector2`
and `snd_se_play`; the second advances the ray lifecycle and calls the circle,
sound, and fixed-speed bullet paths. Treat them as one source/data-owner cohort
before branching into the six Kurumi phase callers.
