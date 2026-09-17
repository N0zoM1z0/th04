; Clear the selected PC-98 graphics page through GRCG black tile writes.
; The mutable VRAM segment/word count belong to the shared graphics state.
; Preserve flags around CLI and restore DI for the historical near ABI.

.8086

_DATA segment word public 'DATA' use16
extrn _graph_VramWords:word
extrn _graph_VramSeg:word
_DATA ends
DGROUP group _DATA

_TEXT segment word public 'CODE' use16
assume cs:_TEXT, ds:DGROUP
public GRAPH_CLEAR

GRAPH_CLEAR proc near
    mov al, 80h
    pushf
    cli
    out 7ch, al
    popf

    xor ax, ax
    mov dx, 7eh
    out dx, al
    out dx, al
    out dx, al
    out dx, al

    mov bx, di
    xor di, di
    mov cx, _graph_VramWords
    mov es, _graph_VramSeg
    rep stosw
    mov di, bx

    out 7ch, al
    ret
GRAPH_CLEAR endp

even
_TEXT ends
end
