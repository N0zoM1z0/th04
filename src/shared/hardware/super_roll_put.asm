; PC-98 rolling sprite renderer adapted from ReC98 master.lib.
; Original algorithm: Kazumi (Hitoshi Okuda), Akihiko Koizuka, 1993.
; TH04 standalone large-model ABI: far Pascal; each plane wraps at line 400.
.186
.model use16 large SHARED
RETSIZE equ 2
.data
extrn super_patsize:word, super_patdata:word
BYTE_MASK db 0FFh,7Fh,3Fh,1Fh,0Fh,7,3,1
; Native CS-relative self-modification needs an ungrouped code segment.
ifdef TH04_LARGE_PRODUCT
.code TH04_SUPER_ROLL_TEXT
else
.code SHARED
endif

; Mutable immediate operands used by the historical self-modifying blitter.
JMOV macro reg,lab
    mov reg,1234h
    org $-2
lab dw ?
endm

public SUPER_ROLL_PUT
SUPER_ROLL_PUT proc far
	push	BP
	mov	BP,SP
	push	DS
	push	SI
	push	DI

	@@x	= (RETSIZE+3)*2
	@@y	= (RETSIZE+2)*2
	@@num	= (RETSIZE+1)*2

	mov	CX,[BP+@@x]
	mov	DI,[BP+@@y]
	mov	SI,DI		;-+
	shl	DI,2		; |
	add	DI,SI		; |DI=y*80
	shl	DI,4		;-+
	mov	AX,CX
	and	CX,7h		;CL=x%8(shift dot counter)
	shr	AX,3		;AX=x/8
	add	DI,AX		;GVRAM offset address

	mov	BX,CX
	mov	AL,BYTE_MASK[BX]

	mov	BX,[BP+@@num]
	shl	BX,1		;integer size & near pointer
	mov	DX,super_patsize[BX]	;pattern size (1-8)
	mov	CH,DH		;DL -> DH
	shr	CH,1

	mov	DS,super_patdata[BX]		;BX+2 -> BX
	mov	BX,DX
	xor	BH,BH
	add	SI,BX		; SI = y + ysize - 400
	sub	SI,400
	jg	short @@noroll
	xor	SI,SI		; SI = 画面下にはみ出た長さ
@@noroll:
	sub	BX,SI		; BX = 画面内に描画できる長さ

	mov	CS:SUPEROLL_BP_,SI
	mov	CS:SUPEROLL_BX_,BX

	mov	BP,DI

	test	DI,1
	jnz	short @@ODD_ADDRESS

@@EVEN_ADDRESS:
	test	DH,1		;DX -> DH
	jnz	short @@ODD_SIZE1

	mov	BYTE PTR CS:[SUPEROLL_BYTE_MASK1],AL
	mov	BYTE PTR CS:[superoll_count1],CH
	mov	AL,80
	sub	AL,DH		;DL -> DH
	mov	BYTE PTR CS:[superoll_add_di1],AL
	mov	CS:SUPEROLL_DISP_ADDRESS,OFFSET superoll_disp1
	jmp	short @@START
	EVEN

@@ODD_SIZE1:
	mov	BYTE PTR CS:[SUPEROLL_BYTE_MASK2],AL
	mov	BYTE PTR CS:[superoll_count2],CH
	mov	AL,80
	sub	AL,DH
	mov	BYTE PTR CS:[superoll_add_di2],AL
	mov	CS:SUPEROLL_DISP_ADDRESS,OFFSET superoll_disp2
	jmp	short @@START
	EVEN

@@ODD_ADDRESS:
	dec	BP
	test	DH,1
	jnz	short @@ODD_SIZE2

	mov	BYTE PTR CS:[SUPEROLL_BYTE_MASK3],AL
	dec	CH		;!!!!!!!!!!!!!!!!!!!!!
	mov	BYTE PTR CS:[superoll_count3],CH
	mov	AL,78		;word
	sub	AL,DH
	mov	BYTE PTR CS:[superoll_add_di3],AL
	mov	CS:SUPEROLL_DISP_ADDRESS,OFFSET superoll_disp3
	jmp	short @@START
	EVEN

@@ODD_SIZE2:
	mov	BYTE PTR CS:[SUPEROLL_BYTE_MASK4],AL
	mov	BYTE PTR CS:[superoll_count4],CH
	mov	AL,79		;word
	sub	AL,DH
	mov	BYTE PTR CS:[superoll_add_di4],AL
	mov	CS:SUPEROLL_DISP_ADDRESS,OFFSET superoll_disp4
	EVEN

@@START:
	mov	CS:SUPEROLL_DI_,BP
	xor	SI,SI

	mov	AX,0c0h		;RMW mode
	out	7ch,AL
	mov	AL,AH
	out	7eh,AL
	out	7eh,AL
	out	7eh,AL
	out	7eh,AL
	mov	AX,0a800h
	mov	ES,AX
	call	SUPEROLL_DISP		;originally cls_loop
	mov	AX,0ff00h + 11001110b
	out	7ch,AL		;RMW mode
	mov	AL,AH		;AL==0ffh
	out	7eh,AL
	out	7eh,AL
	out	7eh,AL
	out	7eh,AL
	call	SUPEROLL_DISP
	mov	AL,11001101b
	out	7ch,AL		;RMW mode
	call	SUPEROLL_DISP
	mov	AL,11001011b
	out	7ch,AL		;RMW mode
	call	SUPEROLL_DISP
	mov	AL,11000111b
	out	7ch,AL		;RMW mode
	call	SUPEROLL_DISP
	xor	AL,AL
	out	7ch,AL		;grcg stop

	pop	DI
	pop	SI
	pop	DS
	pop	BP
	ret	6
	EVEN

SUPEROLL_DISP:
	JMOV	BX,SUPEROLL_BX_
	JMOV	DI,SUPEROLL_DI_
	JMOV	BP,SUPEROLL_BP_
	JMOV	AX,SUPEROLL_DISP_ADDRESS
	jmp	AX
	EVEN
superoll_disp1:
	xor	DL,DL
	EVEN
@@put_loop1:
	lodsw
	ror	AX,CL
	mov	DH,AL
	and	AL,11h	;dummy
SUPEROLL_BYTE_MASK1	equ	$-1
	xor	DH,AL
	or	AL,DL
	stosw	;mov 	ES:[DI],AX	;;;or
	mov	DL,DH
	dec	CH
	jnz	@@put_loop1
	mov	ES:[DI],DL
	mov	DL,CH	;DL=0
	add	DI,80	;dummy
superoll_add_di1		equ	$-1
	mov	CH,11h	;dummy
superoll_count1		equ	$-1
	dec	BX
	jnz	@@put_loop1
	or	BP,BP
	jnz	short @@roll1
	retn
	EVEN
@@roll1:
	sub	DI,7d00h
	mov	BX,BP
	xor	BP,BP
	jmp	short @@put_loop1
	EVEN
superoll_disp2:
	xor	DL,DL
	EVEN
@@single_check2:
	or	CH,CH
	jz	short @@skip2
	EVEN
@@put_loop2:
	lodsw
	ror	AX,CL
	mov	DH,AL
	and	AL,11h	;dummy
SUPEROLL_BYTE_MASK2	equ	$-1
	xor	DH,AL
	or	AL,DL
	stosw	;mov 	ES:[DI],AX	;;;or
	mov	DL,DH
	dec	CH
	jnz	@@put_loop2
@@skip2:
	lodsb
	xor	AH,AH
	ror	AX,CL
	or	AL,DL
	stosw
	dec	DI
	mov	DL,CH	;DL=0
	add	DI,80	;dummy
superoll_add_di2		equ	$-1
	mov	CH,11h	;dummy
superoll_count2		equ	$-1
	dec	BX
	jnz	@@single_check2
	or	BP,BP
	jnz	short @@roll2
	retn
	EVEN
@@roll2:
	sub	DI,7d00h
	mov	BX,BP
	xor	BP,BP
	jmp	short @@single_check2
	EVEN
superoll_disp3:
@@put_loop3_1:
	lodsb
	xor	AH,AH
	ror	AX,CL
	mov	DL,AH
	xchg	AH,AL
	xor	AL,AL
	stosw
	or	CH,CH
	jz	short @@no_word1
	EVEN
@@put_loop3_2:
	lodsw
	ror	AX,CL
	mov	DH,AL
	and	AL,11h	;dummy
SUPEROLL_BYTE_MASK3	equ	$-1
	xor	DH,AL
	or	AL,DL
	stosw	;mov 	ES:[DI],AX	;;;or
	mov	DL,DH
	dec	CH
	jnz	@@put_loop3_2
	EVEN
@@no_word1:
	lodsb
	xor	AH,AH
	ror	AX,CL
	or	AL,DL
	stosw
	mov	DL,CH	;DL=0
	add	DI,80	;dummy
superoll_add_di3		equ	$-1
	mov	CH,11h	;dummy
superoll_count3		equ	$-1
	dec	BX
	jnz	@@put_loop3_1
	or	BP,BP
	jnz	short @@roll3
	retn
	EVEN
@@roll3:
	sub	DI,7d00h
	mov	BX,BP
	xor	BP,BP
	jmp	short @@put_loop3_1
	EVEN
superoll_disp4:
@@put_loop4_1:
	lodsb
	xor	AH,AH
	ror	AX,CL
	mov	DL,AH
	xchg	AH,AL
	xor	AL,AL
	stosw
	or	CH,CH
	jz	short @@no_word2
	EVEN
@@put_loop4_2:
	lodsw
	ror	AX,CL
	mov	DH,AL
	and	AL,11h	;dummy
SUPEROLL_BYTE_MASK4	equ	$-1
	xor	DH,AL
	or	AL,DL
	stosw	;mov 	ES:[DI],AX	;;;or
	mov	DL,DH
	dec	CH
	jnz	@@put_loop4_2
	EVEN
@@no_word2:
	mov	ES:[DI],DL
	mov	DL,CH	;DL=0
	add	DI,80	;dummy
superoll_add_di4		equ	$-1
	mov	CH,11h	;dummy
superoll_count4		equ	$-1
	dec	BX
	jnz	@@put_loop4_1
	or	BP,BP
	jnz	short @@roll4
	retn
	EVEN
@@roll4:
	sub	DI,7d00h
	mov	BX,BP
	xor	BP,BP
	jmp	short @@put_loop4_1
SUPER_ROLL_PUT endp
end
