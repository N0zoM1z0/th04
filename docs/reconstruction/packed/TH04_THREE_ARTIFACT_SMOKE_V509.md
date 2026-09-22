# OP/MAINE/ZUN cold function smoke (v509)

This packet tests whether maintained source can traverse the non-MAIN cold
acceptance path. The pinned packed targets, MZ structure, and three live Ghidra
databases passed attestation on 2026-09-22. Canonicality is still
`candidate-local-attested`. Decoded comparisons do not create raw offsets in
the DIET-packed files or establish a standalone TH04 product build.

## OP.EXE and MAINE.EXE: new authored decoded-exact functions

The reviewed `vram_planes_set()` far function is 41 bytes in each artifact:
OP `SHARED` `0DA1:0002` / decoded load `0xDA12..0xDA3A`, and MAINE
`SHARED` `0CC7:000A` / `0xCC7A..0xCCA2`. It ends at `RETF`; the next
`frame_delay` begins immediately after. The same maintained natural C++ TU,
[`vram_planes.cpp`](../../../src/shared/hardware/vram_planes.cpp), is compiled
independently into each v489 artifact-local link scaffold. ReC98 is the
scaffold, not accepted source. The replay checks valid TC86 OMF, MAP ownership,
the full ordered MZ relocation list, raw complete function bytes, aggregate
program identity, and two isolated rounds.

Run `python3 scripts/probes/replay_th04_shared_vram.py --output-dir
.analysis/reconstruction/probes/NEW-UNIQUE-NAME`. Initial receipt:
`.analysis/reconstruction/probes/v509-shared-vram-001/receipt.json`, SHA-256
`b1566b35192a8a8fb68d4d8b14045965b823415371b0e543496a9990b1b423fd`.
After pinning the DOS runner digest explicitly, the focused replay passed
again at `v509-shared-vram-final/receipt.json`, SHA-256
`a654f571cea045e2b8bd3259eaef9bcfb5ed79b33d278a3bd945056be1c32782`.
Both rounds produced the same source OMF SHA-256
`88d72436b375e2b8aa27a79e9712cf0a04bf3a3daee415e6dc7dcc54f87f35b2`.
OP's complete target and candidate function SHA-256 is
`61209f3e66ab804442a484e2827402fd67c5de3da5a8ff47085bb70c3e213f52`;
MAINE's is `52fae504f84407d7119423f8545d49c19890c2b76b302ee5e6465e2588d35e35`.
Both have zero raw differences. All 804 OP and 559 MAINE ordered relocation
sites agree with their respective target-derived DIET restores. Both complete
candidate decoded program images remain identical to their v489 baselines;
only the independent shared `snd_load` two-byte target residual remains.

The two boundaries are `decoded-exact` in
`config/th04_decoded_function_acceptance.csv`. Their `units.csv` rows remain
`source-present`, because a decoded function has no honest packed-file
`file_offset`. `python3 scripts/decoded_function_acceptance.py --artifact
th04-op` (or `th04-maine`) runs both the existing BGIMAGE backend and the new
VRAM backend and compares each row only with the backend that compiled its
source. This establishes **one additional authored function exact per artifact**,
not whole-artifact exactness.

The combined four-row acceptance wrapper also passed both artifact-local cold
runs: OP receipt `v509-decoded-op-002/receipt.json` SHA-256
`9201ea317c8c70f9f5ffd4c86a0c0ec9c6dd381c98d2890f0a910e6bed70a505`;
MAINE receipt `v509-decoded-maine-001/receipt.json` SHA-256
`5894ddafa999fa44e9881ff007a93d58fee4b958e72646b116ac0eb9e9844503`.
All four per-artifact accepted rows are raw-zero in both rounds.
The static decoded-function gate now also rejects malformed producer-evidence
digests; a negative test covers the failure discovered during receipt review.

## ZUN.COM: exact support slice, authored gate still open

The graph-clear replay was rebased from pruned v214 paths to the retained v489
master library and transitive checked-in headers. Run
`python3 scripts/probes/replay_th04_zun_graph_clear.py --output-dir
.analysis/reconstruction/probes/NEW-UNIQUE-NAME`. Fresh receipt:
`.analysis/reconstruction/probes/v509-zun-graph-clear-001/receipt.json`,
SHA-256 `dfa44ee8fb708cf3a9252c4adb1c1736f497fe3e107feac621a0682e1c41a374`.
Two cold TASM/TLINK rounds compile checked-in
[`graph_clear.asm`](../../../src/shared/pc98/graph_clear.asm) and link its
complete 36-byte `_TEXT` contribution. That linked slice is raw-equal to the
target decoded payload `0xF64..0xF87`, SHA-256
`a210c6bc7dcf7fb2fb44e2e37d14d82d535f71511f0bbfda30d481c5da6c2a07`.
This is a **library-origin support** function and remains `source-present`,
not an accepted authored ZUN exact function. The full resident component
still differs at 4,241 bytes. Its natural `_main` is 246 versus 252 target
bytes; linked `cfg_init` differs at 13 bytes under that layout. Neither C++
function passes the decoded raw gate, and ZUN's authored exact count remains
zero. Next work must resolve that producer/layout dependency or find another
reviewed authored function with natural source; copying target ASM or inert
statements would not satisfy the gate.

The current decoded-authored diagnostic wrapper was also cold-replayed at
`v509-decoded-zun-001/receipt.json`, SHA-256
`6ed6039d0b4ad0a5a3cf5a845a9585f64145bc6d6c945071d40b325e4d37aaa8`:
`cfg_init` still has 13 raw differences and `_main` has 130 within its
target-sized interval. The 36-byte support match must not mask these failures.
