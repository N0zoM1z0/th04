; Private diagnostic code, appended only to the staged fault-trace build.
; Arm after Borland startup so its divide handler is the preserved INT 0 chain.
; All guest register/flag state is restored before forwarding the exception.

extrn _stage_id:byte, _rank:byte, _stage_frame:word
extrn _boss:byte, _boss_statebyte:byte

FAULT_TRACE_TEXT segment word public 'CODE' use16
assume cs:FAULT_TRACE_TEXT

fault_old0 dd 0
fault_old5 dd 0
fault_old6 dd 0
fault_armed db 0

FAULT_HANDLER macro handler_name, vector_number, old_handler
local stack_loop, code_loop
handler_name proc far
 push bp
 mov bp,sp
 pushf
 push ax
 push bx
 push cx
 push dx
 push si
 push ds
 push es
 push di
 mov al,'F'
 out 0E9h,al
 mov ax,vector_number
 call fault_cpu_hex
 mov ax,ss:[bp+4]
 call fault_cpu_hex
 mov ax,ss:[bp+2]
 call fault_cpu_hex
 mov ax,ss
 call fault_cpu_hex
 lea ax,[bp+2]
 call fault_cpu_hex
 mov ax,ss:[bp-14]
 call fault_cpu_hex
 mov ax,ss:[bp-4]
 call fault_cpu_hex
 mov ax,ss:[bp-10]
 call fault_cpu_hex
 mov ax,ss:[bp-6]
 call fault_cpu_hex
 mov ax,ss:[bp-8]
 call fault_cpu_hex
 mov ax,ss:[bp-12]
 call fault_cpu_hex
 mov ax,ss:[bp-16]
 call fault_cpu_hex
 mov ax,ss:[bp+6]
 call fault_cpu_hex
 mov di,bp
 mov dx,16
stack_loop:
 mov ax,ss:[di]
 call fault_cpu_hex
 add di,2
 dec dx
 jnz stack_loop
 mov ax,ss:[bp+4]
 mov es,ax
 mov di,ss:[bp+2]
 mov dx,8
code_loop:
 mov ax,es:[di]
 call fault_cpu_hex
 add di,2
 dec dx
 jnz code_loop
 mov al,10
 out 0E9h,al
 ; A read-only snapshot using the incoming DS, also recorded explicitly.
 ; boss_stuff_t has phase at15 and phase_frame at16 in the current TH04 ABI.
 mov al,'M'
 out 0E9h,al
 mov ax,ds
 call fault_cpu_hex
 xor ax,ax
 mov al,ds:[_stage_id]
 call fault_cpu_hex
 xor ax,ax
 mov al,ds:[_rank]
 call fault_cpu_hex
 mov ax,ds:[_stage_frame]
 call fault_cpu_hex
 xor ax,ax
 mov al,ds:[_boss+15]
 call fault_cpu_hex
 mov ax,word ptr ds:[_boss+16]
 call fault_cpu_hex
 xor ax,ax
 mov al,ds:[_boss_statebyte]
 call fault_cpu_hex
 xor ax,ax
 mov al,ds:[_boss_statebyte+13]
 call fault_cpu_hex
 xor ax,ax
 mov al,ds:[_boss_statebyte+14]
 call fault_cpu_hex
 xor ax,ax
 mov al,ds:[_boss_statebyte+15]
 call fault_cpu_hex
 mov al,10
 out 0E9h,al
 pop di
 pop es
 pop ds
 pop si
 pop dx
 pop cx
 pop bx
 pop ax
 popf
 pop bp
 jmp dword ptr cs:[old_handler]
handler_name endp
endm

FAULT_HANDLER fault_cpu0, 0, fault_old0
FAULT_HANDLER fault_cpu5, 5, fault_old5
FAULT_HANDLER fault_cpu6, 6, fault_old6

fault_cpu_hex proc near
 mov bx,ax
 mov cx,4
fault_cpu_hex_loop:
 push cx
 mov cl,4
 rol bx,cl
 pop cx
 mov al,bl
 and al,15
 add al,'0'
 cmp al,'9'
 jbe fault_cpu_hex_out
 add al,7
fault_cpu_hex_out:
 out 0E9h,al
 loop fault_cpu_hex_loop
 mov al,' '
 out 0E9h,al
 ret
fault_cpu_hex endp

public FAULT_TRACE_SETUP
FAULT_TRACE_SETUP proc far
 pushf
 push ax
 push bx
 push cx
 push dx
 push ds
 push es
 cmp byte ptr cs:[fault_armed],0
 je short fault_setup_install
 jmp fault_setup_restore
fault_setup_install:
 mov ax,3500h
 int 21h
 mov word ptr cs:[fault_old0],bx
 mov word ptr cs:[fault_old0+2],es
 push cs
 pop ds
 mov dx,offset fault_cpu0
 mov ax,2500h
 int 21h
 mov ax,3505h
 int 21h
 mov word ptr cs:[fault_old5],bx
 mov word ptr cs:[fault_old5+2],es
 mov dx,offset fault_cpu5
 mov ax,2505h
 int 21h
 mov ax,3506h
 int 21h
 mov word ptr cs:[fault_old6],bx
 mov word ptr cs:[fault_old6+2],es
 mov dx,offset fault_cpu6
 mov ax,2506h
 int 21h
 mov al,'A'
 out 0E9h,al
 mov ax,cs
 call fault_cpu_hex
 mov ax,word ptr cs:[fault_old0+2]
 call fault_cpu_hex
 mov ax,word ptr cs:[fault_old0]
 call fault_cpu_hex
 mov al,10
 out 0E9h,al
 mov byte ptr cs:[fault_armed],1
fault_setup_restore:
 pop es
 pop ds
 pop dx
 pop cx
 pop bx
 pop ax
 popf
 retf
FAULT_TRACE_SETUP endp
FAULT_TRACE_TEXT ends
