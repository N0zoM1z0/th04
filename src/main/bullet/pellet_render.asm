; TH04 pellet renderer pair.
;
; The top and bottom near routines share one symbolic assembler include. The
; EVEN byte between them belongs to this physical source owner but is not part
; of either logical function body.

PELLET_TOP_H = 6
PELLET_BOTTOM_H = 4
PELLET_BOTTOM_Y = (PELLET_H - PELLET_BOTTOM_H)

ifdef TH04_LARGE_PRODUCT
PELLET_PROC_DISTANCE textequ <far>
PELLET_RETURN macro
    retf
endm
else
PELLET_PROC_DISTANCE textequ <near>
PELLET_RETURN macro
    retn
endm
endif

public _pellets_render_top
ifdef TH04_LARGE_PRODUCT
; Keep this macro within the body exported by the standalone context wrapper.
; The bottom pass deliberately writes its first source word twice.
PELLET_BOTTOM_NATIVE_ROW macro
    local byte2, byte1, next_row
    or al, al
    jz short byte2
    or ah, ah
    jz short byte1
    mov es:[di], ax
    jmp short next_row
byte1:
    mov es:[di], al
    jmp short next_row
byte2:
    mov es:[di+1], ah
next_row:
    add di, ROW_SIZE
endm
endif
_pellets_render_top proc PELLET_PROC_DISTANCE
	mov	ax, _pellets_render_count
	or	ax, ax
	jnz	short @@at_least_one_alive
	PELLET_RETURN

@@at_least_one_alive:
	push	bp
	push	si
	push	di
	mov	bp, ax
	mov	bx, offset _pellets_render

@@pellet_loop:
	mov	di, [bx+pellet_render_t.PRT_left]
	mov	ax, di
	sar	di, 3
	mov	cx, [bx+pellet_render_t.PRT_top]
	shl	cx, 6
	add	di, cx
	shr	cx, 2
	add	di, cx
	and	ax, 7
	mov	si, ax
	shl	si, 4
	add	si, offset _sPELLET
	shl	ax, 3
	mov	cx, PELLET_TOP_H
	or	ax, ax
	jz	short @@bytealigned
	cmp	di, ((RES_Y - PELLET_TOP_H + 1) * ROW_SIZE)
ifdef TH04_LARGE_PRODUCT
	jnb	short @@shifted_roll
	jmp	@@shifted_native
@@shifted_roll:
else
	jb	short @@shifted_yloop2
endif

@@shifted_yloop1:
	movsw
	add	di, (ROW_SIZE - word)
	dec	cx
	cmp	di, PLANE_SIZE
	jb	short @@shifted_yloop1
	sub	di, PLANE_SIZE

@@shifted_yloop2:
	movsw
	add	di, (ROW_SIZE - word)
	loop	@@shifted_yloop2
	jmp	short @@pellet_next
	even

@@bytealigned:
	cmp	di, ((RES_Y - PELLET_TOP_H + 1) * ROW_SIZE)
ifdef TH04_LARGE_PRODUCT
	jnb	short @@bytealigned_roll
	jmp	@@bytealigned_native
@@bytealigned_roll:
else
	jb	short @@bytealigned_yloop2
endif

@@bytealigned_yloop1:
	movsb
	inc	si
	add	di, (ROW_SIZE - byte)
	dec	cx
	cmp	di, PLANE_SIZE
	jb	short @@bytealigned_yloop1
	sub	di, PLANE_SIZE

@@bytealigned_yloop2:
	movsb
	inc	si
	add	di, (ROW_SIZE - byte)
	loop	@@bytealigned_yloop2

@@pellet_next:
	sub	di, (((PELLET_TOP_H + 1) - PELLET_BOTTOM_Y) * ROW_SIZE)
	jns	short @@set_bottom_data
	add	di, PLANE_SIZE

@@set_bottom_data:
	add	ax, offset _sPELLET_BOTTOM
	mov	word ptr [bx+PRB_vram_offset], di
	mov	word ptr [bx+PRB_sprite_offset], ax
	add	bx, size pellet_render_t
	dec	bp
ifdef TH04_LARGE_PRODUCT
	jz	short @@top_done
	jmp	@@pellet_loop
@@top_done:
else
	jnz	short @@pellet_loop
endif
	pop	di
	pop	si
	pop	bp
	PELLET_RETURN
ifdef TH04_LARGE_PRODUCT
@@shifted_native:
	rept PELLET_TOP_H
		movsw
		add di, (ROW_SIZE - word)
	endm
	xor cx, cx
	jmp @@pellet_next
@@bytealigned_native:
	rept PELLET_TOP_H
		movsb
		inc si
		add di, (ROW_SIZE - byte)
	endm
	xor cx, cx
	jmp @@pellet_next
endif
_pellets_render_top endp
	even

public _pellets_render_bottom
_pellets_render_bottom proc PELLET_PROC_DISTANCE
@@rows_after_roll equ <dx>

	mov	ax, _pellets_render_count
	or	ax, ax
	jnz	short @@at_least_one_alive
	PELLET_RETURN

@@at_least_one_alive:
	push	bp
	push	si
	push	di
	mov	bp, ax
	mov	bx, offset _pellets_render

@@pellet_loop:
	mov	di, word ptr [bx+PRB_vram_offset]
	mov	si, word ptr [bx+PRB_sprite_offset]
	xor	@@rows_after_roll, @@rows_after_roll
	cmp	di, ((RES_Y - PELLET_BOTTOM_H - 1) * ROW_SIZE)
ifdef TH04_LARGE_PRODUCT
	jnb	short @@roll_needed
	jmp	@@bottom_native
else
	jnb	short @@roll_needed
endif
	even
	mov	cx, (PELLET_BOTTOM_H + 1)
	jmp	short @@no_roll

@@roll_needed:
	mov	ax, (PLANE_SIZE + (ROW_SIZE - 1))
	sub	ax, di
	mov	cx, ROW_SIZE
	div	cx
	mov	cx, ax
	mov	@@rows_after_roll, (PELLET_BOTTOM_H + 1)
	sub	@@rows_after_roll, cx

@@no_roll:
	mov	ax, [si]
	jmp	short @@put

@@row_loop:
	lodsw

@@put:
	or	al, al
	jz	short @@only_byte_2
	or	ah, ah
	jz	short @@only_byte_1
	mov	es:[di], ax
	jmp	short @@row_next

@@only_byte_1:
	mov	es:[di], al
	jmp	short @@row_next

@@only_byte_2:
	mov	es:[di+1], ah

@@row_next:
	add	di, ROW_SIZE
	loop	@@row_loop
	or	@@rows_after_roll, @@rows_after_roll
	jz	short @@pellet_next
	sub	di, PLANE_SIZE
	xchg	cx, @@rows_after_roll
	jmp	short @@row_loop

@@pellet_next:
	add	bx, size pellet_render_t
	dec	bp
	jnz	short @@pellet_loop
	pop	di
	pop	si
	pop	bp
	PELLET_RETURN
ifdef TH04_LARGE_PRODUCT
@@bottom_native:
	mov ax, [si]
	PELLET_BOTTOM_NATIVE_ROW
	rept PELLET_BOTTOM_H
		lodsw
		PELLET_BOTTOM_NATIVE_ROW
	endm
	xor cx, cx
	jmp @@pellet_next
endif
_pellets_render_bottom endp
