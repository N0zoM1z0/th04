# OP egcrect physical-boundary closure (v757)

This packet closes the last two non-reviewed authored OP boundaries without
granting source exactness.

The current th04/egcrect.cpp SHARED contribution is exactly 0xB0 bytes at OP
payload 0xE378..0xE427. Target bytes, Ghidra, current MAP ownership, and current
TC86 4.02 generated assembly agree on this physical tiling:

- egc_copy_rect_1_to_0_16 at 0xE378: 0x6F / 111-byte FAR body ending in RETF 8;
- payload 0xE3E7: one 0x90 byte emitted by pragma codestring;
- internal egc_start_copy at 0xE3E8: 0x3F / 63-byte near body ending in RET;
- payload 0xE427: one final 0x90 emitted by pragma codestring.

The internal helper has no TLINK public, which is why the old ledger left it
provisional. The current TC86 -S output supplies the missing PROC/ENDP
structure directly and reproduces db 144 after both ENDP directives.

v757 performs two cold diagnostic rebuilds. Both reproduce the complete 0xB0
linked producer, the current OP program image and MAP, and all 804 ordered MZ
relocations.

Receipt:
.analysis/reconstruction/receipt-archive/v757-op-egcrect-boundaries-receipt.json

Receipt SHA-256:
b4a66e90d66cdb0a8d4da9eff384b342cbe4462ae103711053733fe531ac613d

No decoded-function exactness is granted. The current TH04 implementation
explicitly uses inline ASM, Borland pseudo-registers, and codestring NOPs to
force target code shape. The receipt therefore labels its source credit
diagnostic-only.

After this review all 93 authored OP function candidates have reviewed physical
boundaries. The OP acceptance count remains 85/93.
