	.386
	.model use16 large SHARED
	locals

; TH04 CDG slots are 16 bytes each, with 64 entries. These field offsets and
; layout values are checked by the cold-linked MAIN/OP/MAINE module replays.
; A CDG/CD2 file has one 16-byte header followed by fixed-size images.
; plane_layout 0 stores four color planes (B,R,G,E), layout 2 stores just a
; monochrome mask, and layout 1 stores mask followed by four color planes.
; CDG_plane_size is bytes in ONE plane. The last two header words become
; runtime DOS allocation segments; they are not host pointers to file data.
CDG_COLORS = 0
CDG_ALPHA = 2
CDG_SLOT_COUNT = 64

cdg_t struc
	CDG_plane_size dw ?
	pixel_w dw ?
	pixel_h dw ?
	offset_at_bottom_left dw ? ; Relative VRAM byte offset of final image row.
	vram_dword_w dw ?          ; Row width in four-byte groups, not pixels.
	image_count db ?
	plane_layout db ?
	seg_alpha dw ?             ; One heap-owned mask plane, or zero.
	seg_colors dw ?            ; One allocation containing four color planes.
cdg_t ends

cdg_slot_offset macro retval:req, slot:req
	mov retval, slot
	shl retval, 4
	add retval, offset _cdg_slots
endm

	extrn FILE_ROPEN:proc
	extrn FILE_READ:proc
	extrn FILE_SEEK:proc
	extrn FILE_CLOSE:proc
	extrn HMEM_ALLOCBYTE:proc
	extrn HMEM_FREE:proc
	extrn _cdg_slots:cdg_t:CDG_SLOT_COUNT
	extrn _cdg_noalpha:byte
	extrn cdg_images_to_load:byte

	.code SHARED

public CDG_LOAD_SINGLE_NOALPHA
public CDG_LOAD_SINGLE

cdg_load_single_noalpha label proc
	mov	_cdg_noalpha, 1
	align	2

cdg_load_single	proc far

@@n   	=  word ptr  6
@@fn  	= dword	ptr  8
@@slot	=  word ptr  12

	push	bp
	mov	bp, sp
	push	si
	push	di
	mov	di, [bp+@@slot]
	push	di
	nop	; Source-owned instruction retained by the accepted raw-byte replay.
	call	cdg_free
	shl	di, 4	; *= size cdg_t
	add	di, offset _cdg_slots
	call	file_ropen pascal, large [bp+@@fn]
	call	file_read pascal, ds, di, size cdg_t
	mov	ax, [di+cdg_t.CDG_plane_size]
	mov	dx, ax
	; Select one, four, or five planes per file image before skipping [n].
	cmp	[di+cdg_t.plane_layout], CDG_COLORS
	jz	short @@read
	shl	ax, 2
	cmp	[di+cdg_t.plane_layout], CDG_ALPHA
	jz	short @@read
	add	ax, dx

@@read:
	; Retain the 16-bit image-size/index product in AX. Widening it would
	; change overflow behavior even though FILE_SEEK receives a 32-bit value.
	mul	[bp+@@n]
	movzx	eax, ax
	call	file_seek pascal, eax, 1
	call	cdg_read_single
	call	file_close
	mov	_cdg_noalpha, 0
	pop	di
	pop	si
	pop	bp
	retf	8
cdg_load_single endp
	align	2

; Reads a single CDG image from the master.lib file, which previously has been
; positioned at the beginning of the image data, into the slot in DI.
cdg_read_single proc near
	; DI addresses the destination slot in DGROUP. Each retained plane group
	; is separately paragraph-allocated; colors share one four-plane block.
	mov	al, [di+cdg_t.plane_layout]
	or	al, al	; AL == CDG_COLORS?
	jz	short @@colors
	cmp	al, CDG_ALPHA
	jz	short @@alpha
	cmp	_cdg_noalpha, 0
	jnz	short @@skip_alpha

@@alpha:
	call	hmem_allocbyte pascal, [di+cdg_t.CDG_plane_size]
	mov	[di+cdg_t.seg_alpha], ax
	call	file_read pascal, ax, 0, [di+cdg_t.CDG_plane_size]
	jmp	short @@colors

@@skip_alpha:
	; "noalpha" skips file mask bytes for a combined image. A mask-only
	; layout still follows @@alpha, because it has no color planes to retain.
	movzx	eax, [di+cdg_t.CDG_plane_size]
	call	file_seek pascal, eax, 1

@@colors:
	cmp	[di+cdg_t.plane_layout], CDG_ALPHA
	jz	short @@ret
	mov	ax, [di+cdg_t.CDG_plane_size]
	shl	ax, 2
	call	hmem_allocbyte pascal, ax
	mov	[di+cdg_t.seg_colors], ax
	push	ax
	push	0
	mov	ax, [di+cdg_t.CDG_plane_size]
	shl	ax, 2
	push	ax
	call	file_read

@@ret:
	retn
cdg_read_single endp


public CDG_LOAD_ALL_NOALPHA
public CDG_LOAD_ALL

cdg_load_all_noalpha label proc
	mov	_cdg_noalpha, 1
	align	2

cdg_load_all proc far

@@fn        	= dword	ptr  6
@@slot_first	=  word ptr  10

	push	bp
	mov	bp, sp
	push	si
	push	di
	call	file_ropen pascal, large [bp+@@fn]
	cdg_slot_offset	di, [bp+@@slot_first]
	call	file_read pascal, ds, di, size cdg_t
	mov	si, di
	mov	bp, [bp+@@slot_first]
	mov	al, cdg_t.image_count[si]
	mov	cdg_images_to_load, al
	push	ds
	pop	es

@@loop:
	call	cdg_free pascal, bp
ifdef TH04_LARGE_PRODUCT
	; The TH04-local C++ heap uses LES and may leave ES changed. CDG headers
	; must always be copied into DGROUP, including after the first allocation.
	push	ds
	pop	es
endif
	; Copy the first 12 header bytes to each slot. Do not copy the two
	; allocation-segment words: cdg_read_single owns their replacement.
	mov	cx, (cdg_t.seg_alpha / dword)
	rep movsd
	sub	si, cdg_t.seg_alpha
	sub	di, cdg_t.seg_alpha
	call	cdg_read_single
	inc	bp
	add	di, size cdg_t
	dec	cdg_images_to_load
	jnz	short @@loop
	call	file_close
	mov	_cdg_noalpha, 0
	pop	di
	pop	si
	pop	bp
	retf	6
cdg_load_all endp


public CDG_FREE
cdg_free proc far
	mov	bx, sp

	push	di
	mov	di, word ptr ss:[bx+4]
	shl	di, 4	; *= size cdg_t
	add	di, offset _cdg_slots.seg_alpha
	; Each nonzero word is a heap owner. Clear it after release so repeated
	; free calls are harmless; geometry/header metadata deliberately remains.
	cmp	word ptr [di], 0
	jz	short @@colors
	call	hmem_free pascal, word ptr [di]
	mov	word ptr [di], 0

@@colors:
	add	di, word ; = seg_colors
	cmp	word ptr [di], 0
	jz	short @@ret
	call	hmem_free pascal, word ptr [di]
	mov	word ptr [di], 0

@@ret:
	pop	di
	retf	2
cdg_free endp
	align 2


public CDG_FREE_ALL
cdg_free_all proc far
	push	si
	mov	si, CDG_SLOT_COUNT - 1

@@loop:
	call	cdg_free pascal, si
	dec	si
	jge	short @@loop
	pop	si
	retf
cdg_free_all endp

	end
