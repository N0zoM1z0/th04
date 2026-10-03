# OP/MAINE shared input-wait decoded acceptance (v565)

The maintained natural C++ producer `src/shared/hardware/input_wait.cpp` is
decoded-exact independently in OP and MAINE. This is a function-byte claim,
not packed-file or standalone-product exactness. Both `units.csv` owners remain
`source-present` because DIET does not provide honest packed-file offsets for
these decoded bodies.

## Target boundaries and identity

| Artifact | Payload offset | Loaded address | MAP public | Size | Target SHA-256 |
| --- | ---: | --- | --- | ---: | --- |
| OP | `0xDB62` | `1DA1:0152` | `0DA1:0152` | `0x56` | `2ef0578d61ec126f795bcb95f6b2698bd1a8dba3d6160e511889521620ed776e` |
| MAINE | `0xCE7A` | `1CC7:020A` | `0CC7:020A` | `0x56` | `3a73aea1528421db6658b8419aa06f4313b6341b968ffd9c1a043db8ed6964cf` |

For each target slice, the Ghidra inventory reports one contiguous 86-byte body;
independent ndisasm tiles all 44 instructions, all six direct branches land on
aligned internal instructions, and `RETF 2` closes the body. The MAP symbol and
module corroborate placement and candidate naming only; they do not attest
historical source identity.

The maintained source resets/senses input around frame delays, waits for the
current key to be released, then waits for a new key or the requested frame
count. A zero count selects the long repeating wait. This is a target-byte-
supported semantic reading, not a separate runtime observation.

## Cold replay

Focused two-round command:

```sh
python3 scripts/probes/replay_th04_shared_input_wait.py \
  --output-dir .analysis/reconstruction/probes/v566-shared-input-wait-001
```

Both bodies are raw-zero from the same checked-in source object. The SHARED MAP
contributions are exactly `0DA1:0152 0056` and `0CC7:020A 0056`; OMF identifies
TC86 Borland C++ 4.02. OP preserves all 804 ordered relocations and the retained
v489 linked program/EXE (`7e4cb7aa…` / `c32633e0…`); MAINE preserves all 559 and
its v489 linked program/EXE (`0f9658c8…` / `d3bdc485…`). These candidate-image
equalities are linker controls, not whole-target exactness.

The fail-closed decoded acceptance wrapper replays all 22 accepted functions
in each artifact. The v567 OP receipt SHA-256 is
`f53b5a697f71c855cdcdbc319be74e941097feaf47ca41d3ce39d5b5b896ae2d`; the
MAINE receipt SHA-256 is
`a382530b4448445662e2cbe1daafe7b2466bde7cdd5a86c693d0cff7baeea661`. Both
report 22/22 raw-zero, with 804/804 OP and 559/559 MAINE relocation sites.

## Replay snapshot size

The retained v489 source tree is about 27 MiB. `copy_compact_snapshot()` now
copies only C/C++ compiler-facing sources and text includes plus object files
named by the artifact's TLINK response, rather than every historical source,
listing, map, asset, executable, and object directory. The v566 receipt records
2,721,203 selected bytes over 1,174 OP files and 2,754,864 over 1,182 MAINE
files; its `source_bytes` counter includes 15 top-level `.obj`/`.lib` files.
A read-only breakdown attributes 2,549,948 OP and 2,583,609 MAINE bytes to
compiler sources/includes, plus the same 171,255 root support-object/archive
bytes. The linked objects are separately 101,922 bytes across 41 OP objects
and 90,749 bytes across 39 MAINE objects. Each successful replay deletes A/B worktrees;
aggregate runs also discarded backend logs and subreceipts after preserving the
small aggregate receipt. The filter is for these TCC replay paths; extend it
before using it for a TASM source build.

This does not transfer exactness to MAIN, another artifact, or a packed file.
Use `config/th04_decoded_function_acceptance.csv` and `config/evidence.csv` for
the live ownership and replay records.

## Semantic input/timing batch on semantic/readable

The 2026-10-03 batch starts from `33875da`, after the native planar fixes.
Names now identify the press timeout and elapsed press frames. The local
`REPEATING_PRESS_WAIT` constant describes the existing 9999 sentinel; it
introduces no new state. The MAIN and OP/MAINE source owners remain separate,
with their include order, scalar widths and Pascal signatures preserved.

Input sampling has two deliberately different entries. Reset clears key_det
and the first js_stat word, then falls through into sense. Plain sense ORs
BIOS keyboard actions and optional joystick actions into key_det, while Shift
is a fresh, separately sampled modifier. Keypad diagonals occupy independent
high-byte action bits; they are not the OR of two arrow bits. Replay remains
one byte and therefore has a different declaration surface from live input.

The wait first requires release, without a timeout, then counts press-wait
frames. Each iteration samples at reset before the frame and senses again
after it. A release is accepted only when both observations are clear: a
key released on the tick is still latched from the preceding observation.
Zero and an explicit 9999 both repeat indefinitely; negative arguments skip
only the press phase after release. These are preserved contracts, rather
than modernization choices for the x64 port.

The independent CPU fixture executes the complete relocated MAIN, including
its real input_sense, JS_SENSE and frame_delay bodies. It passes 240 keyboard,
Shift, reset/accumulation and joystick combinations plus 12 wait scenarios.
Those include press events after 9999 frames, a press on the deadline and
release lasting beyond the requested press timeout. Its BIOS bitmap, modifier
replies, active-low controller ports and logical IRQ ticks are synthetic;
this is not a physical PC-98 timing or full-route Oracle. The initial model
incorrectly treated release as one post-frame sample; the held-release
control rejected it. Correcting only the fixture to require a complete clear
interval makes all 252 pre-change controls pass.

Historical MAIN cold replay passes both rounds for all three affected owners:

| Owner | Relative target CS:offset | File offset | Bytes |
| --- | --- | --- | ---: |
| frame_delay | `130E:00D7` (SHARED) | `149B7h` | 21 |
| input_wait_for_change | `130E:0133` (SHARED) | `14A13h` | 86 |
| input_s.asm | `130E:06BC` (SHARED) | `14F9Ch` | 266 |

The complete accepted extents, MAP placement and overlapping relocations
remain raw-zero against the pinned MAIN. Source/header edits during an earlier
staged run were correctly rejected by the snapshot check; only the fresh
`semantic-input-v1234-final` two-round receipt is accepted. The old OP/MAINE
decoded replay scaffold and restored files are absent locally; no new decoded
target replay or acceptance promotion is claimed for them.

Replay commands (serialize all Borland/Wine commands):

```text
python3 scripts/replay_th04_main_exact_units.py --unit th04-main-frame-delay --unit th04-main-input-wait-for-change --unit th04-main-module-th04-input-s-asm-1379c --run-id NEW-input-timing
python3 scripts/probes/probe_th04_native_input_timing.py --build-dir .analysis/build/semantic-input-readable-final --output-dir .analysis/reconstruction/probes/NEW-input-timing
```

Receipts:
`.analysis/reconstruction/exact-unit-replay/semantic-input-v1234-final/receipt.json`
and `.analysis/reconstruction/probes/input-timing-v1234-{baseline,final}/receipt.json`.

The final dependency-validated fast build `product-20261003-072525-caaf425d`
preserves every physical byte and ordered relocation in MAIN/OP/MAINE against
the preceding source build: 193,983/79,372/72,246 bytes, SHA-256
`149c1e77…`/`ef37e6e8…`/`7bfd7fd5…`. Complete comparisons are
`.analysis/semantic-input-v1234/ARTIFACT.EXE-final-compare.json`. ZUN source is
unchanged and was not rebuilt in this bounded batch. The final 252 input
fixture results also equal the pre-change results. This proves source-to-source
compiler preservation, not native whole-target equality or a new route test.
