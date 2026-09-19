# TH04 compatibility dependency migration

This is the reusable recipe for removing `compat/rec98/` dependencies from
TH04 product source while preserving exact replay. Product paths and public
types use TH04 concepts. Use `src/shared/` only for declarations shared by two
or more TH04 artifacts.

Old game paths may remain in replay manifests as identities from the pinned
ReC98 scaffold. They must not become product interfaces under `src/`.

## Current baseline

The migration reduced the boundary from 43 forwarders and 261 include sites in
138 product files to **0 forwarders and 0 include sites in 0 product files**.
The audit reports zero missing, unused, invalid, and direct forbidden includes;
`python3 scripts/audit_compat_dependencies.py --require-zero` passes.

| Batch | Localized boundary | Forwarders after | Code commit |
| --- | --- | ---: | --- |
| Leaf declarations | VRAM planes, bullet sizes, init/exit, frame delay, entity, game exec level, polar math | 34 | `26e1bcd` |
| Runtime and graphics | master runtime API and PC-98 graphics API | 32 | `389d4ff` |
| Randring and GRCG | random-ring state/ranges and all GRCG adapters | 28 | `6a15a28` |
| CDG and resident | CDG format API and resident/score layout | 26 | `52cb7b3` |
| Overlap, sound, and shot | overlap predicates, KAJA/sound API, player-shot layout | 23 | `bd61cce` |
| Palette | deferred palette-tone latch and MAIN palette-change declaration | 22 | `e19539d` |
| Playchar | GAME4/5 play-character enum ABI used by shared maintained TUs | 21 | `777b8cf` |
| Rank | rank enum width/constants and MAIN rank selector declaration | 20 | `8005fee` |
| PI | shared PI slots, load/free/display API, row-pointer macros, and GAME-dependent call ABI | 19 | `40ccff5` |
| Tile | shared tile/file-format dimensions and GAME4+ ring-storage width | 18 | `ca98da6` |
| BB | TH04 .BB size/type/segment ABI, text-dissolve helpers, and pinned tile-BB include rewrite | 17 | `0b6bfaf` |
| Enemy size | MAIN enemy and kill-box dimensions used by enemy/midboss code | 16 | `f1884f4` |
| Main pat | bounded GAME4/5 sprite-pattern subset used by maintained explosion/bullet code | 15 | `e726a05` |
| Polar | TH04 polar helper plus consumed unsafe trig-table offset helpers | 14 | `2e871dd` |
| Subpixel | existing TH04 Q12.4 interface reused by the CIRCLE_TEXT scroll helper | 13 | `ff84251` |
| Bullet add impl | ring-group switch macro actually consumed by TH04 bullet/add.cpp | 12 | `1000bb7` |
| HUD metrics | HUD_LEFT geometry consumed indirectly by playfield clipping macros | 11 | `dfdbf1d` |
| Item overflow | power-overflow limit and signed bonus table used by the MAIN item producer | 10 | `b1fbe04` |
| Midboss state | GAME4 midboss_active flag used by the stage script runner | 9 | `a136f71` |
| Scroll state | GAME5 scroll_line declaration used by shared playfield shake source | 8 | `d5a5d3d` |
| Sound impl | shared SE/load helpers plus hash-bound fragment include transforms | 7 | `fc6c1cb` |
| Sound measure | KAJA measure wrapper and MMD quarter-note timing constant | 6 | `9d56bf1` |
| CFG loader | shared GAME3/4 resident-pointer loader with target-specific cfg layouts | 5 | `8d0f544` |
| MAP format | packed TH04 map header/section layout without legacy planar dependency | 4 | `572482e` |
| Thicklaser ABI | target-verified four-byte post-origin padding and maintained laser state layout | 3 | `0b27b64` |
| Homing state | single TH04 SPPoint target declaration used across player/enemy/boss code | 2 | `3c6c9a7` |
| Faceset filenames | conditional GAME4/5 faceset-loader macro with exact filename byte case | 1 | `ee3dbfd` |
| Boss base | common TH04 boss ABI used by GAME4 source and GAME5 calibration | 0 | `510be3b` |

The latest complete proof is
`.analysis/reconstruction/exact-unit-replay/gpt-web-boss-base-aggregate-001/receipt.json`
(SHA-256
`d4289749d75a3b7efcefd9330b83348bd0a206374d4d6d0c6209608b556faa00`).
It builds twice and keeps all 253 selected MAIN owners raw, MAP, relocation,
and OMF exact. This validates the exercised declarations; it gives no exact
credit to unused API declarations.

## Latest completed batch

The boss-base batch removes the final compatibility forwarder,
`compat/rec98/th05/main/boss/boss.hpp`. The recovered
`src/main/boss/boss.hpp` is byte-identical to the pinned TH04 base header
(SHA-256
`51828ba1008dd4b2523352b4a4b3bae8756f2d0d9831f749e16dc67dc9c3085e`).
All 86 maintained consumer files / 89 include lines now use that local path.
The historical `boss_prefix.inl` localized fragment maps its two occurrences
explicitly back to the TH05 wrapper and TH04 base scaffold includes; product
source itself no longer includes either legacy path.

Focused two-cold replay passes for the main035 boss TU (receipt SHA-256
`01bd28013703d1c0737b3bbea2eef84639af908707a7cfae25e20424a61360ff`),
the fused Yuuka6 producer (receipt SHA-256
`dc0a43c2f48af09699b1a67bb45e56181f46ea02196f3629bfbd0d4eeb82aa32`),
and the midboss HUD/defeat TU (receipt SHA-256
`73ce7e3c9a1ae2529c5814f96825e863b7c7bda7259e77cb0814912cc04a343c`).
A pinned PC-98 IDE GAME5 A/B probe uses only the common boss ABI consumed by
the maintained GAME5 branches; all 23 semantic OMF records are byte-identical
after excluding dependency/producer COMENT and LINNUM metadata. Probe receipt
SHA-256 is
`1d296c07acb0eec86546d350d16f08fcf79bd1a7622ddb686c123bd72f2eddb7`.
The TH05-only `boss2`, flystep, and sprite-callback declarations are not needed
by those maintained sources.

The complete `gpt-web-boss-base-aggregate-001` replay passes all 253 default
MAIN owners twice with `failures=[]`; both candidate MAIN images remain
SHA-256 `54b8dc13865db10ab39e4ee0edf1a92346463d1b19cf8a792fde39b562bbc0d6`. The compatibility audit reaches 0 forwarders / 0
sites / 0 product files, and the strict `--require-zero` gate passes. This
completes the `compat/rec98` forwarding migration; it does not by itself prove
complete reconstructed source coverage or whole-artifact standalone rebuilds
for every TH04 executable. No new exact owner is claimed.

## Next families

None. The compatibility forwarding boundary is closed. Keep the final
`--require-zero` audit in the packet gate so future source changes cannot
silently reintroduce a forwarder dependency.

## Migration workflow

1. Establish a clean baseline.

   ```bash
   python3 scripts/preflight.py
   python3 scripts/audit_compat_dependencies.py --check
   python3 scripts/audit_compat_dependencies.py --json > .analysis/compat-before.json
   ```

2. Choose one bounded declaration family. Put MAIN-only declarations below
   `src/main/`; use the owning artifact directory for OP, MAINE, or ZUN. Use
   `src/shared/` only with evidence of sharing inside TH04.

3. Recover the smallest complete interface. Preserve integer and enum widths,
   packing, memory distance, calling convention, declaration order, and inline
   evaluation order. Product APIs must not retain another game's identity.

4. Change every product include in the family and delete the now-unused
   forwarder. The audit must still report zero missing, unused, invalid, and
   direct forbidden includes.

5. Adapt exact replay only where the pinned scaffold needs it:

   - Full translation-unit overlays automatically copy the frozen local header
     closure.
   - Maintained fragments with changed include lines use
     `source_mode = "localized-fragment"` and explicit mappings:

     ```toml
     source_mode = "localized-fragment"
     scaffold_include_mappings = [
       { local = "src/main/subsystem/header.hpp", scaffold = ["old/header.h"] },
     ]
     ```

     Add a one-based `occurrence` when the same include appears in multiple
     branches. One local include may map to several old scaffold includes.
   - Use a hash-bound `[[scaffold_header_rewrites]]` for one unchanged pinned
     TH04 header that still names the old include.
   - Use `[[scaffold_tree_include_rewrites]]` only for a high-reach include
     confined to the pinned `th04/` tree. First prove another artifact's
     calibration does not consume those files.

6. Run the narrow replay, audit, and complete default aggregate.

   ```bash
   python3 tests/test_exact_replay.py Rec98CompatTests
   python3 scripts/replay_th04_main_exact_units.py \
     --unit UNIT_ID --run-id AGENT-BATCH-focused-001
   python3 scripts/replay_th04_main_exact_units.py \
     --run-id AGENT-BATCH-aggregate-001
   python3 scripts/audit_compat_dependencies.py --check
   python3 scripts/ci.py
   git diff --check
   ```

7. Record the before/after counts, local headers, ABI facts, replay adaptations,
   affected artifact, focused result, aggregate receipt and hash, and remaining
   uncertainty. A successful compile alone is compiler evidence.

## Handoff packet

```text
Batch:
Old forwarders:
TH04-owned headers:
Product include sites changed:
ABI facts preserved:
Replay manifest adaptations:
Focused command/result:
Aggregate command/result/receipt SHA-256:
Audit before -> after:
Remaining uncertainty:
Next self-contained family:
```

The final standalone source gate is:

```bash
python3 scripts/audit_compat_dependencies.py --require-zero
```
