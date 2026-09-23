# ZUN resident six-byte layout cascade (v546)

## Scope and replay

This is a read-only diagnostic of the current ZUN resident component, not a
source or byte-acceptance packet. The target remains `candidate-local-attested`.
First replay the reduced-runtime link:

```bash
python3 scripts/probes/replay_th04_zun_runtime_inventory.py \
  --output-dir .analysis/reconstruction/probes/v546-zun-runtime-inventory-001
python3 scripts/probes/probe_th04_zun_resident_shift.py \
  --output-dir .analysis/reconstruction/probes/v546-zun-resident-shift-001
```

The first command independently cold-compiles the maintained ZUN C++ sources,
rebuilds the local MASTER archive, and links twice with the pinned `c0t.obj`
and CT.LIB. It again produces the 6,360-byte resident candidate SHA-256
`a15ee1e7eac9616e9cd60656a00fb5700c7e20299efc2c0ab44bce6c27cf1dab`
and MAP SHA-256
`ebe1475b9e8775e712e0e3ebd045cb1fa578b74592ea0c1dcef3c6e341d329db`.
It confirms exactly 26 CT.LIB members and the existing **4,241 same-position
raw differences** against target. Fresh cold-link receipt SHA-256:
`a4cdbbf3480581e558f1354e9637b8ba2af99a1e32689c9b38ea68c3cfb02d12`.

## Diagnostic alignment

The target `_main` at decoded payload `0xE67..0xF62` contains two near CALLs
absent from the current natural 246-byte build: at payload `0xEE8` and
`0xEF4`. In resident-component coordinates (base payload `0xB68`), these are
`0x380..0x382` and `0x38C..0x38E`. The candidate contains six zero bytes at
component `0x1482..0x1487`, where the diagnostic alignment resynchronizes;
their physical owner still needs independent review. The probe excludes those
twelve unmatched positions; it does not
insert either target CALL into a binary or patch the linked output.

It then compares the remaining 6,354 target positions with the corresponding
candidate positions at displacements 0, -3, -6, and 0 across the four
consecutive ranges. **6,308 positions match; 46 differ.** All 46 byte deltas
are in the small set `+6` (36), `-6` (5), `+3` (4), and one carry byte `+1`
under unsigned 8-bit subtraction. The four `+3` values occur near the
partially accumulated CALL gap; the many `±6` values are consistent with
downstream address and branch displacement changes. This is a falsifiable
layout explanation for why a six-byte `_main` difference presents as thousands
of same-position raw differences, **not** proof that each of the 46 remaining
fields has correct source ownership. Diagnostic receipt SHA-256:
`b1f71da3d8bd7ef6cd45bc1559dd40a6ea115af1e67ac3fb19745f80b6585545`.

The target resident component remains SHA-256
`cdcb949b8b0353ebe5e83f4cd6e580d93cc5383b35b8cb9db3f820c151c95110`;
the candidate remains different. `_main` and `cfg_init` remain source-present,
not exact; ZUNINIT/MEMCHK generated-assembly provenance remains open. Do not
use aligned equality, copied target calls, zero fill, or a modified comparator
to promote any unit. The next exactness-bearing ZUN step is a legitimate
natural-source producer for `_main`'s two separate calls, or independent source
authority for the other authored components.
