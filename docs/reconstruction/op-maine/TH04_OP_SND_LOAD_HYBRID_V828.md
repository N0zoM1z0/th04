# TH04 OP SND_LOAD maintained-hybrid closure (v828)

## Result

v828 promotes OP `SND_LOAD` at decoded payload `0xDDCA..0xDEB3`
(`0xEA` / 234 bytes) to decoded-exact.

This closes the OP authored-function queue at **93/93** reviewed and
decoded-exact functions.

The claim is intentionally narrower than original-source recovery:
literal historical source spelling and packed-file / whole-`OP.EXE` exactness
remain unclaimed.

## Maintained complete source

The accepted source is now repository-maintained:

- `src/shared/sound/load.cpp`
- `src/shared/sound/load_handle_mov.inl`
- the previously accepted `load_*.inl` fragments used by the complete function.

The maintained body composes the already accepted filename/mode logic, DOS
open/read/close path, driver dispatch, and v391 DS save/restore fragments.

Only one newly symbolic primitive remains:

~~~cpp
asm { mov bx, ax; }
~~~

No `__emit__`, target byte array, function-local codestring, object patch, or
post-link patch is used.

## Why `89 C3` is admissible here

v823 already proved the code-generation mechanism:

- ordinary TC4J pseudoregister assignment emits `8B D8`;
- integrated inline assembly emits the target `89 C3`;
- changing that one instruction makes the complete 234-byte function raw-zero;
- the linked natural and diagnostic OP program images differ only at payload
  `0xDE8B` and `0xDE8C`.

v828 adds the missing independent precedent rather than repeating syntax
experiments.

The already accepted v394 `dialog_face_unput_8` hybrid uses the same
register-direction primitive. Independently observed TH04 and TH05 MAIN release
targets both preserve this sequence inside the corresponding 74-byte function:

~~~text
8B 46 04    MOV AX,[BP+4]
89 C3       MOV BX,AX
~~~

The complete TH04 and TH05 dialog bodies differ at only five address/call/data
bytes. Existing accepted evidence
`ev-th04-main-dialog-render-crossgame-v382`,
`ev-th04-main-dialog-render-hybrid-provenance-v394`, and
`ev-th04-main-dialog-render-raw-v394` already bind this register-direction class
as a narrowly scoped cross-game hybrid primitive.

Thus v828 does not invent a new acceptance rule for SND_LOAD. It reuses an
existing, independently corroborated project precedent for the sole two-byte
residual.

## Cold replay

Checked-in replay:

~~~sh
python3 scripts/probes/replay_th04_op_snd_load_hybrid_v828.py   --output-dir .analysis/reconstruction/probes/v828-op-snd-load-hybrid-review-003
~~~

Two isolated TC4.02/TLINK rounds reproduce:

- complete 234-byte SHARED object CODE SHA-256
  `1a486ee1cde1e0766d08ce0efa316ea36002ff836644971977494920b397478e`;
- `89 C3` at relative `+0xC1`;
- complete linked SND_LOAD SHA-256
  `50d62cb466990971edcfe5bdbf78ce99e815af2027cc3d21951db8e73fd6659f`;
- unchanged MAP owner `th04/snd_load.cpp`;
- all 804 ordered MZ relocations.

Relative to the natural OP baseline, the linked program differs only at
`0xDE8B` and `0xDE8C`.

Archived focused


SHA-256:

`0346f3f2d2e89121b1b89aaf7cab25f87cc3bc64540ff4de0e24d62bfe2c5dad`

## Canonical acceptance

The current decoded-function ledger replay checks **93 unique OP authored
function slices**, all with `raw_difference_count = 0`.

Archived canonical


SHA-256:

`50928bc1bcef1ea614574e94ccb9538f1e7167e7eb7ec92cafc6cbe806f22cc5`

## Scope limits

v828 closes the OP authored-function queue only.

The related MAIN and MAINE SND_LOAD boundaries remain separate acceptance
claims and must be replayed artifact-locally before promotion. The packed DIET
container, true file-backed byte ownership, complete product reconstruction,
and runtime verification remain separate work.
