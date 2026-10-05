# TH04 PAR archive fixtures and native state owner

2026-09-27 product-build investigation. The pinned HDI has two game archive
files under `GENSO/`: the OP/ending container is 1,120,284 bytes with 132
members, and the main-game container is 1,053,177 bytes with 158 members.
Their SHA-256 values and raw FAT short names are pinned in
`scripts/probes/probe_th04_pf_archive.py`. This is a local HDI observation;
the HDI still has `candidate-local-attested` provenance.

The 16-byte PAR header contains a directory byte length, member count, and
initial directory key. Its encrypted directory has one 32-byte terminal
record after the declared member count. For each directory byte, the decoder
XORs the current key and subtracts the resulting plain byte from the key.
Each member record stores type, auxiliary XOR key, 13-byte name, packed and
declared original sizes, and 32-bit payload offset. Observed types are
`0xF388` (stored) and `0x9595` (repeated-byte encoding). The historical
PFGETC source corroborates that two equal literal bytes are followed by a
count of *additional* copies. Its optional nibble rotation is commented out
for this game; the auxiliary key applies only an XOR to payload bytes.

The checked-in host probe verifies the pinned HDI hash, FAT geometry and both
mirrors, both archive hashes, directory terminators, all 290 member offsets,
every decoded length, and PI/BFNT magic. It writes four selected fixtures only
under a fresh private `.analysis/reconstruction/probes/` directory. The v3
receipt SHA-256 is
`a3200ed18a538f52a1453f33dd1c5e8d69536ce57ce6f392b20f30fa740c8039`.
The ending archive has 42 PI and 9 BFNT members; the main archive has 13
BFNT members. Private fixtures include `GAMEFT.BFT`, an uncompressed
`CONG10.PI`, a packed `CONG14.PI`, and `ST00.BFT`. Use the receipt's content
hashes to bind a future DOS/PC-98 differential test without checking game
assets into Git. Re-run with a fresh `--output-dir` and repeatable
`--extract op_end:NAME` or `--extract main:NAME` options for other fixtures.

Five complete repeated-byte expansions exceed their directory's declared
logical size by exactly one byte: ending `SCNUM2.BFT`, and main `ST00.BFT`,
`EYE1.CDG`, `EYE4.CDG`, `MIKO.EFC`. The probe reports and pins those cases;
it writes only the declared logical extent for fixtures. A future native
file-hook test must establish how TH04's DOS reads and seeks handle these
members. Do not silently change the declared sizes or treat the extra byte
as proof of corrupt media.

`src/shared/formats/pf_state.asm` owns the TH04-local `bbufsiz`, `pferrno`,
and `pfkey` storage and C/Pascal public aliases. The default buffer size is
512 bytes; `game_init_main()` sets it to 4096 and `game_init_op()` to 8192
before calling `pfstart()`. This data owner does not implement PAR opening or
the DOS INT 21h hook. Two cold no-archive MAINE builds compile 123 TH04 units
(79 C++, 44 ASM), leave 10 unresolved names, and report zero warnings.
The comparator finds equal link-relevant and timestamp-normalized OMF
records; only BGIMAGE has its known raw timestamp drift. The A/B receipt
SHA-256 values are
`95bb7a7aba3f992c0bfa8eab9fda6a0ca0e68713a133ca56cf35b228a7c441bf`
and `5fdd6401e51d9c260208437eaff18828e986bdf353551b6d072ba39d93c36b8b`.
The source manifest digest is
`e69c011ea3bd6748c09df3e264951e449212bcb60aa02b8d6be3f4421c77a68d`.

The historical-library calibration TLINK exits 0 with the known archive
dictionary warning (receipt
`22f204c4be6da2c9e7fc111d208d4e2236b1e7038aadf8b97470fdfafadf85de`).
Its MZ passes 614 relocation sites at two DOS load segments (receipt
`a5388877a411080123247417311b12b84479d43edaead30f56b504f1fea112ca`),
and the far-call audit checks 33 returns, 124 relocated direct calls, and
one same-CS call (receipt
`1fababaf022f9af428ba1c2004b85ed49d973502ad7699c5e7fe281b2b892de8`).
Calibration MAP `0E57:0424` contains both `bbufsiz` and `_bbufsiz`; the
corresponding load-module word is `0x0200`. `_pferrno` and `_pfkey` follow at
`0E57:0426` and `0E57:0428`, initialized to zero. These are calibration
addresses, not target addresses. No independent TH04 product or PC-98
runtime claim follows from either the host archive probe or this data-only
owner.

## TH04-local DOS service

`src/shared/formats/pf_archive.cpp` and `pf_int21.asm` now own `PFSTART`,
`PFEND`, and the resident INT 21h entry. The assembly unit preserves a
24-byte register/flags frame, loads the TH04 data group before its far Pascal
callback, and forwards unrelated DOS calls to the saved vector. The C++ unit
decrypts the PAR directory, exposes a single read-only archive member as a
DOS handle, and decodes payload bytes through the configured `bbufsiz`
buffer. The read cursor can reach an extra expanded byte, while seek-from-end
uses the directory's declared size. The handler restores the vector on
`pfend()` and before forwarding process termination. These are semantic
owners, not exact target-byte claims.

The checked-in `scripts/probes/probe_th04_native_pf_hook_runtime.py` builds
those units with TC4J/TASM/TLINK and runs a DOS program against private copies
of both pinned real archives. It checks compressed and stored members,
auxiliary XOR, loose-file forwarding, buffered reads, seek backwards/end,
all five one-byte expansion cases, and vector restoration after `pfend()`.
The nine-member version passed under pinned MS-DOS Player. Its test MZ has
269 unique nonoverlapping relocation sites and passes relocation checks at
DOS load segments `0x2000` and `0x6000` (receipt SHA-256
`8f8306e50f6a15d7ff8f55970f30f8dc477325150984881e5636e46c3c5f3880`).
The service's one-active-virtual-handle policy and PC-98 game integration
remain open. The test MZ proves DOS behavior only; it does not prove MAINE
reaches a displayed frame.

Two cold no-archive MAINE builds compile 125 TH04-owned units (80 C++, 45
ASM) and reduce TLINK's frontier to eight names without warnings. The
comparator finds all 125 link-relevant and timestamp-normalized OMF records
equal; only BGIMAGE has its prior raw timestamp drift. The A/B receipt
SHA-256 values are
`58aae0ca863032d63aac25f93825d1c310f28991394cc3b1e587c37e1e456c77`
and `f0f82f2b18ff4b25a3f43aa1a0349929047911a65352d66e13f8551e0e5091e9`;
the source manifest digest is
`08c6c7027c4b2576466719e1065bff9b792aa514a5089362d16d4ea710b4500e`.
`PFSTART` and `PFEND` no longer need the historical archive in that link.
The mixed-support calibration TLINK exits 0 with the known extended-dictionary
warning (receipt SHA-256
`52e257047349af5c97be021c6cd6c5a54a80048f47221d79c33bd6d9e5bb4909`).
Its MAP locates TH04-local `PF_DISPATCH` at `0887:316B`, `PFEND` at
`0887:33F6`, `PFSTART` at `0887:342D`, `PF_HOOK_INSTALL` at `0887:482C`,
and `PF_HOOK_REMOVE` at `0887:4859`. These are calibration addresses, not
target offsets. The MZ auditor checks 631 relocation sites at load segments
`0x2000` and `0x6000` (receipt SHA-256
`3dde114975581a09cee81fe0be08c535cb679d79e5cf7517f6cb9d297fe0af58`).
The call-ABI auditor checks 33 far returns, 128 relocated direct far calls,
and one same-CS call (receipt SHA-256
`0ddc34ad73fb0c86fd1ce12cffc6f3ecde58840b5aa4161e1997983cd3a9f67b`).
This is structural evidence for the mixed-support MZ, not a standalone
TH04 product or a PC-98 runtime acceptance.

Replay commands from a clean worktree, using new private output directories:

```text
python3 scripts/probes/probe_th04_native_pf_hook_runtime.py --output-dir .analysis/reconstruction/probes/NEW-runtime
python3 scripts/probes/probe_th04_native_maine_link.py --without-support --output-dir .analysis/reconstruction/probes/NEW-a
python3 scripts/probes/probe_th04_native_maine_link.py --without-support --output-dir .analysis/reconstruction/probes/NEW-b
python3 scripts/probes/compare_th04_native_maine_link.py .analysis/reconstruction/probes/NEW-a .analysis/reconstruction/probes/NEW-b
python3 scripts/probes/probe_th04_native_maine_link.py --output-dir .analysis/reconstruction/probes/NEW-lib
python3 scripts/probes/audit_th04_native_maine_mz.py --link-receipt .analysis/reconstruction/probes/NEW-lib/receipt.json --output-dir .analysis/reconstruction/probes/NEW-mz
python3 scripts/probes/audit_th04_native_maine_call_abi.py --link-receipt .analysis/reconstruction/probes/NEW-lib/receipt.json --output-dir .analysis/reconstruction/probes/NEW-call
```

Two TC4J constraints surfaced during implementation. A translation unit whose
long basename is rewritten to DOS 8.3 cannot reliably resolve `../runtime`
from the rewritten path; use a repository-root include under the existing
`-I.` flag. `_dos_open()` takes `int *` for its output handle under this
toolchain, even when the stored handle is later an unsigned DOS word. These
constraints are worth preserving for TH05's first native build.

## Semantic readability and regression, v1226

`semantic/readable` renames the private member stream and its fields without
changing their types/order, and names directory offsets and intercepted DOS
functions. Source comments explain encoded bytes fetched versus buffered bytes
consumed versus decoded bytes delivered, repeat counts after two equal
literals, the saved AX/carry frame, recursive DOS forwarding, rewind/discard
seek behavior and teardown ownership. Keep the unsigned-16 narrowing before
the seek-discard clamp; seeking directly to 65536 remains an untested boundary
hazard, rather than a correction authorized by this readability batch.

The preceding source build `product-20261003-032057-0eb9ceea` and readable
build `product-20261003-032654-4e1e8830` use dependency-validated object caches.
The latter reuses 191 MAIN C++ objects, 158 OP objects and 132 MAINE objects;
changed inputs rebuild. All three complete MZ files, headers, program images
and ordered relocation tables have zero differences:

| Product | Bytes | Relocations | Complete file SHA-256 |
| --- | ---: | ---: | --- |
| MAIN | 192351 | 1178 | `dbbfa404292022e47142c4c14951f24b1bf2017ab4d2168b4b7464871a4fc615` |
| OP | 77740 | 814 | `c8ac4d73ea0deee10a2d26665cfe1e5a043e69c2e9b16ebac1dbb4521acaf357` |
| MAINE | 70614 | 660 | `0a2d3ce89e7663265b4c498a66b78225e14ea75af9a59a40066928ea6d18afba` |

These are compiler-observed source-to-source results, not original-target
exactness. Replay with `scripts/build.py --only main op maine --progress`,
using the preceding run's `--main-cpp-cache`, `--op-cache`, `--maine-cache`
receipts, then `scripts/compare_artifacts.py BEFORE.EXE AFTER.EXE --json`
for each product. Private manifests are under
`.analysis/build/semantic-resource-{baseline,readable}/build.json`.

The fresh nine-member DOS probe passes compressed/stored/XOR resources,
loose-file forwarding, buffered reads, backward/end seek, all five extra-byte
expansion cases and interrupt-vector restoration. Receipt:
`.analysis/reconstruction/probes/semantic-pf-runtime-20261003/receipt.json`;
MZ SHA-256 `200f139cfe83d142efac18e33b86657c2541dd99c7eed2aae2e3bf540fa50268`,
272 relocation sites checked at load segments 0x2000 and 0x6000. Runtime
coverage remains a bounded DOS service check; full Good Ending rendering is
still failing in the latest user playtest.
