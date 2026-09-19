# MAIN enemy-script natural dispatcher v330

The hash-attested Japanese MAIN.EXE dispatcher and its switch table own
B4M_UPDATE_TEXT `13A9:1B4D..21DC`, MZ load `0x155DD..0x15C6C`, target file
`0x16DDD..0x1746C`. The 1,680-byte target extent has SHA-256
`b38e0b210ee7e7d2abb08056d1bbb97396466925acc988de42a06bd67a4ea100`.
It contains a 1,392-byte near body and a 288-byte, 144-word switch table.
The target's pristine-retail provenance is still unproved.

The maintained [C++ VM](../../src/main/enemy/script_update.cpp) uses
TC4J's `__es` pointer to read stage bytecode while preserving the target's
separate DI pointer addition. It implements the target-observed movement,
bullet-template, timing, loop, clipping, animation, sound, position, and tile
instruction branches. The default path deliberately retains the target's
uninitialized duration/advance behavior; that path remains semantically
uncertain and needs runtime validation. Source SHA-256:
`6976850412439ab34dfcf75f6ff1103afbd7fcbd9f7db4a56d1c5224dcd75226`.

Replay:

    python3 scripts/probes/replay_th04_enemy_script_natural.py \
      --output-dir .analysis/reconstruction/probes/v342-enemy-es-explicit-001

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
target bytes.

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

The v342 private compiler receipt SHA-256 is
`e5ace2d81d9bfcecc1338eaf7b2baa21d9b3d1509bb0a3250f74790ef67549f1`.
All 49 physical blocks now have the target size and order. The complete 0x690
owner remains source-present because raw bytes, MAP placement, the three
ordered MZ relocations, runtime behavior, and cold aggregate replay are open.
