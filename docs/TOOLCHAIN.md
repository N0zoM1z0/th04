# Borland toolchain acquisition, installation, and use

This document reproduces the exact **local candidate** used for TH01-TH05
calibration on 2026-09-06.  The proprietary binaries and downloaded media stay
below ignored `.analysis/`; they are never committed or redistributed.
You are responsible for obtaining and using every third-party component under
rights that apply to you.  A URL here records provenance and reproducibility;
it is not a legal endorsement or a claim that the host is authoritative.

## What is pinned

`config/toolchain.toml` is the machine-readable authority. It includes 16
configured surfaces: 14 required portable tool surfaces and two optional host
Wine observations. It also records expected tree/file hashes, file counts,
exact banners, source URLs, and OMF producer strings. Important acquisition
identities are:

| Surface | Identity |
| --- | --- |
| TC4J flat media, 61 files | SHA-256 `6e7e3c2734044bc799cbd4ad9645654bfd3a4f17ed29e3e2988c9dba1af350a` |
| TASM 5.0 archive | SHA-256 `94723cc2c882525dd561e4d35a9251b8fb992a0352c075ca5f97fff12bbc872f` |
| TASM 5.0 published archive digest | SHA-512 `0580f14adbb785e43ee3b057a5ec0417b3206b26fba4bda034140e7d6aa4947634dcbe167f337de2942fb4a3e3515e9eb829d6b666d31a64afe442111a070061` |
| Active `TCC.EXE` | SHA-256 `0c6a3a364ffd235e0c4b268d6925f29be3f20adafc6d1410c057a411e6634ff0` |
| Active `TLINK.EXE` | SHA-256 `e54f517766a3982dff404ff639b0f94e43c16e688dffb7e14b92df87a8580ad0` |
| Active `TASM32.EXE` | SHA-256 `ba50fe547863b96242d98cff54cdf95ab268a8682395afad172eedbfc46c5b26` |
| ReC98-bundled MS-DOS Player | SHA-256 `f7f6cb0a3e816c5edb13112d327c1bddbf7463fe7bf9a005ca1eb5317751bd02` |

Sources used by the bootstrapper:

- Turbo C++ 4.0J media index:
  `http://pc98.shiz.me/software/borland-4.0j/` (HTTP-only untrusted mirror,
  no independently published hash).
- TASM product and digest page:
  `https://winworldpc.com/product/turbo-assembler/5x` and
  `https://winworldpc.com/download/30487b55-c392-c592-11c3-a6c2bb2a5254`.
- TASM archive mirror URL used by the script:
  `https://winworldpc.com/download/30487b55-c392-c592-11c3-a6c2bb2a5254/from/c39ac2af-c381-c2bf-1b25-11c3a4e284a2`.
- MS-DOS Player comes only from pinned ReC98 revision
  `b6ba5b0a529edbb31efdf8c0e939263804f8ee47`.

If any source changes, **do not update a hash merely to make installation
pass**.  Quarantine the new bytes and establish a new evidence chain first.

## Host prerequisites

The tested host is Debian 12 x86-64, Python 3.11.2, and Debian packages
`wine`/`wine64` `8.0~repack-4`. Package names and host binary hashes may differ
on another x86-64 distribution; Wine is recorded and probed rather than used
as a cross-machine hard gate. Install:

```bash
sudo apt update
sudo apt install git python3 unar wine wine64 p7zip-full mtools curl wget \
  ca-certificates tar unzip
```

Clone the pinned reference repositories with the one-line command in the main
README before bootstrapping.  In particular, `_reference/ReC98/bin/msdos.exe`
must exist and match its pinned hash.

## Fresh automatic installation

From the repository root:

```bash
bash scripts/bootstrap_toolchain.sh
```

This exact command was also tested end-to-end from an empty local clone and an
empty private toolchain directory.  It independently downloaded both media
sets, reproduced all 16 pinned surfaces, and produced the same linked probe
EXE/map identities as the working checkout.

The script intentionally refuses to overlay an existing prefix, media tree, or
installation.  This fail-closed behavior prevents a partial prior download or
locally mutated library from being mistaken for the pinned environment.  Move
the existing `.analysis/toolchain/` aside if you intentionally want a wholly
fresh installation; keep it if it contains evidence you still need.

The bootstrapper performs these reproducible steps:

1. mirrors all TC4J installation files and validates the complete 61-file tree;
2. downloads TASM 5.0 and validates the publisher-listed SHA-512;
3. before executing or extracting downloaded code, validates the TC4J tree,
   TASM archive, and pinned MS-DOS Player and writes
   `.analysis/toolchain/acquisition-attestation.json`;
4. validates 7z container integrity and extracts the media;
5. creates an isolated project-local Wine prefix;
6. expands TC4J `.PAK` files with the pinned MS-DOS Player into `C:\TC4`;
7. extracts `TASM32.EXE` into `C:\TASM50\bin`;
8. preserves canonical unpacked copies below `.analysis/toolchain/installed`;
9. installs checked-in `TURBOC.CFG` and `TLINK.CFG` templates; and
10. runs the complete attestation and execution probe.

No downloaded binary is staged by Git.  Verify this with `git status --short`
after installation.

## Why the isolated short path matters

Running these Borland DPMI tools directly from the repository's deep Wine
`Z:` path reproducibly failed with `Loader error (0000)`.  The project-local
prefix and short DOS path `C:\TC4` avoid that loader failure and also make
compiler dependency records stable.

The compiler configuration filename is `TURBOC.CFG`, **not** `TCC.CFG`.
Using `TCC.CFG` allowed a cold build to start but made standard headers such as
`dos.h` unavailable.  The checked-in file pins:

```text
-IC:\TC4\INCLUDE
-LC:\TC4\LIB
```

`TLINK.CFG` separately pins `-LC:\TC4\LIB`.  Both files are hash-attested.

## Attest before every evidence-producing build

```bash
python3 scripts/attest_toolchain.py
```

Success requires every required surface to match, exact version banners,
two identical probe rounds, valid OMF checksums and module boundaries, expected
embedded producers (`TC86 Borland C++ 4.02` and
`Turbo Assembler  Version 5.0`), an observed dependency on the pinned `dos.h`,
an MZ-valid linked probe, and successful probe execution.  It writes the
private receipt `.analysis/toolchain/attestation.json` and returns nonzero on
any mismatch.

Required identity failure prevents Wine, MS-DOS Player, or any compiler probe
from running. The two host Wine file hashes in the manifest are informational
observations from the calibrated Debian machine; different hashes do not waive
the execution, cold-build, or exact-byte Oracles. To replay only the portable
pre-execution acquisition gate:

```bash
python3 scripts/attest_toolchain.py --identity-only \
  --surface tc40j-media --surface tasm50-archive \
  --surface msdos-player-p0281
```

For inspection of any additional object:

```bash
python3 scripts/inspect_omf.py path/to/module.obj
```

The OMF parser is intentionally strict about record length, checksum,
exactly one THEADR and one MODEND/MODEND32, trailing bytes, producer comments,
and dependency records. Concatenating two valid modules is rejected. OMF
validity proves container integrity, not source correctness.

### OMF raw and dependency-normalized identities

Borland COMENT class `E9` dependency records contain 16-bit DOS time and date
words followed by a counted filename.  This layout is independently confirmed
by Open Watcom's pinned primary
[`omf_coment_dep` definition](https://github.com/open-watcom/open-watcom-v2/blob/b36230f83e0ad7c40fc682f2d2c10bc034efcf23/bld/watcom/h/pcobj.h).
Consequently, identical compilation can produce raw-different objects when an
input's timestamp changes even if linked code is unchanged.

The comparison report preserves **both** identities.  Its narrowly normalized
digest zeros only those four E9 metadata bytes, recomputes each affected OMF
record checksum, then reparses the result.  It does not normalize paths,
producers, record order, fixups, data, code, or source-level `__DATE__` and
`__TIME__` strings in LEDATA.  In the two local builds, the 65 TH01 objects
have different raw set hashes but the same dependency-normalized set SHA-256:
`0ae28223b44f4bf295eaaafd713a99bf2c1e538515f3e5e49e6052a0c0159188`.
Across three local cold builds, each of the TH01-TH05 game object sets has a
stable dependency-normalized identity; the aggregate of those five identities
is `65b5c13ff471e6ef7c4f0cf6c62984197feb129cefc8617835a7991fad808152`.
The full 416-object normalized sets still differ because ReC98 research probes
deliberately embed build date/time strings.  That remaining difference is real
and is not hidden.  This two-digest design provides a fast routing signal while
keeping the raw evidence intact.

## Cold-build and compare all ReC98 PC-98 controls

Create a fresh immutable-source build directory (the run ID must be new):

```bash
python3 scripts/cold_build_rec98.py --run-id cold-local-001
```

The script first reruns full toolchain attestation, materializes the pinned
ReC98 commit with `git archive`, invokes its bundled Tup build through Wine,
and writes a private receipt containing source, command, environment, all 20
selected output hashes, their aggregate identity, and all five games' map and
response-file inventories.  It does not trust the checkout's working tree and
does not call the result exact.

Run the strict gate against the emitted `source` path:

```bash
python3 scripts/survey_rec98_outputs.py \
  .analysis/builds/rec98-b6ba5b0a52/cold-local-001/source
```

For the pinned current ReC98 commit, this command is expected to return 1:
17 files fail this project's whole-file policy and three COM files are exact.
The JSON includes sizes, formats, header fields, relocation counts/sets/site
values, program and overlay difference counts, raw/common extents, full
comparisons, and agent-routing hints.

Add `--compact` for routine agent triage.  It keeps all candidate identities,
numeric comparison dimensions, vector hashes, OMF checks, and gate behavior
while omitting the verbose bounded per-byte difference runs.  Omit it when a
full private comparison receipt is required.

To verify that a new machine reproduces the **known diagnostic vector** rather
than accidentally changing it:

```bash
python3 scripts/survey_rec98_outputs.py \
  .analysis/builds/rec98-b6ba5b0a52/cold-local-001/source \
  --gate calibration
```

Calibration mode returns 0 only when the source archive and cold receipt, all
20 candidate hashes and aggregate identity, complete compact comparison-vector
digests, all 416 valid OMF objects, and every per-game dependency-normalized
OMF identity reproduce `config/rec98_pc98_calibration.toml`.  A one-byte
candidate mutation was tested to fail both its artifact vector and aggregate
identity.  Calibration never changes or bypasses the strict exact gate.

For a smaller display of the TH01 upstream-policy differential, use
`scripts/compare_rec98_th01.py SOURCE`; its default raw gate also intentionally
returns 1, while `--gate calibration` checks the pinned TH01-only vector.

## Direct tool invocation for focused probes

Normally use the checked-in scripts so commands and receipts stay uniform.  If
a minimal compiler or linker hypothesis needs direct invocation, preserve the
same prefix and short paths:

```bash
th04_root=$PWD
export WINEPREFIX="$th04_root/.analysis/toolchain/wineprefix"
export WINEDEBUG=-all
export MSDOS_PATH='C:\TC4\BIN'
mkdir -p "$WINEPREFIX/drive_c/WORK"
cd "$WINEPREFIX/drive_c/WORK"
wine "$th04_root/_reference/ReC98/bin/msdos.exe" \
  -e -x tcc -c -ml -3 -O -Z C:\\WORK\\PROBE.C
wine C:\\TASM50\\bin\\TASM32.EXE /m /mx /kh32768 /t C:\\WORK\\PROBE.ASM
wine "$th04_root/_reference/ReC98/bin/msdos.exe" \
  -e -x tlink @C:\\WORK\\LINK.RSP
```

Place inputs below the prefix's `drive_c/WORK` directory so the DOS paths
resolve.  Record source, response file, outputs, environment, and all digests
before using a focused probe as evidence.  A successful invocation alone is
not a toolchain or exactness verdict.

## Troubleshooting without weakening evidence

- `Loader error (0000)`: confirm the isolated prefix and `C:\TC4`; do not run
  the DPMI binaries from a deep `Z:` path.
- Missing `dos.h` or libraries: verify `TURBOC.CFG` spelling/content and rerun
  attestation.  Do not add ambient host include paths.
- A bootstrap hash fails: preserve the bytes under private quarantine and stop;
  do not bless a changed mirror automatically.
- An existing installation blocks bootstrap: this is intentional.  Move it to
  a specific archival path, then make a new installation.
- The strict all-game or TH01 comparison returns 1: expected for the pinned
  calibration vectors.  Use `--gate calibration` only to test reproducibility.
- Wine, runner, or distribution version differs: it is a new environment.
  Update evidence only after repeated deterministic probes and cold builds;
  never silently edit the existing attestation.
