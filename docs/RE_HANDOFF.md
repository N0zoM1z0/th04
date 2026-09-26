# TH04 reconstruction handoff

Updated 2026-09-26 after the v825 OP EGC rectangle-copy hybrid closure. This is the
current resume index; use
`python3 scripts/status.py`, `config/units.csv`, and the function-boundary and
decoded-acceptance ledgers for live counts. `docs/RE_ROADMAP.md` gives the next
work order; `docs/reconstruction/README.md` routes focused evidence. Versioned
notes and historical receipt paths are snapshots, not current acceptance.

## Resume checks

```sh
git status --short --branch
python3 scripts/preflight.py
python3 scripts/status.py
python3 scripts/audit_compat_dependencies.py --check
python3 scripts/boundary_review/validate_function_boundary_ledger.py
```

The four local targets pass size, SHA-256, format, and MZ-structure checks.
Their provenance is still `candidate-local-attested`, not proof of pristine
release media. Re-attest the active Ghidra database before new target
observations. Run only one writable Borland/Wine replay at a time and limit CPU
use; this host's focused replays use `taskset -c 0,1 nice -n 10`.

## Accepted state and remaining blockers

| Artifact | Reviewed authored boundaries | Exact authored functions | Blocked | Original-ASM observations |
| --- | ---: | ---: | ---: | ---: |
| OP.EXE | 93 / 93 | 89 | 4 | 16 reviewed |
| MAIN.EXE | 495 / 495 | 492 | 3 | 73 attestation entries; 6 provisional |
| MAINE.EXE | 72 / 72 | 63 | 9 | 15 reviewed |
| ZUN.COM | 3 / 3 | 3 | 0 | 12 reviewed |

MAIN's reviewed file-backed authored extent has 83,442 / 83,469 exact bytes.
Its 27-byte remainder belongs to `carpet_lighting_put_new` (23), checkerboard
(2), and `snd_load` (2). OP has 14,295 accepted decoded source-owner bytes of
14,458 tracked; MAINE has 11,187 / 12,553; ZUN has 442 / 442. These decoded
counts do not give a packed-file byte denominator or whole-artifact exactness.
Original-ASM observations are outside the authored C/C++ counts.

OP's four blocked functions and MAINE's nine blocked functions have reviewed
physical boundaries. v821 closes OP `scoredat_decode` and `scoredat_encode`
with maintained hybrid source: all control/data flow stays C++, while the
single 8-bit ROR primitive is independently corroborated by pre-decompilation
TH03 OP/MAINL codec bodies. Focused v821 replay and the archived canonical
current-ledger replay are raw-zero; the latter checks all 87 accepted OP slices.
This does not establish original-source spelling or packed-file exactness.

v822 materially narrows `SND_SE_PLAY` and `_snd_se_update` without promoting
either function. MAIN and OP share the complete 0x86 `th04/snd_se.cpp` fixed
producer, and a temporary helper-shaped candidate reproduces both function
bodies, the full producer, the OP EXE/MAP, and all 804 relocations in two cold
rounds. The required `BX=SP` and BL/BH helper spelling, however, first appears
in pinned ReC98 commit `c85f444b...` whose subject is `[Decompilation]` and
whose own comments tell modders to replace those forms. This is target-derived
provenance, so the two functions remain blocked. The v822 diagnostic receipt is
`v822-op-snd-se-shared-diagnostic-receipt.json`, SHA-256
`2509adb3b0153514025544f0b2b55aa399ddca52c0a4e5e884e28ca19f0696ef`.

v824 closes the internal 63-byte OP `egc_start_copy` helper. v825 then closes
the adjacent 111-byte `egc_copy_rect_1_to_0_16` outer body with a narrowed
hybrid source: ordinary TC4J owns parameter loads and rectangle arithmetic,
while only bounded CLD/SHL/immediate-page-OUT/STOSW/LOOP primitives remain
symbolic. TH05 OP/MAINE descendant bodies and earlier release-target machine
code provide independent mechanism evidence. Two cold v825 links reproduce the
complete `0xB0` producer, accepted OP EXE/MAP, and all 804 relocations.
Canonical v825 checks all 89 accepted OP slices raw-zero. v825 focused receipt
SHA-256 `984291bce653fe242c33003e85eedd1572c71e062f7e0cec02c3840a52ec649d`;
canonical receipt SHA-256
`5df5f441a94e5ce3aadfdd102b84abdba1ffcb4730e92bcdd329b91429b65eca`.

v823 then closes the code-generation mechanism for 234-byte SND_LOAD without
granting source credit. Two cold wrapper builds replacing only _BX=_AX with
TC4J integrated inline asm reproduce the complete reviewed function raw-zero;
natural versus diagnostic OP program images differ only at 0xDE8B..0xDE8C,
while the MAP owner and all 804 ordered relocations stay identical. The pinned
v401 snapshot contains 345 unique TC86 4.02 objects and exactly one other
89 C3; its source explicitly uses asm { mov bx, ax; } and comes from a ReC98
[Decompilation] commit. The TH04 candidate line itself also comes from
[Decompilation] [th04] snd_load(). SND_LOAD therefore remains blocked solely
on independent authored-source provenance. Diagnostic receipt
v823-op-snd-load-provenance-receipt.json, SHA-256
b958943a35c7916ab4a8bc80a9f2dd97bcc25a968ff4a315547f71d6dc37f161.

The remaining OP blockers are `nopoly_b_put`, `SND_LOAD`, `SND_SE_PLAY`,
and `_snd_se_update`.
v820's compiler-path negative remains valid for ordinary TC4J / `-B` lowering;
only the SCORE acceptance decision is superseded by v821's new provenance.
See the [v821 SCORE codec closure](reconstruction/op-maine/TH04_OP_SCORE_CODECS_HYBRID_V821.md),
[v822 shared-sound provenance bound](reconstruction/op-maine/TH04_OP_SND_SE_SHARED_V822.md),
[v823 SND_LOAD provenance bound](reconstruction/op-maine/TH04_OP_SND_LOAD_PROVENANCE_V823.md),
[v824 EGC-start hybrid closure](reconstruction/op-maine/TH04_OP_EGC_START_HYBRID_V824.md),
[v825 EGC rectangle-copy hybrid closure](reconstruction/op-maine/TH04_OP_EGC_COPY_HYBRID_V825.md),
[OP strict frontier](reconstruction/op-maine/TH04_OP_STRICT_FRONTIER_V766.md),
and [MAINE strict frontier](reconstruction/op-maine/TH04_MAINE_STRICT_FRONTIER_V732.md).
Do not substitute target-derived inline ASM, explicit register forcing, or
inert optimizer barriers without independent provenance. All 16 OP and 15
MAINE original-ASM function-like entries now have reviewed boundaries and
source-backed raw-identical modules; the prior MAINE provisional-cut statement
is superseded by v815.

| Shared/original-style ASM source | OP load segment:offset | MAINE load segment:offset | Focused evidence |
| --- | --- | --- | --- |
| `CDG_LOAD`, `0x164` | `0DA1:0B6A` | `0CC7:0B08` | [v797 and v815](reconstruction/op-maine/TH04_SHARED_CDG_LOAD_V797.md) |
| `CDG_PUT_8`, `0x9E` | `0DA1:05FE` | `0CC7:06E6` | [v799](reconstruction/op-maine/TH04_SHARED_CDG_PUT_V799.md) |
| `INPUT_S`, `0x10A` | `0DA1:07CC` | `0CC7:081A` | [v802](reconstruction/op-maine/TH04_SHARED_INPUT_V802.md) |
| `BGIMAGE_PUT_RECT_16`, `0x82` | `0DA1:0AE8` | `0CC7:0A86` | [v805](reconstruction/op-maine/TH04_SHARED_BGIMAGER_V805.md) |
| `_hflip_lut_generate`, `0x1E` | `0DA1:0134` | `0CC7:01EC` | [v808 and v812](reconstruction/op-maine/TH04_OP_HFLIP_LUT_V808.md) |
| `GRAPH_PUTSA_FX`, `0x15A` code + `0x40` data | `0DA1:04A4`, data `0F34:0A00` | `0CC7:058C` | [v809 and v813](reconstruction/op-maine/TH04_OP_GRAPH_PUTSA_FX_V809.md) |

OP also has its local `CDG_PUT_NOCOLORS_8` (`0DA1:0282`, 0x52-byte module)
and shared `CDG_PUT_NOALPHA_8` (`0DA1:0766`, 0x66-byte module). MAINE has local
`CDG_PUT_PLANE` (`0CC7:0408`, 0x9A-byte module). Their [v806](reconstruction/op-maine/TH04_OP_CDG_NOCOLORS_V806.md),
[v807](reconstruction/op-maine/TH04_OP_CDG_NOALPHA_V807.md), and
[v814](reconstruction/op-maine/TH04_MAINE_CDG_PLANE_V814.md) focused A/B links
match complete decoded module bytes and ordered relocations. All OP/MAINE
packed-file offsets remain unknown. The shared CDG and input modules also
passed focused MAIN cold replay; source placement and include composition are
replay inputs, so changes require affected-unit cold replay.

ZUN's natural Tiny-model MEMCHK `_main` at COM payload `0x26A7` was its first
exact authored function (38 bytes). Its complete 4,066-byte component cold-links
raw-identically with maintained `DOS_PUTS2` and `DOS_MAXFREE`; those helpers are
library support, not authored-function credit. See the [MEMCHK note](reconstruction/zun/TH04_ZUN_MEMCHK_NATURAL_EXACT_V773.md).

Maintained symbolic original-style ASM cold-links the 1,141-byte ZUNINIT
component at decoded `0x6F3..0xB67`, 223-byte launcher selector, 8-byte mover,
68-byte outer stub, and 926-byte ONGCHK component. The source-driven composite
replay rebuilds these groups and reproduces the 13,422-byte decoded flat
payload. That older composite integration still uses an external usage asset and a
resident-candidate path, so it remains a diagnostic flat comparison even
though the resident component is independently exact now. Earlier mixed flats repacked with pinned DIET 1.45f to a
byte-identical 7,754-byte MZ target; that does not make the product source
exact. See [ZUNINIT](reconstruction/zun/TH04_ZUNINIT_SYMBOLIC_COMPONENT_V785.md)
and the [composite note](reconstruction/zun/TH04_ZUN_MIXED_COMPOSITE_V788.md).

Resident cfg_init at COM payload 0xDCF and _main at 0xE67 are now
decoded-exact. v817 found a real compiler/source mechanism rather than an inert
barrier: the maintained /R not-resident branch jumps to the no-space failure
return, while TC4J -B plus pinned TASM32 emits the target 252-byte selective
tail. Direct TC4J still emits 246 bytes and remains the negative control. Two
cold resident links produce the target-identical 6,360-byte component, so
cfg_init also links raw-zero. v819 canonical acceptance then raw-compares all
three ZUN authored functions at zero differences. The ZUN resident notes carry
the focused producer and canonical receipt details.

## Private inputs and cleanup

The canonical cold aggregate receipts in
`.analysis/reconstruction/receipt-archive/` remain verified:

| Artifact | Receipt | SHA-256 |
| --- | --- | --- |
| OP | `v825-op-egc-copy-canonical-receipt.json` | `5df5f441a94e5ce3aadfdd102b84abdba1ffcb4730e92bcdd329b91429b65eca` |
| MAINE | `v727-maine-staff-dissolves-canonical-receipt.json` | `d86732f3c46baf5c8b9fe79d65abf4476cdd870353c1de96483bc48b5a632287` |
| ZUN | v819-zun-resident-canonical-receipt.json | fe59d4624229bdc111a427d41144b6b6ca93973d729f570831c28805bba03508 |

Preserve `.analysis/targets/`, `.analysis/toolchain/`, `.analysis/ghidra/`,
`.analysis/runtime/images/zun.hdi`, the v401/v402/v489 source snapshots,
DIET replay inputs, and the configured v546 ZUN runtime inventory. Expanded focused probe worktrees have been pruned again after v821. Before
deletion, 1,860 top-level result/receipt files were checksum-verified into
`focused-probe-heads-v821-20260926.tar.zst` with an adjacent manifest and
archive checksum. Probe scratch now retains only the configured
`v546-zun-runtime-inventory-001` input. The stable v824 EGC-start focused/canonical receipts and earlier accepted
receipts live directly under `.analysis/reconstruction/receipt-archive/`.
These private archives are ignored and exist only on this workspace; a fresh
clone must regenerate evidence from checked-in commands. Historical paths into
pruned worktrees are provenance, not live input promises. Use
`scripts/prune_analysis.py` in dry-run mode before future cleanup; its
probe/exact-replay apply paths verify archive coverage before deletion.

Finish future changes with the focused comparison, `python3 scripts/ci.py`,
`git diff --check`, and an updated handoff when phase or blockers change.
