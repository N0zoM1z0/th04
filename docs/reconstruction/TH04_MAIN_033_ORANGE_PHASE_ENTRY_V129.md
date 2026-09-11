# TH04 MAIN_033 Orange phase-entry boundary and natural-source recovery (v129-v130)

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

v129 established the reviewed authored boundary and maintained natural C++ but deliberately left the function blocked/non-exact. v130 completes the required focused and aggregate cold replay and promotes the same 0xA2 extent to exact without changing the source or replay seam.

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

## v130 formal exact replay and promotion

The v130 session reran repository and analysis identity gates before promotion.
The private target remains the 156,258-byte `candidate-local-attested` MZ with
SHA-256 `077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.
The registered `th04-ghidra` provider exposes no `get_metadata` operation, so
only discovered read-only operations were used. Its `check` result and the
repository-native `python3 scripts/ghidra.py th04-main check` independently
reconfirm the same target mapping and 1,136 relocation sequence.

Focused two-cold replay actually ran and passed:

`python3 scripts/replay_th04_main_exact_units.py --unit th04-main-orange-phase-entry-v129 --run-id gptweb-v130-orange-phase-entry-focused-001`

Receipt: `.analysis/reconstruction/exact-unit-replay/gptweb-v130-orange-phase-entry-focused-001/receipt.json`.
Both isolated builds report exact raw bytes, exact map placement, and exact
ordered relocation overlap for all 162 bytes. Both place `th04/orentry.cpp` at
`13A9:5B54` size `0xA2`, reproduce target slice SHA-256
`28ec524c11fbf14f6dec94f4a24c5fa16b21461952a75ecadfc93b6f8e450b1a`,
and reproduce the sole relocation `[0x19668]`. The emitted TC86 object is valid
and identical across A/B: raw SHA-256
`bbc10cc760a42c7d24ba76e9a7ebfbe9703e309819e3315844b6e233e49a11ea`,
normalized SHA-256
`f0ca55128437f77f35aba95765734a032e70d70c16a9c48a71811d1aa314a052`.
Focused candidate MAIN identity is identical across A/B at
`978bd87221b7b539fd38c3a81d85c6aa3bc7a33b2c9eb29a75d25bf770d9bde5`.

The complete default aggregate then actually ran and passed:

`python3 scripts/replay_th04_main_exact_units.py --run-id gptweb-v130-orange-phase-entry-aggregate-001`

Receipt: `.analysis/reconstruction/exact-unit-replay/gptweb-v130-orange-phase-entry-aggregate-001/receipt.json`.
All 166 default owners pass together twice. The Orange owner retains the same
162-byte target slice, exact map contribution, object identity, and relocation
`[0x19668]`; no previously exact owner regresses. Aggregate candidate MAIN
identity is deterministic across A/B at
`a43129b502291d37518347a554ffc8eada80ee073b9e5fc737a8740ed927cbb1`.

A fresh function-review pass adds a current target-bound Ghidra observation for
`0x295E4`. Fresh Ghidra still reports `body_min=0x295E4`,
`body_max=0x29685`, and only 103 body addresses. The reviewer therefore admits
`orange_phase_entry()` only through the configured `reviewed_exact` sparse-body
path, which separately requires exact owner/public placement and a complete raw
16-bit decode through terminal `RET`. The report yields 290/292 reviewed
authored functions exact, 144 automatic acceptances, 146 manual acceptances,
and zero strict rejections.

These receipts establish repository exact-unit acceptance for this reviewed
extent. They do not establish a standalone TH04 product build, original runtime
storage identity, or runtime scenario validation. Factory Truth-Kernel
acceptance remains a separate plane until a committed imported exact claim is
submitted and accepted.

## Retained unknowns and next validation

`sub_11DE6` in `MAIN_012_TEXT` remains unresolved. The previously tested
ordinary/register counter forms, `for`/`while`/`do`, explicit `_CX`, `-k-`,
`-G`, and CPU-level probes do not emit its DS threshold scan with `CX=9` and
`LOOP`; no new source hypothesis was found in this packet.

The formal v130 promotion gate is closed. The next structurally connected
target-first candidate is the immediately following Orange handler at load
`0x19686` / Ghidra `0x29686`, reviewed together with the remaining three direct
callers at Ghidra image addresses `0x29720`, `0x297BB`, and `0x29814` as one
cohort rather than as isolated small-function wins. Their corresponding
load-module offsets, exact extents, relocation ownership, and source shape must
be re-established from current target/TASM/MAP/Ghidra evidence before any
reconstruction claim.
