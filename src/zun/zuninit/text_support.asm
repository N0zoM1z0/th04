; Maintained original-style ZUNINIT Shift-JIS and PC-98 text support.
; This is a symbolic reconstruction, not an identified historical source file.
;
; Independent TH02/TH04/TH05 release targets preserve the converter byte-for-
; byte. TH02 and TH04 additionally preserve the renderer byte-for-byte, while
; TH05 keeps the same architecture with a revised register allocation.
;
; Calling conventions are register-level because these routines are interrupt-
; side support, not compiler C ABI functions:
;   ZUNINIT_SJIS_TO_JIS: AX = Shift-JIS code, returns AX = PC-98/JIS code.
;   ZUNINIT_TEXT_PUT:    AX = VRAM offset, DX = CS-relative '$'-terminated
;                       Shift-JIS string.

	.8086
	.model tiny
	.code

public ZUNINIT_SJIS_TO_JIS
public ZUNINIT_TEXT_PUT

ZUNINIT_SJIS_TO_JIS proc near
	shl	ah, 1
	cmp	al, 9Fh
	jnb	short @@trail_ready
	cmp	al, 80h
	adc	ax, 0FEDFh

@@trail_ready:
	sbb	ax, 0DFFEh
	and	ax, 7F7Fh
	retn
ZUNINIT_SJIS_TO_JIS endp

ZUNINIT_TEXT_PUT proc near
	mov	bx, dx
	mov	di, 0A000h
	mov	es, di
	mov	di, ax
	mov	dx, ax
	; This pre-loop AX clear is present in both TH02 and TH04 release targets.
	; It is retained as an attested shared ASM instruction, not added padding.
	xor	ax, ax
	xor	cx, cx

@@glyph_loop:
	mov	ax, cs:[bx]
	cmp	al, '$'
	jz	short @@attributes
	xchg	ah, al
	call	ZUNINIT_SJIS_TO_JIS
	xchg	ah, al
	sub	al, ' '
	stosw
	or	ah, 80h
	stosw
	inc	bx
	inc	bx
	inc	cx
	inc	cx
	jmp	short @@glyph_loop

@@attributes:
	mov	di, 0A200h
	mov	es, di
	mov	di, dx
	mov	ax, 41h

@@attribute_loop:
	dec	cx
	stosw
	jz	short @@done
	jmp	short @@attribute_loop

@@done:
	retn
ZUNINIT_TEXT_PUT endp

	end
