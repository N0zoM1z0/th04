; TH04 CIRCLE_TEXT .BB tile-mask rendering and invalidation.
;
; Independent TH04/TH05 targets preserve the same BP-local, FS mask-reader,
; and bit-walk producer architecture. Legal TC4J 4.02 __seg-pointer probes use
; ES rather than FS and expand the complete natural C++ candidate. This source
; records evidence-backed irreducible/original-style symbolic assembly without
; embedding target bytes.

public @TILES_BB_PUT_RAW$QI
@tiles_bb_put_raw$qi proc near
bb_top = word ptr -6
bb_left = word ptr -4
row_tiles_left = byte ptr -2
bb_shiftreg = byte ptr -1
cel = word ptr 4
bb_seg equ <fs>
bb_off equ <di>
	enter	6, 0
	push	di
	push	GC_TDW
	mov	al, _tiles_bb_col
	mov	ah, 0
	call	grcg_setcolor pascal, ax
	mov	ax, _tiles_bb_seg
	mov	bb_seg, ax
	mov	bb_off, [bp+cel]
	shl	bb_off, 7
	mov	[bp+bb_top], PLAYFIELD_TOP
put_row_loop:
	mov	[bp+bb_left], PLAYFIELD_LEFT
	mov	[bp+row_tiles_left], TILES_X
put_byte_loop:
	mov	al, bb_seg:[bb_off]
	mov	[bp+bb_shiftreg], al
put_next_tile:
	test	[bp+bb_shiftreg], 80h
	jz	short put_skip_tile
	mov	ax, [bp+bb_left]
	mov	dx, [bp+bb_top]
if (GAME eq 5)
	cmp	_scroll_active, 0
	jz	short put_roll
endif
	add	dx, _scroll_line
put_roll:
	cmp	dx, RES_Y
	jl	short put_tile
	sub	dx, RES_Y
put_tile:
	call	@grcg_tile_bb_put_8
put_skip_tile:
	shl	[bp+bb_shiftreg], 1
	add	[bp+bb_left], TILE_W
	dec	[bp+row_tiles_left]
	jz	short put_row_next
	test	[bp+row_tiles_left], 7
	jnz	short put_next_tile
	inc	bb_off
	jmp	short put_byte_loop
put_row_next:
	add	bb_off, 2
	add	[bp+bb_top], TILE_H
	cmp	[bp+bb_top], PLAYFIELD_BOTTOM
	jb	short put_row_loop
	GRCG_OFF_CLOBBERING dx
	pop	di
	leave
	retn	2
@tiles_bb_put_raw$qi endp
	even

public @TILES_BB_INVALIDATE_RAW$QI
@tiles_bb_invalidate_raw$qi proc near
tile_center = Point ptr [bp-6]
row_tiles_remaining = byte ptr [bp-2]
inv_shiftreg = byte ptr [bp-1]
inv_cel = word ptr [bp+4]
inv_seg equ <fs>
inv_off equ <di>
	enter	6, 0
	push	di
	mov	_tile_invalidate_box, (2 shl 16) or 2
	; Preserve the target's boss-segment read rather than substituting _tiles_bb_seg.
	mov	ax, _bb_boss_seg
	mov	inv_seg, ax
	mov	inv_off, inv_cel
	shl	inv_off, 7
	mov	tile_center.y, ((TILE_H / 2) shl 4)
inv_row_loop:
	mov	tile_center.x, ((TILE_W / 2) shl 4)
	mov	row_tiles_remaining, TILES_X
inv_byte_loop:
	mov	al, inv_seg:[inv_off]
	mov	inv_shiftreg, al
inv_next_tile:
	test	inv_shiftreg, 80h
	jnz	short inv_skip_tile
	call	tiles_invalidate_around pascal, dword ptr tile_center
inv_skip_tile:
	shl	inv_shiftreg, 1
	add	tile_center.x, (TILE_W shl 4)
	dec	row_tiles_remaining
	jz	short inv_row_next
	test	row_tiles_remaining, 7
	jnz	short inv_next_tile
	inc	inv_off
	jmp	short inv_byte_loop
inv_row_next:
	add	inv_off, 2
	add	tile_center.y, (TILE_H shl 4)
	cmp	tile_center.y, (PLAYFIELD_H shl 4)
	jb	short inv_row_loop
	pop	di
	leave
	retn	2
@tiles_bb_invalidate_raw$qi endp
