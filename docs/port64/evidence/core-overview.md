# TH04 native x64 port

`port/modern-64` is a separate product based on the semantic DOS source. The
DOS build remains the behavioral reference and keeps its own Borland/TASM
acceptance rules. The portable product uses fixed-width state, ordinary host
pointers and host backends; it does not claim byte equality with PC-98 code.

The current preview runs Stages1 through6 including their waves, bosses,
dialogues and departures. Stage4 has both character-dependent NPC battles;
Stage5 joins Yuuka's seven attacks and thick lasers. Normal/Lunatic continue
through Stage6 waves, the complete pre-battle dialogue and Yuuka's final
battle, then all-clear and the appropriate Good Ending. Easy runs its separate
bad dialogue and Bad Ending. The native frontend now joins MAIN's score/run
statistics, mandatory fade, resource release and fresh MAINE lifecycle to all
eight Ending script/graphics routes. Staff Roll now completes its two backgrounds
and three dissolve families. The assessment screen now renders its original
grades and commentary, preserves the held-key release/press wait, then fades
to the original congratulations picture and its release/press wait. After its
blackout, the original100-refresh delay reaches score registration entry.
Registration/save remain next. See [congratulations](../../PORT64.md#congratulations-and-registration-entry),
[verdict graphics](../../PORT64.md#verdict-graphics-and-integration),
[Staff Roll](../../PORT64.md#staff-roll-integration) and
[MAIN-to-MAINE integration](../../PORT64.md#main-to-maine-ending-integration) for the current
acceptance scope. Earlier slices below retain their historical boundaries.
The final-boss [animation/motion helpers](../../PORT64.md#yuuka6-animation-and-motion-helpers)
and [cross/safety-circle entities](../../PORT64.md#yuuka6-cross-and-safety-circle-entities)
plus [gathering/attack helpers](../../PORT64.md#yuuka6-gathering-and-attack-helpers) and
[mirror/core dispatch](../../PORT64.md#yuuka6-mirror-and-core-dispatch) are
independently ported and now joined to the ordinary game loop.
