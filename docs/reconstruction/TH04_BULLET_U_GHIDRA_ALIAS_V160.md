# TH04 BULLET_U Ghidra near-call alias review (v160)

## Scope

This packet reviews the only three current `th04-main / MAIN.EXE` function-boundary rows that were simultaneously provisional reconstruction candidates, Ghidra-only observations, and missing both a TASM PROC and a TLINK public: load `0x1C99C`, `0x1C9DA`, and `0x1CA2E` in `BULLET_U_TEXT`. The private target remains `candidate-local-attested`; this review does not establish independent pristine-release provenance.

All three addresses lie inside the already reviewed and exact natural-C++ `bullets_update()` owner at `BULLET_U_TEXT 13A9:8E38..91A2`, load `0x1C8C8..0x1CC32`. v160 changes function-boundary classification only. It does not change source, byte ownership, or any exact verdict.

## Synthetic-segment near-call aliases

`bullets_render()` is linked in `MAIN_01`, with its exact contribution beginning at `0AAF:81F5`. Its target bytes contain near calls at load `0x12DB1` and `0x12DB9`. Pinned TASM records these as calls to `main_01:_pellets_render_top` and `main_01:_pellets_render_bottom`. The exact MAP places the true publics at `0AAF:1EAC` and `0AAF:1F3E`, which are load `0xC99C` and `0xCA2E`. Target bytes at those loads are the real pellet renderer entries.

The Ghidra import instead represents the caller in a synthetic `0x2000:` segment. Applying the signed near-call displacement to that synthetic offset yields `0x2000:C99C` and `0x2000:CA2E`, rendered as image `0x2C99C` and `0x2CA2E`. Those image addresses correspond to unrelated load `0x1C99C` and `0x1CA2E` inside `bullets_update()`. This is a load-segment interpretation error, not evidence for duplicate functions.

For the top call, target `MAIN_01` arithmetic is `0AAF:82C1` with next IP `0AAF:82C4` plus signed displacement `-0x6418`, giving `0AAF:1EAC` / load `0xC99C`. For the bottom call, `0AAF:82C9` with next IP `0AAF:82CC` plus signed displacement `-0x638E` gives `0AAF:1F3E` / load `0xCA2E`.

## Internal BULLET_U control flow

The bytes at the aliased addresses independently disprove function starts. Load `0x1C99C` is reached from `bullets_update()` by the target conditional branch at `0x1C97A`, has no independent prologue or return, and joins the shared loop tail. Load `0x1CA2E` is ordinary fall-through immediately after the `PlayfieldMotion::update_seg3()` call at `0x1CA2B`; it likewise continues through the shared loop and terminal `RETF`.

The middle Ghidra entry at load `0x1C9DA` is not an alias from `bullets_render()`, but it is still an internal block. Target load `0x1C968` conditionally branches there, and load `0x1C974` contains `EB 64`, an unconditional `JMP`. Ghidra reports that latter xref as `UNCONDITIONAL_CALL`, which is directly contradicted by the target opcode. The block falls through into load `0x1CA2E` and has no independent return.

## Ledger consequence

The three Ghidra entries are excluded as authored function starts. Their bytes remain authored and remain owned by the exact `bullets_update()` natural-C++ unit; exclusion removes only false function-boundary candidates. The true pellet renderer rows at loads `0xC99C` and `0xCA2E` remain separate unreviewed authored candidates in `TILE_TEXT` and receive no v160 exactness claim.

A mechanical audit after this correction finds zero remaining MAIN rows with the exact high-risk signature `boundary_state=provisional`, `work_queue=reconstruct`, `observation=ghidra`, and no TASM PROC or TLINK public. This does not prove the broader function inventory complete; sparse/cross-linked, no-Ghidra, TASM-only, table/shared-tail, and other boundary classes remain open.

## Verification-plane boundaries

v160 establishes a target-first boundary exclusion only. It does not run or require an exact-unit cold replay because no source or exact owner changes. Existing `bullets_update()` exactness is not re-promoted here. Standalone TH04 production closure, runtime-storage identity, runtime-scenario validation, independent pristine provenance, and Factory acceptance remain separate and unestablished by this packet.
