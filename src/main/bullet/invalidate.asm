; Evidence-backed original-style TH04 assembly.
; The independently attested TH05 target preserves the same packed-box
; invalidation architecture. Legal TC4J source probes expand the two 32-bit
; memory shifts instead of emitting this target form.

public @bullets_and_gather_invalidate$qv
@bullets_and_gather_invalidate$qv proc near
	push	si
	push	di
	mov	si, offset _bullets
	mov	di, BULLET_COUNT
	cmp	_bullet_zap_active, 0
	jnz	short @@pellets_decaying
	cmp	_bullet_clear_time, 0
	jnz	short @@pellets_decaying
	mov	_tile_invalidate_box, (PELLET_W shl 16) or PELLET_H
	mov	di, PELLET_COUNT

@@pellet_loop:
	cmp	[si+bullet_t.flag], F_FREE
	jz	short @@pellet_next
	call	tiles_invalidate_around pascal, large dword ptr [si+bullet_t.pos.prev]
@@pellet_next:
	add	si, size bullet_t
	dec	di
	jnz	short @@pellet_loop
	mov	di, BULLET16_COUNT

@@pellets_decaying:
	mov	_tile_invalidate_box, (BULLET16_W shl 16) or BULLET16_H
@@bullet16_loop:
	cmp	[si+bullet_t.flag], F_FREE
	jz	short @@bullet16_next
	cmp	[si+bullet_t.spawn_flag], BSF_GRAZED
	jbe	short @@bullet16_not_grazed
	shl	_tile_invalidate_box, 1
	call	tiles_invalidate_around pascal, large dword ptr [si+bullet_t.pos.prev]
	shr	_tile_invalidate_box, 1
	jmp	short @@bullet16_next
@@bullet16_not_grazed:
	call	tiles_invalidate_around pascal, large dword ptr [si+bullet_t.pos.prev]
@@bullet16_next:
	add	si, size bullet_t
	dec	di
	jnz	short @@bullet16_loop
	mov	si, offset _gather_circles
	mov	di, GATHER_COUNT

@@gather_loop:
	cmp	[si+gather_t.G_flag], F_FREE
	jz	short @@gather_next
	mov	ax, [si+gather_t.G_radius_cur]
	shr	ax, 3
	add	ax, 16
	mov	_tile_invalidate_box.x, ax
	mov	_tile_invalidate_box.y, ax
	call	tiles_invalidate_around pascal, large dword ptr [si+gather_t.G_center.prev]
@@gather_next:
	add	si, size gather_t
	dec	di
	jnz	short @@gather_loop
	pop	di
	pop	si
	retn
@bullets_and_gather_invalidate$qv endp
	even
