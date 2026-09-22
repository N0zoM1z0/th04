# TH04 packed BGM-BSS file-backing mechanism (v492)

## Scope

After v489, OP and MAINE have target-index exact relocation tables and their
linked program images differ from target-restored MZs only at the shared
`snd_load` two-byte encoding. v490 shows `e_minalloc` is mechanically derived
from the file-backed load extent plus unchanged `SS:SP`. The remaining packed
header question is therefore the target-attested `T` extent itself.

v492 identifies a natural linker mechanism for that extent and corroborates the
same physical structure with independent TH05 targets. It deliberately does
**not** claim that the historical ZUN source declared these variables as
initialized zero.

## Shared physical BGM span

The independently attested historical MASTER BGM layout is:

- `timerorg` at BSS `+0x00`;
- `part` / `_bgm_part` at `+0x04`;
- `esound` / `_bgm_esound` at `+0x46`;
- BSS end at `+0xC6`.

All four independently restored target artifacts checked here contain the exact
same 198 zero bytes across this span, SHA-256:

`a6eab4025a7c9c0877549f6e5d790f66af88ee7f2320e814954e638d8051f812`.

For TH04 OP, TH04 MAINE, and TH05 OP, the restored load image ends exactly at
`timerorg + 0xC6`. TH05 MAINE continues for a separate 16-byte post-BGM tail.

## Natural TASM/TLINK mechanism

Pinned TASM32 5.0 distinguishes uninitialized storage from explicit zero data
even inside a BSS-class segment: `dw ?` emits no LEDATA, while `dw 0` emits
LEDATA with a warning. The checked replay template preserves only the attested
BGM layout/symbols and represents the `0xC6` span as symbolic zero data.

Applying that template to isolated v489 source copies and relinking with pinned
TLINK 6.10 gives:

| Artifact | Natural v489 load | v492 load | target-restored load | v492 minalloc | target minalloc |
| --- | ---: | ---: | ---: | ---: | ---: |
| OP | 69,028 | **72,256** | 72,256 | **410** | 410 |
| MAINE | 62,414 | **65,634** | 65,634 | **615** | 615 |

In both cases:

- every byte of the original v489 program prefix is unchanged;
- the new file-backed tail is entirely zero;
- the already target-exact relocation table remains byte-for-byte unchanged;
- only the known adjacent `snd_load` bytes differ from the target-restored MZ.

A/B output identities are stable:

- OP EXE SHA-256
  `994f80821d2918f0071e28f6e82d6ed660eac1d8473a532fd70fb743008f87ee`;
- MAINE EXE SHA-256
  `27c17df711ed08f4c4bcada9b4ba699914d08cb164cd1444c36f1994527bab8a`.

## TH05 cold-build corroboration

The same symbolic BGM storage is applied to two independent copies of the
retained v401 source snapshot and the complete tree is rebuilt for GAME=5.

TH05 OP changes from load extent 73,164 to **75,786 bytes**, with no change to
the old program prefix. This exactly equals the independently DIET-restored
TH05 OP target extent; `e_minalloc` simultaneously becomes the exact target
value **420**. The newly file-backed 2,622 bytes are all zero.

TH05 MAINE similarly file-backs through the exact BGM end and reaches load
extent 75,942 with target `e_minalloc=2533`; the independently restored target
continues another 16 bytes to 75,958. This extra 16-byte TH05-MAINE surface is
separate from the shared BGM mechanism and is not used to infer TH04 bytes.

This is stronger than observing zeros in TH04 alone: the same BGM physical
region is file-backed in independently attested targets from a different game,
and the same symbolic TASM/TLINK mechanism predicts the full TH05 OP extent.

## DIET closure control

Packing the natural v492 TH04 MZs with pinned DIET 1.45f `-B -G` produces:

- OP: 42,289 bytes, target 42,290;
- MAINE: 38,034 bytes, target 38,035.

The remaining packed-stream difference is caused by the known two-byte
`snd_load` program encoding. A **private target-derived diagnostic control**
changes only those two adjacent bytes in a copy of each v492 MZ. The resulting
preimages become byte-identical to the v228 target-restored MZs and DIET packs
them raw-exact to both original targets:

- OP SHA-256
  `8fc3b67fa8470de15b4f2844d5623d0a93d7922fac16d82a25a90a378b516b0f`;
- MAINE SHA-256
  `670de6ba907a2edbc1592de810acd92e5b89541d3dc35b70210171166d1713f8`.

This control grants **no source credit** for `snd_load`; it only proves there is
no additional hidden packed/container degree of freedom once `P`, `R`, and `T`
are exact.

## Provenance limit

v430/v491 independently extract the pinned generic `masters.lib:b_data.OBJ`;
its `0xC6` BSS contribution has **no LEDATA/LIDATA**. v493 then proves from
independent target code that ZUN's TH04/TH05 MASTER object set was not this
generic archive verbatim: the archive gaiji objects retain the official `ADC
5680h` bug, while all four TH04/TH05 OP/MAINE targets contain ZUN's corrected
`ADD` form. The generic `b_data.OBJ` therefore cannot be treated as definitive
negative evidence about ZUN's modified BGM object. Even so, the v492 all-zero replay template is not promoted as ZUN historical
source; the exact modified `b_data` object/source remains unavailable. v494
adds a separate repository-history fact: ReC98 Reduction #172 already used the
binary-equivalent `timerorg dd ?` plus `part/esound dup(<0>)` representation in
2014, with an explicit commit note that the zero initialization was needed to
avoid MZ header size changes. That history attests the reconstruction/build
representation while simultaneously confirming that the known original source
spelling used `?`.

The durable conclusion is narrower:

1. the target T surface is a real cross-game file-backed BGM-BSS structure;
2. a normal TASM/TLINK initialized-BSS mechanism reproduces TH04 T exactly;
3. packed closure then has no hidden variable beyond the unresolved shared
   `snd_load` two-byte program encoding and provenance of the historical T
   trigger.

Private receipt SHA-256:
`4d02370f5acddd24283c0f48a7e3c07033156dbc799125fdeb558898c96b9b63`.
