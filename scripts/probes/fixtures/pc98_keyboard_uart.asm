; Authored PC-98 emulator-input Oracle fixture, not TH04 product source.
; BIOS matrices are read only. Real emulated IRQ1 must admit every key.
bits 16
org 0x100
push cs
pop ds
xor ax,ax
mov es,ax
; Drain startup traffic with guest instruction time and enabled IRQs.
; Sixteen 65535-instruction loops exceed a full 32-byte UART queue at 36000 cycles/ms.
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
wait_shot:
 test byte [es:0x052f],2
 jz wait_shot
mov al,0xa1
out dx,al
wait_enter:
 test byte [es:0x052f],2
 jnz wait_enter
 test byte [es:0x052d],0x10
 jz wait_enter
mov al,0xa2
out dx,al
wait_restore:
 test byte [es:0x052d],0x10
 jnz wait_restore
 test byte [es:0x052f],2
 jz wait_restore
mov al,0xa3
out dx,al
wait_release:
 test byte [es:0x052f],2
 jnz wait_release
mov al,0xa4
out dx,al
; A received byte alone must not become a BIOS key while IF is clear.
cli
mov al,0xa5
out dx,al
mov cx,0xffff
interrupt_blocked:
 loop interrupt_blocked
mov al,0xa6
out dx,al
sti
wait_unblocked:
 test byte [es:0x052f],2
 jz wait_unblocked
mov al,0xa7
out dx,al
wait_final:
 test byte [es:0x052f],2
 jnz wait_final
mov al,0xa8
out dx,al
mov ax,0x4c00
int 0x21
