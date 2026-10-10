# TH04 current handoff

The user is actively using the Windows host. Do not launch Windows GUI
tests, activate foreground windows or inject host keys. Keep every launch
muted; use headless checks or private Linux Xvfb instead. Actual Windows
window/input acceptance stays open under this constraint.

Both final CIs pass, including root live Ghidra replay/mutations. Current
host-window/recovery receipts retain distinct producer/consumer identities.
All launches remain muted.

Updated 2026-10-10. Current focus: resumed x64 implementation on its separate
branch; DOS demo state is retained. This handoff
indexes verified state; detailed experiments belong in focused notes and CSV
ledgers. General semantic work has reached its stopping condition: resume it
only for an ambiguity that blocks a concrete native port owner.

## Products and claim boundaries

| Product | State | Authority |
| --- | --- | --- |
| Historical reconstruction | OP 93/93, MAIN 493/495, MAINE 72/72, ZUN 3/3 accepted authored functions | [Generated progress](PROGRESS.md), acceptance ledgers |
| Standalone DOS PC-98 game | Four products build from maintained local source without master.lib or ReC98 product includes; repaired normal and invincible variants | [DOS operation](DOS_BUILD.md), [hardware findings](PC98_HARDWARE_REUSE.md) |
| Semantic DOS source | Asset, memory, input/timing, scroll, bullet/VM/shot/item, RNG, score and process contracts clarified | [Semantic summary](SEMANTIC_READABILITY.md) |
| Linux/Windows x64 | Separate `port/modern-64` branch; component-tested normal stages and cutscenes; complete game still unfinished | [Port status and TODO](PORTING_STATUS.md) |

Function acceptance is not whole-file exactness. OP/MAINE/ZUN counts cover
recovered payload functions, not original packed-file extents. MAIN's carpet
and checkerboard cases remain deferred; no acceptance is promoted by the
native fixes or this documentation cleanup. Targets remain
`candidate-local-attested` (a provenance gap).

## DOS verification frontier

- The user reports complete Normal routes/Endings/save and earlier invincible
  Easy/Lunatic runs. These are manual Windows observations.
- Recorded ordinary controls cover startup, OP options/Music Room/config
  persistence, Orange clear, Stage 2 entry, the repaired Kurumi empty-ring
  failure and Stage 3 entry. Seeded Good Endings reach registration and save
  the expected section; their final black frames do not accept fresh OP.
- Upper-left pellet corruption is confirmed and repaired by full EAX clearing;
  seven ordinary checkpoints exclude the old mark. The Stage 6 stripe's
  connection to initial scroll state remains inferred, with user confirmation
  that the stripe disappeared.
- Scalar/CPU/I-O controls reject planar and bullet drawing regressions. A
  440-bullet Lunatic/Turbo fixture measures improvement, including the extreme
  all-cloud phase. It is not a natural full Lunatic route or Windows FPS test.
- Full natural dense Lunatic timing/audio, the optional Windows 36,000-cycle
  profile and a second PC-98 emulator remain validation TODOs. New DOS
  performance work is outside the current native batch.

See [reusable hardware contracts and limits](PC98_HARDWARE_REUSE.md) for each
repair, replay entrypoint and evidence/knowledge routing.

## Native x64 frontier

The v1360 GNU Turbo0/ReimuA candidate is terminal and failed the true-clear
gate. Complete trace has88,267 refreshes: six stages reached, Final Stage last
frame11,267/miss13/respawn33/invincibility154 immediately enters MAINE; all physical
masks remain0x19. No all-clear/complete dense-route acceptance. Inner Bad Ending
is source-routed/inferred. Separate new private Scores reader passes795 refreshes
with unchanged physical hashes/zeroaudio; the original failed controller never
started its own reader. All owned jobs are now terminal.

Within this failed candidate, natural>=320 has416 samples/206 slowdown2 and
>=400 has125/63. Complete deadline/terminal reduction passes; >=400 update
P95/P99=8.33/12.27ms, no update exceeds its own admission period. These strengthen
bounded slowdown observations, not successful-route or uninstrumented/physical
performance acceptance. Before another Turbo0 attempt, review ordinary Bomb
input policy: fatal snapshot still has1 Bomb and advice0x20. This is a candidate
policy gap, not a proved game defect. Windows GUI/host keys/audio remain disabled.

v1361 independent `verify_natural_slowdown.py` rechecks complete raw traces,
program/original inputs, CFG, MAIN identity/credit, registration Esc, physical
rename/true clear/nineother partitions and separate Scores restart. Completed
GNU Turbo1 passes route-only with dense acceptance false. Eight live/Turbo/density/
checksum-valid mask/snapshot/deadline controls reject; scratch clones retire.
Reader receipts: native `.analysis/port64/slowdown-consumer-v1361/`.

Retained actual private-Xvfb route acceptance is GNU ReimuA only:

| Route | Complete route + independent Scores refreshes | Physical outcome |
| --- | --- | --- |
| Normal/Turbo1 | 89,008 +794 | Six stages/noContinue, Esc/freshOP, real selected mask1 |
| Lunatic/Turbo1 | 88,927 +790 | Six stages/noContinue; final frame13,633/lives2/miss11/score5,179,856; section3mask1 |
| Extra | 30,388 +790 | NoContinue/full eight A gaiji/credit0/real mask1; nineother partitions and CFG retained |

Unplayed0x19 contains bit0 but native OP normalizes masks>3 to0. Require mask<4
and requested shot bit at both final file and actual rename. Prior UBSan Normal
all-clear/admission is revoked: all final masks stay0x19 after Final Stage miss13
immediately enters MAINE. Bad Ending is source-routed/inferred; no Game Over
scene alone does not prove clear. Its reached-stages/save/Esc/freshOP/restart/
clock/zeroaudio observations remain valid. Old green receipts stay historical.

Registration, Bomb/hit/death/lives/HUD/GameOver/Continue, six stages, Endings,
Extra, Scores, MusicRoom/demo/unlocks/config and muted sound owners have scoped
component/integration evidence. Actual stationary GNU/UBSan Continue cases
freeze MAIN then genuinely resume, store CONTINUE entries and independently
restart. Ten GNU OS setup/corrupt-file cases pass6,305 refreshes/20 renames:
unfinished setup close preserves rankFF/noSCR; ordinary setup keys precede
score creation; bad CFG/first-last SCR recover; valid tails/ranges/metadata and
two fresh readers pass. Generic traces do not expose every inner Ending phase.

Natural GNU Turbo1 Lunatic reaches440 bullets; >=400 has369 samples/update
P95=5.07ms/P99=11.04ms and one19.89ms update over its17.73ms period. Dense samples
have no slowdown2. Current Turbo0 requires complete>=320/>=400 slowdown2 gates;
shared WSL/private Xvfb/advice/trace costs prevent uninstrumented FPS claims.
All27 muted startup combinations passGNU/UBSan; Windows retains19 cases only.

Cold v1356 producer remains485 inputs00af24f7 and204 program identities,
67 contracts per Linux host plus held-input regressions. v1356 Windows is
cross-compiled only; earlier v1355 actual contracts pass but owned-window
foreground input rejects. Do not launch Windows GUI/activate/inject host keys
or open audio backend/device while the user uses the host. Native consumer491
inputs437d7e36 change only Python readers/filelist; every compiled input remains
unchanged. No new build or historical exact/target-provenance promotion.

Remaining: this full Turbo0 terminal/dense verdict, broader character/shot/rank/
Ending/Continue/Extra host routes, actual Windows input/display and uninstrumented
performance. Physical audio remains untested under the mute constraint. Do not
reopen general semantic work or the two deferred exact MAIN cases without a
concrete native blocker. Native subject notes route evidence details; root
[porting status](PORTING_STATUS.md) indexes TODOs, and
[retention](ANALYSIS_RETENTION.md) indexes scoped cleanup/recovery. User DOS/
experimental packages and mutable saves remain untouched.

## Windows DOS demo package

The demo directory retains `start-th04-normal.bat` (ordinary damage) and
`start-th04.bat` (separately compiled invincible MAIN), plus their two unchanged
images/products, standard 24,000-cycle profiles, emulator/font and English
source builder. Independent saves are preserved by full-image hash readback.
Native previews and optional launchers are archived outside that directory.
Windows `Build-TH04.ps1 -CheckOnly -Normal` passes; no rebuild or game launch
was performed. See [retention](ANALYSIS_RETENTION.md) for recovery.

## Working commands

```sh
git status --short
python3 scripts/preflight.py
python3 scripts/status.py
python3 scripts/build.py --help
python3 scripts/catalog/index.py list --category hardware
python3 scripts/ci.py
git diff --check
```

Only one Borland/Wine writer at a time. Use fresh probe output paths. Follow
[DOS build and testing](DOS_BUILD.md) for publication and Windows fast builds;
[script catalog](../scripts/README.md) for the full command map;
[analysis retention](ANALYSIS_RETENTION.md) before deleting private state.

## Navigation

- [Documentation map](README.md), [architecture](ARCHITECTURE.md),
  [workflow](RE_WORKFLOW.md), [source layout](SOURCE_LAYOUT.md).
- [Evidence index](reconstruction/README.md), [knowledge policy](KNOWLEDGE_BASE.md).
- `config/units.csv`, authored/decoded function ledgers: accepted ownership.
- `config/evidence.csv`, `config/knowledge.csv`: observations and reusable findings.

Historical handoff detail is retained in Git (pre-cleanup `a4f7991`) and the
subject notes. Old build/package names and private receipt paths are provenance,
not the current work queue or a promise of expanded artifact retention.
