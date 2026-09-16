; TH04 16x16 one-plane super sprite blitter.
;
; The target ABI consumes top in AX and left in CX while receiving only patnum
; on the Pascal stack. Its DS/ES string-register implementation is not reproduced
; by a truthful typed TC4J function, so preserve the low-level producer as
; symbolic irreducible/original-style assembly.

public @Z_SUPER_PUT_16X16_MONO_RAW$QI
@z_super_put_16x16_mono_raw$qi proc near
	arg_bx near, @patnum:word
	@@left equ <cx>
	@@top equ <ax>
	@@first_bit equ <cl>
	@@vram_offset equ <di>
	@@PATTERN_H = 16

	push	ds
	push	si
	push	di

	mov	@@vram_offset, @@top
	shl	@@top, 2
	add	@@vram_offset, @@top
	shl	@@vram_offset, 4

	mov	ax, @@left
	and	@@left, 7
	shr	ax, 3
	add	@@vram_offset, ax

	mov	bx, @patnum
	shl	bx, 1
	mov	ds, _super_patdata[bx]
	xor	si, si
	mov	ch, @@PATTERN_H
	jcxz	short @@byte_aligned

	mov	dx, 0FFFFh
	shr	dl, @@first_bit
	mov	dh, dl
	not	dh
	test	@@vram_offset, 1
	jnz	short @@odd

@@even:
	lodsw
	ror	ax, @@first_bit
	mov	bl, al
	and	al, dl
	and	bl, dh
	mov	es:[@@vram_offset], ax
	mov	es:[@@vram_offset+2], bl
	add	@@vram_offset, ROW_SIZE
	dec	ch
	jnz	short @@even
	jmp	short @@return
	even

@@odd:
	lodsw
	ror	ax, @@first_bit
	mov	bh, al
	and	al, dl
	and	bh, dh
	mov	bl, ah
	mov	es:[@@vram_offset], al
	mov	es:[@@vram_offset+1], bx
	add	@@vram_offset, ROW_SIZE
	dec	ch
	jnz	short @@odd
	jmp	short @@return
	even

@@byte_aligned:
	lodsw
	mov	es:[@@vram_offset], ax
	add	@@vram_offset, ROW_SIZE
	dec	ch
	jnz	short @@byte_aligned

@@return:
	pop	di
	pop	si
	pop	ds
	ret_bx
@z_super_put_16x16_mono_raw$qi endp
	even
