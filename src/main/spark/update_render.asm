; TH04/TH05 shared spark lifecycle update/render pair.
;
; Independent original-target comparison preserves these complete low-level
; producer shapes across TH04 and TH05. The only target differences are the
; game-specific spark count, linked storage address, and near-call displacements.
; Legal TC4J probes either merge the two removal stores in sparks_update() or
; choose a different third fastcall register / shift shape in sparks_render().
; This source therefore records an evidence-backed original-style symbolic
; assembler owner instead of forcing C++ codegen or an ABI lie.

.386
.model use16 large _TEXT

F_FREE = 0
F_ALIVE = 1
F_REMOVE = 2

SPARK_COUNT = 96
SPARK_W = 8
SPARK_H = 8
PLAYFIELD_LEFT = 32
PLAYFIELD_TOP = 16
PLAYFIELD_W = 384
PLAYFIELD_H = 368
GRAM_400 = 0A800h

spark_t struc
    flag        db ?
    age         db ?
    pos_cur_x   dw ?
    pos_cur_y   dw ?
    pos_prev_x  dw ?
    pos_prev_y  dw ?
    velocity_x  dw ?
    velocity_y  dw ?
    angle       dw ?
spark_t ends

extrn _sparks:spark_t
extrn @PlayfieldMotion@update_seg1$qv:near
extrn @grcg_setcolor_direct_raw$qv:near
extrn SCROLL_SUBPIXEL_Y_TO_VRAM_SEG1:near
extrn @spark_render:near

CIRCLE_TEXT segment word public 'CODE' use16
CIRCLE_TEXT ends
main_01 group CIRCLE_TEXT

CIRCLE_TEXT segment word public 'CODE' use16
assume cs:main_01

public _sparks_update
_sparks_update proc near
    push si
    push di
    mov di, SPARK_COUNT
    mov si, offset _sparks

update_loop:
    cmp [si+spark_t.flag], F_FREE
    jz short update_next
    cmp [si+spark_t.flag], F_ALIVE
    jz short update_active
    mov [si+spark_t.flag], F_FREE
    jmp short update_next

update_active:
    lea ax, [si+spark_t.pos_cur_x]
    push ax
    call @PlayfieldMotion@update_seg1$qv
    add ax, ((SPARK_W / 2) shl 4)
    cmp ax, ((PLAYFIELD_W + SPARK_W) shl 4)
    jnb short update_remove
    add dx, ((SPARK_H / 2) shl 4)
    cmp dx, ((PLAYFIELD_H + SPARK_H) shl 4)
    jb short update_age

update_remove:
    mov [si+spark_t.flag], F_REMOVE
    jmp short update_next

update_age:
    inc [si+spark_t.velocity_y]
    inc [si+spark_t.age]
    cmp [si+spark_t.age], 40
    jbe short update_next
    mov [si+spark_t.flag], F_REMOVE

update_next:
    add si, size spark_t
    dec di
    jg short update_loop
    pop di
    pop si
    retn
_sparks_update endp

public _sparks_render
_sparks_render proc near
    push si
    push di
    mov ah, 12
    call @grcg_setcolor_direct_raw$qv
    mov ax, GRAM_400
    mov es, ax
    mov di, SPARK_COUNT
    mov si, offset _sparks

render_loop:
    cmp [si+spark_t.flag], F_ALIVE
    jnz short render_next
    mov ax, [si+spark_t.pos_cur_y]
    add ax, ((PLAYFIELD_TOP - (SPARK_H / 2)) shl 4)
    push ax
    call SCROLL_SUBPIXEL_Y_TO_VRAM_SEG1
    mov dx, ax
    mov ax, [si+spark_t.pos_cur_x]
    add ax, ((PLAYFIELD_LEFT - (SPARK_W / 2)) shl 4)
    sar ax, 4
    mov cl, [si+spark_t.age]
    call @spark_render

render_next:
    add si, size spark_t
    dec di
    jg short render_loop
    pop di
    pop si
    retn
_sparks_render endp
    even

CIRCLE_TEXT ends
end
