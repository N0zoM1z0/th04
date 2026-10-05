# Native bullet drawing and dense-pool controls

The user reports the preceding planar batch improves the title, Ending and
Yuuka crosses, with no remaining gameplay bugs and little slowdown in Extra.
Those are Windows playtest observations, not automated route acceptance.
This batch reduces native pellet/tiny-sprite drawing cost and measures a
bounded Lunatic/full-pool fixture. Historical exact branches remain separate.

## Ownership and change

The pinned MAIN target passes preflight and the current Ghidra database
attestation. Canonicality remains `candidate-local-attested`. Historical
owners are MAIN `0AAF:193A`, file `DC2A`, size `220h` (tiny-sprite pair and
private word), and `0AAF:1EAC`, file `E19C`, size `FCh` (pellet pair and EVEN).

Only `TH04_LARGE_PRODUCT` emits the new fixed-row paths. Nonrolling pellet
top/bottom, 16x16 sprites and 32x32 clouds avoid row-loop bookkeeping; the
32x32 paths also inline their row helper and two-word loop. Rolling paths
retain the existing branches. Every conditional byte/word mask write, color
port event, source step and Pascal near/far return is preserved. The pellet
bottom path still repeats its first source word. There is no new GRCG mode,
EGC mode, redraw omission, bullet-cap change, motion change or slowdown policy.

The initial fast MAIN is 199,455 bytes, SHA-256 `cb4c5b66…`, versus 193,983
bytes `149c1e77…`. Its relative MAP entries are tiny32 `0708:1274`, tiny16
`0708:2558`, pellet top `156A:3130`, bottom `156A:3206`. These are native
addresses, not target addresses. The full near groups remain within 64 KiB;
link, IRQ/renderer-CS and all 14 bullet-switch destinations pass.

## Independent CPU controls

`probe_th04_native_bullet_load.py` executes complete relocated MAIN calls at
load segment `2000h`, with a hashed Unicorn engine. Scalar pixel models
independently check color-mask layers and pellet masks, while old/new calls
must retain their ordered VRAM writes and GRCG port events. Its 3,604 cases
cover all eight X shifts, both byte parities, empty/full/random masks, both
tiny sizes, rolling boundaries, all 400 pellet rows and complete pools from
zero through the actual cap: 240 pellets plus 200 regular bullets, stride 26.

The separate model calibration runs both sides against the old product first.
The final old/new receipt is
`.analysis/reconstruction/probes/bullet-load-kernels-v1235/receipt.json`,
SHA-256 `efbe6897…`. All cases pass. At full pool with Turbo enabled:

| Fixture | Update instructions, old/new | Render instructions, old/new |
| --- | ---: | ---: |
| Regular pool | 28,783 / 28,783 | 150,852 / 130,641 |
| Pool with 200 clouds | 26,783 / 26,783 | 797,461 / 624,250 |

These are 13.40% and 21.72% less drawing work, not measured Windows FPS.
An additional seeded high-EAX/EDX replay compares all volatile register and
flag outputs over 13,568 tiny/pellet calls; it also passes, including rolling
paths. The private register control uses the final normal build.
Lunatic rank, Turbo and the deliberate bullet-count slowdown remain equal;
the previous independent original/native 96-case policy control is retained.

## Actual PC-98 timing fixture

`--bullet-load-trace` overlays copied source only. Six phases buffer 192
fourteen-word records without per-frame file/debug output, then write
`BLOAD.BIN`. They seed zero, 120, 340 and 440 stationary bullets, 440 with
200 clouds, and 440 decay sprites. Actual loaded game masks, scrolling
background, GRCG and physical emulator IRQ callbacks execute. Rank is forced
to Lunatic and Turbo is enabled, with collision suppressed. Reseed cost is
recorded separately. The exporter rejects this diagnostic as a playable build.

The scenario is `config/runtime/scenarios/main_bullet_load.json`. The pinned
Linux DOSBox-X is `30a5fdf8…`, normal core, auto CPU, mixer enabled, at fixed
24,000 cycles. The true baseline uses the two complete renderer sources from
`55c4617`; all C++/state/sprite link-relevant OMF records agree with the new
fixture, and only the two renderer ASM objects differ. These are recorded
under `.analysis/reconstruction/probes/bullet-pc98-before-v1235-verified/`.

At 24,000 cycles, 440 ordinary bullets retain a mean one logical refresh
period per fixture frame on both versions. The artificial all-cloud phase
uses 43 render IRQ ticks over 32 frames before, 34 after; consecutive frame
spacing averages 1.742 periods before and 1.452 after. This quantized,
instrumented comparison supports a bounded improvement and also shows that
an extreme cloud load can still exceed the frame budget. It does not prove
a complete natural Lunatic route, another emulator, Windows dynamic-core FPS
or general audio/timing equivalence.

With only the after-fixture CPU budget raised to 36,000, all six phases
average one logical refresh period per frame, including the full cloud pool.
The cloud phase consumes 32 render IRQ ticks over 32 frames. Receipt:
`.analysis/runtime/candidates/bullet-load-after-v1235/run-36000/`.

Receipts and independent reducers:

```text
.analysis/runtime/candidates/bullet-load-before-v1235-verified/run-24000/
.analysis/runtime/candidates/bullet-load-after-v1235/run-24000/
python3 scripts/probes/inspect_th04_bullet_load_trace.py --run-dir RUN
```

An early private baseline accidentally used the current pellet body because
the body wrapper reread the checkout instead of its copied source. That run
is a mixed-renderer control, not the true baseline. The builder now reads and
hashes staged assembly, including generated sprites. An early inserted
bullet header also changed twelve near callback fixups; fixture helpers now
follow the existing fused session initializer's declarations. Rejected
diagnostics were never exported. These are useful compiler/provenance hazards.

## Host CPU budget

The Windows package uses dynamic core, Pentium and fixed 24,000 cycles. The
host reports i9-13900H, 14 cores/20 logical processors. DOSBox-X's official
[CPU guide](https://github.com/joncampbell123/dosbox-x/wiki/Guide%3ACPU-settings-in-DOSBox%E2%80%90X)
says extra host cores do not increase emulation speed. Increasing the fixed
guest budget is a separate option and preserves the game's VSync waits;
`max`/fast-forward are not a tested replacement.

The exporter provides `start-th04-normal-highcpu.bat` and
`start-th04-highcpu.bat`, setting only `cpu cycles=36000` for their respective
existing saved images. Standard launchers remain at 24,000. Host-specific
Windows gameplay/audio validation remains separate from Linux fixture timing.

## Historical and product gates

`check_th04_bullet_default_objects.py --baseline-revision 55c4617` compares
complete link-relevant OMF for the old source and two fresh current assemblies
without `TH04_LARGE_PRODUCT`. Both owners are identical. The full historical
exact driver instead stops before compilation on the existing
`th04-main-items-invalidate-v185-layout` scaffold digest check. Its failed
attempt is `.analysis/runtime/bullet-kernels-v1235-exact.log`; no full cold
target/aggregate pass or new exact promotion is claimed.

Final normal and invincible MAIN/OP/MAINE are rebuilt serially through the
dependency-verified fast path. Unchanged ZUN's cold source/packing receipts,
37 component-source/build-driver hashes and product hash are rechecked; its
source does not depend on the changed input/VSync or bullet owners. See
`.analysis/reconstruction/probes/bullet-zun-retention-v1235/receipt.json`.
The independent original/native slowdown replay again passes 96 cases.

The final uninstrumented normal build reaches visible Lunatic combat at
125 seconds in the same pinned Linux emulator, with all four executed image
products and configuration checks verified. This smoke checkpoint does not
clear a route or establish its frame rate. Receipt:
`.analysis/bullet-v1235/normal-smoke-attestation.json`.

Both final variants are exported to
`D:\Entertainment\Game\Touhou\th04-reconstruct`. Readback verifies the products
against their build and package receipts. Only MAIN.EXE changes in either saved
image; all fourteen nonproduct GENSO files, including configuration and scores,
remain byte-identical. Standard profiles remain at 24,000 cycles and the optional
36,000-cycle launcher bytes are hashed in each package receipt. Final MAIN hashes
are normal `cb4c5b66…` and invincible `0d99bc5a…`; OP/MAINE/ZUN agree between
variants. See `.analysis/bullet-v1235/windows-export-receipt.json`.

Final `python3 scripts/validate_tracking.py`, `python3 scripts/ci.py` and
`git diff --check` pass. CI output is `.analysis/bullet-v1235/ci-final.log`;
the separately recorded historical exact replay failure above remains a limit.
