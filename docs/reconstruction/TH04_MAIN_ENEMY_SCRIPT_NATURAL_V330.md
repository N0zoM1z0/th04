# MAIN enemy-script natural dispatcher v330

The hash-attested Japanese MAIN.EXE dispatcher and its switch table own
B4M_UPDATE_TEXT `13A9:1B4D..21DC`, MZ load `0x155DD..0x15C6C`, target file
`0x16DDD..0x1746C`. The 1,680-byte target extent has SHA-256
`b38e0b210ee7e7d2abb08056d1bbb97396466925acc988de42a06bd67a4ea100`.
It contains a 1,392-byte near body and a 288-byte, 144-word switch table.
The target's pristine-retail provenance is still unproved.

The maintained [natural C++ VM](../../src/main/enemy/script_update.cpp) uses
TC4J's `__es` pointer to read stage bytecode while preserving the target's
separate DI pointer addition. It implements the target-observed movement,
bullet-template, timing, loop, clipping, animation, sound, position, and tile
instruction branches. The default path deliberately retains the target's
uninitialized duration/advance behavior; that path remains semantically
uncertain and needs runtime validation. Source SHA-256:
`980382bba545775e5b610f235a9a3a388781a3e6141b0565c7e77e77df12ad2`.

Replay:

    python3 scripts/probes/replay_th04_enemy_script_natural.py \
      --output-dir .analysis/reconstruction/probes/v335-enemy-script-volatile-002

The pinned TC4J 4.02 and frozen compiler snapshot produce a valid OMF object
with B4M_UPDATE_TEXT LEDATA spans `0..1023` and `1024..1669`. The resulting
1,670 CODE bytes contain a 1,382-byte executable body and a 288-byte table.
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

The private receipt SHA-256 is
`3a8aabdaa7cdaadef232c2822f85257e085150237a44d06fb4652a53020dbce1`.
The candidate executable body is 10 bytes shorter than the target before
linking (1,382 versus 1,392). The complete 0x690 owner is source-present,
but raw bytes, MAP placement, ordered MZ relocations, runtime behavior, and
cold aggregate replay remain open. The next matching step is to classify
compiler differences inside the 49 branch bodies without changing the
verified 144-case destination partition.
