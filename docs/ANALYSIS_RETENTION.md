# Native private-state retention

v1363 archives and retires the unused historical mutable native
`.analysis/port64/ubsan-live-v1251/` build materialization. All936 files, modes,
sizes and SHA-256 values read back from a complete recovery archive before
retirement; a separate reader rechecks every archive member after retirement.
No process executable/cwd/argv/mapping refers to the old tree. Net252,231,680
allocated B (about240.5MiB) reclaimed after retaining the105,898,956-byte archive
and journal; final receipt overhead excluded. This preserves the current bytes
of an old mutable build, not a cold historical replay or refreshed acceptance.

Recovery: root `.analysis/cleanup/ubsan-old-build-v1363/` holds
`ubsan-live-v1251.tar.gz`, `retention-before-v1.json` with all original paths/
modes/hashes, and the independent readback. Extract into a fresh scratch root
(`tar -xzf ARCHIVE -C FRESH_DIR`), then verify every member against the journal
before use. Active v1356 programs and pinned helper/HDI/font/source archive
hashes remain unchanged; current traces, saves, user packages and toolchains are
excluded. The muted private-Xvfb Turbo0 candidate continues on the same PIDs;
no Windows GUI, host keys, audio device or new build is involved.

The v1361 Turbo0 candidate is now terminal failed-clear; its separate bad-save
Scores reader and final CIs pass. Final terminal-CI cache pruning retires962
source-backed caches/net15,650,816 allocated B, including now-unused port64
helpers. Receipt: `.analysis/cleanup/slowdown-terminal-caches-readback-v1361.json`.
Together with the earlier reader-CI interval (955 entries/net15,478,784 B), this
turn's two distinct cleanup intervals reclaim31,129,600 allocated B (about29.7MiB).
Programs, current failed trace/actions, saves, source archives and all negative
receipts remain for ordinary input-policy review; no new build is produced.

v1361 both final CIs pass (root includes live Ghidra/mutation replay). The
independent reader and eight controls create no build/game output. Source-backed
public-script caches retire955 files after source/protected hash readback,
net15,478,784 allocated B (about14.8MiB), subtracting the journal. Active port64
helper caches, program, trace, saves and frozen consumer snapshots are preserved.
Root receipt: `.analysis/cleanup/slowdown-reader-caches-readback-v1361.json`.

v1360 CIs pass on both branches, including root live Ghidra/mutation replay.
Scoped post-CI pruning retires955 source-backed public-script caches after full
source/protected hash readback, net15,478,784 allocated bytes (about14.8MiB),
subtracting the journal. Active port64 helper caches, program, source archive,
trace and physical saves are excluded. No new build intermediates are created.
Root receipt: `.analysis/cleanup/slowdown-source-caches-readback-v1360.json`.

v1359 final CIs pass on both branches, including root live Ghidra replay and
mutation controls. No new build intermediates are created. Post-CI cleanup
retires961 source-backed Python caches after all source and protected-input
hashes read back; net15,634,432 allocated bytes (about14.9MiB), subtracting the
journal. Programs, source archives, traces, physical saves and negative readers
remain. Root receipt: `.analysis/cleanup/host-storage-source-caches-readback-v1359.json`.

Post-final-CI pruning retires 1,018 source-backed public Python caches,
net 16,633,856 allocated bytes after the persisted journal and full source
hash readback. Root receipts: `.analysis/cleanup/full-window-post-ci-caches-v1356*.json`.

v1356 also archives and retires 1,190 terminal build intermediates after
complete member/hash readback, net 398,848,000 allocated bytes. A second
full archive retires 201 completed contract program materializations,
net 393,736,192 allocated bytes. All 204 current program bytes and
identities remain recoverable: three game programs stay live; restore
`contract-programs-recovery-v2.tar.gz` into `.analysis/product-v1356/`
before running CTest. The complete 485-input producer source vector,
CMake/link/compiler metadata, preceding 204 programs, failed recipes,
physical files and active private-Xvfb route remain intact. Independent
replay checks 3,254 hashes; package readback confirms 21 DOS / 13 native
v1354 installed files unchanged. Both CIs pass. Final receipt overhead
is excluded. Recovery journals: native `.analysis/port64/full-window-v1356/`.

v1356 retires only two terminal owned Windows startup staging directories.
All 155 files are preserved in a complete recovery archive and every member
was read back before deletion. Net logical bytes reclaimed: 36,333,457
(archive retained; final receipt overhead excluded). Original inputs,
current/preceding programs and user saves are untouched. Native receipts:
`.analysis/port64/full-window-v1356/windows-gui-stop-cleanup-v1.json` and
`windows-startup-stage-recovery-v1.tar.gz`. No new build was needed for that Windows stage cleanup.

v1355 scoped cleanup keeps all 204 programs, producer/consumer source archives,
compiler/CMake metadata, traces, physical files, captures and failed attempts.
It retires 1190 regenerable build files / 70 completed contract-stage files after
two full recovery archives / 144 members read back, net 596836352 allocated bytes.
An independent replay verifies 2847 protected hashes and all 1260 absent files.
The three earlier desktop stages retire 20 files, net 35110912 bytes; the terminal
GUI stage and archived failed consumer materialization retire 494 files,
net 22450176 bytes. Immutable capture sharing keeps 324 complete BMP/PCM paths
and hashes, net 210509824 bytes. Counts subtract their journals/archives but
exclude final receipt size. No original input, accepted program or save deleted.
Post-CI pruning retires 1020 source-backed Python caches, net 16822272 allocated
bytes; root `.analysis/cleanup/host-route-post-ci-caches-v1355.json` records
source/hash readback. Both CIs pass, including root live Ghidra replay/mutations.

Restore from native `.analysis/port64/host-route-v1355/` recovery archives and
member journals; retain distinct 481-input producer and consumer vectors.

## Previous v1354 recovery


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
