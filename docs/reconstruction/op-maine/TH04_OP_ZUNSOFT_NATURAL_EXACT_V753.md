# OP ZUNSOFT current natural-C++ owner exact replay (v753)

The older boundary ledger still attributed the four ZUNSOFT entries to the
historical target-derived th04_op.asm owner. That attribution is no longer true
for the current pinned reconstruction snapshot.

The current v489 MAP contains a zero-sized historical th04_op.asm contribution
at OP_MUSIC_TEXT 1A74:1305 and, at the same address, a real 0x490-byte
th04/zunsoft.cpp contribution. The current pinned C++ implementation contains
all four functions as ordinary TC86 C++ and uses no keep_0,
optimization_barrier, emitted opcode bytes, inline target assembly, or
pseudo-register forcing.

Fresh target/current-TU review closes the physical layout as:

- ZUNSOFT_PYRO_NEW at payload 0xBA45: 0x84 / 132-byte body;
- ZUNSOFT_UPDATE_AND_RENDER at 0xBAC9: 0x12B / 299-byte body;
- ZUNSOFT_PALETTE_UPDATE_AND_SHOW at 0xBBF4: 0x41 / 65-byte body;
- zunsoft_animate at 0xBC35: 0x26F / 623-byte body;
- immediately after zunsoft_animate, payload 0xBEA4..0xBED4 is a 0x31-byte
  compiler-owned auxiliary extent: one alignment byte, twelve word case
  values, and twelve word jump offsets for the sparse frame switch.

Ghidra already closes the first three bodies contiguously. Its zunsoft_animate
auto-function exposes only 522 reachable addresses across the correct 0x26F
physical span. Current TC86 4.02 generated assembly supplies the matching
PROC/ENDP and sparse-switch structure. The legacy TASM PROC names for the
palette helper and animate remain useful boundary corroboration, but they are
not source ownership.

Maintained source:

- src/op/music/zunsoft_pyro_new.inl
- src/op/music/zunsoft_update_and_render.inl
- src/op/music/zunsoft_palette_update_and_show.inl
- src/op/music/zunsoft_animate.inl

v753 injects only these four maintained bodies into the pinned current
th04/zunsoft.cpp translation unit. Two independent TC86/TLINK cold rounds
reproduce every reviewed body, the 0x31 compiler auxiliary extent, the complete
0x490 linked ZUNSOFT producer, the current OP program image, MAP, and all 804
ordered MZ relocations. The rebuilt OMF OP_MUSIC_TEXT CODE stream also equals
the pinned current C++ object in both rounds.

Focused receipt:
.analysis/reconstruction/receipt-archive/v753-op-zunsoft-natural-focused-receipt.json

Focused receipt SHA-256:
f9aa22cf08ebc19da42631526e79043ec30185a21b8b6323aecb6455460299e2

The in-memory v754 pre-acceptance aggregate passed 85/85 OP decoded slices.
After all four rows were written into the checked-in acceptance ledger,
canonical v755 again passed 85/85.

Canonical aggregate receipt:
.analysis/reconstruction/receipt-archive/v755-op-zunsoft-natural-canonical-receipt.json

Canonical aggregate receipt SHA-256:
14a85e9330db6b1728bf7264ab5e8eebf608deb54a5d9dc427d6c17fd2a146f2

This supersedes the live-ledger source attribution of these four entries to
target-derived th04_op.asm. Historical TASM evidence is retained only as
corroboration of physical boundaries. This does not claim packed-file or
whole-OP exactness.
