; Standalone assembly declarations for the adjacent maintained body.
; Evidence-backed original-style TH04 assembly.
; The independently attested TH05 target preserves the same packed-box
; invalidation architecture. Legal TC4J source probes expand the two 32-bit
; memory shifts instead of emitting this target form.

.386
.model use16 large
locals

F_FREE = 0
BSF_GRAZED = 1
PELLET_COUNT = 240
BULLET16_COUNT = 200
BULLET_COUNT = 440
GATHER_COUNT = 16
PELLET_W = 8
PELLET_H = 8
BULLET16_W = 16
BULLET16_H = 16

Point struc
	x dw ?
	y dw ?
Point ends
motion_t struc
	cur Point <?>
	prev Point <?>
	velocity Point <?>
motion_t ends
bullet_t struc
	flag db ?
	age db ?
	pos motion_t <?>
	spawn_group db ?
	unused db ?
	speed_cur db ?
	angle db ?
	spawn_flag db ?
	move_flag db ?
	special_motion db ?
	speed_final db ?
	decelerate_time db ?
	decelerate_speed_delta db ?
	patnum dw ?
bullet_t ends
gather_t struc
	G_flag db ?
	G_col db ?
	G_center motion_t <?>
	G_radius_cur dw ?
	G_ring_points dw ?
	G_angle_cur db ?
	G_angle_delta db ?
	G_bullet_template db 18 dup(?)
	G_radius_prev dw ?
	G_radius_delta dw ?
gather_t ends

extrn _bullets:byte
extrn _bullet_zap_active:byte
extrn _bullet_clear_time:byte
; Packed x/y words: the body assigns and shifts both dimensions together.
; MAIN TILE_TEXT 0AAF:1FBE/1FDF/1FF3/1FFF use 32-bit memory operands.
extrn _tile_invalidate_box:dword
extrn _gather_circles:byte
TILES_INVALIDATE_AROUND procdesc pascal near center:dword

TILE_TEXT segment word public 'CODE' use16
TILE_TEXT ends
main_01 group TILE_TEXT
TILE_TEXT segment word public 'CODE' use16
assume cs:main_01

; TH04_NATIVE_BODY
	even
TILE_TEXT ends
end
