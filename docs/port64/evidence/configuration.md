# Native configuration file and OP boundaries

Historical v1323, 2026-10-09. Configuration-enabled native menus now load an independent
host `MIKO.CFG`, save at normal/Extra/demo entry and OP exit, and reload after
fresh OP or process restart. Every launch stays muted. This does not accept
original ZUN's first setup scene, sound playback, complete natural game routes,
physical PC-98 timing, current Windows execution or DOS exactness.

## Original evidence and native policy

Pinned OP is42290 bytes, SHA-256
`8fc3b67fa8470de15b4f2844d5623d0a93d7922fac16d82a25a90a378b516b0f`.
Its independently stub-restored69028-byte payload is SHA-256
`13222cb667e15c5034bd64c840a1db0a07c9acbb56e50f0bcf6025d12fe78d74`,
with804 relocations. Fresh preflights and packed OP database attestation pass.
The database is not a decoded-function Oracle. Provenance remains
candidate-local-attested. Relative segment0A74 executes at CS1A74/2A74 for
load segments1000/2000; DATA is relative0F34.

Original cfg_load0A74:000C..00AF reads ten bytes then closes the file. Six
bytes copy to resident rank, configured lives/Bombs, BGM, SE and raw Turbo.
Unsigned resident comparisons correct lives0/>6 to3, Bombs>2 to2, BGM/SE>=3
to0. Rank and Turbo are copied without correction. The original checksum is
not checked here. The native raw codec retains those widths, including raw
Turbo255; the typed host menu adapter handles supported boolean values.

Original cfg_save0A74:00B0..0132 opens for update, seeks0, writes six option
bytes, seeks9, writes their wrapping BYTE checksum and closes. Bytes6..8 and
any trailing file bytes remain unchanged. cfg_save_exit0A74:0133..01B0 instead
zeros its local record using actual F_SCOPY0000:4202..421B and writes ten
bytes at0; resident segment and debug bytes become zero. Trailing bytes still
remain because update-open does not truncate. The two paths are distinct.

Normal and Extra callers request cfg_save after the character menu succeeds;
canceling selection does not save. Demo requests it after blackout1 and before
MAIN execution. OP's ordinary DOS exit requests cfg_save_exit. Maintained DOS
source/caller findings route these boundaries; native file-operation semantics
are independently checked by executing the three original functions.

The host file lives beside independent `GENSOU.SCR`, under the existing native
save directory or `--save-dir`. It never writes the supplied HDI. Segment/debug
bytes are opaque file metadata and never become host pointers. Live saves
preserve them; OP exit clears them. A complete new record starts with zero
metadata and a defined checksum. Publication uses a reserved temporary
directory, writer flush/close and atomic replacement; failed writers propagate
before application phase changes and remove their temporary outputs.

Missing/short/bad-checksum records and unsupported rank/noncanonical Turbo are
explicitly repaired at the host boundary. Current repair uses existing native
menu defaults: Normal,3 lives,2 Bombs,FM86 BGM,FM SE,Turbo on. Prior ZUN
layout/source evidence describes missing-file defaults rankFF/FM26, a first
setup request and an uninitialized checksum. That launcher path is not replayed
in this batch. Native repair does not reproduce that undefined value or present
native defaults as original ZUN initialization. The historical routing is in
`docs/reconstruction/zun/TH04_ZUN_CFG_LAYOUT_V311.md` in the DOS checkout.
The first setup owner remains required alongside the audio work. Valid records
with out-of-range lives/Bombs/BGM/SE load through original OP corrections; the
physical record changes only at its next save boundary.

## Independent and frontend controls

`verify_configuration.py` executes original OP code at both relocated loads.
2112 controls cover all256 byte values in each of six load fields and randomized
load/live-save/exit-save records of10/11/29 bytes. The actual far structure-copy
helper runs. Complete option outputs, file bytes, ordered open/seek/read/write/
close requests, return-stack balance and unrelated resident guards agree.
Original DOS file consumers are explicit adapters; physical DOS filesystem
behavior and ZUN startup are outside that claim.

GNU and optimized UBSan consume the independent original reference. Seven
physical host controls cover valid, missing, short, bad-checksum, unsupported
rank, noncanonical bool and corrected ranges. Each saves, closes, reopens,
checks live metadata preservation, then exits and reopens the cleared record.
A failed configuration read is retained. A current source-only mutant that
leaves debug byte8 uncleared is rejected at trace line8256; mutant source,
driver snapshot, exact compile command and expected/actual trace remain private.

`verify_configuration_join.py` runs two separate muted application processes
per host.16 actual menu cases cover four ranks, ordinary/demo save boundaries,
all six options, bad/short/missing/unsupported startup data and restart into
ordinary MAIN. Options edits do not save early. Demo forces Hard/Turbo locally;
configured settings survive. A separately closed physical config is changed
during demo exit; fresh OP loads that file instead of retaining stale options.

One real Extra entry uses score-derived unlock/availability, without an unlock
adapter. The file retains configured6 lives/0 Bombs while Extra starts with
its fixed3/2 credits. Four failed writers exercise normal entry, demo entry,
keyboard OP Quit and window-close ownership; all remain OP with no live MAIN
and no temporary directory. Native GNU/UBSan scene file maps and captured views
are compared. They do not execute whole original OP or its complete pixels.

The interactive SDL and Win32 entry paths explicitly enable the configuration
owner before registration/score reading. Fresh OP reloads it before score-derived
menus. Older seeded component fixtures leave this owner disabled and retain
their earlier independent scope; their passing references do not establish
configuration integration. Configuration-enabled checks independently bind
the new owner. Current Windows runtime remains unavailable.

All three builds produce45 AMD64 programs each, bound to358 sources.44 CTests
pass per Linux host. Prior demo frontend references regress on both Linux hosts;
GNU Music Room and score-only MAINE routes also guard retained menu/MAIN paths.
Current receipts, failures, profiles and full uncommitted recovery are under
native `.analysis/port64/config-v1323/`. Producer manifests remain distinct
when source adds only frontend/driver gates; no old receipt is restamped.

The v1323 cleanup shares651 terminal duplicate outputs after complete byte/hash
comparison, retires8 regenerable Python caches andtwo experimental mutant
binaries, and reclaims412155904 allocated bytes (about393MiB).5233 protected
files are unchanged at that boundary. Current three caches,135 programs,
sources, private inputs and replay/failure references remain.

## Replay and frontier

Use fresh output directories. Completed captures may share immutable storage.

```sh
python3 port64/verify_configuration.py --target ../../targets/th04/op.exe \
  --decoded-dir ../../port64/op-unlock-v1317/decoded-original \
  --exe .analysis/port64/linux-live-v1251/th04-port64-configuration-contracts \
  --output-dir NEW
```

The frontend verifier requires the completed independent original directory,
pinned HDI, supplied font BMP and a private physical score fixture. Its launch
always includes `--mute`. Raw core helpers preserve unsupported byte fields;
the host repair policy must stay separate from the original comparison.

Next: first setup and audio request/state ownership while muted, complete natural
ordinary/Extra routes, current Linux/Windows save/restart and dense Lunatic
timing/performance. Git metadata remains read-only and Windows interop fails
before PowerShell. Current cross-builds do not accept Windows execution; full
source/evidence/root-document recovery replaces neither a commit nor push.

## v1324 setup policy supersedes v1323 repair defaults

Missing/short/bad-checksum or unsafe typed host records now use observed ZUN
six defaults FF0302010101, zero metadata and defined checksum07. Valid rankFF
is accepted as a pending setup request. Actual OP setup finishes to Normal
and selected modes, while physical persistence waits for the existing save
boundary. Closing during setup preserves pending rankFF. Raw OP codec widths,
metadata and tail rules above are unchanged. The earlier v1323 defaults and
receipts remain historical evidence. See [setup evidence](setup.md).

Current GNU/optimized UBSan repeat2112 raw controls/seven physical cases,
16 configuration-enabled menu cases, Extra andfour failed writers. Failure
fixtures complete actual setup before exercising their intended save boundary;
the rejected old fixture is retained. All launches stay muted.

Correction v1325: original ZUN six defaults use BGM2, which target OP text
labels stereo FM (FM86). The historical FM26 label above was wrong; raw
configuration values and original/native comparisons are unchanged.

## Current Windows replay v1332

Current actual Windows configuration phases0/1 pass with separate processes,
physical NTFS saves, Extra/demo/ordinary boundaries and four blocked writers.
The rejected text-mode CRLF captures are retained; the diagnostic stream now
uses binary mode and full file equality passes without normalization.
See [current Windows evidence](windows-current.md) for identities, nine-case
scope, negative records and retention. Full natural routes remain unaccepted.
