# Windows x64 functional smoke — 2026-10-27

## Scope and acceptance

The user resumed native testing and authorized silent background Windows runs,
process-local input hooks, replay-based controls, and a temporary no-life-loss
runtime patch. Overall game flow is the acceptance target. Original DOS pixel
and physical timing parity are supporting work, not this preview's release
gates. Do not run further UBSan work for this task. Keep the user's active
Windows desktop and global input untouched.

No gameplay source or executable file was changed or rebuilt. The tested
Windows AMD64 PE32+ candidate is SHA-256
`b7aabad98c193ed1a425e5126bfa01a721b7f8f3dfa7949641b6270bd3493015`.
GNU reference SHA-256 is
`895ef3b036c072f77997f492f692021879d40832eacd9c69938752069f25449b`.
These are the retained v1497 products. All compiled C/C++/header inputs still
agree with that producer. The current 581-file consumer manifest adds test
controllers and updates Python automation; it is not a new product build.
The Japanese data HDI and FREECG98 font retain their pinned identities.

## Runtime observations

`verification.json` independently accepts nine scoped cases:

| Scenario | Result |
| --- | --- |
| Actual Windows hooked Win32/GDI window | 1,068 refreshes; menu/Marisa B entry, ordinary/keypad Return, movement, half-speed Shift movement, firing/release, Bomb, pause/resume, virtual focus loss/recovery, normal window close; zero audio opens |
| Unmodified ordinary route | 34,651 admissions; natural Game Over, registration and fresh OP; complete inputs, states, CFG and SCR equal the GNU reference |
| Normal Reimu A, no life loss | 90,294 admissions; all six stages, Good Ending `_ED000.TXT`, registration and fresh OP; actual clear mask 1 |
| Normal Marisa B, no life loss | 85,134 admissions; all six stages, Good Ending `_ED110.TXT`, registration and fresh OP; actual clear mask 2 |
| Earned Extra Reimu A, no life loss | 29,251 admissions; stage 6, Extra ending route, registration and fresh OP; actual clear mask 1 |
| Pause controls | Eight component character/resume/Quit/reentry cases |
| Game Over controls | Authored finite-wave component fixtures exercising real hits, Continue, rendering/storage and lifecycle |
| Score routes | Score dispatch, physical persistence, fresh OP and second MAIN, including expected I/O failures |
| Configuration | All four ranks/two paths, actual menu changes/save/reload, physically unlocked Extra and expected write failures |

All ten complete 16-bit score checksums are validated for the clear routes.
Extra consumes a copy of the physical SCR produced by this session's Normal
clear in a fresh process. Clear acceptance requires the requested shot bit in
an actual mask below 4, full stage coverage, the expected ending and return to
OP. Process exit 0 alone is insufficient. Initial exploratory route CFGs were
repaired by HostStore before the typed Normal setup; the final Reimu run starts
with a valid physical Normal/six-life/two-bomb configuration.

The window test uses real Win32 message/timer/GDI code on an inactive private
Windows desktop. An eight-byte IAT replacement for `GetForegroundWindow` at
candidate RVA `0x324D30` points to a test-owned x64 adapter returning an owned
HWND or zero. Only the spawned candidate is affected. Posted messages feed its
ordinary keyboard path; virtual focus loss also reaches its focus handler.
No `SwitchDesktop`, `SendInput`, global foreground change or audible launch is
used. This is instrumented input acceptance, not physical keyboard/controller
or Windows activation acceptance. The complete clear routes use the existing
logical input controller with `render_every=0`; they do not validate continuous
full-route presentation. The short window run records actual GDI screenshots.

The no-life-loss patch changes only the immediate at candidate RVA `0xDE432`:
`83 E8 01 88 42 19` becomes `83 E8 00 88 42 19` in
`player::Lifecycle::miss_update`, preserving ordinary hits, power loss,
respawns and stock HUD updates. The candidate file hash and full instruction
are checked before patching; memory is read back. A suspended owned process is
patched before its first instruction. Original DOS targets are never patched.
Clear results do not establish ordinary difficulty/balance or original-game
fidelity. The unmodified death/Continue checks remain separate.

## Replay and preview

The native branch owns `port64/verify_windows_background.ps1`,
`windows_background_controller.cs`, `verify_background_results.py`, and
`run_no_life_loss.ps1`. The controller requires a pinned muted version-1 JSON
plan and fresh outputs. Cases run serially on owned inactive desktops with a
768 MiB job limit, a 35% job CPU cap and below-normal priority. The retained
plans contain exact commands, identities and optional initial score/route data.

Private root index: `.analysis/host-smoke-20261027/`.
Windows case root:
`C:\Users\21992\AppData\Local\Temp\TH04-background-smoke-20261027`.
The independent reader runs from the native worktree:

```sh
python3 -B port64/verify_background_results.py \
  --manifest /ABS/DOS-ROOT/.analysis/host-smoke-20261027/suite-manifest.json \
  --output /ABS/DOS-ROOT/.analysis/host-smoke-20261027/FRESH-readback.json
```

The private preview is
`D:\Entertainment\Game\Touhou\th04-reconstruct`.
`Play.bat` starts ordinary gameplay; `Play-no-life-loss.bat` uses the attested
memory-only patch. The initial launchers were muted. The current [performance update](TH04_PORTABLE_RENDER_PERFORMANCE.md) enables audio in both manual BAT launchers; background tests remain muted. Both use separate local saves. The no-life-loss
profile contains this session's earned Normal/Extra test scores; ordinary saves
start separately. The manual patch launcher also passes an actual Windows
headless startup/BMP/exit check without opening a visible window.

## Rejected preparation and remaining limits

Earlier failed controllers stay failed: inactive-desktop foreground activation
was refused; an unadapted inactive-window message fixture violates the input
observer's focus invariant; old Linux automation incorrectly expected MAIN Esc
to close instead of pause. The retained GNU window control passes after sending
WM_DELETE_WINDOW. Short wall-clock pulses did not give the throttled exploratory
sanitizer enough samples; no sanitizer acceptance is claimed or needed here.

Unprepared diagnostic flags rejected missing stdout/checkpoint/phase/CFG inputs.
After explicit stdout and correct phase/config fixtures, Game Over, score and
configuration controls pass. The old Ending-screenshot flag remains an
unadmitted fixture with missing script checkpoint files; the complete natural
Normal/Extra routes above provide the accepted ending-flow evidence. Do not
relabel any failed prefix as an application failure or accepted test.

Manual review remains for physical input feel, controller hardware, audible
sound and continuous visual quality. No new pristine provenance, historical
exactness, DOS differential, hardware timing or full ordinary clear claim is
made. Test-only patches must remain separate from the ordinary preview.

Final root/native `scripts/ci.py`, tracking validation, independent result
readback and `git diff --check` pass. The owned Windows process audit records
zero remaining test processes. Retirement removes 404496432 logical bytes of
regenerable render output; commands, scalar/input/state/save witnesses and
selected window pictures remain. Physical allocation release was not measured.
