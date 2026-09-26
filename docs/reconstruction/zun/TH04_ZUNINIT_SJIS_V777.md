# ZUNINIT character converter semantics (v777)

## Target and claim

The attested TH04 ZUN.COM decoded payload contains a reviewed 18-byte function
at `th04-zun / com-payload / 0x7B0..0x7C1`, or ZUNINIT runtime COM
`0x1BD..0x1CE`. Its SHA-256 is
`044ce9480a0506ffac42aeaf78844e0266262c10ffd075d2c861a7a78689adf8`.
The caller at runtime `0x1E7` passes a two-byte character in AX, lead byte in
AH and trail byte in AL. The hypothesis is that the helper returns the
standard JIS X 0208 row and cell in AH and AL.

## Independent semantic Oracle

Run:

```sh
python3 scripts/probes/probe_th04_zuninit_sjis_to_jis.py \
  --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME
```

The probe attests the target, extracts this complete target function, and runs
its real instructions in Unicorn x86 16-bit mode. For every mapped two-byte
pair accepted by Python's strict `shift_jis` codec, it independently obtains
the corresponding JIS row/cell by encoding the decoded character as `euc_jp`
and subtracting `0x80` from each EUC byte. All **6,879 of 6,879** pairs agree.
The output vector SHA-256 is
`52ec41e515445541d9cbfad63147f1fdd7202b1969f36fbf5b9a5c7406b92d53`.

The broader `cp932` control compares 6,883 pairs and has ten mismatches, all
listed in the receipt. These are extension/duplicate mappings whose encoded
JIS location differs from the arithmetic Shift-JIS position. This restricts
the verified claim to the strict standard pair set.

Durable receipt: `.analysis/reconstruction/probes/v777-zuninit-sjis-002/receipt.json`,
SHA-256 `d0d057dabfa0c671f0a0b3883c3302a658ee0fec4838b77dae0a1f3f72043a2d`.
The receipt pins the payload slice, probe source, Unicorn binary, Python
version, register state, compared pair counts, and counterexamples.

## Reconstruction consequence

The `sub_1BD` behavior and register interface are now runtime-observed. Its
current target-derived ASM remains untrusted as original source; no maintained
source owner, decoded exact state, or whole-ZUN.COM exactness follows. The
natural next bounded ZUNINIT question is the caller at `0x7C2`, which renders
the converted characters into PC-98 text VRAM and still needs source/origin
review.
