# TH04 `MAIN.EXE` initial authored screen

> **Historical routing snapshot.** This document records the initial screen that
> established the first 16 reviewed single-function extents. It is intentionally
> not rewritten as current progress. The later cold-replayed exact batch is
> documented in `TH04_MAIN_EXACT_BATCH.md`, while `../PROGRESS.md` and
> `config/th04_main_authored_functions.csv` contain the current reviewed
> denominators.


## Scope and method

This is a routing inventory, not a bulk source import or exactness claim. The
screen used the hash-attested Japanese `MAIN.EXE`, the attested headless Ghidra
database, and the locally cold-built pinned ReC98 candidate at revision
`b6ba5b0a529edbb31efdf8c0e939263804f8ee47`.

The candidate TLINK map was filtered to its 58 nonzero source-module code
contributions, excluding the large `th04_main.asm` placeholder and Borland
runtime modules. Each contribution was compared byte-for-byte against the same
load-module offset in the target. A read-only Ghidra inventory then checked all
module starts and counted function entries inside each extent.

The map remains upstream/compiler evidence. Raw alignment and Ghidra agreement
can prioritize and review a bounded target extent, but neither imports the
upstream source nor promotes any unit to exact.

## Results

| Measure | Result |
| --- | ---: |
| Screened module contributions | 58 |
| Screened bytes | 17,412 |
| Raw-identical contributions | 54 / 14,123 bytes |
| Contributions with differences | 4 / 3,289 bytes |
| Differences in those four contributions | 25 bytes |
| Ghidra function entries inside all spans | 151 |
| Complete single-function reviewed units | 16 / 1,446 bytes |
| Provisional module candidates | 42 / 15,966 bytes |

Of the 16 reviewed authored units, 15 have raw-identical candidate ranges.
`snd_load` has a complete target boundary but two candidate-byte differences.
Only `slowdown_frame_delay` currently has maintained repository source.

## Reviewed authored units

The Ghidra function body and candidate map contribution agree on the complete
extent for every row. These ranges enter the provisional authored denominator;
they do not count as exact.

| Unit | Target file | Load offset | Size | Candidate bytes | State |
| --- | ---: | ---: | ---: | --- | --- |
| `slowdown_frame_delay` | `0xC2F2` | `0xAAF2` | 26 | identical | source-present |
| `tile_ring_set_vo` | `0xCE82` | `0xB682` | 79 | identical | boundary-reviewed |
| `playfield_shake_update_and_render` | `0xE536` | `0xCD36` | 208 | identical | boundary-reviewed |
| `midboss4_render` | `0xE606` | `0xCE06` | 141 | identical | boundary-reviewed |
| `cfg_load_resident_ptr` | `0x13796` | `0x11F96` | 49 | identical | boundary-reviewed |
| `vram_planes_set` | `0x148EE` | `0x130EE` | 41 | identical | boundary-reviewed |
| `frame_delay` | `0x149B7` | `0x131B7` | 21 | identical | boundary-reviewed |
| `mpn_free` | `0x149EA` | `0x131EA` | 41 | identical | boundary-reviewed |
| `input_wait_for_change` | `0x14A13` | `0x13213` | 86 | identical | boundary-reviewed |
| `snd_pmd_resident` | `0x14B7E` | `0x1337E` | 46 | identical | boundary-reviewed |
| `snd_kaja_interrupt` | `0x14BDC` | `0x133DC` | 30 | identical | boundary-reviewed |
| `snd_determine_modes` | `0x14BFA` | `0x133FA` | 156 | identical | boundary-reviewed |
| `snd_load` | `0x14C96` | `0x13496` | 234 | 2 differences | boundary-reviewed |
| `game_exit` | `0x14E1E` | `0x1361E` | 72 | identical | boundary-reviewed |
| `marisa_flystep_pointreflected` | `0x18385` | `0x16B85` | 128 | identical | boundary-reviewed |
| `hud_hp_update_and_render` | `0x1B716` | `0x19F16` | 88 | identical | boundary-reviewed |

## Provisional module candidates

These 42 rows are retained as `candidate` with `origin=unknown`. Even a
raw-identical module remains outside the authored denominator until its
internal functions, data/padding, and ownership have been reconciled.

| Candidate module | Load offset | Size | Raw comparison | Ghidra entries |
| --- | ---: | ---: | --- | ---: |
| `th04/demo.cpp` | `0xB3EE` | 154 | identical | 2 |
| `th04/ems.cpp` | `0xB488` | 506 | identical | 3 |
| `th04/std.cpp` | `0xB6D1` | 232 | identical | 2 |
| `th04/circle.cpp` | `0xC64A` | 257 | identical | 4 |
| `th04/tile.cpp` | `0xCB2E` | 137 | identical | 6 |
| `th04/f_dialog.cpp` | `0xCE93` | 170 | identical | 4 |
| `th04/dialog.cpp` | `0xCF3D` | 2,383 | 12 differences | 13 |
| `th04/boss_exp.cpp` | `0xD88C` | 451 | identical | 2 |
| `th04/stages.cpp` | `0xEA8A` | 516 | 10 differences | 4 |
| `th04/player_m.cpp` | `0x10898` | 184 | identical | 1 |
| `th04/player_p.cpp` | `0x10950` | 56 | identical | 1 |
| `th04/hud_ovrl.cpp` | `0x10D4B` | 2,054 | identical | 10 |
| `th04/scoreupd.asm` | `0x11692` | 257 | identical | 0 |
| `th04/checkerb.cpp` | `0x12076` | 174 | identical | 1 |
| `th04/mb_inv.cpp` | `0x12124` | 51 | identical | 0 |
| `th04/boss_bd.cpp` | `0x12157` | 39 | identical | 0 |
| `th04/score_rm.cpp` | `0x12A0A` | 731 | identical | 7 |
| `th03/vector.cpp` | `0x13117` | 160 | identical | 2 |
| `th03/hfliplut.asm` | `0x131CC` | 30 | identical | 0 |
| `th04/mpn_l_i.cpp` | `0x13269` | 183 | identical | 2 |
| `th04/vector.cpp` | `0x13320` | 94 | identical | 2 |
| `th04/snd_mmdr.c` | `0x133AC` | 48 | identical | 1 |
| `th04/cdg_put.asm` | `0x13580` | 158 | identical | 1 |
| `th04/initmain.cpp` | `0x13666` | 78 | identical | 1 |
| `th04/cdg_p_na.cpp` | `0x136B4` | 102 | identical | 1 |
| `th04/cdg_p_pr.asm` | `0x1371A` | 130 | identical | 1 |
| `th04/input_s.asm` | `0x1379C` | 266 | identical | 2 |
| `th02/snd_se_r.cpp` | `0x138A6` | 12 | identical | 0 |
| `th04/snd_se.cpp` | `0x138B2` | 134 | identical | 2 |
| `th04/cdg_load.asm` | `0x13938` | 356 | identical | 5 |
| `th04/gather.cpp` | `0x13A9C` | 587 | identical | 8 |
| `th04/scrolly3.cpp` | `0x13CE8` | 74 | identical | 2 |
| `th04/motion_3.asm` | `0x13D32` | 32 | identical | 1 |
| `th04/vector2n.asm` | `0x13DF2` | 56 | identical | 1 |
| `th04/spark_a.asm` | `0x13E2A` | 204 | identical | 2 |
| `th04/grcg_3.cpp` | `0x13EF6` | 32 | identical | 1 |
| `th04/it_spl_u.cpp` | `0x13F16` | 156 | 1 difference | 3 |
| `th04/midboss.cpp` | `0x19EBC` | 90 | identical | 2 |
| `th04/mb_dft.cpp` | `0x19F6E` | 281 | identical | 3 |
| `th04/bullet_u.cpp` | `0x1C6CE` | 1,381 | identical | 5 |
| `th04/bullet_a.cpp` | `0x1CC33` | 2,139 | identical | 20 |
| `th04/boss.cpp` | `0x1E5D8` | 831 | identical | 7 |

## Difference routing

| Module | Relative differing offsets | Difference count | Next question |
| --- | --- | ---: | --- |
| `dialog.cpp` | `0xA1..0x131` | 12 | Split the first affected functions and test source/flag shape. |
| `stages.cpp` | `0x0F..0x3F` | 10 | Isolate the first function and inspect constants/branch encoding. |
| `snd_load.cpp` | `0xC1..0xC2` | 2 | Review the one localized word without changing its accepted boundary. |
| `it_spl_u.cpp` | `0x0B` | 1 | Compile a minimal source-shape probe for the first function. |

Private query receipts used during this screen are under
`.analysis/reconstruction/authored-screen/`. The complete function list has
SHA-256 `862cf70cc171b66dfa45822a3beaedaf4fdbd071eb3ce41871e23b1a9f94bcbb`;
the 58-start function metadata report has SHA-256
`a214b78f40f3c2437e73b4dbeec200f0b5983ed5892ac689323c1b5b432436ae`.
