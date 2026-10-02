; Standalone assembly declarations for the adjacent maintained body.
; TH04 text-dissolve .BB blitter.
;
; The caller supplies left/top in AX/DX, sprite in CX, and the destination VRAM
; segment in ES. Independent TH05 target code preserves the same producer modulo
; the linked bb_txt_seg word. Typed TC4J expands the implicit-register/string
; architecture, so maintain this as symbolic irreducible/original-style assembly.

	.386
	.model use16 large
	locals
RES_Y = 400
ROW_SIZE = 80
PLANE_SIZE = 32000
BB_TXT_H = 32
BB_TXT_VRAM_W = 4

extrn _bb_txt_seg:word

CIRCLE_TEXT segment word public 'CODE' use16
CIRCLE_TEXT ends
main_01 group CIRCLE_TEXT

CIRCLE_TEXT segment word public 'CODE' use16
assume cs:main_01

; TH04_NATIVE_BODY
	even

CIRCLE_TEXT ends
end
