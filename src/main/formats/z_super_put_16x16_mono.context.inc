; Standalone assembly declarations for the adjacent maintained body.
; TH04 16x16 one-plane super sprite blitter.
;
; The target ABI consumes top in AX and left in CX while receiving only patnum
; on the Pascal stack. Its DS/ES string-register implementation is not reproduced
; by a truthful typed TC4J function, so preserve the low-level producer as
; symbolic irreducible/original-style assembly.

.386
.model use16 large
locals
ROW_SIZE = 80
extrn _super_patdata:word

CIRCLE_TEXT segment word public 'CODE' use16
CIRCLE_TEXT ends
main_01 group CIRCLE_TEXT
CIRCLE_TEXT segment word public 'CODE' use16
assume cs:main_01

; TH04_NATIVE_BODY
	even
CIRCLE_TEXT ends
end
