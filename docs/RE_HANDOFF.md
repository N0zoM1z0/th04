# TH04 current handoff

Updated 2026-10-04. The standalone PC-98 game is the behavioral reference:
checked-in TH04 source, successful builds, and normal gameplay. Native whole-build byte
equality is not required. The two remaining MAIN exactness cases are deferred
and retain their nonexact states. ReC98 implementations are adaptation inputs;
upstream exactness claims are not inherited. Current phase: native x64 integration after bounded semantic readability and
the native bullet-performance, scroll-pipeline, MAINE registration,
three-executable process-handoff, shared-random-ring, process-local-LCG and
item-lifecycle batches; semantic work is paused unless it blocks a port slice.

On `port/modern-64`, semantic work is paused at the user's stopping condition:
sufficient clarity for the current x64 slice, then implement and verify it.
The native slice runs ordinary Stage1 through midboss, pre-dialog, Orange,
post-dialog, clear bonus and the416/488 departure. Dialog resumes inside the
already entered frame; actors/RNG are not updated twice. Bonus drains through
the ordinary score owner. The shared enter/leave byte remains72 after enter,
then leave replaces bonus TRAM and clears the callback after reaching zero.
Graze/lives/Bombs and resident stage/ascii are published. Semantic remains stopped.
The GUI now replaces Stage2 resources at the actual next-stage request. Controlled MAIN
actor integration now continues through real Stage2 STD/MAP and its own midboss
to the pre-Kurumi dialog gate at6982. Stage2 chooses its actual four-pattern
callback at2600; do not reuse Stage1 behavior. Entry is96 frames, private phase2
retreats upward. Timeout after17 patterns skips collision and all defeat awards;
defeat requests score/Bomb/zap/shake/sparks. Quads tune only their first producer.
Hit parameter10 is a sound ID. Sprite geometry uses146..153 and consumes flash
only when drawn; invalid sprite>2 has undefined target SI and is rejected natively.

Stage actor preparation preserves seven actual owners' scalar metadata,
pending/decimal score,power/performance,input/velocity and process generation.
The same MAIN LCG supplies ring256/drop1/spark96 draws; the preceding928 reset/
seed controls remain independently replayed. The midboss2 comparator executes
MAIN13A9:1062..14D3/642C/6454/6486/64DE and0AAF:214A, with original
bullet/gather/random/hittest wrapper callees.9,282 controls/13,512 records agree
Linux/Wine/optimized UBSan, including four retained update/render sequences.
Spark/popups/Bomb/HP/video/audio consumers remain intercepted in CPU controls;
retained sequences omit ordinary other-actor updates. Native four-route
integration joins those implemented actor consumers and holds at Kurumi's gate.
No full original Stage2 or GUI pacing/exactness claim. Fourteen contracts,
previous64 natural Stage1 BMPs and32 Stage2 BMPs/36 counters agree on Linux,
Wine-hosted PE32+ and native Windows; optimized UBSan also agrees on Stage2.
Stage2 releases dynamic slots128..255, installs18 BFT/16 BMT sprites at128..161,
uses ST01 MPN/MAP for both characters and replaces palette/portrait/script owners.
Its pre-Kurumi dialog holds frame6982 and gameplay actors/RNG, then explicitly
holds the unported battle frontier. Original setup requests across five rank
seeds and all48 dialog controls/76 scenes have independent CPU checks with
graphics/file/audio consumers intercepted;57,188 opaque Kurumi portrait pixels
agree with independently decoded archive pixels. Root Windows preview and
`port64-preview/v1266` use this Stage1/Stage2 slice. Next implement Kurumi's
state/attacks/render, then later stages/death/Bomb/HUD/audio/save/Ending.
Semantic remains stopped unless a concrete port ambiguity requires it.
Current scope: [Stage2 visual resources and dialog](PORT64.md#stage2-visual-resources-and-dialog).
Receipts: `.analysis/port64/stage2-v1266/{resources-final,integration-review,native-windows-receipt}.json`,
`dialog-cpu-{linux,windows}/receipt.json`, `windows-export-receipt.json`, and
`.analysis/port64/verification-stage2-v1266/receipt.json`.
Current scope: [Stage2 midboss and actor integration](PORT64.md#stage2-midboss-and-actor-integration).
Receipts: `.analysis/port64/midboss2-v1265/cpu-{linux,windows,ubsan}-final/receipt.json`,
`session-{linux,windows,ubsan}-final/receipt.json`, `native-windows-midboss2.json`,
`native-windows-receipt.json`, `integration-review.json`, and
`.analysis/port64/verification-midboss2-v1265-final/receipt.json`.
Previous reset/seed scope: [Stage actor-session preparation](PORT64.md#stage-actor-session-preparation).
Current scope: [Stage enter and departure](PORT64.md#stage-enter-and-departure).
MAIN main01 0AAF:62B3/6349/6287 and main03 13A9:ACB3..AE86 agree4,331
controls/7,265 trace records on Linux/Wine/UBSan and actual Windows. Three
retained489-tick leave+score sequences preserve pending score at stage advance;
TH04 ordinary leave has no forced flush. Original gameplay-loop 0AAF:0098..0212
places actor prefix before boss callback, items/gathers/overlay/clock/score after it.
Twelve contracts and eight natural Stage1 scenarios/64 BMPs/72 counters agree
across Linux/Wine/UBSan/native Windows. Windows package is `port64-preview/v1263`.
Current receipts: `.analysis/port64/leave-v1263/cpu-linux-attested-final/receipt.json`,
`cpu-{windows,ubsan}-attested-final/receipt.json`, `integration-review.json`,
`native-windows-cpu.json`, `native-windows-receipt.json`, and
`.analysis/port64/verification-leave-v1263-final/receipt.json`.
The initial CPU fixture's native-aligned Bh pack wrote frame1 as256; explicit
little-endian packed <Bh fixes the adapter. Do not modernize target arithmetic
to fit malformed fixtures. New60-frame BMP differs only by8,726 actual enter
gaiji57 mask pixels; every other pixel including HUD is unchanged from v1262.
Current score scope: [Score drain and extends](PORT64.md#score-drain-and-extends).
MAIN main01 0AAF:6BD4/6BA2/4316, actual1874 raise and DATA2134:4349
ownership agree4,690 original CPU transitions on Linux/Wine/UBSan, including
926 retained-state steps. Continue aliases score digit0 in the target; highest
byte carry, low-word frame-delta write and direct extend-digit predicates remain
intact. Saved high-score data, life-HUD/audio/popup consumers remain absent.
The preceding score batch passed eleven contracts and40 natural BMPs across
Linux/Wine/UBSan and actual Windows headless execution. Its60-frame image
changes only960 score/hiscore pixels in TRAM56 rows4/6; its other pixels remain
identical to v1261. DOS products and normal/invincible launchers stay separate.
Score receipts: `.analysis/port64/score-v1262/cpu-{linux,windows,ubsan}-attested/receipt.json`,
`integration-review.json`, `native-windows-receipt.json` and
`.analysis/port64/verification-score-v1262-attested/receipt.json`.
Current bonus owner and scope: [Stage-clear bonus](PORT64.md#stage-clear-and-all-clear-bonus).
Original MAIN main03 13A9:9C31/9E06 and99FE/9A89/9AFF/9B59, plus actual
main01 0AAF:1874/188E performance arithmetic, agree1,837 complete ordinary /
all-clear state and ordered text/gaiji/HUD controls on Linux, Wine-PE32+ and
optimized UBSan/bounds. Preserve unsigned16 components, ten-point units,
separate truncated factors, timeout-zero/Bomb increment and unmodified
performance thresholds. Extra life scaling and zero-life wrapping are covered
only by isolated CPU controls; later-stage live consumers remain unported.
CPU receipts: `.analysis/port64/bonus-v1261/cpu-{linux,windows,ubsan}-attested/receipt.json`.
Current cross-product manifest/receipt:
`.analysis/port64/verification-bonus-v1261-final/receipt.json`.
The preceding bonus batch passed ten contracts and40 natural BMPs/counters across Linux/Wine/UBSan and actual
native Windows headless execution; prior combat/midboss/Orange snapshots and
first four dialog checkpoints remain unchanged. Bonus updates delta/Bomb once
and its colored TRAM remains bright over graphics tone60. Native death/Bomb/
Continue counters are still absent/zero; their effects have CPU controls only.
Review/native-Windows receipts: `.analysis/port64/bonus-v1261/integration-review.json`
and `native-windows-receipt.json`. Windows package `port64-preview/v1261` and
root `start-th04-port64.bat` use private `play-normal.hdi`/`FREECG98.bmp`.
The timeout DATA candidate has one extra full-width space at pinned
DATA2134:1F79; portable text is corrected. DOS source/link layout is unchanged,
recorded at `.analysis/port64/bonus-v1261/candidate-text-mismatch.json`.
Dialog still preserves script cursor, waits release/new press and freezes game
frames/RNG. Earlier48 cases/76 scenes/18,768 events/768 activation controls
remain under `.analysis/port64/dialog-v1260/`. Actual pre-dialog clean/load of
ST00.BB1/BB2 fixes the former diagnostic's wrong battle sprite bank.
No DOS source or exact state changes. Original complete color/page/fade pacing,
GUI pacing, audio/HUD/death/Bomb, later-stage resources and Ending/save remain
outside this x64 slice. Later new-run initialization must reset accumulated graze
at its actual owner; the current controls start with a fresh application state.
The native product is rebased through the latest item semantics. Linux ELF64
and Wine-hosted Windows PE32+ pass the existing OP/resource/process/random
contracts and a new live MAIN slice. Game confirmation now starts a timed
window with the original player sprite, held arrows and Shift slowdown.
The 32-slot item pool preserves movement, attraction, pickup/scoring and
next-frame release. Seven item types appear only in the explicit headless
60-frame fixture; both hosts now produce `a6341ebd...` with player Q12.4 position
5232,2960. Independent original MAIN `main_01 0AAF:5DA8` CPU replay agrees
with native movement across 256 masks; this is a bounded primitive comparison,
not full gameplay or original timing. GNU UBSan/bounds also passes. Private
receipts: `.analysis/port64/verification-background-v1252/receipt.json` and
`.analysis/port64/background-v1252/`. Original initial tile fill and scroll
CPU code agree with the host 25x24 ring and state across 6,715 frames through
termination; all 128 MPN tiles match 32,768 original-renderer indexed pixels.
Both character windows pass held-key/Shift tests over the real Stage 1 scrolling
background. Scroll graphics calls/EGC are intercepted, not a complete video
replay. No DOS source or acceptance state changes.
The next bounded slice now adds all four player-shot routes and ten power
levels, the 68-slot pool, original trigger cadence, hit animation/damage and
Marisa option lasers. MAIN updates player/shots/items in original order and
samples held Z on both host backends. Independent original CPU replay agrees
on 4,072 checkpoints: 2,216 firing, 512 trigger, 64 update, 640 hit and 640
repeated-hit cases. Spark requests are recorded, with spark RNG/rendering and
sound deferred. A negative control observes original allocator reads past
slot 67; the host safely stops at the actual capacity. Both character windows
pass held-Z firing/release against original BFNT pixels; all four headless
full-power BMPs agree across hosts. Cross-host receipt is
`.analysis/port64/verification-shots-v1253-final/receipt.json`; CPU/window
receipts are under `.analysis/port64/shots-v1253/`. Sanitizer replay passes.
No DOS source or exact acceptance changes were needed.
The current bounded slice adds all-seven STD wave parsing and the complete
52-opcode enemy VM, 32 enemy slots, shot damage, collision requests, homing,
kill scoring/drops and MIKO32/ST00 sprites. Independent original CPU comparison
passes 9,414 VM vectors, 896 hit/lifecycle cases, all seven wave schedules and
12,600 Easy/Normal/Lunatic Stage 1 update/render frames. Enemy animation/flash
advances once per simulation frame. The 6,715-frame background oracle also
compares the published prior-frame scroll delta, including the stop boundary.
Both x64 products run real 1,200-frame shooting/enemy/drop fixtures with no
injected entities: 26 kills, score delta 5,761, power 7; BMPs/counters agree.
Cross-host receipt: `.analysis/port64/verification-enemies-v1254/receipt.json`;
CPU receipts: `.analysis/port64/enemies-v1254/cpu-{linux,windows,ubsan}-final/receipt.json`.
The latest bounded slice connects enemy FIRE/autofire immediately to the same
ring and separate 240-pellet/200-large pools. Rank/performance tuning, 14 groups,
nine special motions, cloud phases, graze/collision, clear/zap and original
optional count-based delay are portable fixed-width state. Both products show
natural Lunatic Stage 1 bullets and retain earlier fixture hashes/counters.
Original MAIN CPU replay agrees on 36,216 tune/add/update cases, 2,400 joint
Normal/Lunatic STD/enemy/bullet frames and 72 pellet glyph alignment/Y-roll
controls. A repeated lower row starts at Y+3, producing an 8x8 white/purple
glyph. Original zero-count rings independently fault at loaded 33A9:9648/9669;
the host keeps the playable DOS skip guard. Scope: MAIN main_03 13A9,
update 8E38, tune/wrappers 9435..94F6, pool DS:5A22, load2000 DS8000;
glyph main_01 0AAF:1EAC/1F3E. Spark/HUD/point-number/gather callees are intercepted;
their effects/RNG, complete routes and natural timing remain excluded.
Cross-host receipt: `.analysis/port64/verification-bullets-v1255/receipt.json`;
CPU receipts under `.analysis/port64/bullets-v1255/`. Five contracts and
UBSan/bounds pass. Windows execution is under Wine; native Windows pacing is
untested. Player hits are exposed but death is still absent.
The next completed slice adds 96 sparks and 16 gather circles, same-process
spark-angle initialization, immediate free-slot random draws, wrapped circular
bursts, gravity/age/reclaim ordering, saved templates and delayed regular
release without retuning. Original foreground order now includes procedural
gather/spark masks. Independent original CPU comparison agrees on 3,075 full
state/render cases, 648 aligned/Y-roll glyph controls and 2,400 Normal/Lunatic
joint frames with explicitly injected shot/gather inputs. Original effect and
shot-hit/bullet callees execute in the joint test; drops/HUD/audio/graphics
remain intercepted. Scope: MAIN main_01 0AAF:1824/1776/17C2/1710; main_03
13A9:039A/03FC and gather0027/0091/013E/01CC/1008, load2000 DS8000.
Spark/gather pools are DS:53E2/9292; spark attempt offset DS:41F4. Original
zero-circle DIV faults at loaded33A9:043A; host guard is explicit.
Linux, Wine/Win32 and UBSan/bounds pass six contracts and matching fixtures.
Real Stage 1 held-Z now produces24 kills/score5720/power6; natural Lunatic
900-frame fixtures contain6 live bullets per character. Earlier counts are
historical partial-RNG results. Cross-host receipt:
`.analysis/port64/verification-effects-v1256-final2/receipt.json`; scoped CPU
receipts under `.analysis/port64/effects-v1256/cpu-{linux,windows,ubsan}-final/`.
DOS source and exact acceptance states are unchanged. Next connect the Stage 1
control/midboss boundary, then bosses, stage transitions/visuals, HUD,
Bomb/player death, audio, Ending and saved-data I/O. Semantic readability
remains paused until a concrete native ambiguity. See [the x64 port handoff](PORT64.md).

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


The separate `port/modern-64` branch has an initial native resource/PI decoder
slice under `port64/`. Linux ELF64 and Windows PE32+ x64 builds both run on the
attested HDI; the Windows build also ran under the Windows host command line.
`CONG10.PI`/`CONG14.PI` packed pixel hashes match the 16-bit DOS probe, and
Linux/Windows main and Options BMP outputs are byte-identical. The portable
menu/config and resident process-handoff contracts pass on both hosts. The x64
core also implements one `SharedRandomRing` rather than reproducing the two
historical accessor copies. Both hosts verify the descending 256-call fill,
overlapping samples, shared cursor, AND/MOD consumption order, all cursor
positions, explicit `0xFF00` boundary sample and a defined zero-divisor
exception after cursor advance. `Lcg32` now supplies the exact unsigned 32-bit
update, 15-bit output, default/demo vectors and production ring fill. The
application model keeps resident, OP, MAIN and MAINE state separate and makes
the route-dependent verdict re-seed explicit. The first MAIN item contract now
preserves automatic/miss drop random consumption, fixed-pool truncation,
fixed-width score/performance state and wrapped pickup tests. Linux and Windows
x64 agree, and UBSan/bounds passes the historical above-cap big-power case
without an out-of-range host access. The live motion/item-pool slice now renders original BFNT player/item cels;
remaining gameplay call sites stay unported. A playable native game
still requires the remaining
hardware and runtime boundaries described in `port64/README.md`.

## Current state

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
4. Keep semantic work paused unless a native ambiguity requires a bounded
   clarification; continue the native gameplay queue above. Repair the historical
   scaffold digest/replay surface separately before a new cold exact claim.

## Navigation

- [Architecture](ARCHITECTURE.md): artifact/ABI and source ownership.
- [Runtime](RUNTIME.md): pinned emulator and image setup.
- [Progress](PROGRESS.md): historical function acceptance.
- [Evidence index](reconstruction/README.md): focused historical investigations.
- `config/evidence.csv` / `config/knowledge.csv`: durable receipts and findings.

Historical checkpoints remain in Git and the ledgers. Old missing-header counts
and blockers are not the current work queue.
