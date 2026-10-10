# Native private-state retention

Both final CIs pass, including root live Ghidra replay/mutations. Final readback
checks 8,640 retained hashes. Post-CI cleanup separately retires 1,014 public
source-backed Python caches and preserves their source hashes, reclaiming
16,433,152 allocated bytes net. Cache journal/receipt:
root `.analysis/cleanup/audio-output-post-ci-caches-v1353{,-before}.json`.

Keep pinned game-data inputs, toolchains, active caches, complete current and
preceding program/source vectors, recorded inputs, physical saves and evidence.
Prune only terminal owned stages and regenerable intermediates after archived
recovery and full hash readback. Use fresh output paths; retained equal capture
hardlinks are immutable. Never use blanket git clean or delete .analysis.

v1353 preserves current/preceding AMD64 programs, frozen sources/compiler/link
metadata, complete fake-transport frontend/Continue captures, physical final
saves and both rejected attempts. Three archives under
`.analysis/port64/audio-output-v1353/` recover closed first-candidate
intermediates, both owned Windows stages and final static link inputs.

Two scoped passes report 1,494,827,008 allocated bytes reclaimed. They retire
970 first-candidate intermediates, 1,177 final regenerable files and 872 owned
stage files; 350 full-byte-identical BMP/PCM paths share immutable storage.
Independent readback verifies all 1,915 archive members and 2,320/8,636 protected
hashes for the two intervals. Source protection describes the cleanup interval;
authorized later changes retain the earlier producer archive. Final CI cache
cleanup and final readback overhead are accounted separately.

Restore archives into fresh directories. Read `retention-before-v1.json` and
`retention-before-v2.json` for original paths, complete member hashes, sources,
programs and compiler/CMake metadata. `retention-readback-v2.json` checks both
passes independently. The failed compiler snapshot and Windows mutable-input
plan remain failed, with their logs and exact recovery material retained.
