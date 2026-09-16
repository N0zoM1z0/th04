; TH04 option-laser raw blitter.
;
; This routine consumes left/top/cel/height in AX/DX/BX/SI, rotates the
; one-byte laser mask into AX, and writes directly through ES with wrapped
; STOSB/STOSW loops. A bounded natural TC4J probe preserves the external ABI
; but expands this register/string-loop architecture substantially, so this is
; maintained as evidence-backed irreducible/original-style symbolic assembly.

public SHOT_LASER_PUT_RAW
shot_laser_put_raw proc near
    @@left equ <ax>
    @@top equ <dx>
    @@cel equ <bx>
    @@h equ <si>
    @@rows_after_roll equ <dx>
    @@top_in equ <bx>

    push si
    push di
    mov cx, @@left
    sar @@left, 3
    mov di, @@left
    and cl, 7
    xor ah, ah
    mov al, _SHOT_LASER_DOTS[@@cel]
    ror ax, cl
    mov @@top_in, @@top
    shl @@top, 6
    add di, @@top
    shr @@top, 2
    add di, @@top
    mov dx, GRAM_400
    mov es, dx
    shr @@h, 4
    mov cx, @@h
    add cx, @@top_in
    cmp cx, RES_Y
    ja short @@roll_needed
    mov cx, @@h
    xor @@rows_after_roll, @@rows_after_roll
    jmp short @@blit_loop

@@roll_needed:
    mov cx, RES_Y
    sub cx, @@top_in
    mov @@rows_after_roll, @@h
    sub @@rows_after_roll, cx

@@blit_loop:
    or ah, ah
    jz short @@byte_loop
    even

@@word_loop:
    stosw
    add di, (ROW_SIZE - word)
    loop @@word_loop
    jmp short @@roll_check

@@byte_loop:
    stosb
    add di, (ROW_SIZE - byte)
    loop @@byte_loop

@@roll_check:
    or @@rows_after_roll, @@rows_after_roll
    jz short @@return
    sub di, PLANE_SIZE
    xchg cx, @@rows_after_roll
    jmp short @@blit_loop

@@return:
    pop di
    pop si
    retn
shot_laser_put_raw endp
    even
