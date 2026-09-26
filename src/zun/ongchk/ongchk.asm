; PMD ADPCM RAM diagnostic bundled as ONGCHK.COM in the TH04 ZUN selector.
; Symbolic original-style reconstruction of an external library component.
; COM runtime starts at CS:0100h. The PSP command tail is at 0080h.

.8086
.model tiny
.code
org 100h

start:
    cld
    mov ax,cs
    mov ds,ax
    mov es,ax
    mov byte ptr [opna_first],0h
    mov si,80h
skip_psp_spaces:
    lodsb
    cmp al,20h
    jz skip_psp_spaces
    cmp al,38h
    jnz run_probe
    mov byte ptr [opna_first],1h
run_probe:
    call probe_device
    mov ah,4Ch
    mov al,[exit_status]
    int 21h

; Detect PMD/OPNA ports and remember the four I/O addresses.
probe_device:
    cmp byte ptr [opna_first],1h
    jz try_opna
    call probe_pmd
    jnc finish_probe
try_opna:
    call probe_opna
    jnc finish_probe
    cmp byte ptr [opna_first],1h
    jnz scan_silent_ports
    call probe_pmd
    jnc finish_probe
scan_silent_ports:
    mov byte ptr [exit_status],1h
    mov ah,4h
    mov dx,88h
    cmp byte ptr [port_select],0FFh
    jz try_silent_port
    mov dh,[port_select]
    mov ah,1h
try_silent_port:
    cli
    mov cx,64h
delay_before_index:
    loop delay_before_index
    mov al,0Bh
    out dx,al
    mov cx,64h
delay_before_data:
    loop delay_before_data
    add dx,2h
    mov al,0AAh
    out dx,al
    mov cx,64h
delay_before_readback:
    loop delay_before_readback
    in al,dx
    sti
    sub dx,2h
    cmp al,0AAh
    jnz next_silent_port
    jmp near ptr record_ports
next_silent_port:
    dec ah
    jnz next_silent_bank
    jmp near ptr probe_failed
next_silent_bank:
    add dx,100h
    jmp short try_silent_port
finish_probe:
    cmp byte ptr [exit_status],2h
    jc probe_done
    call check_adpcm_ram
    jc probe_done
    add byte ptr [exit_status],2h
probe_done:
    clc
    ret

probe_pmd:
    mov byte ptr [exit_status],3h
    mov byte ptr [pmd_found],0h
    mov ax,0FD80h
    mov es,ax
    cmp word ptr es:[2h],2A27h
    jnz pmd_external_ports
    mov byte ptr [pmd_found],1h
    cmp byte ptr es:[4h],6h
    jnc pmd_external_ports
    jmp near ptr probe_failed
pmd_external_ports:
    mov dx,0A460h
    in al,dx
    cmp al,0FFh
    jnz pmd_enable
    jmp near ptr probe_failed
pmd_enable:
    out 5Fh,al
    and al,0FCh
    out dx,al
    mov ah,2h
    mov dx,188h
    cmp byte ptr [port_select],0FFh
    jz try_pmd_port
    mov dh,[port_select]
    mov ah,1h
try_pmd_port:
    cli
    mov al,0FFh
    mov cx,64h
loc_01F0:
    loop loc_01F0
    out dx,al
    add dx,2h
    mov cx,64h
loc_01F9:
    loop loc_01F9
    in al,dx
    sti
    sub dx,2h
    dec al
    jnz next_pmd_port
    add dx,4h
    in al,dx
    mov bl,al
    add dx,2h
    in al,dx
    sub dx,6h
    and al,bl
    inc al
    jz activate_pmd
next_pmd_port:
    dec ah
    jnz next_pmd_bank
    jmp near ptr probe_failed
next_pmd_bank:
    inc dh
    jmp short try_pmd_port
activate_pmd:
    push dx
    mov dx,0A460h
    cli
    in al,dx
    out 5Fh,al
    and al,0FCh
    or al,1h
    out dx,al
    mov dx,0A66Eh
    in al,dx
    out 5Fh,al
    and al,0FEh
    out dx,al
    cmp byte ptr [pmd_found],0h
    jz pmd_ready
    mov al,1h
    out 6Eh,al
pmd_ready:
    sti
    pop dx
    jmp short record_ports
probe_opna:
    mov byte ptr [exit_status],2h
    mov byte ptr [pmd_found],0h
    mov ax,0FD80h
    mov es,ax
    cmp word ptr es:[2h],2A27h
    jnz opna_external_ports
    mov byte ptr [pmd_found],1h
    cmp byte ptr es:[4h],6h
    jc start_opna_ports
opna_external_ports:
    mov dx,0A460h
    in al,dx
    cmp al,0FFh
    jz start_opna_ports
    out 5Fh,al
    and al,0FCh
    out dx,al
start_opna_ports:
    mov ah,4h
    mov dx,88h
    cmp byte ptr [port_select],0FFh
    jz try_opna_port
    mov dh,[port_select]
    mov ah,1h
try_opna_port:
    cli
    mov al,0FFh
    mov cx,64h
loc_0291:
    loop loc_0291
    out dx,al
    add dx,2h
    mov cx,64h
loc_029A:
    loop loc_029A
    in al,dx
    sti
    sub dx,2h
    dec al
    jnz next_opna_port
    add dx,4h
    in al,dx
    mov bl,al
    add dx,2h
    in al,dx
    sub dx,6h
    and al,bl
    inc al
    jnz record_ports
next_opna_port:
    dec ah
    jz probe_failed
    add dx,100h
    jmp short try_opna_port
record_ports:
    mov [command_port],dx
    add dx,2h
    mov [data_port],dx
    add dx,2h
    mov [status_port],dx
    add dx,2h
    mov [adpcm_port],dx
    clc
    ret

probe_failed:
    mov byte ptr [exit_status],0h
    stc
    ret

; Write, read, and compare the 32-byte diagnostic pattern.
check_adpcm_ram:
    mov ax,cs
    mov ds,ax
    mov es,ax
    call write_test_pattern
    jc loc_02F7
    call read_test_pattern
    call compare_pattern
    jz loc_02F9
loc_02F7:
    stc
    ret

loc_02F9:
    clc
    ret

write_test_pattern:
    mov dx,1h
    call write_register
    mov dx,1017h
    call write_register
    mov dx,1080h
    call write_register
    mov dx,60h
    call write_register
    mov dx,102h
    call write_register
    mov dx,0CFFh
    call write_register
    inc dh
    call write_register
    mov bx,1FFFh
    mov dh,2h
    mov dl,bl
    call write_register
    inc dh
    mov dl,bh
    call write_register
    mov dx,4FFh
    call write_register
    inc dh
    call write_register
    mov si,offset test_pattern
    mov cx,20h
    mov dx,[status_port]
    mov bx,[adpcm_port]
write_next_pattern_byte:
    cli
    in al,dx
wait_adpcm_ready:
    in al,dx
    or al,al
    js wait_adpcm_ready
    mov al,8h
    out dx,al
    push cx
    mov cx,64h
delay_adpcm_command:
    loop delay_adpcm_command
    pop cx
    xchg bx,dx
    lodsb
    out dx,al
    sti
    xchg dx,bx
    push cx
    mov cx,2710h
    in al,dx
wait_adpcm_write:
    in al,dx
    test al,8h
    jnz wait_adpcm_data
    loop wait_adpcm_write
    pop cx
    stc
    ret

wait_adpcm_data:
    pop cx
    in al,dx
wait_adpcm_idle:
    in al,dx
    test al,al
    jns finish_adpcm_write
    in al,dx
    jmp short wait_adpcm_idle
finish_adpcm_write:
    mov al,10h
    cli
    out dx,al
    push cx
    mov cx,64h
delay_adpcm_finish:
    loop delay_adpcm_finish
    pop cx
    xchg dx,bx
    mov al,80h
    out dx,al
    sti
    xchg dx,bx
    loop write_next_pattern_byte
    mov dx,1000h
    call write_register
    mov dx,1080h
    call write_register
    mov dx,1h
    call write_register
    clc
    ret

read_test_pattern:
    mov dx,1h
    call write_register
    mov dx,1000h
    call write_register
    mov dx,1080h
    call write_register
    mov dx,20h
    call write_register
    mov dx,102h
    call write_register
    mov dx,0CFFh
    call write_register
    inc dh
    call write_register
    mov bx,1FFFh
    mov dh,2h
    mov dl,bl
    call write_register
    mov dh,3h
    mov dl,bh
    call write_register
    mov dx,4FFh
    call write_register
    inc dh
    call write_register
    call read_adpcm_byte
    call read_adpcm_byte
    mov cx,20h
    mov di,offset readback
read_next_pattern_byte:
    mov dx,[status_port]
    cli
wait_read_ready:
    in al,dx
    test al,al
    js wait_read_ready
    mov al,8h
    out dx,al
    in al,dx
wait_read_data:
    in al,dx
    test al,8h
    jz wait_read_data
    in al,dx
wait_read_idle:
    in al,dx
    or al,al
    js wait_read_idle
    mov dx,[adpcm_port]
    in al,dx
    sti
    stosb
    mov dx,1080h
    call write_register
    loop read_next_pattern_byte
    mov dx,1h
    call write_register
    ret

read_adpcm_byte:
    cli
    mov dx,[status_port]
wait_single_ready:
    in al,dx
    test al,al
    js wait_single_ready
    mov al,8h
    out dx,al
    push cx
    mov cx,64h
delay_single_read:
    loop delay_single_read
    pop cx
    mov dx,[adpcm_port]
    in al,dx
    sti
    mov dx,1080h
    call write_register
    ret

compare_pattern:
    mov si,offset test_pattern
    mov di,offset readback
    mov cx,20h
    repe cmpsb
    ret

; DX carries register in DH and value in DL. Preserve caller flags.
write_register:
    push ax
    push bx
    push dx
    mov bx,dx
    mov dx,[status_port]
    pushf
    cli
    in al,dx
wait_register_ready:
    in al,dx
    or al,al
    js wait_register_ready
    mov al,bh
    out dx,al
    push cx
    mov cx,64h
delay_register_write:
    loop delay_register_write
    pop cx
    mov dx,[adpcm_port]
    mov al,bl
    out dx,al
    popf
    pop dx
    pop bx
    pop ax
    ret


; Initialized bytes end at exit_status. The following buffers are COM BSS.
test_pattern db "*+=-PMD ADPCM RAM Check Data-=+*"
port_select db 0FFh
exit_status db 0
command_port dw ?
data_port dw ?
status_port dw ?
adpcm_port dw ?
pmd_found db ?
opna_first db ?
readback db 32 dup (?)

end start
