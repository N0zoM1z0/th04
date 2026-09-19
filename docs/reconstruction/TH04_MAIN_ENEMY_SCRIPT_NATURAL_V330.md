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
`73bcfcc36ffbb4c7d21a4de932402c8d55cd6fb85bbe21915c0840751ba9beef`.

Replay:

    python3 scripts/probes/replay_th04_enemy_script_natural.py \
      --output-dir .analysis/reconstruction/probes/v333-enemy-script-natural-002

The pinned TC4J 4.02 and frozen compiler snapshot produce a valid OMF object
with B4M_UPDATE_TEXT LEDATA spans `0..1023` and `1024..1633`. The resulting
1,634 CODE bytes contain a 1,346-byte executable body and a 288-byte table.
The first 42 entry bytes have the same opcodes as the target after masking
two DS addresses, one conditional branch displacement, and one table address.
The candidate's 144 table entries have **exactly the same partition into 49
destination groups** as the target, and those 49 groups now occur in exactly
the same physical order. Every opcode shares a destination with the same other
opcodes in both tables. Declaration order also reproduces the target
`duration`/`advance` BP-local offsets. This compares table structure and
compiler layout, not literal destination offsets.

The private receipt SHA-256 is
`6548866c6a36a4512614d5a3ebf5250c8e2af08723a51fc25a4536bf3901143d`.
The candidate executable body is 46 bytes shorter than the target before
linking (1,346 versus 1,392). The complete 0x690 owner is now source-present,
but raw bytes, MAP placement, ordered MZ relocations, runtime behavior, and
cold aggregate replay remain open. The next matching step is to classify
compiler differences inside the 49 branch bodies without changing the
verified 144-case destination partition.
