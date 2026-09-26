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
