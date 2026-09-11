# TH04 `MAIN_012_TEXT` frontier exact-link packet (v119)

## Scope

v119 resolves the physical producer-order blocker left by v117/v118 without
claiming source recovery for the two unresolved routines in the middle of the
frontier. The packet promotes the already-maintained natural C++ for
`yuuka6_fg_render()` and `shots_add()` only after focused and aggregate cold
replay prove their declared owned extents at the target link positions.

The active artifact is `th04-main` / `MAIN.EXE`. The private target remains
operator input with `candidate-local-attested` canonicality and SHA-256
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.
No target file is modified, copied into the repository, or used as generated
source input.

## Recovery provenance

This packet was recovered at conversation start as coherent dirty work on HEAD
`23e54a6c6ed3a63526bcddd4b5fe49105bb85555`. The worktree contained exact-unit
manifest/replay changes, evidence and function-review updates, replay tests, and
one untracked replay wrapper template. Three private replay directories already
existed and no Borland/Wine/replay producer was active:

- `gptweb-v119-shots-focused-001`;
- `gptweb-v119-yuuka-focused-001`;
- `gptweb-v119-aggregate-001`.

All three receipts bind the current manifest SHA-256
`dbb517424ff21d5c992e9f8294fb51da2869d2d2249a13ac2446765e70d12f93`,
the current maintained source hashes, and the attested target above. The
interrupted packet initially lacked the function-boundary projection and
current handoff/generated documentation; those omissions were completed during
recovery rather than discarding the existing replay evidence.

## Target frontier

The reviewed order in `MAIN_012_TEXT` is:

| Routine | TLINK/TASM | Load-module extent | File extent | Size | v119 state |
| --- | --- | --- | --- | ---: | --- |
| `yuuka6_fg_render()` | `0AAF:712A` | `0x11C1A..0x11D95` | `0x1341A..0x13595` | `0x17C` | exact natural C++ |
| `shots_add()` | `0AAF:72A6` | `0x11D96..0x11DC9` | `0x13596..0x135C9` | `0x34` | exact natural C++ |
| `shot_velocity_set()` | `0AAF:72DA` | `0x11DCA..0x11DE5` | `0x135CA..0x135E5` | `0x1C` | unresolved source/origin |
| `sub_11DE6` | `0AAF:72F6` | `0x11DE6..0x11E11` | `0x135E6..0x13611` | `0x2C` | unresolved source/origin |
| `elly_fg_render()` | `0AAF:7322` | `0x11E12..0x11ECA` | `0x13612..0x136CA` | `0xB9` | exact natural C++ |

`yuuka6_fg_render()` remains a complete contiguous target/Ghidra/TASM body and
owns ten FAR-call MZ relocation sites. `shots_add()` remains absent as a Ghidra
function entry, but pinned TASM plus gap-free raw decode close the 52-byte body
through its terminal `RET`; the exact natural-C++ contribution ends at the
independent next producer address `0x11DCA`.

## Replay-only residual extraction

The original blocker was physical OMF producer order. The unresolved
`shot_velocity_set()` and `sub_11DE6` bytes followed `shots_add()` inside the
monolithic pinned ReC98 `th04_main.asm` contribution. Appending natural C++
after that monolith could not place the recovered owners at their target
addresses.

v119 adds a narrowly scoped exact-replay mechanism in
`scripts/replay_th04_main_exact_units.py`: `scaffold_extractions` materialize a
hash-bound span from the pinned reference scaffold into an Oracle-only assembly
producer. This is not repository product source and receives no reconstruction
credit.

For this frontier:

- complete pinned scaffold SHA-256:
  `c872e7c1d94d571fc62e6b14e0960b89ef882f46df60a1d8467d117b9e0e549b`;
- extracted `sub_11DE6` source span size: 393 bytes;
- extracted span SHA-256:
  `c7e8ffaa8ea1ce95941dcdd9035070cf39eb633a42dd80b5c9e5ccfd174cc70a`;
- checked-in wrapper template:
  `config/replay/th04_main012_frontier_residual.asm.in`;
- wrapper SHA-256:
  `f9a9893443074fc4e430fb8825c20d1d4e27527cc85ad5954e653b7262cfeee5`;
- generated replay-only source: `th04/m12seam.asm` inside each isolated cold
  materialization;
- generated source SHA-256:
  `f225c09c8558336a0eb607fe7729cf2284802fb034646a2a2ff530d0fabceddc`;
- replay-only OMF normalized SHA-256:
  `589f46874c476e6425138cc2ab4d6ef1470f6c278a2f1fc1e326ced664d7b1b7`.

The wrapper includes the existing pinned `shot_velocity.asm` and the extracted
pinned `sub_11DE6` span solely to preserve the unresolved residual's physical
link contribution between the exact C++ owners. It does not convert either
routine to accepted original assembly, reconstructed source, or an exact
function. Raw OMF hashes may differ through Borland dependency timestamps, so
replay compares their narrowly normalized identity; all link-relevant content
remains covered.

The extraction implementation is fail-closed over the complete scaffold hash,
unique start/end anchors, extracted-span hash, checked-in template hash, and
bounded symbol-only replacements. New unit tests cover successful extraction,
span drift rejection, input snapshot inclusion, and auxiliary OMF validation.

## Exact replay results

### `shots_add()`

Focused replay:

```text
python3 scripts/replay_th04_main_exact_units.py \
  --unit th04-main-shots-add-v117 \
  --run-id gptweb-v119-shots-focused-001
```

Both isolated builds report:

- target-exact 52-byte raw slice;
- exact map contribution `0AAF:72A6 0034 ... M=th04/shots.cpp`;
- exact ordered overlapping MZ relocation list (empty for this extent);
- valid deterministic TC86 OMF;
- deterministic normalized auxiliary residual OMF;
- stable scaffold-extraction receipt.

The maintained source hash is
`88b223e0ce8c52638fb2e9bac4378828a70625a9aa8a7082f371d92c347dc6fa`.

### `yuuka6_fg_render()`

Focused replay:

```text
python3 scripts/replay_th04_main_exact_units.py \
  --unit th04-main-yuuka6-fg-v118 \
  --run-id gptweb-v119-yuuka-focused-001
```

Both isolated builds report:

- target-exact 380-byte raw slice;
- exact map placement at load `0x11C1A` / TLINK `0AAF:712A`;
- exact ordered overlap of all ten target MZ relocations;
- valid deterministic TC86 OMF;
- deterministic normalized auxiliary residual OMF;
- stable scaffold-extraction receipt.

The maintained source hash is
`5fe271098eb60096df819c6ebb819f0c2d96010857ab4df92276a2f50188fa45`.

### Aggregate replay

The required current default cohort passes twice under:

```text
python3 scripts/replay_th04_main_exact_units.py \
  --run-id gptweb-v119-aggregate-001
```

All 155 selected owners pass. The A/B candidate `MAIN.EXE` SHA-256 is identical:

`a4a0f6637e5d7401bf3fd5ed3e92301558d018834cc0b0bc7e376b0b67637c3b`.

No previously accepted owner regresses.

## Function review

A fresh function review uses the v119 aggregate map, fresh target-bound Ghidra
metadata, pinned raw target bytes, and the explicit no-Ghidra/manual gates. It
reports:

- reviewed authored functions: 274;
- exact functions: 272 (99.270073%);
- automatic exact acceptances: 131;
- manual exact acceptances: 141;
- strict provisional rejections: 0;
- reviewed nonexact functions: 2.

The private report SHA-256 is
`97159d4095888307cca3582f14538bf4cc8e2af1aea4525198c4a036835a9e3c`.
`shot_velocity_set()` and `sub_11DE6` are intentionally absent from accepted
function credit.

## Current exactness and retained unknowns

After v119 the live reviewed C/C++ byte denominator is 41,101 bytes, of which
41,070 are exact (99.924576%). The only 31 reviewed nonexact bytes remain the
previously blocked `snd_load` and `enemy_bullet_template_push` functions.

The following questions remain open:

- `shot_velocity_set()` still has no accepted natural source or proved
  original-assembly classification. The target `MOV BX,SP; PUSH SI` plus
  `XOR BH,BH` shape remains unexplained by the allowed natural TC4J probes.
- `sub_11DE6` remains a reviewed 44-byte FAR target extent whose nine-threshold
  DS scan uses `CX=9` plus `LOOP`. TC4J is known to emit `LOOP` for generated CS
  switch-table scanners, but no accepted source-level DS threshold-loop shape
  reproduces this routine.
- Replay-only residual extraction is exactness plumbing, not standalone TH04
  production closure and not evidence about either unresolved routine's
  original source language.

## Continuation

The first structurally connected target-first packet remains the preceding
`sub_11B44` Yuuka6 entity renderer in `MAIN_012_TEXT`: load
`0x11B44..0x11C19`, file `0x13344..0x13419`, size `0xD6` / 214 bytes. It is
called from the now-exact `yuuka6_fg_render()` and renders chase-cross and
safety-circle entities. Reconcile its callers, six callees, MZ relocations,
data ownership, and terminal boundary before attempting natural source.
