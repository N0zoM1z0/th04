bits 16
org 100h
start:
 cli
 mov al,0a0h
 out 0e9h,al
 mov cx,65535
wait_overrun:
 loop wait_overrun
 mov al,0a1h
 out 0e9h,al
 sti
 nop
wait_both_pressed:
 xor ax,ax
 mov es,ax
 test byte [es:52fh],2
 jz wait_both_pressed
 test byte [es:52dh],10h
 jz wait_both_pressed
 mov al,0a2h
 out 0e9h,al
wait_both_released:
 test byte [es:52fh],2
 jnz wait_both_released
 test byte [es:52dh],10h
 jnz wait_both_released
 mov al,0a3h
 out 0e9h,al
 mov ax,4c00h
 int 21h
