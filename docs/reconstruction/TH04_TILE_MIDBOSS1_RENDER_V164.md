# TH04 TILE Stage 1 midboss renderer reconstruction (v164)

## Scope

This packet closes `midboss1_render()` in `th04-main / MAIN.EXE / TILE_TEXT` at `0AAF:1C88..1D94`, load `0xC778..0xC884`, target file `0xDF78..0xE084`, size `0x10D / 269`, target slice SHA-256 `f746590b8e7f3b70527c3be7413062c34cd6be5076d8f09e3266e1ea1f91350a`. The next target byte starts the independently exact v163 Stage 3 renderer at load `0xC885`.

Fresh target-bound Ghidra constructs one contiguous 269-byte near body. Pinned TASM/MAP and gap-free raw decoding agree on the same public/RET extent. The Stage 1 setup path installs this function through `midboss_render_func`, explaining why Ghidra reports no direct caller edge.

## Natural-source and physical-owner result

`src/main/midboss/m1_render.cpp` uses ordinary natural C++ only. A production-profile TC86 Borland C++ 4.02 probe emits exactly `0x10D` CODE bytes with `@MIDBOSS1_RENDER$QV` at object offset zero. Before linker fixup resolution, every non-fixup byte is already target-identical; the only unresolved differences are the 32 two-byte OMF fixup operand fields.

An ephemeral link probe inserts this object immediately before the exact v163 Stage 3 / Stage X objects. The complete linked 269-byte slice becomes target-identical with zero differences, and the ordered target/candidate relocation sequence is exactly `[0xC86E,0xC853,0xC821,0xC7E1,0xC7C7]`. The following Stage 3 and Stage X map starts remain `0AAF:1D95` and `0AAF:1E5A`. This supports one standalone Stage 1 physical C++ object rather than folding the renderer into a neighboring translation unit.

Focused A/B `m1r.obj` raw SHA-256 is `e474982f4915e3fd09cb0811d52290d0c985818d25c9093321d0cdd9353a4abf`; dependency-normalized SHA-256 is `993b62d774019a2af3b67827a5e1ef27ecd57555509c4ff5303bad4c31df7368`.

## Exactness Oracles actually run

Focused `gptweb-v164-midboss1-render-focused-candidate-002` selects a 118-owner dependency closure and passes two isolated cold builds with `failures=[]`; receipt SHA-256 is `abff4ed3298b042906db7c6419ae66111708270c7f7216c7888d2ff59ce7866f`. Both candidate MAIN images are SHA-256 `92cad9d97a2424564d6615db5a91a649f48fefea7f0f97af73e8a5bb2ef99a32`.

Candidate-state aggregate `gptweb-v164-midboss1-render-aggregate-candidate-001` passes all 197 default owners twice with `failures=[]`; receipt SHA-256 is `6e34fb2e09906ed188a6fd5aef74c8b4053f1ba4984960d5795018508c0523f9`. Post-promotion aggregate `gptweb-v164-midboss1-render-aggregate-final-001` passes the same 197-owner cohort twice again; receipt SHA-256 is `71d36675154a8824ee7a87fd3dab3e2a727795380f2fcb8bd70f3b4fe55a023d`. Both aggregate runs produce deterministic candidate MAIN SHA-256 `2f984f3b7852be26c624ab6db56afe99fde4fa56fd183cdd04374c4c9ce23b2e`.

The fail-closed authored-function reviewer admits exactly one new row for `midboss1_render()` after explicit `[[new_exact]]` policy. Historical ledger rows are preserved rather than accepting unrelated reviewer note normalization.

## Factory acceptance and verification-plane boundaries

After the clean implementation checkpoint `701792a773ec8488b75a308969d7716d901abcea`, Factory replay job `job:4315bb55902049368e62032e0d8ecd8a` independently replayed the imported `claim:unit:th04-main-midboss1-render-v164:owned-extent-exact` claim. It completed with receipt `receipt:002bee2a9dd16f2030c7930588899c280493ca53be42d1aa0bfdf9d4181c1093`, `receipt_verdict=pass`, `acceptance_decision=accepted`, no rejection reasons, and registry entry `registry:a77c077f11ebbcb77ad7b34fe57c41411545e3a4f82ef6d40333d5a3b0336637`. The replay source binding is the clean implementation commit and tree `14c921ba0e9627338535cbf2cbe422f7580e8c8e` with no untracked files.

This Factory acceptance is scoped only to the v164 owned-extent exact claim. Repository-native and Factory-controlled exactness are therefore both established for the Stage 1 renderer and its standalone TC4J object. Standalone TH04 production compile/link closure remains unestablished, runtime-storage identity remains unestablished, no runtime scenario was executed, whole-image exactness is unestablished, and independent pristine-release provenance is unestablished. The private target remains only `candidate-local-attested`.
