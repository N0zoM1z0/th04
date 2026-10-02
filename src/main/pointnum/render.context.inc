; Standalone assembly declarations for the adjacent maintained body.
; Point-number renderer for TH04.
;
; The width of the currently rendered number is intentionally written into the
; immediate operand of @@set_width. This code-owned state is part of the target
; behavior and is kept symbolic through the assembler label rather than encoded
; as a target-derived address or byte sequence.

	.186
	.model use16 large
	locals
GRAM_400 = 0A800h
PLAYFIELD_LEFT = 32
PLAYFIELD_TOP = 16
POINTNUM_H = 8
POINTNUM_W = 8
POINTNUM_TIMES_2_W = 16
POINTNUM_TIMES = 4
POINTNUM_TIMES_2 = 5
POINTNUM_DIGITS = 4

Point struc
	x dw ?
	y dw ?
Point ends

pointnum_t struc
	PN_flag db ?
	PN_age db ?
	PN_center_cur Point <?>
	PN_center_prev_y dw ?
	PN_digits_lebcd db POINTNUM_DIGITS dup(?)
	PN_width dw ?
	PN_times_2 db ?
	db ?
pointnum_t ends

extrn _pointnums_alive:word
extrn _pointnum_first_yellow_alive:word
extrn _pointnums:byte
extrn _sPOINTNUMS:byte
extrn SCROLL_SUBPIXEL_Y_TO_VRAM_SEG1:near
extrn @pointnum_put:near

CIRCLE_TEXT segment word public 'CODE' use16
CIRCLE_TEXT ends
main_01 group CIRCLE_TEXT

CIRCLE_TEXT segment word public 'CODE' use16
assume cs:main_01

; TH04_NATIVE_BODY
CIRCLE_TEXT ends
end
