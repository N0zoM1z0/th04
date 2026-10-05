# Postgame evidence

Historical bounded results, preserved from `docs/PORT64.md`. Current state is
[the port overview](../../PORT64.md). Original CPU execution and adapter scope
remain explicit; successful component controls do not accept complete gameplay.

## Staff Roll integration

The v1293 native MAINE owner runs the complete `staffroll_animate` sequence
for both Good and Bad Ending. `staff_roll` separates the ordered graphics/file/
sound requests from their host consumers; both the GUI and deterministic route
runner use the same owner. The preceding Ending graphics pages transfer once,
then its script/PI/text-box owner releases. MAINE generation, resident counters
and process RNG remain unchanged. Staff Roll releases its background snapshot
and six CDG slots, completes the final blackout and holds at verdict entry.

The dissolve producer preserves radial, diagonal and axis displacements,
unsigned angle wrapping, signed polar/SAR rounding and the original 63-frame
alternation. Fade and music waits remain blocking. Keys never skip Staff Roll;
active music requires a real reported measure, while the inactive backend uses
64/160-frame fallbacks. The resulting deterministic inactive-audio run contains
10,396 requests and 3,967 ticks. These are native scheduling counters, not
measured physical PC-98 timing or synthesized audio.

Two hardware details matter: `graph_copy_page(destination)` copies the opposite
page and leaves access on the destination; `BGIMAGER` restores WORD-aligned
rectangles with TH04's inclusive `h+1` row loop. The last SFF7 expansion touches
row400, so full-page comparisons cover visible rows0..399 and do not claim the
heap/offscreen allocation tail. CDG opaque draws clear the mask then OR color
planes, while the displaced plane helper uses white GRCG masks. The shared
read-only `cdg_image.hpp` replaces the GUI's private CDG/CD2 parser without
embedding original files or turning DOS segment fields into host pointers.

Verification at `.analysis/port64/staff-roll-v1293` binds the 208-file source
manifest `830f7c96cca70b471124d408cbad3ece832d94f7964d62a18604338d7cc487b9`:

- Eight original CPU request controls execute all eight bodies at decoded
  MAINE_01 `0A05:0E80..1736`, using loads1000/2000 and initial angles0/7/64/255.
  The complete producer digest is independently checked against the recovered
  payload; original polar at `0CC7:0260` executes its signed multiply/SAR.
  File, sound, graphics and VSync consumers are explicit adapters.
- 268 direct original CPU graphics controls execute `0CC7:0408` plane drawing,
  `0CC7:06E6` opaque CDG and `0CC7:0A86` background restore. They cover all18
  CDG assets, four color planes, alignments0/7/15, varying seeded backgrounds,
  zero-height inclusive copies and the visible portion of the row400 write.
  A supplied GRCG adapter applies masks; ordinary target OR/copy instructions
  execute. Unsupported requests fail closed.
- An independent original-request-driven raster compares332 complete indexed
  pages and166 palette/page/lifetime checkpoints. CDG planes are independently
  unpacked; the two PI backgrounds use a recorded v1292 decoder regression
  dependency, not an original-CPU PI decoding claim. A whole-page byte mutation
  is rejected. GNU, Wine and optimized UBSan pass all controls.
- Three fast incremental builds each produce31 AMD64 executables and pass all
  30 CTests.29 GNU and29 UBSan executables remain raw-identical to v1292. The
  changed GUI and cutscene consumer pass full original-controlled regressions;
  there is no PE body equality claim from the prior hash-only snapshot.
- Each host runs24 natural menu/STD/dialogue/boss/Good-or-Bad-Ending routes,
  then the entire Staff Roll to verdict entry. The preceding576 Ending pages,
  288 palette/state and288 RGB checks remain intact;48 final Staff Roll pages
  and24 palettes agree with the independently controlled component gallery.
  Resident publication, resource release and fresh MAINE lifetime stay checked.

The actual-Windows consumer is `verify_maine_join_windows.ps1 -StaffDirectory
CONTROLS`; it also checks the original handoff/counter/fade controls and all30
contracts. Its original/reference producer scope stays separate from Windows
execution. Source snapshots and original CPU streams remain immutable; only
completed derived media may be archived after full SHA-256 readback.

Target provenance remains candidate-local-attested, including the recovered
MAINE payload7495ae43. The Ghidra MAINE database attests its packed wrapper,
not a distinct recovered-payload semantics Oracle. No DOS source or acceptance
ledger changes. Verdict, congratulations, score persistence, Extra/death/Bomb/
Continue/full HUD/audio/config and a complete original-game video comparison
remain outside this batch. General semantic work stays stopped.

Actual Windows passes all30 contracts, eight original request streams,268
kernel controls,332 complete component pages and24 natural Ending/Staff Roll
routes. The route consumer compares1,248 binary/state files; independent Python
readback checks the original Ending/RGB reference and final Staff Roll pages.
Native and root CI pass. The validated preview is published at
`D:\Entertainment\Game\Touhou\th04-reconstruct\port64-preview\v1293-staff-roll`;
root `start-th04-port64.bat` is updated and previousv1292 is backed up. All2,206
pre-existing Windows files outside the two authorized native replacements keep
their hashes. The versioned launcher uses its own verified original HDI/font;
publication does not launch the GUI or change DOS products/scripts/config/saves.

A focused follow-up reads all eight original Ending request streams: every
copy0 has access1 beforehand and an explicit access0 immediately afterward.
Their visible-page regressions remain valid under the existing request-adapter
state convention. Do not reuse that convention as generic graph_copy_page
semantics for new owners; Staff Roll uses the independently reviewed destination
semantics. `ending-copy-caller-review.json` preserves this narrowed caller proof.

After all consumers finish,6,977 completed v1293 render buffers/BMPs are losslessly
gzip-archived, releasing1.98GiB. Seven explicit inputs retain hashes; supplementary
post-archive verification checks93 current native executables and456 expanded
original-controlled Ending/font reference buffers against accepted pre-archive
receipts. Two final GNU Staff Roll pages, original request/fixture streams,
PI decoder baseline, current build caches and Windows inputs remain available.
Restore archived direct-consumer paths with `gzip -d -- PATH.bin.gz` or
`PATH.bmp.gz`; `media-archive-receipt.json` and `archive-readback.json` retain
member/readback and protected-product/reference digests.

## Verdict calculation and clock

v1294 ports the complete recovered MAINE0A05:1737..20F8 owner to
`port64/verdict.cpp`. `Plan` computes the assessment and owns the ordered
graphics/file/palette/wait requests. `Script` consumes them with explicit
refresh and key waits. These are native components; the GUI still holds at
the v1293 verdict-entry frontier. No synthetic cutscene script, copied
instruction array, DOS pointer alias or host floating-point rate is used.

Source comments retain the operations affecting results: percentages divide
before multiplying, accumulation wraps as DWORD, signed division truncates
toward zero, frame rates narrow to WORD after division by10, and graze doubling
wraps AX before zero extension. Completion overrides STD to44000 for Good
and12000 for completed Extra. Chance bonus re-seeds MAINE LCG from resident
menu-time rand and draws once only if item penalty is nonzero. Result exposes
the continued LCG and changed STD for later publication at calculation time;
it does not itself mutate application resident state or replace a process.

Original DATA0E53:071A is the initialized-zero subtraction flag. The separate
BSS0E53:3F9C completion toggle does not feed that helper: fresh percentages
all add, including completion and slowdown. Fixed-two-digit mode is initialized
DATA0743. Skill/rank are3F9E/3FA2. The30-byte commentary buffer starts3FA3;
its byte28 terminator is3FBF. CP932 file records retain30-byte stride. Assessment
is hidden if `(frames>>1)<=slow_frames`, without opening commentary. Valid
scores cover26 rows, including line0/no seek for skill at least1500000.

`verify_verdict.py` executes all original bodies/switch tables and
irand0000:1C5A..1C83.916 fixtures at both load1000/2000 compare complete
consumer requests, CP932/gaiji strings, skill/cap/rank, resident STD, RNG,
independent subtraction/fixed/toggle globals and file lifetime. Coverage includes
legal rank/life/bomb/end/Turbo combinations, all26 commentary records, miss15
and Bomb30 edges, BCD thresholds, invalid slowdown, WORD/DWORD wrap, equal/zero
denominators and wrapped hundreds glyphs terminating a gaiji string.

Ten further controls execute original black-in0000:0622, black-out0666,
frame_delay0CC7:0033 and input_wait0CC7:020A. Only VSync, keyboard samples
and palette-display consumers are adapted. Ordered request refresh times,
changed palette tones and completion times match native scheduling at both
loads. Release combines previous/current samples; a fresh press resumes requests
in the same scheduler call. Zero wait budget never expires. Profiles include
initially-held Enter, one-refresh release, a press during release and a
one-refresh fresh press. These are bounded modeled-refresh controls, not
physical PC-98 pacing, audio synthesis or rendered-pixel evidence.

GNU8.4Release, MinGW13-posix AMD64 and optimized GNU UBSan/bounds fast builds
each produce31 products and pass30CTests. Three native consumers match916
cases and10 clocks. `verify_verdict_windows.ps1` also runs30 contracts and
the same comparisons on actual Windows; independent Python output readback
checks original hashes.213-file manifest:
6c846b7fb01bfa03c11a2a9d5f7c0e896d7da3c69c5c8b6c98a77dcffd707268.
Receipts:.analysis/port64/verdict-v1294.30GNU/30UBSan products, including
the game executable, are raw-identical to v1293. PE metadata changes on relink;
no preceding PE body equality is claimed. Native/root CI pass.

v1294 validates the calculation/clock component only. Its Windows preview,
DOS source, original targets and exact acceptance remain unchanged. The
graphics and application-state publication are verified separately below.

## Verdict graphics and integration

v1295 extracts `cutscene::Canvas` from Ending's script owner. The canvas owns
two indexed pages, the PI slot, saved text-box pixels and palette, borrowing
only immutable assets. `verdict::Scene` composes this canvas with the verified
Plan/Script; `_UDE.TXT` supplies fixed-width commentary records and is never
parsed as a fabricated cutscene. Full-string CP932 and gaiji rendering preserve
ANK/SJIS advances, weight, color and NUL termination. Page copying now implements
the original destination/opposite-page contract, including the selected access
page. The eight old Ending callers explicitly use access1/copy0/access0, so
their complete visible-page references remain valid after this correction.

MAINE transfers both completed Staff Roll pages once, then releases the Staff
owner. Verdict construction and the complete UDE background fade leave resident
STD and the MAINE LCG untouched. At the first completion digit request it
publishes STD; at the chance digit request it re-seeds the real MAINE LCG and
consumes exactly the original conditional draw. No new process or generation
is created. A seeded contract uses resident rand3 and previous STD123 to make
early or repeated publication observable, independently of headless routes
whose immediate menu confirmation leaves resident rand0. Holding a key and
host repaint do not repeat calculation or alter pixels. After release and a
fresh press, the original final blackout completes. Good/Easy Bad route to
`congratulations_pending`; other Bad ranks route to `registration_pending`.
These are explicit unfinished owners, not score-save completion.

`verify_verdict_pixels.py` uses complete original verdict requests and executes
the full original FAR Pascal text kernel at recovered `0CC7:058C..06EB` and
gaiji-string kernel at `0000:36B6..375E`. Eighty assessment fixtures exercise
all26 commentary rows, the invalid assessment, all5 rank labels and width/
truncation/termination boundaries. The527 distinct full-string drawing calls
agree at loads1000/2000; all160 complete indexed pages,80 palettes and page/
tone/request states agree with the native canvas. CGROM and GRCG are explicit
supplied-font/write adapters. UDE.PI decoding is regressed against the retained
v1294 executable, not claimed as original CPU PI decoding or physical video.

Fast GNU8.4Release, MinGW13-posix AMD64 and optimized UBSan/bounds builds each
produce31 executables and pass30CTests. All three execute the previous916
calculation and10 clock controls and the80 complete-page cases. Each also
passes24 natural menu/STD/dialogue/boss/Ending/Staff Roll/verdict routes: the
preceding576 Ending pages,288 palettes/states and288 RGB frames remain equal;
the48 final Staff pages remain equal; fresh original scoring on the actual
published resident inputs plus original full-string kernels validates48
verdict pages,24 palettes and24 computed RGB frames per host. This route has
no player death/Bomb/Continue/Extra or audio implementation.

Runtime-tested216-file manifest is
`fef77a46355aba231a0c02ed2dd6d3d0da3f092066bbd0131510cd1ef143707c`.
The English launcher description was then corrected; only
`port64/start-th04-port64.bat` differs in release manifest
`501137c49beedd70be9eedf6c30bb3712a207deeaa780afa3bbbada58ff200a8`.
The source-binding receipt verifies all executable, verifier and build inputs
remain identical to the tested manifest. Receipts are below
`.analysis/port64/verdict-v1295`; generated development media are losslessly
archived with restoration instructions in the root
`.analysis/cleanup/development-media-20261005/receipt.json`.

Actual Windows executes the30 contracts,916 calculation/10 clock controls,
80 graphics cases,8 Staff Roll request streams and268 Staff graphics kernels.
Its24 natural routes agree on1,344 complete page/palette/RGB/state files.
Independent Python readback rechecks the retained outputs and original font/
scoring controls, with CRLF normalization restricted to text streams. The
Windows reference consumer requires all499 expanded Staff page/palette/state
files and268 expanded kernel files; archived `.gz` siblings are excluded,
but a missing expanded reference fails rather than silently reducing coverage.

Windows preview is `D:\Entertainment\Game\Touhou\th04-reconstruct\port64-preview\v1295-verdict`;
the root `start-th04-port64.bat` selects the updated GUI. The versioned package
contains31 verified AMD64 products and its own attested original HDI/font.
Previousv1293 GUI/launcher remain in `previous-v1293`;69 unrelated existing
Windows files retain their complete hashes. No GUI is launched automatically.
Finished generated buffers are losslessly archived after all consumers finish;
the80-case GNU page reference remains expanded. All other archived captures
require restoration before direct replay, including the598 temporarily expanded
Staff references. The archive/member manifests and restoration commands live
in `media-archive-receipt.json`; it records the diagnosed self-log false positive
in the first final protection check and the independent full successful reread.

Next implement congratulations and registration/save against the original
control flow. General semantic expansion remains stopped unless a concrete
port ambiguity requires it. Native whole-build exactness is not required;
DOS source, original targets and historical acceptance remain separate.


## Congratulations and registration entry

v1296 joins `maine::Congratulations` after verdict. It selects `CONGxy.pi` by
resident character/rank, accesses page1, loads/applies/puts/frees the real PI
slot0, copies page1 to0, fades in at speed1, waits for a full key release and a
fresh press, then fades out at speed4. It transfers both pages and releases the
verdict owner without starting another MAINE generation or changing resident
counters/LCG. `maine::Animation` owns the existing verdict refresh/key/fade
algorithm independently of score calculation, so congratulations needs no
dummy score Plan or fabricated Ending script. Source comments explain the
before/after-refresh key OR and independent repaint behavior.

Good Ending and Easy Bad Ending display the picture. Other Bad ranks skip it.
Both paths request song fade4 and consume exactly100 further refreshes before
`registration_pending`, including while Enter stays held. The preview holds
there because registration/save is still unported. Native seeded branches
check this distinction, the100th-refresh boundary, one sound request and a
stable frontier; a non-Easy Bad fixture has its congratulations asset removed.

`verify_congratulations.py` attests all400 bytes of recovered `_main` at
MAINE`0A05:00B2..0241` (payload`A102..A292`, SHA-256`9a44bbf5...`). Original
instructions select filenames and branches; full original fade/key/counter
loops execute at load segments1000/2000. Thirty-two distinct Good/Bad/Extra/
score-only entry fixtures and missing-CFG controls preserve all256 resident
bytes. Extra's registration-before-congratulations-before-verdict order stays
separate from Normal; this is original branch evidence, not Extra integration.
Ending/Staff/verdict/register, initialization, PI calls, sound and process
execution are explicit guarded adapters. The PI palette wrapper and original
far memcpy run rather than discarding the wrapper's initial palette_show.
An early adapter omission caused a first-tone clock mismatch and is retained
as a rejected development experiment, not a native game defect.

Ten character/rank pictures pass50 original fade/key profiles and20 complete
native pages,10 palettes and page/access/tone/request states. Original picture
bytes and a retained v1294 native PI decoder provide the pixel dependency;
these controls do not claim original CPU PI decoding or physical PC-98 VRAM.
All three hosts freshly rerun the full original main/clock producer. Previously
verified verdict916 state/request fixtures and10 clocks remain unchanged;
80 original-controlled verdict graphics cases still execute527 original font
kernels at two loads and match160 pages. All24 natural menu/STD/dialogue/boss/
Ending/Staff/verdict/congratulations paths pass on GNU, Wine, optimized UBSan
and actual Windows. Each preserves previous576 Ending pages,48 final Staff
pages,48 verdict pages and adds48 congratulations pages/24 palettes/24 RGB.
MAINE generation3, resident statistics and continued RNG remain stable through
held input, repaint, confirmation and the registration delay.

Three fast builds produce31 AMD64 executables and pass30CTests each. Frozen
222-file manifest`4c872c8aa01bad662f7c43367a2055cc5a6b2e0a3441ad859a74789b4a4dd1a5`
binds all93 products and the English launcher before testing. Actual Windows
checks1,440 route files,50 clocks,20 component pages and preceding Staff/
verdict controls. Python independently rechecks actual Windows indexed/RGB
outputs and original scoring/font kernels; pixel/palette/state/request/clock
mutations reject. The older numeric PowerShell receipt's source field describes
its original reference producer; candidate executable hashes are independently
bound to the new build inventory. No physical timing/audio or saved-score claim.

GNU8.4 requires its separate `stdc++fs` archive. The current newer host shared
libstdc++ exports filesystem symbols but its path lifetime crashes with this
compiler ABI; the same isolated probe crashes without the archive and exits0
with it. CMake links the active archive for GNU versions below9. This is a
compiler-observed current-host compatibility result, separate from TH04
semantics; all native products/contract controls pass after the correction.
Windows versioned package is `D:\Entertainment\Game\Touhou\th04-reconstruct\port64-preview\v1296-congratulations`;
root `start-th04-port64.bat` launches the updated native GUI. All31 products,
owned original HDI/font and previousv1295 GUI/launcher rollback are retained.
All106 unrelated existing Windows files keep hashes; no GUI auto-launch.
Receipts and exact commands live at `.analysis/port64/post-verdict-v1296`.
Completed5,564 generated buffers are losslessly tar/zstd-archived with every
member's full size/hash readback. Net2,094MiB reclaimed includes598 temporary
Staff raw expansions;12,025 protected files remain identical. GNU80-case
verdict and10-picture congratulations references stay expanded for the next
Windows consumer, alongside all three fast caches. Restore other captures
before direct replay;`media-archive-receipt.json` records exact commands.
DOS source and exact/unit/function acceptance are unchanged. General semantic
work remains stopped; next port registration, score-file persistence and the
fresh OP return, followed by remaining complete-game owners.
