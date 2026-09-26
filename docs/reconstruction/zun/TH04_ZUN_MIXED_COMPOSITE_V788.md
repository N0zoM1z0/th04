# ZUN generated directory and mixed-input flat build (v788)

## Builder and input boundary

`scripts/build_zun_composite.py` is a checked-in build tool for the flat
`ZUN.COM` payload. It derives the 327-byte selector directory from the four
supplied COM lengths: count, fixed-width names `-O/-I/-S/-M`, 33-entry offset
table, and the mover call displacement. It then composes the documented
COMCSTM header, usage text, selector, directory, components, mover, and outer
customization stub. It takes the binary inputs explicitly and contains no
target component byte arrays.

The v788 integration probe uses these two classes of input:

| Origin | Inputs |
| --- | --- |
| Maintained TH04 source cold outputs | selector, ZUNINIT, MEMCHK, mover, customization stub |
| External/diagnostic | usage text, ONGCHK library binary, ReC98 resident component candidate |

The resident candidate is raw-identical to its target component only because
its upstream source retains inert optimizer barriers. It is **not** the
maintained natural `src/zun/resident/main.cpp`, which still compiles six bytes
short. The external inputs and the candidate do not earn product-source or
exact authored credit.

## Focused integration result

```sh
taskset -c 0,1 nice -n 10 python3 scripts/probes/replay_th04_zun_mixed_composite.py \
  --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME
```

The probe checks the attested decoded target SHA-256 and every input size and
digest. Two independent A/B input sets produce the same generated directory:
`com-payload 0x20E+0x147`, SHA-256
`34f8cc401b162e16c8fbc45a2227fa877157b25e71c0edb45eacb9b232e9cb33`.
The complete 13,422-byte flat payload is raw-identical to the decoded target,
SHA-256 `baf5a58b333af1135d67c7dd7a4f86e2c828ae149c8219d5d1f589073b0bde9e`.
Appending one byte to the ZUNINIT input changes the calculated directory and
causes both directory and full-flat comparators to reject equality.

Focused receipt:
`.analysis/reconstruction/probes/v788-zun-mixed-flat-final-001/receipt.json`,
SHA-256 `0f215d53d2696647d183b670ef73cc13a70124a7b8dd9ba6f256aa3cb300815b`.

This is a **mixed-input integration Oracle**. It closes the directory formula
and demonstrates that the maintained components fit the outer flat layout.
It does not close the external usage/ONGCHK ownership, resident natural-source
gap, DIET-packed MZ generation, or whole `ZUN.COM` exact acceptance.

## v789 pinned DIET packaging continuation

The two v788 flat outputs were passed to the existing pinned DIET 1.45f
replay under low priority and a two-core CPU affinity:

```sh
taskset -c 0,1 nice -n 10 python3 scripts/probes/replay_diet145f.py th04-zun \
  --candidate-a .analysis/reconstruction/probes/v788-zun-mixed-flat-final-001/a.flat.bin \
  --candidate-b .analysis/reconstruction/probes/v788-zun-mixed-flat-final-001/b.flat.bin \
  --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME --require-exact
```

Both independent DIET runs emit the same valid 7,754-byte MZ and raw-match the
pinned `ZUN.COM` SHA-256
`0a12e9a489d3b704a77cf04ca3062ee48f298a9df6d237dc7dad46986e2d116e`.
Receipt: `.analysis/reconstruction/probes/v789-zun-mixed-diet-001/receipt.json`,
SHA-256 `d2093ff4382f7e2c13a2657fcabafd1ba8765219de1f9d48ac5579c76ff9ed95`.
This establishes that DIET packaging is reproducible for the mixed-input flat
payload. It does not resolve the external inputs or the natural resident
`_main` gap; the receipt explicitly grants no source acceptance.

## v790 ONGCHK library component closure

`src/zun/ongchk/ongchk.asm` now describes the embedded PMD ADPCM RAM diagnostic
as one symbolic original-style Tiny-model assembly translation unit. The
runtime code occupies COM `0x100..0x47B`, the initialized diagnostic pattern
and two state bytes occupy `0x47C..0x49D`, and the subsequent port variables
and 32-byte readback buffer are BSS. These boundaries correspond to ZUN decoded
payload `0x355..0x6F2`; the selector directory supplies the complete 926-byte
component extent. The maintained source uses named control-flow and data
symbols, not an embedded copy of the COM file. Its historical source spelling
and original assembler provenance remain inferred.

```sh
taskset -c 0,1 nice -n 10 python3 scripts/probes/replay_th04_zun_ongchk.py \
  --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME
```

Two isolated TASM 5.0/TLINK 6.10 cold builds produce identical checksum-valid
OMF, MAP and 926-byte COM outputs. Both complete COM outputs have zero raw
differences from the hash-attested target component, SHA-256
`4f9a9451f19bdd8d3ea8949a5ea75df6c2f92a9a84dcf39e1d7cf13421acc8a0`.
Focused receipt:
`.analysis/reconstruction/probes/v790-zun-ongchk-symbolic-002/receipt.json`,
SHA-256 `feb10c6deb6cad68f8304ad8707805936c24d359b7db45b8cf3806c80f92c1c0`.

The mixed flat builder now takes its ONGCHK input from these A/B maintained
outputs. Both 13,422-byte flat outputs and the generated directory remain
raw-identical; receipt
`.analysis/reconstruction/probes/v790-zun-mixed-ongchk-001/receipt.json`,
SHA-256 `9605007ca6ba2f0a32f8eb3e0c6ad7f18d19436d50e01e280461025d199ae22e`.
ONGCHK is third-party library code, so this closes one external binary input
without adding a ZUN authored-function exact claim. Usage text is still an
external asset and RES_HUMA still comes from a diagnostic ReC98 candidate.
The earlier v789 DIET receipt used the binary ONGCHK input; repacking the new
maintained-input flat outputs remains a separate verification step.
