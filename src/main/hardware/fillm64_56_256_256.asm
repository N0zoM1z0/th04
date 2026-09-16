; TH04/TH05-style 64,56,256,256 playfield backdrop filler.
;
; With the GRCG already in TDW mode, the source value in EAX is irrelevant to
; VRAM. The target deliberately reuses EAX and instruction flags while using
; STOSD/LOOP. Defined natural TC4J dword-store loops expand those mechanisms,
; so keep this shared low-level producer as symbolic original-style assembly.

public @REIMU_MARISA_BACKDROP_COLORFILL$QV
public @MAI_YUKI_BACKDROP_COLORFILL$QV
label @mai_yuki_backdrop_colorfill$qv near
@reimu_marisa_backdrop_colorfill$qv proc near
    push di
    mov ax, GRAM_400 + (PLAYFIELD_TOP * ROW_SIZE) shr 4
    mov es, ax
    assume es:nothing
    mov di, (55 * ROW_SIZE) + PLAYFIELD_VRAM_LEFT
    nop

@@rows_next:
    mov cx, PLAYFIELD_VRAM_W / 4

@@rows_top_and_bottom:
    mov es:[di+(312 * ROW_SIZE)], eax
    stosd
    loop @@rows_top_and_bottom
    sub di, ROW_SIZE + PLAYFIELD_VRAM_W
    jge short @@rows_next
    mov ax, GRAM_400 + ((56 + PLAYFIELD_TOP) * ROW_SIZE) shr 4
    mov es, ax
    assume es:nothing
    mov di, (255 * ROW_SIZE) + PLAYFIELD_VRAM_LEFT
    nop

@@cols:
    mov es:[di+(320 / 8)], eax
    stosd
    mov es:[di+(320 / 8)], eax
    stosd
    sub di, ROW_SIZE + 8
    jge short @@cols
    pop di
    retn
@reimu_marisa_backdrop_colorfill$qv endp
    even
