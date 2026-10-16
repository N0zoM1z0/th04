# TH04 current handoff

Updated 2026-10-17. Both full reconstruction/native goals remain active.
Start with [the actionable handoff](NEXT_AGENT_HANDOFF.md). This file is a
current index; historical experiment details remain in focused notes and Git.
All code/docs stay English. Use one low-priority CPU for heavy jobs; keep
launches muted/headless. Do not open Windows GUI, change focus or inject host keys.

## Original/reconstructed DOS Boss suffix (v1456)

The primary DOS comparison now reaches **9836 after-actor checkpoints**, with
loop samples I0..I9835 and 9835 complete update boundaries. Both independent
no-video and video pairs agree on configured scalar fields, all 5052 ordered RNG
calls (354 LCG/4698 ring), nine complete pools and 22 state blocks. The video
pair agrees on all 38 configured regions across all 9836 checkpoints: both
pages/all four graphics planes, full TRAM, palettes, modes and programmed GDC
fields. Each side's complete pool/state digests match its no-video control.

**Aggregate acceptance remains false:** no-video retains 302 post-reset input
differences, video retains 312, and complete raw GDC differs on all 9836 video
checkpoints. Across all four captures, complete initial/final CFG/SCR bytes agree; all ten
full 16-bit score checksums validate and real Continue changes decoded section 1.
The original and candidate use their own files/MAP/CS/DS. This is MAIN-only
replacement with original OP/MAINE/ZUN/assets, not a full four-product campaign.
Complete update 9836, Stage2 transitions, interior UI, physical timing, NP2,
Windows, pristine provenance and historical exactness remain open.

Source/capture/result/recovery details:
[original/reconstructed/native differential](reconstruction/product/TH04_REPLAY_DIFFERENTIAL.md).
Private proof root: `.analysis/reconstruction/probes/dos-boss-extent-v1456/`.
`result.json` deliberately remains `passed=false`; successful subgates do not
waive post-reset input or raw-GDC differences.

## Native current producer

Native source `d22e190`, published with later evidence commits on
`port/modern-64`, retains closure 565/533075c0 in
`.analysis/native/port64-recovery-v1445/`. Current frozen programs/cache are
`.analysis/port64/clock-phase-v1455-final/{gnu,ubsan}` inside that checkout.
GNU 87 programs/83 CTests and optimized UBSan 2 programs passed in v1455.

Its recorded elapsed display fixture matches all 59 complete RGB/TRAM samples
and 9835 selected updates, with real input/homing/nine pools/four Boss blocks,
Continue/full CFG-SCR and title/popup/2665 BB calls. Independent PIC time and
first display initialization predict all 9896 original phase/count samples.
Only elapsed ns enter native; an actual ignored-time producer is rejected.
Default logical mode still has three 407-pixel failures on that capture; the
older v1454 two-sample failure is unchanged. Natural OP/loader/UI-interior and
CPU/I/O clocks, every-frame pictures and physical scanout remain open.
See the same focused note and native `docs/port64/evidence/stage-lifecycle.md`.

## Available DOS producer and targets

Use `.analysis/build/dos-four-products-v1443/` for the retained same-run normal
four-product cohort. MAIN SHA is `778641ab845bcd67...`; MAP is
`.analysis/reconstruction/probes/product-20261016-065147-3427b48f-main/source/obj/main-native.map`.
The v1456 comparison replaces MAIN only. The old `.analysis/build/th04/` is not
the current validated cohort. Build future changes into a fresh `--output-dir`.
Only one Borland/Wine writer may run. No new exact promotion follows a build.

Pinned original Japanese executables are in `.analysis/targets/th04/` and
identified by `config/targets.toml`. Provenance is `candidate-local-attested`.
Before target work run preflight and attest the active database against the full
MZ/header/relocations/entry/module/sample bytes. A database view is not an
independent semantic Oracle. Historical byte exactness remains separate; MAIN's
two deferred exact cases stay deferred.

## Next bounded work

1. Measure the actual MAIN suffix after actor 9836, stage/frame reset and STD
   rebind, then extend original/reconstructed DOS and native Stage2 with each
   producer's own MAP/CS/DS. Do not change gameplay or observer ordering from a
   guessed stage boundary.
2. Diagnose the first post-reset input differences (no-video checkpoint 5,
   video checkpoint 48) against actual reset/IRQ/read ownership; preserve the
   302/312 vectors and
   raw GDC differences. Natural timing is not settled by equal consumed input.
3. Preserve the earlier four-source nine-entry/second-MAIN component result,
   its OP confirmation/readiness failure and missing-producer limitations.
   Complete process/campaign, native full original parity, NP2, Windows and
   physical audio/input/rendering remain required separate surfaces.

## Recovery and missing historical files

Sixteen owned capture image/font/raw aliases are archived in six blobs. Net
release is 157.621 MiB after archive, gzip and both journal files. The chain
verifies 24890 distinct protected hashes, including all 21663 parent
hashes and the two old public capture paths. New protected recipes use private
immutable copies. Actual archive restoration and fresh-output reducer replays
reproduce both failed state aggregates and the passing video regions before
SHA/mode/nsmtime verification and retirement of all sixteen aliases. No borrowed
files or duplicate cleanup credit. Use `replay_restored_v2.py --output-dir NEW`
for repeatable recovery; initial receipts, snapshots and replay remain unchanged.

For a fresh recovery replay from this DOS root:

```sh
python3 .analysis/reconstruction/probes/dos-boss-extent-v1456/replay_restored_v2.py \
  --output-dir .analysis/reconstruction/probes/NEW-suffix-recovery
```

The old `.analysis/worktrees/` directory is absent although Git registrations
remain. Native v1432 has 94 missing protected files; its archive cannot restore
the complete tree. Older v1437 candidate MAIN/MAP paths are also missing. Keep
those gaps explicit: do not recreate frozen directories, prune registrations,
rebind old receipts or count missing files as cleanup. The fresh native checkout
and current DOS cohort have independent identities.
