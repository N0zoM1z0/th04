# TH04 MAINE SND_LOAD artifact-local hybrid closure (v829)

v829 promotes MAINE `SND_LOAD` at payload `0xD112..0xD1FB` (234 bytes).

The source is the maintained shared loader already accepted in OP v828, but
MAINE exactness is proved independently. Two isolated TC4.02/TLINK MAINE
rounds reproduce the exact 234-byte body, preserve the `th04/snd_load.cpp` MAP
owner, and keep all 559 ordered MZ relocations target-equal. Relative to the
natural v489 MAINE baseline, only payload `0xD1D3..0xD1D4` changes from
`8B D8` to target `89 C3`.

The sole symbolic primitive reuses the accepted v394 TH04/TH05
`dialog_face_unput_8` register-direction precedent. OP exactness is not
borrowed.

Focused SHA-256:
`673dd33c725a40d9857c4c4bb4975079dd8905b12068b75f761a8530620419af`

Canonical SHA-256:
`1acb6e013468f46742ec8bc3c12f3fae5c6893ab0044683beb5d69c08d9ce62b`

Canonical replay checks 64/64 current MAINE accepted slices raw-zero.
Packed-file and whole-`MAINE.EXE` exactness are not claimed.
