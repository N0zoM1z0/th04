# TH04 BGM BSS Reduction #172 provenance (v494)

## Why this packet matters

v492 finds a natural TASM/TLINK mechanism for the target-attested OP/MAINE `T`
extents: make the shared MASTER BGM BSS file-backed zero data. Its explicit-zero
replay template was intentionally kept as mechanism evidence because the pinned
generic `masters.lib:b_data.OBJ` has no BSS LEDATA.

v494 adds an independent repository-history source for **the same binary-
preserving representation**. It does not infer source spelling from target
bytes.

## ReC98 Reduction #172

ReC98 commit
`509d3b31b9197711b65062108e12fe5a52a767e9` (2014) introduced
`libs/master.lib/bgm[bss].asm` with this exact body:

```asm
timerorg    dd      ?
_bgm_part   label   word
part        SPART   PMAX dup(<0>)
_bgm_esound label   word
esound      SESOUND SMAX dup(<0>)
```

The blob SHA-256 is
`c6c7e07f7b9ac47397f5a2101ae077dc6e422c81cfbfa125149800b17eb12b31`.

Most importantly, the commit message explicitly records the reason:

> Initializing the BSS data to 0 instead of the ? in the original source file
> avoids size changes in the MZ header.

Thus two facts are separately preserved by project history:

1. the **original source spelling** known to that reduction used `?`;
2. a zero-initialized reconstruction spelling was already required in 2014 to
   preserve the target-compatible MZ header/file-size surface after moving this
   internal MASTER data.

This is stronger provenance than deriving an explicit-zero template solely
from the current target.

## Current-toolchain replay

`probe_th04_bgm_bss_reduction172_v494.py` verifies the commit message and exact
historical Git blob before doing any build work. It then copies that unmodified
blob into two independent v489 OP and MAINE source snapshots, rebuilds only the
master data-tail object with pinned TASM32 5.0, and relinks with TLINK 6.10.

Both A/B runs reproduce the exact v492 mechanism outputs:

| Artifact | EXE SHA-256 | File bytes | Load bytes | minalloc | Remaining target-restored program diff |
| --- | --- | ---: | ---: | ---: | --- |
| OP | `994f80821d2918f0071e28f6e82d6ed660eac1d8473a532fd70fb743008f87ee` | 76,864 | 72,256 | 410 | `0xDE8B..0xDE8C` only |
| MAINE | `27c17df711ed08f4c4bcada9b4ba699914d08cb164cd1444c36f1994527bab8a` | 69,218 | 65,634 | 615 | `0xD1D3..0xD1D4` only |

For both artifacts:

- the old v489 program prefix is byte-identical;
- the newly file-backed extent is all zero;
- the complete relocation table remains target-index exact;
- the only target-restored program mismatch remains the shared two-byte
  `snd_load` encoding.

Private receipt SHA-256:
`bd3e0c3e1df2e8de3e480e790978d1ad8ec336206c0d4be3a91293b46e869715`.

## Interpretation and limit

v494 does **not** prove that ZUN's original BGM source declared `part` or
`esound` as initialized zero. In fact, the historical commit explicitly says
the original source used `?`. The zero-initialized spelling is a historically
attested **binary-preserving reconstruction/build representation** that
compensated for a lost original object/segment/post-link condition.

Combined with v492's TH05 cross-game target evidence and v493's proof that ZUN
used a modified MASTER object set rather than the pinned generic archive
verbatim, this makes the T surface highly constrained without overstating the
missing original source.
