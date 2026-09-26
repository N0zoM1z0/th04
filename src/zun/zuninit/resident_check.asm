; Print ZUNINIT banner and detect an already-installed INT 06h handler.
; AX returns 1 when ES points to a segment carrying the ZUNP marker.

.8086

_TEXT segment byte public 'CODE' use16
assume cs:_TEXT

extrn ZUNINIT_BANNER:byte
extrn ZUNINIT_SIGNATURE:word

public ZUNINIT_RESIDENT_CHECK

ZUNINIT_RESIDENT_CHECK proc near
    mov dx, offset ZUNINIT_BANNER
    mov ah, 9
    int 21h
    mov ax, 3506h
    int 21h
    cmp word ptr es:ZUNINIT_SIGNATURE, 'ZU'
    jnz short absent
    cmp word ptr es:ZUNINIT_SIGNATURE+2, 'NP'
    jnz short absent
    mov ax, 1
    jmp short done
absent:
    mov ax, 0
done:
    ret
ZUNINIT_RESIDENT_CHECK endp

_TEXT ends
end
