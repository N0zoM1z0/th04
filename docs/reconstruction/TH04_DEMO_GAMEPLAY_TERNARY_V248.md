# MAIN gameplay loop conditional producer (v248)

The pinned MAIN.EXE target and active Ghidra database passed this session's
preflight and database attestation. The reviewed `gameplay_loop()` body is
`th04-main / DEMO_TEXT 0AAF:0098`, MZ load `0xAB88..0xAD02`, target file
`0xC388..0xC502`, 379 bytes, SHA-256
`54ac4974b571dc990934e9c5ed39afb1b91206c397b67c734442fe81fd6c4448`.
The target's lives-to-play-performance-interval branch begins at load
`0xACC7` and has a unique 25-byte sequence, SHA-256
`2ae6bf38991401052fbd9ef0995b4557466b4f5bc982130e4466498ffadba1f9`.

The earlier maintained source assigned `frames_per_playperf_raise` in both
branches. Target machine code instead forms either branch result in `AX`, then
moves it into `SI` once at the join. A bounded diagnostic replaced only those
assignments with a conditional expression of the same values. The verified
conditional expression is now maintained in `src/main/core/gameplay_loop.cpp`.

Run:

```sh
python3 scripts/probes/probe_th04_gameplay_ternary.py --output-dir .analysis/reconstruction/probes/v248-gameplay-ternary-replay
```

The replay verifies target SHA-256 and the pinned TC4J 4.02 binary, compiles
both sources under `-c -I. -O -b- -3 -Z -d -DGAME=4 -ml` in a temporary v214
source materialization, and validates OMF checksums. The baseline emits 370
DEMO_TEXT bytes (SHA-256
`8d097211c052105dad8da37d9af0305ca28d7ea7371472207284d97e70490224`)
and lacks the target branch. The conditional expression emits 372 bytes
(SHA-256
`54c691f5ea776a4b71003c10f772c825e729ea852eb494fa65a364710c8c6ebc`)
and contains **the exact 25 target branch bytes** once, at object offset 314.
The private receipt SHA-256 is
`3e49ce3a4af999c67ec74cd27aba8c1274f818ee932cc3987f501a6298c511ff`.

The full target function is still seven bytes longer than this source
object. Relative to this compiler output, the target's frame-counter sequence
is three bytes longer and it retains two `EB 00` jumps. Their natural source
producer remains open; the linked call shape also needs the complete raw/MAP/
ordered-relocation replay. This is compiler-observed local codegen, not
exactness, and it does not justify an inert jump or byte padding. The probe
now reconstructs the historical baseline from the maintained source and
replays both variants, preserving the original v248 comparison.

The historical maintained-source rerun was
`python3 scripts/probes/probe_th04_gameplay_ternary.py --output-dir .analysis/reconstruction/probes/v252-gameplay-ternary-maintained`.
Its private receipt SHA-256 was
`3e49ce3a4af999c67ec74cd27aba8c1274f818ee932cc3987f501a6298c511ff`:
both variants, object CODE hashes, and branch offsets were unchanged. The
source SHA-256 for that run is
`330b49a298b0a27a52685b4daa4cad3ebf34fdb7e5ada51b4a62c9a8ea8b0c5b`.

## v273 frame-counter source revision

The current maintained source combines the increment and first modulo assignment
as `stage_frame_mod16 = ((stage_frame = stage_frame + 1) & 15)`. Its unsigned
16-bit `stage_frame` declaration makes this equivalent to the former two
statements. Run `python3 scripts/probes/probe_th04_gameplay_ternary.py
--output-dir .analysis/reconstruction/probes/v273-gameplay-frame-replay`.
The pinned TC4J/OMF replay compares the old and revised frame expressions and
also retains the old branch control. The revised 372-byte CODE SHA-256 is
`e3d6e451f5c5988c21c885be406815bf8c8fd23c181494db67bea74001b245ed`;
the former 372-byte CODE is still
`54c691f5ea776a4b71003c10f772c825e729ea852eb494fa65a364710c8c6ebc`.
The revision emits the target-style `MOV AX; INC AX; MOV [stage_frame],AX`
sequence while preserving the exact 25-byte interval branch. The target still
has an extra `MOV DX,AX`, a 16-bit rather than 8-bit first mask, and two
`EB 00` jumps. Complete bytes remain 372 versus 379, so this is
compiler-observed local progress, not exactness. Receipt SHA-256:
`b107b6d7d48ebc53a5a1b7086d6c9a8b6fda09f201535141106c454c2b479e97`.
