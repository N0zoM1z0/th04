; TH04 shared 32-pixel .CDG four-plane renderer.
;
; MAIN.EXE and OP.EXE independently preserve the same complete 0x65-byte FAR
; body modulo the linked _cdg_slots offset, followed by the same source-owned
; EVEN NOP. TH05 MAIN preserves the same producer lineage. A legal natural
; TC4J far-pointer implementation expands into scalar ES accesses and ordinary
; loops instead of the target DS/ES stack and REP MOVSD architecture. Keep this
; as evidence-backed irreducible/original-style symbolic assembly; this is not
; a claim that the historical source text had this exact spelling.

.386

SEG_PLANE_B equ 0A800h
SEG_PLANE_R equ 0B000h
SEG_PLANE_G equ 0B800h
SEG_PLANE_E equ 0E000h
ROW_SIZE equ 80
PLANE_COUNT equ 4
CDG_SIZE equ 16
CDG_OFFSET_AT_BOTTOM_LEFT equ 6
CDG_VRAM_DWORD_W equ 8
CDG_SEG_COLORS equ 14

extrn _cdg_slots:byte

SHARED segment word public 'CODE' use16
assume cs:SHARED

public CDG_PUT_NOALPHA_8
cdg_put_noalpha_8 proc far
arg_slot = word ptr 6
arg_top  = word ptr 8
arg_left = word ptr 0Ah

	push	bp
	mov	bp, sp
	push	si
	push	di
	push	ds

	; SEG_PLANE_B + (top * (ROW_SIZE / 16)).
	mov	ax, [bp+arg_top]
	mov	bx, ax
	shl	ax, 2
	add	ax, bx
	add	ax, SEG_PLANE_B
	mov	es, ax
	; Save E, G, and R so each completed plane can POP the next ES value.
	add	ax, (SEG_PLANE_E - SEG_PLANE_B)
	push	ax
	sub	ax, (SEG_PLANE_E - SEG_PLANE_G)
	push	ax
	sub	ax, (SEG_PLANE_G - SEG_PLANE_R)
	push	ax

	; cdg_slots[slot], sizeof(CDG) == 16.
	mov	si, [bp+arg_slot]
	shl	si, 4
	add	si, offset _cdg_slots
	mov	bx, [bp+arg_left]
	sar	bx, 3
	add	bx, [si+CDG_OFFSET_AT_BOTTOM_LEFT]
	mov	ax, [si+CDG_VRAM_DWORD_W]
	; BP is free after all three arguments have been consumed.
	mov	bp, ax
	shl	ax, 2
	add	ax, ROW_SIZE
	mov	dx, ax
	mov	ax, [si+CDG_SEG_COLORS]
	mov	ds, ax
	xor	si, si
	mov	al, PLANE_COUNT
	cld
	even

plane_start:
	mov	di, bx
row_start:
	mov	cx, bp
	rep movsd
	sub	di, dx
	jns	short row_start
	dec	al
	jz	short done
	pop	es
	jmp	short plane_start

done:
	pop	ds
	pop	di
	pop	si
	pop	bp
	retf	6
cdg_put_noalpha_8 endp
	even
SHARED ends
end
