# MAIN gather-point renderer v326

The pinned Japanese `MAIN.EXE` (SHA-256
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`)
contains a 90-byte near renderer at B4M_UPDATE_TEXT `13A9:1008..1061`, MZ
load `0x14A98..0x14AF1`, file `0x16298..0x162F1`. Its target slice SHA-256 is
`a435b2f6443e99048b73017bdab8a374337ca524dc65a72640879889a8dae9af`.
The target remains `candidate-local-attested` rather than independently proved
pristine.

Target-bound Ghidra reports one contiguous body and one caller. Target raw
decode ends in `RET` at the final byte; the next B4M owner begins immediately
at load `0x14AF2`. The v151 MAP and TASM listing identify the near public, and
no MZ relocation overlaps the 90-byte extent. The body computes a PC-98 VRAM
offset, selects shifted `MOVSW` or byte-aligned `MOVSB`, and rolls at the
400-row boundary. Its two `LOOP` instructions and direct DS:SI to ES:DI string
copies are low-level hardware code; the earlier pinned TC4J control in
`TH04_MAIN_DIALOG_RENDER_V182.md` showed ordinary loops do not emit `LOOP`.
These observations justify an original-style assembly owner, without claiming
to possess the historical source file or proving that its author used TASM.

Maintained symbolic source is `src/main/gather/point_render.asm`, SHA-256
`d4e79c0ded8e3e6cbe22f1c44a775d206bc8b3b330fb95a91d0f4fb59a0533c4`.
The `EVEN` directive at relative offset `0x3B` aligns the shifted-copy loop
to offset `0x1044` and emits the observed `90` byte at `0x1043`. All other
operands use named dimensions and an external `_sPELLET` symbol; the source
contains no target byte array or code-byte directives. The old v151 wrapper
was only a zero-credit replay dependency and is removed from the active build.

`python3 scripts/replay_th04_main_exact_units.py --unit
th04-main-gather-point-render-asm-v326 --run-id
gpt-5-6-sol-v326-gather-focused-002` compiles the local source in two isolated
cold builds. Both produce valid deterministic TASM 5.0 OMF, SHA-256
`26fa9e9b5c29aaf16029f40c1ce007e3b95d92e3d6cecaa2c4af1bb11cfa253a`,
with only `th04\\b4mgath.asm` in the OMF dependency list. Both linked images
place it at `13A9:1008` with size `005A`; MAP SHA-256 is
`cadd4cdeff9416e254e78978e9b6b93aeb64e0f6c35bb9d0d77e2e2048bd5edc`.
The complete raw slice and empty ordered relocation overlap match the target.
Focused receipt SHA-256 is
`1f2dbe03b42cafd9b78c47ac391282cba067fd8fb71a87d36dc0f0da637ab3ee`.
An earlier diagnostic run with ID `...focused-001` was a false positive because
the v151 build insertion overwrote the local overlay with the old wrapper;
its result carries no source or exactness credit.

The candidate-state no-unit aggregate run
`gpt-5-6-sol-v326-gather-aggregate-candidate-001` passes all 249 default
MAIN owners twice, `failures=[]`, and retains the same OMF and slice identities.
Receipt SHA-256 is
`76b1f7254b46ce33c025527e1954130a552eed4d1a8cd9489a162836bb1d3766`.
Final post-promotion aggregate evidence is recorded in `config/evidence.csv`.
This adds 90 exact bytes to the separate original-style ASM plane; it does not
change the authored C/C++ percentage or establish whole MAIN equality,
standalone TH04 link closure, or playable DOSBox execution.
