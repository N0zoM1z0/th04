# TH04 BGIMAGE hybrid producer closure (v489)

## Scope

After v487/v488, both TH04 OP and MAINE have the same final ordered relocation
blocker: the eight segment relocations in the shared `BGIMAGE` owner.

The linked BGIMAGE machine code is already target-identical. The remaining
question is source/provenance and OMF producer direction. Direct TC86 compilation
of the historical low-level source emits those eight FIXUPPs high-address first,
while the target requires TASM's ascending record order.

v489 closes both dimensions without editing OMF or MZ relocation bytes.

## Pure-C++ negative surface

The maintained pre-v489 implementation used eight `memcpy()` calls and produces
269 bytes instead of the target `0xD0` owner. Bounded compiler probes also close
several plausible natural-C++ alternatives:

- indexed `unsigned long` plane-copy loops;
- pointer and `do/while` 32-bit copy loops;
- whole-structure copy;
- `#pragma intrinsic memcpy`;
- `_fmemcpy` / `movedata` intrinsic pragmas.

TC86 either emits ordinary scalar long copies, a structure-copy helper, or
`REP MOVSW`. None produces the target `REP MOVSD` loop.

## Independent TH05 provenance

The v489 replay uses pinned DIET 1.45F to restore independently attested TH05
OP and MAINE targets. Their BGIMAGE owners are at load offsets `0xD688` and
`0xEB6C`, respectively. TH04 OP, TH05 OP, and TH05 MAINE all preserve:

- four HMem allocations;
- the same E/G/R/B segment-stack order;
- the same DS/ES pop order for snap versus put;
- `CX = 0x1F40` and `REP MOVSD`;
- the same four-iteration `DL` loop;
- the external even-alignment byte before `bgimage_free()`;
- relative relocation sites
  `0x0F, 0x1A, 0x25, 0x30, 0xAC, 0xB5, 0xBE, 0xC7`.

The three 0xD0 slices differ only at 27 linked 16-bit address fields. Masking
those 54 bytes yields the same normalized SHA-256 for all three targets:

`de718574f65aaa539ef0d56da3ef4c7ee1f9d498418aa11d780e368cb05390d9`.

This is the independent cross-game evidence used to classify the irreducible
low-level statements, following the accepted v393/v394 hybrid-source precedent.

## Maintained source shape

`src/shared/hardware/bgimage.cpp` keeps allocation/free and control flow in C++.
Only target- and TH05-corroborated low-level operations remain symbolic:

- pushing the four source/destination segment pairs;
- `push/pop DS/ES`;
- `REP MOVSD`;
- an `EVEN` directive in SHARED between `bgimage_put()` and `bgimage_free()`.

No `__emit__`, target-byte array, `#pragma codestring`, object patch, FIXUPP
rewrite, or MZ relocation permutation is present.

A useful producer detail is that integrated TC86 rejects the 386 `rep movsd`
inline-assembly statement, while `TCC -B` successfully emits it as symbolic
assembler text. Therefore the historical producer surface is reconstructed as:

`TC86 4.02 -B -> generated symbolic ASM -> pinned TASM32 5.0`.

TASM32 naturally emits the eight segment FIXUPPs at LOCATs:

`0x0D, 0x18, 0x23, 0x2E, 0xAA, 0xB3, 0xBC, 0xC5`.

The generated SHARED CODE is exactly `0xD0` bytes with SHA-256:

`efb4f7170ae577f5f18df689baffeeaad9fb34db3766d01ebdb25209d1f8f554`.

## Full OP / MAINE replay

Run:

```sh
python3 scripts/probes/probe_th04_bgimage_hybrid_v489.py \
  --op-source-dir .analysis/gpt-web/v488-op-score-group-replay-002/a/source \
  --maine-source-dir .analysis/gpt-web/v487-maine-score-super-replay-001/a/source \
  --op-target-restored .analysis/reconstruction/diet-replay/v228-op-target-roundtrip/a/restored.bin \
  --maine-target-restored .analysis/reconstruction/diet-replay/v228-maine-target-roundtrip/a/restored.bin \
  --output-dir .analysis/gpt-web/v489-bgimage-hybrid-replay-003
```

The replay performs two independent product-source builds and relinks both
artifacts. Final identities are:

- OP EXE SHA-256
  `c32633e0b679e8d8bd97f55b9280bb1a9beae82a4530fd33f4cbcc9d1f421274`;
- OP MAP SHA-256
  `65d5d2768ac6c7d36dc9462b6e03487281f007af2350378d14d7d37f157580ee`;
- MAINE EXE SHA-256
  `d3bdc485782a9fb953823155426ca7f0e6e8212d6bc0cdffaaa32f91df2dc90c`;
- MAINE MAP SHA-256
  `014d8dfdf31a2c42c39e76288f23842cff7bd84fb6534f6d46479ba5d8b0838e`.

Replacing BGIMAGE changes no linked program byte relative to v488/v487 and
preserves both relocation multisets. It changes exactly OP indices `186..193`
and MAINE indices `80..87`, making both complete MZ relocation tables
**target-index exact**:

- OP: `804 / 804` same-index relocations;
- MAINE: `559 / 559` same-index relocations.

The only remaining difference in either target-restored program image is the
independent two-byte shared `snd_load` register encoding.

Private receipt SHA-256:
`700ffe3149d0bc67f559f18a52bbc5505a02acbd73076d405ddf3fa84b90d4f8`.

## Tracking semantics

The six decoded BGIMAGE function boundaries are promoted to exact maintained
hybrid source. Their `units.csv` rows intentionally remain `source-present`:
OP/MAINE are DIET-packed artifacts and there is no honest packed-file byte
`file_offset` corresponding to these decompressed function bodies. This avoids
claiming compressed raw-unit exactness while still recording decoded/link exact
function reconstruction.
