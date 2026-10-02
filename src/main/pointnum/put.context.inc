; Standalone assembly declarations for the adjacent maintained body.
; Register-ABI point-number glyph blitter for TH04.
;
; Inputs are carried in AX (top), DX (left), and CX (glyph number). The helper
; intentionally preserves AX/DX and returns the next glyph X coordinate in DX.

	.386
	.model use16 large
	locals
RES_Y = 400
ROW_SIZE = 80
PLANE_SIZE = 32000
POINTNUM_H = 8
POINTNUM_W = 8

extrn _sPOINTNUMS:byte

blit_dots16_empty2opt_emptyopt_roll macro @@top:req, @@h:req
@@rows_after_roll equ <bx>
	cmp	@@top, (RES_Y - @@h)
	ja	short @@roll_needed
	mov	cx, @@h
	xor	@@rows_after_roll, @@rows_after_roll
	jmp	short @@blit_loop
@@roll_needed:
	mov	cx, RES_Y
	sub	cx, @@top
	mov	@@rows_after_roll, @@h
	sub	@@rows_after_roll, cx
	even
@@blit_loop:
	lodsw
	or	ah, ah
	jz	short @@blit_al?
	mov	es:[di], ax
	jmp	short @@next_row
@@blit_al?:
	or	al, al
	jz	short @@next_row
	mov	es:[di], al
@@next_row:
	add	di, ROW_SIZE
	loop	@@blit_loop
	or	@@rows_after_roll, @@rows_after_roll
	jz	short @@blit_done
	sub	di, PLANE_SIZE
	xchg	cx, @@rows_after_roll
	jmp	short @@blit_loop
@@blit_done:
endm

CIRCLE_TEXT segment word public 'CODE' use16
CIRCLE_TEXT ends
main_01 group CIRCLE_TEXT

CIRCLE_TEXT segment word public 'CODE' use16
assume cs:main_01

; TH04_NATIVE_BODY
CIRCLE_TEXT ends
end
