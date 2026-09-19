# MAIN gameplay session initializer v377

The reviewed `gameplay_session_init()` owner is `DEMO_TEXT 0AAF:0213`,
target file `0xC503..0xC6CF`, size `0x1CD` / 461 bytes. The executable body is
`0x1C2` bytes through `RET`, followed by one `0x00` byte and five 16-bit switch
jump words. Earlier isolated TC4J compilations emitted only 460 bytes and
therefore withheld exactness.

## Compiler mechanism

The missing byte is a natural Borland switch-table alignment byte, but only in
the original physical producer context. `_main` (0x7C bytes), `gameplay_loop`
(0x17B bytes), and `gameplay_session_init` share one TC4J `DEMO_TEXT` producer.
Within that object the session starts at odd offset `0x1F7`. The repository's
Borland decompilation research documents `-a2` / `#pragma option -a` as
word-aligning compiler-generated switch jump tables with a `0x00` byte.

`src/main/core/demo_prefix.cpp` reconstructs that fused producer using the same
combined-source pattern already accepted for other TH04 physical producers.
`gameplay_session_init.cpp` enables `#pragma option -a` for the session body.
TC4J then emits a 0x3C4-byte DEMO_TEXT object: `_main` at 0x0000,
`gameplay_loop` at 0x007C, and `gameplay_session_init` at 0x01F7. The session
tail is naturally `RET; 00; five jump words`; maintained source contains no
padding-byte emission, code string, target byte array, or object patch.

The fused source also preserves the original `BULLET_A_TEXT/main_03` segment
frame while declaring difficulty-wrapper near functions. This lets TC4J encode
the session's function-pointer assignments with the same cross-segment offsets
as the target. Existing monolithic shot-function tables are exposed through
same-address public labels rather than copied.

## Exact replay

Focused replay:

```sh
python3 scripts/replay_th04_main_exact_units.py \
  --unit th04-main-gameplay-session-init-v165 \
  --run-id gpt-web-session-v377-focused-003
```

Receipt SHA-256:
`465b98fbbebd02a963d2d35d906b0908d39bbd4ac47eff016905f04d2839897d`.
All 186 selected dependency owners pass both cold builds. The session target and
candidate slice SHA-256 are both
`2e37dff3ee0d9933fc207c7157cc5bdb3a8dd582128a07089f4cac2538cf833b`;
the logical extent has no MZ relocations. The fused object SHA-256 is
`0c5ed157f333b183c435f2be6caef6a136426c585018d8c10ffb51c02c903a15`.

Candidate aggregate:

```sh
python3 scripts/replay_th04_main_exact_units.py \
  --run-id gpt-web-session-v377-aggregate-candidate-001
```

Receipt SHA-256:
`6e314bf2b6c50c46c2e2311a2a8628a6cd2a4cccc0a05b339841597c23020759`.
All 255 default candidate owners pass twice with `failures=[]`.

Fail-closed `reviewed_exact_extent` validation decodes 110 instructions through
the `RET` at `0x1AEC4`, checks the target `0x00` at `0x1AEC5`, validates jump
words `0327 / 034C / 035E / 0387 / 03B0`, and confirms every jump target is an
instruction start. Only `th04-main-fn-1ad03` is merged from the trial function
ledger.

Post-promotion aggregate:

```sh
python3 scripts/replay_th04_main_exact_units.py \
  --run-id gpt-web-session-v377-aggregate-final-001
```

Receipt SHA-256:
`20a23766aa1963d93907179709fa55030a1ff26d4a0018aa489f0aa638a86b5f`.
All 255 promoted default MAIN owners pass twice with `failures=[]`; both
candidate MAIN images remain SHA-256
`c87c943f91614cc5b37828e1ffcadc3f83dc6284801e61d157b74fbc59053a8f`.

v377 promotes 461 reviewed authored C/C++ bytes and one reviewed function.
MAIN becomes 80,023 / 83,441 reviewed authored C/C++ bytes exact
(95.903692%) and 478 / 491 reviewed authored functions exact (97.352342%).
