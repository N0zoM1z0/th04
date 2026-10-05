# Stage 3 evidence

Historical bounded results, preserved from `docs/PORT64.md`. Current state is
[the port overview](../../PORT64.md). Original CPU execution and adapter scope
remain explicit; successful component controls do not accept complete gameplay.

## Stage3 midboss and pre-Elly integration

The native window now continues from Kurumi's actual departure into Stage3,
runs its real STD/MAP and midboss, and finishes the Elly pre-dialog. Elly's
battle is held at the genuine frame9202 gate. No placeholder boss update runs.
Stage3 setup is derived from MAIN13A9:A6F6..A7B4, which installs the midboss
callbacks09FB/1D95, start frame1600, HP850, current/previous3072,-512 and
velocity0,64. Reset clears active/HP before setup; phase, phase clock, damaged
flag, unused angle, shared HP-bar and defeat angle survive until their real
owners change them.1,280 CPU controls seed all22 actor bytes across256 markers
and five ranks, and compare those retained fields on three builds and actual
Windows. Elly's own retained Boss setup is deferred to the next batch.

Four attack helpers occupy13A9:0861..09FA; the dispatcher ends at0C09. The
zero byte0C0A and switch table0C0B..0C1E have separate static ownership.
Renderer0AAF:1D95..1E59 preserves signed division for the flying animation,
strict playfield bounds, one scroll wrap, damage-flash consumption and the
shared defeat-angle updates. Original update controls execute actual aim,
rank/performance tune, ordinary/fixed-speed bullet allocation, gather3stack,
collision wrapper, score bonus, HP bar, activation/reset and render helpers.
Audio, point popup/item/spark consumers and hardware drawing remain adapters;
shot damage is injected at the real collision boundary.

Entry lasts20 ticks. Four attacks alternate with pauses and twelve mirrored
flight directions observed at DATA:1790. After dash12, the original keeps
moving until a boundary exit rather than selecting another attack. Boundary
exit still performs shot collision; a lethal shot on that frame takes the
original defeat/reward path. Defeat clears only horizontal velocity. The native
core throws for a corrupt new-dash index>=12 instead of reading adjacent host
memory. Ordinary retained Normal/Lunatic controls at both ring-cursor seeds
complete without that exception; corrupt-state equivalence is excluded.

The actual target produces15,886 complete state/event/draw records from9,792
input controls:2,568 updates,7,200 renders, eight activation/reset controls each
and eight retained shot/timeout sequences. State comparisons include all22
actor bytes, three private bytes, shared defeat angle, score, RNG cursor, full
bullet/gather templates,440 bullet records,16 gather records and ordered events/
draw geometry. Current Linux/Wine/optimized UBSan/actual Windows replay the same
independent trace. The original was reexecuted before the new contract target's
static-link repair; the current Linux contract executable remains identical.
Reference replay verifies target/fixture/trace identities and record counts;
it does not claim to reexecute original code. Hook rejection propagates, and
a disposable output-byte mutation fails the comparator.

Stage loading validates resources/STD before actor mutation, consumes353 next
process LCG draws, keeps MAIN generation2 and publishes resident/resource2.
Stage slots initially append16 BFT and four BMT images, replacing the preceding
bank. Pre-dialog cleanup installs ST02.BB1's six32x32 images and ST02.BB2's
twelve64x64 images. BB2 supplies the new active palette. Independent Python
FAT/PAR/CDG decoding checks106,880 opaque Elly portrait pixels across eight
Normal/Lunatic Reimu/Marisa shot/idle routes. A disposable checked-pixel mutation
fails the comparator. File loaders are request adapters in the original CPU
setup; these asset controls are not complete original VRAM comparisons.

Sixteen contracts and240 BMPs/268 counters agree Linux, Wine, optimized UBSan
and actual Windows. Prior168 BMPs/188 counters stay identical to v1269. Dialog
freezes actors/invincibility/RNG and the completed Elly frontier remains held.
Windows test-target DLL loading initially failed because its declaration came
after the static-link/warning loops; it now participates in both loops. All17
package PE executables import only Windows-provided DLLs. Windows builds use
MinGW13 cross-compilation; actual Windows execution is separately observed,
not a native Windows compiler claim. GNU8.4 builds Linux and optimized UBSan.

```sh
python3 port64/verify_midboss3.py \
  --target /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-midboss3-contracts \
  --output-dir .analysis/port64/midboss3-control
python3 port64/verify_stage3_resources.py \
  --target /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/targets/th04/main.exe \
  --hdi /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/runtime/images/zun.hdi \
  --exe .analysis/port64/linux-live-v1251/th04-port64-midboss3-contracts \
  --frames .analysis/port64/verification-stage3-v1270-final/stage3-linux \
  --output .analysis/port64/stage3-resource-control/receipt.json
```

Runtime batch manifest:
`416e8079931e7754318f7abc2176762951a3d22212a2590fd965518b9de922e7`.
Current manifest after a CTest-only registration correction: `322e213a739262231351902ee294c0bdd582b84f6abd1f88d93cb3dafb0c0a2e`.
`control-review.json` confirms all51 executable bytes are unchanged and the
16 CTest contracts pass Linux/UBSan; the runtime receipts keep their original
batch manifest above. No gameplay source changed in that correction.

Receipts: `.analysis/port64/midboss3-v1270/{target-live,integration-review,negative-live,native-windows-receipt,native-windows-setup,native-windows-core,windows-export-receipt}.json`,
`core-linux-final/receipt.json`, `core-{linux,windows,ubsan}-replay-final/receipt.json`,
`setup-{linux,windows,ubsan}-replay-final/receipt.json`, and
`.analysis/port64/verification-stage3-v1270-final/receipt.json`.
Windows root native EXE/launcher use the v1270 preview;21 other existing files
remain identical. No GUI was launched. Elly battle/later stages, player death/
Bomb, complete HUD/audio, Ending and persistence remain unported. The DOS source
and exact acceptance states are untouched. Semantic remains stopped; next port
Elly's retained setup, foreground, backdrop/tile ownership and battle.


## Elly battle and departure integration

The v1271 native window continues through Stage3's genuine pre-dialog at frame
9202, Elly's entrance, scythe/orbit and all attack groups, defeat, post-dialog,
clear bonus and the 416/488-frame departure. It holds at the actual Stage4
resource request. Semantic readability stays stopped once sufficient for the
next native slice; clarify only a concrete ambiguity. DOS source and exact
acceptance are unchanged.

Observed pinned MAIN ownership is13A9:7ECC..8C3D (scythe/helpers/dispatcher),
0AAF:7322..73DA (foreground),7757..777E (previous-position invalidation),
777F..77E6 (background), and13A9:A6F6..A7B4 (Stage3 setup).
The background generator's1154:0D2F alias has the same file extent; the executed
identity above is used in runtime records. Separate scythe jump destinations
819C..81AB, gather alignment83A2/table83A3..83B2 and dispatcher tables8C02..8C3D
are data ownership, not executable instructions. Original08F6:2F6C..2F79 executes
its unrolled fill;12,288 CPU write addresses independently establish the
32,128,384,256 rectangle. This does not prove physical GRCG color/VRAM behavior.

The original scythe has an unsigned16-bit clock, byte angle/speed and signed
turn. It runs before the Boss phase dispatcher and uses raw shot damage with
against-boss=false to reduce only vertical velocity; Boss body hits use true
and truncate returned damage to a byte. Native integration supplies separate
callbacks with the shared shot-score/spark consumers in their original order.
Entrance advances the Boss clock twice; the orbit uses previous.x as radius.
Phase0 sets the blue component of palette0, and phase2 clears it. Attack gather
calls use gather-only allocation, retaining the entity's bullet-template fields.
These details were resolved by target CPU controls rather than DOS refactoring.

256 retained setup controls compare the complete24-byte Boss,16 additional and
48 explosion bytes, hitbox and timeout. Original setup leaves all19 private
scythe bytes, orbit clock and pattern group untouched. The native first Stage3
load uses fresh MAIN BSS for those private fields; this is not a claim that
Stage3 setup resets them. Preceding Kurumi HP/endHP/angle and other untouched
Boss/explosion metadata are retained; stage-common globals have separate reset
ownership. The pre-dialog already installs six32x32 and twelve64x64 battle
sprites and the BB2 palette.

Independent original CPU expectations cover9,329 controls/39,297 complete
state/event records:2,958 scythe,288 orbit,6,075 dispatcher controls and eight
retained sequences across all four ordinary ranks with injected damage0/19.
Each no-shot Boss-only sequence departs after6,523 ticks; damage19 after971.
These sequences omit ordinary pool updates/rendering; native full-stage
integration is checked separately. Native foreground compares5,316 controls
and background compares11,264, including signed clock boundaries, scythe bounds,
explosion/flash metadata,64x64 invalidations and copied BB pointer.

The first comparison exposed gather allocation copying a bullet template.
After correcting gather-only ownership, the final builds replay the independently
recorded original expectations. `full-cpu-linux/original-reference.json` is a
target-only receipt, distinct from native candidate passes and the retained
initial mismatch. Native replay validates target/fixture/trace identity; it
reports original_cpu_reexecuted=false. Foreground/background and retained setup
execute the original again for each of Linux, Wine and optimized UBSan.

17 native contracts and336 BMPs/372 counters agree Linux, Wine, optimized
UBSan/bounds and actual Windows. The preceding240 BMPs/268 counters remain
identical to v1270. Eight Normal/Lunatic Reimu/Marisa shot/idle scenarios each
capture twelve new checkpoints: entrance/scythe assembly, BB transition, orbital
attack/scythe flight, two group transitions, defeat, post-dialog, bonus, fade and
Stage4 request. Post-dialog freezes actor/invincibility/RNG ownership; MAIN
generation2 survives and resident stage advances to3 while resource stage stays2.
Three additional advances at the pending request do not simulate again.

A disposable modified output token is rejected at checkpoint0/field0. Each
original callback rejection is propagated. An attempted background-only
asset/screenshot comparison is deliberately not accepted: retained shots,
sparks and items can overdraw even the top rows. Shared native asset decoding
and prior portrait checks still pass, but no new full-screen original VRAM or
unobstructed-background pixel assertion is made.

Replay from the native worktree:

```sh
python3 port64/verify_elly.py \
  --target /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-elly-contracts \
  --output-dir .analysis/port64/elly-cold/core
python3 port64/verify_elly_setup.py \
  --target /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-elly-contracts \
  --output-dir .analysis/port64/elly-cold/setup
python3 port64/verify_elly_render.py \
  --target /home/pentester/coding/codex_ida/th04-reconstruction/th04/.analysis/targets/th04/main.exe \
  --exe .analysis/port64/linux-live-v1251/th04-port64-elly-contracts \
  --output-dir .analysis/port64/elly-cold/render
```

Use the Windows `.exe` with `--runner wine`, or the optimized UBSan build for
same-source controls. `port64/verify.py` includes all five natural scenario
suites; `port64/verify_windows.ps1` executes the17 contracts and all336 checkpoints
on actual Windows. Receipts live below `.analysis/port64/elly-v1271/`:
`target-live.json`, `core-{linux,windows,ubsan}-final/receipt.json`,
`setup-{linux,windows,ubsan}-final/receipt.json`,
`render-{linux,windows,ubsan}-final/receipt.json`, `negative-live.json`,
`native-windows-{receipt,core,setup,render,background}.json`,
`integration-review.json` and `windows-export-receipt.json`.
Cross-build receipt: `.analysis/port64/verification-elly-v1271/receipt.json`.
Source manifest: `464f6e89661d8adf112ef12645b6c5ae01d1d00f8f7141d686e828853bd7641b`.

Windows root native EXE/launcher use v1271; the versioned package contains18
checked static x64 PE executables.21 other existing DOS/HDI/config/font/build
files remain identical and no GUI was launched. Linux uses SDL2; Windows uses
Win32/GDI. No native Windows compiler or GUI frame-pacing claim is made.
Stage4 onward, player death/Bomb, complete HUD/audio and Ending/save remain
unported. Next bounded work is Stage4 resources/actor reset/midboss and its
character-dependent pre-boss gate.
