# TH04 MAIN gameplay entry reconstruction (v202)

## Scope

v202 reconstructs the gameplay `_main` entry in `MAIN.EXE` as maintainable
natural Turbo C++.

The reviewed target extent is `DEMO_TEXT 0AAF:001C`, load
`0xAB0C..0xAB87`, file `0xC30C..0xC387`, size `0x7C / 124`, SHA-256
`fd82b0be8ecde06f30c04b2f3066380ffa9017cb7bba9118da46418f05235a2e`.
It is a FAR body and ends in `RETF`; `gameplay_loop()` begins at the following
byte, load `0xAB88`.

The MZ startup entry is `CS:IP = 0000:0000`. Raw target decode shows a direct
FAR call at load `0x013B` to `0AAF:001C`. Fresh target-bound Ghidra independently
constructs the complete contiguous 124-byte function, reports the startup as its
only caller, and reports twelve callees. Ghidra remains provisional navigation
only and receives no exactness credit.

Six ordered MZ relocation words lie inside `_main`, at loads `0xAB23`,
`0xAB38`, `0xAB3D`, `0xAB46`, `0xAB5D`, and `0xAB69`. The final `GameExecl()`
call is same-group code: TLINK performs the length-preserving historical
relaxation from a normal FAR object fixup to target `NOP; PUSH CS; CALL near`, so
it adds no MZ relocation.

## Natural source

Maintained source is `src/main/core/main.cpp`, SHA-256
`b1eeed5be7cf8d8082108667cab3af616fefdac0bf1f501c22d269926ff3c295`.
It expresses only the target-proved gameplay startup sequence:

- load the resident pointer and return if absent;
- reserve `320000 >> 4` memory paragraphs;
- run `game_init_main()` and copy the resident random seed;
- allocate/preload EMS eyecatch data;
- clear text, back up gaiji, and load `GAMEFT.bft`;
- select sound modes and load the stage SE file;
- run the stage-session/gameplay loop while `quit == Q_NEXT_STAGE`;
- execute the OP binary through same-segment `GameExecl()`.

The source uses the real MASTER.LIB declarations from `pc98_gfx.hpp`; no inline
assembly, target-derived byte array, codestring, byte emitter, fake return,
padding, or target patch is present.

A bounded standalone TC86 Borland C++ 4.02 probe first established the source
shape before replay integration. Its valid OMF object SHA-256 is
`652060d2cd1423af76ebb659c7d369d30c167e8d6aeaf2905f6f48b4343589da`.
TC4J emits exactly 124 DEMO_TEXT bytes and one `_main` public. Fixed bytes match
the target directly; symbol fields are ordinary OMF fixups. The final object
FAR `GameExecl()` call is the expected linker-relaxation form described above.
This probe was source-shape evidence only; exactness comes from the linked cold
replays below.

## Physical producer split

The old monolithic scaffold supplied `_main` and the following DEMO helpers in
one object. v202 inserts `th04/mainent.cpp` before `th04_main.asm`, removes only
the historical `_main` body from the monolith, and leaves all following DEMO
bytes in the original object.

Focused MAP proves:

- `th04/mainent.cpp`: `DEMO_TEXT 0AAF:001C +0x007C`;
- shortened `th04_main.asm`: `DEMO_TEXT 0AAF:0098 +0x0866`;
- the following maintained `th04/demo.cpp` owner still starts at `0AAF:08FE`.

Three previously internal, reviewed-nonexact helpers must become link-visible so
natural `_main` can call across the new object boundary:
`gameplay_loop()`, `stage_session_init()`, and `_stage_session_free`. v202 adds
only OMF public aliases at their existing addresses. Their source, extents, raw
bytes, relocation verdicts, and nonexact status are unchanged. Their existing
`reviewed_nonexact_internal_call` policies explicitly acknowledge the generated
publics; no exact credit is transferred to them.

Four existing string/data labels are similarly published as aliases for the
natural object. This changes symbol metadata only, not storage or layout.

The source transform is fail closed against both observed v201 focused and
aggregate scaffold hashes. Focused history used a `nopcall GameExecl` textual
adapter while aggregate history used the equivalent expanded `NOP; PUSH CS;
CALL near`; v202 first performs one uniquely scoped optional normalization at
`_main` and then validates/removes the same normalized body digest.

## Cold replay

The authoritative focused run is
`gptweb-v202-main-entry-focused-candidate-004`:

- selected owners: 139;
- two isolated cold builds;
- `failures=[]`;
- receipt SHA-256
  `58d3ed4dd8b45c238f84d76243506868637c517cfac5e9d14299e6cabe7d47ba`;
- A/B `mainent.obj` raw SHA-256
  `85235e275214ae905e7c2e957714d6e2cb86e2650b7fe00e1c6ecd5a0edb5745`;
- A/B dependency-normalized `mainent.obj` SHA-256
  `8c545d6bc1d0129c960a29c72bc2cb40a10617be4dea0cbb2d2b2442ca6650b5`;
- A/B MAP SHA-256
  `b92af86d956216beec421793248dbe14de11deeeca0ee30cc369dbe7c451756a`;
- A/B candidate MAIN SHA-256
  `ad51bc32345301eb9e212bc009e6ce757fe24d10c77e0dbc20de4a398648c0a6`.

The owner is `raw=True`, `map=True`, and `relocs=True`; target and candidate
ordered relocation overlap is identical at all six sites.

Candidate no-unit aggregate
`gptweb-v202-main-entry-aggregate-candidate-001` passes all 243 candidate-state
default owners twice with `failures=[]`; receipt SHA-256 is
`70e7103bfc716645980dabea6d2934184d526e1bd6785d48ef638d0dbd4e5ce8`.

After promotion, no-unit aggregate
`gptweb-v202-main-entry-aggregate-final-001` again passes all 243 tracked default
owners twice with `failures=[]`; receipt SHA-256 is
`106cb3d8fa621168ea5a52106dfd706260e72b68056e9ce0944bd755616b9ac0`.
Tracked exact-manifest SHA-256 is
`9cadda0658a6c54db63e02e41b57b999561ea114674797240336cb162bd95a75`.
Final A/B MAP SHA-256 is
`4a565e0cff733a69ae1dbb976234333a65bb81d624c09989fc22a7d312821d05`;
A/B candidate MAIN SHA-256 is
`1932b7feb681e3fa198d24a10cd93a70ce2cb6d400d1ecab39545cafa26b9f9b`.

## Function review

Unlike several CIRCLE callbacks, fresh Ghidra constructs `_main` as a complete
contiguous function. The strict reviewer therefore uses the automatic exact
path: target Ghidra body, generated TLINK public, exact byte owner, raw terminal
`RETF`, and target-bound metadata must all agree.

The v202 trial report SHA-256 is
`1416aca86c7405187e3a4cde1773ef22559f9ac1cb078497d5ed8613fa089894`.
The trial ledger SHA-256 is
`66a5aae5f3673256362c3fd3b480cea9cd9b9295462a12da611d3a32f5d3e6e3`.
It grows the maintained ledger from 482 to 483 rows by adding exactly
`th04-main-fn-1ab0c` and removing none. The generic writer proposes 43 unrelated
historical normalization changes; only the new validated `_main` row is merged.

The split-generated publics for the three old DEMO helpers initially caused the
reviewer to fail closed because their historical policy required no TLINK
public. Their existing nonexact policies were then updated with the actual
new generated public names. This acknowledges the physical split without
changing any helper's nonexact verdict.

## Other TH04 artifacts

No fresh OP/MAINE/ZUN unpack is claimed in v202. Instead, the existing
independently attested packed targets and retained boundary-review payloads are
rebound by SHA-256 and scanned against the 124-byte MAIN `_main` body.

- OP payload: 69,028 bytes, SHA-256
  `13222cb667e15c5034bd64c840a1db0a07c9acbb56e50f0bcf6025d12fe78d74`;
  longest exact run is 15 bytes.
- MAINE payload: 62,414 bytes, SHA-256
  `7495ae43641bc696d13d18c366e364f6bc8b6a86a1afb681f34c9a334dae792c`;
  longest exact run is 15 bytes.
- ZUN payload: 13,422 bytes, SHA-256
  `baf5a58b333af1135d67c7dd7a4f86e2c828ae149c8219d5d1f589073b0bde9e`;
  longest exact run is 3 bytes.

The OP/MAINE 15-byte match is a generic resident-mode-load/FAR-call sequence,
not a complete producer. Packed `ZUN.COM` still begins with `MZ`. This is
negative routing evidence only; no MAIN source, boundary, or exactness credit is
transferred to any other artifact. Routing receipt SHA-256 is
`c1f197942448b480da76c27a4cb6ba9c6e4f15835c61f81692440e6a9ac4bea1`.

## Recovery and negative controls

Several fail-closed controls receive zero exactness credit:

- the first standalone probe omitted the DOS TCC search path;
- the next self-contained probe used `true` without a supporting definition;
- the successful compiler invocation wrote its ignored object to repository CWD;
  recovery audit established current-session ownership, copied the object to
  bounded v202 scratch, and removed only that object;
- focused-001 rejected the focused scaffold's historical `nopcall GameExecl`
  spelling at the normalized `_main` span hash gate;
- focused-002 rejected an over-broad optional normalization because two
  `nopcall GameExecl` sites existed;
- focused-003 reached TLINK and proved natural `mainent.cpp` compilation but
  exposed probe-style `_text_clear` / `_gaiji_backup` names. The maintained
  source was corrected to use the actual MASTER_RET declarations rather than
  adding fake aliases;
- early function-review attempts rejected newly generated publics on historical
  reviewed-nonexact internal DEMO helpers. Their policies were explicitly and
  narrowly updated to acknowledge the split-created public names while keeping
  every nonexact verdict intact.

These are compiler/control-plane recovery observations, not target mismatches.

## Accounting and verification planes

After v202, live MAIN accounting is:

- exact reviewed C/C++ bytes: `75,620 / 81,279` (`93.037562%`);
- exact reviewed functions: `460 / 483` (`95.238095%`);
- MAIN authored routing: 503 candidates, 460 exact, 24 blocked, 19 unreviewed,
  and 65 ASM-attestation observations.

Original-style ASM remains a separate accounting plane; v202 adds no ASM owner.

Repository-native exact physical and function ownership is established for the
natural `_main`. Standalone TH04 product compile/link closure, whole-image
exactness, runtime-storage identity, runtime-scenario validation, portable
runtime validation, independent pristine-release provenance, and v202 Factory
Truth-Kernel acceptance remain unestablished.

## Analysis lifecycle

`.analysis/` started v202 at **3,963,193,860 bytes** and peaked at
**4,226,635,831 bytes** after failed controls plus focused/candidate/final cold
replays. After proving no active TCC/TASM/TLINK/replay producer, only explicit
v202 failed runs were removed; focused-004 and the candidate aggregate were
compacted to receipt-only state after their receipts and compact OMF/MAP evidence
were copied into v202 durable scratch. The complete 243-owner post-promotion
aggregate remains the current cold baseline. Pre-final-CI `.analysis/` is
**4,043,321,084 bytes**. Full final `python3 scripts/ci.py` returns `CI: PASS`;
after its live Ghidra replay, `.analysis/` is **4,043,350,901 bytes**, net growth
**80,157,041 bytes** from v202 entry. Older baselines, private targets,
toolchains, Wine/Ghidra state, unrelated ignored objects, and legacy/unknown
analysis content remain untouched.

## Continuation

The next evidence-connected structural candidate is `sub_3680` in `_TEXT`, load
`0x3680`, analysis `0x13680`, size `0x75`, FAR. The boundary is currently only
corroborated (`ghidra+tasm-proc`) and source/origin remain unresolved. Fresh
v202 target-bound Ghidra constructs one contiguous 117-byte body and reports one
caller: the independently exact v195 `MPN_LOAD` at `0x1B8FC`. Next review should
bound its physical owner against neighboring MASTER.LIB includes, ABI/data
inputs, target callers, TH04/TH05 lineage, relocations, and natural TC4J
feasibility before assigning source or original-ASM origin.
