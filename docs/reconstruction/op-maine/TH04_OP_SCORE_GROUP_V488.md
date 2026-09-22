# TH04 OP historical SCORE_TEXT producer (v488)

## Scope

After v466, OP has 71 ordered relocation differences:

- shared BGIMAGE: 8 entries at indices `186..193`;
- `score_e + hi_view`: 63 entries at indices `403..465`.

The linked program image already differs from the target only at the shared
2-byte `snd_load` register encoding. The SCORE residual is therefore an OMF
producer/topology problem, not a code-byte problem.

## Physical producer clue

The v466 MAP places three exact TC86 SCORE_TEXT contributions consecutively:

| Current object | Load extent | Bytes |
| --- | --- | ---: |
| `score_db` | `0xC57A..0xC626` | `0xAD` |
| `score_e` | `0xC627..0xC68B` | `0x65` |
| `hi_view` | `0xC68C..0xCC96` | `0x60B` |

As a standalone object, `hi_view` batches at `0x400 + 0x20B`. Its 61 segment
relocations are emitted as two FIXUPP records, while the target requires the
characteristic interleave:

`hi_view 23 -> score_e 2 -> hi_view 38`.

This is the same class of problem closed for MAINE SCORE in v487: recover the
larger historical TC86 translation unit that shifts LEDATA boundaries.

## Combined TC86 TU

v488 compiles, in physical code order:

```cpp
#include "th04/score_db.cpp"
#include "th04/score_e.cpp"
#include "th04/hi_view.cpp"
```

The source tree needs only compile-scaffold hygiene:

- a temporary guard around historically guardless `scoredat.hpp`;
- suppression of the later `op_01` segment switch in `view.cpp`;
- suppression of duplicate mid-TU `SCORE_TEXT` pragmas in `encode.cpp` and
  `recreate.cpp`.

No function body changes.

TC86 produces a `0x71D` SCORE_TEXT CODE contribution with natural LEDATA
extents:

- `0x000..0x3FD` (`0x3FE` bytes);
- `0x3FE..0x71C` (`0x31F` bytes).

The first kind-3 FIXUPP record has 25 segment relocations. Its last two LOCATs
are `0xD7` and `0xCF`, the two `score_e` sites; the preceding 23 belong to
`hi_view`. The second record has the remaining 38 `hi_view` sites. This is
exactly the target-constrained order.

## Linked replay

Run:

```sh
python3 scripts/probes/probe_th04_op_score_group_v488.py \
  --source-dir .analysis/gpt-web/v466-zunsoft-full-cpp-replay-001/a/source \
  --target-restored .analysis/reconstruction/diet-replay/v228-op-target-roundtrip/a/restored.bin \
  --output-dir .analysis/gpt-web/v488-op-score-group-replay-002
```

Both targeted A/B copies compile the grouped producer and relink OP only. They
produce:

- OP SHA-256
  `d1e64a65e06844831264ad9691710007e629e63599639e73d1ca0a180d5a29d8`;
- MAP SHA-256
  `3f48d379d567cce4be13c68e9f053dffd8712a941ea4f32f9296df85bab3fe07`;
- unchanged program-image SHA-256
  `7e4cb7aa24782700d6db85c4cd39622d7b23e3a62d9da325b92089e9b8f1b948`;
- target-equal 804-site relocation multiset;
- target-index exact relocation entries `403..465`;
- **796 / 804 same-index relocations**.

Ordered OP residual falls from **71 to 8**. The only remaining differences are
shared BGIMAGE indices `186..193`.

Private receipt SHA-256:
`5f5c871c91e7f9e4e12086401003c4e0d778ecb8b801e2cd5d843fbf06cce0e1`.

## Remaining OP work

OP and MAINE now share exactly the same final packed blocker: the eight BGIMAGE
segment relocations. v234 already proves that TCC assembly-output followed by
TASM naturally reverses those eight entries without changing BGIMAGE code, but
the historical ReC98 source used inline assembly/codestring and is not accepted
as maintained authored source. Continue only with a legal source/provenance
mechanism; do not hand-permute FIXUPP or MZ entries.
