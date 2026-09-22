# ZUN FILE_WRITE library replacement (v529)

This packet replaces the external MASTER filwrite member in the ZUN resident
diagnostic link with maintained symbolic TASM source. It is library support,
not authored ZUN exactness.

## Target-first function extent

The target FILE_WRITE entry is decoded payload 0x11AA. A complete instruction
walk closes at RET 6 at the end of payload 0x124F, for a 0xA6 / 166-byte
function and module. SHA-256:
aedf0cf1cbc8b4a9a2ca24475d02b761019148143de91f412e1274fa6167ae71.

This matters because the older Ghidra inventory exposed a noncontiguous 0xA5
body inside a 0xA6 span. Target-first disassembly shows that all 0xA6 bytes are
function-owned. The 0x90 at candidate runtime 0x7B1 is not trailing padding:
it is the historical EVEN between the buffered success path and the direct DOS
write path, and execution can branch immediately past it to 0x7B2.

There is no function-external byte at the module tail.

## Maintained source and OMF

src/shared/dos/file_write.asm keeps the historical near Pascal far-buffer ABI,
MASTER file-buffer globals in _DATA/DGROUP, the buffered copy/flush loop, and
the direct INT 21h/AH=40h path.

Two isolated TASM32 5.0 rounds emit deterministic 0xA6 LEDATA with SHA-256
b0b3dee01db46e8000b8b335e32f6270a9940a067a75c700a833775e89433c90
and deterministic link-relevant OMF SHA-256
b73370867ca98773148bba4b0d333669cde6e61107705fbd88c3bc70e693ac5a.
The extracted historical filwrite member has identical zero-placeholder
LEDATA. Raw object identity is not the acceptance gate; final linked bytes are.

## Cold replay

Run:

    python3 scripts/probes/replay_th04_zun_file_write.py       --output-dir .analysis/reconstruction/probes/NEW-UNIQUE-NAME

The replay keeps all previously localized support members and replaces
filwrite at zero-based MASTER archive position 171. The accepted receipt is
.analysis/reconstruction/probes/v529-zun-file-write-001/receipt.json,
SHA-256
dc24e1cc712486546dedd2f56334b38ccd48e13b8a36a8e1636410f068770f84.

Both cold rounds retain the historical resident candidate MAP SHA-256
9798e11f400727f4c5b2a0e22d9fd72f5d202f48eb79ffb4b24f68e3bbb07053
and 6360-byte component SHA-256
a15ee1e7eac9616e9cd60656a00fb5700c7e20299efc2c0ab44bce6c27cf1dab.
The linked FILE_WRITE extent is raw-equal to target. The full resident target
residual remains 4241 bytes.

## Acceptance boundary

units.csv records all 0xA6 FILE_WRITE bytes as reviewed, library-origin,
source-present support. This does not change authored ZUN exactness.

Continue the file-helper family with FILE_SEEK, FILE_APPEND, and FILE_CLOSE
under the same physical archive, OMF, MAP, and raw-linked gates.
