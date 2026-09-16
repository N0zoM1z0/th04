; Player-performance adjustment helpers.
;
; TH04 and TH05 preserve the same frameless BX/SP argument ABI and byte clamp
; instruction skeleton. Legal TC4J probes introduce BP frames and, for the
; signed lower clamp, integer-promotion code that is absent from the targets.

.386
.model use16 large _TEXT

extrn _playperf:byte
extrn _playperf_max:byte
extrn _playperf_min:byte

CIRCLE_TEXT segment word public 'CODE' use16
CIRCLE_TEXT ends
main_01 group CIRCLE_TEXT

CIRCLE_TEXT segment word public 'CODE' use16
assume cs:main_01

public PLAYPERF_RAISE
PLAYPERF_RAISE proc far
    mov bx, sp
    mov al, ss:[bx+4]
    add al, _playperf
    cmp al, _playperf_max
    jbe short raise_ret
    mov al, _playperf_max
raise_ret:
    mov _playperf, al
    retf 2
PLAYPERF_RAISE endp
    even

public PLAYPERF_LOWER
PLAYPERF_LOWER proc far
    mov bx, sp
    mov al, _playperf
    sub al, ss:[bx+4]
    cmp al, _playperf_min
    jge short lower_ret
    mov al, _playperf_min
lower_ret:
    mov _playperf, al
    retf 2
PLAYPERF_LOWER endp

CIRCLE_TEXT ends
end
