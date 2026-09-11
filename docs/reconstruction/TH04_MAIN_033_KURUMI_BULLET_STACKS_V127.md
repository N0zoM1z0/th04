# TH04 MAIN_033 Kurumi bullet stacks v127

## Exact owner

v127 reconstructs `kurumi_bullet_stacks_phase()` as maintainable natural Turbo C++.

- segment: `MAIN_033_TEXT`
- map: `13A9:55CA`
- load: `0x1905A..0x1915C`
- file: `0x1A85A..0x1A95C`
- size: `0x103 / 259` bytes
- target SHA-256: `85d2e8324f93bb6c3e7dbc88bc3c0915881bf9ea34647132d0120d75a0f1b2d3`
- sole overlapping MZ relocation: load `0x190DC`
- next physical PROC: FAR `kurumi_update()` at `0x1915D`

Fresh attested Ghidra constructs the complete contiguous 259-byte near body at
`0x2905A..0x2915C`. It reports no caller because the enclosing FAR Kurumi
dispatcher is cross-linked, but pinned TASM proves the direct call at `loc_194BE`.

The helper uses existing `boss_statebyte[]` and bullet-template storage. It
maintains the two stack angles in bytes 14/15, the stack counter in byte 13,
and uses byte 0 as the rank-selected spread interval. Stage-2 setup assigns
that interval with `select_for_rank(255, 128, 32, 8)`.

## Natural source

Maintained source:

`src/main/boss/kurumi_bullet_stacks.cpp`

Source SHA-256:

`323d68f8675eb394979eaf9f70b141b35318a37138cd5d841f21592715cceb26`

The first successful TC4J probe emitted exactly 259 code bytes and the target
control-flow/register skeleton. The only non-link differences were two
semantically equivalent angle expressions: `rand - 0x60` emits `SUB AL,60h`,
while the target has `ADD AL,A0h`. Writing `rand + 0xA0` naturally reproduces
the target shape.

The final isolated probe differs only in 48 two-byte link words plus the one
four-byte FAR `SND_SE_PLAY` pointer. Masking those unresolved fields yields
complete 259-byte equality with diagnostic SHA-256
`cbb3499f15629fa3ea7258491d419dd6969f4230d2c49fe0fcb017ddeabfd891`.

No inline assembly, target byte arrays, `#pragma codestring`, fake return,
padding, ABI lie, or target patching is used.

## Replay integration

The v126 replay-only `MAIN_033_TEXT` suffix began with the old
`kurumi_1905A` PROC. v127 removes only that PROC, declares
`_kurumi_bullet_stacks_phase:near`, redirects the single dispatcher call, and
inserts `th04/kstack.cpp` before the remaining residual suffix. The residual
assembler remains zero-credit replay plumbing.

Hash-bound transform inputs:

- input residual SHA-256: `5d60d84d16ef9eb7fac753f825fefdebe5be80387bc0e8ec46339a5f1f36de23`
- removed PROC text SHA-256: `03abe04488342cb67cc61676473fdbee83e967dc64f474c515c50cef6c765c5f`
- patched residual SHA-256: `1155fe0dd0cecf2f2af0bc7013b9186538eb87703376130bd6d0aed8d1bbcaca`
- final exact-unit manifest SHA-256: `96d210fc972968ade42114bf18039d03844625a3a56c3bff82ac6b458f3924b5`

`focused-001` failed before cold build because the initially configured patched
hash omitted the transform's replacement comment. The hash gate remained
fail-closed and was corrected from the actual transform semantics. `focused-002`
then passed diagnostically before default-owner promotion. The final focused
run was repeated after enabling the owner so focused and aggregate evidence bind
the same final manifest.

## Final Oracle receipts

Focused `gptweb-v127-kurumi-bullet-stacks-focused-003`:

- `pass=true`, `failures=[]`
- 99-unit dependency closure
- A/B raw, map, relocation, and OMF exact/valid
- map: `13A9:55CA 0103 C=CODE S=MAIN_033_TEXT G=MAIN_03 M=th04/kstack.cpp ACBP=28`
- normalized OMF SHA-256: `e016808a3a35f31c9efaa9487193fff0e8cfa30ece114bb712daa2a27cd1fbf4`
- raw OMF SHA-256: `b1e95fc4269e64372117b8f4d9e5b1e63bc4af49ef6536f137c2dac22c44bc62`
- A/B candidate MAIN SHA-256: `7aa8c37e63990386c434fddf1120d919004378c0d1ff7fa71d26b68f9e539d8f`
- receipt SHA-256: `9599245c5747b7ab8ef14b1a91be8a7a21e9e3a652a21dcf445b1936cb55674b`

Aggregate `gptweb-v127-kurumi-bullet-stacks-aggregate-001`:

- `pass=true`, `failures=[]`
- 163 default owners, two cold builds
- no prior owner regression
- A/B candidate MAIN SHA-256: `ffbf3b6c13670b338e53af3fb6020ff1d62bea2c0c903479fc45ba5975a23918`
- receipt SHA-256: `ece3fc789eae1632573d6f0f2d1b27ffccc5ad6a9623b23849b7a11a42667034`

## Function review

The ordinary complete-body gate accepts the new function without manual
boundary override. The fresh reviewer reports:

- 286 / 288 exact functions = `99.305556%`
- automatic = 142
- manual = 144
- reviewed nonexact = 2
- strict rejections = 0
- report SHA-256: `c09481b68fc486998c6d4cc9fac8924da64a9a977e3dc32a3dc14cc68449b890`

## Next boundary: `kurumi_update()`

The same packet corrects the physical owner of the immediately following FAR
dispatcher without granting source or exactness credit.

Ghidra reports entry `0x2915D`, max `0x2A71F`, but only 41 body addresses.
Pinned TASM and raw bytes instead prove:

- code `0x1915D..0x195C2`, `0x466 / 1126` bytes, ending in `RETF`
- one alignment byte at `0x195C3`
- three near-jump tables with 4, 5, and 7 entries at `0x195C4..0x195E3`
- next true PROC `orange_195E4` at `0x195E4`
- full compiler owner `0x1915D..0x195E3`, `0x487 / 1159` bytes
- owner SHA-256: `ee4c76d8aa70d2665ffd07d22f7bf0976e49e05e3fee34afa4df7e5a64d56451`
- relocations: `0x19212`, `0x19233`, `0x1925F`, `0x19457`, `0x19591`

The boundary ledger is upgraded only to corroborated. The dispatcher remains
`authored / reconstruct / unreviewed` and receives zero source/exactness credit.

## Verification planes

v127 establishes repository exactness only for the bounded 259-byte natural
owner. It does not establish standalone TH04 production build closure,
runtime-storage identity, deterministic runtime scenario validation, whole-image
identity, or project completion. v127 has not been submitted to Factory Truth
Kernel acceptance here.
