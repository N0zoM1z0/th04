; Private diagnostic resident seed; never install as a gameplay MAIN.EXE.
; CHAR_ASCII and RANK are supplied by the preparation driver.
bits 16
org 100h
start:
 push cs
 pop ds
 mov dx, filename
 mov ax, 3d00h
 int 21h
 jc fail
 mov bx, ax
 mov dx, cfg
 mov cx, 10
 mov ah, 3fh
 int 21h
 pushf
 push ax
 mov ah, 3eh
 int 21h
 pop ax
 popf
 jc fail
 cmp ax, 10
 jne fail
 mov ax, [cfg+6]
 or ax, ax
 jz fail
 mov es, ax
 cmp byte [es:0], 'H'
 jne fail
 mov byte [es:011h], 5
 mov byte [es:012h], CHAR_ASCII
 mov byte [es:013h], '5'
 mov byte [es:019h], 0
 mov byte [es:025h], '0'
 mov byte [es:030h], 0ffh
 mov byte [es:00fh], RANK
 mov byte [es:049h], 1
 mov byte [es:048h], 1
 mov byte [es:01dh], 8
 mov byte [es:01eh], 7
 mov byte [es:01fh], 6
 mov byte [es:020h], 5
 mov byte [es:021h], 4
 mov byte [es:022h], 3
 mov byte [es:023h], 2
 mov byte [es:024h], 1
 mov word [es:044h], 44000
 mov word [es:046h], 0
 mov word [es:026h], 44000
 mov word [es:028h], 100
 mov word [es:02ah], 80
 mov word [es:02ch], 100
 mov word [es:02eh], 80
 mov word [es:034h], 100
 mov word [es:036h], 80
 mov dx, ok
 mov ah, 09h
 int 21h
; Match the OP text-clear side effect when bypassing its menu.
 mov al, 27
 int 29h
 mov al, '['
 int 29h
 mov al, '2'
 int 29h
 mov al, 'J'
 int 29h
 mov ax, cs
 mov es, ax
 mov bx, ((program_end - $$ + 0100h + 15) / 16)
 mov ah, 4ah
 int 21h
 jc fail
 mov ax, cs
 mov [exec_block + 4], ax
 mov [exec_block + 8], ax
 mov [exec_block + 12], ax
 mov bx, exec_block
 mov dx, maine_name
 mov ax, 4b00h
 int 21h
 jc fail
 mov ax, 4c00h
 int 21h
fail:
 mov dx, bad
 mov ah, 09h
 int 21h
 mov ax, 4c01h
 int 21h
filename db 'MIKO.CFG',0
cfg times 10 db 0
ok db 'GOOD ENDING FIXTURE READY',13,10,'$'
bad db 'GOOD ENDING FIXTURE FAILED',13,10,'$'
maine_name db 'MAINE.EXE',0
empty_tail db 0,13
exec_block dw 0, empty_tail, 0, 05ch, 0, 06ch, 0
program_end:
