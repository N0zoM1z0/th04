; Read-only DOS open helper and its sharing-mode state.
; DOS_ROPEN and FONTFILE_OPEN are aliases of the same near Pascal entry.

.8086

_DATA segment word public 'DATA' use16
public file_sharingmode, _file_sharingmode
_file_sharingmode label word
file_sharingmode dw 0
_DATA ends
DGROUP group _DATA

_TEXT segment word public 'CODE' use16
assume cs:_TEXT, ds:DGROUP

public DOS_ROPEN, FONTFILE_OPEN

FileNotFound equ -2

DOS_ROPEN label near
FONTFILE_OPEN proc near
    mov bx, sp
    mov ah, 3Dh
    mov al, byte ptr file_sharingmode
    mov dx, ss:[bx+2]
    int 21h
    jc short open_error
    ret 2

even
open_error:
    mov ax, FileNotFound
    ret 2
FONTFILE_OPEN endp

_TEXT ends
end
