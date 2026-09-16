; Symbolic standalone producer probe for TH04 MAIN_013_TEXT.
.386
.model use16 large _TEXT

RES_Y = 400
ROW_SIZE = 80
PLANE_SIZE = 32000
PLAYFIELD_TOP = 16
PLAYFIELD_H = 368
PLAYFIELD_BOTTOM = 384
PLAYFIELD_VRAM_LEFT = 4
PLAYFIELD_VRAM_W = 48
TILE_H = 16
TILE_VRAM_W = 2
GRAM_400 = 0A800h
GC_TDW = 080h
GRCG_MODE_PORT = 07Ch
GRCG_TILE_PORT = 07Eh

MAIN_013_TEXT segment word public 'CODE' use16
MAIN_013_TEXT ends
main_01 group MAIN_013_TEXT

MAIN_013_TEXT segment word public 'CODE' use16
assume cs:main_01

public @grcg_tile_bb_put_8
@grcg_tile_bb_put_8 proc near
    push di
    mov bx, dx
    sar ax, 3
    shl dx, 6
    add ax, dx
    shr dx, 2
    add ax, dx
    mov di, ax
    mov ax, GRAM_400
    mov es, ax
    cmp bx, PLAYFIELD_BOTTOM
    ja short tile_roll_needed
    mov cx, TILE_H
    xor bx, bx
    jmp short tile_row_loop

tile_roll_needed:
    mov cx, RES_Y
    sub cx, bx
    mov bx, TILE_H
    sub bx, cx

tile_row_loop:
    stosw
    add di, (ROW_SIZE - TILE_VRAM_W)
    loop tile_row_loop
    or bx, bx
    jz short tile_ret
    sub di, PLANE_SIZE
    xchg cx, bx
    jmp short tile_row_loop

tile_ret:
    pop di
    ret
@grcg_tile_bb_put_8 endp

public PLAYFIELD_FILLM_0_40_384_274
public playfield_fillm_0_40_384_274
public _playfield_fillm_0_40_384_274
PLAYFIELD_FILLM_0_40_384_274 label near
_playfield_fillm_0_40_384_274 label near
playfield_fillm_0_40_384_274 proc near
    push di
    mov ax, 0A850h
    mov es, ax
    mov di, 0C34h
    call _grcg_fill_playfield_rows
    mov ax, 0AE72h
    mov es, ax
    mov di, 1094h
    call _grcg_fill_playfield_rows
    pop di
    ret
playfield_fillm_0_40_384_274 endp
    nop

public sub_12024
public @sub_12024$qv
sub_12024 proc near
@sub_12024$qv label near
    cli
    mov al, GC_TDW
    out GRCG_MODE_PORT, al
    mov dx, GRCG_TILE_PORT
    mov al, 0FFh
    out dx, al
    xor al, al
    out dx, al
    out dx, al
    out dx, al
    sti
    push di
    mov ax, GRAM_400
    mov es, ax
    mov ax, 1
    out 0A6h, ax
    xor di, di
    mov cx, (PLANE_SIZE / 4)
    rep stosd
    xor ax, ax
    out 0A6h, ax
    mov cx, (PLANE_SIZE / 4)
    xor di, di
    rep stosd
    pop di
    xor al, al
    out GRCG_MODE_PORT, al
    ret
sub_12024 endp

public playfield_fill
public _playfield_fill
_playfield_fill label near
playfield_fill proc near
    push di
    mov ax, 0A850h
    mov es, ax
    mov di, 72B4h
    call _grcg_fill_playfield_rows
    pop di
    ret
playfield_fill endp

public _grcg_fill_playfield_rows
_grcg_fill_playfield_rows proc near
    mov cx, (PLAYFIELD_VRAM_W / 4)
    rep stosd
    sub di, (ROW_SIZE + PLAYFIELD_VRAM_W)
    jge short _grcg_fill_playfield_rows
    ret
_grcg_fill_playfield_rows endp
    nop

MAIN_013_TEXT ends
end
