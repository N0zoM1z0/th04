# EFS beeper effects and offline PCM

v1326, 2026-10-09. The native `Beeper` owns EFS frequency tables, effect
selection, tempo and the PC-98 timer interrupt's SE scheduler. `BeepPcm`
samples its retained digital PIT state without opening an audio device.
`Beeper::consume` accepts the sound-control owner's EFS-file/effect requests.
This is a component and core consumer chain; frontend audio, PMD/FM synthesis,
physical timer installation and analogue speaker behavior remain unaccepted.

## Attested original evidence

Pinned OP is 42290 bytes, SHA-256
`8fc3b67fa8470de15b4f2844d5623d0a93d7922fac16d82a25a90a378b516b0f`.
Its stub-restored payload is 69028 bytes, SHA-256
`13222cb667e15c5034bd64c840a1db0a07c9acbb56e50f0bcf6025d12fe78d74`,
with 804 relocations. Fresh preflight and packed OP database attestation pass.
The database establishes identity, not independent decoded semantics.
Provenance remains `candidate-local-attested`.

`verify_beeper.py` executes original relative CODE0000 functions at load
segments 1000 and 2000, with DATA relative0F34:

| Owner | Original segment:offset |
| --- | --- |
| EFS read/parse | 0000:3632..3771 |
| Effect selection | 0000:3A64..3AAD |
| Frequency/end helper | 0000:3AAE..3B25 |
| Tempo | 0000:3B40..3B6D |
| PC-98 IRQ | 0000:381E..38CC |
| Silence | 0000:34B0..34DE |

The 16 effect descriptors start at DATA0F34:2680; count, selection and active
state are at 09B0,09B2,09AE. Tempo/timer words are 0956/0954; IRQ phase is
0962. Guarded file/allocator consumers supply temporary input and paragraph
buffers. Actual parser, arithmetic, calls/returns, IRQ and OUT instructions
execute; file-system/allocation failure behavior beyond missing-file return
is outside this bytes-owning native interface. DS, return-stack balance and
buffer/unrelated-data canaries are checked.

The parser appends effects without resetting prior count. Decimal arithmetic
wraps as WORD, including values above65535. Semicolon comments are recognized
while looking for a number; a semicolon already consumed as its delimiter
does not begin a comment. FF ends input and discards an undelimited final
number. Zero or256 nonzero frequencies completes an effect and stores another
zero terminator without advancing its cursor. A partial final effect remains
written even when return is -11; a missing file returns -2 without changes.
Parsing stops after16 completed effects.

The original allocator requests513 bytes per effect; a paragraph-rounded
528-byte test allocation permits the observed terminator WORD at offset512.
Native storage explicitly owns257 WORDs. Starting another read with count16,
oversized segment input and unsupported descriptors are host admission errors,
not claims about original out-of-range DS accesses.

Effect indices are signed1..count. Only enabled WORD exactly1 starts an effect;
other enabled values return success while retaining previous state. Play first
silences, selects the effect, resets its cursor and sets active1.

On PC-98 every IRQ reloads port71, increments the WORD phase, resets phase
exactly20 and skips SE there. Other phases divisible by4 advance an active
effect. A zero frequency clears active/cursor and silences. The original
library beeper-music flag is explicitly0; its separate music sequencer and
the IBM branch are outside TH04 SE scope. PIC acknowledgement is OUT0,20h.
The 8MHz/10MHz models use1996800/2457600Hz; frequency divisors clamp toFFFF
at the original30/37Hz division thresholds. Quiet divisors are998/1229.
Signed tempo30..240 divides the corresponding1996/2458 timer base times120.

## Independent controls and adapters

The real private MIKO.EFS is8284 bytes, SHA-256
`12045fed57d7c5a07da0047ae13c6607cbc78155cfbf5baa719fc310131de607`.
The pinned HDI is verified before extracting it; no asset is compiled into
product source or committed.254 cases compare221913 complete state/port/data
records across both original loads and GNU/optimized UBSan. They cover real
effects, parser delimiters/comments/overflow/capacity, appended loads, invalid
indices, enabled states, WORD phase wrap and tempo boundaries.

All15 real effects run at both clock bases. An independent scalar digital
PIT adapter consumes actual original OUTs at rational IRQ deadlines; native
output compares8,640,000 samples per host with block sizes144000 and137.
Sampling at the end of each sample, PIT mode3 odd-count high duration and
gain +/-8192 are explicit host policies. Neither digital adapter claims to
measure a physical PC-98 speaker or analogue waveform. Device/backend APIs
are never opened.30 private reference waveforms and their SHA-256s remain.

A source-only mutant changes `phase==20` to `phase>=20`. The independent trace
rejects it at line188204. Mutant source, compile command, executable digest
and differing state remain recorded; the disposable executable may be retired.
The default CTest also consumes actual Control->resource->Beeper->PCM requests,
using a bounded synthetic resource; this is not a frontend timeline test.

374 registered sources bind144 AMD64 products,48 per GNU/UBSan/MinGW;
47 CTests pass per Linux host. All94 prior Linux products remain byte-identical
to v1325. All47 prior MinGW products have new link hashes and receive current
build/format checks only. The original sound-control13198-case/73751-record
reference regresses unchanged on both Linux hosts. Producer receipts keep
their original manifests; current consumers have their own receipts.

Replay from the native checkout, using a fresh output directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 port64/verify_beeper.py \
  --target ../../targets/th04/op.exe \
  --decoded-dir ../../port64/op-unlock-v1317/decoded-original \
  --exe .analysis/port64/linux-live-v1251/th04-port64-beeper-contracts \
  --hdi ../../runtime/images/zun.hdi \
  --output-dir .analysis/port64/beeper-v1326/replay-new
```

Use `--reference-dir .analysis/port64/beeper-v1326/original-linux` for a current
UBSan consumer. Completed producers and any shared hardlinks are immutable.
Receipts, mutation, profiles, full pending-source recovery and cleanup live
under `.analysis/port64/beeper-v1326/`.

## Retention

The v1326 terminal-output cleanup shares44 duplicates after full bytes/hashes,
retires one source-only mutant executable and reclaims88,682,496 allocated
bytes (about84.6MiB).4,197 protected hashes remain unchanged at that boundary;
sources, inputs, independent references and all144 current programs remain.

Completed original/native streams and PCM references share immutable hardlinks.
Use fresh output paths; do not overwrite either alias. The source-only mutant
source/driver/commands/digests remain after its binary retirement.

## Reuse and remaining product work

The DOS v871 replacement parser rejects decimal overflow and its scheduler
differs from these target observations. It is semantic replacement source,
not an exact original beeper library; do not reuse it as an independent Oracle
or silently change DOS accepted state in this native batch. The Python
Oracle's inherited initial-DS field `data` must remain distinct from its
effect-buffer reader (`effect_data`).

Next join ordered OP/MAIN/MAINE sound requests and resource lifetimes,
including SE update after completed MAIN refresh. Implement PMD/OPN state,
music/FM synthesis and actual driver measure queries for waits, while keeping
all launches muted. Full natural ordinary/Extra routes, actual Windows
save/restart and dense Lunatic timing/performance remain required. This batch
does not promote DOS exact acceptance or publish a new GUI.
