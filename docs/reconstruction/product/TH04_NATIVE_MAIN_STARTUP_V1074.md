# TH04 native MAIN runtime differential, v1074

This bounded batch checks the first normal `GAME.BAT` route after the native
MAIN diagnostic link closed. It is runtime and layout evidence only; it does
not promote the candidate to exactness or full startup acceptance.

## Link input

The pinned single-writer replay was:

```text
taskset -c 0,1 nice -n 10 python3 scripts/probes/probe_th04_native_main_link.py \
  --output-dir .analysis/reconstruction/probes/native-main-link-v1074-20260930 \
  --require-link
```

The receipt SHA-256 is
`08927a64fa285feecedd88ebfe92445a5b8d682b6949e3a1bbb65431289493ae`.
All 192 C/C++ roots, 8 state owners, 125 product ASM owners, and 4 private
sprite-resource owners passed their compile/assemble gates. TLINK exited 0
with no unresolved symbols, duplicate publics, group overflows, or fixup
overflows. The candidate MZ is 190,937 bytes with 1,163 relocations and SHA-256
`81b694dee05807bc3a975e86bd9e83010f560102d22aed1af479f62371b117d1`.
The twelve body-only ASM roots still use private historical-context wrappers;
this remains a diagnostic link.

## Normal route checkpoint

The candidate was inserted into a disposable copy of the pinned runtime image
with `prepare_th04_main_diagnostic_hdi.py --startup game-bat` and booted through
the normal `GAME.BAT` route under the pinned DOSBox-X profile:


The run receipt SHA-256 is
`23f92a1266f5a4324b99b20c2a28979e4c84dcba51d0091f574631f1307a56b6`.
DOS boot markers passed and `DIAG.TXT` contains `START\r\n`; no MAIN-hit,
OP-trace, or CDG marker is instrumented in this image. The 60-second frame is
the red Japanese STOP-key help screen on a black background rather than the
gameplay frame. This is a candidate runtime differential, not a claim that the
full product route is accepted.

As the pinned control, the unmodified original MAIN/MAINE image was run through
the same `GAME.BAT` route and checkpoint. Its run receipt SHA-256 is
`0a08fc95e7154bb75a68823fa1d3a194bf2001dd140727a1e615a3b96509fd38`. The
control frame renders the red checkerboard playfield, player, bullets, and HUD
at the same 60-second checkpoint. Therefore the candidate/control difference
is not explained by the emulator's normal route or the black DOS frame.

## Input DATA/BSS observation

The target `MAIN` input module at load-module offset `0x1379C`
(`130E:06BC`, 0x10A bytes) encodes `_key_det` at DS offset `0x3974`,
`_shiftkey` at `0x3976`, and `js_bexist` at `0x039A`. In the v1074 TLINK map,
the maintained shared input body starts at `10E9:35FC` and the candidate
symbols are `_key_det` at `224E:C4B4`, `_shiftkey` at `224E:C4B6`, and
`_js_bexist` at `224E:136E`. These are target-observed versus
compiler-observed layout facts; they are not an exactness claim. The candidate
BSS order therefore remains a concrete static lead for the STOP-screen
differential, alongside the still-open startup and resident/layout closure.

## Cleanup and next bounded step

After the receipts and frame were hashed, disposable HDI, DOSBox execution
copy, and expanded native source/object payloads were pruned. Receipts and the
frame are retained under `.analysis/`; the pinned targets, toolchain, and
canonical runtime image remain untouched.

The next useful experiment is a private input/BSS checkpoint that records the
candidate `key_det`, `shiftkey`, and `js_bexist` values immediately after the
first `input_sense()` on the normal route, then compares that trace with the
target control. Do not change the maintained input module or claim startup
readiness from the current STOP-screen result.
