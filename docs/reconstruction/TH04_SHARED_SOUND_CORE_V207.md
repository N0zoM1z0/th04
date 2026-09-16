# TH04 shared sound-core ownership and MAINE alignment review (v207)

## Scope

v207 follows the v206 `SND_LOAD` cross-artifact result upstream through the
TH04 SHARED sound chain. The packet separates function bytes from two distinct
classes of inter-function layout bytes, then promotes only source ownership that
is directly supported by target and compiler evidence.

The active exactness target remains Japanese `MAIN.EXE`, target identity
`target:th04-main`. OP and MAINE use their independently attested unpacked
payloads for boundary/source-ownership review only. ZUN has no corresponding
sound-core producer in this packet.

## Target-first boundaries

The following OP bodies are now reviewed from raw target control flow:

| Function | OP payload | Size | Terminal instruction |
| --- | ---: | ---: | --- |
| `_snd_mmd_resident` | `0xDC44` | `0x2F` | `RETF` |
| `SND_KAJA_INTERRUPT` | `0xDC74` | `0x1E` | `RETF 2` |
| `SND_DETERMINE_MODES` | `0xDCE4` | `0x9C` | `RETF 4` |
| `SND_DELAY_UNTIL_MEASURE` | `0xDD80` | `0x31` | `RETF 4` |

The corresponding MAINE target bodies are:

| Function | MAINE payload | Size | Terminal instruction |
| --- | ---: | ---: | --- |
| `_snd_mmd_resident` | `0xCF5C` | `0x2F` | `RETF` |
| `SND_KAJA_INTERRUPT` | `0xCF8C` | `0x1E` | `RETF 2` |
| `SND_DETERMINE_MODES` | `0xCFAA` | `0x9C` | `RETF 4` |
| `SND_DELAY_UNTIL_MEASURE` | `0xD046` | `0x31` | `RETF 4` |
| `CDG_PUT_PLANE` | `0xD078` | `0x9A` | `RETF 8` |

`CDG_PUT_PLANE` remains an original-style-ASM attestation candidate. Its
boundary is reviewed here because it closes the second alignment seam and ends
immediately before already-reviewed MAINE `SND_LOAD` at `0xD112`; no ASM
exactness is granted.

Fresh target-bound MAIN Ghidra independently reconstructs the maintained exact
MAIN sound bodies as contiguous functions:

- `_snd_mmd_resident`: analysis `0x233AC..0x233DA`, 47 bytes;
- `SND_KAJA_INTERRUPT`: analysis `0x233DC..0x233F9`, 30 bytes;
- `SND_DETERMINE_MODES`: analysis `0x233FA..0x23495`, 156 bytes.

Ghidra remains provisional navigation evidence and receives no exactness credit.

## Fixed-producer identity

The v206 cold candidate objects were used only to derive positions changed by
normal link resolution. For each producer, the union of candidate pre-link
LEDATA versus linked candidate bytes defines the mask. Target differences do not
define the mask.

The results are:

| Producer | Logical size | Link-field positions | Fixed-byte SHA-256 | Target artifacts |
| --- | ---: | ---: | --- | --- |
| `snd_mmdr` | 47 | 4 | `11786fa28aa8e40ea2a8bf19533098a72c2d20ea0e5fec267cb9bf7f3226afb6` | MAIN / OP / MAINE |
| `snd_kaja` | 30 | 4 | `22776cbef0cdd63cf55b2643a263230459c1f0584162712434ff4d66589cb45f` | MAIN / OP / MAINE |
| `snd_mode` | 156 | 36 | `12274c8ac59b56c78d7bdccaa7a79bf7f2d6aa208f6bade1c3b4ad3d6922e2cb` | MAIN / OP / MAINE |
| `snd_dlym` | 49 | 9 | `01b90abb46302d79cda253a007c8015427d727bd68e74029d2c840b1a6325384` | OP / MAINE |

Every target pair has zero fixed-byte differences after its candidate-derived
mask. Every target-versus-candidate fixed-byte comparison also has zero
differences. The compact receipt is
`.analysis/gpt-web/th04-main-20260917-v207/sound-core-cross-artifact.json`,
SHA-256
`6cf4ffb89d4084554b51dbc951df86957dfe90e4f66c7f189045a79963d0d4bd`.

This is strong TH04-local evidence that MMD, KAJA, and MODE are shared natural
producers across OP, MAIN, and MAINE. DELAY is likewise one shared producer
between OP and MAINE, but it does not occur in the active MAIN link graph and is
not promoted to an exact unit in this packet.

## The MMD trailing NOP is not part of the function

All three TH04 targets contain the same byte immediately after the complete
47-byte MMD function:

- MAIN load `0x133DB`: `90`;
- OP payload `0xDC73`: `90`;
- MAINE payload `0xCF8B`: `90`.

Each preceding body ends in `RETF`, and each following KAJA body begins at the
next byte. The byte is therefore function-external padding, not a hidden MMD tail
or KAJA prologue.

MAIN already tracked this distinction as `th04-main-snd-mmd-padding`. Historical
ReC98 contains `#pragma codestring "\x90"` after its reconstructed MMD source,
but that target-derived candidate is corroboration only. v207 does not adopt a
codestring, copied byte, inert source padding, or another byte-emission shortcut.
The maintained natural function remains exactly 47 bytes.

The existing MAIN-only `src/main/sound/mmd_align.c` also remains intentionally
separate. It is a zero-code exact-replay layout control that emits a word-aligned
SHARED SEGDEF and no LEDATA. It preserves MAIN link placement without claiming
the target NOP and is not reclassified as shared game source.

## OP control: padding and linker fill are different bytes

OP provides a clean control for distinguishing target padding from linker
alignment fill.

The target stores the shared `90` before KAJA at `0xDC73`, so target KAJA starts
at `0xDC74`. The cold candidate has no such byte and therefore starts KAJA at
`0xDC73`. After the 30-byte candidate KAJA body, the next free candidate byte is
odd `0xDC91`. The following `CDG_PUT_NOCOLORS_8` assembly contribution is
word-aligned (`ACBP=48`), so TLINK inserts a `00` at candidate `0xDC91` and
starts the contribution at `0xDC92`.

The target has no gap after its shifted KAJA body and also starts
`CDG_PUT_NOCOLORS_8` at `0xDC92`. Thus OP proves that the target NOP and a TLINK
zero fill can occupy different sides of the same function while producing the
same later module address. They must not be assigned one common source owner.

## MAINE `0xD077` is linker alignment fill

MAINE lacks an intervening word-aligned contribution after KAJA. Consequently,
the target-only MMD padding shifts KAJA, MODE, and DELAY by one byte relative to
the candidate:

- target KAJA `0xCF8C`, candidate `0xCF8B`;
- target MODE `0xCFAA`, candidate `0xCFA9`;
- target DELAY `0xD046`, candidate `0xD045`.

The target DELAY body is exactly 49 bytes, so its next free byte is odd
`0xD077`. The following `th04\\cdg_p_pl.asm` contribution is word-aligned
(`ACBP=48`). TLINK therefore inserts target byte `00` at `0xD077` and starts
`CDG_PUT_PLANE` at even `0xD078`.

The candidate DELAY starts one byte earlier and ends with next free byte
`0xD076`, already even, so it needs no fill and starts its CDG contribution at
`0xD076`. The second v206 layout delta is therefore a linker consequence of the
first target-only NOP, not a missing authored function byte or another source
statement.

No target relocation overlaps either one-byte seam in the independently attested
OP or MAINE payload relocation records.

## Maintained shared source

Three already-exact MAIN natural producers are now stored under TH04 shared
ownership with content unchanged:

- `src/shared/sound/mmd_resident.c`, SHA-256
  `a65bb7bf8c1bfeaf02f8e6da38aa3df968d4b77881d0932ffe91d43a6995ada5`;
- `src/shared/sound/kaja_interrupt.cpp`, SHA-256
  `f01beb0fece5673d113c3a32297b42f32c16bbb044d5027ca07a0961a0648e93`;
- `src/shared/sound/determine_modes.cpp`, SHA-256
  `248aca155a313409bb76bfc397837b91ce1b0f792443d9ed71a14f9390903a82`.

The MAIN exact-unit manifest and accepted function ledger now bind those shared
paths. OP and MAINE boundary rows also refer to the maintained shared source, but
remain `accepted_state=unreviewed`; source ownership is not byte-exactness.

`SND_DELAY_UNTIL_MEASURE` remains a reviewed OP/MAINE boundary with a validated
shared producer shape. ReC98's `th03/snd/delaymea.cpp` is still only a source
hypothesis. The next packet should localize that natural source under TH04 shared
ownership and prove its compiler/profile/ABI without inheriting a TH03 exactness
claim.

## Cold replay after ownership migration

Focused run `gptweb-v207-shared-sound-core-focused-001` selected all three moved
MAIN units and performed two isolated cold builds. Receipt SHA-256 is
`ffb516247086ff83d468a991c42a0eb62cb0a47b8a61983193f52609635c9632`.
All three units pass `raw/map/relocs=true`:

- MMD target slice SHA-256
  `6857612b6eef899a413ab7e244f2e7f0e3c08a43a18f9c3d1d9b10f9194974a6`;
- KAJA target slice SHA-256
  `6173530a731d72e5d77fda50bbd68f5c29b1f52553ac90c906842deb5010583f`;
- MODE target slice SHA-256
  `6c7dda598a314fb93015a664bfe2bc58cbf82b18df2bd4bd817fbf77fed4c075`.

Focused A/B object identities are deterministic:

- `snd_mmdr.obj`: `8cbc7b19f51ce4c4185da700a66d4d5ac909ec90d48d25a382b65e7ddb19edb0`;
- `snd_kaja.obj`: `b030046945a74e5ac4c207a77495b8a1b6686d35d3963c81f315d010c973d3d3`;
- `snd_mode.obj`: `d72462fdc6d759e5cce8d1a13f8b90cf7ba828970094678cba179d452b2de0cd`.

Mandatory no-unit aggregate `gptweb-v207-shared-sound-core-aggregate-001`
passes all 246 default exact owners twice with `failures=[]`. Receipt SHA-256 is
`82495b0b08693f0f972cf09174e1adb6d2f0b9805e092e1401323646f75999ef`.
The tracked exact manifest SHA-256 is
`8ecd1d6270c2d5c2c884b72c8a09fac1e870a5d6c677917058c9efe93d6a2892`.
Aggregate A/B MAP returns to
`4bea5732094f5f08b2c37365d7cae466f063e54f7cb22cad115c973810cf59cc`,
and aggregate A/B candidate MAIN returns to
`1932b7feb681e3fa198d24a10cd93a70ce2cb6d400d1ecab39545cafa26b9f9b`.

This is an ownership migration of already-exact MAIN source, not a new exact
promotion. No second post-promotion aggregate is claimed.

## Verification state and continuation

MAIN exact accounting is unchanged by design. OP and MAINE gain reviewed
boundaries and maintained shared-source ownership where directly established,
but no artifact-local exactness denominator is invented.

Standalone TH04 product compile/link closure, whole-image equality,
runtime-storage identity, runtime-scenario validation, portable runtime,
independent pristine provenance, and Factory Truth-Kernel acceptance remain
separate and unestablished.

The first evidence-connected continuation is natural-source localization for
`SND_DELAY_UNTIL_MEASURE`, target OP `0xDD80..0xDDB0` and MAINE
`0xD046..0xD076`. Its 49 fixed producer bytes are already proven identical
between OP and MAINE. Start from the ReC98 TH03 source only as a hypothesis,
localize its dependencies into TH04-compatible headers or `compat/rec98/`
forwarders, and validate the TC4J object/ABI before considering any new
artifact-local exactness claim.
