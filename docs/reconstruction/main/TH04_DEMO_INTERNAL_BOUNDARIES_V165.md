# TH04 DEMO_TEXT internal boundary review (v165)

## Scope

This packet reviews three target-called internal functions in `th04-main / MAIN.EXE / DEMO_TEXT` without trusting Ghidra cross-links or the absence of TLINK publics. It intentionally expands the reviewed authored denominator and does not claim exact reconstruction.

Target identity remains the 156,258-byte `candidate-local-attested` Japanese `MAIN.EXE`, SHA-256 `077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`. The registered `th04-ghidra` provider and the repository-native Ghidra MZ/database check both re-attested that target before review.

## Reviewed boundaries

### `gameplay_loop()`

- `DEMO_TEXT 0AAF:0098`
- MZ load `0xAB88..0xAD02`
- target file `0xC388..0xC502`
- `0x17B / 379` bytes
- target slice SHA-256 `54ac4974b571dc990934e9c5ed39afb1b91206c397b67c734442fe81fd6c4448`

Fresh Ghidra independently constructs exactly 379 contiguous body bytes through the terminal `RET`. Pinned TASM/raw decode agrees, target near `CALL` at load `0xAB6E` resolves to `0xAB88`, and `sub_AD03` begins at the next byte. The body overlaps twelve MZ relocation sites belonging to far calls.

Maintained natural source is `src/main/core/gameplay_loop.cpp`, SHA-256 `8da7b71af0efb01f15d1f3bb9e111ea2d16b374a94f3ce4cb7b8a173b242eff2`. Production-profile TC86 Borland C++ 4.02 compiles it without warnings to valid OMF but emits 370 CODE bytes, nine short of target. The dependency-normalized OMF SHA-256 is `0dd46474b0b7d8cc2451d191b6dcd6450e21ee19af329ca620489d4e29e674bf`. Remaining source-shape differences include target register/dataflow around stage-frame/play-performance timing and linked same-segment call shaping. This is `source-present` / nonexact compiler evidence only.

### `gameplay_session_init()`

- `DEMO_TEXT 0AAF:0213`
- MZ load `0xAD03..0xAECF`
- target file `0xC503..0xC6CF`
- physical `0x1CD / 461` bytes
- executable `0x1C2 / 450` bytes through `RET` at `0xAEC4`
- zero compiler metadata byte at `0xAEC5`
- five jump words at `0xAEC6..0xAECF`
- target slice SHA-256 `2e37dff3ee0d9933fc207c7157cc5bdb3a8dd582128a07089f4cac2538cf833b`

Ghidra cross-links this entry into unrelated earlier code. Pinned TASM, gap-free raw decode, the next local PROC, and target near `CALL 0xAF10 -> 0xAD03` instead close the physical extent above. The five table words resolve to loads `0xAE17`, `0xAE3C`, `0xAE4E`, `0xAE77`, and `0xAEA0`, all decoded instruction starts. No MZ relocation overlaps the physical owner.

Maintained natural source is `src/main/core/gameplay_session_init.cpp`, SHA-256 `d42f952cdf7e1c500c70a186ca6c702f8f125a184101c2849752af834e58e714`. Production-profile TC4J emits 460 CODE bytes with the intended rank-switch producer shape, one byte short of the target physical extent because the candidate places the five-word table immediately after `RET` and omits the target zero metadata/alignment byte. The dependency-normalized OMF SHA-256 is `32e2dba9c27a2427a5a8654189e09cd325de04467de7384bd4e9550384e70c41`.

A new falsifiable compiler-mechanism probe added `#pragma option -a`, motivated by earlier dense-switch metadata recovery. It still emitted 460 CODE bytes and did not create the target byte. The aligned-probe raw OMF SHA-256 is `03c4ce16fa27dcd2d8e91ac3578a87a6e090e4d7dcd84084febbd5eaab7f41ca`, normalized SHA-256 `3f3816a7fb86d687253b082630eaa75b49b2f2cde9366a6e4c17ed00755d1075`. Do not continue alignment-pragma spelling without a new mechanism.

### `stage_session_init()`

- `DEMO_TEXT 0AAF:03E0`
- MZ load `0xAED0..0xB1CF`
- target file `0xC6D0..0xC9CF`
- physical `0x300 / 768` bytes
- executable `0x2F2 / 754` bytes through `RET` at `0xB1C1`
- seven jump words at `0xB1C2..0xB1CF`
- target slice SHA-256 `8a00b573ab1fa3127a37a24b4cd9f8a5ed7558296a3b7233a617b7a49b07537c`

Ghidra cross-links this function over seven ranges into unrelated code. Pinned TASM/raw instead close the physical extent at the next local PROC `sub_B1D0`. Target near `CALL 0xAB6B -> 0xAED0` independently anchors the entry. The seven table words resolve to `0xB003`, `0xB04B`, `0xB071`, `0xB097`, `0xB0D4`, `0xB0F9`, and `0xB11E`, all decoded instruction starts. The function contains numerous far-call MZ relocations. No maintained natural source is claimed in v165.

## Function-review control-plane change

The function reviewer now has a fail-closed `reviewed_nonexact_internal_call` path for target-called internal functions that have no TLINK public. Admission requires a real Ghidra function entry, a target near-call anchor resolving exactly to the entry, an immediately adjacent configured next boundary, raw terminal `RET`/`RETF`, and full accounting of configured trailing compiler data. Cross-linked Ghidra bodies require explicit opt-in. `new_nonexact` remains mandatory before a newly reviewed function may enter the authored ledger.

The optional `owner_unit` / `source` projection is used only when a maintained source-present candidate exists. It records source presence without granting exactness. The v165 trial reviewer adds exactly the three functions above; unrelated historical note/name rewrites from the generic writer are deliberately not adopted.

## Verification state

There is no v165 focused exact-unit replay, aggregate replay, or Factory exact claim because no v165 function is exact. Repository-native exact owners from v164 remain unchanged. This packet establishes reviewed authored boundaries and maintained natural source presence for two functions, not byte exactness, production closure, runtime-storage identity, runtime-scenario validation, whole-image exactness, or pristine provenance.

The reviewed MAIN denominator therefore grows by `0x348 / 840` bytes and three functions. The exact numerator is unchanged.

## v238 compiler placement control

The target `gameplay_session_init()` ends with `RET` at DEMO_TEXT
`0AAF:03D4` (load `0xAEC4`), then `00` at `0AAF:03D5` and five jump words
from `0AAF:03D6`. A pinned TC4J probe compiled the unchanged v165 source alone
and after a naturally emitted five-byte function in the **same** `DEMO_TEXT`
segment. The ordinary source reproduces its prior 460-byte object CODE SHA-256
`c6240957d82e978078e247c06dd9c0ae79469661e8ac4c612474b8b24218d526`.
The added function moves the initializer to odd object offset 5, but its jump
table still begins immediately after `RET`: object offsets 450 versus 455,
with no inserted byte. Simple odd starting position therefore does not explain
the target zero under this compiler profile. This does not classify the target
byte as compiler output or linker fill; the historical OMF is unavailable.

A related `gameplay_loop()` probe kept its 370-byte diagnostic object CODE
unchanged after declaring `stage_frame` volatile. Moving the increment into
`stage_frame_mod16 = (++stage_frame & 15)` changed only object byte `0x117`
from `A0` to `A1`; it did not emit the target `MOV AX; MOV DX,AX; INC AX;
MOV [stage_frame],AX` sequence. The target loop remains 379 bytes and blocked.
The isolated source, valid OMF objects, compiler logs, and full hashes are in
`.analysis/reconstruction/probes/v238-gameplay-switch-align/receipt.json`,
SHA-256 `d4706c035f945aab1fbd186eecb3e68efbe0e3dae607ac610d7808c122eb8fed`.
No source or exact state changed; the 25 MB temporary build clone was removed.

## v376 session metadata producer matrix

The remaining `gameplay_session_init()` blocker is still exactly one physical
byte: target executable code ends with `RET` at load `0xAEC4`, target byte
`0xAEC5` is zero, and the five jump words occupy `0xAEC6..0xAECF`. The
current pinned-TC4J source emits 460 bytes with the same rank-switch structure
but puts the five jump words immediately after `RET`.

A new isolated producer matrix rules out several plausible historical-TU and
compiler explanations. The baseline command-line TC4J object remains 460 bytes
with CODE SHA-256
`c6240957d82e978078e247c06dd9c0ae79469661e8ac4c612474b8b24218d526`.
Compiling the exact 379-byte gameplay producer before it yields `379 + 460`;
compiling exact `_main` plus gameplay before it leaves the session public at
offset `0x1F7` and still 460 bytes. Appending the maintained
`stage_session_init()`/`stage_runtime_init()` producer places
`stage_session_init()` at `+0x1CC`, not `+0x1CD`, while preserving that
producer's known 768-byte first logical extent. Therefore the target zero is not
naturally created merely by the real preceding or following DEMO_TEXT functions.

Near/far, C/C++, and C/Pascal declaration variants all stay at 460. Explicit
`return;`, explicit `default: break;`, and their combination optimize to the
same baseline object. Function-level option probes produce `-G` 465 bytes,
`-O-` 462, `-k-` 456, `-Z-` 492, and `-r-` 467; `-G-`, `-O`, `-k`,
`-Z`, `-r`, `-a1`, and `-a2` remain exactly 460. None yields the target
461-byte layout.

This is not evidence that TC4J cannot generate a post-return zero: accepted
natural `midboss4_update()`, near `midbossx_pattern_events()`, and
`midbossx_update()` objects contain compiler-emitted zero bytes before their
switch metadata/tables. The unresolved question is therefore a more specific
historical switch-data/OMF materialization mechanism. Private probe receipt:
`.analysis/gpt-web/gameplay-session-fusion-001/receipt.json`, SHA-256
`448a90e324fa121a8f172bedd6b4c3a11509a4c81bb0874e4697870ecf443720`.
No product source, exact-unit state, or reviewed denominator changes in v376.
