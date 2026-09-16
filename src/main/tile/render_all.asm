; TH04 MAI_TEXT stage-tile full renderer and EGC setup.
;
; Independent TH04/TH05 targets preserve the same low-level register/LOOP and
; direct-port architecture. Legal TC4J probes do not reproduce these forms.
; This probe uses symbolic original-style assembly and contains no target bytes.

.386
.model use16 large _TEXT
include ReC98.inc
include th04/th04.inc
include th04/main/tile/tile.inc
include th01/hardware/egc.inc

TILES_MEMORY_X = 512 / TILE_W

extrn _tile_ring:word
extrn EGC_OFF:far

MAI_TEXT segment word public 'CODE' use16
MAI_TEXT ends
main_01 group MAI_TEXT

MAI_TEXT segment word public 'CODE' use16
assume cs:main_01

public @TILES_RENDER_ALL$QV
@tiles_render_all$qv proc near
	push	si
	push	di
	call	@egc_start_copy_noframe$qv
	mov	di, ((RES_Y - TILE_H) * ROW_SIZE) + PLAYFIELD_VRAM_LEFT
	mov	bx, offset _tile_ring[TILES_MEMORY_X * (TILES_Y - 1) * 2]
	mov	ax, GRAM_400
	mov	es, ax
	assume es:nothing

@@start_row:
	mov	dl, TILES_X
@@next_tile:
	mov	si, [bx]
	mov	cx, TILE_H
	nop
@@line:
	mov	ax, es:[si]
	mov	es:[di], ax
	add	si, ROW_SIZE
	add	di, ROW_SIZE
	loop	@@line
	sub	di, (TILE_H * ROW_SIZE) - TILE_VRAM_W
	add	bx, 2
	dec	dl
	jnz	short @@next_tile
	sub	bx, (TILES_MEMORY_X + TILES_X) * 2
	sub	di, (TILE_H * ROW_SIZE) + (TILE_VRAM_W * TILES_X)
	jge	short @@start_row
	call	EGC_OFF
	pop	di
	pop	si
	retn
@tiles_render_all$qv endp

public @egc_start_copy_noframe$qv
@egc_start_copy_noframe$qv proc near
	EGC_START_COPY_INLINED
	retn
@egc_start_copy_noframe$qv endp
	nop

MAI_TEXT ends
end
