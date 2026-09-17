# MAIN dialog and stage session `-B` producer diagnostic (v236–v237)

The pinned MAIN.EXE target is SHA-256
`077440a3c4e9ab52e72e9bae411276c47edc11995b5c2b83dfc83fbc039dc58b`
and remains `candidate-local-attested`. Target identity, MZ checks, and the
MAIN Ghidra database passed this session's preflight. The comparison inputs
are the exact-source v213 `dialog.cpp` and v214 `sess.cpp` cold replay snapshots,
whose ordinary TCC objects already link to raw-matching target extents but
have the wrong ordered MZ relocations.

The v234 BGIMAGE experiment showed that TCC `-B` generated ASM assembled by
pinned TASM32 can alter FIXUPP order while retaining code bytes for one small
contribution. This bounded probe tests that mechanism on the two MAIN owners.
In each isolated snapshot, TCC 4.02 used the production flags plus `-B`.
It emitted ASM but failed its automatic `tasm.exe` invocation. Unmodified
manual TASM32 5.0 also failed: generated ASM lacked group segment declarations;
dialog additionally contained a truncated external call name. A **diagnostic
copy only** of the generated ASM received empty group segment declarations;
the dialog call was repaired to its declared full far symbol. These modified
ASM objects cannot be accepted as reconstructed product source.

| Owner and source snapshot | Ordinary cold object CODE | Diagnostic `-B`/TASM CODE | Result |
| --- | --- | --- | --- |
| MAIN.EXE DIALOG_TEXT `0AAF:244D`, load `0xCF3D..0xD728`, file `0xE73D..0xEF28`; v213 | 2028 bytes, LEDATA 1020/1008, object SHA-256 `15bf3a323b07d735ec0abae6b5c1bc48992038d83f6a4f5044853f28d0fc4e7c` | 2029 bytes, LEDATA 1004/1006/19, object SHA-256 `1d4525dd36c04610ac4ac764b3a3f5a902cb60d5b749a62ef447917d9301cee4` | 1753 bytes differ over the common prefix; physical extent changes |
| MAIN.EXE DEMO_TEXT `0AAF:03E0`, load `0xAED0..0xB3ED`, file `0xC6D0..0xCBED`; v214 | 1310 bytes, LEDATA 1024/286, object SHA-256 `3816b5f0aaabe5e8646243d22fbe13d40e97f53f012a398ae95ec76ae426f6ad` | 1306 bytes, LEDATA 1005/301, object SHA-256 `c7dcc286bd0dfa48c995799b5a4034a3110869e6b28f0850147314330f7e0f86` | Physical extent changes |

The valid diagnostic OMF objects fail the prerequisite raw CODE size and byte
gate. No linker or packed-file run is needed to reject this producer for these
source snapshots; no exact unit or function credit changes. The original
target OMF and its actual FIXUPP grouping remain unknown. Receipts and
generated ASM/objects are under `.analysis/reconstruction/probes/`:
`v236-main-B-diagnostic/receipt.json` SHA-256
`b6068e890f3907f6348c27bfdf091857b6ce943c8740ec02d71306c9aa203dd7`
and `v237-dialog-B/receipt.json` SHA-256
`9b226745470b9bc1de24afed2b23f71c7a28b17b4e20e1f7b6b53d873305db22`.

The first v236 dialog trial accidentally used v214's unrelated dialog source
snapshot. Its result was excluded; v237 re-ran dialog against the correct v213
source. The temporary 51 MB replay clones were removed after retaining the
reproducible generated ASM, OMF objects, logs, and receipts.
