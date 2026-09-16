; TH04 16x16 four-plane .MPN image renderer.
;
; Target/raw/TASM review closes this game-owned FAR routine between JS_SENSE and
; the MASTER.LIB BGM block. Independent TH05 target code preserves the same
; 16-row MOVSW/LOOP plane-copy architecture, while legal TC4J 4.02 far-pointer
; source expands to ES-only accesses and ordinary loop control. Keep this as
; evidence-backed original-style symbolic assembly rather than manufacturing a
; C++ spelling for the target's DS/FS/GS/ES register allocation.

sub_3680 proc far
mpn_arg_image = word ptr 6
mpn_arg_slot = word ptr 8
mpn_arg_top = word ptr 0Ah
mpn_arg_left = word ptr 0Ch

	push	bp
	mov	bp, sp
	push	si
	push	di
	push	ds

	; VRAM word offset = (left / 8) + (top * ROW_SIZE).
	mov	ax, [bp+mpn_arg_left]
	sar	ax, 3
	mov	dx, [bp+mpn_arg_top]
	shl	dx, 6
	add	ax, dx
	shr	dx, 2
	add	ax, dx
	mov	di, ax

	; mpn_t is exactly 64 bytes in TH04.
	mov	bx, [bp+mpn_arg_slot]
	shl	bx, 6
	mov	ax, [bp+mpn_arg_image]
	cmp	ax, _mpn_slots[bx].MPN_count
	ja	short mpn_render_done

	; One image is four 16-word planes (0x80 bytes). Start at the green
	; plane so the B/R/G pass can use SI-0x40, SI-0x20, and MOVSW.
	shl	ax, 7
	mov	si, ax
	add	si, 40h
	mov	dx, word ptr _mpn_slots[bx].MPN_images+2
	mov	ds, dx

	mov	ax, SEG_PLANE_B
	mov	fs, ax
	assume fs:nothing
	mov	ax, SEG_PLANE_R
	mov	gs, ax
	assume gs:nothing
	mov	ax, SEG_PLANE_G
	mov	es, ax
	assume es:nothing
	mov	cx, TILE_H

mpn_render_brg_row:
	mov	ax, [si-40h]
	mov	fs:[di], ax
	mov	ax, [si-20h]
	mov	gs:[di], ax
	movsw
	add	di, (ROW_SIZE - word)
	loop	mpn_render_brg_row

	; Rewind to the top row; SI now points at the effect plane.
	sub	di, (TILE_H * ROW_SIZE)
	mov	ax, SEG_PLANE_E
	mov	es, ax
	assume es:nothing
	mov	cx, TILE_H

mpn_render_e_row:
	movsw
	add	di, (ROW_SIZE - word)
	loop	mpn_render_e_row

mpn_render_done:
	pop	ds
	pop	di
	pop	si
	pop	bp
	retf	8
sub_3680 endp
