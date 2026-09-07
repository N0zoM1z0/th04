# Knowledge base

The knowledge base is durable project memory for future agents.  It records
facts, recipes, reusable patterns, hazards, negative results, and open
questions without converting uncertainty into folklore.

`config/knowledge.csv` is the canonical index.  This document explains how to
use it and expands only the entries that need context.  Evidence remains in
`config/evidence.csv`; falsifiable unsettled claims remain in
`config/hypotheses.csv`.

## Entry contract

Every knowledge row has:

- a stable ID and one kind: `fact`, `recipe`, `pattern`, `hazard`,
  `negative-result`, or `open-question`;
- the narrowest portability scope (`th04-main`, `th04`, `pc98-borland`,
  `control-plane`, and so on);
- one of the controlled confidence terms from `AGENTS.md`;
- evidence IDs when the fact was established locally;
- source references for reproducibility;
- a concise statement and verification date.

Do not create an entry merely because a decompiler emitted a plausible name.
Do create one when a result will change how the next agent searches, probes,
builds, compares, or avoids a known dead end.

## Current target knowledge

- The public manifest pins the extracted Japanese HDI and executable hashes,
  not the private outer archive.  Canonicality is
  `candidate-local-attested` until independent confirmation.
- The Anex86 HDI header is 4096 bytes.  The `TOUHOU` FAT12 boot sector begins
  at file offset 38912 and uses 1024-byte logical FAT sectors even though the
  HDI geometry reports 512-byte physical sectors.
- TH04 `OP.EXE`, `MAIN.EXE`, and `MAINE.EXE` are MZ.  `ZUN.COM` is also MZ;
  extensions are not reliable format evidence across the five games.
- TH02 and TH05 `ZUN.COM` are flat COM in the local corpus, while TH03 and TH04
  launcher containers begin with MZ.  Parser routing must inspect bytes.

## Current Oracle knowledge

- Raw equality is the only exact verdict.
- Relocation-normalized equality is useful for isolating changed linked
  segment words, but it is explicitly diagnostic.
- Header, ordered relocation table, relocation set, load module, normalized
  load module, and overlay are separate dimensions.
- The TH01-TH05 original corpus plus injected mutations validates parsing and
  failure routing over real artifact diversity.
- The locally pinned build-chain candidate passes 14 required portable
  identity surfaces, and the calibrated host also matches two diagnostic Wine
  surfaces. Two deterministic C-to-OMF-to-MZ plus ASM-to-OMF execution rounds
  prove what local bytes executed, not universal canonicality of the HTTP-only
  TC4J source.
- OMF producer comments and dependency records provide cheap, high-signal
  contamination checks before final linking.  They supplement binary hashes;
  they do not prove semantics or source correctness.
- Borland COMENT `E9` records carry DOS time/date metadata.  Retain the raw OMF
  digest and compare a second digest that normalizes only those four bytes.
  Never normalize LEDATA: ReC98 research probes intentionally compile
  `__DATE__`/`__TIME__` into data, and that is a real build difference.
- Three isolated ReC98 cold builds agree on all 20 selected TH01-TH05 outputs.
  All 416 generated OMF objects validate.  Strict comparison finds three
  raw-exact COM files and rejects all four TH04 candidates.
- Per-game dependency-timestamp-normalized OMF identities are stable across
  all three builds.  The combined Research/Pipeline-inclusive identity is not,
  because those probes retain real source-level build-date strings in LEDATA.
- The pinned known TH01 vector is a regression Oracle for build/comparator
  stability.  It must never be interpreted as three waived exact failures.
- The all-game vector is a fast routing Oracle: it pins every compact numeric
  dimension and candidate byte identity, yet the default command remains a
  strict raw gate.  TH02's 2/17/1-byte MZ differences are good narrow-probe
  controls; TH04 `OP`/`MAINE` require broader ownership/layout work.
- Exact evidence is explicitly global, artifact-scoped, or unit-and-extent
  scoped. Same-artifact evidence cannot satisfy another unit's compilation,
  layout, raw-byte, or cold-replay gate.
- A synthetically forged exact row now fails on reused unit evidence, missing
  metadata/source/address, unequal raw hashes, private replay drivers, and
  out-of-artifact extents.
- OMF validation requires one module rather than merely valid outer records;
  concatenating two valid THEADR-to-MODEND streams is rejected.
- For difficult Borland FIXUPP ordering, the already-attested TC4J `TDUTIL.PAK`
  contains Turbo Dump 4.1. Extract `TDUMP.EXE` only into ignored analysis space
  with the same-media unpacker; never commit the proprietary tool. TDUMP's
  Pointer16 fixup location refers to the offset word, so the linked MZ segment
  relocation is LEDATA base + fixup location + 2.
- MZ format validation includes the last-page encoding, allocation ordering,
  and minimum-allocation stack envelope. All 20 private target controls still
  pass the stricter parser.
- Never borrow a target file offset when comparing a structurally relinked MZ
  candidate. Parse each file's own `e_cparhdr` and compare load-module/program
  offsets. A TH04 dialog split produced exact code at the same program address
  with a `0x1600` candidate header versus the target's `0x1800`; target-file-
  offset slicing falsely reported hundreds of code differences.
- `ndisasm` can wrap the raw bytes of an instruction longer than eight bytes
  onto a continuation line such as `-00`. Never infer instruction length from
  only the first displayed hex field. Use adjacent decoded addresses (x86 max
  length 15 bytes) and separately require complete extent coverage.

## Current toolchain knowledge

- The Borland DPMI loader fails with `Loader error (0000)` from the deep Wine
  `Z:` repository path.  A project-local prefix and short `C:\TC4` path are
  part of the reproducible environment.
- Turbo C++ 4.02 reads `TURBOC.CFG` for the include/library configuration used
  here.  The plausible `TCC.CFG` filename does not supply `dos.h` and caused a
  failed first cold build.
- TC4J BIN, INCLUDE, LIB, and startup source trees are independent attestation
  surfaces.  Pinning only `TCC.EXE` would miss ABI-affecting headers, startup
  objects, emulation libraries, and linker inputs.
- The original PC-98 `TC.EXE` IDE is another same-media diagnostic surface.
  Replay it only through `scripts/probe_tc4j_pc98_ide.py` under the pinned
  DOSBox-X `machine=pc98` profile; the IBM-compatible MS-DOS Player cannot pass
  its machine detection. Despite the IDE's 4.0 banner, generated OMF reports
  `TC86 Borland C++ 4.02`, and `_BX = _AX` still emits `8B D8`, not `89 C3`.
- Required downloaded/tool identities are checked before execution. Host Wine
  hashes are diagnostic because distro builds vary; exact cold output remains
  the portable gate.
- Detailed acquisition, automatic installation, focused invocation, cold-build
  usage, and recovery instructions are in `docs/TOOLCHAIN.md`.
- Headless analysis uses Ghidra 12.1.3 and Temurin JDK 21.0.12.1+1. Downloads,
  versioned trees, and stable `ghidra`/`jdk` symlinks belong under ignored
  `.tools/`; private databases belong under ignored `ghidra-project/`; only
  generated cache/export/receipt state belongs under `.analysis/ghidra/`.
- Ghidra refuses a project path with the dot-prefixed `.analysis` component.
  This negative result is why `ghidra-project/` is an explicit repository
  safety exception rather than an arbitrary second private-state convention.
- The headless wrapper validates the target and analysis tools on every run.
  A fresh nonce plus an external Python MZ parser prevents a stale Java export
  from passing even if Ghidra reports a script failure with process status 0.
- Ghidra project files are disposable local state rather than cross-machine
  hash surfaces. The fresh export is strict: every target-backed mapping must
  be exactly header or load-module, so an additional alias is rejected.
- Ghidra's MZ loader applies relocation words for load segment `0x1000` and
  maps the header into a `HEADER` overlay. Full database bytes, relocation
  records, source mapping, entry point, and samples are attestable; inferred
  block/function topology is not.
- The database Oracle has real-corpus controls for both 0-relocation TH04 OP
  and 625-relocation TH01 OP, plus a 1,136-relocation analyzed TH04 MAIN. The
  loaded-byte, relocation, mapping, and nonce negative mutations all fail.
- Complete headless installation, import, read-only check, calibration, path
  layout, failure recovery, and limitation instructions are in
  `docs/GHIDRA.md`.

## Reference knowledge boundary

ReC98 is strong evidence for PC-98 hardware behavior, target-specific
semantics, compiler patterns, source partition candidates, and the known
toolchain family.  Its names and source are corroboration until checked against
the selected TH04 target.  Its public reverse-engineered/finalized/position-
independent metrics are not per-unit byte-match states.

Upstream work is always quarantined as candidate material.  Even a ReC98 unit
described as finalized or matching must pass local boundary review, an attested
cold rebuild, the full required Oracle vector, and affected-unit replay before
this repository can call it exact.

TH08/TH095/TH105 provide control-plane patterns and examples of strict
promotion, but PE/COFF/MSVC assumptions do not transfer to 16-bit MZ code.

## Negative-result discipline

When a plausible experiment fails:

1. keep bulky raw output below `.analysis/`;
2. record the exact target/tool/input and what observation rejected the idea;
3. add an evidence row with `fail` or `inconclusive`;
4. add a `negative-result` knowledge row only when it rules out a reusable
   search path;
5. state the narrow scope so another artifact, memory model, or TU is not
   incorrectly constrained.

This is the highest-leverage form of agent memory: it prevents future sessions
from repeating source-shape guesses that the target or compiler already
falsified.

## Query recipes

```bash
# Live reconstruction state
python3 scripts/status.py --json

# All durable knowledge (CSV remains deliberately grep-friendly)
column -s, -t < config/knowledge.csv

# Evidence for one knowledge entry
rg 'ev-oracle-smoke-corpus' config/evidence.csv config/knowledge.csv
```

Before handoff, update the index and this document only when the routing map or
entry contract changes.  Detailed target discoveries should live in focused
notes linked from `source_refs`, not in an ever-growing monolith.

- A direct Borland pseudo-register load from a parameter can change register
  allocation globally. In TH04 `snd_load`, `_AX = func` promotes `func` to DI;
  reading through `*reinterpret_cast<snd_load_func_t near *>(&func)` keeps it
  memory-resident and naturally recovers the target BP-relative `8B 46 06`.
- For a small natural replacement inside a pinned upstream scaffold, use the
  replay driver's fail-closed `source_mode=replace`: bind the complete scaffold
  SHA-256, old-span offset/size, and old-span SHA-256 before replacement. Never
  treat surrounding scaffold source as maintained exact source merely because
  the linked slice matches.
- `geninterrupt(i)` is just TC4J `__int__(i)` and carries no DS-clobber contract.
  In the clean corpus, isolated mid-function `PUSH DS ... POP DS` has no natural
  C/C++ compiler precedent outside full `__saveregs`/interrupt prologues; `__seg`
  locals still lower to MOV-based segment saves/restores.

- For Borland far-call bridge recovery, separate compiler OMF from final linker
  output. TC86 may leave an external call as five-byte `CALL FAR`; `#pragma
  samecodeseg` can change only the Pointer16 frame. TLINK 6.10 defaults to
  far-to-near optimization unless `/f` is supplied and can then preserve the
  five-byte footprint as `NOP; PUSH CS; CALL near`, removing the segment
  relocation. TH04 `bullets_update` is the accepted control for this exact
  mechanism. `#pragma alloc_text` and `/P` packing alone do not produce it.

- Raw-identical module contributions are not automatically authored-C/C++
  boundaries. TH04 `mb_dft.cpp` is the concrete control: only its first 0xD9
  bytes are currently reviewed authored C/C++, because target Ghidra + TLINK
  bind two pure score-bonus functions there and the next public begins the
  upstream inline-assembly-containing `midboss_defeat_update`. When Ghidra
  min/max spans agree but its body set is noncontiguous, keep the automatic
  function gate strict and use the configured manual exact path with exact
  owner + TLINK public + matching min/max + gap-free `ndisasm` through RET.
- Exact-replay overlays must respect cross-game source ownership. A TH04 wrapper
  can include a lower-game source that is also independently compiled for
  TH02/TH03; replacing that shared path with TH04-only source can break the
  full corpus even if the TH04 object is the intended target. For
  `snd_mmd_resident`, overlay `th04/snd_mmdr.c`, not shared
  `th02/snd/mmd_res.c`. The `__es` pointer form recovers the natural LES, but
  TC4J C-mode early-return tail merging remains a separate byte-exactness
  blocker; ordinary return, explicit-goto, `_AX` self-assignment, and `-O-`
  variants are recorded negative results rather than reasons to reintroduce
  inline `RETF` assembly.

- For a raw-identical contribution ending in `#pragma codestring`, split the
  maintained authored-C/C++ owner at an independently decoded function return.
  TH04 `snd_se_reset` is the concrete control: TLINK starts the public at
  `0x238A6`, raw decode reaches `RETF` after 11 bytes, and the twelfth byte is a
  standalone NOP from the codestring. The 11-byte function can be exact byte
  ownership even though Ghidra has no function there; do not fabricate a
  function-ledger row. Cross-game maintained includes use `compat/rec98` plus
  replay `forwarded-fragment`, preserving both policy and scaffold identity.
- Re-screen candidate residuals before treating them as denominator growth.
  The 0x5A-byte `stages.cpp` gap is exactly `carpet_lighting_put_new()` by TLINK
  publics, and its candidate source uses inline ASM for DS/ES, MUL, LODSB, SHL,
  and LOOP. The following 0x1AA bytes are already exact pure C/C++; leave the
  mixed-ASM prefix outside authored-C/C++ ownership unless those operations are
  first recovered naturally and revalidated.

- Treat one-byte module gaps as explicit ownership surfaces rather than leaving
  a whole raw-identical module provisional. TH04 now has six target-observed
  padding owners at file `0xE341`, `0x14EB3`, `0x150B1`, `0x150EB`, `0x15531`,
  and `0x15715`; reference-source `#pragma codestring` values corroborate but do
  not establish these target bytes. Retire a routing umbrella only when exact
  owners plus reviewed padding cover its complete contribution.
- `item_splashes_init` is a useful TC4J zeroing negative control. Its 26-byte
  target body differs from the current candidate only by `31 C0` versus
  `33 C0`. Regular `memset` calls the runtime; Borland `__memset__` is a true
  compiler intrinsic but changes register-setup order and still uses `33 C0`;
  `_AX ^= _AX` also canonicalizes to `33 C0`. Do not use inline assembly or
  `__emit__` to manufacture the target encoding.

- Do not use Ghidra's function inventory as the authored-function universe.
  Cross-check every TLINK public that falls inside an exact authored byte owner
  against the function ledger. TH04 recovered eight omitted functions this way;
  one (`bullet_turn_y`) was even hidden inside an unrelated oversized Ghidra
  body. `reviewed_exact_no_ghidra` requires a matching exact owner/public,
  gap-free raw decode through `RET`/`RETF`, and an exact next-public or owner-end
  boundary. Switch metadata/tables must completely fill any trailing extent and
  target decoded instruction starts. The current exact-owner public audit has
  zero remaining omissions.
- `dialog_animate` is a second accepted control for Borland `#pragma
  samecodeseg` plus normal TLINK far-call optimization. A natural external C++
  call reproduces the target five-byte `NOP; PUSH CS; CALL near` bridge and
  ordered relocations in both focused and 65-unit cold replay. This mechanism
  does not explain four-byte `PUSH CS; CALL near` targets; those require a
  different TU/segment producer explanation rather than byte injection.
