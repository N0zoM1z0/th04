# Native private-state retention

v1354 retains all 204 current programs, complete producer/consumer source
archives, compiler/CMake metadata, Linux window and fake-audio captures,
physical saves, controller failures, pinned inputs and preceding products.
Current intermediates and both terminal owned Windows stages are recoverable
through three archives under native `.analysis/port64/host-window-v1354/`.
All 299 members read back before deletion. The scoped pass retires 1,190
regenerable build files and 225 stage files, reporting 628,129,792 allocated
bytes net reclaimed; accounting excludes its final receipt. A separate
pre-build pass prunes 12 source-backed Python caches (278,528 allocated bytes).

Sources have two distinct identities: the frozen cold producer and the final
consumer with two corrected verifier scripts. All compiled inputs are raw-equal.
Cleanup protection is scoped to its interval; later authorized source edits
must keep the earlier producer/archive identity instead of restamping receipts.

Keep pinned assets/targets/tools, active caches/databases, complete current and
preceding source/program vectors, recorded inputs, physical saves and failures.
Prune only terminal owned stages and regenerable intermediates after recovery
and hash readback. Restore archives into fresh directories; use the persisted
`retention-before-v1.json` journal for original paths/member hashes. Never
blanket-delete `.analysis/`, run git clean over private state, or remove user saves.

Prior v1353 recovery and its failed attempts remain indexed by the prior
receipts and Git; their archives are preserved. Both final CIs pass. Additional terminal capture sharing retains all 324
BMP/PCM paths and complete byte hashes while reclaiming 210,509,824 allocated
bytes net after its journal. Source-backed post-CI cache pruning retires 957
files with 15,585,280 allocated bytes net after its journal. Receipt overhead
is excluded. Main build cleanup, capture sharing and cache accounting remain
separate. The first follow-up helper had a str/Path readback typo; corrected
full journal readbacks verify all captures/sources before acceptance.
