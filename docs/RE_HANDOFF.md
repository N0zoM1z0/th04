# TH04 reconstruction handoff

Updated 2026-09-25. This file is the concise resume index. Do not infer current
progress from historical experiment directories, old receipt paths, candidate
source names, or previous session prose. Live counts come from:

- `config/units.csv`
- `config/th04_function_boundaries.csv`
- `config/th04_decoded_function_acceptance.csv`
- `config/th04_main_authored_functions.csv`
- `python3 scripts/status.py`

The active plan is [RE_ROADMAP.md](RE_ROADMAP.md). Bounded historical evidence
and reusable negative results are routed through
[reconstruction/README.md](reconstruction/README.md) and the evidence ledger.

## Resume checks

Before target-dependent work:

```sh
git status --short
python3 scripts/preflight.py
python3 scripts/status.py
python3 scripts/audit_compat_dependencies.py --check
python3 scripts/decoded_function_acceptance.py
python3 scripts/boundary_review/validate_function_boundary_ledger.py
```

Current target canonicality is `candidate-local-attested`: size, SHA-256, MZ
structure, tracking, function-boundary ledgers, and decoded acceptance validate,
but this is not proof of an official pristine release. Re-attest the active
Ghidra database before making new target observations. Keep one writable
Borland/Wine reconstruction session at a time.

## Current non-MAIN state

| Artifact | Boundary reviewed / corroborated / provisional | Function exact | Pending / blocked | Decoded source-owner bytes |
| --- | ---: | ---: | ---: | ---: |
| OP.EXE | 70 / 15 / 8 | 64 | 29 / 0 | 6,277 |
| MAINE.EXE | 47 / 20 / 5 | 41 | 31 / 0 | 4,037 |
| ZUN.COM | 13 / 0 / 0 | 0 | 11 / 2 | 404 |

These are decoded-function/source-owner extents, not packed-file coverage.
There is still no honest packed-file authored-source denominator for OP, MAINE,
or ZUN.

OP has 5,840 exact source-owner bytes. Its maintained but nonexact decoded
candidates are:

- SCORE `scoredat_decode` + `scoredat_encode`: 274 bytes total;
- `_snd_se_update`: 76 bytes;
- `SND_SE_PLAY`: 57 bytes;
- `nopoly_B_put`: 30 bytes.

MAINE has 3,662 exact source-owner bytes. Its maintained but nonexact decoded
candidates are:

- SCORE `scoredat_decode`: 88 bytes;
- SCORE `scoredat_encode`: 101 bytes;
- `box_1_to_0_masked`: 134 bytes;
- `egc_start_copy`: 52 bytes.

MAIN remains an evidence-triggered side lane, not the active reconstruction
queue. ZUN's 13 physical authored boundaries are reviewed, but 11 still lack
accepted source/origin ownership and two C++ items remain blocked.

## Most recent accepted work

The newest accepted OP function is `playchar_titles_put(int)` at payload
`0xD285`, 179 bytes. The v685 OP aggregate passes 64/64 registered decoded
slices raw-zero with all 804 target-ordered relocations preserved. Receipt
SHA-256: `07faf8423c08e345939042856be69bf98a6a583e4f3aa45e9576600e98a91ba9`.

The newest accepted MAINE function is `hiscore_scoredat_save()` at payload
`0xC316`, 156 bytes. The v683 MAINE aggregate passes 41/41 registered decoded
slices raw-zero with all 559 target-ordered relocations preserved. Exact credit
is local to the save wrapper; the surrounding SCORE codecs remain nonexact.
Receipt SHA-256:
`fd272880c0b8bb3f750398cc5aa1883e5492fbaa4c2a57c5880812e91ea82823`.

Other recent accepted OP work includes `cfg_load()` at `0xA74C` and
`polygon_build(...)` at `0xBFC5`. Their function-level exactness is already
represented in the acceptance/evidence ledgers; do not reopen them without new
contradictory evidence.

## Known low-level codegen gaps

Do not promote these by copying target instructions, using decompilation helper
assembly, or forcing pseudo-registers merely to obtain byte equality.

- MAINE `egc_start_copy()` (`0xA2D6`, 52 bytes): ordinary `outport()` produces
  DX-before-AX loads and a different zero-value form; the historical
  `outport2` route is decompilation-oriented inline assembly.
- MAINE `box_1_to_0_masked()` (`0xA78F`, 134 bytes): after natural-codegen
  tuning, the remaining differences are the EGC setup write ordering; the
  known byte-forcing helper is again decompilation support.
- OP `SND_SE_PLAY` (`0xE2F2`, 57 bytes): natural Pascal C++ uses a BP frame and
  ordinary extension/indexing; target uses SP-relative access and forced BL/BH
  register shapes.
- OP `_snd_se_update` (`0xE32C`, 76 bytes): natural C++ is one byte longer due
  to ordinary unsigned-byte indexing; register-specific forcing is diagnostic
  only.
- OP `nopoly_B_put` (`0xBFA7`, 30 bytes): intrinsic `memcpy` naturally reaches
  the same 30-byte `REP MOVSW` strategy but orders source/destination segment
  setup differently. Cross-game pseudo-register/`__memcpy__` code is not
  authored-source evidence.

These negative results are reusable. Do not repeatedly retry them without a
new compiler mechanism or materially new provenance.

## Boundary and ownership hazards

Use reviewed physical ownership, not raw Ghidra auto-function size, when
prioritizing work. MAINE payload `0xA847..0xADBB` is the resolved example:
v571 proved one `0x575`-byte owner even though Ghidra exposed only two small
ranges; v685 then reproduced the complete 1,397-byte body, the adjacent
64-byte compiler switch table, the complete `0xC3E` `CUTSCENE_TEXT` producer,
and all 559 ordered relocations with maintained natural C++.

The maintained reconstruction label is `script_op(unsigned char)`. Exact code
generation supports that source body and semantics, but it does not recover an
original ZUN debug symbol or comment spelling. Candidate history remains
corroboration; target boundary evidence, maintained source ownership, compiler
replay, and exact acceptance stay separate claims.

## Next work order

1. Current campaign order is **MAINE.EXE → OP.EXE → ZUN.COM**. Do not spend
   reconstruction time on `MAIN.EXE` in this campaign.
   v687 closes `cutscene_animate` at `0xADFC` (212 bytes), bringing MAINE to 43/72 function-level exact.
2. Continue MAINE with both large/medium owners and leaf functions. Select by
   reviewed physical spans and producer structure, not by Ghidra auto-size or
   by whichever candidate looks easiest.
3. For each promotion, independently re-check the target boundary and source
   assumption, then require natural-source codegen, complete producer bytes,
   ordered relocations, raw function equality, and the aggregate gate.
4. After the MAINE queue is materially reduced, apply the same process to OP.
   Only then move to ZUN source/origin and component ownership.
5. For ZUN, IDA-/disassembler-generated initial-state code and raw-equal
   generated assembly remain zero-credit provenance unless independent source
   ownership is established.

## Analysis/worktree hygiene

Ignored analysis output is disposable unless a checked-in script/config names
it as a required input. Current long-lived inputs include:

- `.analysis/targets/`;
- `.analysis/toolchain/`;
- `.analysis/ghidra/`, especially boundary exports/attestations;
- `.analysis/runtime/images/zun.hdi`;
- `.analysis/gpt-web/v401-master-vs-object-replay-001`;
- `.analysis/gpt-web/v402-opmusic-hybrid-replay-001`;
- `.analysis/gpt-web/v489-bgimage-hybrid-replay-003`;
- `.analysis/reconstruction/diet-replay/`;
- `.analysis/reconstruction/v218-th04-*-diet/`;
- `.analysis/reconstruction/probes/v546-zun-runtime-inventory-001`.

Some historical MAIN diagnostics still contain literal references to the old
`gptweb-v213-dialog-reloc-diagnostic-001` and
`gptweb-v214-demo-fixupp-diagnostic-001` exact-unit replay trees. Those expanded
worktrees are not present in the current analysis state and are not resume
prerequisites. Treat the command strings as historical provenance; intentionally
revisiting those diagnostics requires rebuilding or restoring the old snapshot
first.

Focused replay worktrees under `.analysis/reconstruction/probes/` are
rebuildable outputs unless explicitly retained above. Evidence paths are
provenance strings, not promises that expanded worktrees remain on disk. Use
`scripts/prune_analysis.py` in dry-run mode before applying cleanup.

The 2026-09-25 cleanup archived 1,699 probe `receipt.json` files before pruning
to `.analysis/reconstruction/receipt-archive/probes-cleanup-20260925.tar.zst`
(SHA-256
`2980355ea7a47db8fc7e6234900d7257b3998a93a9582b35caca3f515d32057f`).
It then removed 186 rebuildable probe worktrees plus interpreter caches. The
live probe root now retains only `v546-zun-runtime-inventory-001`; observed
`.analysis` usage fell from about 3.4 GiB to about 1.6 GiB. Pinned targets,
toolchains, Ghidra inputs/exports, runtime image, v401/v402/v489 snapshots, and
DIET inputs were preserved.

Finish a work session with:

```sh
python3 scripts/status.py
python3 scripts/ci.py
git diff --check
git status --short
```

Leave no untracked candidate source behind. If a candidate has not reached a
reusable probe/evidence checkpoint, delete it rather than letting a future
agent mistake it for maintained source.
