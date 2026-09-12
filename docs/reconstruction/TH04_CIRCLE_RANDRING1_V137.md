# TH04 CIRCLE_TEXT randring1 reconstruction (v137)

## Scope

Artifact: `th04-main / MAIN.EXE` (`candidate-local-attested`). Target SHA-256:
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`.
The private executable remains ignored operator input and is not a repository
artifact.

This packet reviews the five consecutive RNG/null entries immediately before the
point-number lifecycle block in `CIRCLE_TEXT`:

| Entry | CIRCLE_TEXT | Load | File | Body | v137 outcome |
| --- | --- | ---: | ---: | ---: | --- |
| `randring1_next16()` | `0AAF:1180` | `0xBC70` | `0xD470` | `0x0D` | exact natural C++ |
| `randring1_next16_and(unsigned int)` | `0AAF:118E` | `0xBC7E` | `0xD47E` | `0x15` | exact natural C++ |
| `randring1_next16_mod(unsigned int)` | `0AAF:11A4` | `0xBC94` | `0xD494` | `0x19` | reviewed, source/origin unresolved |
| `NULLFUNC_NEAR` | `0AAF:11BE` | `0xBCAE` | `0xD4AE` | `0x01` | reviewed, source/origin unresolved |
| `NULLFUNC_FAR` | `0AAF:11C0` | `0xBCB0` | `0xD4B0` | `0x01` | reviewed, source/origin unresolved |

Independent one-byte `NOP` alignment remains at load `0xBC7D`, `0xBC93`,
`0xBCAD`, `0xBCAF`, and `0xBCB1`. None of those bytes is credited to a natural
function owner. No MZ relocation site overlaps either v137 exact owner.

Fresh attested Ghidra constructs only `randring1_next16_and()` in this packet:
its body is exactly image `0x1BC7E..0x1BC92` and terminates in `RET 2`.
Fresh Ghidra has no function entry at `0x1BC70`, `0x1BC94`, `0x1BCAE`, or
`0x1BCB0`. Pinned TASM, target raw decoding, and TLINK publics keep all five
entries visible. Ghidra absence therefore receives no ownership veto and no
exactness credit by itself.

## Natural source

`src/main/math/randring1_next16.cpp` reconstructs the 13-byte near function.
The source SHA-256 bound by both formal replay receipts is
`0bab87a865cef8ec405ce97d6a22a43b56b59b6e1ccb0da688a42846084f89e3`.
It models the target-proved word `randring_p` storage while incrementing only its
low byte, using the same Borland register-pseudovariable technique already
accepted for adjacent randring code. The complete target/candidate owner SHA-256
is `c27e97be00882e3e236241c44b423c0e1fb9b7d237e0c83ec209674e4993efc4`.

`src/main/math/randring1_next16_and.cpp` reconstructs the 21-byte near Pascal
function. The source SHA-256 is
`3827f1aa350527de3b445d1c9bb7ad22acea4314aa6468143f3b1ba2d544558b`.
The target reads the Pascal argument through the historical stack/register shape
`MOV BX,SP; AND AX,SS:[BX+2]`; the maintained source expresses that through the
repository's tracked `_SP` / `_SS` / `peek` 16-bit ABI idiom rather than inline
assembly or target-derived bytes. The complete owner SHA-256 is
`76c1425512e9bb1aee3ce84148365b6196b9ad42bbf0adc4cdbc7533aa3ef69a`.

Neither source uses inline assembly, `#pragma codestring`, target byte arrays,
fake returns, inert padding, target patching, or a fabricated calling convention.

## Replay-only layout seam

The original `CIRCLE_TEXT` contribution contains alignment and still-unresolved
functions around these two natural owners. v137 therefore source-extracts the
prefix and one-byte gaps into hash-bound replay-only TASM objects, and leaves
`randring1_next16_mod()` plus the null entries in target-derived residual source.
Those residual bytes receive no source or exactness credit.

The bounded pre-replay diagnostic link placed the two natural owners exactly at
`0AAF:1180` and `0AAF:118E` and matched their target bytes. That diagnostic is
zero-credit. During recovery, two ad-hoc comparisons initially used incorrect
MZ file-offset arithmetic: one double-added the target header and another assumed
the diagnostic candidate had the same header size as the target. Recomputing by
load-module address fixed both checks. Formal replay below is authoritative and
uses the repository's configured MZ/load mapping rather than either diagnostic.

## Formal focused replay

Focused command:

```text
python3 scripts/replay_th04_main_exact_units.py --unit th04-main-randring1-next16-v137 --run-id gptweb-v137-randring1-focused-001
```

Receipt SHA-256:
`20ce8610e2ba555d6565e238436f3fee0cd9bf3607afab06346b725e9cc678d6`.

The two isolated builds pass the complete 108-owner dependency closure. Both
v137 units pass raw, exact MAP contribution, ordered relocation, OMF, and
determinism gates:

- `randring1_next16()`: `CIRCLE_TEXT 0AAF:1180`, size `0x0D`, no overlapping
  relocations, `r1next.obj` raw SHA-256
  `06e6e4bdf4219d7a28cb7ec83d0d37e9194b82232b86fecaa10a5883d22f848e`,
  dependency-normalized SHA-256
  `2a37043af98aa5a8513f92ac48360097da212746d04358edc1eb6eaa11834b8f`.
- `randring1_next16_and(unsigned int)`: `CIRCLE_TEXT 0AAF:118E`, size `0x15`,
  no overlapping relocations, `r1and.obj` raw SHA-256
  `db6d316c6d649198a20aa2e5e88b9f0df7a6177dbfc9d48bc84900f785400d31`,
  dependency-normalized SHA-256
  `a5ac631df716ca3607b21c9063da94e46a5eeb7dd593ff23dba5c232b616c278`.

Focused A/B candidate MAIN identity is
`a5fc38ca41550e3b0faf25d54cb5eb0c65504eb195039793b9aa9ed7f49adc63`.

## Aggregate replay

Aggregate command:

```text
python3 scripts/replay_th04_main_exact_units.py --run-id gptweb-v137-randring1-aggregate-001
```

Receipt SHA-256:
`809e96dc5619aa61778f0944aa3a6a32ca104f0e9c614c706d739b8a5cd01a90`.

Both isolated aggregate builds pass all **172** default natural-C/C++ owners.
No previously exact owner regresses. The two v137 slices retain the same raw,
MAP, relocation, and OMF identities as focused replay. Aggregate A/B candidate
MAIN identity is
`ad3892d8093df45c1fb6452e288dcd6e9f8cfb0b900909c3686827fa9efc47f8`.

## Independent function review

The v137 review metadata deliberately contains the fresh complete Ghidra entry
for `0x1BC7E` and no synthetic entry for `0x1BC70`. The aggregate v137 MAP and
private target are then screened through `scripts/review_th04_main_functions.py`.
The retained report SHA-256 is
`16036df3bbaf86ec5242d0530f181aba61af2cddbb0c7430d73e8ee7aab99ece`.

`randring1_next16_and()` is an ordinary strict automatic admission: its 21-byte
Ghidra body starts at the same TLINK public and lies wholly inside the exact
natural owner.

`randring1_next16()` uses the pre-existing `reviewed_exact_no_ghidra` path. The
reviewer requires its exact owner and generated public, independently decodes all
13 target bytes as four instructions through terminal `RET`, and verifies that
the owner ends exactly at `0x1BC7D`, before the unowned target NOP. No Ghidra
metadata is synthesized for the missing entry.

The private reviewer screen reports 300 exact admissions out of the 302 entries
covered by its current configured review universe, with 150 automatic, 150
manual, and zero strict rejections. That report is not the campaign denominator:
the live authored-function ledger also contains three newer v136 blocked pointnum
functions, so repository status after v137 promotion is **300 / 305 exact**.

## Accounting and retained unknowns

After v137 promotion the live reviewed authored C/C++ accounting is:

- **47,564 / 47,771 bytes exact (99.566683%)**;
- **300 / 305 functions exact (98.360656%)**;
- **172 exact natural-C/C++ owners**.

`randring1_next16_mod(unsigned int)` remains reviewed but source/origin
unresolved. A bounded stack-peek natural TC4J probe reaches the target 0x19-byte
size but orders `MOV BX,SP` before `XOR DX,DX`, unlike the target. That is a
source/code-generation mismatch, not permission for inline assembly or byte
injection. `NULLFUNC_NEAR` and `NULLFUNC_FAR` remain reviewed one-byte target
entries with unknown source/origin and receive no exactness credit.

## Factory Truth-Kernel state

Post-commit Factory replay is intentionally separate from the repository cold
replay above. Both claims originate from repository exact checkpoint
`bb36fa09797ec6baaab95e82510ba7377c10cbb3`. The first controlled replay used
that clean snapshot. The successful sibling retry remained bound to the same
commit/tree while the two documentation-only post-commit edits were present;
Factory independently accepted that bound snapshot.

`claim:unit:th04-main-randring1-next16-v137:owned-extent-exact` is independently
accepted. Controlled job `job:bd788d6bb4f44681bc0867e6e92a9178` completed with
receipt `receipt:50309921428bfd73a0f4303f51cca499e47211746a81310ba7b14277a38ac7fc`,
`receipt_verdict=pass`, and `acceptance_decision=accepted`; the returned registry
identity is `registry:bf19f29e893833b1c2b9ce1335869178b27d2d5d956ce7c8de3255559ec36a62`.

The sibling
`claim:unit:th04-main-randring1-next16-and-v137:owned-extent-exact` first hit two
pre-verdict infrastructure failures. Job `job:fd96d580cf4c47f182d46a2443d649a4`
and bounded retry `job:c92fab8813c448c6b434016742d80b5a` both terminated before
an Oracle receipt because another Factory operation owned the registered TH095
worktree. Both failures have `outcome=null`; they remain infrastructure history,
not target-byte rejection. After that external lock state changed, controlled
retry `job:0698e8bf1da345e38c84fe7186917180` completed with receipt
`receipt:10c933dff77a1042832990364b5fb2a032207e9914ee4f4a22e8da2d4255bf6e`,
`receipt_verdict=pass`, and `acceptance_decision=accepted`; the returned registry
identity is `registry:5249a655c14970b38965fbc584258cb413ebba6235f31ce5dfcc89f8c77d7d4c`.

Repository exactness for both v137 owners remains established by the focused and
aggregate receipts above, and both imported v137 `owned_extent_exact` claims now
have independent Factory-accepted replay history. Those acceptances do not
establish standalone product closure, runtime-storage identity, or runtime-
scenario validation.
