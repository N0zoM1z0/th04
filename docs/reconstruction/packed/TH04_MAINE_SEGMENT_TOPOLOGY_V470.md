# TH04 MAINE source-level segment topology (v470)

## Scope

v468 recovered natural TC86 producer direction for 24 MAINE relocation entries,
but those blocks were still globally misplaced because the reconstructed
`th04_maine.asm` owned both grouped code segments in one physical OMF module.
The v228 target-constrained order instead cleanly separates the monolith's 175
segment relocations into:

- **139** entries from `MAINE_01_TEXT`;
- **36** entries from `SCORE_TEXT`;

with the combined v468 `hi_end + score_e` TC86 owner between them.

v470 tests whether that order can be recovered at **source-level segment
boundaries**, without editing OMF or MZ relocation records.

## Source split

The replay derives three TASM sources from the retained reconstructed
`th04_maine.asm`:

1. a `MAINE_01_TEXT` owner containing the original segment body verbatim;
2. a `SCORE_TEXT` owner containing the original segment body verbatim;
3. a rest owner retaining the original `_TEXT`, `SHARED`, DATA and BSS surfaces,
   with both grouped code segments empty.

The two code wrappers carry the original external ABI surfaces plus explicit
`EXTRN` declarations for data that was formerly module-local. The rest owner
publishes exactly those formerly-local labels. `SCORE_TEXT` also restores the
`ASSUME cs:group_01` state it inherited from `MAINE_01_TEXT` inside the original
monolith.

`ReC98.inc` publishes an absolute `_address_0 = 0` helper whenever `BINARY` is
defined. A replay-only include copy suppresses only that duplicate `PUBLIC`
record in the two code owners; the value and every macro remain unchanged, and
the rest owner remains the sole publisher. This is a symbol-visibility adapter,
not machine-code or object-record patching.

The resulting TASM objects contain exactly:

- 139 kind-3 segment fixups in `MAINE_01_TEXT`;
- 36 kind-3 segment fixups in `SCORE_TEXT`.

## Natural physical order

The rest/data owner stays at the original monolith's response-file position, so
DATA/BSS layout is unchanged. Only independent/zero-code relocation producers
move:

- `mainemtail` follows `pi_put_q`;
- TC86 `SND_LOAD_EXT` follows `snd_load`;
- after `cutscene`, the response order is
  `MAINE_01_TEXT → score_hi → SCORE_TEXT`.

This recovers the target-constrained global relocation block sequence without
changing physical program bytes.

## Replay result

Run:

```sh
python3 scripts/probes/probe_th04_maine_segment_topology_v470.py \
  --source-dir .analysis/gpt-web/v401-master-vs-object-replay-001/a/source \
  --target-restored .analysis/reconstruction/diet-replay/v228-maine-target-roundtrip/a/restored.bin \
  --output-dir .analysis/gpt-web/v470-maine-segment-topology-replay-001
```

Both cold builds produce:

- MAINE SHA-256
  `2e4b7bc9abf039a4a0d105cf141c1959f3e54ce5812066e9d409e69b42a72c3c`;
- MAP SHA-256
  `5ebb1b6f5ae0371df3eb9a1ebb72735bfb6f5eef4a43b1660c6f0c19ce9c8636`;
- decoded program-image SHA-256
  `0f9658c8a89a6e29d4eb0eba852299b1b2c08037f79ec76ce1f9d0981e1a34d1`,
  byte-identical to v425 and still differing from target only at the shared
  two-byte `snd_load` encoding;
- target-equal 559-site relocation multiset;
- **381 / 559 same-index relocations**, up from v429/v425's 260 / 559;
- ordered relocation mismatch reduced **299 → 178**.

The v468 producer blocks are now globally exact as well:

- `SND_LOAD_EXT`: indices `58..61`;
- combined `hi_end + score_e`: indices `291..310`.

The remaining 178 mismatches are fully confined to already-correct global
owner ranges:

| Owner | Target indices | Mismatches |
| --- | ---: | ---: |
| BGIMAGE | 80..87 | 8 / 8 |
| `MAINE_01_TEXT` split owner | 152..290 | 136 / 139 |
| `SCORE_TEXT` split owner | 311..346 | 34 / 36 |

The first and last MAINE_01 TASM FIXUPP records are simple exact reversals, but
the middle records still require cross-record producer-order recovery. SCORE is
similarly not a single whole-block reversal. Therefore the next blocker is
**internal producer direction**, not link position and not monolith ownership.

Private receipt SHA-256:
`216f2bea926a1d2fc3b38ed0b674943be679614616bea97f539e466b39c42a84`.
