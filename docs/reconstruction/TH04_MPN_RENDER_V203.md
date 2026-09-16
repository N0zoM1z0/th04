# TH04 MAIN MPN renderer reconstruction (v203)

## Scope

v203 reviews and reconstructs the game-owned four-plane `.MPN` renderer that
historical target-derived assembly names `sub_3680`.

The reviewed target extent is:

- artifact: `MAIN.EXE`;
- link segment/offset: `_TEXT 0000:3680`;
- MZ load-module extent: `0x3680..0x36F4`;
- file extent: `0x4E80..0x4EF4`;
- size: `0x75 / 117` bytes;
- target slice SHA-256:
  `70b048108a2279b0246b32199d65fa77633e2280792fd179309539d2deb74d13`.

Raw target decode closes the body through `RETF 8`. No MZ relocation site
lies inside the extent. The following load byte at `0x36F5` is not part of the
renderer: the emitting TASM listing proves that it is the `EVEN` byte emitted by
the immediately following MASTER.LIB `_BGM_BELL_ORG` function macro, whose body
starts at `0x36F6`.

Fresh target-bound Ghidra constructs one contiguous 117-byte FAR function at
analysis address `0x13680`, reports no callees, and reports exactly one caller:
the independently exact v195 `MPN_LOAD` wrapper at analysis `0x1B8FC`.
Ghidra is navigation evidence only. Its text renderer reverses the apparent
operand direction for the segment-register opcodes `8E DA`, `8E E0`, `8E E8`,
and `8E C0`; raw `ndisasm` plus the emitting TASM listing establish the actual
instructions as `MOV DS,DX`, `MOV FS,AX`, `MOV GS,AX`, and `MOV ES,AX`.

## Ownership and source form

The source seam matters. The function is not part of MASTER.LIB even though it
sits between MASTER.LIB includes in the monolithic object. The relevant order is
`js_sense.asm`, one source-owned zero byte, the game-owned MPN renderer, then
`bgm_bell_org.asm`.

The target implementation computes

`(left >> 3) + (top * 80)`

as the starting VRAM word offset, indexes 64-byte `mpn_t` slots and 128-byte
four-plane images, points DS at the image data, then assigns PC-98 VRAM segments
as follows:

- FS = `0xA800` (blue);
- GS = `0xB000` (red);
- ES = `0xB800` (green).

A 16-row loop writes blue and red through FS/GS and green through `MOVSW`, then
rewinds DI by `16 * 80`, switches ES to `0xE000`, and performs a second 16-row
`MOVSW` loop for the effect plane. Both loops use the x86 `LOOP` instruction.

Independent TH05 target/source lineage preserves the same game-owned 16-row
`MOVSW`/`LOOP` plane-copy architecture, but TH05 uses a FAR controller plus a
near per-plane helper. TH04 instead fuses B/R/G using DS+FS+GS+ES and performs E
in a second loop. This supports a shared low-level design lineage without
transferring TH05 source shape, bytes, or exactness.

## Natural-source negative evidence

One bounded semantic Turbo C++ 4.02 probe was sufficient to test the relevant
compiler mechanism; no source-spelling matrix was pursued.

Probe source:
`.analysis/gpt-web/th04-main-20260916-v203/sub3680_probe.cpp`

Source SHA-256:
`07a00541859a93f6033af4da2ad79a5a9c013ca2c795f1578c1481eca1d6aafc`

The source declares a Pascal FAR four-argument renderer, preserves the true
64-byte slot and 128-byte image geometry, and expresses four semantic far VRAM
pointers under the production `-ml -3 -O -Z` profile. The resulting valid TC86
OMF object has SHA-256
`20429763691e51e16b7c60011789ade2b2c27a98fce016ca4afe2f230e4e5416`.

TC4J emits 207 CODE bytes, versus the 117-byte target. It creates a 0x14-byte
local frame for four far pointers, repeatedly reloads pointers with `LES`, uses
ES for every plane, emits `IMUL` for the `top * 80` calculation, and lowers the
row loop to `INC / CMP / JL`. It does not naturally produce the target's
DS/FS/GS/ES allocation, paired `MOVSW` architecture, or `LOOP` instructions.
This independently agrees with the earlier v198 legal `__seg` probe, which found
no natural `_FS` compiler surface in the inspected toolchain headers.

The probe therefore supplies source-form/origin evidence only. It does not grant
exactness, and further blind C++ spelling search was intentionally stopped.

## Maintained symbolic source

Maintained source is `src/main/formats/mpn_render.asm`, SHA-256
`8428d8bd4d80817384fe71a09b95ba3f93deab833ce0c7b3f5862986c169445b`.

The file is evidence-backed original-style symbolic assembly. It names the
four parameters, slot/image geometry, VRAM segments, row size, and plane-copy
loops; it does not contain a target-derived byte array or copied code string.
The replay transform replaces only the historical inline `sub_3680` body with
an include of this maintained fragment, leaving all neighboring MASTER.LIB
producers and the following BGM alignment byte in place.

The first focused integration reached TASM but failed because generic equate
names such as `slot` leaked into the monolithic assembler namespace and collided
with later MASTER.LIB symbols. Renaming only those parameter equates to unique
`mpn_arg_*` names fixed the integration without changing any instruction, ABI,
or byte intent. That failed build receives zero exactness credit.

## Focused replay

Authoritative focused run:
`gptweb-v203-mpn-render-focused-candidate-002`

- selected owners: 140;
- two isolated cold builds;
- `failures=[]`;
- receipt SHA-256:
  `8371d798ac05265bda4718be7170a07fef182fed9ae6f807bb21aa11612ac924`;
- target/candidate slice SHA-256:
  `70b048108a2279b0246b32199d65fa77633e2280792fd179309539d2deb74d13`;
- A/B MAP SHA-256:
  `b92af86d956216beec421793248dbe14de11deeeca0ee30cc369dbe7c451756a`;
- A/B candidate MAIN SHA-256:
  `ad51bc32345301eb9e212bc009e6ce757fe24d10c77e0dbc20de4a398648c0a6`.

The owner passes `raw=True`, `map=True`, and `relocs=True`; the relocation
overlap is empty in both target and candidate.

Because the source remains inside the monolithic TASM object, raw object hashes
contain Borland dependency timestamp differences. The focused A/B object hashes
are `048647d6...` and `19c47743...`, while dependency-normalized OMF identity is
identical at
`0110922f5d2f52db6cf2ed0eef8ce519a00e22a6166c6a4769ca0548e3339a54`.

## Aggregate replay

Candidate no-unit aggregate
`gptweb-v203-mpn-render-aggregate-candidate-001` passes all 244 candidate-state
default owners twice with `failures=[]`.

Receipt SHA-256:
`4573778c74a4ac4a11645366b47ca48ed47fa9f10f15b104413f974cce038746`

After promotion, no-unit aggregate
`gptweb-v203-mpn-render-aggregate-final-001` passes the same 244 tracked default
owners twice with `failures=[]`.

Receipt SHA-256:
`b873433bb06c459f6b7f1d965aa9739f3a315088e0f6189600b532a07e70bda9`

Tracked replay-manifest SHA-256:
`edc8ba8a195fb1e9ab43f7f336da7b0764957b439543c38e425ec8daedd4db65`

Final A/B MAP SHA-256:
`4a565e0cff733a69ae1dbb976234333a65bb81d624c09989fc22a7d312821d05`

Final A/B candidate MAIN SHA-256:
`1932b7feb681e3fa198d24a10cd93a70ce2cb6d400d1ecab39545cafa26b9f9b`

The promoted renderer remains `raw=True`, `map=True`, and `relocs=True` in both
final builds.

## Accounting

The renderer moves from the MAIN C/C++ reconstruction queue to the separate
original-style ASM attestation plane. It therefore does not create C/C++ exact
function credit and does not alter the reviewed C/C++ byte numerator or
denominator.

Current MAIN accounting after v203 is:

- C/C++ exact reviewed bytes: `75,620 / 81,279` (`93.037562%`);
- C/C++ exact reviewed functions: `460 / 483` (`95.238095%`);
- MAIN reconstruction candidates: 502;
- exact C/C++ boundaries: 460;
- blocked C/C++ functions: 24;
- unreviewed reconstruction candidates: 18;
- ASM-attestation observations: 66;
- exact original-style ASM units: `37 / 5,263 bytes`.

The boundary ledger deliberately keeps this ASM observation's
`accepted_state=unreviewed`, matching the existing ASM-attestation convention;
physical exactness is recorded in the exact-unit/evidence plane instead of the
C/C++ authored-function ledger.

## Other TH04 artifacts

No fresh OP/MAINE/ZUN unpack is claimed. The existing independently attested
retained payloads were rebound by SHA-256 and scanned against the complete
117-byte MAIN renderer.

- OP payload: 69,028 bytes, SHA-256
  `13222cb667e15c5034bd64c840a1db0a07c9acbb56e50f0bcf6025d12fe78d74`;
  longest exact run: 8 bytes.
- MAINE payload: 62,414 bytes, SHA-256
  `7495ae43641bc696d13d18c366e364f6bc8b6a86a1afb681f34c9a334dae792c`;
  longest exact run: 8 bytes.
- ZUN payload: 13,422 bytes, SHA-256
  `baf5a58b333af1135d67c7dd7a4f86e2c828ae149c8219d5d1f589073b0bde9e`;
  longest exact run: 6 bytes.

All three matches are generic FAR-prologue prefixes. Packed `ZUN.COM` still
begins `MZ`. Routing receipt SHA-256 is
`b486cc6ab5d9cec0013ff25dd7bc7b7e34b243d9db816d10625aaf0a1240f2ad`.
No MAIN ownership/source/exactness credit transfers to another artifact.

## Analysis lifecycle and verification planes

v203 entered with `.analysis/` at **4,043,355,632 bytes** and peaked at
**4,262,184,643 bytes** while the failed focused run plus focused/candidate/final
cold trees coexisted. After confirming no active TCC/TASM/TLINK/replay producer,
only the explicit failed focused tree was deleted. Focused-002 and the candidate
aggregate were compacted to receipt-only form after their receipts, A/B OMF/MAP,
and candidate MAIN evidence were copied into v203 durable scratch. The complete
244-owner post-promotion aggregate remains the current cold baseline.
Pre-final-CI `.analysis/` is **4,124,523,508 bytes**. Full final `python3 scripts/ci.py` returns `CI: PASS`; after its live Ghidra replay, `.analysis/` is **4,124,529,641 bytes**, net growth **81,174,009 bytes** from v203 entry.

Repository-native exact physical ownership is established for this original-
style ASM renderer. Standalone TH04 product compile/link closure, whole-image
exactness, runtime-storage identity, runtime-scenario validation, portable
runtime validation, independent pristine-release provenance, and v203 Factory
Truth-Kernel acceptance remain unestablished.

## Continuation

The next structural candidate is `CDG_PUT_NOALPHA_8` in the shared code seam.
MAIN ledger coordinates are load `0x136B4`, analysis `0x236B4`, size `0x65`,
segment `SHARED`; the existing module candidate `th04/cdg_p_na.cpp` contributes
`0x66` raw-identical bytes but ownership/internal boundaries remain provisional.
Fresh v203 Ghidra constructs a contiguous 101-byte FAR body and reports five
callers.

This is also an explicit cross-artifact opportunity rather than a MAIN-only
shortcut: the OP boundary ledger independently contains a same-named authored
`CDG_PUT_NOALPHA_8` candidate of the same `0x65` size. The next review should
compare MAIN and OP raw bodies, their one-byte module/layout seam, callers,
relocations, candidate C++ producer, and TH03/TH05 lineage before deciding
whether ownership is truly shared or artifact-local. No cross-artifact exactness
should be inherited without that proof.
