# TH04 MAINE natural relocation producers (v468)

## Scope

The v429 target-constrained MAINE projection has 299 / 559 ordered relocation
index differences even though the decoded program image differs only at the
shared two-byte `snd_load` code encoding and the relocation-site multiset is
exact. v448 separates two questions: **producer direction** and **global
owner/segment placement**.

v468 closes two producer-direction questions without moving them to their final
target indices.

## `SND_LOAD_EXT`

The four segment relocations previously attributed to the reconstructed master
DATA tail are the TH04 extension-pointer table. Replacing only its TASM data
include with the same ordinary TC86 initializer already proven in OP:

```cpp
extern "C" const char *SND_LOAD_EXT[4] = {
    "m26", "m26", "m86", "mmd"
};
```

produces one OMF FIXUPP stream at LOCAT offsets
`0x0C, 0x08, 0x04, 0x00`. In the v425 MAINE physical position the linked MZ
sites become:

`0xEAE2, 0xEADE, 0xEADA, 0xEAD6`.

That is exactly the target's local order. The block remains at indices
`51..54`; target placement is `58..61`, so no global-order credit is claimed.

## `score_e` + `hi_end` as one TC86 TU

The maintained ReC98 wrappers are minimal:

```cpp
// score_e.cpp
#include "th04/formats/scoredat/encode.cpp"

// hi_end.cpp
#include "th04/hiscore/end.cpp"
```

A combined-TU probe includes these same function bodies in the same physical
SCORE_TEXT order. The source tree needs two compile-scaffold hygiene changes
only: a temporary include guard around the historically guardless
`scoredat.hpp`, and suppression of the duplicate mid-TU
`#pragma option -zCSCORE_TEXT`. Neither function body is edited.

TC86 emits one `0x211` SCORE_TEXT contribution. The linked MAINE program image
is **byte-identical** to v425. Its 20 kind-3 segment fixups are naturally
ordered high-address first:

- all 18 `hi_end` sites;
- then both `score_e` sites.

This exactly matches the target-local order. At the current physical object
position they occupy indices `55..74`; target placement is `hi_end 291..308`
then `score_e 309..310`.

## Replay

Run:

```sh
python3 scripts/probes/probe_th04_maine_score_producers_v468.py \
  --source-dir .analysis/gpt-web/v401-master-vs-object-replay-001/a/source \
  --target-restored .analysis/reconstruction/diet-replay/v228-maine-target-roundtrip/a/restored.bin \
  --output-dir .analysis/gpt-web/v468-maine-score-producers-replay-001
```

The probe reconstructs the accepted v425 baseline twice, then performs only
targeted producer recompilation/reassembly and a TH04 MAINE relink. Both A/B
runs produce:

- MAINE SHA-256
  `f23a056af351c748269f02fed19c11e7d21270cda756b83151d65af3de103af4`;
- MAP SHA-256
  `032ff715818b483ee488cb688c834958c058eeb576947e62b3386d548e91f234`;
- unchanged decoded program-image SHA-256
  `0f9658c8a89a6e29d4eb0eba852299b1b2c08037f79ec76ce1f9d0981e1a34d1`;
- target-equal 559-site relocation multiset;
- the same global 299-entry ordered mismatch frontier, by design.

Private receipt SHA-256:
`b5496ba469a627206e54de2b5f67a99469029d5341eb6cf091192780b4bccb59`.

## Next blocker

The target sequence proves that the 175 relocations currently owned by
`th04_maine.asm` split cleanly into **139 `MAINE_01_TEXT` + 36 `SCORE_TEXT`**.
The target places the combined `hi_end + score_e` producer between those two
runs. Therefore the next work is segment-level ownership recovery for the
monolithic ASM, not further FIXUPP direction experiments and not MZ table
permutation.
