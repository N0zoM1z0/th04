; TH04 MAIN far 2D vector construction producer.
;
; TH03 MAIN and TH05 MAIN preserve the same complete instruction producer
; modulo ordinary linked table/call operands. ReC98 introduced a C++
; decompilation in 2021 that requires raw inline opcodes and a codestring NOP.
; Three legal TC4J 4.02 mechanisms fail to reproduce the target register
; lifetime naturally. Keep this as evidence-backed irreducible/original-style
; symbolic assembly; this does not claim historical source spelling.

.386

extrn _SinTable8:word
extrn _CosTable8:word
extrn IATAN2:far

SHARED segment byte public 'CODE' use16
assume cs:SHARED

public VECTOR2
vector2 proc far
arg_length = word ptr 6
arg_angle = byte ptr 8
arg_ret_y = dword ptr 0Ah
arg_ret_x = dword ptr 0Eh

	push	bp
	mov	bp, sp
	push	si
	mov	dl, [bp+arg_angle]
	mov	si, [bp+arg_length]
	movsx	eax, si
	mov	dh, 0
	add	dx, dx
	mov	bx, dx
	movsx	edx, _CosTable8[bx]
	movsx	ecx, _SinTable8[bx]
	imul	eax, edx
	sar	eax, 8
	les	bx, [bp+arg_ret_x]
	mov	es:[bx], ax
	movsx	eax, si
	imul	eax, ecx
	sar	eax, 8
	les	bx, [bp+arg_ret_y]
	mov	es:[bx], ax
	pop	si
	pop	bp
	retf	0Ch
vector2 endp
	even

public VECTOR2_BETWEEN_PLUS
vector2_between_plus proc far
arg2_length = word ptr 6
arg2_ret_x = dword ptr 8
arg2_ret_y = dword ptr 0Ch
arg2_plus_angle = byte ptr 10h
arg2_y2 = word ptr 12h
arg2_x2 = word ptr 14h
arg2_y1 = word ptr 16h
arg2_x1 = word ptr 18h

	push	bp
	mov	bp, sp
	push	si
	mov	si, [bp+arg2_length]
	mov	ax, [bp+arg2_y2]
	sub	ax, [bp+arg2_y1]
	push	ax
	mov	ax, [bp+arg2_x2]
	sub	ax, [bp+arg2_x1]
	push	ax
	call	IATAN2
	add	al, [bp+arg2_plus_angle]
	mov	dl, al
	movsx	eax, si
	mov	dh, 0
	add	dx, dx
	mov	bx, dx
	movsx	edx, _CosTable8[bx]
	movsx	ecx, _SinTable8[bx]
	imul	eax, edx
	sar	eax, 8
	les	bx, [bp+arg2_ret_y]
	mov	es:[bx], ax
	movsx	eax, si
	imul	eax, ecx
	sar	eax, 8
	les	bx, [bp+arg2_ret_x]
	mov	es:[bx], ax
	pop	si
	pop	bp
	retf	14h
vector2_between_plus endp

SHARED ends
end
