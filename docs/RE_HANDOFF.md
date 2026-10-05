# TH04 current handoff

Updated 2026-10-05. The active goal is a standalone PC-98 game: checked-in
TH04 source, successful builds, and normal gameplay. Native whole-build byte
equality is not required. The two remaining MAIN exactness cases are deferred
and retain their nonexact states. ReC98 implementations are adaptation inputs;
upstream exactness claims are not inherited. Current phase: native x64 implementation
in `port/modern-64`; semantic work stops at the clarity needed for a concrete
port owner. Completed DOS semantic and runtime results remain below.

The `semantic/readable` branch now prepares the DOS source for the native
x64 port; it starts at current local `main` commit `8d20492`. The first bounded
batch clarifies the shared PI decoder's command names, units, history, DOS
allocation and ownership. Two cold isolated DOS builds remain raw-identical:
38,050 bytes, SHA-256 `9cc4e7ad…`, 254 relocation entries, zero differences.
Independent historical pixel hashes and slot load/free controls also pass.
This proves a source-to-source regression result for the service harness;
it is not original-target equality or a complete Good Ending visual replay.
See [semantic readability](SEMANTIC_READABILITY.md) for the remaining queue.
The PAR/CDG semantic batch also passes dependency-validated incremental builds:
complete MAIN/OP/MAINE files and ordered relocations equal their preceding
source builds (192,351/77,740/70,614 bytes; SHA-256 `dbbfa404…`,
`c8ac4d73…`, `0a2d3ce8…`). Nine real PAR-member controls pass. Historical
CDG replay could not complete: the old OP/MAINE private snapshot is absent,
and the current MAIN driver rejects a scaffold-transform digest before
building. No target acceptance or ledger state is promoted by this batch.
The BFNT semantic batch likewise preserves all three complete DOS files and
ordered relocations. Historical pattern/palette hashes and fake-VRAM screen
hash `0BE615EA` pass with lifecycle and clipped-placement controls; see the
[BFNT note](reconstruction/product/TH04_NATIVE_SUPER_SPRITE_V870.md).
The segmented-heap semantic batch passes the same three-file fast-build byte
and ordered-relocation equality plus the existing exact-handle reuse, split,
coalescing and DOS reassignment harness. See the
[heap note](reconstruction/product/TH04_NATIVE_HEAP_V863.md).
The input/timing batch names press budgets, action latches, joystick registers,
IRQ cadence and GDC polling. MAIN/OP/MAINE remain complete-file raw-identical
to `33875da`; three accepted MAIN owners pass two cold target/MAP/relocation
replays, and 252 pre/post CPU controls plus DOS VSync lifecycle pass. A rejected
TC4J enum substitution changed polling instructions; literal macros preserve
them. No new acceptance is promoted; the old OP/MAINE decoded scaffolds remain
absent. See the [input/timing note](reconstruction/packed/TH04_SHARED_INPUT_WAIT_V565.md).
Fetch/rebase confirms `main` is still `8d20492` and already an ancestor.
The semantic-only baseline is `.analysis/build/semantic-input-readable-final`;
the following native performance batch updates the Windows package separately.
The authorized native Ending/scroll repair is built and deployed. MAINE's two
CDG renderers now own independent CS frames; the expanded build auditor rejects
their former writes into the PI decoder. Real staff-image CPU controls complete
both far calls at load 2000/6000 and preserve aligned plane bytes. Seeded
Reimu/Lunatic and Marisa/Normal Good Ending replays reach registration, accept
names and save 12,345,678 in the expected score sections. Other sections remain
byte-identical and all ten checksums pass. Their final black frames do not
accept return to OP. These private fixtures bypass gameplay/OP initialization
and use zero resident sound mode/frame-based waits. The user subsequently
confirms all Normal Windows routes and their Endings/save handoff; automated
full-route and cross-emulator validation remain separate. See the
[Ending CDG note](reconstruction/product/TH04_NATIVE_ENDING_CDG_CS_V1230.md).
Native readable scroll names now label the driver's existing storage; seeded
initialization clears all three actual fields. Historical branches preserve
their complete link-relevant OMF in cold source-to-source controls. The top
stripe's connection to that defect remains inferred; the user now confirms
the Stage 6 top stripe is absent.
The original/native bullet-count slowdown agrees across 96 CPU controls;
the user's latest Normal saved configuration has Turbo enabled, so deliberate
count-based slowdown is inactive if those options were loaded. The user reports
Yuuka crosses and Ending are smoother after the planar batch, the title is
smooth, and Extra has little slowdown. That attack has no direct player-speed
or special half-speed write; natural Lunatic/Windows frame pacing remains
separate from the bounded full-pool timing control below. See the
[scroll integration note](reconstruction/product/TH04_NATIVE_SCROLL_BOX_V858.md).

The remaining upper-left pellet is confirmed as native state-clear corruption:
at load 1100h, CLEAR_DWORDS (0708:1178; guest 1808:1187) stores EAX=000E0000
through the complete bullet array, making 220 flags nonzero and queuing 120
coincident pellets. Native full-EAX clearing now passes 54 complete-call CPU
controls; two cold default objects preserve all 22 accepted target bytes.
The old corner mark is absent at seven ordinary Normal checkpoints. See the
[state-clear note](reconstruction/product/TH04_NATIVE_STATE_CLEAR_V1231.md).
The coherent planar batch adds native word sprite/copy kernels and packed PI
pair lookup. Three source reviews, 460 scalar-pixel/ABI controls and the DOS
loader/packed-row harnesses pass. A complete 31-cross renderer control uses
68% fewer instructions with identical pixels; this is not Windows FPS.
Ordinary gameplay and seeded Marisa/Normal Ending/save still pass after the
change. The user subsequently reports no gameplay bugs. See the
[planar performance controls](reconstruction/product/TH04_NATIVE_SUPER_SPRITE_V870.md).

Native fixed-row pellet/tiny-sprite paths now reduce full-pool drawing
instructions by 13.40% (regular) and 21.72% (200 clouds). All 3,604 independent
pixel/ordered-I/O/pool controls, seeded volatile-register controls and 96
original/native slowdown cases pass. In pinned Linux DOSBox-X, the stationary
Lunatic/Turbo 440-bullet fixture averages one refresh period for ordinary
bullets; its artificial all-cloud phase improves from 1.742 to 1.452 periods
at 24,000 cycles. At 36,000, all six phases average one period. This is a
bounded instrumented control, not a complete natural Lunatic route or Windows
FPS claim. Two cold default assemblies preserve both complete link-relevant
OMF owners; full historical replay remains blocked before compilation by the
existing items-invalidate scaffold digest drift. No exact state is promoted.
The uninstrumented final normal product reaches a visible Lunatic combat
checkpoint at 125 seconds with all four executed product hashes verified.
See the [bullet performance note](reconstruction/product/TH04_NATIVE_BULLET_LOAD_V1235.md).

The semantic bullet-generation batch now names the 8-bit clockwise angle
unit, spread/ring member index and offsets, aim/template rotation stages,
final spawn angle, byte-sized source group and synchronous scratch lifetime.
The final 199,455-byte native MAIN remains raw-identical at SHA-256
`cb4c5b66...`; equivalent old/new header harnesses have identical semantic
OMF, and the accepted 2,139-byte `bullet_a.cpp` owner passes two isolated cold
target/MAP/relocation/raw replays. A rejected signed `% 0x80` replacement grew
TC4J output by five bytes, so the directional-sprite half-turn period remains
explicitly unsigned. No acceptance state changes. See the
[semantic bullet note](reconstruction/product/TH04_SEMANTIC_BULLET_GENERATION_V1236.md).

The enemy-script VM semantic batch names all 49 opcode destinations while
preserving their compiler-sensitive physical `case` order. Source comments now
record ES-relative unaligned operands, same-frame setup chains, the timed
instruction's inclusive final update, absolute/backward loops, FIRE template
transfer and performance-scaled autofire. The pre-batch and semantic sources
produce identical timestamp-normalized OMF in one recorded TC4J context; the
complete 199,455-byte native MAIN and all 1,181 ordered relocations also remain
identical. A fresh historical target replay stopped before compilation because
the dependency closure rejects the current `th04_main.asm` at the older v148
boss-background transform. This batch therefore changes no exact state. See the
[enemy-script note](reconstruction/main/TH04_MAIN_ENEMY_SCRIPT_NATURAL_V330.md).

The player-shot semantic batch makes the collision cache, hit animation,
laser render/test, shared spark phase and damage/score ordering explicit. Its
pre/post shot objects have identical timestamp-normalized OMF; the complete
199,455-byte MAIN and all 1,181 ordered relocations remain identical. Focused
historical replay currently cannot reach the target comparison because its
old dependency staging first omits the semantic bullet header and, when that
owner is selected, duplicates two point-number assembly constants. Existing
v177 exact evidence remains unchanged. See the
[player-shot note](reconstruction/main/TH04_MAIN_SHOTS_SEMANTIC_V1239.md).

The scroll semantic batch makes the Q12.4 accumulator, 400-line wrap,
five-row map-section traversal, 24-word ring refill and two-frame row-copy
request handoff explicit. Historical public names remain the OMF ABI while
source expressions use their already established native initialization names.
The two changed C++ owners have byte-identical timestamp-normalized OMF before
and after the edit. The dependency-validated 199,455-byte MAIN remains
SHA-256 `cb4c5b66...`, with identical headers, program image and all 1,181
ordered relocations. This is source-to-source preservation; no fresh cold
target replay or acceptance promotion is claimed. See the
[scroll integration note](reconstruction/product/TH04_NATIVE_SCROLL_BOX_V858.md).

The MAINE score-registration semantic batch makes the single-section work
buffer, two-character/five-rank file offsets, table insertion order, unsigned
no-entry sentinel, gaiji keyboard repeat, clear-mask update and all-section
re-key/save pass explicit. The build recompiles the four edited SCORE roots
plus its BGIMAGE control owner; all five pre/post objects have identical timestamp-normalized OMF and
link-relevant records. The complete 72,246-byte MAINE remains SHA-256
`7bfd7fd5...`, with identical header, program image and all 663 ordered
relocations. This is incremental source-to-source preservation. The existing
decoded-exact states of load, insert, save and registration-menu owners are
unchanged; no fresh cold target replay or promotion is claimed. See the
[MAINE score note](reconstruction/op-maine/TH04_MAINE_SCORE_CPP_V479.md).

The process-handoff semantic batch documents the shared ZUN.COM resident block,
the segment pointer persisted through `MIKO.CFG`, successful `execl()`'s
non-returning behavior, and each executable's publish/cleanup boundary. The
semantic build recompiles 3 MAIN, 5 OP and 4 MAINE roots/control owners; all 12
pre/post OMF streams are timestamp-normalized and link-relevant identical.
Complete MAIN/OP/MAINE stay raw-identical at 199,455/79,372/72,246 bytes and
retain all 1,181/817/663 ordered relocations. Existing user route results
continue to corroborate the ordinary handoff; v1242 adds no new runtime or cold
target claim. See the
[process-handoff note](reconstruction/product/TH04_SEMANTIC_PROCESS_HANDOFF_V1242.md).

The random-ring semantic batch confirms one shared 256-byte ring and word
cursor behind both `randring1_*` and `randring2_*` families. Accessors take
overlapping little-endian words, increment only the cursor's low byte, and at
index 255 read the adjacent pre-increment cursor byte (`0xFF`) as the sample's
high byte. The descending `IRand()` fill and unchecked AND/MOD range behavior
are now explicit. The dependency closure recompiles 53 C++ roots and three ASM
objects; all 56 pre/post streams have identical timestamp-normalized OMF and
link-relevant records. Complete MAIN stays 199,455 bytes at SHA-256
`cb4c5b66...`, with identical header, program image and all 1,181 ordered
relocations. No fresh cold target replay or exact-state change is claimed. See
the [random-ring note](reconstruction/main/TH04_MAIN_RANDRING_SEMANTICS_V1244.md).

The shared-LCG semantic batch documents `random_seed` as initialized,
process-local 32-bit state and resident `rand` as a persistent seed source. The
update performs unsigned modulo-2^32 arithmetic and returns new-state bits
16..30. OP increments the resident seed once per menu frame while keeping its
own LCG separate; MAIN copies the resident value once, overrides it with 318
for demos, and continues one stream across direct draws, ring fills and Stage
transitions; MAINE re-seeds during verdict calculation, so verdict/save order
also selects the score-key stream. Three changed/control objects in each of
MAIN, OP and MAINE have identical normalized and link-relevant OMF, and the
complete 199,455/79,372/72,246-byte products plus all 1,181/817/663 ordered
relocations equal the pre-edit baseline. This is incremental source-to-source
preservation, with no fresh cold target or runtime-randomness claim. See the
[shared-LCG note](reconstruction/product/TH04_SHARED_RANDOM_LCG_SEMANTICS_V1246.md).

The item-lifecycle semantic batch covers `th04-main-items-update-v154` without
changing its accepted extent. Automatic drops emit on every second request;
miss drops retain their discarded distinct-slot draw and conditional per-item
ring consumption; scoring names the Bomb multiplier, dream saturation,
inclusive power-overflow table and performance carries. Motion comments record
pull cancellation, deferred removal and the unsigned pickup rectangle. The
big-power path reads its bonus before clamping but overwrites above-cap results
with 2,560; the portable implementation must preserve the final result without
an out-of-bounds access. All 21 recompiled dependency objects have identical
normalized and link-relevant OMF. Complete MAIN remains 199,455 bytes at
`cb4c5b66...`, with all 1,181 ordered relocations unchanged. This is
incremental source-to-source preservation, with no fresh cold target or runtime
item claim. See the
[item semantic note](reconstruction/main/TH04_MAIN_ITEM_SEMANTICS_V1248.md).


## Current state

Native x64 work is isolated in `port/modern-64`; general semantic expansion
stays stopped unless a concrete port ambiguity requires it. Latest native
commit `b5ec7fc` (v1296) joins congratulations after verdict. Character/rank
selects the real CONGxy.pi image; Good/Easy Bad show it, other Bad ranks skip it.
Speed1-in, held-key release/fresh press, speed4-out then song fade4 and exactly
100 further refreshes reach score registration entry. The preview holds there;
registration/save/fresh OP return is next. MAINE generation3, resident counters
and continued LCG remain unchanged through picture transfer/release and waits.

Attested recovered _main0A05:00B2..0241 (400bytes9a44bbf5) passes32 distinct
branch fixtures plus missingCFG at loads1000/2000.50 original fade/key clock
profiles and10 pictures/20 complete pages pass;PI palette wrapper/far memcpy
execute fully. Child routines/PI/sound/init/exec remain explicit adapters;
pixels use pinned picture bytes and retainedv1294 native decoder regression.
Original Extra registration->congratulations->verdict order is observed by
bounded CPU fixtures;Extra gameplay is still unported. Previous verdict916/10,
80 graphic cases/527 original font kernels/160 pages remain valid.

GNU/Wine/optimizedUBSan/actualWindows pass24 natural menu/boss/Ending/Staff/
verdict/congratulations routes, adding48 congratulations pages/24 RGB frames
per host while preserving prior576 Ending/48 Staff/48 verdict pages. Actual
Windows1440 route files and component pages/clocks pass independent Python
readback and mutations. Three fast builds31AMD64 products/30CTests each bind
all93 products to222-file source manifest4c872c8a. Current GNU8.4 filesystem ABI
requires its matchingstdc++fs archive;isolated failure/repaired probes and
CMake linkage correction pass. No physical VRAM/audio/saved-score/exact claim.

Windowsv1296-congratulations/root native GUI/English start-th04-port64.bat are
published without auto-launch;previousv1295 GUI/launcher rollback retained.
106 unrelated Windows hashes remain unchanged. DOS scripts/products/config/
saves/source/unit/function acceptance unchanged. Root/native CI and diff-check
pass. Current native receipts and focused handoff:
`.analysis/worktrees/port-modern-64/.analysis/port64/post-verdict-v1296/` and
native branch `docs/PORT64.md#congratulations-and-registration-entry`.
Full native game still lacks registration/save, Extra/death/Bomb/Continue/full
HUD/audio/config. Keep the full objective active and port the next concrete owner.

Finished5564 generated buffers are losslessly archived after full member
hash/size readback;net2094MiB reclaimed including598 temporaryStaff expansions.
12025 protected files retain hashes. GNU80-case verdict/10-picture congratulations
references and all three fast caches remain expanded;restore other captures
before direct replay. See native `post-verdict-v1296/media-archive-receipt.json`.
Earlier requested development cleanup receipt remains at
`.analysis/cleanup/development-media-20261005/receipt.json`;older v1295 captures
use `verdict-v1295/media-archive-receipt.json`. Original images/toolchains/saves
are protected;do not delete active caches to save space at the cost of fast builds.

The preceding Staff Roll baseline commit `85049b8` (v1293)
continues both Good/Bad Ending through the complete Staff Roll and holds at
verdict entry. MAIN score/run-counter publication, resource release, fresh
MAINE generation and LCG stay checked. Staff Roll transfers/releases the old
Ending owner, runs both backgrounds and radial/diagonal/axis dissolves, frees
its background/CDG slots and completes its blackout. At that checkpoint verdict, congratulations,
registration/save and Extra/death/Bomb/Continue/full HUD/audio/config remain
incomplete; this is not a complete native port.

Eight original CPU request controls execute recovered MAINE `0A05:0E80..1736`
at loads1000/2000 and angles0/7/64/255, including signed polar `0CC7:0260`.
268 original graphics-kernel controls at `0CC7:0408/06E6/0A86` cover18 CDGs,
four planes, alignments0/7/15 and background rectangle quirks. All three native
consumers pass332 complete pages and166 palette/page/lifetime checkpoints.
Each also passes24 natural menu/STD/dialogue/boss/Ending/Staff Roll routes:
576 Ending pages,288 palette/states,288 RGB and48 final Staff pages per host.
Three fast builds each produce31 AMD64 products and pass30CTests;29 GNU and
29 UBSan products remain raw-identical to v1292. Actual Windows passes all
controls/routes and1,248 binary/state comparisons, followed by independent
Python original-gallery/RGB/final-Staff readback. Final208-file source manifest:
`830f7c96cca70b471124d408cbad3ece832d94f7964d62a18604338d7cc487b9`.

Hardware copy uses its destination's opposite page and leaves access on the
destination. BGIMAGER restores WORD-aligned rectangles over h+1 rows; visible
page coverage excludes the row400 allocation tail. Original Ending callers
explicitly access1/copy0/access0, preserving their visible-page reference under
its existing request-adapter convention. PI decode remains a recorded regression
dependency; GRCG/VSync/file/sound consumers are explicit adapters, not physical
capture or music synthesis. Targets including packedMAINE670de6ba/recovered
payload7495ae43 remain candidate-local-attested; its Ghidra database attests the
packed wrapper. No DOS source or exact/unit/function acceptance changes.
Native receipt root: `.analysis/worktrees/port-modern-64/.analysis/port64/staff-roll-v1293/`;
bounded note: `docs/PORT64.md#staff-roll-integration` on `port/modern-64`.

Windows root `start-th04-port64.bat` and versioned `port64-preview/v1293-staff-roll`
contain the validated preview; previousv1292 is backed up. All2,206 pre-existing
Windows files outside the two native replacements retain hashes. DOS launchers,
products/config/saves are unchanged; publication does not launch the GUI.
Historical B-labelled native GUI fixtures before v1292 selectedA; their B
coverage claim is invalid. The v1291 diagnostic PNG RGB correction does not
change its original indexed/palette references.

The latest completed render outputs are losslessly gzip-compressed:6,977 files
pass readback and release approximately1.98GiB. Seven explicit inputs stay
unchanged; supplementary post-archive comparisons verify all93 active native
executables and456 raw original-controlled Ending/font reference buffers against
accepted pre-archive digests. Both final GNU Staff Roll pages remain expanded;
current caches, targets, original CPU streams and Windows inputs stay available.
Restore historical `.bin`/`.bmp` paths with `gzip -d -- PATH.gz`; receipts are
`media-archive-receipt.json` and `archive-readback.json` under the native root.
The preceding v1292 archive releases3.21GiB and preserves its553 protected hashes;
its original/compressed digests remain in the separate v1292 receipt root.

The historical-fixture cleanup compresses 32 completed pre-v1290 generated fixture files
and shares storage for 16 byte-identical historical gzip archives. SHA-256
readback passes for every compressed fixture and all 38,563 protected files;
both worktrees retain their prior source states, including then-unfinished v1292
native work. Net allocated space released is approximately 263 MiB. Current
DOS products, all three native incremental caches, original CPU reference
streams, targets, toolchains, databases and the Windows package/saves stay live.
Receipt: `.analysis/cleanup/historical-fixtures-20261005/receipt.json`.
Restore historical fixture paths with `gzip -d -- PATH.txt.gz`. Shared gzip
archives are immutable: restore or replace them rather than overwriting in
place. Historical reference digests and archive paths are unchanged.

The follow-up 2026-10-05 cleanup retires 173 historical runtime image archives,
42,362 completed native screenshot archives and 30 superseded Windows preview
directories (v1260--v1289). Three lossless tar/zstd archives pass every member's
SHA-256 readback before removal; 1,980 active build/input/package files retain
their hashes. Net allocated space released is approximately 2.08 GiB, including
archive and receipt overhead; Windows removes 624 MiB of old file contents.
DOS products, x64 incremental caches, published launchers and saves remain
available; the former v1290 package is now archived by the later cleanup below.
Archive manifests, hashes and
restore commands are in
`.analysis/cleanup/superseded-artifacts-20261005/receipt.json`. Historical disk
and screenshot `.gz` paths now require tar restoration before the existing
`gzip -d` step. Earlier archived Windows executables remain in their separate
archive described below. Original CPU reference streams remain at their paths.

The 2026-10-05 cleanup losslessly compresses 12 historical x64 rendering
traces and archives 49 superseded Windows preview executables (v1281 and
earlier), reclaiming 745 MiB net across Linux and Windows. Every archived
file passes SHA-256 readback; 2,028 protected current build/input/package
files and both worktrees' source states remain unchanged. Current DOS builds,
the three native x64 build caches, published Windows GUI and saves remain
available. Restore commands and digests are in
`.analysis/cleanup/historical-port-builds-20261005/receipt.json`; old trace
paths require `gzip -d -- PATH.gz` before replay. Windows scripts, assets and
replay observations remain at their original paths.

Latest cleanup keeps all three incrementally built x64 caches and Windowsv1293
with its previousv1292 rollback executable, and moves oldv1290/v1292 packages
to a verified WSL tar/zstd archive.20,142 identical historical gzip outputs
share hard-linked storage with all original paths preserved.6,522 protected
hashes agree; net space released is513MiB on WSL and237MiB on D:.
Receipt:.analysis/cleanup/build-followup-20261005/receipt.json. Replace shared
gzip paths atomically; do not edit a hard-linked compressed inode in place.

| Artifact | Accepted authored functions | Native build/runtime |
| --- | ---: | --- |
| OP | 93/93 | Standalone build; normal options/Music Room/scores/DOS exit and saved config pass |
| MAIN | 493/495 | Standalone build; user completed invincible Easy/Lunatic and all normal Windows Normal routes; optimized bounded ordinary replay passes |
| MAINE | 72/72 | Standalone build; seeded Good Endings register/save; user confirms full Normal Windows Ending/save before the planar batch |
| ZUN | 3/3 | Source-only cold packed build; four-product GAME.BAT startup passes |

These counts describe historical function acceptance, not whole executable or
normal-game completion. `python3 scripts/status.py` reports the live ledgers.
Targets remain `candidate-local-attested`. Product include checks have zero
compatibility forwarders and forbidden ReC98 edges.

The full native build compiles 193 MAIN C/C++ roots, 155 ASM roots, eight state
owners and four generated sprite owners without `masters.lib`. All four products
build through `scripts/build.py`. The bullet batch uses dependency-validated
fast MAIN/OP/MAINE builds and rechecks the preceding cold ZUN source/packing
receipts and 37 unchanged component-source/build-driver hashes. Current
normal/invincible inventories are `.analysis/build/th04-{normal,invincible}/build.json`.
Normal products are MAIN 199,455 bytes (`cb4c5b66…`), OP 79,372 (`ef37e6e8…`),
MAINE 72,246 (`7bfd7fd5…`) and ZUN 7,723 (`d6043dce…`). Invincible MAIN is
also 199,455 bytes (`0d99bc5a…`); the other three products are identical.

Verified integration fixes:
- MAIN EGC tile copy uses 3100h, observed at MAI_TEXT 0AAF:212C (file E41Ch).
  All 600 initial tiles match their four-plane source images. HUD data includes
  four rank strings and a NUL-terminated blank HP bar.
- OP frees its temporary palette DOS block before overlay. The former four-
  paragraph block split free memory and made `execl` return ENOMEM=8.
- MAINE's C++ code group changed the CS frame for SHARED assembly. Independent
  native IRQ/PAR and self-modifying renderer segments repair four vectors and
  42 MAINE CS-relative operands (40 for OP, 39 for MAIN, including their CDG entries).
  The build checks these destinations, including
  observed direct-call CS frames. The default renderer branch retains its
  previous complete link-relevant OMF output in cold compiler comparisons.
- OP labels use monochrome CDG masks and description color 15, observed in
  OP_MAIN_TEXT 0A74:0375/0497. Native call composition and FAR Pascal RETF6
  checks pass; historical accepted inline bodies remain unchanged.
- MAIN's native bullet TU explicitly declares BULLET_U_TEXT/main_03. The old
  link-only group made both dense switch tables segment-relative under group
  CS. All 14 linked destinations now pass the far-caller/frame audit, which
  runs before MAIN publication. Other program bytes remain unchanged; the MZ
  relocation table changes. Historical exact source branches remain unchanged.

The uninstrumented v1178 normal route reaches stage 0, Game Over, Continue,
MAINE name entry, score persistence and the OP title menu. Ten saved-score
section checksums and digit ranges pass. Private v1176 separately records all
MAINE initialization call completions. Pinned originals under the same emulator
also show pale score colors and previous CONTINUE/stage-image remnants; do not
attribute these to reconstruction without another control.

The uninstrumented v1181 normal-menu scenario passes on native and original
products. Options frames 75/95 and returned-menu frame 165 are raw-identical.
Both enter Music Room, emit non-silent stereo audio, view scores, exit to DOS
and save the same valid configuration `0304010201010000000c` (Lunatic, four
lives, one Bomb). Startup/loading and polygon-animation phases differ;
waveform or general timing equality is not claimed.
The native v1182 reboot loads those saved options into the menu and exits to
DOS with the complete ten-byte configuration unchanged.

The explicit bullet-group repair passes ordinary Orange clear and stage 2
entry. Both old switch frames fail the static gate; the published and cold
repaired builds pass. Historical private fault layouts remain in the ledgers.

The ordinary v1203 `main_progression.json` run reaches Kurumi combat but
displays Divide error/DOS return by 575 seconds. The same-image v1208 repeat
still fights Kurumi at 605 and displays the same guest failure at 635. All four
executed product identities pass in both runs. Host exit 0 does not accept the
guest failure; the repeat's black final frame is also unaccepted.

The pinned-original v1204 control reaches third-stage Elly dialogue at 635;
its final 650 frame is black and is not an accepted checkpoint. The private
cpu-only v1207 MAIN also reaches stage 3, with a valid observer arm but no
exception. Neither result repairs the ordinary native failure. A private
source-built emulator likewise changes progression and does not reproduce it.

The primary VM86 observer confirms vector 0 at `24FB:9780`, MAIN load `10FC`,
MAIN_03 `13FF:9780`: all 64 relocated code bytes match the ring-count IDIV in
`bullet_velocity_and_angle_set()`. DS `334F` has Easy rank, performance/min/max
4/4/16, ring-aimed group 2Ch and count zero. The BP chain and actual near-call
instructions identify Kurumi dual spawnrays, fixed regular generation and the
Easy wrapper. Pinned target file `1E612h` has the same cumulative reductions:
six shots minus two minus four becomes zero, then Easy halves zero.
The native `TH04P` clip branch now skips empty rings; the original replay branch
retains its bytes. The isolated x86 Oracle rejects the old native build and
accepts both empty-ring cases plus nonempty-ring/single negative controls.
The ordinary repaired v1217 run clears Kurumi and explicitly enters STAGE 3 at
635 seconds. All four executed product identities pass; the black final frame
is unaccepted. Native cold-build equality and the generated-code Oracle pass.
Two default-branch cold replays preserve the complete 2,139-byte bullet owner:
raw bytes, MAP and relocations pass (`empty-ring-v1219/receipt.json`).
The read-only observer passes real-mode and DOS/EMM386 VM86 DIV fixtures,
including 27 instruction bytes and complete RAM snapshots. Calibration:
`.analysis/runtime/emulators/primary-observer-v1215b/calibration-vm86/receipt.json`.

For interactive testing, the separate `--invincible-main` build clears pending
player hits before miss processing in a private staged source overlay. Its four
products build and pass MZ/link audits; the normal published MAIN is unchanged.
`scripts/export_windows_play.py` packages the four verified products, saved HDI,
Windows DOSBox-X and `start-th04.bat` at
`D:\Entertainment\Game\Touhou\th04-reconstruct`. The Windows 2023.05.01
emulator reached OP with the user's dynamic/Pentium/15000/32 MB profile; Z/X
worked after switching Windows input to English. The user completed the
invincible Easy route through the ending, with slow OP fireworks, boss defeat
explosions and some stage-5 Yuuka barrages but no other reported faults. Their
saved Easy config has turbo mode enabled, so the explicit bullet-count slow-
down branch is inactive. This is user runtime observation, not an instrumented
ordinary-build acceptance. The shared `SUPER_PUT` now uses masked byte-sized
planar writes. Fake-VRAM output and 45 randomized placements match the prior
renderer. Under pinned Linux DOSBox-X, the old OP was still in fireworks at
30 seconds; the changed OP reached the title menu at 30 seconds. Receipts:
`.analysis/runtime/candidates/super-perf-{before,after}-20261002/run-logo/receipt.json`.
Windows-host and stage-5 performance need fresh playtest. The Windows builder
is `build-th04.cmd`: it shows English progress, hashes, and uses validated
incremental object reuse by default; `-Cold` forces a four-product source build.
The complete invincible Windows run
`product-20261002-155156-92d1f35a` passed all four source/link audits and
refreshed the saved package. The following default Windows CLI run
`product-20261002-162226-4cebef25` passed in 98.8 seconds: MAIN reused 192
C++ objects, OP 163 objects, MAINE 137 objects, and ZUN passed unchanged-input
fingerprint and package/product hash checks. All four final product hashes
equaled the cold build. The saved `MIKO.CFG` and `GENSOU.SCR` SHA-256 values
were unchanged across both exports. The Windows package is ready for a new
playtest; these build checks do not establish its frame rate.
Shared `SUPER_PUT` composes each destination byte once, directly overwrites
fully opaque bytes, and clips row/byte intervals before drawing. DOS fake-VRAM
screen hash remains `0BE615EA`; randomized planar and clipping controls pass.
The user completed the invincible Lunatic route and reported that Good Ending
score registration showed background/remnants without the menu or text and
turned black after Esc. Their copied HDI is preserved at
`.analysis/runtime/candidates/lunatic-ending-user-20261003/` (SHA-256
`91cafe8a…`). The saved Lunatic configuration has turbo enabled; the
bullet-count intentional slowdown branch is inactive, so Yuuka spell lag is
inferred to be render/CPU load pending a phase-specific trace.

The product PI slot free path now clears its owner pointer before the next
load. A bounded DOS load/free/load/free probe passes and the product far-call,
vector and MZ audits pass; this fixes a verified stale-pointer hazard, but a
ordinary gameplay-to-Good-Ending handoff remains separate from seeded replays. See
[`TH04_NATIVE_PI_SLOT_LIFETIME_V1224.md`](reconstruction/product/TH04_NATIVE_PI_SLOT_LIFETIME_V1224.md).
The Windows package at `D:\Entertainment\Game\Touhou\th04-reconstruct`
contains optimized normal `product-20261003-082645-59909a08` and invincible
`product-20261003-083233-dcc0bfe1` variants. `start-th04-normal.bat` mounts ordinary
collision damage in `play-normal.hdi`; `start-th04.bat` mounts the separately
source-compiled invincible MAIN in `play.hdi`. Invincibility remains a private
staged source overlay, not a maintained player change or launcher memory patch.
OP/MAINE/ZUN are identical between variants. Both launchers use 24,000 cycles;
reference launchers use 15,000. Optional `start-th04-normal-highcpu.bat` and
`start-th04-highcpu.bat` set only 36,000 cycles for those same respective images.
The latest serial fast builds and Windows readback pass; only MAIN.EXE changed
in either saved image, with every nonproduct GENSO file retained byte-for-byte.
Control: `.analysis/bullet-v1235/windows-export-receipt.json`. Windows CLI builds
retain their English progress and validated object reuse; actual Windows CLI
controls for the preceding batch remain at
`.analysis/render-corner-20261003/windows-fast-control.json`.

The user confirms normal death-to-registration/save and subsequently full
Normal routes/Endings before the planar batch, then improved title/cross/Ending
performance and little Extra slowdown. Optimized bounded ordinary and seeded
Ending/save replays pass; full Lunatic and the optional Windows 36,000-cycle
profile still need a user test. The Linux emulator aborts after PC-98 reset
with dynamic core; Linux runtime controls use normal/Pentium. Old damaged
Ending and Divide-error reports are superseded by the bounded repairs above;
private fault layouts remain replay evidence in the ledgers.

Current runtime receipts:
- `.analysis/runtime/candidates/native-four-cs-v1178-20261002/run/receipt.json`
- `.analysis/runtime/candidates/native-four-cs-v1178-20261002/run/handoff-state.json`
- `.analysis/runtime/candidates/native-op-menu-v1181-20261002/run/handoff-state.json`
- `.analysis/runtime/candidates/original-op-menu-v1181-20261002/run/handoff-state.json`
- `.analysis/runtime/candidates/native-op-reload-v1182-20261002/run/handoff-state.json`
- `.analysis/runtime/candidates/native-bullet-group-v1199-20261002/run-progress/receipt.json`
- `.analysis/runtime/candidates/native-bullet-group-v1199-20261002/run-repeat-v1208/receipt.json`
- `.analysis/runtime/candidates/original-progression-v1204-20261002/run/receipt.json`
- `.analysis/runtime/candidates/native-cpu-state-v1207-20261002/run/cpu-fault.json`
- `.analysis/runtime/candidates/native-bullet-group-v1199-20261002/run-primary-gdb-v1214/emulator-cpu-fault.json`
- `.analysis/runtime/candidates/native-bullet-group-v1199-20261002/run-primary-vm86-v1216/emulator-cpu-fault.json`
- `.analysis/runtime/candidates/native-empty-ring-v1217-20261002/run/handoff-state.json`

## Build and validation

```sh
python3 scripts/preflight.py
python3 scripts/build.py
python3 scripts/prepare_product_hdi.py --output-dir .analysis/runtime/candidates/NEW-game
xvfb-run -a python3 scripts/probes/run_th04_maine_diagnostic_hdi.py \
  --prepared-dir .analysis/runtime/candidates/NEW-game \
  --output-dir .analysis/runtime/candidates/NEW-game/run \
  --frame-second 95 --time-limit 1000 --stop-after-frame
python3 scripts/ci.py
git diff --check
```

Only one Borland/Wine build may run at a time. `--only main` selects one product;
`--main-cpp-cache`, `--op-cache` and `--maine-cache` reuse only verified inputs.
`prepare_product_hdi.py --original` creates an attested original baseline;
`--lives 1 --bombs 0` sets an ordinary configuration fixture in the disposable
image; `--rank 0` selects Easy. Runtime `--checkpoint-second` captures
intermediate frames; held keys use
`--input-event down:z@SECOND` / `up:z@SECOND`. `--key-delay-ms 300` gives menu taps
adequate duration. Always use new output paths. Private state probes do not
replace uninstrumented runs. `inspect_th04_handoff_trace.py --require-score-saved`
checks executed-image identity and changed decoded score sections.
Use `--scenario config/runtime/scenarios/op_menu.json` for the normal menu
regression and `inspect_th04_handoff_trace.py --require-config-options
030401020101` to check persistence. `prepare_product_hdi.py --config-from-run
RUN_DIR` seeds a fresh disposable image with a verified saved configuration.
Use `--scenario config/runtime/scenarios/main_stage1.json` with Easy/six-life/
two-Bomb options for the repaired first-stage regression (the pre-repair
`837b4b8` build stops on this route). Private MAIN `--fault-trace` emits gameplay,
bullet and decimal DIV checkpoints plus chained CPU exception frames;
`--debug-port-e9` captures them without losing boot-log smoke markers.
`main_progression.json` adds frequent shot-release gaps and balanced movement
for longer ordinary-game runs. It does not force stages or change product code.
`--cpu-debugger-receipt .analysis/runtime/emulators/primary-observer-v1215b/receipt.json`
uses the calibrated primary-emulator exception observer. After the completed
run, `inspect_th04_emulator_cpu_fault.py --run-dir RUN --require-fault` verifies
all executed products and locates captured code against the relocated MAIN/MAP.

## Next work

1. Retest dense Lunatic/Extra and the optional 36,000-cycle Windows profile;
   separate natural-route timing/audio from the completed synthetic pool control.
2. Inspect the completed ordinary sweep at
   `.analysis/runtime/candidates/native-empty-ring-v1217-20261002/run-sweep-v1222`.
   Validate later stages, endings, Extra and character/rank variants; the
   independent playable invincible image can expose additional integration bugs.
3. Compare rendering/audio under another PC-98 emulator before assigning
   original-and-native shared display artifacts to source bugs.
4. Keep semantic expansion stopped unless it blocks a concrete native owner.
   Continue native verdict, congratulations and registration/save;
   repair historical scaffold replay separately from native progress.

## Navigation

- [Architecture](ARCHITECTURE.md): artifact/ABI and source ownership.
- [Runtime](RUNTIME.md): pinned emulator and image setup.
- [Progress](PROGRESS.md): historical function acceptance.
- [Evidence index](reconstruction/README.md): focused historical investigations.
- `config/evidence.csv` / `config/knowledge.csv`: durable receipts and findings.

Historical checkpoints remain in Git and the ledgers. Old missing-header counts
and blockers are not the current work queue.
