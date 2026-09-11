# TH04 MAIN_033 Orange phase-entry boundary and natural-source candidate (v129)

## Scope and status

This packet reviews the target-authored near function historically labeled
`orange_195E4` and maintains its natural C++ candidate as
`orange_phase_entry()` in `src/main/boss/orange_phase_entry.cpp`.

Artifact binding:

- artifact: `th04-main` / `MAIN.EXE`;
- target identity: SHA-256
  `077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`;
- target canonicality: `candidate-local-attested`;
- code segment: `MAIN_033_TEXT`;
- TLINK group address: `13A9:5B54`;
- MZ load-module offset: `0x195E4..0x19685`;
- Ghidra image address: `0x295E4..0x29685`;
- file extent: `0x1ADE4..0x1AE85`;
- size: `0xA2 / 162` bytes;
- target-slice SHA-256:
  `28ec524c11fbf14f6dec94f4a24c5fa16b21461952a75ecadfc93b6f8e450b1a`.

The boundary is reviewed authored C/C++, but exact acceptance is deliberately
**blocked/non-exact** in the live ledger. Formal focused and aggregate cold
replay have not completed in this checkpoint.

## Boundary correction

Fresh target-bound Ghidra reports the correct minimum and maximum addresses but
only 103 body bytes in two ranges. The omitted 59 bytes are
`0x2960C..0x29646` in the Ghidra image, corresponding to ordinary reachable
code inside the same target PROC rather than post-return data or a second entry.

Pinned TASM, gap-free raw decoding, and adjacent control flow agree on the full
162-byte near function. The omitted block is reached when `boss.phase_frame ==
16`; it generates two random target coordinates, derives X/Y velocity by signed
division by 64, and initializes the gather radius and point count. Control then
rejoins the ordinary phase-motion path. The function terminates with `RET` at
load-module offset `0x19685`; the next Orange handler starts immediately at
`0x19686`.

Fresh Ghidra reports four direct callers at image addresses `0x29686`,
`0x29720`, `0x297BB`, and `0x29814`. It reports four unique callees. This is a
useful cross-check only; Ghidra names, types, and sparse body membership are not
exactness evidence.

One MZ relocation overlaps this owner at load-module offset `0x19668` (file
`0x1AE68`, target segment:offset `13A9:5BD8`).

## Natural C++ recovery

The maintained source uses the existing TH04 boss, gather, circle, randring,
and color types. No inline assembly, target-byte arrays, codestrings, fake
returns, target patching, or inert padding are used.

The first compiling TC4J probe emitted 160 code bytes. Two source-shape facts
explained the difference:

1. two direct `return 0` statements let TC4J move the shared zero-return block
   before the final tests, removing the target's two-byte jump; an ordinary
   `goto ret0` preserves the target terminal shared-return sink;
2. `gather_add_only_3stack()` uses the historical Pascal argument convention.
   Source arguments `(7, 6)` emit the target packed immediate
   `0x00070006`; `(6, 7)` emits the reversed packed value.

With only those source-level corrections, TC86 Borland C++ 4.02 emits a
162-byte code LEDATA with the target instruction and branch layout before link
fixups. The source SHA-256 is
`652eb8e30588cd5ca3e4d9ec9e870a1c1197ee8306a4a2ea46988705a4d604e3`.
The pre-link code LEDATA SHA-256 is
`f23e0fb3860ee00b4b228973641cd41edf5b07cbda584f0a421eed284b81807a`.

## Producer seam and diagnostic link

The retained v128 aggregate baseline has this physical order in
`MAIN_033_TEXT`:

`kupdate.obj -> m33kpre.obj -> m33kseam.obj -> kurumifg.obj`.

`m33kseam.asm` begins exactly at `orange_195E4`. The v129 replay transform
removes only that complete PROC, introduces `EXTRN _orange_phase_entry`, and
rebinds the four later Orange-handler calls. The remaining residual continues
at target offset `0x19686`; it remains replay-only target-derived plumbing and
receives zero reconstruction credit.

A bounded diagnostic link reused the v128 aggregate objects read-only, compiled
`th04/orentry.cpp`, assembled the hash-bound residual, and relinked in the same
object order. This is **not** the repository cold-replay Oracle and grants zero
exactness credit. It established:

- `th04/orentry.cpp` map contribution: `13A9:5B54`, size `0xA2`;
- residual map contribution: `13A9:5BF6`, size `0x836`;
- candidate owner bytes equal all 162 target bytes;
- target/candidate overlapping MZ relocation lists both equal `[0x19668]`;
- the complete diagnostic overlay SHA-256 is
  `a43129b502291d37518347a554ffc8eada80ee073b9e5fc737a8740ed927cbb1`,
  the same retained whole-overlay identity as v128.

The last point is layout-preservation evidence only. The overlay contains many
other replay scaffold owners and is not a standalone TH04 product build or a
whole-image exactness claim.

## Formal replay limitation in this conversation

The required focused command was requested but the execution surface rejected
it before the repository script started, so there is no focused Oracle result
from that attempt. The TH04 Factory adapter imports native exact-unit rows as
replayable claims but does not import candidate/source-present rows. Marking
this unit exact merely to obtain a Factory replay claim would invert the truth
boundary and was therefore not done. No Factory replay job was submitted for
v129.

Consequently, there is also no new aggregate cold-replay result. The retained
accepted aggregate baseline remains `gptweb-v128-kurumi-full-aggregate-001`
with 165 accepted owners.

## Retained unknowns and next validation

`sub_11DE6` in `MAIN_012_TEXT` remains unresolved. The previously tested
ordinary/register counter forms, `for`/`while`/`do`, explicit `_CX`, `-k-`,
`-G`, and CPU-level probes do not emit its DS threshold scan with `CX=9` and
`LOOP`; no new source hypothesis was found in this packet.

The first continuation step for v129 is to run the configured focused replay:

`python3 scripts/replay_th04_main_exact_units.py --unit th04-main-orange-phase-entry-v129 --run-id <unique-id>`

If and only if that passes both isolated cold builds, run the complete default
aggregate with no `--unit` selection. Promotion requires the resulting raw,
map, ordered-relocation, OMF, repository-snapshot, and determinism gates. After
that, the next structurally connected target-first candidate is the immediately
following Orange handler at load `0x19686` / Ghidra `0x29686`, reviewed together
with the remaining three direct callers as one cohort rather than as isolated
small-function wins.
