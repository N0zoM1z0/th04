# TH04 `MAIN.EXE` accepted reconstruction

This is the compact acceptance and replay note for reconstructed MAIN owners.
It is not a chronological batch log and not a work queue. Current counts come
only from:

```bash
python3 scripts/status.py
```

`config/units.csv` owns byte state,
`config/th04_main_authored_functions.csv` owns reviewed function state, and
`config/th04_function_boundaries.csv` owns all-artifact routing. Git history,
`config/evidence.csv`, and `config/knowledge.csv` retain the former v1-v107
batch detail without presenting old frontiers as current instructions.

## Scope and current meaning

The accepted set consists of bounded, maintained TH04 source owners that pass
the configured Oracle stack against the hash-attested Japanese `MAIN.EXE`.
ReC98 revision `b6ba5b0a529edbb31efdf8c0e939263804f8ee47` supplies pinned clean-build
scaffolding and candidate provenance only.

The generated [progress summary](../PROGRESS.md) reports the live reviewed
denominator. It is not whole-executable or whole-game completion. `OP.EXE`,
`MAINE.EXE`, and `ZUN.COM` have separate identities and currently have no
accepted reconstruction units.

## Cold replay contract

`config/th04_main_exact_units.toml` and
`scripts/replay_th04_main_exact_units.py` define acceptance. Each replay:

1. attests the selected target and pinned TC4J/TASM/TLINK/MS-DOS Player
   toolchain before execution;
2. freezes every live repository input to one path/size/SHA snapshot;
3. materializes two independent source trees from the pinned ReC98 commit;
4. materializes and attests the one-line `compat/rec98/` forwarding boundary;
5. overlays only declared maintained translation units or hash/offset-bound
   fragments and transformations;
6. preserves source metadata that affects Borland OMF records;
7. builds serially in the declared input order;
8. validates each emitted Intel OMF module and deterministic normalized OMF
   identity;
9. verifies exact TLINK contribution placement and complete ordered overlapping
   MZ relocation sequences;
10. requires raw zero difference over every complete accepted extent in both
    cold builds;
11. records source, build-graph, object, map, relocation, and output digests;
12. fails if a dependency, source snapshot, boundary, or accepted owner drifts.

Focused replay includes the dependency closure of selected owners. Aggregate
replay selects every default accepted owner and is required after shared
headers, flags, segment declarations, link order, or global layout changes.

```bash
python3 scripts/replay_th04_main_exact_units.py --unit UNIT_ID --run-id RUN_ID
python3 scripts/replay_th04_main_exact_units.py --run-id RUN_ID
```

An overlay replay is an exactness Oracle. It is not evidence that this
repository already has a standalone TH04 build; the tree still lacks many
translation units, localized declarations, and a complete TH04-owned link
graph.

## Boundary and function accounting

An exact byte owner does not automatically prove all internal function
boundaries. `scripts/review_th04_main_functions.py` combines target-local raw
decode/control flow, an attested Ghidra view, TLINK ownership, TASM local
`PROC` observations, exact owner containment, and explicit manual exceptions.

The reviewer fails closed for:

- missing or sparse Ghidra bodies;
- internal functions without original linker publics;
- shared tails and noncontiguous body sets;
- compiler switch tables trailing a return;
- generated publics introduced only by reconstruction;
- ownership extents that cross the next proven function or contribution.

Function exactness requires complete containment in an exact authored owner.
The all-artifact boundary ledger is a discovery/routing inventory and cannot
promote function or byte state by itself.

## Maintained source and layout

Product source follows the TH08-style semantic layout under `src/main/`.
Reconstruction state never appears in a directory name. A `.cpp`, `.c`, or
`.asm` file is a translation unit; `.inl` is reserved for a bounded body that a
semantic translation unit includes.

Direct ReC98, `libs/`, `platform/`, or another game's include paths are not
product dependencies. Existing unlocalized declarations cross only checked-in
one-line `compat/rec98/<upstream-path>` forwarders. Recover the declaration
under its TH04 owner or proved `src/shared/`, replay every affected owner, then
remove the forwarder.

## Current nonexact MAIN cases

The live authoritative states are in the ledgers. The focused producer
constraints and disproved approaches are kept in
`TH04_MAIN_FIXUP_CODEGEN_PROBES.md`:

- reviewed `snd_load` has four nonexact bytes;
- reviewed `enemy_bullet_template_push` has a complete 27-byte nonexact extent;
- `dialog_op` and `dialog_run` have maintained raw-identical code but mismatched
  ordered MZ relocation sequences and remain outside the reviewed exact
  function denominator.

Do not manufacture equality with inline assembly, target opcodes, `__emit__`,
`#pragma codestring`, hand-edited compiler output, patched OMF, or fake padding.

## Reusable Borland findings

These conclusions remain useful beyond the historical batches; their detailed
evidence IDs are indexed in `config/knowledge.csv`.

- Translation-unit and segment boundaries can alter LEDATA/FIXUPP batching and
  MZ relocation order even when code bytes are unchanged.
- A target-contiguous range with a near bridge across reconstructed segments
  can disprove the reconstructed TU/segment split. Verify final symbol address
  and displacement, not merely a plausible call opcode.
- `#pragma samecodeseg` changes fixup framing; TLINK's normal far-to-near
  optimization can produce `NOP; PUSH CS; CALL near`. It is not a universal
  substitute for correct producer ownership.
  v99 gives a concrete positive case: `#pragma samecodeseg GameExecl` removes
  one segment relocation per END_TEXT caller and reproduces the target
  optimized call sequence without inline byte emission.
- The first declaration of a symbol can affect Borland segment/group fixups.
- Local declaration order can control BP-relative stack-slot allocation.
- `-WX` affects both control-flow code generation and SEGDEF alignment. A
  zero-code translation unit may restore layout without claiming padding.
- Borland segment-specific pointer types such as `__es` can produce instruction
  forms that generic far pointers and `MK_FP` do not.
- Sparse `switch` syntax can reproduce one-load/shared-compare lowering that a
  semantically equivalent `if` chain cannot.
- TC4J expression grouping is codegen-significant: parenthesizing an inner
  constant-index term before adding a random term can change the exact AX/DX
  accumulation order without changing semantics.
- Equivalent early-return and `if/else` forms can differ by a near-vs-short
  conditional branch and therefore by whole-function size. Preserve the target
  control-flow shape instead of optimizing source aesthetics during matching.
- A `static inline` helper with an early return may duplicate extra branch bytes
  at every inline site. The Gengetsu dispatcher matched only after four such
  blocks were expressed as direct nested `if` statements, with no byte emission.
- Compiler switch tables can belong to the authored function extent even when
  Ghidra stops at the return; every table target must decode to an instruction
  boundary inside the reviewed function.
- Ghidra entries and linker publics are both incomplete function universes.
  Local TASM boundaries, raw call targets, return tiling, and adjacent ownership
  must close the gap.
- ReC98 structures and semantics remain hypotheses: target member offsets,
  constants, and control flow have disproved multiple plausible candidates.
- Turbo C++ OMF COMENT metadata is real build output. Normalize only the
  explicitly attested dependency timestamp fields, never code/data/fixups.

## Latest boundary expansion

v99-v107 expand the reviewed denominator outside the completed MAIN_036 frontier.
Three contiguous END_TEXT FAR functions (`end_game_good`, `end_game_bad`, and
`end_extra`) are exact from one maintained pure-C++ 0x7C-byte producer. v100
then recovers the final 0x65 bytes of END_TEXT (`map_load` + `map_free`) from
target-first natural C++ despite ReC98 having no C++ body. v101 then corrects
`gengetsu_fg_render` from Ghidra's sparse 0x5-byte body to the TASM/raw/segment-
end-proved 0x18E-byte BOSS_FG_TEXT suffix. v102 then recovers the 0x91-byte
BOSS_BG_TEXT Mugetsu/Gengetsu renderer and target-verifies backdrop coordinates
(32,16), disproving the initial reversed hypothesis. v103 then recovers the
0x2B TILE_TEXT `enemies_invalidate` prefix from pure C++; the following 0x90
remains excluded alignment padding and is reproduced naturally by TLINK before
the remaining word-aligned assembler contribution. v104 then recovers the 0x65 MAIN_01_TEXT `BB_TXT_LOAD`/`BB_TXT_FREE` prefix from pure C++, including the target far-pointer offset for the second file read. The same review returns `pointnums_add_yellow` to provisional because its 0x1A Ghidra body jumps into a shared tail at 0x23DBE that is also reached by `pointnums_add_white`. v105 then recovers the following 0x91-byte `mugetsu_fg_render` prefix from natural C++; its first cold build exposed the separate-public ownership hazard, fixed by changing the assembler top-level PUBLIC to EXTRN when TC4J becomes the producer. v106 then recovers the following 0x4B `gengetsu_bomb_inv_render` helper from pure C++, replacing the previously published semantic alias with maintained source. Its first probe was two bytes too long because a fixed `_SI` expression produced MOV+ADD; compiler-managed register allocation emits the target LEA. This closes the target-derived C/C++ contribution in MAIN_01_TEXT while leaving the independent scoreupd.asm owner separate. v107 then opens MAIN_033_TEXT with the 0x8C Mugetsu gather prefix. Fresh Ghidra correctly sees the first 0x15 helper but truncates `mugetsu_gather_intro` to 0x11; TASM/raw/reviewer proof expands it to 0x77, consisting of 0x67 code bytes plus contiguous 4-word compare and 4-word jump tables through 0x280BA. Focused and 145-owner
aggregate cold replays preserve raw bytes, exact map contribution, ordered
relocation overlap, and deterministic TC86 OMF. Segment-edge owners remain
natural C++ without manufactured padding. Candidate-C++ paths that require inline
ASM/codestring remain explicitly unaccepted.

## Historical detail

Former per-version narratives were pruned because old counts and “next
frontier” statements repeatedly conflicted with the live boundary ledger.
Nothing was made unverifiable:

- accepted source remains in `src/main/`;
- immutable decisions and replay commands remain in the CSV ledgers;
- reusable positive and negative findings remain in `config/knowledge.csv`;
- target/compiler observations and hashes remain in `config/evidence.csv`;
- the removed prose remains available through Git history.

Historical `.analysis` materializations are disposable. Keep current target,
toolchain, Ghidra, boundary-review, and latest focused/aggregate receipts; rerun
a named historical experiment only when its checked-in evidence leaves a real
open question.
