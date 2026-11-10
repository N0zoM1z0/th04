# TH04 MAINE SCORE EGC helper closure (v834)

v834 promotes the 67-byte SCORE `_egc_start_copy_inlined` helper at payload
`0xCBB0`.

The maintained source removes `_outportb_` and `keep_0`. Its hardware behavior
uses bounded PC-98 primitives whose complete 62-byte core independently occurs
in TH04 MAIN and TH05 MAIN release targets. Two cold TC4.02/TLINK MAINE builds
reproduce the complete `0xB30` SCORE CODE and the helper raw-zero.

The only object-format delta removes the decomp-only `keep_0(0)` `_address_0`
linker-zero fixup. Final MAINE bytes and all 559 ordered MZ relocations remain
identical.

Canonical replay checks 71/71 current MAINE accepted slices raw-zero.
Packed-file and literal original-source claims remain separate.
