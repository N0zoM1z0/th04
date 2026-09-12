; Copy one enemy-local bullet template into the active global template.
;
; TH04 passes an enemy_t pointer, so the source begins at the validated
; bullet_template member offset. The low-level CX/SI/DI/ES setup order is part
; of the reviewed producer shape shared with the corresponding TH05 helper.

	.186
	.model use16 large
	locals

BULLET_TEMPLATE_WORDS       = 9
ENEMY_BULLET_TEMPLATE_OFFSET = 44

	extern _bullet_template:byte

main_03 group MAIN_033_TEXT
MAIN_033_TEXT segment word public 'CODE' use16
	assume cs:main_03

public ENEMY_BULLET_TEMPLATE_PUSH
enemy_bullet_template_push proc near
@@enemy = word ptr 4
	push	bp
	mov	bp, sp
	push	si
	push	di
	mov	cx, BULLET_TEMPLATE_WORDS
	mov	si, [bp+@@enemy]
	add	si, ENEMY_BULLET_TEMPLATE_OFFSET
	mov	di, offset _bullet_template
	push	ds
	pop	es
	rep movsw
	pop	di
	pop	si
	pop	bp
	retn	2
enemy_bullet_template_push endp

MAIN_033_TEXT ends
	end
