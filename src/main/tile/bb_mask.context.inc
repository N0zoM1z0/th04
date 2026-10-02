; Standalone assembly declarations for the adjacent maintained body.
; TH04 CIRCLE_TEXT .BB tile-mask rendering and invalidation.
;
; Independent TH04/TH05 targets preserve the same BP-local, FS mask-reader,
; and bit-walk producer architecture. Legal TC4J 4.02 __seg-pointer probes use
; ES rather than FS and expand the complete natural C++ candidate. This source
; records evidence-backed irreducible/original-style symbolic assembly without
; embedding target bytes.

.386
.model use16 large
locals
GRAM_400 = 0A800h
RES_Y = 400
PLAYFIELD_LEFT = 32
PLAYFIELD_TOP = 16
PLAYFIELD_W = 384
PLAYFIELD_H = 368
PLAYFIELD_BOTTOM = (PLAYFIELD_TOP + PLAYFIELD_H)
TILE_W = 16
TILE_H = 16
TILES_X = 24
GC_TDW = 80h

Point struc
	x dw ?
	y dw ?
Point ends

extrn _tiles_bb_col:byte
extrn _tiles_bb_seg:word
extrn _bb_boss_seg:word
extrn _tile_invalidate_box:byte
extrn _scroll_active:byte
extrn _scroll_line:word
extrn @grcg_tile_bb_put_8:near
TILES_INVALIDATE_AROUND procdesc pascal near center:dword
GRCG_SETCOLOR procdesc pascal far mode:word, col:word

GRCG_OFF_CLOBBERING macro reg:req
	xor	al, al
	mov	reg, 7Ch
	out	reg, al
endm

CIRCLE_TEXT segment word public 'CODE' use16
CIRCLE_TEXT ends
main_01 group CIRCLE_TEXT
CIRCLE_TEXT segment word public 'CODE' use16
assume cs:main_01

; TH04_NATIVE_BODY
CIRCLE_TEXT ends
end
