# MAIN gameplay loop conditional producer (v248)

The pinned MAIN.EXE target and active Ghidra database passed this session's
preflight and database attestation. The reviewed `gameplay_loop()` body is
`th04-main / DEMO_TEXT 0AAF:0098`, MZ load `0xAB88..0xAD02`, target file
`0xC388..0xC502`, 379 bytes, SHA-256
`54ac4974b571dc990934e9c5ed39afb1b91206c397b67c734442fe81fd6c4448`.
The target's lives-to-play-performance-interval branch begins at load
`0xACC7` and has a unique 25-byte sequence, SHA-256
`2ae6bf38991401052fbd9ef0995b4557466b4f5bc982130e4466498ffadba1f9`.

The earlier maintained source assigned `frames_per_playperf_raise` in both
branches. Target machine code instead forms either branch result in `AX`, then
moves it into `SI` once at the join. A bounded diagnostic replaced only those
assignments with a conditional expression of the same values. The verified
conditional expression is now maintained in `src/main/core/gameplay_loop.cpp`.

Run:

```sh
python3 scripts/probes/probe_th04_gameplay_ternary.py --output-dir .analysis/reconstruction/probes/v248-gameplay-ternary-replay
```

The replay verifies target SHA-256 and the pinned TC4J 4.02 binary, compiles
both sources under `-c -I. -O -b- -3 -Z -d -DGAME=4 -ml` in a temporary v214
source materialization, and validates OMF checksums. The baseline emits 370
DEMO_TEXT bytes (SHA-256
`8d097211c052105dad8da37d9af0305ca28d7ea7371472207284d97e70490224`)
and lacks the target branch. The conditional expression emits 372 bytes
(SHA-256
`54c691f5ea776a4b71003c10f772c825e729ea852eb494fa65a364710c8c6ebc`)
and contains **the exact 25 target branch bytes** once, at object offset 314.
The private receipt SHA-256 is
`3e49ce3a4af999c67ec74cd27aba8c1274f818ee932cc3987f501a6298c511ff`.

The full target function is still seven bytes longer than this source
object. Relative to this compiler output, the target's frame-counter sequence
is three bytes longer and it retains two `EB 00` jumps. Their natural source
producer remains open; the linked call shape also needs the complete raw/MAP/
ordered-relocation replay. This is compiler-observed local codegen, not
exactness, and it does not justify an inert jump or byte padding. The probe
now reconstructs the historical baseline from the maintained source and
replays both variants, preserving the original v248 comparison.

The historical maintained-source rerun was
`python3 scripts/probes/probe_th04_gameplay_ternary.py --output-dir .analysis/reconstruction/probes/v252-gameplay-ternary-maintained`.
Its private receipt SHA-256 was
`3e49ce3a4af999c67ec74cd27aba8c1274f818ee932cc3987f501a6298c511ff`:
both variants, object CODE hashes, and branch offsets were unchanged. The
source SHA-256 for that run is
`330b49a298b0a27a52685b4daa4cad3ebf34fdb7e5ada51b4a62c9a8ea8b0c5b`.

## v273 frame-counter source revision

The current maintained source combines the increment and first modulo assignment
as `stage_frame_mod16 = ((stage_frame = stage_frame + 1) & 15)`. Its unsigned
16-bit `stage_frame` declaration makes this equivalent to the former two
statements. Run `python3 scripts/probes/probe_th04_gameplay_ternary.py
--output-dir .analysis/reconstruction/probes/v273-gameplay-frame-replay`.
The pinned TC4J/OMF replay compares the old and revised frame expressions and
also retains the old branch control. The revised 372-byte CODE SHA-256 is
`e3d6e451f5c5988c21c885be406815bf8c8fd23c181494db67bea74001b245ed`;
the former 372-byte CODE is still
`54c691f5ea776a4b71003c10f772c825e729ea852eb494fa65a364710c8c6ebc`.
The revision emits the target-style `MOV AX; INC AX; MOV [stage_frame],AX`
sequence while preserving the exact 25-byte interval branch. The target still
has an extra `MOV DX,AX`, a 16-bit rather than 8-bit first mask, and two
`EB 00` jumps. Complete bytes remain 372 versus 379, so this is
compiler-observed local progress, not exactness. Receipt SHA-256:
`b107b6d7d48ebc53a5a1b7086d6c9a8b6fda09f201535141106c454c2b479e97`.

## v285 optimization-toggle control

Replacing only production `-O` with `-O-` for the current maintained source
under the pinned TC4J/v214 header snapshot emits the **same** 372-byte
DEMO_TEXT CODE, SHA-256
`e3d6e451f5c5988c21c885be406815bf8c8fd23c181494db67bea74001b245ed`.
It still contains no `EB 00`, `MOV DX,AX`, or 16-bit `AND AX,000F`; the exact
25-byte interval branch remains. This single option toggle does not explain
the seven target bytes. The command, valid OMF, CODE, and private receipt are
under `.analysis/reconstruction/probes/v285-gameplay-opt/`; receipt SHA-256
`57b9e2be2f15f9fb7098c059953987bdef5aad0f76dbe8c06d4eb2145d875ad4`.
No source or exact state changes.

## v296 word-width source revision

The maintained source now assigns the first frame mask through TC4J's real
`_AX` register interface, then chains the smaller masks through `_AL`.
For unsigned 16-bit `stage_frame`, the four stored phase values are unchanged.
This naturally emits target `AND AX,000F` instead of `AND AL,0F`, while leaving
the previous CODE prefix byte-identical and changing only the necessary
branch displacement afterward.

Run `python3 scripts/probes/probe_th04_gameplay_ternary.py --output-dir
.analysis/reconstruction/probes/v296-gameplay-wide-mask-replay`. An independent
repeat under `v297-gameplay-wide-mask-repeat` produces identical valid OMF
SHA-256 `3cede1302faeb34bcf68bbf481e6ead8fdbb7c3ead028fa6b15ef32892283387`
and 373-byte `DEMO_TEXT` CODE SHA-256
`b756cf95be543098dfb679fadcf7135dd7b54b163731e653b7a149f1595c7c50`.
Both receipts are byte-identical, SHA-256
`205e5592a8b5f7626a5e57c078a068af3755f2497b55fc662d012c487be9f8e1`.
The probe also replays the earlier 370/372-byte historical controls from the
maintained source, so their compiler observations remain reproducible.

The target remains 379 bytes. Its extra `MOV DX,AX` at body offset 0x118 and
two `EB 00` jumps at 0xF0 and 0x16A have no justified natural producer yet.
This revision improves compiler shape by one byte; it does not pass a linked
raw/MAP/ordered-relocation comparison or promote the unit to exact.

## v302 conditional-expression control

The target has `EB 00` at body offsets `0xF0` and `0x16A`, immediately after
the palette update and play-performance raise conditional bodies. A pinned
TC4J synthetic control shows that an ordinary one-arm `if` and an explicit
empty `else` emit no such jump. A void conditional expression with a true
side effect and `(void)0` false arm emits `EB 00` after the true body.

`python3 scripts/probes/probe_th04_gameplay_conditional.py --output-dir
.analysis/reconstruction/probes/v302-gameplay-conditional-replay` applies
each candidate form independently to the maintained complete loop. Two
isolated compiler rounds produce identical valid objects:

| Temporary source form | CODE bytes | `EB 00` offsets |
| --- | ---: | --- |
| Maintained `if` source | 373 | none |
| Explicit empty `else` | 373 | none |
| Palette condition only | 375 | `0xF0` |
| Raise condition only | 375 | `0x166` |
| Both conditions | 377 | `0xF0`, `0x168` |

The second offset is two bytes before the target's `0x16A`, consistent with
the still-missing target `MOV DX,AX` at `0x118`. The two-condition CODE SHA-256
is `4715a98c6b059be0f7ebfff9c67172bb81e9458037280c2f8f467b93f9419b6e`;
private receipt SHA-256 is
`3a7abc379d5209239533e0e9424ece435eb57f31c3480e35a233c85d59e8a8bd`.

This identifies a possible compiler mechanism, not the historical source.
The `(void)0` arms have no runtime effect and cannot be inserted into product
source solely to manufacture the two jumps. The maintained source and exact
state remain unchanged. The original source form, target `MOV DX,AX`
producer, and linked owner comparison are still open.

## v308 frame-increment control

The target frame-counter bytes at body `0x115..0x120` remain
`A1 8A 53 8B D0 40 A3 8A 53 25 0F 00`: `MOV DX,AX` precedes the increment.
`python3 scripts/probes/probe_th04_gameplay_increment.py --output-dir
.analysis/reconstruction/probes/v308-gameplay-increment-replay` compiles four
semantically equivalent increment forms in two isolated pinned-TC4J rounds.
All OMF and CODE pairs agree. Pre-increment, `+= 1`, and a separate
post-increment/read each emit 373 bytes; post-increment plus one emits 374.
None emits `MOV DX,AX`. The maintained 373-byte baseline is unchanged.

Receipt SHA-256: `5e97328ffe6a36f8ea027c423b402cbd2de4152332d663c11299284686984636`.
These ordinary increment forms do not solve the two-byte gap. No product
source, linked bytes, or exactness state changed. The target producer remains
unknown; introducing a dead DX assignment would not be justified.

## v346 shared-codegen handoff

The pinned TH05 MAIN target supplies independent cross-game evidence for all
three remaining TH04 instruction shapes. A masked scan of the two attested
load modules finds the same
`MOV AX,[stage_frame]; MOV DX,AX; INC AX; MOV [stage_frame],AX; AND AX,000F`
sequence at TH04 load `0xAC9D` and TH05 load `0xB026`. The nearby zero-distance
jumps are at TH04 loads `0xAC78/0xACF2` and TH05 loads `0xB001/0xB053`.

A bounded TC4J experiment combined the two already observed void conditional
expressions with symbolic `_AX/_DX` frame-counter dataflow. The resulting
valid `gloop.obj` CODE is exactly 379 bytes, SHA-256
`645e6530f9907d469842dd924db5c1f7b2e2414177a76ea9f3de35441f3e8c27`.
It places `EB 00` at body offsets `0xF0/0x16A` and `MOV DX,AX` at `0x118`,
matching the target instruction positions. This is compiler-observed and
cross-game-corroborated source evidence; it has not passed linked raw bytes,
MAP, ordered relocations, or aggregate replay.

The temporary v346 product/config edits were restored. The retained private
build
`.analysis/reconstruction/exact-unit-replay/gpt-5-6-sol-v346-gameplay-symbolic-focused-004/`
reaches TLINK and stops only on the case-sensitive `SHOTS_RENDER()` external.
Earlier ABI fixes reduced the initial unresolved list to that one symbol. A
continuation should reconstruct the bounded source/config change from this
materialization, bind the external without changing generated instructions,
then run focused A/B and the full default aggregate before promotion.


## v375 exact linked closure

The v346 compiler result is now a linked exact owner. The maintained
`src/main/core/gameplay_loop.cpp` keeps the two void conditional expressions
and the cross-game-corroborated `_AX`/`_DX` frame-counter dataflow. Under
the current localized header closure, TC4J still emits exactly 379 DEMO_TEXT
CODE bytes with SHA-256
`645e6530f9907d469842dd924db5c1f7b2e2414177a76ea9f3de35441f3e8c27`;
this is identical to the retained v346 LEDATA.

Two link-only details were required without changing those instructions.
First, splitting the original word-aligned DEMO_TEXT monolith after a 0x17B
object made TLINK align the residual `th04_main.asm` contribution from target
offset `0x0213` to `0x0214`. A SHA-bound replay transform changes only the
residual contribution alignment to byte alignment, restoring physical continuity
at `0AAF:0213` without emitting a padding byte. Second, the historical
monolith exposed alternate public names including the case-sensitive
`SHOTS_RENDER()` name. OMF `ALIAS` records bind those names to already
accepted natural producers and add no code bytes.

After those fixes, the only mismatch was the call to `playperf_raise()`.
Both v346 and v375 objects use the same far-pointer FIXUPP shape and identical
LEDATA, but an ordinary split link retained a FAR call and added a segment
relocation at load `0xACF0`. `#pragma samecodeseg playperf_raise` leaves the
379-byte LEDATA unchanged and gives TLINK the segment relation needed to emit
the target five-byte `NOP; PUSH CS; CALL near` nopcall form. The extra
relocation disappears.

`gpt-web-gameplay-v375-focused-006` passes two cold builds across its
185-owner dependency closure. Its gameplay MAP contribution is exactly
`0AAF:0098 017B`, its linked slice SHA-256 is the target
`54ac4974b571dc990934e9c5ed39afb1b91206c397b67c734442fe81fd6c4448`,
and all twelve ordered MZ relocation sites match. Receipt SHA-256 is
`378aaccbe3b739577ebb0bb1b816e2abd566f3e6389c987bea80319ae29b2bcc`.

The candidate-state 254-owner aggregate
`gpt-web-gameplay-v375-aggregate-candidate-001` and promoted aggregate
`gpt-web-gameplay-v375-aggregate-final-001` both pass twice with
`failures=[]`. The final receipt SHA-256 is
`bc4aabf5e3c3f5f241f52a7946459064190bd13b9e6d95b83bb1108f7404a200`.
Strict internal-call function review also accepts the complete target-called
`gameplay_loop()` boundary using the exact owner, target near CALL at
`0x1AB6E`, raw terminal RET, and a target-prefix-attested next entry at
`0x1AD03`. This promotes 379 reviewed authored C/C++ bytes and one reviewed
function; it does not establish whole MAIN.EXE equality.
