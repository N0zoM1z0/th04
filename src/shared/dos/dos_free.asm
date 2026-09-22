; Free one MS-DOS memory block by segment.
; Near Pascal ABI: one segment argument, callee removes two bytes.
; Preserve ES and BP around INT 21h/AH=49h.

.8086

_DATA segment word public 'DATA' use16
_DATA ends
DGROUP group _DATA

_TEXT segment word public 'CODE' use16
assume cs:_TEXT, ds:DGROUP
public MEM_FREE, DOS_FREE

MEM_FREE label near
DOS_FREE proc near
    push bp
    push es
    mov bp, sp
    mov es, [bp+6]
    mov ah, 49h
    int 21h
    pop es
    pop bp
    ret 2
DOS_FREE endp

_TEXT ends
end
