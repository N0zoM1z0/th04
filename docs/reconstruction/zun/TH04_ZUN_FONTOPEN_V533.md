# ZUN DOS_ROPEN / FONTFILE_OPEN library replacement (v533)

This packet replaces the external MASTER fontopen member with maintained
symbolic TASM source. The member owns both code and data; all of it is
library support rather than authored ZUN exactness.

## Physical owner

The decoded target code at payload 0x136C..0x1383 is exactly 0x18 / 24 bytes,
SHA-256
3442d8129f35ad11432cf42da08320cff50c6473a4540457f82a2e43f8a188dd.
DOS_ROPEN and FONTFILE_OPEN are public aliases of the same entry. The success
and FileNotFound paths both end in RET 2, with no trailing code padding.

The same archive member contributes file_sharingmode at target decoded _DATA
payload 0x2212..0x2213. It is a zero word, SHA-256
96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7.
The historical MASTER source kept this word in a separate data fragment, but
the linker MAP and extracted archive member assign code and data to one
physical fontopen owner.

## Maintained source and OMF

src/shared/dos/dos_ropen.asm emits both sections in one maintained TU. Two
isolated TASM32 5.0 rounds emit deterministic two-byte DATA and 24-byte CODE.
The unlinked CODE has SHA-256
292d9f139fa2d096f2606edff3d59228025c42a5da34e17db638a512ef318f51
because its file_sharingmode address remains a FIXUPP placeholder; the DATA
already equals target. Link-relevant OMF SHA-256 is
7468e2b53697ba2426ba9c394e79510246da348935d80c95f49f024031900ac9.
The extracted historical member has identical CODE/DATA LEDATA. Final linked
raw bytes remain the acceptance gate.

## Cold replay

Run:

    python3 scripts/probes/replay_th04_zun_fontopen.py       --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME

The replay preserves all earlier localized support and replaces fontopen at
zero-based MASTER archive position 337. The accepted v533 receipt is
.analysis/reconstruction/probes/v533-zun-fontopen-001/receipt.json,
SHA-256
f5ead877075464861fc5c5f9226efa8de397c1bb7193879a61d2c0ca9d34b567.

Both cold rounds retain candidate MAP SHA-256
9798e11f400727f4c5b2a0e22d9fd72f5d202f48eb79ffb4b24f68e3bbb07053
and 6360-byte resident component SHA-256
a15ee1e7eac9616e9cd60656a00fb5700c7e20299efc2c0ab44bce6c27cf1dab.
Both linked CODE and DATA are raw-equal to target. The resident target
residual remains 4241 bytes.

## Acceptance boundary

units.csv records one 24-byte code support unit and one two-byte data support
unit sharing the same maintained TU. Neither changes authored ZUN exactness.

The next coherent support packet is the pure-data VERSION/GRP members; keeping
those separate avoids mixing data ownership with this code-bearing member.
