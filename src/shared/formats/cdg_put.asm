	.386
	.model use16 large SHARED
	locals

; TH04 640-pixel PC-98 planar VRAM and CDG slot layout. The complete linked
; module is checked independently against MAIN, OP, and MAINE targets.
; File rows run bottom-to-top; each row is copied left-to-right in dwords.
; The mask clears destination bits through GRCG, then B/R/G/E source planes
; are ORed into those cleared positions. Color zero can therefore be opaque.
; Color bits outside the mask must already be zero in the source asset.
; The caller must provide a combined mask/color slot, valid placement and
; 32-pixel row geometry. This routine has no general rectangle clipping.
ROW_SIZE = 80
SEG_PLANE_B = 0A800h
SEG_PLANE_G = 0B800h
SEG_PLANE_E = 0E000h
SEG_PLANE_DIST_BRG = 800h
SEG_PLANE_DIST_E = 2800h
GC_RMW = 0C0h
CDG_SLOT_COUNT = 64

cdg_t struc
	CDG_plane_size dw ?
	pixel_w dw ?
	pixel_h dw ?
	offset_at_bottom_left dw ?
	vram_dword_w dw ?
	image_count db ?
	plane_layout db ?
	seg_alpha dw ?
	seg_colors dw ?
cdg_t ends

cdg_slot_offset macro retval:req, slot:req
	mov retval, slot
	shl retval, 4
	add retval, offset _cdg_slots
endm

cdg_dst_segment macro retval:req, top:req, tmp:req
	mov ax, top
	mov tmp, ax
	shl ax, 2
	add ax, tmp
	add ax, SEG_PLANE_B
	mov retval, ax
endm

	extrn _cdg_slots:cdg_t:CDG_SLOT_COUNT

; A far caller enters with the linked public's CS. Keep native code outside
; SHARED's group so the writable instruction label uses that same CS base.
ifdef TH04_LARGE_PRODUCT
	.code TH04_CDG_PUT_TEXT
else
	.code SHARED
endif

public CDG_PUT_8
cdg_put_8 proc far
	; (PASCAL calling convention, parameter list needs to be reversed here)
	arg @@slot:word, @@top:word, @@left:word
	@@vram_dword_w	equ <bp>
	@@vram_offset_at_bottom_left	equ <bx>
	@@stride	equ <dx>

	push	bp
	mov	bp, sp
	push	si
	push	di
	push	ds
	cli

	; grcg_setcolor(GC_RMW, 0);
	; One GRCG tile color covers all four destination planes. Its zero tile
	; clears only pixels whose mask bit is set; other pixels remain unchanged.
	mov	al, GC_RMW
	out	7Ch, al
	mov	dx, 7Eh
	xor	al, al
	out	dx, al
	out	dx, al
	out	dx, al
	out	dx, al

	sti

	cdg_slot_offset	si, @@slot

if GAME eq 4
	mov	ax, [si+cdg_t.seg_colors]
	mov	@@seg_colors, ax
	jmp	short $+2

	cdg_dst_segment	es, @@top, bx
else
	mov	ax, @@top
	shl	ax, 2
	add	ax, @@top
	add	ax, SEG_PLANE_B
	mov	es, ax
endif
	push	0	; (sentinel)
	; Start on B and stack the following segment order as R, G, E, sentinel.
	add	ax, (SEG_PLANE_E - SEG_PLANE_B)	; AX == SEG_PLANE_E
	push	ax
	sub	ax, SEG_PLANE_DIST_E	; AX == SEG_PLANE_G
	push	ax
	sub	ax, SEG_PLANE_DIST_BRG	; AX == SEG_PLANE_R
	push	ax

	; cdg_dst_offset() with SHR instead of SAR, for a change
	mov	ax, @@left
	shr	ax, 3
	add	ax, [si+cdg_t.offset_at_bottom_left]

	mov	di, ax
	mov	@@vram_offset_at_bottom_left, ax
	mov	ax, [si+cdg_t.vram_dword_w]
	mov	@@vram_dword_w, ax
	shl	ax, 2	; *= size dword
	; REP MOVSD advances DI by row_bytes. Subtract row_bytes+80 afterward
	; to move to the preceding screen row while SI advances through the file.
	add	ax, ROW_SIZE
	mov	@@stride, ax
if GAME eq 4
	mov	ax, [si+cdg_t.seg_alpha]
	mov	ds, ax
else
	mov	ax, [si+cdg_t.seg_colors]
	mov	cx, [si+cdg_t.seg_alpha]
	mov	ds, cx
endif
	xor	si, si
	cld
	even

@@alpha:
	mov	cx, @@vram_dword_w
	rep movsd
	sub	di, @@stride
	jns	short @@alpha
if GAME eq 5
	mov	ds, ax
endif
	xor	al, al
	out	7Ch, al
	; Disable GRCG before direct color writes. The caller's earlier GRCG
	; mode/color is not restored by this entry.

	xor	si, si
if GAME eq 5
	even
endif

if GAME eq 4
	@@seg_colors = word ptr $+1
	; TH04 patches this instruction's segment immediate for the loaded slot.
	; This CS-relative write is a real self-modifying ownership surface.
	mov	ax, 1234h
	mov	ds, ax
endif

@@next_plane:
	mov	di, @@vram_offset_at_bottom_left

@@next_row:
	mov	cx, @@vram_dword_w

@@blit_dword:
	lodsd
	or	es:[di], eax
	add	di, dword
	loop	@@blit_dword
	sub	di, @@stride
	jns	short @@next_row
	pop	ax
	mov	es, ax
	or	ax, ax
	jnz	short @@next_plane
	pop	ds
	pop	di
	pop	si
	pop	bp
	retf	6
cdg_put_8 endp
	even

	end
