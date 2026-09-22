# TH04 public trial provenance intake v500

## Why this route matters

The reviewed MAIN frontier is down to 27 bytes: `snd_load`'s two-byte
`MOV BX,AX` encoding, checkerboard's two-byte counted `LOOP`, and 23 low-level
bytes in `carpet_lighting_put_new()`.

The existing registered TH01-TH05 targets do not independently witness these
TH04-only producer choices. In particular, TH02/TH03/TH05 `snd_load` use the
ordinary `8B D8` form, while the generalized checkerboard and carpet lineage
scans remain unique to TH04. Compiler/mechanism probes can reproduce the
integrated-assembler forms, but mechanism alone is not source provenance.

An earlier TH04 build is therefore unusually valuable. If a genuinely
independent trial build contains the homologous operation with the same rare
low-level encoding, it can provide the same *kind* of source-origin
corroboration that earlier packets used for accepted handwritten low-level
idioms. It still cannot replace the retail target exactness Oracle.

## Public historical routing evidence

The old Amusement Makers download listing is preserved in later PC-98 setup
material as identifying the TH04 trial self-extractor as `GEN_TS1.EXE`, dated
1998-07-02 and sized **597,930 bytes**. Independent installation guides identify
the same filename as a self-extracting TH04 trial and launch the extracted game
through `GAME.BAT`.

The trial's separately preserved `体験版.TXT` identifies itself as
`東方幻想郷 体験版 ver1.00`, PC-98/EPSON-PC software from 1998, and states that
play is limited to Stage 3. The same text permits redistribution of the trial
archive when its files are left unmodified.

These are external routing constraints only. They do not establish the SHA-256
or pristine identity of any candidate binary.

Useful public references:

- historical download endpoint: `http://www.kt.rim.or.jp/~aotaka/am/get.htm`
- installation walkthrough identifying `gen_ts1.exe`:
  `https://j02.nobody.jp/jto98/n_desk_install_t/th345t.htm`
- preserved trial text:
  `https://thbwiki.cc/附带文档:东方幻想乡体验版/Taiken`

## Current acquisition state

No trial binary is registered under `.analysis/targets`, and the v413-v419
forensic packets already show that the supplied hash-attested TH04 HDI contains
no recoverable `GEN_TS1.EXE` in active files, deleted entries, free clusters,
allocated slack, or active archives.

During v500 the historical direct download endpoint was not usable from the
current environment. Public pages can therefore route a future candidate but
cannot substitute for candidate bytes. No mirror metadata is promoted into a
target or Oracle claim.

## Fail-closed intake gate

`scripts/probes/probe_th04_trial_intake_v500.py` accepts only a private candidate
below `.analysis/` and never executes it. It requires:

1. the published 597,930-byte outer size;
2. a structurally valid DOS MZ self-extractor;
3. an appended sequential level-0/1 LHA stream beginning exactly at the MZ
   declared end;
4. valid LHA base-header checksums and a complete terminator;
5. `GAME.BAT` and `体験版.TXT` in the member table;
6. archive CRC acceptance by host `lha` plus independent `7z` acceptance;
7. decompressed CP932 markers for `東方幻想`, `体験版 ver1.00`, and `３面まで`.

A passing receipt labels the artifact only
`candidate-public-trial-structural` and explicitly records
`official_pristine_identity_proved = false`. The candidate SHA-256 then becomes
stable enough for bounded semantic comparison and later provenance review.

The parser has checked-in regression tests for CP932 member names, header
checksums, the level-0/1 fail-closed boundary, and DOS-style basenames. A manual
negative control also confirms that the attested retail `MAIN.EXE` is rejected
at the outer-size gate.

## Next experiment after a candidate passes

Do not immediately add the trial to the exact target set. First retain its
private intake receipt, extract the executable members without executing the
SFX, and classify the trial's own target identities as provisional historical
cross-build evidence.

Then search specifically for the three final blocker semantics:

- the DOS-open handle transfer in `snd_load`;
- the checkerboard ES dword-store counted loop;
- the carpet word/dirty-column fill producer.

A matching rare instruction or sequence must be bound to a homologous semantic
operation, not found by naked byte search alone. If that independent build
corroborates a handwritten low-level idiom, source classification may be
reopened. Any resulting retail-source change must still pass the normal focused
cold replay, raw/MAP/ordered-relocation gates, and full affected aggregate
before receiving exact credit.

Until candidate bytes pass this intake, the MAIN gap remains **27 bytes**.
