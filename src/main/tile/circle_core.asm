; TH04 CIRCLE_TEXT stage-tile invalidation and redraw core.
;
; Independent TH04/TH05 target comparison preserves the same low-level
; REP/LOOP/segment-register producer architecture. Legal TC4J 4.02 probes do
; not emit these forms from ordinary C++ loops, __memset__(), or __memcpy__().
; This source therefore records an evidence-backed original-style assembler
; owner rather than forcing an ABI or embedding target bytes.

.386
.model use16 large _TEXT
include ReC98.inc
include th04/th04.inc
include th01/math/subpixel.inc
include th04/main/tile/tile.inc

TILES_MEMORY_X = 512 / TILE_W

extrn _tile_invalidate_box:Point
extrn _invalidate_left_x_tile:word
extrn _page_back:byte
extrn _scroll_line_on_page:word
extrn _halftiles_dirty:byte
extrn _halftiles_dirty_end:byte
extrn _tile_ring:word
extrn _std_seg:word
extrn _map_seg:word
extrn _TILE_SECTION_OFFSETS:word
extrn _scroll_line:word
extrn byte_25104:byte
extrn word_25105:word
extrn word_25107:word
extrn word_25109:word
extrn @egc_start_copy_noframe$qv:near
extrn EGC_OFF:far

CIRCLE_TEXT segment word public 'CODE' use16
CIRCLE_TEXT ends
main_01 group CIRCLE_TEXT

CIRCLE_TEXT segment word public 'CODE' use16
assume cs:main_01
public sub_BAEE
; void pascal near tiles_invalidate_around(Point center);
public TILES_INVALIDATE_AROUND
tiles_invalidate_around proc near
arg_bx	near, @center:dword

	mov	dx, _tile_invalidate_box.x
	shr	dx, 1
	mov	ax, @center.x
	sar	ax, 4
	sub	ax, dx
	cmp	ax, PLAYFIELD_W
	jl	short @@left_edge_left_of_playfield?

@@outside_playfield:
	ret_bx
; ---------------------------------------------------------------------------

@@left_edge_left_of_playfield?:
	mov	cx, ax
	or	ax, ax
	js	short @@right_edge_left_of_playfield?
	and	ax, (TILE_W - 1)

@@right_edge_left_of_playfield?:
	add	ax, _tile_invalidate_box.x
	dec	ax
	js	short @@outside_playfield
	sar	cx, 4
	jns	short @@check_y
	xor	cx, cx

@@check_y:
	mov	_invalidate_left_x_tile, cx
	shr	ax, 4
	inc	ax
	mov	cx, ax	; CX = number of horizontal tiles to invalidate
	mov	dx, _tile_invalidate_box.y
	sar	dx, 1
	mov	ax, @center.y
	sar	ax, 4
	add	ax, TILE_H
	sub	ax, dx
	jns	short @@bottom_below_playfield?
	mov	dx, _tile_invalidate_box.y
	add	dx, ax
	or	dx, dx
	jle	short @@outside_playfield

@@bottom_below_playfield?:
	cmp	ax, PLAYFIELD_H + TILE_H
	jge	short @@outside_playfield
	mov	bh, 0
	mov	bl, _page_back
	add	bx, bx
	add	ax, _scroll_line_on_page[bx]
	jns	short @@scroll_wrap?
	add	ax, RES_Y
	jmp	short @@invalidate
; ---------------------------------------------------------------------------

@@scroll_wrap?:
	cmp	ax, RES_Y
	jl	short @@invalidate
	sub	ax, RES_Y

@@invalidate:
	mov	dx, ax
	and	dx, 7
	add	dx, _tile_invalidate_box.y	; DX = Invalidated height in pixels
	mov	bx, dx
	add	bx, ax
	shr	ax, 3
	shl	ax, 5	; AX *= TILES_MEMORY_X
	push	si
	push	di
	push	ds
	pop	es
	assume es:_DATA
	mov	di, ax
	add	di, _invalidate_left_x_tile
	add	di, offset _halftiles_dirty
	mov	si, TILES_MEMORY_X
	sub	si, cx	; SI = row stride
	mov	ah, cl
	mov	al, 1
	cmp	bx, RES_Y
	jl	short @@set_nowrap
	mov	bx, offset _halftiles_dirty_end

@@set_wrap:
	mov	cl, ah
	rep stosb
	sub	dx, TILE_FLAG_H
	add	di, si
	cmp	di, bx
	jl	short @@set_wrap
	sub	di, (TILES_MEMORY_X * TILE_FLAGS_Y)

@@set_nowrap:
	mov	cl, ah
	rep stosb
	add	di, si
	sub	dx, TILE_FLAG_H
	jg	short @@set_nowrap
	pop	di
	pop	si
	ret_bx
tiles_invalidate_around endp
public TILES_FILL_INITIAL
tiles_fill_initial	proc near

@@section	equ <bx>
@@std_seg	equ <fs>

	push	di
	push	si
	push	ds
if GAME eq 5
	mov	@@section, _std_map_section_p
	sub	@@section, (TILE_ROWS_PER_SECTION - 1)
else
	xor	@@section, @@section
endif
	mov	di, offset _tile_ring
	add	di, TILES_MEMORY_X * (TILES_Y - 1) * word
	xor	dx, dx
	mov	ax, ds
	mov	es, ax
	assume es:_DATA
	mov	ax, _std_seg
	mov	@@std_seg, ax
	mov	ax, _map_seg
	mov	ds, ax
	mov	al, (TILES_Y / TILE_ROWS_PER_SECTION)

@@section_in_screen_loop:
	xor	dx, dx
	mov	dl, @@std_seg:[@@section]
	mov	si, dx
	if GAME ne 5
		; Since TILE_SECTION_OFFSETS is a 16-bit array, we have to double the
		; section ID read from the .STD …except that in TH05's version of the
		; format, we don't, and simply assume that the .STD file's section IDs
		; already come pre-multiplied by the element size of the lookup table.
		; Way to go. Making the format more annoying just to save a single
		; instruction for a table lookup that is pointless to begin with.
		add	si, si
	endif
	mov	si, es:_TILE_SECTION_OFFSETS[si]
	add	si, ((TILE_ROWS_PER_SECTION - 1) * TILES_MEMORY_X * word)
	mov	ah, TILE_ROWS_PER_SECTION

@@row_in_section_loop:
	mov	cx, (TILES_X / 2)
	rep movsd
	sub	di, ((TILES_MEMORY_X + TILES_X) * word)
	sub	si, ((TILES_MEMORY_X + TILES_X) * word)
	dec	ah
	jnz	short @@row_in_section_loop
	inc	@@section
	dec	al
	jnz	short @@section_in_screen_loop
	pop	ds
	pop	si
	pop	di
	retn
tiles_fill_initial	endp
	even

; =============== S U B	R O U T	I N E =======================================


sub_BAEE	proc near
		push	bp
		push	si
		push	di
		mov	ax, GRAM_400
		mov	es, ax
		assume es:nothing
		mov	dx, _scroll_line
		mov	ax, 4
		mov	cx, dx
		shl	cx, 6
		add	ax, cx
		shr	cx, 2
		add	ax, cx
		mov	word_25107, ax
		mov	ax, dx
		shr	ax, 4
		shl	ax, 6
		mov	bx, ax
		mov	si, _tile_ring[bx]
		mov	bx, dx
		and	bx, 0Fh
		mov	cx, bx
		shl	cx, 6
		mov	dx, cx
		shr	cx, 2
		add	dx, cx
		mov	word_25105, dx
		xor	ch, ch
		mov	cl, byte_25104
		mov	bh, bl
		add	bl, cl
		cmp	bl, 10h
		jbe	short loc_BB49
		sub	bl, 10h
		mov	cl, 10h
		sub	cl, bh
		mov	dh, bl
		jmp	short loc_BB4B
; ---------------------------------------------------------------------------

loc_BB49:
		xor	dh, dh

loc_BB4B:
		mov	dl, TILES_X
		mov	word_25109, cx

loc_BB51:
		mov	di, word_25107
		add	si, word_25105
		add	word_25107, 2
		mov	bl, dh

loc_BB60:
		mov	bp, es:[si]
		mov	es:[di], bp
		add	si, ROW_SIZE
		add	di, ROW_SIZE
		loop	loc_BB60
		or	bl, bl
		jz	short loc_BB8F
		mov	cl, bl
		mov	bx, ax
		add	bx, 40h
		cmp	di, PLANE_SIZE
		jb	short loc_BB87
		sub	di, PLANE_SIZE
		sub	bx, (TILES_MEMORY_X * TILES_Y * word)

loc_BB87:
		mov	si, _tile_ring[bx]
		xor	bx, bx
		jmp	short loc_BB60
; ---------------------------------------------------------------------------

loc_BB8F:
		mov	cx, word_25109
		add	ax, 2
		mov	bx, ax
		mov	si, _tile_ring[bx]
		dec	dl
		jnz	short loc_BB51
		pop	di
		pop	si
		pop	bp
		retn
sub_BAEE	endp

public @TILES_REDRAW_INVALIDATED$QV
@tiles_redraw_invalidated$qv proc near
	push	si
	push	di
	call	@egc_start_copy_noframe$qv
	mov	ax, GRAM_400
	mov	es, ax
	assume es:nothing
	mov	bx, offset _halftiles_dirty[TILES_MEMORY_X * (TILE_FLAGS_Y - 1)]
	mov	di, ((RES_Y - TILE_FLAG_H) * ROW_SIZE) + PLAYFIELD_VRAM_LEFT
	mov	dh, TILE_FLAGS_Y
	mov	si, TILES_MEMORY_X * (TILES_Y - 1) * 2

@@start_row:
	mov	dl, TILES_X

@@dirty?:
	cmp	byte ptr [bx], 0
	jz	short @@next_tile_in_row
	push	si
	mov	byte ptr [bx], 0
	mov	si, _tile_ring[si]
	test	dh, 1
	jnz	short @@redraw
	add	si, TILE_FLAG_H * ROW_SIZE

@@redraw:
	mov	cx, TILE_FLAG_H

@@blit_tile_redraw_lines:
	mov	ax, es:[si]
	mov	es:[di], ax
	add	si, ROW_SIZE
	add	di, ROW_SIZE
	loop	@@blit_tile_redraw_lines
	sub	di, TILE_FLAG_H * ROW_SIZE
	pop	si

@@next_tile_in_row:
	add	di, 2
	add	si, 2
	inc	bx
	dec	dl
	jnz	short @@dirty?
	test	dh, 1
	jnz	short @@previous_row
	add	si, (TILES_MEMORY_X * 2)

@@previous_row:
	sub	si, (TILES_MEMORY_X * 2) + (TILES_X * 2)
	dec	dh
	sub	bx, TILES_X + TILES_MEMORY_X
	sub	di, (TILES_X * 2) + (TILE_FLAG_H * ROW_SIZE)
	jge	short @@start_row
	call	egc_off
	pop	di
	pop	si
	retn
@tiles_redraw_invalidated$qv endp

CIRCLE_TEXT ends
end
