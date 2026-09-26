	.386
	locals

; TH04 CDG slot and PC-98 VRAM values used by this OP translation unit.
ROW_SIZE = 80
SEG_PLANE_B = 0A800h
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

cdg_dst_offset macro retval:req, cdg:req, left:req
	mov retval, left
	sar retval, 3
	add retval, [cdg+cdg_t.offset_at_bottom_left]
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

SHARED	segment word public 'CODE' use16
	assume cs:SHARED

; Identical to the barely decompilable TH05 version, which doesn't rely on
; self-modifying code for the width.
public CDG_PUT_NOCOLORS_8
cdg_put_nocolors_8 proc far
	; (PASCAL calling convention, parameter list needs to be reversed here)
	arg @@slot:word, @@top:word, @@left:word
	@@stride_backwards	equ <dx>

	push	bp
	mov	bp, sp
	push	si
	push	di

	cdg_slot_offset	si, @@slot
	cdg_dst_offset	di, si, @@left

	mov	ax, [si+cdg_t.vram_dword_w]
	mov	@@width, ax
	jmp	short $+2
	shl	ax, 2
	add	ax, ROW_SIZE
	mov	@@stride_backwards, ax

	cdg_dst_segment	es, @@top, bx

	push	ds
	mov	ds, [si+cdg_t.seg_alpha]
	xor	si, si
	cld
	even

@@next_row:
	@@width = word ptr $+1
	mov	cx, 1234h
	rep movsd
	sub	di, @@stride_backwards
	jns	short @@next_row

	pop	ds
	pop	di
	pop	si
	pop	bp
	retf	6
cdg_put_nocolors_8 endp
	even

SHARED	ends

	end
