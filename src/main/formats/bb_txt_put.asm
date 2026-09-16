; TH04 text-dissolve .BB blitter.
;
; The caller supplies left/top in AX/DX, sprite in CX, and the destination VRAM
; segment in ES. Independent TH05 target code preserves the same producer modulo
; the linked bb_txt_seg word. Typed TC4J expands the implicit-register/string
; architecture, so maintain this as symbolic irreducible/original-style assembly.

public @bb_txt_put_8_raw$quiui
@bb_txt_put_8_raw$quiui proc near
	@@left equ <ax>
	@@top equ <dx>
	@@sprite equ <cx>
	@@rows_after_roll equ <ax>
	@@top_in equ <bx>

	push	si
	push	di
	push	ds
	mov	@@top_in, @@top
	sar	ax, 3
	shl	dx, 6
	add	ax, dx
	shr	dx, 2
	add	ax, dx
	mov	di, ax
	shl	@@sprite, 7
	mov	si, @@sprite
	mov	ax, _bb_txt_seg
	mov	ds, ax
	cmp	@@top_in, (RES_Y - BB_TXT_H)
	ja	short @@roll_needed
	mov	cx, BB_TXT_H
	even

@@no_roll:
	lodsd
	or	eax, eax
	jz	short @@skip_blank
	stosd
	add	di, (ROW_SIZE - BB_TXT_VRAM_W)
	loop	@@no_roll
	jmp	short @@return

@@skip_blank:
	add	di, ROW_SIZE
	loop	@@no_roll
	jmp	short @@return

@@roll_needed:
	mov	@@rows_after_roll, BB_TXT_H
	mov	cx, RES_Y
	sub	cx, @@top_in
	sub	@@rows_after_roll, cx

@@roll_first:
	movsd
	add	di, (ROW_SIZE - BB_TXT_VRAM_W)
	loop	@@roll_first
	sub	di, PLANE_SIZE
	mov	cx, @@rows_after_roll

@@roll_second:
	movsd
	add	di, (ROW_SIZE - BB_TXT_VRAM_W)
	loop	@@roll_second

@@return:
	pop	ds
	pop	di
	pop	si
	retn
@bb_txt_put_8_raw$quiui endp
	even
