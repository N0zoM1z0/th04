# MAIN enemy-script natural dispatcher v330

The hash-attested Japanese MAIN.EXE dispatcher and its switch table own
B4M_UPDATE_TEXT `13A9:1B4D..21DC`, MZ load `0x155DD..0x15C6C`, target file
`0x16DDD..0x1746C`. The 1,680-byte target extent has SHA-256
`b38e0b210ee7e7d2abb08056d1bbb97396466925acc988de42a06bd67a4ea100`.
It contains a 1,392-byte near body and a 288-byte, 144-word switch table.
The target's pristine-retail provenance is still unproved.

The maintained [C++ VM](../../../src/main/enemy/script_update.cpp) uses
TC4J's `__es` pointer to read stage bytecode while preserving the target's
separate DI pointer addition. It implements the target-observed movement,
bullet-template, timing, loop, clipping, animation, sound, position, and tile
instruction branches. The default path deliberately retains the target's
uninitialized duration/advance behavior; that path remains semantically
uncertain and needs runtime validation. Source SHA-256:
`35f5c69e8c86b7886712b50461a6c1623ab7b123efdb16a10f3a774b510ff8a1`.

Replay:

    python3 scripts/probes/replay_th04_enemy_script_natural.py \
      --output-dir .analysis/reconstruction/probes/v343-enemy-dispatch-compound-div-001

The pinned TC4J 4.02 and frozen compiler snapshot produce a valid OMF object
with B4M_UPDATE_TEXT LEDATA spans `0..1023` and `1024..1679`. The resulting
1,680 CODE bytes contain a 1,392-byte executable body and a 288-byte table.
The first 42 entry bytes have the same opcodes as the target after masking
two DS addresses, one conditional branch displacement, and one table address.
The candidate's 144 table entries have **exactly the same partition into 49
destination groups** as the target, and those 49 groups now occur in exactly
the same physical order. Every opcode shares a destination with the same other
opcodes in both tables. Declaration order also reproduces the target
`duration`/`advance` BP-local offsets. This compares table structure and
compiler layout, not literal destination offsets.

Opcode `0x2C` uses separate multiply, divide, and add/subtract assignments.
That source shape recovers 30 target bytes. The target also reloads the
`temp` local from `[bp-4]` before both divisions; declaring that local
`volatile` makes TC4J emit both three-byte reloads without assembly or copied
target bytes. Writing the two divisions as `temp /= 32` also makes TC4J load
the divisor before reloading `temp`, reproducing the target order at both
sites without changing the arithmetic.

Routing opcodes `0x09`, `0x2C`, `0x86`, and `0x80/81` through their target
shared tails, placing the `0x89` and `0x8A/8B` assignments in target order,
and making the `0x8B` script-word additions explicitly signed reproduces the
target size for 48 of the 49 physical switch blocks. The remaining block,
opcode `0x20`, is two bytes short: its instructions otherwise agree in shape,
but the target surrounds two indirect calls with `PUSH ES` and `POP ES`.

The v340 target Oracle attests this pair and the equivalent pair in the TH04
aim helper. It also finds three analogous save/call/restore sites in the
independently hash-attested TH05 MAIN target. A masked TH03 target/compiler
comparison additionally locates the same handwritten ES-save source idiom in
an enemy velocity helper. This evidence supports classifying the two inline
instructions as handwritten ABI preservation. The target evidence receipt
SHA-256 is
`8f4529c1de197a4d97561828ac5fea3b19d8588bb950af014627df1480f4424a`.
This cross-game evidence supplies no exact credit by itself.

The v343 compiler receipt SHA-256 is
`c8d64061f96a214f35165aa3716187469f6128bddb0f7dfcf8ac899b8e58b050`.
All 49 physical blocks have the target size and order.

Strict replay:

    python3 scripts/replay_th04_main_exact_units.py \
      --unit th04-main-enemy-script-dispatch-v328 \
      --run-id gpt-5-6-sol-v343-enemy-dispatch-candidate-003

The focused A/B receipt has SHA-256
`7cc714a84a331708d1faabc31e280e57f5a751d95baa09e9a29e4dc7e2e5d8bb`.
Both cold builds produce valid deterministic OMF, the exact
`13A9:1B4D 0690` MAP contribution, ordered relocation sites `0x15AE2` then
`0x15A00`, and zero raw differences across the 1,392-byte body and 288-byte
table. The 251-owner aggregate
`gpt-5-6-sol-v343-enemy-dispatch-aggregate-final-004` also passes twice; its
receipt SHA-256 is
`8addd30b7e420cab0bf1709fc3d275310c80fd4e5b4eed2debd8317813f17898`.
The complete 0x690 owner is therefore exact. Runtime validation of the
target-preserved uninitialized default path remains open.
