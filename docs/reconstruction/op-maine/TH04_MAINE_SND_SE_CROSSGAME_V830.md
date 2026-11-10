# TH04 MAINE shared-sound artifact-local closure (v830)

v830 promotes MAINE `SND_SE_PLAY` (57 bytes at `0xD5A0`) and
`_snd_se_update` (76 bytes at `0xD5DA`).

The functions occupy one `0x86` `th04/snd_se.cpp` SHARED producer with a
single layout NOP between them. The maintained v827 source policy is reused,
but MAINE exactness is proved by MAINE-local cold replay.

Two isolated TC4.02/TLINK rounds reproduce the complete 134-byte producer,
both reviewed function bodies, the retained MAINE EXE/MAP identity, all 559
ordered MZ relocations, and the same 20 ordered OMF fixup operands.

Focused SHA-256:
`85a4d4f0f4c85652033b129d70088d5fedd074c719cc91226793dd23bb829dc8`

Canonical SHA-256:
`e570bcf46c3e4c1f6d9f5856bfb8536ffb7d3c49abf49eb85cf17fdb31c6d5d8`

Canonical replay checks 66/66 current MAINE accepted slices raw-zero.
Packed-file ownership, literal original-source spelling, and whole-`MAINE.EXE`
exactness remain separate claims.
