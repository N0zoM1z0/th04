# OP/MAINE/ZUN decoded-function acceptance plane (v508)

This is a reusable **artifact-local decoded** comparison contract, separate
from `config/units.csv` raw packed-file exactness. The eight initial rows in
`config/th04_decoded_function_acceptance.csv` cover six existing OP/MAINE
BGIMAGE `decoded-exact` functions and two ZUN `source-present` diagnostics.
No unit, function, or packed artifact was promoted in this packet.

`python3 scripts/decoded_function_acceptance.py` is a public static gate run
by preflight and CI. It joins each row to a reviewed authored boundary,
one source-present unit, real checked-in source, a complete decoded function
extent inside a declared physical producer, and artifact-scoped replay
evidence. Every `decoded-exact` row additionally requires a function-scoped
`raw-bytes` pass with equal target/candidate SHA-256s; producer-scoped boundary,
toolchain, OMF, cold, layout, and aggregate evidence must all pass. It rejects
overlap, cross-artifact credit, invented packed file offsets, source/backend
mismatch, missing evidence, and an exact boundary omitted from this ledger.
Public mutation tests cover target hash drift, candidate byte drift, truncation,
mis-scoping, and exact-state confusion.

Run a new cold artifact-local replay with a unique private output directory:

```bash
python3 scripts/decoded_function_acceptance.py --artifact th04-op
python3 scripts/decoded_function_acceptance.py --artifact th04-maine
python3 scripts/decoded_function_acceptance.py --artifact th04-zun
```

Successful wrapper replays now discard only the generated OP/MAINE A/B
`source` worktrees immediately after each backend has read and checked both
linked images. Backend and aggregate receipts and logs remain. This limits
peak disk usage as the backend count grows; pass `--keep-workdirs` only when
the expanded source/object trees are needed for debugging. The inputs under
`.analysis/gpt-web/`, pinned targets, and checked-in source are never pruned
by this option. A failed backend is left intact for diagnosis.

OP/MAINE backends now materialize independent compact v489 snapshots through
`scripts/probes/compact_op_maine_snapshot.py`. The helper keeps writable source
trees, the artifact's response-file link inputs, and its baseline EXE/MAP,
but omits unused object trees, generated listings, and Tup metadata. This
reduces each A/B worktree from about 27 MiB to about 11 MiB before the wrapper
removes it. It never hardlinks or symlinks a writable worktree to the retained
baseline. The v554 full OP and MAINE aggregate replays reproduce the earlier
linked-image hashes with this input closure; the pruning behavior is covered
by failure-preservation tests.

The v554 final control replays checked 17 OP and 20 MAINE slices with zero
raw differences in both cold rounds, and reproduced the prior compact
aggregate candidate-image and function-slice hashes. Their retained wrapper
receipts are `v554-op-compact-final-001/receipt.json` (SHA-256
`1c1533b0bc5602a5412c386c1690d3b8475cc9a908f0439742e0eaa051f41992`)
and `v554-maine-compact-final-001/receipt.json` (SHA-256
`c1422a5b7de9be61b5d483b69e9342b72ca9db0c5d8ba6d85325cac1e94e72ce`)
under `.analysis/reconstruction/probes/`. The ZUN control replay still has
13 and 130 raw differences in its two diagnostic C++ slices, respectively;
`v554-zun-control-final-001/receipt.json` has SHA-256
`45ae0f170c7bda7d29994319fb0c579e776414e9cc332ba9c0e40a9897bace37`.
No ZUN source or exactness promotion follows from this control.

OP/MAINE use the retained v489 source snapshots and v228 **target-derived**
DIET restores. The backend recompiles maintained BGIMAGE hybrid source via
TC86 `-B`/TASM, relinks both programs in two isolated rounds, and checks each
full ordered relocation table. The wrapper separately hashes and compares
every ledger function slice in both rounds. ZUN uses checked-in
`cfg_init.cpp`/`main.cpp` plus their transitive TH04 headers, then cold-links
the resident component against the pinned external `masters.lib` diagnostic
scaffold. Its old driver had a broken `HEADERS` import and a pruned v214
library path; both now use current attested inputs. The library SHA-256 remains
`6be41dbcfcf4504977165ccc44443525a29a01f85a1580e6ad0c620bf802faf6`.

| Artifact | Cold result | Receipt SHA-256 |
| --- | --- | --- |
| OP.EXE | Three BGIMAGE slices raw-zero; 804 ordered relocations exact | `77964f8bb4c705f74efba94d085ccc3a8502eb3e75925dafb6318b73d02c39f3` |
| MAINE.EXE | Three BGIMAGE slices raw-zero; 559 ordered relocations exact | `da1bd0d3dfa0bff2576f3af428b55eeee669f8bd3705f5d65a9a9f9f49f70d4d` |
| ZUN.COM | `cfg_init` 13 differing linked bytes; `_main` 130 differing bytes in its target-sized interval; zero accepted | `6542091d838059274c470c9f567c2e3bb2ba57d42a71f411cca99326908560b5` |

The private receipt paths are
`.analysis/reconstruction/probes/v508-decoded-op-001/receipt.json`,
`.analysis/reconstruction/probes/v508-decoded-maine-001/receipt.json`, and
`.analysis/reconstruction/probes/v508-decoded-zun-001/receipt.json`.
The ZUN component remains 6,360 bytes with 4,241 raw differences; its cold
candidate SHA-256 is
`a15ee1e7eac9616e9cd60656a00fb5700c7e20299efc2c0ab44bce6c27cf1dab`.
The 13-byte `cfg_init` linked mismatch is consistent with the six-byte
`_main` layout shift, but that is diagnostic, not a normalized exact pass.

These replays do **not** assert equal whole decoded-image lengths: OP/MAINE's
v489 program images are 3,228/3,220 bytes shorter than their target-restored
images until the separate BGM-BSS file-backing control is applied. Nor do
they assert independent TH04-only product builds or complete DIET-packed
file equality. The pinned targets retain `candidate-local-attested`
provenance.

To accept a new function, first review its physical boundary and source/TU
ownership. Add or extend a cold backend that actually compiles that source;
the current BGIMAGE backend is deliberately restricted to BGIMAGE, and the
ZUN backend to its two resident C++ TUs. Add function-scoped equal raw hashes
and producer-scoped evidence, update the decoded ledger and existing boundary
state, then run the artifact replay and affected aggregate. A source-only
compile or byte match in another artifact is insufficient. Packed-file
`units.csv` exact promotion still requires its own complete raw-file extent
and full exact Oracle set. The current ledger accepts **contiguous** reviewed
function extents (`body_span == body_size`); discontiguous tails/tables need a
reviewed piecewise-extent extension before they can enter this plane.
