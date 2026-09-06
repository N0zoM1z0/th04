# Headless Ghidra workflow

TH04 uses a pinned, headless-only Ghidra installation. The layout follows the
working TH095 pattern, while the database Oracle is rewritten for 16-bit DOS
MZ targets rather than PE images.

## Pinned versions and layout

`config/analysis_toolchain.toml` is the machine-readable lock file.

| Component | Version | Download SHA-256 |
| --- | --- | --- |
| [Ghidra](https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_12.1.3_build) | 12.1.3 (`Ghidra_12.1.3_build`) | `93a5d11a9ad510622acaaf908c556a7b9b764d338e78a7567f3689bf5081fd54` |
| [Eclipse Temurin JDK](https://github.com/adoptium/temurin21-binaries/releases/tag/jdk-21.0.12.1%2B1) | 21.0.12.1+1 | `ce79869e1307ed8ee1e2baa86a412b1eb5b75d10a01006d788a6f968bcfaee94` |

The resulting local layout is deliberately explicit:

```text
.tools/                              ignored acquisition and installations
├── downloads/
│   ├── ghidra_12.1.3_PUBLIC_20260817.zip
│   └── OpenJDK21U-jdk_x64_linux_hotspot_21.0.12.1_1.tar.gz
├── ghidra -> ghidra_12.1.3_PUBLIC
├── ghidra_12.1.3_PUBLIC/
├── jdk -> jdk-21.0.12.1+1
└── jdk-21.0.12.1+1/

ghidra-project/                      ignored private headless databases
├── TH04-th04-main.gpr
└── TH04-th04-main.rep/

.analysis/ghidra/                    ignored generated state
├── cache/ config/ data/             isolated XDG state
├── exports/ARTIFACT/                independently checkable database views
├── database-attestations/           final private receipts
└── toolchain-attestation.json
```

Do not move the downloaded or installed tools into `.analysis/`. Conversely,
do not put database exports or receipts in `.tools/`. This separation is part
of the documented interface, not an incidental local choice.

TH095 keeps its private database in an ignored root `ghidra-project/`, and
TH04 does the same. An attempted project below `.analysis/` failed with
`Path element starting with '.' is not permitted`; Ghidra rejects a project
path containing any dot-prefixed component. `AGENTS.md` therefore names
`ghidra-project/` as the one permitted private database directory inside the
repository.

## Install and attest

On Debian/Ubuntu x86-64, install the small host prerequisites and run the
bootstrapper:

```bash
sudo apt update
sudo apt install ca-certificates curl python3 tar unzip
bash scripts/bootstrap_analysis_toolchain.sh
```

The bootstrapper:

1. downloads the exact official Ghidra and Temurin assets into
   `.tools/downloads/`;
2. checks byte size and SHA-256 before extraction;
3. rejects absolute or parent-traversing archive members;
4. extracts into the versioned `.tools/` directories without overlaying an
   existing path;
5. creates `.tools/ghidra` and `.tools/jdk` as stable relative symlinks;
6. runs the complete identity and execution attestation.

It is safe to rerun when the pinned installation is already present. An
existing wrong or partial tree is never silently repaired or trusted: move it
aside, inspect the cause, and rerun. Validate at any time with:

```bash
python3 scripts/attest_analysis_toolchain.py
```

The attestor checks both archives; the complete 5,218-file Ghidra tree; the
complete JDK tree including 249 regular files and 205 safe internal symlinks;
the stable symlink targets; `application.properties`; `analyzeHeadless`;
`Base-src.zip`; the exact `MzLoader.java` member; `java`, `lib/modules`, and
the JDK release file; the JDK banner; and an actual headless usage launch.
The expected Ghidra tree identity is
`e0010fa34fd19c0f5da778f3bf693db56082378367034dafd2e6c58a12b75c39`.
A clean temporary checkout with an empty `.tools/` directory has replayed the
complete extraction, link creation, and attestation path; this is not merely an
in-place check of the first manual installation.

`scripts/tool-env.sh` exposes the same stable links and isolated XDG
directories for an unusual manual headless command:

```bash
source scripts/tool-env.sh
"$GHIDRA_HOME/support/analyzeHeadless" 2>&1 | head
```

Normal work must use `scripts/ghidra.py`, which repeats target and tool
attestation automatically. There is intentionally no GUI command or GUI
workflow. Ghidra's own
[headless analyzer reference](https://github.com/NationalSecurityAgency/ghidra/blob/Ghidra_12.1.3_build/Ghidra/RuntimeScripts/support/analyzeHeadlessREADME.md)
documents the underlying command-line engine; the repository wrapper adds the
TH04 safety and MZ checks described below.

## Clean headless import

First import and analyze one pinned MZ artifact:

```bash
python3 scripts/ghidra.py th04-main import
```

The command refuses to overwrite an existing project. It explicitly selects
`MzLoader`, language `x86:LE:16:Real Mode`, compiler specification `default`,
and defaults to project `ghidra-project/TH04-th04-main`. Override CPU or the
per-file analysis timeout when necessary:

```bash
python3 scripts/ghidra.py th04-main import \
  --max-cpu 4 --analysis-timeout 1800
```

`--no-analysis` is available only for quick loader/Oracle calibration. It does
not create trusted function boundaries:

```bash
python3 scripts/ghidra.py th04-op import --no-analysis
python3 scripts/ghidra.py th01-op-smoke import --no-analysis
```

Other MZ artifact IDs from `config/targets.toml` work the same way. Project
names are per artifact. The wrapper will not import a target whose size,
SHA-256, MD5, detected format, or MZ structure differs from the manifest.

To intentionally rebuild a project, move both its `.gpr` and `.rep` into a
private backup directory first. Never ask the wrapper to overwrite a database
whose provenance is unknown.

## Required read-only check

Before using a database for target-dependent work, run:

```bash
python3 scripts/ghidra.py th04-main check
```

This opens the saved program with `-readOnly -noanalysis`, exports a fresh
view, and invokes an independent Python MZ parser. A random per-run nonce ties
the final receipt to that exact export. This is necessary because Ghidra
headless can report a post-script exception while still returning process
status 0; stale output cannot pass the nonce check.

The following dimensions must all pass:

- target SHA-256 and original complete Ghidra `FileBytes`;
- MZ loader display name, language, compiler specification, image base, and
  absence of an analysis timeout;
- complete MZ header bytes as read from the `HEADER` overlay;
- complete load module bytes after applying every MZ relocation for Ghidra's
  fixed load segment `0x1000`;
- modified `FileBytes`, with no changes except the independently predicted
  relocation words;
- exact header and load-module file-offset coverage with no gaps or overlaps;
- segment:offset-to-file-offset consistency for every loaded source range;
- every relocation address, raw table segment/offset, status, type, original
  word, relocated word, and multiplicity;
- the external entry point `(0x1000 + CS):IP`;
- deterministic entry, quartile, tail, and relocation-site byte samples.

The full digests are stronger than samples, but samples remain in the receipt
for fast human and agent inspection. Exports and receipts stay private below
`.analysis/ghidra/`; they contain original game bytes and must never be
committed.

## Oracle calibration

Run fault injection against a fresh positive export:

```bash
python3 scripts/smoke_ghidra_oracle.py th04-main
```

The test changes one loaded byte, one relocation result, one file mapping, and
the export nonce in isolated temporary copies. Each must fail its intended
dimension. The test never changes the target or saved database.

Real-corpus calibration also covers both major branches:

- TH04 `OP.EXE`: 32-byte header and zero relocations;
- TH01 `OP.EXE`: 4,096-byte header and 625 relocations;
- TH04 `MAIN.EXE`: 6,144-byte header and 1,136 relocations, tested after a
  complete auto-analysis and again through the read-only check.

These passes prove that the importer/exporter/attestor agree with the pinned
targets. They do not prove Ghidra's inferred functions, types, names, control
flow, or decompiler output.

## MZ loader limits and evidence boundary

The pinned Ghidra 12.1.3
[`MzLoader` source](https://github.com/NationalSecurityAgency/ghidra/blob/Ghidra_12.1.3_build/Ghidra/Features/Base/src/main/java/ghidra/app/util/opinion/MzLoader.java)
shows that it:

- uses load segment `0x1000`;
- discovers candidate segment blocks from relocation values;
- applies the relocation words to loaded program memory;
- maps the MZ header through a `HEADER` overlay based on the OTHER space;
- creates entry `(0x1000 + CS):IP`;
- heuristically shifts some block starts after scanning their first 16 bytes
  for a far-return opcode (`RETF`, `0xCB`).

Consequently, the database's original bytes, relocated memory, relocation
records, and entry can be checked exactly, but its block and function
boundaries remain provisional navigation data. A Ghidra database and its
decompiler are a single target-analysis view, never an independent semantic
Oracle and never an exact reconstruction result.

## Provenance

The directory and wrapper pattern was adapted from the pinned TH095 reference
checkout. TH04 adds full MZ/FileBytes/relocation/mapping attestation because
TH095's PE-oriented image-base and `.text` checks are insufficient for 16-bit
real-mode targets. Ghidra and Temurin remain third-party tools under their own
licenses; neither binary distribution is committed here.
