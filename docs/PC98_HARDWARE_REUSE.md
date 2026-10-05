# PC-98 hardware fixes and performance reuse

This guide routes verified TH04 patterns for another PC-98 reconstruction.
Do not copy a mode, ABI, address or optimization into another game without
re-attesting its target and testing the corresponding contract. `native` in
older DOS notes means the standalone **16-bit PC-98** source product;
`port64` means the separate host x64 product.

## Separate the evidence layers

- Pinned Japanese targets are `candidate-local-attested`; provenance is not
  independently pristine. Target instruction observations are artifact-local.
- Historical exact acceptance requires the complete configured extent,
  relocations/layout and cold aggregate replay. Function counts are not
  original packed-file equality. See [progress](PROGRESS.md).
- `TH04_LARGE_PRODUCT`/product branches repair or optimize the standalone game;
  those whole executables may differ from targets. Preserve default exact
  branches and record their before/after OMF/raw controls separately.
- A CPU model with ordinary RAM or emulated device hooks is a bounded Oracle.
  An actual emulator checkpoint, manual Windows route and physical PC-98
  observation have different scopes. No physical-hardware validation is claimed.

## Confirmed repairs and reusable checks

| Surface | Verified finding and repair | Evidence / reuse route |
| --- | --- | --- |
| EGC tile copy | Pattern-register VRAM copy requires mode `3100h` in this owner. Old `2300h` broadcasts blue into all four planes. All 600 initial tiles match after repair. Target MAIN MAI_TEXT `0AAF:212C`, file `E41Ch`. | KB `th04-main-native-egc-copy-mode-v1152`; `inspect_th04_main_graphics_trace.py`; `src/main/tile/render_all.asm` |
| C++ code groups / CS | Grouped far callers can use a different CS frame from ASM `OFFSET` labels. IRQ/PAR providers and self-modifying renderers need independent native frames plus actual linked-caller audits. TLINK success is insufficient. | [IRQ/BGM](reconstruction/product/TH04_NATIVE_BGM_V871.md); KB `kb-th04-native-cs-and-score-return-v1178`; `audit_th04_native_irq_vectors.py` |
| Ending CDG corruption | Deployed native MAINE `0703` callers wrote four operands into the PI decoder instead of their CDG kernels. Independent native CDG frames repair the destinations; actual calls at loads `2000h/6000h` return with aligned plane bytes. | [Ending CDG](reconstruction/product/TH04_NATIVE_ENDING_CDG_CS_V1230.md); KB `th04-native-ending-cdg-cs-v1230`; `probe_th04_native_cdg_cs.py` |
| Bullet switch tables | Compiler-generated segment-relative tables disagreed with a group-CS far caller. Native TU declares both `BULLET_U_TEXT` and `main_03`; all 14 destinations pass a publication gate. | KB `kb-th04-native-bullet-switch-cs-v1199`; `audit_th04_native_bullet_switches.py` |
| Word versus dword clear | `XOR AX,AX; REP STOSD` retains high EAX. At native MAIN load `1100h`, `0708:1178` / guest `1808:1187` writes `000E0000`, creating 220 nonzero bullet flags and 120 coincident pellets. Product-only full EAX clear repairs it. | [Corner/state clear](reconstruction/product/TH04_NATIVE_STATE_CLEAR_V1231.md); KB `th04-native-state-clear-fix-v1233`; 54 calls and seven ordinary checkpoints; two cold default objects retain all 22 target bytes |
| DOS overlay memory | OP's temporary four-paragraph palette block split free memory before `execl`, causing ENOMEM=8 despite a larger free block elsewhere. Release it before overlay. | KB `kb-th04-op-native-overlay-palette-v1162`; OP source and startup/memory evidence |
| Far calls / Pascal cleanup | Far CALL to a near-return routine, or linker-relaxed far callbacks with the wrong frame, can link successfully. Check actual decoded target, relocation, caller CS and RET/RETF immediate. | [Far ABI](reconstruction/product/TH04_NATIVE_FAR_CALL_ABI_V856.md), [BGM](reconstruction/product/TH04_NATIVE_BGM_V871.md); `audit_th04_native_{maine,op}_call_abi.py` |
| PI slot ownership | Free left a stale slot pointer; a subsequent load could free a reallocated block. Product free clears the owner pointer first. This was a separate hazard and did not by itself fix Ending. | [PI lifetime](reconstruction/product/TH04_NATIVE_PI_SLOT_LIFETIME_V1224.md); KB `th04-native-pi-slot-lifetime-v1224`; load/free/load/free DOS control |
| Zero ring count | Actual Kurumi Easy fault reaches ring IDIV with count zero after cumulative reductions. Product-only empty-ring skip repairs the rejecting scenario; default owner remains byte-preserved. | KB `kb-th04-main-empty-ring-v1216`; target file `1E612h`; ordinary repaired Stage 3 entry and cold 2,139-byte owner controls |

Script names above are under `scripts/probes/`; use the
[hardware script catalog](../scripts/catalog/hardware.md) and
[all categories](../scripts/README.md) for full paths/purposes. Stable evidence
IDs in `config/knowledge.csv` link the corresponding `config/evidence.csv`
observations. Rediscover **native** addresses from each actual product MAP.

## Performance batches and their measured limits

| Batch | Preserved contract | Measured result | Limit |
| --- | --- | --- | --- |
| BFNT masked-byte composition | Original mask/color planes, clipping, background and GRCG-off effect; one destination-byte composition, opaque overwrite, interval clipping | DOS hashes and randomized placements agree; recorded Linux OP reaches title earlier | No general Windows FPS or timing equality |
| Word sprite/copy + PI pair lookup (v1233) | One shifted alpha row shared by planes, empty-row skips, even-word composition/byte carry at column 79, old clipped path; copy keeps odd tail/DF/segments/page switches; format-derived pair table keeps hidden row 400 | 460 scalar-pixel/ABI controls; complete 31-cross renderer 1,063,853 → 343,020 instructions with identical four-plane pixels | Synthetic CPU cost; not natural late-attack frame pacing |
| Fixed-row pellet/tiny paths (v1235) | Nonrolling row expansion only; rolling paths, all masks/source steps, ordered VRAM writes/GRCG ports and returns retained; unchanged update/slowdown logic | 3,604 controls; full regular pool draw 150,852 → 130,641 instructions (13.40%); 200-cloud pool 797,461 → 624,250 (21.72%) | No bullet-cap/motion/skip-redraw changes; no Windows FPS claim |
| Dense PC-98 fixture | Actual loaded masks/scrolling/GRCG/IRQ callbacks; stationary Lunatic/Turbo pool up to 240 pellets + 200 bullets, buffered instrumentation | Linux DOSBox-X 24,000 cycles: all-cloud spacing 1.742 → 1.452 refresh periods; at 36,000 all six after-phases average one period | Instrumented stationary fixture, not natural complete Lunatic or host audio validation |

Detailed producers/negative controls:
[sprite/planar note](reconstruction/product/TH04_NATIVE_SUPER_SPRITE_V870.md),
[bullet load note](reconstruction/product/TH04_NATIVE_BULLET_LOAD_V1235.md).
The early dense-pool baseline accidentally reread current pellet source;
that mixed build is rejected. The repaired producer hashes staged ASM inputs.

```sh
python3 scripts/probes/probe_th04_native_planar_kernels.py --help
python3 scripts/probes/probe_th04_native_bullet_load.py --help
python3 scripts/probes/inspect_th04_bullet_load_trace.py --help
python3 scripts/probes/check_th04_bullet_default_objects.py --help
```

Use the documented baseline manifests and fresh private output directories.
Some historical captures require archive restoration; `--help` is discovery,
not a successful replay. Full historical bullet aggregate replay stops before
compilation at a stale items-invalidate scaffold digest; cold default OMF
continuity does not waive that failure or promote exactness.

## Timing and display policies to carry across ports

- Keep plane order and MSB-first bit placement explicit; distinguish packed
  pixels, source bytes, VRAM bytes, words, rows and screen coordinates.
- Treat GRCG/EGC mode/register order, page access/show changes and interrupts
  as observable effects, including off-screen/empty calls. Preserve calling
  registers, DF, near/far returns and stack cleanup separately from pixels.
- `graph_copy_page(destination)` copies the opposite page and leaves destination
  access. BGIMAGER uses its observed `h+1`; the MAINE registration name restore
  uses exactly `h`, byte-rounded X and word-rounded width. Do not generalize
  one rectangle helper into another.
- PI/BFNT raw palette order and DAC RGB channels are distinct. Derive lookup
  tables from the format, not copied target output buffers.
- VSync interrupt counters and GDC polling are separate lifecycles. Verify
  vector install/restore and the actual group/segment of CS-resident state.
- Generic bullet-count slowdown has a 96-case original/native CPU control;
  Turbo suppresses that policy. The Yuuka cross helper has no direct special
  player-speed write. A lag report still needs actual Turbo/Shift/frame timing.
- Windows's optional 36,000-cycle launchers change guest budget, not gameplay
  policy. Natural route/audio validation remains TODO. Existing Linux controls
  use normal/Pentium. Multi-core host CPU utilization is not a verified source
  optimization; preserve a measured frame budget before changing emulator setup.

See [scroll](reconstruction/product/TH04_NATIVE_SCROLL_BOX_V858.md),
[VSync](reconstruction/product/TH04_NATIVE_VSYNC_V864.md),
[page copy](reconstruction/product/TH04_NATIVE_GRAPH_COPY_V862.md),
[packed rows](reconstruction/product/TH04_NATIVE_PACK_PUT_V866.md),
[gaiji](reconstruction/product/TH04_NATIVE_GAIJI_TEXT_V860.md).

## What remains unproved

- The Stage 6 stripe disappeared after scroll initialization changes according
  to the user; causality remains inferred. Preserve this distinction from the
  confirmed EAX corner defect.
- Seeded Good Ending CPU/emulator controls accept rendering, name entry and
  section-correct persistence; they bypass ordinary OP/gameplay setup and their
  final black frame does not accept fresh OP. Manual full Normal Windows routes
  are a separate later observation.
- Natural dense Lunatic/Extra timing, optional Windows high-cycle audio/pacing
  and a second emulator need dedicated replays if development resumes.
- Host x64 registration RGB reverse/bright text policy is corroborated by pinned
  DOSBox-X video source, with actual original TRAM stores but explicit device/
  ROM/PI and far-return adapters. It is not physical video or complete native
  scene/save integration. See [port status](PORTING_STATUS.md).

## Reuse procedure

1. Pin the new game's assets/target and mark provenance; identify its actual
   owner, segment:offset, relocations and call frame.
2. Retrieve the relevant KB row and linked evidence; restore necessary private
   inputs or regenerate them. Keep rejected alternatives and adapter scope.
3. Reproduce a rejecting baseline before applying a repair. Compare full calls,
   pixels/state, ordered I/O, ABI and memory guards; check relocated loads.
4. Preserve exact/default source branches and cold-replay affected accepted
   owners when ABI/layout changes. Record source-to-source controls separately.
5. Measure uninstrumented runtime timing/audio on the intended host and route
   before claiming smoothness; retain bounded instruction costs as their own
   result. Add scoped evidence/knowledge in the destination project.
