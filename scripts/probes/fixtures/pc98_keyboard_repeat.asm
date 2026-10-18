; Authored read-only BIOS repeat control, not TH04 product code.
bits 16
org 0x100
push cs
pop ds
xor ax,ax
mov es,ax
sti
mov bx,16
warm_outer:
 mov cx,0xffff
warm_inner:
 loop warm_inner
 dec bx
 jnz warm_outer
mov dx,0xe9
mov al,0xa0
out dx,al
wait_initial:
 test byte [es:0x52f],2
 jz wait_initial
mov al,0xa1
out dx,al
; No physical release is requested. Wait for an actual BIOS clear.
wait_repeat_break:
 test byte [es:0x52f],2
 jnz wait_repeat_break
mov al,0xa2
out dx,al
wait_repeat_make:
 test byte [es:0x52f],2
 jz wait_repeat_make
mov al,0xa3
out dx,al
wait_second_break:
 test byte [es:0x52f],2
 jnz wait_second_break
mov al,0xa4
out dx,al
wait_second_make:
 test byte [es:0x52f],2
 jz wait_second_make
mov al,0xa5
out dx,al
wait_release:
 test byte [es:0x52f],2
 jnz wait_release
mov al,0xa6
out dx,al
mov ax,0x4c00
int 0x21
