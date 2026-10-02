; Standalone assembly declarations for the adjacent maintained body.
; TH04 option-laser raw blitter.
;
; This routine consumes left/top/cel/height in AX/DX/BX/SI, rotates the
; one-byte laser mask into AX, and writes directly through ES with wrapped
; STOSB/STOSW loops. A bounded natural TC4J probe preserves the external ABI
; but expands this register/string-loop architecture substantially, so this is
; maintained as evidence-backed irreducible/original-style symbolic assembly.

.386
.model use16 large
locals
GRAM_400 = 0A800h
RES_Y = 400
ROW_SIZE = 80
PLANE_SIZE = 32000
extrn _SHOT_LASER_DOTS:byte

MAIN_01_TEXT segment word public 'CODE' use16
MAIN_01_TEXT ends
main_01 group MAIN_01_TEXT
MAIN_01_TEXT segment word public 'CODE' use16
assume cs:main_01

; TH04_NATIVE_BODY
    even
MAIN_01_TEXT ends
end
