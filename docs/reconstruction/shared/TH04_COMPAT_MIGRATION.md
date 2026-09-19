# TH04 compatibility dependency migration

This is the reusable recipe for removing `compat/rec98/` dependencies from
TH04 product source while preserving exact replay. Product paths and public
types use TH04 concepts. Use `src/shared/` only for declarations shared by two
or more TH04 artifacts.

Old game paths may remain in replay manifests as identities from the pinned
ReC98 scaffold. They must not become product interfaces under `src/`.

## Current baseline

The migration reduced the boundary from 43 forwarders and 261 include sites in
138 product files to **17 forwarders and 20 include sites in 19 files**. The
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

The latest complete proof is
`.analysis/reconstruction/exact-unit-replay/gpt-web-bb-aggregate-001/receipt.json`
(SHA-256
`c3512f416504c122fae23b9c57a3ac23f4d72c47069c05eb6360edae67ad6ef2`).
It builds twice and keeps all 253 selected MAIN owners raw, MAP, relocation,
and OMF exact. This validates the exercised declarations; it gives no exact
credit to unused API declarations.

## Latest completed batch

The BB batch replaces all six maintained direct uses of
`th04/formats/bb.h` with the MAIN-owned `src/main/formats/bb.hpp`.
This includes the two remaining compatibility-forwarder sites and four
same-game scaffold-path includes. The local interface preserves
`BB_SIZE=2048`, the 8-bit `bb_tiles8_t` element type, segmented boss
storage, the GAME5 near versus GAME4 far distance of `bb_boss_free()`, and
the original `bb_txt_put_8()` register/evaluation order.

The pinned scaffold header `th04/main/tile/bb.hpp` also includes the old
BB header transitively. Exact replay therefore uses one
`scaffold_header_rewrites` entry bound to source SHA-256
`ffb1a3f9e522e4c94680e43ca20468430630f574e237acf83234ef8df42a59ad`; this keeps the rewrite confined to that attested header
rather than applying a broad tree substitution. The historical
`boss_prefix.inl` localized fragment gets an explicit include mapping.

Focused two-cold replay passes for `th04-main-bb-txt-v104`
(receipt SHA-256 `5a241539abd9d24d49699e02233ebc95ec8fab7c3659de715298d463603f8029`) and
`th04-main-module-th04-hud-ovrl-cpp-10d4b`
(receipt SHA-256 `08fa27b086507da1d9f02fdd7baabd53fd5f3b4f967944f3b2a9c0e561e0a2b8`). The complete
`gpt-web-bb-aggregate-001` replay passes all 253 default MAIN owners twice
with `failures=[]` and includes all seven affected exact owners, including
the bomb core and both Yuuka6 background owners. Both candidate MAIN images
remain SHA-256 `54b8dc13865db10ab39e4ee0edf1a92346463d1b19cf8a792fde39b562bbc0d6`. The compat audit moves from 18 forwarders /
22 sites / 21 files to 17 / 20 / 19, with no missing, orphan, invalid, or
direct forbidden include. No new exact owner is claimed.

## Next families

Run `python3 scripts/audit_compat_dependencies.py --json` for exact source and
line locations. The next bounded families are:

| Forwarder | Sites | Product files |
| --- | ---: | ---: |
| `th04/main/enemy/size.hpp` | 2 | 2 |
| `th05/main/boss/boss.hpp` | 2 | 2 |
| `th05/sprites/main_pat.h` | 2 | 2 |

The remaining fourteen families have one site each. Re-run the audit instead
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
