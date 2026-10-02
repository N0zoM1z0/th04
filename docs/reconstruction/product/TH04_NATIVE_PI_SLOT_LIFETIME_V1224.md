# Standalone PI slot lifetime after the ending

The Windows invincible build was reported to show only background or remnants
on the score-registration page after a Lunatic Good Ending; Esc then left a
black screen. The copied user HDI is preserved under
`.analysis/runtime/candidates/lunatic-ending-user-20261003/` (SHA-256
`91cafe8a9e6c4aa19ce7fdeb93b2a665da42b22a71f390c2e34ffe162e7aa0f2`).
This is a user runtime observation, not an independently captured MAINE frame.

Source inspection found a concrete standalone lifetime defect in
`src/shared/formats/pi.hpp`: `pi_free(slot)` called `graph_pi_free()` but kept
`pi_buffers[slot]` pointing at the freed DOS heap block. `pi_load()` calls
`pi_free()` before every load. MAINE repeatedly uses slot 0 while showing the
ending, staff roll, verdict and score screen. A later load could therefore
free a block that had already been returned to the heap, including a block
reused by another resource. The standalone branch now calls a shared
`pi_free()` function that clears the slot after freeing it. The historical
exact-replay macro retains its source shape. A first inline product repair
compiled but triggered a TLINK general error in OP's `selection.cpp`; moving
the ownership update into the shared producer linked OP cleanly.

`probe_th04_native_pi_decode_runtime.py` passes with two consecutive product
`pi_load()`/`pi_free()` cycles and verifies that each released slot is null.
The MAINE product builds and its far-call/vector audit passes. The independent
full Good Ending-to-registration visual comparison remains open. A private
direct-MAINE fixture was useful for exercising the route but skips OP startup
and shows different palette/page behavior; it is not evidence that the user
path is fixed. The score file from the user's session has valid section
checksums, but comparison with an older HDI cannot attribute its changed
sections to the Lunatic run or prove a new score was registered.

The user's saved `MIKO.CFG` is Lunatic with turbo enabled. Both MAIN bullet
update paths enter their bullet-count slowdown branch only when turbo is off.
Yuuka spell lag is therefore inferred to be CPU/render load until a stage-5
or final-stage frame trace identifies the hot operation. The Windows package
offers a 24,000-cycle profile and a 15,000-cycle reference launcher for the
next comparison; neither profile is a gameplay-speed acceptance Oracle.
