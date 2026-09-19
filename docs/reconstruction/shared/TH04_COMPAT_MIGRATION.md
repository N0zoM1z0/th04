# TH04 compatibility dependency migration

This is the reusable recipe for removing `compat/rec98/` dependencies from
TH04 product source while preserving exact replay. Product paths and public
types use TH04 concepts. Use `src/shared/` only for declarations shared by two
or more TH04 artifacts.

Old game paths may remain in replay manifests as identities from the pinned
ReC98 scaffold. They must not become product interfaces under `src/`.

## Current baseline

The migration reduced the boundary from 43 forwarders and 261 include sites in
138 product files to **5 forwarders and 6 include sites in 6 files**. The
audit reports zero missing, unused, invalid, and direct forbidden includes.

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

The latest complete proof is
`.analysis/reconstruction/exact-unit-replay/gpt-web-cfg-impl-aggregate-001/receipt.json`
(SHA-256
`246373a243c353fb813ea8846743b34328be8ad311645f50b9d7ceafcbc52e7d`).
It builds twice and keeps all 253 selected MAIN owners raw, MAP, relocation,
and OMF exact. This validates the exercised declarations; it gives no exact
credit to unused API declarations.

## Latest completed batch

The CFG-loader batch removes `compat/rec98/th03/formats/cfg_impl.hpp` from
`src/main/config/load_resident_ptr.cpp` and replaces it with
`src/main/config/load_resident_impl.hpp`. The maintained source is genuinely
shared by the GAME3 and GAME4 build paths, but not GAME5; the local header
therefore preserves exactly those two producer contexts rather than importing
the complete historical TH03 configuration API.

For GAME4, the helper uses the already-attested `src/shared/config/cfg.hpp`
10-byte file layout. For GAME3, it declares only the compact calibration
`cfg_options_t` and `cfg_t` needed by this producer. The previous cold GAME3
`cfg_lres.obj` directly emits `ENTER 8,0` and pushes 8 as the `file_read` size,
proving `sizeof(cfg_t)==8`; the observed field order fixes the options prefix
at five bytes. The local runtime file declarations preserve master.lib's
large-model far-Pascal return convention and far filename pointer.

The exact TH04 `th04-main-cfg-load-resident-ptr` owner passes focused two-cold
replay (receipt SHA-256
`bb6e94169f00dc0aaf4bc19d41428c4a932d820a1aad4fae5ce6f4fb6d3faf31`).
Separately, the actual old and new GAME3 cold-build `cfg_lres.obj` files have
11 byte-identical semantic OMF records after excluding dependency/producer
COMENT and source-line LINNUM metadata; the semantic receipt SHA-256 is
`6bbcdc04b3e6e27fb285dc702f790c3dfce8b9b650c79a62d76528c2995310b9`.
The complete `gpt-web-cfg-impl-aggregate-001` replay passes all 253 default
MAIN owners twice with `failures=[]`; both candidate MAIN images remain
SHA-256 `54b8dc13865db10ab39e4ee0edf1a92346463d1b19cf8a792fde39b562bbc0d6`.
The compat audit moves from 6 forwarders / 7 sites / 7 files to 5 / 6 / 6,
with no missing, orphan, invalid, or direct forbidden include. No new exact
owner is claimed.

## Next families

Run `python3 scripts/audit_compat_dependencies.py --json` for exact source and
line locations. The next bounded families are:

| Forwarder | Sites | Product files |
| --- | ---: | ---: |
| `th05/main/boss/boss.hpp` | 2 | 2 |

The remaining four families have one site each. Re-run the audit instead
of copying this queue once another batch lands.

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
